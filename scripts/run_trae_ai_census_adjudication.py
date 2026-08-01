#!/usr/bin/env python3
"""Run Reviewer C for v0.4 census disagreements."""
from __future__ import annotations
import argparse,json,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];BENCHMARK=ROOT/"experiments"/"long_tail_benchmark";PRIVATE=BENCHMARK/"private"/"formal_v0_3"/"ai_census_v0_4"/"adjudication";SCHEMA=BENCHMARK/"ai_adjudication_output_schema_v0_1.json"
def prompt(p):return f"""You are Reviewer C adjudicating two independent evidence reviews. Use ONLY the frozen evidence; do not browse, call tools, inspect files, or use outside company knowledge. Re-evaluate each row rather than mechanically choosing a reviewer. EQDP=yes requires operating commercial business, direct production/rebuilding/contract manufacturing, explicit capability match, eligible production presence in the queried state, and current commercial offering. Missing state-production evidence prevents yes. Use no for supported exclusions and unclear for insufficient evidence. Scale and legal form remain unknown without explicit support. Return exactly every review_id, resolve listed differences, keep quotes short and verbatim, and match the JSON schema.\n\nBATCH:\n{json.dumps(p,ensure_ascii=False)}"""
def validate(p,o):
 e={r['review_id'] for r in p['rows']};r=o.get('results')
 if not isinstance(r,list) or len(r)!=len(e) or {x.get('review_id') for x in r}!=e:raise ValueError('coverage mismatch')
 for x in r:
  if x['eqdp']=='yes' and not(x['identity_status']=='yes' and x['direct_producer_status']=='yes' and x['capability_match']=='yes' and x['production_presence'] in {'industrial_facility_confirmed','job_shop_or_workshop_confirmed','owner_or_home_production_confirmed'} and x['commercial_offering']=='yes' and x['primary_exclusion_reason']=='none'):raise ValueError('inconsistent positive')
def run(path,timeout,retries):
 p=json.loads(path.read_text());out=PRIVATE/'reviewer_c';out.mkdir(parents=True,exist_ok=True);target=out/path.name
 if target.exists():o=json.loads(target.read_text());validate(p,o);return {'batch_id':p['batch_id'],'status':'existing'}
 err=[]
 for attempt in range(1,retries+2):
  last=out/f'.{path.stem}.attempt-{attempt}.json'
  try:
   z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(SCHEMA),'--output-last-message',str(last),'-'],input=prompt(p),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
   if z.returncode:raise RuntimeError(z.stderr[-2000:])
   o=json.loads(last.read_text());validate(p,o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');last.unlink(missing_ok=True);return {'batch_id':p['batch_id'],'status':'accepted','attempt':attempt}
  except Exception as x:err.append(str(x));last.unlink(missing_ok=True);time.sleep(2*attempt) if attempt<=retries else None
 raise RuntimeError(f"{p['batch_id']}: {' | '.join(err)}")
def main():
 a=argparse.ArgumentParser();a.add_argument('--workers',type=int,default=6);a.add_argument('--timeout',type=int,default=900);a.add_argument('--retries',type=int,default=1);x=a.parse_args();b=sorted((PRIVATE/'batches').glob('batch-*.json'));m=[]
 with ThreadPoolExecutor(max_workers=x.workers) as e:
  fs={e.submit(run,p,x.timeout,x.retries):p for p in b}
  for i,f in enumerate(as_completed(fs),1):r=f.result();m.append(r);print(json.dumps({'completed':i,'total':len(b),**r}),flush=True)
 m.sort(key=lambda r:r['batch_id']);(PRIVATE/'reviewer_c_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=="__main__":main()
