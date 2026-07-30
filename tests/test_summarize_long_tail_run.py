import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "summarize_long_tail_run", ROOT / "scripts" / "summarize_long_tail_run.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LongTailSummaryTest(unittest.TestCase):
    def test_sha256_file_is_stable(self):
        first = MODULE.sha256_file(MODULE.LATTICE)
        second = MODULE.sha256_file(MODULE.LATTICE)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))


if __name__ == "__main__":
    unittest.main()
