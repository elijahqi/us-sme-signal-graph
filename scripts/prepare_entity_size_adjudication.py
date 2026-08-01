#!/usr/bin/env python3
"""Prepare operating-entity size evidence disagreements for Reviewer C."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3'/'ai_census_v0_4'/'entity_size_v0_1'
FIELDS=('employee_evidence_status','employee_lower','employee_upper','currentness','evidence_scope','descriptive_scale_band','owner_only_supported','federal_small_business_representation')
def load_results(path):
 out={}
 for f in sorted(path.glob('batch-*.json')):
  for r in json.load(open(f))['results']:out[r['operating_entity_id']]=r
 return out
def main():
 src={}
 for f in sorted((OUT/'batches').glob('batch-*.json')):
  for r in json.load(open(f))['rows']:src[r['operating_entity_id']]=r
 a,b=load_results(OUT/'reviewer_a'),load_results(OUT/'reviewer_b')
 if set(a)!=set(src) or set(b)!=set(src):raise ValueError('A/B coverage')
 rows=[];counts={f:0 for f in FIELDS}
 for eid in sorted(src):
  diff=[f for f in FIELDS if a[eid][f]!=b[eid][f]]
  if not diff:continue
  for f in diff:counts[f]+=1
  rows.append({**src[eid],'differing_fields':diff,'reviewer_a':a[eid],'reviewer_b':b[eid]})
 d=OUT/'adjudication';batches=d/'batches';batches.mkdir(parents=True,exist_ok=True)
 for old in batches.glob('batch-*.json'):old.unlink()
 for i in range(0,len(rows),8):
  n=i//8+1;(batches/f'batch-{n:03d}.json').write_text(json.dumps({'batch_id':f'entity-size-c-{n:03d}','rows':rows[i:i+8]},ensure_ascii=False,indent=2)+'\n')
 m={'reviewed_candidate_entities':len(src),'semantic_disagreements':len(rows),'semantic_agreements':len(src)-len(rows),'field_disagreement_counts':counts,'batches':(len(rows)+7)//8};(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
