import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_lawyer_pack.py"
SPEC = importlib.util.spec_from_file_location("build_lawyer_pack", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

class LawyerPackTest(unittest.TestCase):
    def test_markdown_renderer_outputs_real_structure(self):
        source = "# Title\n\n- one\n- two\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        rendered = MODULE.markdown_to_html(source)
        self.assertIn("<h1>Title</h1>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("<table>", rendered)
        self.assertNotIn("# Title", rendered)

    def test_native_docx_contains_heading_and_table_xml(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "memo.docx"
            MODULE.write_native_docx("# Title\n\n| A | B |\n|---|---|\n| 1 | 2 |", output)
            with ZipFile(output) as archive:
                document = archive.read("word/document.xml").decode()
            self.assertIn('<w:pStyle w:val="Heading1"/>', document)
            self.assertIn("<w:tbl>", document)

if __name__ == "__main__":
    unittest.main()
