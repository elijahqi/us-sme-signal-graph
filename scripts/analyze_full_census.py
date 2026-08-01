#!/usr/bin/env python3
"""Merge v0.3 calibration and v0.4 extension into the complete 6,164-pair census."""
from __future__ import annotations
from collections import Counter,defaultdict
import csv,hashlib,json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/"experiments"/"long_tail_benchmark"/"private"/"formal_v0_3";CAL=BASE/"ai_review_v0_1";EXT=BASE/"ai_census_v0_4"
KEY=("identity_status","direct_producer_status","capability_match","production_presence","commercial_offering","eqdp","primary_exclusion_reason","scale_band","legal_form","web_visibility")
FINAL=("candidate_business_name",)+KEY+("production_city","production_state","confidence","evidence_quote","rationale")
def read_csv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def load(d,expected):
 out={}
 for p in sorted(d.glob('batch-*.json')):
  for r in json.loads(p.read_text())['results']:out[r['review_id']]=r
 if len(out)!=expected:raise ValueError(f'{d}: {len(out)}')
 return out
def kappa(a,b):
 po=sum(x==y for x,y in zip(a,b))/len(a);ca,cb=Counter(a),Counter(b);pe=sum(ca[k]/len(a)*cb[k]/len(b) for k in set(ca)|set(cb));return (po-pe)/(1-pe) if pe<1 else 1
def norm(s):
 s=unicodedata.normalize('NFKC',s).strip().strip('“”"‘’\'').replace('…','...').replace('–','-').replace('—','-');return re.sub(r'\s+',' ',s).casefold()
def main():
 cal_rows=read_csv(CAL/'final_cross_review_v0_1.csv');cal={r['review_id']:r for r in cal_rows}
 evidence={}
 for p in sorted((EXT/'batches').glob('batch-*.json')):
  for r in json.loads(p.read_text())['rows']:evidence[r['review_id']]=r
 a,b=load(EXT/'reviewer_a',4964),load(EXT/'reviewer_b',4964);c=load(EXT/'adjudication'/'reviewer_c',2661)
 disagreements={rid for rid in a if any(a[rid][f]!=b[rid][f] for f in KEY)}
 if disagreements!=set(c):raise ValueError('C coverage mismatch')
 ext=[]
 for rid in sorted(a):
  d=c[rid] if rid in c else a[rid];e=evidence[rid]
  row={"review_id":rid,"candidate_id":e['candidate_id'],"capability_id":e['capability_id'],"industry_family":e['industry_family'],"state_id":e['queried_state_id'],"query_intents":e['query_intents'],"source_url":e['source_url'],"registrable_domain":e['registrable_domain'],"page_sha256":e['page_sha256'],**{f:d[f] for f in FINAL},"final_source":'C_adjudication' if rid in c else 'AB_agreement',"a_eqdp":a[rid]['eqdp'],"b_eqdp":b[rid]['eqdp'],"quote_audit_pass":str(bool(norm(d['evidence_quote'])) and norm(d['evidence_quote']) in norm(e['evidence_excerpt'])).lower()}
  ext.append(row)
 rows=cal_rows+ext
 if len(rows)!=6164 or len({r['review_id'] for r in rows})!=6164:raise ValueError('full census coverage')
 states={r['state_id']:r for r in read_csv(ROOT/'experiments'/'long_tail_benchmark'/'geographies_v0_1.csv')}
 pos=[r for r in rows if r['eqdp']=='yes'];mis=[]
 for r in pos:
  s=states[r['state_id']];actual=r['production_state'].casefold().replace('.','').strip();
  if actual not in {s['state_name'].casefold(),s['state_abbr'].casefold()}:mis.append(r['review_id'])
 if mis:raise ValueError(f'state mismatch {mis}')
 agreement={}
 for f in KEY:
  aa=[a[r][f] for r in sorted(a)];bb=[b[r][f] for r in sorted(a)];agreement[f]={"agree":sum(x==y for x,y in zip(aa,bb)),"raw":sum(x==y for x,y in zip(aa,bb))/len(aa),"kappa":kappa(aa,bb)}
 dims={}
 for d in ['industry_family','state_id']:
  dims[d]={}
  for v in sorted({r[d] for r in rows}):
   sub=[r for r in rows if r[d]==v];dims[d][v]={"rows":len(sub),**Counter(r['eqdp'] for r in sub)}
 intent=Counter()
 for r in rows:
  for x in r['query_intents'].split('|'):intent[(x,r['eqdp'])]+=1
 summary={"pairs":len(rows),"eqdp":dict(Counter(r['eqdp'] for r in rows)),"positive_source_pages":len({r['candidate_id'] for r in pos}),"positive_domains":len({r['registrable_domain'] for r in pos}),"positive_quote_audit_pass":sum(r['quote_audit_pass']=='true' for r in pos),"positive_quote_audit_fail":sum(r['quote_audit_pass']!='true' for r in pos),"positive_state_mismatch":0,"positive_scale":dict(Counter(r['scale_band'] for r in pos)),"positive_legal_form":dict(Counter(r['legal_form'] for r in pos)),"positive_presence":dict(Counter(r['production_presence'] for r in pos)),"exclusions":dict(Counter(r['primary_exclusion_reason'] for r in rows if r['eqdp']!='yes')),"extension_ab_agreement":agreement,"dimensions":dims,"intent_incidence":{f'{k[0]}|{k[1]}':v for k,v in sorted(intent.items())}}
 out=EXT/'full_census_final_v0_1.csv'
 with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary['final_table_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(EXT/'full_census_summary_v0_1.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
