import importlib.util
import unittest
import json
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_trae_ai_review", ROOT / "scripts" / "run_trae_ai_review.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AiReviewValidationTest(unittest.TestCase):
    def test_failed_batch_preserves_successes_and_failure_in_manifest(self):
        def fake_batch(path, *args):
            if path.stem == "batch-002":
                raise RuntimeError("synthetic failure")
            return {"batch_id": path.stem, "status": "accepted"}
        with tempfile.TemporaryDirectory() as directory, patch.object(MODULE, "PRIVATE", Path(directory)), patch.object(
                MODULE, "run_batch", side_effect=fake_batch), patch.object(sys, "argv", [
                    "review", "--reviewer", "A", "--start", "1", "--end", "2", "--workers", "1"]), patch("builtins.print"):
            with self.assertRaisesRegex(SystemExit, "outcomes are preserved"):
                MODULE.main()
            rows = json.loads((Path(directory) / "reviewer_a_manifest_001_002.json").read_text())
            self.assertEqual([row["status"] for row in rows], ["accepted", "failed"])

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
