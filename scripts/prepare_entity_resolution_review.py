#!/usr/bin/env python3
"""Prepare all flagged positive entity clusters for provider-blind entity review."""
from __future__ import annotations
import csv,json,hashlib
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT/"experiments"/"long_tail_benchmark"/"private"/"formal_v0_3"/"ai_census_v0_4";INPUT=PRIVATE/"full_census_final_v0_1.csv"
def main():
 rows=[r for r in csv.DictReader(open(INPUT)) if r['eqdp']=='yes'];by=defaultdict(list)
 for r in rows:by[r['registrable_domain']].append(r)
 flagged=[]
 for domain,rs in sorted(by.items()):
  names=sorted({r['candidate_business_name'] for r in rs});states=sorted({r['state_id'] for r in rs});vis=sorted({r['web_visibility'] for r in rs});urls=sorted({r['source_url'] for r in rs})
  if len(names)>1 or len(states)>1 or vis!=['dedicated_business_domain']:
   flagged.append({"cluster_id":"cluster-"+hashlib.sha256(domain.encode()).hexdigest()[:16],"domain":domain,"names":names,"states":states,"visibility":vis,"pair_count":len(rs),"evidence":[{"name":r['candidate_business_name'],"state":r['state_id'],"source_url":r['source_url'],"evidence_quote":r['evidence_quote'],"rationale":r['rationale']} for r in rs]})
 out=PRIVATE/'entity_resolution'/'review_batches';out.mkdir(parents=True,exist_ok=True)
 for old in out.glob('batch-*.json'):old.unlink()
 for i in range(0,len(flagged),10):
  n=i//10+1;(out/f'batch-{n:03d}.json').write_text(json.dumps({"batch_id":f"entity-{n:03d}","clusters":flagged[i:i+10]},ensure_ascii=False,indent=2)+'\n')
 m={"flagged_clusters":len(flagged),"batches":(len(flagged)+9)//10,"last_batch_size":len(flagged)%10};(PRIVATE/'entity_resolution'/'review_input_manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
