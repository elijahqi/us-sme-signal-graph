import json
from pathlib import Path
import sys
import tempfile
import unittest
from decimal import Decimal
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gemini_cross_review as g


def row(rid="r", domain="example.test"):
    r = dict.fromkeys(g.INPUT_FIELDS, "")
    r.update(review_id=rid, registrable_domain=domain, queried_state="California",
             task={}, evidence_excerpt="We manufacture precision parts in California.")
    return r


def positive():
    r = {k: (v["enum"][0] if "enum" in v else "") for k, v in g.schema()["properties"].items()}
    r.update(review_id="r", identity_status="yes", direct_producer_status="yes",
             capability_match="yes", commercial_offering="yes", eqdp="yes",
             production_presence="industrial_facility_confirmed", primary_exclusion_reason="none",
             production_state="CA", evidence_quote="precision parts in California")
    return r


class GeminiReviewTest(unittest.TestCase):
    def test_jsonl_retains_unicode_line_separators_inside_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            data = [{"excerpt": "first\u2028second\u2029third\x85fourth"}, {"excerpt": "last"}]
            path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in data) + "\n")
            self.assertEqual(g.read_rows(path), data)

    def test_split_is_domain_disjoint_and_strips_model_fields(self):
        evidence = [{**row(str(i), f"d{i}.test"), "eqdp": "yes", "rationale": "hidden"} for i in range(330)]
        sample = [{"review_id": str(i), "double_review": str(i < 300).lower()} for i in range(330)]
        result = g.select_rows(evidence, sample)
        self.assertEqual(len(result["development"]), 20)
        self.assertEqual(len(result["evaluation"]), 300)
        self.assertFalse({r["registrable_domain"] for r in result["development"]}
                         & {r["registrable_domain"] for r in result["evaluation"]})
        self.assertTrue(all(set(r) == set(g.INPUT_FIELDS) for rows in result.values() for r in rows))
        self.assertEqual(result, g.select_rows(evidence, sample))

    def test_missing_evidence_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "coverage"):
            g.select_rows([], [{"review_id": "r", "double_review": "true"}])

    def test_budget_reserves_unknown_outcomes(self):
        ledger = {"entries": [{"accounted_usd": "8.70", "status": "uncertain"}]}
        with self.assertRaisesRegex(ValueError, "budget stop"):
            g.reserve(ledger, "development", row(), Decimal("0.50"))
        self.assertEqual(len(ledger["entries"]), 1)

    def test_usage_includes_reasoning_tokens(self):
        response = {"usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20,
                                      "thoughtsTokenCount": 80, "totalTokenCount": 200}}
        self.assertEqual(g.charged_usage(response), g.cost(100, 100))
        self.assertIsNone(g.charged_usage({}))

    def test_positive_state_and_quote_failures_are_retained_as_flags(self):
        result = positive()
        self.assertEqual(g.validate_result(result, row()), [])
        result.update(production_state="TX", evidence_quote="Invented quotation.")
        flags = g.validate_result(result, row())
        self.assertEqual(set(flags), {"positive_quote_not_literal", "positive_state_not_matching_query"})
        self.assertEqual(result["eqdp"], "yes")

    def test_timeout_is_accounted_and_resume_does_not_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            with patch.object(g, "load_prepared", return_value=({}, {"development": [row()]})), patch.dict(
                    g.CONFIG, {"live_execution_verified": True, "model": "gemini-test",
                               "pricing_checked": "2026-01-01", "pricing_valid_through": "9999-12-31"}):
                def failed_call(*args):
                    raise TimeoutError()
                with self.assertRaisesRegex(ValueError, "uncertain"):
                    g.run("development", 1, "example-project", work, failed_call, lambda: "synthetic")
                ledger = g.read_ledger(work)
                self.assertEqual(ledger["entries"][0]["status"], "uncertain")
                self.assertGreater(Decimal(ledger["entries"][0]["accounted_usd"]), 0)
                with self.assertRaisesRegex(ValueError, "unresolved"):
                    g.run("development", 1, "example-project", work,
                          lambda *args: self.fail("must not call API"), lambda: "synthetic")

    def test_unverified_live_configuration_stops_before_credentials_or_network(self):
        with patch.dict(g.CONFIG, {"live_execution_verified": False}):
            with self.assertRaisesRegex(ValueError, "live execution disabled"):
                g.run("development", 1, "example-project",
                      call=lambda *args: self.fail("must not call API"),
                      get_token=lambda: self.fail("must not request credentials"))

    def test_agreement_is_not_reported_as_accuracy(self):
        value = g.agreement([("yes", "yes"), ("no", "unclear"), ("no", "no")])
        self.assertAlmostEqual(value["agreement"], 2 / 3)
        self.assertNotIn("accuracy", value)
        self.assertIsNone(g.agreement([])["agreement"])


if __name__ == "__main__":
    unittest.main()
