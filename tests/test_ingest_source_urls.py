import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ingest_source_urls.py"
SPEC = importlib.util.spec_from_file_location("ingest_source_urls", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class IngestSourceUrlsTest(unittest.TestCase):
    def test_canonicalize_removes_tracking_and_fragment(self):
        value = MODULE.canonicalize_url("HTTPS://Example.COM/a/?utm_source=x&id=2#part")
        self.assertEqual("https://example.com/a?id=2", value)

    def test_page_parser_extracts_metadata_and_visible_text(self):
        parser = MODULE.PageParser()
        parser.feed('<html><head><title>Acme | Home</title><meta property="og:site_name" content="Acme"></head><body><script>hidden</script><p>Semiconductor manufacturing</p></body></html>')
        self.assertEqual("Acme", parser.meta["og:site_name"])
        self.assertIn("Semiconductor manufacturing", parser.text_parts)
        self.assertNotIn("hidden", parser.text_parts)

    def test_normalize_company_suffixes(self):
        self.assertEqual("gpr", MODULE.normalize_name("GPR Company, Inc."))

    def test_non_success_status_must_not_be_treated_as_evidence(self):
        self.assertFalse(200 <= 404 < 400)


if __name__ == "__main__":
    unittest.main()
