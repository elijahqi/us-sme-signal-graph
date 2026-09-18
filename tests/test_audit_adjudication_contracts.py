import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_adjudication_contracts import KEY_FIELDS, positive_contracts, routing


class AdjudicationContractsTest(unittest.TestCase):
    def test_other_field_dispute_exposes_agreed_primary_to_whole_record_overwrite(self):
        a = {"r": dict.fromkeys(KEY_FIELDS, "no")}
        b = {"r": {**a["r"], "legal_form": "unknown"}}
        c = {"r": {**b["r"], "eqdp": "unclear"}}
        result = routing(a, b, c)
        self.assertEqual(result["routed_to_c_primary_disagreement"], 0)
        self.assertEqual(result["whole_record_primary_agreement_overwrites"], 1)
        self.assertEqual(result["trigger_field_disagreements_in_overwritten_rows"]["legal_form"], 1)

    def test_primary_dispute_is_not_counted_as_agreement_overwrite(self):
        a = {"r": dict.fromkeys(KEY_FIELDS, "no")}
        b = {"r": {**a["r"], "eqdp": "unclear"}}
        result = routing(a, b, b)
        self.assertEqual(result["routed_to_c_primary_disagreement"], 1)
        self.assertEqual(result["whole_record_primary_agreement_overwrites"], 0)
        self.assertIsNone(result["whole_record_overwrite_fraction_among_agreed_primary_routed_rows"])

    def test_rejects_missing_adjudicator(self):
        a = {"r": dict.fromkeys(KEY_FIELDS, "no")}
        b = {"r": {**a["r"], "eqdp": "yes"}}
        with self.assertRaisesRegex(ValueError, "C coverage"):
            routing(a, b, {})

    def test_state_check_separates_location_from_facility_type(self):
        row = dict.fromkeys(KEY_FIELDS, "yes")
        row.update(production_presence="industrial_facility_confirmed", primary_exclusion_reason="none",
                   state_id="CA", production_state="Texas")
        result = positive_contracts({"r": row}, {"ca": "california", "tx": "texas"})
        self.assertEqual(result["positive_component_violations"], 0)
        self.assertEqual(result["positive_state_field_mismatches"], 1)


if __name__ == "__main__":
    unittest.main()
