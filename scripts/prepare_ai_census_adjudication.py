#!/usr/bin/env python3
"""Prepare v0.4 census A/B disagreements for C adjudication."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT/"experiments"/"long_tail_benchmark"/"private"/"formal_v0_3"/"ai_census_v0_4"
KEY_FIELDS=("identity_status","direct_producer_status","capability_match","production_presence","commercial_offering","eqdp","primary_exclusion_reason","scale_band","legal_form","web_visibility")
def load(x):
 d={}
 for p in sorted((PRIVATE/f"reviewer_{x}").glob("batch-*.json")):
  for r in json.loads(p.read_text(encoding="utf-8"))["results"]:d[r["review_id"]]=r
 if len(d)!=4964:raise ValueError(f"reviewer {x}: {len(d)}")
 return d
def main():
 evidence={}
 for p in sorted((PRIVATE/"batches").glob("batch-*.json")):
  for r in json.loads(p.read_text(encoding="utf-8"))["rows"]:evidence[r["review_id"]]=r
 a,b=load('a'),load('b');rows=[]
 for rid in sorted(a):
  diff=[f for f in KEY_FIELDS if a[rid][f]!=b[rid][f]]
  if diff:rows.append({"review_id":rid,"differences":diff,"evidence":evidence[rid],"reviewer_a":a[rid],"reviewer_b":b[rid]})
 out=PRIVATE/"adjudication"/"batches";out.mkdir(parents=True,exist_ok=True)
 for old in out.glob('batch-*.json'):old.unlink()
 for i in range(0,len(rows),10):
  n=i//10+1;(out/f"batch-{n:03d}.json").write_text(json.dumps({"batch_id":f"census-adjudication-{n:03d}","rows":rows[i:i+10]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 m={"disagreement_rows":len(rows),"eqdp_disagreement_rows":sum(a[r["review_id"]]["eqdp"]!=b[r["review_id"]]["eqdp"] for r in rows),"batches":(len(rows)+9)//10,"last_batch_size":len(rows)%10}
 (PRIVATE/"adjudication"/"input_manifest.json").write_text(json.dumps(m,indent=2)+"\n");print(json.dumps(m,indent=2))
if __name__=="__main__":main()
