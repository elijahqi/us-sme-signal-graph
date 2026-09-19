import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import glm_cross_review as g


def evidence(rid="r"):
    row = dict.fromkeys(g.INPUT_FIELDS, "")
    row.update(review_id=rid, task={}, queried_state="California", evidence_excerpt="We manufacture parts in California.")
    return row


def decision(rid="r"):
    row = {k: rule.get("enum", [""])[0] for k, rule in g.item_schema()["properties"].items()}
    row.update(review_id=rid, candidate_business_name="Example", identity_status="yes",
               direct_producer_status="yes", capability_match="yes", commercial_offering="yes", eqdp="yes",
               production_presence="industrial_facility_confirmed", production_state="CA", primary_exclusion_reason="none",
               evidence_quote="We manufacture parts in California.", rationale="The supplied excerpt states production and location.")
    return row


def frozen(work):
    batch = {"batch_id": "batch-0001", "rows": [evidence()]}
    g.save(work / "inputs/batch-0001.json", batch)
    g.save(work / "reference.json", {"r": decision()})
    manifest = {"protocol_sha256": g.sha(g.encoded(g.protocol())), "planned_rows": 1,
                "reference_sha256": g.sha((work / "reference.json").read_bytes()),
                "original_final_csv_sha256": "synthetic",
                "batches": [{"batch_id": "batch-0001", "rows": 1,
                             "sha256": g.sha((work / "inputs/batch-0001.json").read_bytes())}]}
    g.save(work / "manifest.json", manifest)
    return batch


class FullGLMReviewTest(unittest.TestCase):
    def test_invalid_enum_is_quarantined_without_changing_any_label(self):
        invalid = decision("s")
        invalid["direct_producer_status"] = "partial"
        partition = g.partition_output({"results": [decision(), invalid]}, {"rows": [evidence(), evidence("s")]})
        self.assertEqual(len(partition["results"]), 1)
        self.assertEqual(len(partition["invalid_results"]), 1)
        self.assertEqual(partition["invalid_results"][0]["result"]["eqdp"], "yes")
        self.assertEqual(invalid["direct_producer_status"], "partial")

    def test_valid_positive_and_quality_flags_do_not_relabel(self):
        batch = {"rows": [evidence()]}
        row = decision()
        self.assertEqual(g.validate_output({"results": [row]}, batch), {"r": []})
        row.update(production_state="TX", evidence_quote="not supplied")
        flags = g.validate_output({"results": [row]}, batch)["r"]
        self.assertEqual(set(flags), {"positive_state_not_matching_query", "positive_quote_not_literal"})
        self.assertEqual(row["eqdp"], "yes")

    def test_duplicate_or_missing_rows_fail(self):
        batch = {"rows": [evidence(), evidence("s")]}
        for results in ([decision()], [decision(), decision()]):
            with self.assertRaises(ValueError):
                g.validate_output({"results": results}, batch)

    def test_omissions_are_separate_from_unclear_and_invalid(self):
        batch = {"rows": [evidence(), evidence("s")]}
        partition = g.partition_output({"results": [decision()]}, batch)
        self.assertEqual(partition["missing_review_ids"], ["s"])
        self.assertEqual(partition["results"], [decision()])
        self.assertEqual(partition["invalid_results"], [])
        for rows in ([decision(), decision()], [decision("unknown")]):
            with self.assertRaisesRegex(ValueError, "Duplicate or unexpected"):
                g.partition_output({"results": rows}, batch)

    def test_complete_response_with_no_rows_is_accounted_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            frozen(work)
            with patch.object(g, "EDITORIAL_OUTPUT", work / "lock"), patch("builtins.print"):
                g.run(1, work, lambda *args: {"result": '{"results": []}'})
                g.run(1, work, lambda *args: self.fail("must not retry omitted rows"))
            summary = g.analyze(work)
            self.assertEqual(summary["status"], "complete_with_missing_rows")
            self.assertEqual(summary["omitted_rows"], 1)
            self.assertEqual(summary["response_rows_received"], 0)
            self.assertEqual(summary["component_agreement"]["eqdp"]["n"], 0)
            self.assertEqual(summary["coverage_by_gpt_label"]["yes"]["omitted"], 1)

    def test_input_label_leak_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            batch = frozen(work)
            batch["rows"][0]["eqdp"] = "yes"
            g.save(work / "inputs/batch-0001.json", batch)
            with self.assertRaisesRegex(ValueError, "input hash"):
                g.load_frozen(work)

    def test_timeout_cannot_be_retried_on_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            frozen(work)
            with patch.object(g, "EDITORIAL_OUTPUT", work / "lock"), patch.object(g, "invoke"):
                def fail(*args):
                    raise TimeoutError()
                with self.assertRaisesRegex(ValueError, "no automatic retry"):
                    g.run(1, work, fail)
                with self.assertRaisesRegex(ValueError, "Unresolved"):
                    g.run(1, work, lambda *args: self.fail("must not call API"))
                summary = g.analyze(work)
                self.assertEqual(summary["status"], "partial")
                self.assertEqual(summary["valid_rows"], 0)
                self.assertEqual(summary["missing_or_failed_rows"], 1)

    def test_completed_batch_resumes_without_call_and_hash_tamper_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            frozen(work)
            def success(*args):
                return {"result": json.dumps({"results": [decision()]}), "usage": {"input_tokens": 10}}
            with patch.object(g, "EDITORIAL_OUTPUT", work / "lock"), patch("builtins.print"):
                g.run(1, work, success)
                g.run(1, work, lambda *args: self.fail("must not re-review completed rows"))
                self.assertEqual(g.analyze(work)["component_agreement"]["eqdp"]["agreement"], 1)
                (work / "results/batch-0001.json").write_text("{}")
                with self.assertRaisesRegex(ValueError, "Result hash"):
                    g.analyze(work)


if __name__ == "__main__":
    unittest.main()
