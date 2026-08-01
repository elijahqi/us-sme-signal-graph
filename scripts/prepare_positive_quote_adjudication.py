#!/usr/bin/env python3
"""Prepare semantic disagreements from the literal positive-quote re-audit."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3'/'ai_census_v0_4'/'positive_quote_reaudit_v0_1';FIELDS=('identity_status','direct_producer_status','capability_match','production_presence','commercial_offering','eqdp','primary_exclusion_reason','scale_band','legal_form','web_visibility')
def load(d):
 o={}
 for f in sorted(d.glob('batch-*.json')):
  for r in json.load(open(f))['results']:o[r['review_id']]=r
 return o
def main():
 src={json.loads(x)['review_id']:json.loads(x) for x in (OUT/'rows.jsonl').read_text().splitlines() if x};a,b=load(OUT/'reviewer_a'),load(OUT/'reviewer_b')
 rows=[];counts={f:0 for f in FIELDS}
 for rid in sorted(src):
  diff=[f for f in FIELDS if a[rid][f]!=b[rid][f]]
  if not diff:continue
  for f in diff:counts[f]+=1
  rows.append({**src[rid],'differing_fields':diff,'reviewer_a':a[rid],'reviewer_b':b[rid]})
 d=OUT/'adjudication';bt=d/'batches';bt.mkdir(parents=True,exist_ok=True)
 for old in bt.glob('batch-*.json'):old.unlink()
 for i in range(0,len(rows),10):
  n=i//10+1;(bt/f'batch-{n:03d}.json').write_text(json.dumps({'batch_id':f'quote-c-{n:03d}','rows':rows[i:i+10]},ensure_ascii=False,indent=2)+'\n')
 m={'reviewed_rows':len(src),'semantic_disagreements':len(rows),'eqdp_disagreements':sum(a[r]['eqdp']!=b[r]['eqdp'] for r in src),'field_counts':counts,'batches':(len(rows)+9)//10};(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
