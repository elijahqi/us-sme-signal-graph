import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_processing_sensitivity import KEY_FIELDS, changes, read_final


class ProcessingAuditTest(unittest.TestCase):
    def test_invalid_final_label_cannot_disappear_from_positive_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "final.csv"
            path.write_text("review_id,eqdp\na,yes\nb,maybe\n")
            with self.assertRaisesRegex(ValueError, "Invalid final primary label"):
                read_final(path)

    def test_primary_change_is_already_a_key_field_change(self):
        before = {"r": dict.fromkeys(KEY_FIELDS, "no")}
        after = {"r": {**before["r"], "eqdp": "unclear"}}
        result = changes(before, after)
        self.assertEqual(result["primary_label_changed_rows"], 1)
        self.assertEqual(result["any_key_field_changed_rows"], 1)
        self.assertEqual(result["nonprimary_only_changed_rows"], 0)


if __name__ == "__main__":
    unittest.main()
