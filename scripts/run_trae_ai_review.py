#!/usr/bin/env python3
"""Run reproducible TraeCLI headless cross-review batches."""

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
PRIVATE = BENCHMARK / "private" / "formal_v0_3" / "ai_review_v0_1"
SCHEMA = BENCHMARK / "ai_review_output_schema_v0_1.json"
MODEL = "GPT-5.6-Sol"
KEY_FIELDS = (
    "identity_status", "direct_producer_status", "capability_match",
    "production_presence", "commercial_offering", "eqdp",
    "primary_exclusion_reason", "scale_band", "legal_form", "web_visibility",
)


def reviewer_prompt(reviewer: str, payload: dict) -> str:
    rows = list(payload["rows"])
    if reviewer == "B":
        random.Random(20260730 + int(payload["batch_id"].split("-")[1])).shuffle(rows)
        stance = (
            "Act as an adversarial falsification reviewer. Demand explicit evidence for every positive "
            "component and prefer unclear over filling gaps from general knowledge."
        )
    else:
        stance = (
            "Act as a conservative evidence-first reviewer. Apply every criterion literally and do not "
            "reward plausible but unsupported claims."
        )
    return f"""
You are Reviewer {reviewer} in a blinded supplier-discovery evidence study. {stance}

Decide all 10 rows using ONLY the supplied frozen evidence. Do not browse, call tools, inspect other files, or use remembered facts about a company. Do not infer that a business is small, a manufacturer, or located in the queried state from its name. Search provider and rank are intentionally absent.

EQDP is yes only if the evidence establishes all five: a specific operating commercial business; direct production/rebuilding/contract-manufacturing role; explicit task-capability match; eligible production presence in the queried state; and current commercial offering. A headquarters, office, warehouse, lab, directory category page, listicle, news article, planned site, or broad sector claim is insufficient unless the evidence directly establishes the required facts. If the excerpt is empty, broken, or insufficient, use unclear/source_unavailable or insufficient_evidence.

Production presence allowed positives: industrial_facility_confirmed, job_shop_or_workshop_confirmed, owner_or_home_production_confirmed. Never publish or repeat a residential street address.

Scale band and legal form require explicit support in the evidence. Otherwise use unknown. An employee estimate or phrases such as family-owned may support a research scale band only when explicitly stated; they do not establish SBA status.

Return exactly one result for every supplied review_id, no extra IDs and no missing IDs. Keep evidence_quote short and verbatim. Keep rationale specific to what is and is not proven. Return JSON matching the supplied schema.

FROZEN BATCH:
{json.dumps({"batch_id": payload["batch_id"], "rows": rows}, ensure_ascii=False)}
""".strip()


def validate(payload: dict, output: dict) -> None:
    expected = {row["review_id"] for row in payload["rows"]}
    results = output.get("results")
    if not isinstance(results, list) or len(results) != 10:
        raise ValueError("output must contain exactly 10 results")
    actual = [row.get("review_id") for row in results]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError(f"review ID coverage mismatch: expected={expected}, actual={actual}")
    for row in results:
        if row["eqdp"] == "yes":
            if not (
                row["identity_status"] == "yes"
                and row["direct_producer_status"] == "yes"
                and row["capability_match"] == "yes"
                and row["production_presence"] in {
                    "industrial_facility_confirmed", "job_shop_or_workshop_confirmed",
                    "owner_or_home_production_confirmed",
                }
                and row["commercial_offering"] == "yes"
                and row["primary_exclusion_reason"] == "none"
            ):
                raise ValueError(f"inconsistent EQDP positive: {row['review_id']}")


def run_batch(batch_path: Path, reviewer: str, timeout: int, retries: int) -> dict:
    payload = json.loads(batch_path.read_text(encoding="utf-8"))
    output_dir = PRIVATE / f"reviewer_{reviewer.lower()}"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / batch_path.name
    if result_path.exists():
        output = json.loads(result_path.read_text(encoding="utf-8"))
        validate(payload, output)
        return {"batch_id": payload["batch_id"], "status": "existing"}
    prompt = reviewer_prompt(reviewer, payload)
    errors = []
    for attempt in range(1, retries + 2):
        last_message = output_dir / f".{batch_path.stem}.attempt-{attempt}.json"
        events = output_dir / f".{batch_path.stem}.attempt-{attempt}.jsonl"
        command = [
            "traecli", "exec", "--model", MODEL, "--ephemeral", "--json",
            "--color", "never", "--skip-git-repo-check", "--sandbox", "read-only",
            "-C", str(ROOT), "--output-schema", str(SCHEMA),
            "--output-last-message", str(last_message), "-",
        ]
        try:
            completed = subprocess.run(
                command, input=prompt, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=timeout,
            )
            events.write_text(completed.stdout, encoding="utf-8")
            if completed.returncode:
                raise RuntimeError(completed.stderr[-2000:])
            output = json.loads(last_message.read_text(encoding="utf-8"))
            validate(payload, output)
            result_path.write_text(
                json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return {
                "batch_id": payload["batch_id"], "status": "accepted",
                "attempt": attempt,
            }
        except Exception as exc:
            errors.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
            last_message.unlink(missing_ok=True)
            if attempt <= retries:
                time.sleep(attempt * 2)
    raise RuntimeError(f"{payload['batch_id']} reviewer {reviewer} failed: {' | '.join(errors)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer", choices=["A", "B"], required=True)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=120)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=1)
    args = parser.parse_args()
    batches = [PRIVATE / "batches" / f"batch-{number:03d}.json" for number in range(args.start, args.end + 1)]
    manifest = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_batch, batch, args.reviewer, args.timeout, args.retries): batch
            for batch in batches
        }
        for index, future in enumerate(as_completed(futures), 1):
            result = future.result()
            manifest.append(result)
            print(json.dumps({"completed": index, "total": len(batches), **result}), flush=True)
    manifest.sort(key=lambda row: row["batch_id"])
    path = PRIVATE / f"reviewer_{args.reviewer.lower()}_manifest_{args.start:03d}_{args.end:03d}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
