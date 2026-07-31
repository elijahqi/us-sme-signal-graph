#!/usr/bin/env python3
"""Adjudicate A/B disagreements with a third GPT-5.6-Sol headless pass."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3" / "ai_review_v0_1" / "adjudication"
SCHEMA = BENCHMARK / "ai_adjudication_output_schema_v0_1.json"


def prompt(payload: dict) -> str:
    return f"""
You are Reviewer C, the evidence adjudicator in a supplier-discovery study. The rows below were independently reviewed twice with the same frozen evidence. You see both decisions only to identify and resolve their disagreements. Do not browse, call tools, inspect files, or use outside knowledge. Re-evaluate each row from the frozen evidence; do not split the difference mechanically and do not assume either reviewer is senior.

EQDP is yes only when evidence proves: operating commercial business, direct producer/rebuilder/contract manufacturer, explicit capability match, eligible production presence in the queried state, and current commercial offering. Missing queried-state production evidence prevents yes. Use no where evidence affirmatively supports an exclusion; use unclear where the evidence is insufficient to decide. Scale and legal form remain unknown without explicit evidence.

Return exactly one result for every review_id in this batch. Preserve agreed fields when supported, resolve every listed difference, keep quotes verbatim and short, and provide a specific final rationale. Output JSON matching the schema.

ADJUDICATION BATCH:
{json.dumps(payload, ensure_ascii=False)}
""".strip()


def validate(payload: dict, output: dict) -> None:
    expected = {row["review_id"] for row in payload["rows"]}
    results = output.get("results")
    if not isinstance(results, list) or len(results) != len(expected):
        raise ValueError("result count mismatch")
    actual = [row.get("review_id") for row in results]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("review ID coverage mismatch")
    for row in results:
        if row["eqdp"] == "yes" and not (
            row["identity_status"] == "yes" and row["direct_producer_status"] == "yes"
            and row["capability_match"] == "yes"
            and row["production_presence"] in {"industrial_facility_confirmed", "job_shop_or_workshop_confirmed", "owner_or_home_production_confirmed"}
            and row["commercial_offering"] == "yes" and row["primary_exclusion_reason"] == "none"
        ):
            raise ValueError(f"inconsistent positive: {row['review_id']}")


def run(path: Path, timeout: int, retries: int) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    output_dir = PRIVATE / "reviewer_c"
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / path.name
    if target.exists():
        out = json.loads(target.read_text(encoding="utf-8")); validate(payload, out)
        return {"batch_id": payload["batch_id"], "status": "existing"}
    errors = []
    for attempt in range(1, retries + 2):
        last = output_dir / f".{path.stem}.attempt-{attempt}.json"
        try:
            result = subprocess.run([
                "traecli", "exec", "--model", "GPT-5.6-Sol", "--ephemeral",
                "--json", "--color", "never", "--skip-git-repo-check",
                "--sandbox", "read-only", "-C", str(ROOT), "--output-schema",
                str(SCHEMA), "--output-last-message", str(last), "-",
            ], input=prompt(payload), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            if result.returncode:
                raise RuntimeError(result.stderr[-2000:])
            out = json.loads(last.read_text(encoding="utf-8")); validate(payload, out)
            target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            last.unlink(missing_ok=True)
            return {"batch_id": payload["batch_id"], "status": "accepted", "attempt": attempt}
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}"); last.unlink(missing_ok=True)
            if attempt <= retries: time.sleep(2 * attempt)
    raise RuntimeError(f"{payload['batch_id']} failed: {' | '.join(errors)}")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--workers", type=int, default=4); parser.add_argument("--timeout", type=int, default=900); parser.add_argument("--retries", type=int, default=1); args = parser.parse_args()
    batches = sorted((PRIVATE / "batches").glob("batch-*.json")); manifest = []
    if not batches:
        raise SystemExit("No adjudication batches found; run prepare_ai_adjudication.py first")
    (PRIVATE / "reviewer_c").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run, batch, args.timeout, args.retries): batch for batch in batches}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result(); manifest.append(row); print(json.dumps({"completed": index, "total": len(batches), **row}), flush=True)
    manifest.sort(key=lambda row: row["batch_id"]); (PRIVATE / "reviewer_c_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__": main()
