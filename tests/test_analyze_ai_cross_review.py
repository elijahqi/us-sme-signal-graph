import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "analyze_ai_cross_review", ROOT / "scripts" / "analyze_ai_cross_review.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CrossReviewAnalysisTest(unittest.TestCase):
    def test_kappa_perfect_agreement(self):
        self.assertEqual(1.0, MODULE.cohen_kappa(["yes", "no"], ["yes", "no"]))

    def test_weighted_rate(self):
        rows = [
            {"inclusion_probability": "0.5", "eqdp": "yes"},
            {"inclusion_probability": "0.25", "eqdp": "no"},
        ]
        self.assertAlmostEqual(1 / 3, MODULE.weighted_rate(rows, lambda row: row["eqdp"] == "yes"))

    def test_normalize_quote_strips_curly_quotes(self):
        self.assertEqual("quoted text", MODULE.normalize_quote("“Quoted   text”"))


if __name__ == "__main__": unittest.main()
