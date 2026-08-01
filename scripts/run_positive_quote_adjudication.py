#!/usr/bin/env python3
"""Run Reviewer C for literal positive-quote re-audit disagreements."""
from __future__ import annotations
import argparse,json,subprocess,time
from pathlib import Path
from run_positive_quote_reaudit import ROOT,SCHEMA,OUT,norm,validate
ADJ=OUT/'adjudication'
def prompt(p):return f"""You are Reviewer C adjudicating two blinded re-audits of provisional manufacturing producer labels. Re-evaluate evidence_excerpt; do not mechanically choose A or B. Use ONLY supplied text. Do not browse or use remembered facts.

EQDP=yes requires all five: operating commercial business; direct production/rebuilding/contract manufacturing; explicit task-capability match; eligible production presence in the queried state; and current commercial offering. Office, warehouse, lab, service area, directory category, planned site, or broad U.S. claim does not prove queried-state production.

For EQDP=yes, evidence_quote MUST be one contiguous exact substring from evidence_excerpt sufficient in its local wording to support the decisive producer/capability/in-state-production claim. Never join clauses, add ellipses, compress, or paraphrase. If no single quote within 600 characters can carry decisive support, use no or unclear. Resolve differing_fields, return every review_id, and match the schema.

BATCH:
{json.dumps(p,ensure_ascii=False)}"""
def run(path,timeout,retries):
 p=json.load(open(path));v={'rows':p['rows']};d=ADJ/'reviewer_c';d.mkdir(parents=True,exist_ok=True);target=d/path.name
 if target.exists():o=json.load(open(target));validate(v,o);return {'batch_id':p['batch_id'],'status':'existing'}
 errs=[]
 for attempt in range(1,retries+2):
  tmp=d/f'.{path.stem}.attempt-{attempt}.json'
  try:
   z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(SCHEMA),'--output-last-message',str(tmp),'-'],input=prompt(p),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
   if z.returncode:raise RuntimeError(z.stderr[-1500:])
   o=json.load(open(tmp));validate(v,o);target.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');tmp.unlink(missing_ok=True);return {'batch_id':p['batch_id'],'status':'accepted','attempt':attempt}
  except Exception as e:errs.append(str(e));tmp.unlink(missing_ok=True);time.sleep(2*attempt) if attempt<=retries else None
 raise RuntimeError(' | '.join(errs))
def main():
 a=argparse.ArgumentParser();a.add_argument('--timeout',type=int,default=900);a.add_argument('--retries',type=int,default=2);x=a.parse_args();m=[]
 for p in sorted((ADJ/'batches').glob('batch-*.json')):r=run(p,x.timeout,x.retries);m.append(r);print(json.dumps(r),flush=True)
 (ADJ/'reviewer_c_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
