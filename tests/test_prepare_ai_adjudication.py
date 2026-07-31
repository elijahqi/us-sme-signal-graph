import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prepare_ai_adjudication", ROOT / "scripts" / "prepare_ai_adjudication.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AdjudicationPreparationTest(unittest.TestCase):
    def test_key_fields_include_eqdp_and_production_presence(self):
        self.assertIn("eqdp", MODULE.KEY_FIELDS)
        self.assertIn("production_presence", MODULE.KEY_FIELDS)


if __name__ == "__main__":
    unittest.main()
