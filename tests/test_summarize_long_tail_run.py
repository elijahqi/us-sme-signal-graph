import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "summarize_long_tail_run", ROOT / "scripts" / "summarize_long_tail_run.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LongTailSummaryTest(unittest.TestCase):
    def test_sha256_file_is_stable(self):
        first = MODULE.sha256_file(MODULE.LATTICE)
        second = MODULE.sha256_file(MODULE.LATTICE)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))

    def test_summary_distinguishes_pooled_and_macro_jaccard(self):
        def write_csv(path, rows):
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)

        # The successful queries have Jaccards 1/1 and 1/9. A failed Brave
        # query still has four You URLs, so its all-query Jaccard is 0/4.
        aggregates = [
            {
                "query_id": query_id,
                "brave_call_status": brave_status,
                "you_call_status": "success",
                "brave_returned_count": brave_count,
                "you_returned_count": you_count,
                "canonical_url_intersection_count": intersection,
                "canonical_url_union_count": union,
                "domain_intersection_count": intersection,
            }
            for query_id, brave_status, brave_count, you_count, intersection, union in (
                ("query-1", "success", 1, 1, 1, 1),
                ("query-2", "success", 5, 5, 1, 9),
                ("query-3", "failed", 0, 4, 0, 4),
            )
        ]
        with tempfile.TemporaryDirectory() as temporary:
            benchmark = Path(temporary)
            private = benchmark / "private"
            private.mkdir()
            lattice = benchmark / "query_lattice_v0_2.csv"
            for filename, row in (
                ("capability_set_v0_2.csv", {"capability_id": "test-capability"}),
                ("geographies_v0_1.csv", {"state_id": "test-state"}),
                ("intent_templates_v0_1.csv", {"intent_id": "test-intent"}),
            ):
                write_csv(benchmark / filename, [row])

            def summarize_queries(selected):
                write_csv(lattice, [
                    {
                        "query_id": row["query_id"],
                        "industry_family": "test-industry",
                        "intent_id": "test-intent",
                        "state_id": "test-state",
                    }
                    for row in selected
                ])
                write_csv(private / "query_aggregates.csv", selected)
                sources, links = [], []
                for row in selected:
                    for index in range(row["canonical_url_union_count"]):
                        candidate_id = f"{row['query_id']}-source-{index}"
                        url = f"https://{candidate_id}.example.invalid/"
                        sources.append({
                            "candidate_id": candidate_id,
                            "canonical_url": url,
                            "http_status": "200",
                            "robots_status": "allowed",
                            "fetch_error": "",
                        })
                        links.append({
                            "query_id": row["query_id"],
                            "candidate_id": candidate_id,
                            "canonical_url": url,
                        })
                write_csv(private / "source_candidates.csv", sources)
                write_csv(private / "query_source_links.csv", links)
                return MODULE.summarize(private=private)

            with patch.multiple(MODULE, LATTICE=lattice, BENCHMARK=benchmark):
                summary = summarize_queries(aggregates)
                self.assertEqual(3, summary["query_count"])
                self.assertEqual(1, summary["brave_failed_queries"])
                self.assertEqual(0, summary["you_failed_queries"])
                self.assertEqual(14, summary["query_source_links"])
                self.assertAlmostEqual(2 / 14, summary["pooled_query_url_jaccard"])
                self.assertAlmostEqual(10 / 27, summary["macro_mean_query_url_jaccard"])
                dimension = summary["dimensions"]["industry_family"]["test-industry"]
                self.assertAlmostEqual(2 / 14, dimension["pooled_url_jaccard"])
                self.assertAlmostEqual(10 / 27, dimension["macro_mean_query_url_jaccard"])

                dual_success = summarize_queries(aggregates[:2])
                self.assertEqual(2, dual_success["query_count"])
                self.assertEqual(0, dual_success["brave_failed_queries"])
                self.assertAlmostEqual(2 / 10, dual_success["pooled_query_url_jaccard"])
                self.assertAlmostEqual(5 / 9, dual_success["macro_mean_query_url_jaccard"])
                self.assertNotEqual(
                    summary["pooled_query_url_jaccard"],
                    dual_success["pooled_query_url_jaccard"],
                )


if __name__ == "__main__":
    unittest.main()
