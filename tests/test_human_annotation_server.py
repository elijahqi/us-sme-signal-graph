import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import human_annotation_server as h

ROW = {"review_id": "synthetic-review-1", "capability_id": "TEST", "queried_state": "Ohio",
       "source_url": "https://example.org", "page_title": "Fictional test source", "meta_description": "",
       "task": {"capability_label": "Synthetic test", "positive_scope": "Test only", "explicit_exclusions": "Test only"},
       "evidence_excerpt": "This fictional example is only for testing the annotation software.", "page_sha256": "synthetic"}


def complete_answers():
    return {"identity_status": "unclear", "direct_producer_status": "unclear", "capability_match": "unclear",
            "production_presence": "unknown", "commercial_offering": "unclear", "eqdp": "unclear",
            "primary_exclusion_reason": "insufficient_evidence", "source_current_status": "unclear",
            "confidence": "high", "conflict_disclosed": "false", "notes": "Synthetic test; no research judgment.",
            "review_minutes": 1}


class HumanAnnotationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = h.Store(Path(self.tmp.name), [ROW], {"synthetic_test": True})
        self.token_a, self.a = self.store.create_session("TEST_A")
        self.token_b, self.b = self.store.create_session("TEST_B")

    def tearDown(self):
        self.tmp.cleanup()

    def test_answers_survive_restart_and_reviewers_are_separate(self):
        draft = self.store.save(self.a, ROW["review_id"], {"identity_status": "no"}, "draft", 0)
        self.assertEqual(self.store.records(self.b), {})
        restarted = h.Store(Path(self.tmp.name), [ROW], {"synthetic_test": True})
        reviewer = restarted.reviewer(self.token_a)
        self.assertEqual(restarted.records(reviewer)[ROW["review_id"]], draft)
        with self.assertRaisesRegex(ValueError, "代号已经使用"):
            restarted.create_session("TEST_A")

    def test_history_preserves_prior_decisions_and_stale_write_is_rejected(self):
        first = self.store.save(self.a, ROW["review_id"], {"identity_status": "no"}, "draft", 0)
        final = self.store.save(self.a, ROW["review_id"], complete_answers(), "submitted", 1)
        with self.assertRaisesRegex(ValueError, "另一页面更新"):
            self.store.save(self.a, ROW["review_id"], {"identity_status": "yes"}, "draft", 1)
        path = Path(self.tmp.name) / "reviewers" / self.a["id"] / "history.jsonl"
        self.assertEqual([json.loads(line) for line in path.read_text().splitlines()], [first, final])
        self.assertTrue(final["supplementary_fields_missing"])
        self.assertFalse(final["independent_second_review_completed"])

    def test_invalid_input_and_incomplete_submissions_are_not_counted(self):
        for answers, status in [({"identity_status": "partial"}, "draft"), ({"model_answer": "yes"}, "draft"),
                                 ({"identity_status": "no"}, "submitted"),
                                 ({**complete_answers(), "review_minutes": float("nan")}, "submitted")]:
            with self.assertRaises(ValueError):
                self.store.save(self.a, ROW["review_id"], answers, status, 0)
        self.assertEqual(self.store.records(self.a), {})

    def test_http_rejects_other_origins_and_export_contains_only_active_reviewer(self):
        self.store.save(self.a, ROW["review_id"], complete_answers(), "submitted", 0)
        server = h.make_server(self.store)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        port = server.server_port
        def request(path, token, origin=None, nonce=None, body=None):
            client = http.client.HTTPConnection("127.0.0.1", port)
            headers = {"Cookie": self.store.cookie_name + "=" + token}
            if origin: headers["Origin"] = origin
            if nonce: headers["X-Review-Nonce"] = nonce
            if body is not None: headers["Content-Type"] = "application/json"
            client.request("POST" if body is not None else "GET", path,
                           body=json.dumps(body) if body is not None else None, headers=headers)
            response = client.getresponse(); result = response.status, json.loads(response.read()); client.close()
            return result
        try:
            code, value = request("/api/export", self.token_a)
            self.assertEqual(code, 200); self.assertEqual(len(value["records"]), 1)
            code, value = request("/api/export", self.token_b)
            self.assertEqual(value["records"], [])
            self.assertEqual(request("/api/state", self.token_a, origin="http://evil.example")[0], 403)
            self.assertEqual(request("/api/save", self.token_a, body={})[0], 400)
            code, value = request("/api/save", self.token_b, nonce=self.store.nonce,
                body={"review_id": ROW["review_id"], "answers": {"eqdp": "no"}, "status": "draft", "base_revision": 0})
            self.assertEqual(code, 200); self.assertEqual(value["record"]["reviewer_id"], "TEST_B")
        finally:
            server.shutdown(); server.server_close(); thread.join()
