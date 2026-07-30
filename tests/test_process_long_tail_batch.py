import importlib.util
import base64
import io
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "process_long_tail_batch", ROOT / "scripts" / "process_long_tail_batch.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LongTailBatchTest(unittest.TestCase):
    def test_parse_accepts_rights_safe_record(self):
        records = MODULE.parse_input(io.StringIO(
            '{"query_id":"LTQ0001","union_urls":["https://example.com/a"]}\n'
        ))
        MODULE.validate_records(records)
        self.assertEqual(1, len(records))

    def test_raw_provider_fields_fail_closed(self):
        records = MODULE.parse_input(io.StringIO(
            '{"query_id":"LTQ0001","union_urls":[],"snippets":["x"]}\n'
        ))
        with self.assertRaisesRegex(ValueError, "raw provider field"):
            MODULE.validate_records(records)

    def test_unknown_query_fails_closed(self):
        records = MODULE.parse_input(io.StringIO(
            '{"query_id":"LTQ9999","union_urls":[]}\n'
        ))
        with self.assertRaisesRegex(ValueError, "frozen lattice"):
            MODULE.validate_records(records)

    def test_base64_transport_round_trip(self):
        payload = b'{"query_id":"LTQ0001","union_urls":[]}\n'
        decoded = base64.b64decode(base64.b64encode(payload), validate=True).decode("utf-8")
        records = MODULE.parse_input(io.StringIO(decoded))
        MODULE.validate_records(records)


if __name__ == "__main__":
    unittest.main()
