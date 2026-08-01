#!/usr/bin/env python3
"""Run blinded A/B re-audit with mandatory literal quotes for positive outcomes."""
from __future__ import annotations
import argparse,json,random,re,subprocess,time,unicodedata
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'experiments'/'long_tail_benchmark';OUT=B/'private'/'formal_v0_3'/'ai_census_v0_4'/'positive_quote_reaudit_v0_1';SCHEMA=B/'ai_census_output_schema_v0_1.json'
def norm(s):s=unicodedata.normalize('NFKC',s).strip().strip('“”"‘’\'').replace('…','...').replace('–','-').replace('—','-');return re.sub(r'\s+',' ',s).casefold()
def prompt(reviewer,p):
 rows=list(p['rows']);random.Random(20260803+int(p['batch_id'].rsplit('-',1)[1])).shuffle(rows) if reviewer=='B' else None
 stance='adversarially try to falsify every required component' if reviewer=='B' else 'conservatively require literal support for every component'
 return f"""You are Reviewer {reviewer} re-auditing provisional positive manufacturing producer labels whose earlier quotes were not literal substrings. {stance}. Use ONLY evidence_excerpt. Do not browse, call tools, inspect files, use remembered facts, or trust the prior label.

EQDP=yes only when the excerpt establishes all five: a specific operating commercial business; direct production/rebuilding/contract manufacturing; explicit task-capability match; eligible production presence in the queried state; and current commercial offering. Office, warehouse, lab, service area, directory category, planned site, or broad U.S. claim does not establish production in the queried state. Use unclear for missing evidence and no for supported exclusion.

For EQDP=yes, evidence_quote MUST be one contiguous, exact substring copied from evidence_excerpt and must be sufficient, in its local wording, to support the decisive producer/capability/in-state-production claim. Never join noncontiguous clauses, add ellipses, normalize punctuation, compress, or paraphrase. If no single quote of at most 600 characters can carry that decisive support, EQDP cannot be yes under this re-audit. For no/unclear, keep any quote exact or leave it empty. Return every review_id exactly once and match the schema.

ROWS:
{json.dumps({'batch_id':p['batch_id'],'rows':rows},ensure_ascii=False)}"""
def validate(p,o):
 inp={r['review_id']:r for r in p['rows']};res=o.get('results')
 if not isinstance(res,list) or len(res)!=len(inp) or {r.get('review_id') for r in res}!=set(inp):raise ValueError('coverage')
 for r in res:
  quote=r['evidence_quote'];excerpt=inp[r['review_id']]['evidence_excerpt']
  if quote.strip() and norm(quote) not in norm(excerpt):raise ValueError(f"quote mismatch {r['review_id']}")
  if r['eqdp']=='yes':
   if not quote.strip():raise ValueError('positive without quote')
   if not(r['identity_status']=='yes' and r['direct_producer_status']=='yes' and r['capability_match']=='yes' and r['production_presence'] in {'industrial_facility_confirmed','job_shop_or_workshop_confirmed','owner_or_home_production_confirmed'} and r['commercial_offering']=='yes' and r['primary_exclusion_reason']=='none'):raise ValueError('inconsistent positive')
def run(path,reviewer,timeout,retries):
 p=json.load(open(path));d=OUT/f'reviewer_{reviewer.lower()}';d.mkdir(exist_ok=True);target=d/path.name
 if target.exists():o=json.load(open(target));validate(p,o);return {'batch_id':p['batch_id'],'status':'existing'}
 errs=[]
 for attempt in range(1,retries+2):
  tmp=d/f'.{path.stem}.attempt-{attempt}.json'
  try:
   z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(SCHEMA),'--output-last-message',str(tmp),'-'],input=prompt(reviewer,p),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
   if z.returncode:raise RuntimeError(z.stderr[-1500:])
   o=json.load(open(tmp));validate(p,o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');tmp.unlink(missing_ok=True);return {'batch_id':p['batch_id'],'status':'accepted','attempt':attempt}
  except Exception as e:errs.append(str(e));tmp.unlink(missing_ok=True);time.sleep(2*attempt) if attempt<=retries else None
 raise RuntimeError(f"{p['batch_id']} {reviewer}: {' | '.join(errs)}")
def main():
 a=argparse.ArgumentParser();a.add_argument('--reviewer',choices=['A','B'],required=True);a.add_argument('--workers',type=int,default=4);a.add_argument('--timeout',type=int,default=900);a.add_argument('--retries',type=int,default=2);x=a.parse_args();paths=sorted((OUT/'batches').glob('batch-*.json'));m=[]
 with ThreadPoolExecutor(max_workers=x.workers) as e:
  fs={e.submit(run,p,x.reviewer,x.timeout,x.retries):p for p in paths}
  for i,f in enumerate(as_completed(fs),1):r=f.result();m.append(r);print(json.dumps({'completed':i,'total':len(paths),**r}),flush=True)
 m.sort(key=lambda r:r['batch_id']);(OUT/f'reviewer_{x.reviewer.lower()}_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
