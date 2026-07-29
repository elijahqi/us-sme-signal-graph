import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_public_release.py"
SPEC = importlib.util.spec_from_file_location("validate_public_release", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class PublicReleaseValidatorTest(unittest.TestCase):
    def test_provider_columns_are_forbidden(self):
        self.assertIn("provider", MODULE.FORBIDDEN_COLUMNS)
        self.assertIn("snippet", MODULE.FORBIDDEN_COLUMNS)

if __name__ == "__main__":
    unittest.main()
