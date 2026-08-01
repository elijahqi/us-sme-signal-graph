import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];SPEC=importlib.util.spec_from_file_location("run_trae_ai_census_review",ROOT/"scripts"/"run_trae_ai_census_review.py");MODULE=importlib.util.module_from_spec(SPEC);assert SPEC.loader is not None;SPEC.loader.exec_module(MODULE)

class CensusValidationTest(unittest.TestCase):
    def test_variable_batch_size(self):
        payload={"rows":[{"review_id":f"r{i}"} for i in range(4)]}
        base={"candidate_business_name":"x","identity_status":"no","direct_producer_status":"no","capability_match":"no","production_presence":"unknown","commercial_offering":"unclear","eqdp":"no","primary_exclusion_reason":"insufficient_evidence","scale_band":"unknown","legal_form":"unknown","web_visibility":"unknown","production_city":"","production_state":"","confidence":"low","evidence_quote":"","rationale":"insufficient"}
        MODULE.validate(payload,{"results":[{"review_id":f"r{i}",**base} for i in range(4)]})

if __name__=="__main__":unittest.main()
