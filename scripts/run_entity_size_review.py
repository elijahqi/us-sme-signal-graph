#!/usr/bin/env python3
"""Run blinded A/B operating-entity size evidence reviews."""
from __future__ import annotations
import argparse,json,random,re,subprocess,time,unicodedata
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'experiments'/'long_tail_benchmark';OUT=B/'private'/'formal_v0_3'/'ai_census_v0_4'/'entity_size_v0_1';SCHEMA=B/'entity_size_output_schema_v0_1.json'
def norm(x):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',x).replace('“','"').replace('”','"').replace('’',"'")).strip().casefold()
def prompt(reviewer,payload):
 rows=list(payload['rows']);random.Random(20260802+int(payload['batch_id'].rsplit('-',1)[1])).shuffle(rows) if reviewer=='B' else None
 stance='adversarially test currentness, scope, and approximation' if reviewer=='B' else 'apply the evidence rules conservatively'
 return f"""You are Reviewer {reviewer} in a blinded operating-entity size-evidence audit. {stance}. Use ONLY original_page_sources. Do not browse, call tools, inspect files, or use remembered facts. Prior pair labels are intentionally absent.

Consolidate all supplied pages for each operating entity. Employee evidence must refer to the focal operating entity, not customers, an industry, a family of companies, or an unidentified facility. Distinguish present/current language, undated present-tense claims, clearly historical narratives, and ambiguous timing. Preserve exact, approximate, two-sided range, lower-bound, and upper-bound semantics; never turn "approximately/nearly" into exact or invent an endpoint. Contradictory but compatible current claims should yield the tightest defensible interval; incompatible claims make timing or scope ambiguous.

Assign a descriptive scale band only when the evidence bounds the entity wholly within it: owner-only; 1-9; 10-99; 100-499; or 500+. If a valid interval/lower bound crosses bands, use bounded_but_crosses_bands. Historical-only or ambiguous-scope evidence yields unknown. These are study bands, not SBA legal determinations.

Federal status is only a page-reported representation: explicit_sam_or_sba_page_claim for text explicitly naming SAM.gov or SBA status; named_federal_program_page_claim for WOSB/HUBZone or a named federal small-business program without an explicit current SAM/SBA statement; generic_or_ambiguous_claim for generic small-business language. Do not call any claim verified, current, or legally dispositive.

Copy up to four short exact quotes, each from a supplied original_size_context, and list only review IDs that actually support the final decision. Return every operating_entity_id exactly once and match the schema.

ROWS:
{json.dumps({'batch_id':payload['batch_id'],'rows':rows},ensure_ascii=False)}"""
def validate(payload,out):
 inp={r['operating_entity_id']:r for r in payload['rows']};res=out.get('results')
 if not isinstance(res,list) or len(res)!=len(inp) or {r.get('operating_entity_id') for r in res}!=set(inp):raise ValueError('coverage')
 for r in res:
  src=inp[r['operating_entity_id']];ids=set(src['candidate_review_ids'])
  if not set(r['supporting_review_ids'])<=ids:raise ValueError('supporting ID not supplied')
  text=' '.join(s['original_size_context'] for s in src['original_page_sources'])
  if any(not q.strip() or norm(q) not in norm(text) for q in r['evidence_quotes']):raise ValueError('quote audit')
  lo,hi=r['employee_lower'],r['employee_upper'];status=r['employee_evidence_status']
  if status=='exact' and (lo is None or hi is None or lo!=hi):raise ValueError('exact bounds')
  if status in {'approximate','range'} and (lo is None or hi is None or lo>hi):raise ValueError('bounded evidence')
  if status=='lower_bound' and (lo is None or hi is not None):raise ValueError('lower bound')
  if status=='upper_bound' and (lo is not None or hi is None):raise ValueError('upper bound')
  if status in {'historical_only','ambiguous_scope'}:
   if lo is not None and hi is not None and lo>hi:raise ValueError('invalid retained bounds')
   if r['descriptive_scale_band']!='unknown':raise ValueError('historical or ambiguous evidence cannot set current scale')
  if status=='historical_only' and r['currentness']!='historical':raise ValueError('historical currentness mismatch')
  if status=='none' and (lo is not None or hi is not None):raise ValueError('unsupported bounds')
  if r['owner_only_supported'] and r['descriptive_scale_band']!='owner_only_supported':raise ValueError('owner band')
def run(path,reviewer,timeout,retries):
 p=json.loads(path.read_text());d=OUT/f'reviewer_{reviewer.lower()}';d.mkdir(exist_ok=True);target=d/path.name
 if target.exists():o=json.loads(target.read_text());validate(p,o);return {'batch_id':p['batch_id'],'status':'existing'}
 errs=[]
 for attempt in range(1,retries+2):
  tmp=d/f'.{path.stem}.attempt-{attempt}.json'
  try:
   z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(SCHEMA),'--output-last-message',str(tmp),'-'],input=prompt(reviewer,p),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
   if z.returncode:raise RuntimeError(z.stderr[-1500:])
   o=json.loads(tmp.read_text());validate(p,o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');tmp.unlink(missing_ok=True);return {'batch_id':p['batch_id'],'status':'accepted','attempt':attempt}
  except Exception as e:errs.append(str(e));tmp.unlink(missing_ok=True);time.sleep(2*attempt) if attempt<=retries else None
 raise RuntimeError(f"{p['batch_id']} {reviewer}: {' | '.join(errs)}")
def main():
 a=argparse.ArgumentParser();a.add_argument('--reviewer',choices=['A','B'],required=True);a.add_argument('--workers',type=int,default=4);a.add_argument('--timeout',type=int,default=900);a.add_argument('--retries',type=int,default=2);x=a.parse_args();paths=sorted((OUT/'batches').glob('batch-*.json'));m=[]
 with ThreadPoolExecutor(max_workers=x.workers) as e:
  fs={e.submit(run,p,x.reviewer,x.timeout,x.retries):p for p in paths}
  for i,f in enumerate(as_completed(fs),1):r=f.result();m.append(r);print(json.dumps({'completed':i,'total':len(paths),**r}),flush=True)
 m.sort(key=lambda r:r['batch_id']);(OUT/f'reviewer_{x.reviewer.lower()}_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
