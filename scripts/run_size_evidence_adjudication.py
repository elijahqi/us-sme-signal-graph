#!/usr/bin/env python3
"""Run Reviewer C over A/B size-evidence disagreements."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import time

from audit_positive_size_evidence import ROOT, SCHEMA, normalize, validate


PRIVATE = (
    ROOT / "experiments" / "long_tail_benchmark" / "private" / "formal_v0_3"
    / "ai_census_v0_4" / "size_evidence_v0_2" / "adjudication"
)


def make_prompt(payload: dict) -> str:
    return f"""
You are Reviewer C adjudicating two blinded firm-size evidence reviews. Re-evaluate the original_size_context yourself; do not mechanically choose A or B. Use ONLY the supplied original-page context and the two reviews. Do not browse, call tools, inspect files, or use remembered company facts.

A current or clearly stated employee count, range, lower bound, or upper bound must explicitly refer to the focal business. Use employee_range only when both numeric inclusive endpoints are stated or directly implied; use employee_lower_bound or employee_upper_bound when one endpoint is genuinely open, and never invent the other endpoint. The words employees, staff, team, workers, or people without an actual firm-level number are insufficient. Facility size, revenue, years, production volume, ownership, team pages, job openings, and benefits do not establish headcount. owner-only/nonemployer evidence requires explicit no-paid-employee or owner-only operation language. SBA evidence requires an explicit SBA, SAM.gov, or equivalent federal small-business representation; generic "small business" is insufficient.

For supported evidence, copy a short exact quote from original_size_context without ellipses or paraphrase. For insufficient evidence, return null bounds, false booleans, and an empty quote. Resolve the semantic fields listed in differing_fields, return exactly every review_id, and match the JSON schema.

ADJUDICATION BATCH:
{json.dumps(payload, ensure_ascii=False)}
""".strip()


def run(path: Path, timeout: int, retries: int) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation_payload = {"rows": payload["rows"]}
    output_dir = PRIVATE / "reviewer_c"
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / path.name
    if target.exists():
        output = json.loads(target.read_text(encoding="utf-8"))
        validate(validation_payload, output)
        return {"batch_id": payload["batch_id"], "status": "existing"}
    errors = []
    for attempt in range(1, retries + 2):
        last = output_dir / f".{path.stem}.attempt-{attempt}.json"
        try:
            result = subprocess.run(
                [
                    "traecli", "exec", "--model", "GPT-5.6-Sol",
                    "--ephemeral", "--json", "--color", "never",
                    "--skip-git-repo-check", "--sandbox", "read-only",
                    "-C", str(ROOT), "--output-schema", str(SCHEMA),
                    "--output-last-message", str(last), "-",
                ],
                input=make_prompt(payload), text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=timeout,
            )
            if result.returncode:
                raise RuntimeError(result.stderr[-2000:])
            output = json.loads(last.read_text(encoding="utf-8"))
            validate(validation_payload, output)
            target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            last.unlink(missing_ok=True)
            return {"batch_id": payload["batch_id"], "status": "accepted", "attempt": attempt}
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            last.unlink(missing_ok=True)
            if attempt <= retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"{payload['batch_id']} Reviewer C failed: {' | '.join(errors)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    paths = sorted((PRIVATE / "batches").glob("batch-*.json"))
    manifest = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run, path, args.timeout, args.retries): path for path in paths}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            manifest.append(row)
            print(json.dumps({"completed": index, "total": len(paths), **row}), flush=True)
    manifest.sort(key=lambda row: row["batch_id"])
    (PRIVATE / "reviewer_c_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
