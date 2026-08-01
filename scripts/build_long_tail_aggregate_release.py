#!/usr/bin/env python3
"""Build a row-free exploratory aggregate package for the long-tail evidence audit."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];PRIVATE=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3';OUT=ROOT/'release'/'public'/'long-tail-evidence-audit-v0.1-exploratory'
FILES={
 'retrieval_aggregate.json':PRIVATE/'aggregate_snapshot.json',
 'calibration_aggregate.json':PRIVATE/'ai_review_v0_1'/'cross_review_summary_v0_1.json',
 'constructed_corpus_aggregate.json':PRIVATE/'ai_census_v0_4'/'full_census_summary_v0_1.json',
 'provisional_entity_aggregate.json':PRIVATE/'ai_census_v0_4'/'entity_resolution'/'final_entity_resolution_summary.json',
 'pair_size_aggregate.json':PRIVATE/'ai_census_v0_4'/'size_evidence_v0_2'/'final_size_evidence_summary_v0_2.json',
 'entity_size_aggregate.json':PRIVATE/'ai_census_v0_4'/'entity_size_v0_1'/'final_entity_size_summary_v0_1.json',
}
FORBIDDEN_KEYS={'candidate_business_name','source_url','canonical_url','evidence_quote','rationale','registrable_domain','review_id','candidate_id'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def scan(value,path='root'):
 if isinstance(value,dict):
  for k,v in value.items():
   if k.casefold() in FORBIDDEN_KEYS:raise ValueError(f'forbidden aggregate key {path}.{k}')
   scan(v,f'{path}.{k}')
 elif isinstance(value,list):
  for i,v in enumerate(value):scan(v,f'{path}[{i}]')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 for dst,src in FILES.items():
  data=json.loads(src.read_text());scan(data);(OUT/dst).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 readme='''# Long-tail manufacturing evidence audit v0.1 (exploratory)

This row-free aggregate package accompanies the exploratory, same-model evidence audit. It is not a validated benchmark, supplier directory, company dataset, or SME list. Human double annotation and the preregistered entity-resolution precision audit remain incomplete.

Included files contain aggregate counts, agreement statistics, protocol warnings, and SHA-256 fingerprints of private row-level artifacts. They do not include company rows, destination-page text, provider payloads, titles, snippets, ranks, or model rationales. Hashes identify exact private artifact bytes but do not make those closed artifacts independently auditable.

The query lattice, schemas, code, manuscript draft, and deviation log are maintained in the repository.
''';(OUT/'README.md').write_text(readme)
 manifest={'release_version':'long-tail-evidence-audit-v0.1-exploratory','validated_benchmark':False,'human_expert_validation':False,'external_entity_resolution_precision_audit':False,'row_level_company_data':False,'provider_payloads':False,'third_party_page_text':False,'files':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in {'release_manifest.json','SHA256SUMS'}}};(OUT/'release_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 files=[OUT/name for name in sorted([*FILES,'README.md','release_manifest.json'])];(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));print(json.dumps(manifest,indent=2,sort_keys=True))
if __name__=='__main__':main()
