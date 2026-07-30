import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_long_tail_review_sample", ROOT / "scripts" / "build_long_tail_review_sample.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LongTailReviewSampleTest(unittest.TestCase):
    def test_stable_pick_is_deterministic(self):
        rows = [{"id": str(index)} for index in range(20)]
        self.assertEqual(MODULE.stable_pick(rows, 5, 7), MODULE.stable_pick(rows, 5, 7))


if __name__ == "__main__":
    unittest.main()
