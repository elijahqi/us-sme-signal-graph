import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compute_pilot_metrics.py"
SPEC = importlib.util.spec_from_file_location("compute_pilot_metrics", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class MetricsTest(unittest.TestCase):
    def test_wilson_known_interval(self):
        low, high = MODULE.wilson(29, 75)
        self.assertAlmostEqual(low, 0.285, places=3)
        self.assertAlmostEqual(high, 0.500, places=3)

    def test_empty_wilson(self):
        self.assertEqual(MODULE.wilson(0, 0), (0.0, 0.0))

if __name__ == "__main__":
    unittest.main()
