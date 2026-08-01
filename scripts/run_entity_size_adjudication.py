#!/usr/bin/env python3
"""Adjudicate operating-entity size evidence disagreements."""
from __future__ import annotations
import argparse,json,subprocess,time
from pathlib import Path
from run_entity_size_review import ROOT,SCHEMA,OUT,validate

ADJ=OUT/'adjudication'
def prompt(p):return f"""You are Reviewer C adjudicating two blinded operating-entity size-evidence reviews. Re-evaluate the original_page_sources; do not mechanically choose A or B. Use ONLY supplied text, never browse or use outside facts.

Employee evidence must refer to the focal operating entity. Preserve exact vs approximate vs range vs lower/upper bound. For integer language, "over 80" means a lower bound of 81 and "over 1,500" means 1,501. A dated old source is historical_only for current classification even if it supplies a historical bound. Present-tense official company text is undated_present_tense unless it explicitly says today/currently/now. Approximate values may support a descriptive band only when the approximation is sufficiently far from a band boundary to remain wholly within it; explain the judgment. Generic uses of "small" that do not assert federal status are federal representation none.

Study bands are owner-only, 1-9, 10-99, 100-499, and 500+. They are not SBA determinations. SAM.gov/SBA wording is only an explicit page claim; WOSB/HUBZone is only a named-program page claim; neither is externally verified. Copy exact quotes, return every operating_entity_id, and match the schema.

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
 a=argparse.ArgumentParser();a.add_argument('--timeout',type=int,default=900);a.add_argument('--retries',type=int,default=2);x=a.parse_args();rows=[]
 for p in sorted((ADJ/'batches').glob('batch-*.json')):r=run(p,x.timeout,x.retries);rows.append(r);print(json.dumps(r),flush=True)
 (ADJ/'reviewer_c_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
