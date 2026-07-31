import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_trae_ai_review", ROOT / "scripts" / "run_trae_ai_review.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AiReviewValidationTest(unittest.TestCase):
    def test_rejects_missing_rows(self):
        payload = {"rows": [{"review_id": f"r{index}"} for index in range(10)]}
        with self.assertRaisesRegex(ValueError, "exactly 10"):
            MODULE.validate(payload, {"results": []})

    def test_rejects_inconsistent_positive(self):
        payload = {"rows": [{"review_id": f"r{index}"} for index in range(10)]}
        row = {
            "identity_status": "no", "direct_producer_status": "yes",
            "capability_match": "yes", "production_presence": "industrial_facility_confirmed",
            "commercial_offering": "yes", "eqdp": "yes",
            "primary_exclusion_reason": "none",
        }
        results = [{"review_id": f"r{index}", **row} for index in range(10)]
        with self.assertRaisesRegex(ValueError, "inconsistent EQDP"):
            MODULE.validate(payload, {"results": results})


if __name__ == "__main__":
    unittest.main()
