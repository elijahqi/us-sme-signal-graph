import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_evidence_review.py"
SPEC = importlib.util.spec_from_file_location("prepare_evidence_review", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class EvidenceReviewTest(unittest.TestCase):
    def test_extracts_semiconductor_window(self):
        text = "prefix " * 80 + "We manufacture semiconductor vacuum chambers in Texas." + " suffix" * 80
        self.assertTrue(any("semiconductor vacuum chambers" in value for value in MODULE.evidence_windows(text)))

    def test_visible_text_skips_script(self):
        parser = MODULE.VisibleText()
        parser.feed("<script>semiconductor hidden</script><p>Visible manufacturing</p>")
        self.assertNotIn("semiconductor hidden", parser.parts)
        self.assertIn("Visible manufacturing", parser.parts)


if __name__ == "__main__":
    unittest.main()
