#!/usr/bin/env python3
"""Run A/B GPT-5.6-Sol reviews for the v0.4 census extension."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import random
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3" / "ai_census_v0_4"
SCHEMA = BENCHMARK / "ai_census_output_schema_v0_1.json"


def make_prompt(reviewer: str, payload: dict) -> str:
    rows = list(payload["rows"])
    if reviewer == "B":
        random.Random(20260731 + int(payload["batch_id"].split("-")[1])).shuffle(rows)
        stance = "Act as an adversarial falsification reviewer; prefer unclear over unsupported completion."
    else:
        stance = "Act as a conservative evidence-first reviewer; apply every criterion literally."
    return f"""
You are Reviewer {reviewer} in a blinded manufacturing-producer census study. {stance}
Use ONLY the frozen evidence below. Do not browse, call tools, inspect files, or use remembered company facts. Provider and rank are absent.

EQDP=yes only when evidence establishes an operating commercial business, direct production/rebuilding/contract manufacturing, explicit capability match, eligible production presence in the queried state, and current commercial offering. Office, service-area, directory category, listicle, planned site, or broad sector claims do not prove production. Empty or insufficient evidence must remain no/unclear with the appropriate exclusion reason. Scale and legal form require explicit evidence and otherwise are unknown.

Return exactly one result for every supplied review_id, no extras or omissions. Keep evidence_quote short and verbatim. Never repeat a residential street address. Return JSON matching the schema.

FROZEN BATCH:
{json.dumps({"batch_id": payload["batch_id"], "rows": rows}, ensure_ascii=False)}
""".strip()


def validate(payload: dict, output: dict) -> None:
    expected = {row["review_id"] for row in payload["rows"]}; results = output.get("results")
    if not isinstance(results, list) or len(results) != len(expected): raise ValueError("result count mismatch")
    actual = [row.get("review_id") for row in results]
    if len(actual) != len(set(actual)) or set(actual) != expected: raise ValueError("review ID coverage mismatch")
    for row in results:
        if row["eqdp"] == "yes" and not (row["identity_status"] == "yes" and row["direct_producer_status"] == "yes" and row["capability_match"] == "yes" and row["production_presence"] in {"industrial_facility_confirmed", "job_shop_or_workshop_confirmed", "owner_or_home_production_confirmed"} and row["commercial_offering"] == "yes" and row["primary_exclusion_reason"] == "none"):
            raise ValueError(f"inconsistent positive: {row['review_id']}")


def run(path: Path, reviewer: str, timeout: int, retries: int) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8")); output_dir = PRIVATE / f"reviewer_{reviewer.lower()}"; output_dir.mkdir(parents=True, exist_ok=True); target = output_dir / path.name
    if target.exists(): out=json.loads(target.read_text(encoding="utf-8"));validate(payload,out);return {"batch_id":payload["batch_id"],"status":"existing"}
    errors=[]
    for attempt in range(1,retries+2):
        last=output_dir/f".{path.stem}.attempt-{attempt}.json"
        try:
            result=subprocess.run(["traecli","exec","--model","GPT-5.6-Sol","--ephemeral","--json","--color","never","--skip-git-repo-check","--sandbox","read-only","-C",str(ROOT),"--output-schema",str(SCHEMA),"--output-last-message",str(last),"-"],input=make_prompt(reviewer,payload),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
            if result.returncode: raise RuntimeError(result.stderr[-2000:])
            out=json.loads(last.read_text(encoding="utf-8"));validate(payload,out);target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");last.unlink(missing_ok=True);return {"batch_id":payload["batch_id"],"status":"accepted","attempt":attempt}
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}");last.unlink(missing_ok=True)
            if attempt<=retries:time.sleep(2*attempt)
    raise RuntimeError(f"{payload['batch_id']} reviewer {reviewer} failed: {' | '.join(errors)}")


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--reviewer",choices=["A","B"],required=True);parser.add_argument("--start",type=int,default=1);parser.add_argument("--end",type=int,default=497);parser.add_argument("--workers",type=int,default=6);parser.add_argument("--timeout",type=int,default=900);parser.add_argument("--retries",type=int,default=1);args=parser.parse_args()
    batches=[PRIVATE/"batches"/f"batch-{n:03d}.json" for n in range(args.start,args.end+1)];manifest=[]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures={executor.submit(run,b,args.reviewer,args.timeout,args.retries):b for b in batches}
        for index,future in enumerate(as_completed(futures),1):row=future.result();manifest.append(row);print(json.dumps({"completed":index,"total":len(batches),**row}),flush=True)
    manifest.sort(key=lambda r:r["batch_id"]);(PRIVATE/f"reviewer_{args.reviewer.lower()}_manifest_{args.start:03d}_{args.end:03d}.json").write_text(json.dumps(manifest,indent=2)+"\n")


if __name__=="__main__":main()
