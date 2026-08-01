#!/usr/bin/env python3
"""Fail closed on restricted fields or stale hashes in the exploratory aggregate package."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release'/'public'/'long-tail-evidence-audit-v0.1-exploratory';FORBIDDEN_KEYS={'candidate_business_name','source_url','canonical_url','evidence_quote','rationale','registrable_domain','review_id','candidate_id'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scan(value,path='root'):
 if isinstance(value,dict):
  for k,v in value.items():
   if k.casefold() in FORBIDDEN_KEYS:raise ValueError(f'restricted key {path}.{k}')
   scan(v,f'{path}.{k}')
 elif isinstance(value,list):
  for i,v in enumerate(value):scan(v,f'{path}[{i}]')
 elif isinstance(value,str) and ('http://' in value.casefold() or 'https://' in value.casefold()):raise ValueError(f'URL content at {path}')
def main():
 manifest=json.loads((OUT/'release_manifest.json').read_text())
 if manifest['validated_benchmark'] or manifest['human_expert_validation'] or manifest['row_level_company_data']:raise ValueError('unsafe manifest claim')
 for name,digest in manifest['files'].items():
  p=OUT/name
  if not p.exists() or sha(p)!=digest:raise ValueError(f'stale manifest hash: {name}')
 for p in OUT.glob('*.json'):scan(json.loads(p.read_text()),p.name)
 expected={}
 for line in (OUT/'SHA256SUMS').read_text().splitlines():digest,name=line.split('  ',1);expected[name]=digest
 for name,digest in expected.items():
  if sha(OUT/name)!=digest:raise ValueError(f'stale SHA256SUMS: {name}')
 print(f'validated {len(expected)} row-free aggregate release files')
if __name__=='__main__':main()
