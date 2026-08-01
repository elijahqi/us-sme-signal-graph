"""Load final fieldwise decisions from the literal positive-quote re-audit."""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path

KEY_FIELDS=("identity_status","direct_producer_status","capability_match","production_presence","commercial_offering","eqdp","primary_exclusion_reason","scale_band","legal_form","web_visibility")
FINAL_FIELDS=("candidate_business_name",)+KEY_FIELDS+("production_city","production_state","confidence","evidence_quote","rationale")
def normalize(value):
 value=unicodedata.normalize('NFKC',value).strip().strip('“”"‘’\'').replace('…','...').replace('–','-').replace('—','-');return re.sub(r'\s+',' ',value).casefold()
def load_results(directory:Path):
 out={}
 for path in sorted(directory.glob('batch-*.json')):
  for row in json.load(open(path))['results']:out[row['review_id']]=row
 return out
def final_decisions(directory:Path):
 if not directory.exists():return {}
 a,b=load_results(directory/'reviewer_a'),load_results(directory/'reviewer_b');c=load_results(directory/'adjudication'/'reviewer_c')
 if set(a)!=set(b):raise ValueError('quote re-audit A/B coverage mismatch')
 out={}
 for rid in sorted(a):
  disputed=[f for f in KEY_FIELDS if a[rid][f]!=b[rid][f]]
  if disputed and rid not in c:raise ValueError(f'missing quote re-audit C decision: {rid}')
  decision=dict(c[rid] if disputed else a[rid])
  for field in KEY_FIELDS:decision[field]=a[rid][field] if a[rid][field]==b[rid][field] else c[rid][field]
  if decision['eqdp']=='yes' and not(decision['identity_status']=='yes' and decision['direct_producer_status']=='yes' and decision['capability_match']=='yes' and decision['production_presence'] in {'industrial_facility_confirmed','job_shop_or_workshop_confirmed','owner_or_home_production_confirmed'} and decision['commercial_offering']=='yes' and decision['primary_exclusion_reason']=='none'):raise ValueError(f'inconsistent quote re-audit positive: {rid}')
  out[rid]={**decision,'adjudicated_fields':'|'.join(disputed)}
 return out
