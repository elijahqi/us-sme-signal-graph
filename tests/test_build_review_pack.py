import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_review_pack.py"
SPEC = importlib.util.spec_from_file_location("build_review_pack", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReviewPackTest(unittest.TestCase):
    def test_source_kind_marks_known_directory(self):
        self.assertEqual("aggregator_or_directory", MODULE.source_kind("thomasnet.com", "Acme", ""))

    def test_source_kind_keeps_direct_company_candidate(self):
        self.assertEqual("direct_company_candidate", MODULE.source_kind("acme.com", "Acme Semiconductor", "Acme"))

    def test_source_kind_marks_news(self):
        self.assertEqual(
            "news_government_research_or_logistics",
            MODULE.source_kind("cnbc.com", "Inside ASML", "CNBC"),
        )

    def test_name_normalization(self):
        self.assertEqual("applied materials", MODULE.normalize_name("Applied Materials, Inc."))

    def test_review_id_and_candidate_id_are_distinct_concepts(self):
        self.assertNotEqual("review-domain", "candidate-url")


if __name__ == "__main__":
    unittest.main()
