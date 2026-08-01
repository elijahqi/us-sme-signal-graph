#!/usr/bin/env python3
"""Prepare original-context-only operating-entity size review batches."""
from __future__ import annotations
from collections import defaultdict
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3'/'ai_census_v0_4';SIZE=BASE/'size_evidence_v0_2';OUT=BASE/'entity_size_v0_1'
def main():
 mapping={r['review_id']:r for r in csv.DictReader(open(BASE/'entity_resolution'/'positive_pair_entity_mapping.csv'))}
 entities={e['operating_entity_id']:e for e in json.load(open(BASE/'entity_resolution'/'final_operating_entities.json'))}
 contexts={r['review_id']:r for r in (json.loads(line) for line in (SIZE/'rows.jsonl').read_text().splitlines() if line)}
 pair_results=list(csv.DictReader(open(SIZE/'final_size_evidence_v0_2.csv')));candidate_ids={r['review_id'] for r in pair_results if r['size_evidence_status']!='insufficient'}
 by=defaultdict(list)
 for rid in sorted(candidate_ids):
  m=mapping[rid];c=contexts[rid];by[m['operating_entity_id']].append({'review_id':rid,'candidate_id':c['candidate_id'],'source_url':c['source_url'],'page_sha256':c['page_sha256'],'original_size_context':c['original_size_context']})
 rows=[]
 for eid,items in sorted(by.items()):
  e=entities[eid];seen=set();sources=[]
  for item in items:
   key=(item['page_sha256'],item['original_size_context'])
   if key in seen:continue
   seen.add(key);sources.append(item)
  rows.append({'operating_entity_id':eid,'canonical_name':e['canonical_name'],'known_names':e['names'],'domains':e['domains'],'states':e['states'],'candidate_review_ids':sorted(x['review_id'] for x in items),'original_page_sources':sources})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 batches=OUT/'batches';batches.mkdir(exist_ok=True)
 for old in batches.glob('batch-*.json'):old.unlink()
 for i in range(0,len(rows),8):
  n=i//8+1;(batches/f'batch-{n:03d}.json').write_text(json.dumps({'batch_id':f'entity-size-{n:03d}','rows':rows[i:i+8]},ensure_ascii=False,indent=2)+'\n')
 manifest={'positive_operating_entities':len(entities),'candidate_entities_with_pair_level_size_signal':len(rows),'automatic_insufficient_entities':len(entities)-len(rows),'batches':(len(rows)+7)//8,'context_source':'frozen_original_page_visible_text_only','selection_rule':'at_least_one_pair_level_non_insufficient_signal'};(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
