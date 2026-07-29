import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_public_release.py"
SPEC = importlib.util.spec_from_file_location("build_public_release", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class PublicReleaseTest(unittest.TestCase):
    def test_public_fields_exclude_provider_origin_and_page_text(self):
        fields = set(MODULE.PUBLIC_FIELDS)
        self.assertNotIn("provider", fields)
        self.assertNotIn("evidence_quote", fields)
        self.assertNotIn("source_evidence_windows", fields)

if __name__ == "__main__":
    unittest.main()
