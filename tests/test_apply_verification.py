import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apply_verification.py"
SPEC = importlib.util.spec_from_file_location("apply_verification", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class VerificationTest(unittest.TestCase):
    def test_boolean_fails_closed(self):
        self.assertTrue(MODULE.as_bool("true", "x"))
        with self.assertRaises(ValueError):
            MODULE.as_bool("pending", "x")

if __name__ == "__main__":
    unittest.main()
