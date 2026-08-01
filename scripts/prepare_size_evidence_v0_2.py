#!/usr/bin/env python3
"""Build size-only contexts directly from frozen original-page visible text."""
from __future__ import annotations
import csv,json,re,sys
from pathlib import Path
SCRIPT=Path(__file__).resolve().parent
if str(SCRIPT) not in sys.path:sys.path.insert(0,str(SCRIPT))
from prepare_ai_review_batches import visible_text

ROOT=Path(__file__).resolve().parents[1];P=ROOT/'experiments'/'long_tail_benchmark'/'private'/'formal_v0_3';C=P/'ai_census_v0_4';OUT=C/'size_evidence_v0_2'
TERMS=[r'\bemployees?\b',r'\bheadcount\b',r'\bworkforce\b',r'\bstaff(?:ed|ing)?\b',r'\bteam members?\b',r'\bworkers?\b',r'\bpeople\b',r'\bassociates?\b',r'\bone[- ](?:man|person|woman)\b',r'\bowner[- ]only\b',r'\bnonemployer\b',r'\bno paid employees\b',r'\bsole proprietor\b',r'\bself[- ]certif(?:y|ied|ication)\b',r'\bsmall business search\b',r'\bsam\.gov\b',r'\bsba\b']
PAT=re.compile('|'.join(f'(?:{x})' for x in TERMS),re.I)
def windows(text,limit=8000):
 spans=[]
 for m in PAT.finditer(text):spans.append((max(0,m.start()-500),min(len(text),m.end()+900)))
 if not spans:return ''
 spans.sort();merged=[]
 for a,b in spans:
  if merged and a<=merged[-1][1]+100:merged[-1]=(merged[-1][0],max(merged[-1][1],b))
  else:merged.append((a,b))
 out=[];used=0
 for a,b in merged:
  x=text[a:b].strip();n=min(len(x),limit-used)
  if n<=0:break
  out.append(x[:n]);used+=n
 return '\n[...]\n'.join(out)
def main():
 positives=[r for r in csv.DictReader(open(C/'full_census_final_v0_1.csv')) if r['eqdp']=='yes'];rows=[]
 for r in positives:
  text=visible_text(P/'source_pages'/f"{r['candidate_id']}.html")
  rows.append({"review_id":r['review_id'],"candidate_id":r['candidate_id'],"business_name":r['candidate_business_name'],"state":r['state_id'],"source_url":r['source_url'],"page_sha256":r['page_sha256'],"original_size_context":windows(text)})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'rows.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8');non=[x for x in rows if x['original_size_context']];b=OUT/'batches';b.mkdir(exist_ok=True)
 for old in b.glob('batch-*.json'):old.unlink()
 for i in range(0,len(non),10):n=i//10+1;(b/f'batch-{n:03d}.json').write_text(json.dumps({"batch_id":f"size-v2-{n:03d}","rows":non[i:i+10]},ensure_ascii=False,indent=2)+'\n')
 m={"positive_pairs":len(rows),"nonempty_original_size_contexts":len(non),"auto_insufficient_empty_contexts":len(rows)-len(non),"batches":(len(non)+9)//10,"last_batch_size":len(non)%10,"context_source":"frozen_original_page_visible_text_only"};(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
