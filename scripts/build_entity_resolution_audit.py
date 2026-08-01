#!/usr/bin/env python3
"""Build conservative entity-resolution bounds and an audit queue for positive census pairs."""
from __future__ import annotations
from collections import defaultdict
import csv,hashlib,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT/"experiments"/"long_tail_benchmark"/"private"/"formal_v0_3"/"ai_census_v0_4";INPUT=PRIVATE/"full_census_final_v0_1.csv"
SUFFIXES=r"\b(incorporated|inc|corporation|corp|company|co|limited|ltd|llc|l\.?l\.?c|lp|l\.?p|pllc)\b"
def norm_name(x):
 x=unicodedata.normalize('NFKC',x).casefold();x=re.sub(r'\([^)]*\)',' ',x);x=re.sub(SUFFIXES,' ',x);x=re.sub(r'[^a-z0-9]+',' ',x);return re.sub(r'\s+',' ',x).strip()
def alias(a,b):
 if a==b:return True
 if min(len(a),len(b))>=5 and (a in b or b in a):return True
 return SequenceMatcher(None,a,b).ratio()>=0.88
def clusters(names):
 groups=[]
 for name in sorted(set(names)):
  for g in groups:
   if any(alias(name,x) for x in g):g.add(name);break
  else:groups.append({name})
 changed=True
 while changed:
  changed=False
  for i in range(len(groups)):
   for j in range(i+1,len(groups)):
    if any(alias(a,b) for a in groups[i] for b in groups[j]):groups[i]|=groups[j];groups.pop(j);changed=True;break
   if changed:break
 return groups
def main():
 rows=[r for r in csv.DictReader(open(INPUT)) if r['eqdp']=='yes'];by=defaultdict(list)
 for r in rows:by[r['registrable_domain']].append(r)
 audit=[];auto=[];lower=0;conservative=0
 for domain,rs in sorted(by.items()):
  vis={r['web_visibility'] for r in rs};states=sorted({r['state_id'] for r in rs});raw=sorted({r['candidate_business_name'] for r in rs});norms=[norm_name(x) for x in raw if norm_name(x)];gs=clusters(norms)
  dedicated=vis=={'dedicated_business_domain'}
  lower += 1 if dedicated else len({(norm_name(r['candidate_business_name']),r['state_id']) for r in rs})
  if dedicated and len(gs)==1:
   conservative+=1;status='auto_domain_entity'
  elif dedicated:
   conservative+=len({(norm_name(r['candidate_business_name']),r['state_id']) for r in rs});status='audit_multi_name_domain'
  else:
   conservative+=len({(norm_name(r['candidate_business_name']),r['state_id']) for r in rs});status='audit_non_dedicated_source'
  item={"cluster_id":"cluster-"+hashlib.sha256(domain.encode()).hexdigest()[:16],"domain":domain,"status":status,"visibility":sorted(vis),"states":states,"raw_names":raw,"normalized_name_groups":[sorted(x) for x in gs],"pair_count":len(rs),"source_urls":sorted({r['source_url'] for r in rs})}
  (auto if status=='auto_domain_entity' else audit).append(item)
 upper=len({(norm_name(r['candidate_business_name']),r['state_id'],r['registrable_domain']) for r in rows})
 out=PRIVATE/'entity_resolution';out.mkdir(exist_ok=True)
 (out/'audit_queue.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(out/'auto_clusters.json').write_text(json.dumps(auto,ensure_ascii=False,indent=2)+'\n')
 summary={"positive_pairs":len(rows),"positive_domains":len(by),"auto_domain_clusters":len(auto),"audit_clusters":len(audit),"lower_bound_entities":lower,"pre_audit_conservative_entities":conservative,"upper_bound_name_state_domain_entities":upper,"audit_status_counts":{x:sum(r['status']==x for r in audit) for x in sorted({r['status'] for r in audit})}}
 (out/'pre_audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
