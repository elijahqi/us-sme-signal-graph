#!/usr/bin/env python3
"""Merge operating-entity size reviews and produce audited aggregate results."""
from __future__ import annotations
from collections import Counter
import csv,hashlib,json,re,unicodedata
from pathlib import Path
from prepare_entity_size_adjudication import FIELDS,load_results

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3'/'ai_census_v0_4';OUT=BASE/'entity_size_v0_1'
def norm(x):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',x).replace('“','"').replace('”','"').replace('’',"'")).strip().casefold()
def kappa(a,b):
 po=sum(x==y for x,y in zip(a,b))/len(a);ca,cb=Counter(a),Counter(b);pe=sum(ca[k]/len(a)*cb[k]/len(b) for k in set(ca)|set(cb));return (po-pe)/(1-pe) if pe<1 else 1.0
def main():
 entities=json.load(open(BASE/'entity_resolution'/'final_operating_entities.json'));entity={e['operating_entity_id']:e for e in entities}
 inputs={json.loads(line)['operating_entity_id']:json.loads(line) for line in (OUT/'rows.jsonl').read_text().splitlines() if line}
 a,b=load_results(OUT/'reviewer_a'),load_results(OUT/'reviewer_b');c=load_results(OUT/'adjudication'/'reviewer_c')
 disagreements={eid for eid in a if any(a[eid][f]!=b[eid][f] for f in FIELDS)}
 if set(a)!=set(inputs) or set(b)!=set(inputs) or set(c)!=disagreements:raise ValueError('review coverage mismatch')
 rows=[]
 for eid in sorted(entity):
  e=entity[eid]
  if eid not in inputs:
   decision={'employee_evidence_status':'none','employee_lower':None,'employee_upper':None,'currentness':'not_applicable','evidence_scope':'not_applicable','descriptive_scale_band':'unknown','owner_only_supported':False,'federal_small_business_representation':'none','supporting_review_ids':[],'evidence_quotes':[],'confidence':'high','rationale':'No pair-level original-page size signal survived the conservative size-evidence screen.'};source='automatic_no_size_signal';quote_status='not_applicable'
  else:
   decision=dict(c[eid] if eid in c else a[eid])
   if eid in c:
    for field in FIELDS:decision[field]=a[eid][field] if a[eid][field]==b[eid][field] else c[eid][field]
   source='fieldwise_C_adjudication' if eid in c else 'AB_semantic_agreement'
   text=' '.join(s['original_size_context'] for s in inputs[eid]['original_page_sources'])
   if any(norm(q) not in norm(text) for q in decision['evidence_quotes']):raise ValueError(f'quote audit: {eid}')
   quote_status='pass'
  rows.append({'operating_entity_id':eid,'corporate_group_id':e['corporate_group_id'],'canonical_name':e['canonical_name'],'domains':'|'.join(e['domains']),'states':'|'.join(e['states']),**{f:decision[f] for f in FIELDS},'supporting_review_ids':'|'.join(decision['supporting_review_ids']),'evidence_quotes':' || '.join(decision['evidence_quotes']),'confidence':decision['confidence'],'rationale':decision['rationale'],'final_source':source,'quote_audit_status':quote_status})
 expected_entities=len(entities)
 if len(rows)!=expected_entities or len({r['operating_entity_id'] for r in rows})!=expected_entities:raise ValueError('entity coverage mismatch')
 out=OUT/'final_entity_size_v0_1.csv'
 with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 agreement={}
 for field in FIELDS:
  left=[a[eid][field] for eid in sorted(a)];right=[b[eid][field] for eid in sorted(a)];agreement[field]={'agree':sum(x==y for x,y in zip(left,right)),'raw':sum(x==y for x,y in zip(left,right))/len(left),'kappa':kappa(left,right)}
 numerical={'exact','approximate','range','lower_bound','upper_bound'}
 federal={'explicit_sam_or_sba_page_claim','named_federal_program_page_claim'}
 summary={'positive_operating_entities':len(rows),'candidate_entities_reviewed':len(inputs),'automatic_no_size_signal_entities':len(rows)-len(inputs),'ab_semantic_disagreements':len(disagreements),'ab_agreement':agreement,'employee_evidence_status':dict(Counter(r['employee_evidence_status'] for r in rows)),'currentness':dict(Counter(r['currentness'] for r in rows)),'evidence_scope':dict(Counter(r['evidence_scope'] for r in rows)),'descriptive_scale_band':dict(Counter(r['descriptive_scale_band'] for r in rows)),'federal_small_business_representation':dict(Counter(r['federal_small_business_representation'] for r in rows)),'entities_with_nonhistorical_numerical_employee_evidence':sum(r['employee_evidence_status'] in numerical for r in rows),'entities_wholly_within_one_descriptive_employee_band':sum(r['descriptive_scale_band'] in {'micro_1_9_supported','small_10_99_supported','mid_100_499_supported','large_500_plus_supported'} for r in rows),'entities_with_current_owner_only_support':sum(r['owner_only_supported'] for r in rows),'entities_with_named_or_explicit_federal_small_business_page_representation':sum(r['federal_small_business_representation'] in federal for r in rows),'external_sba_small_verification_performed':False,'externally_verified_sba_small_entities':None,'quote_audit_eligible_entities':len(inputs),'quote_audit_pass':sum(r['quote_audit_status']=='pass' for r in rows),'quote_audit_fail':sum(r['quote_audit_status']=='fail' for r in rows),'quote_audit_not_applicable':sum(r['quote_audit_status']=='not_applicable' for r in rows),'interpretation_warning':'Descriptive employee bands and page-reported federal representations are not SBA size determinations. Activity-specific NAICS, affiliates, current authoritative registration, and applicable SBA thresholds were not fully verified. External SBA verification was not performed; null is not zero.','final_table_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (OUT/'final_entity_size_summary_v0_1.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
