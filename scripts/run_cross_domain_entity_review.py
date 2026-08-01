#!/usr/bin/env python3
"""Review plausible cross-domain aliases without allowing fuzzy over-merges."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'experiments'/'long_tail_benchmark';P=B/'private'/'formal_v0_3'/'ai_census_v0_4'/'entity_resolution';S=B/'cross_domain_entity_schema_v0_1.json'
def main():
 pairs=json.loads((P/'ambiguous_cross_domain_aliases.json').read_text());dedup=[];seen=set()
 for x in pairs:
  key=tuple(sorted([(x['left_name'],x['left_domain']),(x['right_name'],x['right_domain'])]))+(x['state'],)
  if key in seen:continue
  seen.add(key);dedup.append({"pair_id":"pair-"+hashlib.sha256(repr(key).encode()).hexdigest()[:16],**{k:x[k] for k in ['state','left_name','right_name','left_domain','right_domain','similarity']}})
 prompt=f"""You are auditing plausible cross-domain business-name aliases. Use only supplied names, domains, state, and similarity. Do not browse or infer affiliation from generic shared words such as Foam, Metal, Products, Manufacturing, or Electric Motors. same_operating_entity=yes requires strong evidence that the records name the same operating business (clear spelling variant, DBA, acronym expansion, or exact distinctive name). same_corporate_group may be yes while operating entity is no only when a parent/division relationship is explicit in the names. If uncertain, use unclear; avoid over-merging unrelated firms. Return every pair_id.\n\nPAIRS:\n{json.dumps(dedup,ensure_ascii=False)}"""
 out=P/'cross_domain_alias_review.json';tmp=P/'.cross_domain_alias_review.tmp.json'
 z=subprocess.run(['traecli','exec','--model','GPT-5.6-Sol','--ephemeral','--json','--color','never','--skip-git-repo-check','--sandbox','read-only','-C',str(ROOT),'--output-schema',str(S),'--output-last-message',str(tmp),'-'],input=prompt,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=900)
 if z.returncode:raise SystemExit(z.stderr[-2000:])
 r=json.loads(tmp.read_text());expected={x['pair_id'] for x in dedup}
 if {x['pair_id'] for x in r['decisions']}!=expected:raise ValueError('coverage mismatch')
 out.write_text(json.dumps({"input_pairs":dedup,**r},ensure_ascii=False,indent=2)+'\n');tmp.unlink(missing_ok=True);print(json.dumps({"pairs":len(dedup),"same_operating_yes":sum(x['same_operating_entity']=='yes' for x in r['decisions']),"unclear":sum(x['same_operating_entity']=='unclear' for x in r['decisions'])},indent=2))
if __name__=='__main__':main()
