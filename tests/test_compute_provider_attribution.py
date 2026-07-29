import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compute_provider_attribution.py"
SPEC = importlib.util.spec_from_file_location("compute_provider_attribution", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class ProviderAttributionTest(unittest.TestCase):
    def test_domain_normalization(self):
        self.assertEqual(MODULE.registrable_domain("https://www.example.com/a"), "example.com")
        self.assertEqual(MODULE.registrable_domain("https://a.example.co.uk/a"), "example.co.uk")

if __name__ == "__main__":
    unittest.main()
