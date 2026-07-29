import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_baseline.py"
SPEC = importlib.util.spec_from_file_location("build_baseline", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class BaselineBuilderTest(unittest.TestCase):
    def test_normalize_full_state_name_preserves_raw_value(self):
        state, raw_state, flag = MODULE.normalize_state("Oklahoma")
        self.assertEqual("OK", state)
        self.assertEqual("OKLAHOMA", raw_state)
        self.assertEqual("normalized_full_name", flag)

    def test_extract_handles_nested_array_and_bracket_in_string(self):
        page = 'before var companiesData = [{"name":"A ] Co","company_type":["Equipment"]}]; after'
        records = MODULE.extract_records(page)
        self.assertEqual("A ] Co", records[0]["name"])

    def test_build_merges_company_but_keeps_two_facilities(self):
        page = b'''<script>var companiesData = [
          {"name":"A &amp; B, Inc.","company_type":["Equipment"],"city":"Mesa","state":"AZ","lat":1.0,"lon":2.0,"company_activity":["Manufacturing"],"announcement_type":["Existing"],"source":"https://example.com/a"},
          {"name":"A &amp; B, Inc.","company_type":["Equipment"],"city":"Austin","state":"TX","lat":3.0,"lon":4.0,"company_activity":["R&D"],"announcement_type":["New"],"source":""}
        ]; const x = 1;</script>'''
        source = {"source_id":"test","publisher":"Test","url":"https://example.com/map","scope_note":"test"}
        with tempfile.TemporaryDirectory() as directory:
            manifest = MODULE.build(page, source, "2026-07-29T00:00:00+00:00", Path(directory))
            self.assertEqual(1, manifest["counts"]["companies"])
            self.assertEqual(2, manifest["counts"]["facilities"])
            self.assertEqual(1, manifest["counts"]["equipment_or_materials_companies"])


if __name__ == "__main__":
    unittest.main()
