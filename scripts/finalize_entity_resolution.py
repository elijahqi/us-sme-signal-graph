#!/usr/bin/env python3
"""Finalize corporate-group and operating-entity counts from reviewed domain clusters."""
from __future__ import annotations
from collections import defaultdict
import csv,hashlib,json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];P=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3'/'ai_census_v0_4';INPUT=P/'full_census_final_v0_1.csv';ER=P/'entity_resolution'
SUFFIX=r"\b(incorporated|inc|corporation|corp|company|co|limited|ltd|llc|l\.?l\.?c|lp|l\.?p|pllc)\b"
def norm(x):x=unicodedata.normalize('NFKC',x).casefold();x=re.sub(r'\([^)]*\)',' ',x);x=re.sub(SUFFIX,' ',x);return re.sub(r'[^a-z0-9]+',' ',x).strip()
def stable_id(prefix, values):
 return prefix+'-'+hashlib.sha256('||'.join(sorted(values)).encode()).hexdigest()[:20]
class UF:
 def __init__(self,n):self.p=list(range(n))
 def find(self,x):
  while self.p[x]!=x:self.p[x]=self.p[self.p[x]];x=self.p[x]
  return x
 def union(self,a,b):
  a,b=self.find(a),self.find(b)
  if a!=b:self.p[b]=a
def main():
 rows=[r for r in csv.DictReader(open(INPUT)) if r['eqdp']=='yes'];by=defaultdict(list)
 for r in rows:by[r['registrable_domain']].append(r)
 decisions={}
 for f in sorted((ER/'review_results').glob('batch-*.json')):
  for d in json.load(open(f))['decisions']:decisions[d['cluster_id']]=d
 audit={x['domain']:x for x in json.load(open(ER/'audit_queue.json'))}
 op=[];corp=[];name_to_op=defaultdict(list);review_to_op={}
 for domain,rs in sorted(by.items()):
  raw_names=sorted({r['candidate_business_name'] for r in rs});states_by_name=defaultdict(set)
  for r in rs:states_by_name[r['candidate_business_name']].add(r['state_id'])
  cluster=next((x for x in audit.values() if x['domain']==domain),None)
  decision=decisions.get(cluster['cluster_id']) if cluster else None
  groups=decision['merge_groups'] if decision else [raw_names]
  flattened=[name for group in groups for name in group]
  if sorted(flattened)!=raw_names:raise ValueError(f'invalid merge group coverage for {domain}')
  if decision and (decision['operating_entity_count']!=len(groups)):raise ValueError(f'operating count mismatch for {domain}')
  corp_ids=[]
  if not decision or decision['decision']=='single_operating_entity':corp_ids=[len(corp)]*len(groups);corp.append({'domain':domain,'groups':list(range(len(groups)))})
  elif decision['decision']=='single_corporate_multiple_operating_entities':corp_ids=[len(corp)]*len(groups);corp.append({'domain':domain,'groups':list(range(len(groups)))})
  else:
   for i in range(len(groups)):corp_ids.append(len(corp));corp.append({'domain':domain,'groups':[i]})
  for gi,g in enumerate(groups):
   oid=len(op);states=sorted({s for name in g for s in states_by_name.get(name,set())});op.append({'domain':domain,'names':g,'states':states,'corp':corp_ids[gi]})
   for name in g:name_to_op[(domain,name)].append(oid)
   for r in rs:
    if r['candidate_business_name'] in g:review_to_op[r['review_id']]=oid
 opuf,corpuf=UF(len(op)),UF(len(corp));exact_edges=[]
 # exact normalized-name + state across domains
 index=defaultdict(list)
 for i,u in enumerate(op):
  for name in u['names']:
   for state in u['states']:index[(norm(name),state)].append(i)
 for key,ids in index.items():
  domains={op[i]['domain'] for i in ids}
  if len(domains)>1:
   for i in ids[1:]:opuf.union(ids[0],i);corpuf.union(op[ids[0]]['corp'],op[i]['corp']);exact_edges.append((ids[0],i,key))
 review=json.load(open(ER/'cross_domain_alias_review.json'));inputs={x['pair_id']:x for x in review['input_pairs']};unresolved=[]
 for d in review['decisions']:
  x=inputs[d['pair_id']];left=name_to_op.get((x['left_domain'],x['left_name']),[]);right=name_to_op.get((x['right_domain'],x['right_name']),[])
  if not left or not right:continue
  if d['same_operating_entity']=='yes':opuf.union(left[0],right[0]);corpuf.union(op[left[0]]['corp'],op[right[0]]['corp'])
  elif d['same_corporate_group']=='yes':corpuf.union(op[left[0]]['corp'],op[right[0]]['corp'])
  elif d['same_operating_entity']=='unclear' or d['same_corporate_group']=='unclear':unresolved.append(d['pair_id'])
 op_count=len({opuf.find(i) for i in range(len(op))});corp_count=len({corpuf.find(i) for i in range(len(corp))})
 if set(review_to_op)!={r['review_id'] for r in rows}:raise ValueError('positive review mapping mismatch')
 op_groups=defaultdict(list);corp_groups=defaultdict(list)
 for i in range(len(op)):op_groups[opuf.find(i)].append(i)
 for i in range(len(corp)):corp_groups[corpuf.find(i)].append(i)
 op_ids={root:stable_id('operating-entity',[f"{op[i]['domain']}|{name}" for i in ids for name in op[i]['names']]) for root,ids in op_groups.items()}
 corp_ids_final={root:stable_id('corporate-group',[f"{corp[i]['domain']}|{i}" for i in ids]) for root,ids in corp_groups.items()}
 unresolved_op_roots=set();unresolved_corp_roots=set()
 for pair_id in unresolved:
  x=inputs[pair_id];left=name_to_op[(x['left_domain'],x['left_name'])][0];right=name_to_op[(x['right_domain'],x['right_name'])][0]
  unresolved_op_roots.update([opuf.find(left),opuf.find(right)]);unresolved_corp_roots.update([corpuf.find(op[left]['corp']),corpuf.find(op[right]['corp'])])
 final_entities=[]
 for root,ids in sorted(op_groups.items(),key=lambda item:op_ids[item[0]]):
  review_ids=sorted(rid for rid,oid in review_to_op.items() if opuf.find(oid)==root)
  source_rows=[r for r in rows if r['review_id'] in set(review_ids)]
  corporate_root=corpuf.find(op[ids[0]]['corp'])
  final_entities.append({'operating_entity_id':op_ids[root],'corporate_group_id':corp_ids_final[corporate_root],'canonical_name':min({name for i in ids for name in op[i]['names']},key=len),'names':sorted({name for i in ids for name in op[i]['names']}),'domains':sorted({op[i]['domain'] for i in ids}),'states':sorted({state for i in ids for state in op[i]['states']}),'positive_pair_count':len(review_ids),'review_ids':review_ids,'source_urls':sorted({r['source_url'] for r in source_rows}),'unresolved_cross_domain_relationship':root in unresolved_op_roots})
 mapping=[]
 entity_by_root={opuf.find(root):entity for root,entity in [(root,next(e for e in final_entities if e['operating_entity_id']==op_ids[root])) for root in op_groups]}
 for r in sorted(rows,key=lambda row:row['review_id']):
  root=opuf.find(review_to_op[r['review_id']]);entity=entity_by_root[root]
  mapping.append({'review_id':r['review_id'],'candidate_id':r['candidate_id'],'operating_entity_id':entity['operating_entity_id'],'corporate_group_id':entity['corporate_group_id'],'candidate_business_name':r['candidate_business_name'],'registrable_domain':r['registrable_domain'],'state_id':r['state_id']})
 # Each unresolved pair could reduce one count; report conservative no-merge point and lower range.
 summary={'positive_pairs':len(rows),'reviewed_domain_clusters':len(by),'pre_cross_domain_operating_units':len(op),'pre_cross_domain_corporate_units':len(corp),'auto_exact_cross_domain_edges':len(exact_edges),'provisional_operating_entity_clusters':op_count,'provisional_corporate_group_clusters':corp_count,'unresolved_cross_domain_pairs':len(unresolved),'unresolved_pair_sensitivity_operating_clusters':[max(1,op_count-len(unresolved)),op_count],'unresolved_pair_sensitivity_corporate_clusters':[max(1,corp_count-len(unresolved)),corp_count],'point_estimate_policy':'do not merge unresolved pairs','external_entity_resolution_precision_audit_completed':False}
 (ER/'final_operating_entities.json').write_text(json.dumps(final_entities,ensure_ascii=False,indent=2)+'\n')
 with (ER/'positive_pair_entity_mapping.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(mapping[0]));w.writeheader();w.writerows(mapping)
 summary['operating_entities_sha256']=hashlib.sha256((ER/'final_operating_entities.json').read_bytes()).hexdigest();summary['pair_mapping_sha256']=hashlib.sha256((ER/'positive_pair_entity_mapping.csv').read_bytes()).hexdigest()
 (ER/'final_entity_resolution_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
