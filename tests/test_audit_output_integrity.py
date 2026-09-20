import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_output_integrity import FINAL_FIELDS, summarize_outputs, verify_final_fields


class OutputIntegrityTest(unittest.TestCase):
    def test_non_key_quote_mismatch_fails_full_decision_verification(self):
        original = {"r": dict.fromkeys(FINAL_FIELDS, "same")}
        changed = {"r": {**original["r"], "evidence_quote": "different"}}
        with self.assertRaisesRegex(ValueError, "decision fields differ"):
            verify_final_fields(original, changed)

    def test_quote_categories_partition_each_label_without_relabeling(self):
        rows = {
            "a": {"eqdp": "no", "primary_exclusion_reason": "insufficient_evidence", "evidence_quote": ""},
            "b": {"eqdp": "unclear", "primary_exclusion_reason": "insufficient_evidence", "evidence_quote": "ACTUAL TEXT"},
            "c": {"eqdp": "no", "primary_exclusion_reason": "source_unavailable", "evidence_quote": "invented"},
        }
        evidence = {rid: {"evidence_excerpt": "Actual text"} for rid in rows}
        result = summarize_outputs(rows, evidence)
        self.assertEqual(result["no_with_evidence_gap_primary_reason"], 2)
        self.assertEqual(result["quote_check_by_label"]["no"]["empty"], 1)
        self.assertEqual(result["quote_check_by_label"]["no"]["nonempty_literal_fail"], 1)
        self.assertEqual(result["quote_check_by_label"]["unclear"]["literal_pass"], 1)
        for counts in result["quote_check_by_label"].values():
            self.assertEqual(counts["rows"], counts["literal_pass"] + counts["empty"] + counts["nonempty_literal_fail"])
        self.assertEqual(rows["c"]["eqdp"], "no")


if __name__ == "__main__":
    unittest.main()
