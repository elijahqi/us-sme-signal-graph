import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apply_reviewer1_adjudication.py"
SPEC = importlib.util.spec_from_file_location("apply_reviewer1_adjudication", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class Reviewer1AdjudicationTest(unittest.TestCase):
    def test_review_scope_requires_all_three_signals(self):
        row = {
            "source_kind_prelabel": "direct_company_candidate",
            "semiconductor_signal": "True",
            "manufacturing_signal": "True",
            "us_presence_signal": "True",
        }
        self.assertTrue(MODULE.in_review_scope(row))
        row["us_presence_signal"] = "False"
        self.assertTrue(MODULE.in_review_scope(row))
        self.assertFalse(MODULE.in_review_scope(row, "us_signal_subset"))

    def test_boolean_parser_fails_closed(self):
        self.assertTrue(MODULE.bool_value("true", "x"))
        self.assertFalse(MODULE.bool_value("False", "x"))
        with self.assertRaises(ValueError):
            MODULE.bool_value("unknown", "x")

    def test_decision_coverage_rejects_missing_rows(self):
        rows = [
            {
                "review_id": "r1",
                "source_kind_prelabel": "direct_company_candidate",
                "semiconductor_signal": "True",
                "manufacturing_signal": "True",
                "us_presence_signal": "True",
            }
        ]
        with self.assertRaises(ValueError):
            MODULE.validate_decisions(rows, [])


if __name__ == "__main__":
    unittest.main()
