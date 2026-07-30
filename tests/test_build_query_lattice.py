import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_query_lattice", ROOT / "scripts" / "build_query_lattice.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class QueryLatticeTest(unittest.TestCase):
    def setUp(self):
        self.capabilities = MODULE.read_csv(MODULE.CAPABILITIES)
        self.geographies = MODULE.read_csv(MODULE.GEOGRAPHIES)
        self.intents = MODULE.read_csv(MODULE.INTENTS)
        self.rows = MODULE.build_rows(self.capabilities, self.geographies, self.intents)

    def test_expected_scale_and_balance(self):
        self.assertEqual(960, len(self.rows))
        self.assertEqual(10, len({row["industry_family"] for row in self.rows}))
        for family in {row["industry_family"] for row in self.rows}:
            self.assertEqual(96, sum(row["industry_family"] == family for row in self.rows))
        for intent in {row["intent_id"] for row in self.rows}:
            self.assertEqual(320, sum(row["intent_id"] == intent for row in self.rows))

    def test_queries_are_unique_and_provider_neutral(self):
        queries = [row["query"].casefold() for row in self.rows]
        self.assertEqual(len(queries), len(set(queries)))
        self.assertFalse(any("brave" in query or "you.com" in query for query in queries))

    def test_render_is_deterministic(self):
        self.assertEqual(MODULE.render(self.rows), MODULE.render(self.rows))


if __name__ == "__main__":
    unittest.main()
