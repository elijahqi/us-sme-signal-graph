import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prepare_ai_review_batches", ROOT / "scripts" / "prepare_ai_review_batches.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class EvidenceWindowTest(unittest.TestCase):
    def test_window_includes_keyword_context_and_is_bounded(self):
        text = "start " + "x " * 2000 + "precision machining in Ohio production facility"
        output = MODULE.evidence_window(text, ["precision machining", "Ohio"], 1200)
        self.assertIn("precision machining", output)
        self.assertLessEqual(len(output.replace("\n[...]\n", "")), 1200)

    def test_empty_text_stays_empty(self):
        self.assertEqual("", MODULE.evidence_window("", ["test"]))

    def test_visible_text_removes_common_cookie_banner(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            target = Path(directory) / "page.html"
            target.write_text(
                "<html><body>We use cookies and privacy tracking. Settings. "
                "Products Electrode coating production facility in Ohio.</body></html>"
            )
            output = MODULE.visible_text(target)
        self.assertNotIn("cookies", output.casefold())
        self.assertIn("Electrode coating", output)


if __name__ == "__main__":
    unittest.main()
