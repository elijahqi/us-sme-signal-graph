#!/usr/bin/env python3
"""Resolve positive pairs into conservative operating-business entities with audit flags."""
from __future__ import annotations
from collections import defaultdict,Counter
import csv,hashlib,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT/"experiments"/"long_tail_benchmark"/"private"/"formal_v0_3"/"ai_census_v0_4";INPUT=PRIVATE/"full_census_final_v0_1.csv"
SUFFIXES=r"\b(incorporated|inc|corporation|corp|company|co|limited|ltd|llc|l\.?l\.?c|lp|l\.?p|pllc)\b"
ABBREV={"mfg":"manufacturing","mfr":"manufacturing","tech":"technology","technologies":"technology","svc":"service","svcs":"service","assn":"association"}
def norm_name(x):
 x=unicodedata.normalize('NFKC',x).casefold();x=re.sub(r'\([^)]*\)',' ',x);x=re.sub(SUFFIXES,' ',x);t=re.findall(r'[a-z0-9]+',x);t=[ABBREV.get(v,v) for v in t];return ' '.join(t)
def acronym(x):return ''.join(w[0] for w in x.split() if w and w not in {'the','and','of'})
def alias(a,b):
 if not a or not b:return False
 if a==b:return True
 if min(len(a),len(b))>=6 and (a in b or b in a):return True
 if acronym(a)==b.replace(' ','') or acronym(b)==a.replace(' ',''):return True
 return SequenceMatcher(None,a,b).ratio()>=0.91
class UF:
 def __init__(self,n):self.p=list(range(n))
 def find(self,x):
  while self.p[x]!=x:self.p[x]=self.p[self.p[x]];x=self.p[x]
  return x
 def union(self,a,b):
  a,b=self.find(a),self.find(b)
  if a!=b:self.p[b]=a
def main():
 rows=[r for r in csv.DictReader(open(INPUT)) if r['eqdp']=='yes'];nodes=[];by_key={}
 for r in rows:
  key=(r['candidate_id'],r['candidate_business_name'],r['state_id'])
  if key not in by_key:by_key[key]=len(nodes);nodes.append({"candidate_id":r['candidate_id'],"name":r['candidate_business_name'],"norm":norm_name(r['candidate_business_name']),"state":r['state_id'],"domain":r['registrable_domain'],"visibility":r['web_visibility'],"urls":set(),"pairs":[]})
  n=nodes[by_key[key]];n['urls'].add(r['source_url']);n['pairs'].append(r['review_id'])
 uf=UF(len(nodes));reasons=[]
 # Same dedicated domain normally identifies one operating business; flag multi-state/division names for audit later.
 by_domain=defaultdict(list)
 for i,n in enumerate(nodes):by_domain[n['domain']].append(i)
 for d,ids in by_domain.items():
  if all(nodes[i]['visibility']=='dedicated_business_domain' for i in ids):
   for i in ids[1:]:uf.union(ids[0],i);reasons.append((ids[0],i,'same_dedicated_domain'))
 # Exact/strong alias name in same state across domains.
 by_state=defaultdict(list)
 for i,n in enumerate(nodes):by_state[n['state']].append(i)
 ambiguous=[]
 for state,ids in by_state.items():
  for x,a in enumerate(ids):
   for b in ids[x+1:]:
    if nodes[a]['domain']==nodes[b]['domain']:continue
    if nodes[a]['norm']==nodes[b]['norm'] and nodes[a]['norm']:
     uf.union(a,b);reasons.append((a,b,'exact_name_state'))
    elif alias(nodes[a]['norm'],nodes[b]['norm']):
     ambiguous.append({"state":state,"left_id":a,"right_id":b,"left_name":nodes[a]['name'],"right_name":nodes[b]['name'],"left_domain":nodes[a]['domain'],"right_domain":nodes[b]['domain'],"similarity":SequenceMatcher(None,nodes[a]['norm'],nodes[b]['norm']).ratio()})
 groups=defaultdict(list)
 for i,n in enumerate(nodes):groups[uf.find(i)].append(i)
 entities=[]
 for ids in groups.values():
  names=sorted({nodes[i]['name'] for i in ids});domains=sorted({nodes[i]['domain'] for i in ids});states=sorted({nodes[i]['state'] for i in ids});pairs=sorted({p for i in ids for p in nodes[i]['pairs']});urls=sorted({u for i in ids for u in nodes[i]['urls']})
  entity_id='entity-'+hashlib.sha256(('|'.join(domains)+'||'+'|'.join(sorted(norm_name(n) for n in names))+'||'+'|'.join(states)).encode()).hexdigest()[:20]
  flags=[]
  if len(domains)>1:flags.append('cross_domain_merge')
  if len({norm_name(n) for n in names})>1:flags.append('multi_name')
  if len(states)>1:flags.append('multi_state')
  entities.append({"entity_id":entity_id,"canonical_name":min(names,key=len),"names":names,"domains":domains,"states":states,"pair_count":len(pairs),"review_ids":pairs,"source_urls":urls,"audit_flags":flags})
 entities.sort(key=lambda e:e['entity_id']);out=PRIVATE/'entity_resolution';out.mkdir(exist_ok=True)
 (out/'resolved_entities_pre_audit.json').write_text(json.dumps(entities,ensure_ascii=False,indent=2)+'\n');(out/'ambiguous_cross_domain_aliases.json').write_text(json.dumps(ambiguous,ensure_ascii=False,indent=2)+'\n')
 summary={"positive_pairs":len(rows),"positive_candidate_name_state_nodes":len(nodes),"pre_audit_resolved_entities":len(entities),"cross_domain_entities":sum('cross_domain_merge' in e['audit_flags'] for e in entities),"multi_name_entities":sum('multi_name' in e['audit_flags'] for e in entities),"multi_state_entities":sum('multi_state' in e['audit_flags'] for e in entities),"ambiguous_cross_domain_alias_pairs":len(ambiguous),"merge_reason_counts":dict(Counter(r[2] for r in reasons))}
 (out/'global_pre_audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
