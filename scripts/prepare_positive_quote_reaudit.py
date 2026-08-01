#!/usr/bin/env python3
"""Prepare every positive pair whose final quote failed literal excerpt audit."""
from __future__ import annotations
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3';CAL=BASE/'ai_review_v0_1';EXT=BASE/'ai_census_v0_4';OUT=EXT/'positive_quote_reaudit_v0_1'
def main():
 final=list(csv.DictReader(open(EXT/'full_census_final_v0_1.csv')));failed={r['review_id']:r for r in final if r['eqdp']=='yes' and r['quote_audit_pass']!='true'}
 evidence={}
 for root in [CAL/'batches',EXT/'batches']:
  for p in sorted(root.glob('batch-*.json')):
   for r in json.load(open(p))['rows']:evidence[r['review_id']]=r
 if set(failed)-set(evidence):raise ValueError('missing evidence rows')
 rows=[]
 for rid in sorted(failed):
  prior=failed[rid];e=evidence[rid]
  rows.append({'review_id':rid,'candidate_id':prior['candidate_id'],'capability_id':prior['capability_id'],'industry_family':prior['industry_family'],'queried_state_id':prior['state_id'],'query_intents':prior['query_intents'],'source_url':prior['source_url'],'registrable_domain':prior['registrable_domain'],'page_sha256':prior['page_sha256'],'task':e['task'],'queried_state':e['queried_state'],'page_title':e.get('page_title',''),'meta_description':e.get('meta_description',''),'evidence_excerpt':e['evidence_excerpt']})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));b=OUT/'batches';b.mkdir(exist_ok=True)
 for old in b.glob('batch-*.json'):old.unlink()
 for i in range(0,len(rows),10):
  n=i//10+1;(b/f'batch-{n:03d}.json').write_text(json.dumps({'batch_id':f'quote-reaudit-{n:03d}','rows':rows[i:i+10]},ensure_ascii=False,indent=2)+'\n')
 m={'failed_positive_pairs':len(rows),'batches':(len(rows)+9)//10,'last_batch_size':len(rows)%10,'evidence_source':'same_frozen_excerpt_used_for_original_review'};(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
