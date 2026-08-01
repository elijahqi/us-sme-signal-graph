#!/usr/bin/env python3
"""Run a conservative GPT-5.6-Sol review of flagged entity clusters."""
from __future__ import annotations
import json,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'experiments'/'long_tail_benchmark';P=B/'private'/'formal_v0_3'/'ai_census_v0_4'/'entity_resolution';S=B/'entity_resolution_output_schema_v0_1.json'
def prompt(p):return f"""You are auditing entity resolution for U.S. manufacturing producer records. Use ONLY supplied names, states, URLs, quotes, and rationales; do not browse or use external facts. Separate three levels: corporate group, operating entity/division, and production site. A shared domain may cover multiple divisions; a directory domain may contain unrelated companies. Minor Inc/LLC/punctuation/abbreviation variants are aliases. Different state facilities of the same operating company do not automatically create new operating entities, but explicitly named divisions may. Return every cluster_id. merge_groups must partition the supplied raw names into operating-entity groups; each raw name must appear exactly once. If evidence cannot resolve the relationship, choose unresolved and use a conservative count justified by the supplied records.\n\nCLUSTERS:\n{json.dumps(p,ensure_ascii=False)}"""
def validate(p,o):
 expected={x['cluster_id'] for x in p['clusters']};d=o.get('decisions')
 if not isinstance(d,list) or len(d)!=len(expected) or {x.get('cluster_id') for x in d}!=expected:raise ValueError('coverage mismatch')
 raw={x['cluster_id']:x['names'] for x in p['clusters']}
 for x in d:
  names=[n for g in x['merge_groups'] for n in g]
  if sorted(names)!=sorted(raw[x['cluster_id']]) or len(names)!=len(set(names)):raise ValueError('merge_groups do not partition names')
  if x['operating_entity_count']!=len(x['merge_groups']):raise ValueError('operating count mismatch')
def run(path):
 p=json.loads(path.read_text());out=P/'review_results';out.mkdir(exist_ok=True);target=out/path.name
 if target.exists():o=json.loads(target.read_text());validate(p,o);return p['batch_id'],'existing',1
 for a in [1,2]:
  last=out/f'.{path.stem}.{a}.json'
  try:
   z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(S),'--output-last-message',str(last),'-'],input=prompt(p),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=900)
   if z.returncode:raise RuntimeError(z.stderr[-1000:])
   o=json.loads(last.read_text());validate(p,o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');last.unlink(missing_ok=True);return p['batch_id'],'accepted',a
  except Exception:last.unlink(missing_ok=True);time.sleep(2*a)
 raise RuntimeError(p['batch_id'])
def main():
 files=sorted((P/'review_batches').glob('batch-*.json'))
 with ThreadPoolExecutor(max_workers=4) as e:
  fs=[e.submit(run,p) for p in files]
  for i,f in enumerate(as_completed(fs),1):bid,status,a=f.result();print(json.dumps({"completed":i,"total":len(files),"batch_id":bid,"status":status,"attempt":a}),flush=True)
if __name__=='__main__':main()
