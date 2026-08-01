#!/usr/bin/env python3
"""Run blinded A/B size-evidence reviews over original-page-only contexts."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import random
import re
import subprocess
import time
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = (
    BENCHMARK
    / "private"
    / "formal_v0_3"
    / "ai_census_v0_4"
    / "size_evidence_v0_2"
)
SCHEMA = BENCHMARK / "size_evidence_output_schema_v0_1.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    return re.sub(r"\s+", " ", value).strip().casefold()


def make_prompt(reviewer: str, payload: dict) -> str:
    rows = list(payload["rows"])
    if reviewer == "B":
        random.Random(20260801 + int(payload["batch_id"].rsplit("-", 1)[1])).shuffle(rows)
        stance = "Act as an adversarial falsification reviewer; reject indirect or ambiguous size language."
    else:
        stance = "Act as a conservative evidence-first reviewer; apply every rule literally."
    return f"""
You are Reviewer {reviewer} in a blinded firm-size evidence study. {stance}
Use ONLY each row's original_size_context. Do not browse, call tools, inspect files, or use remembered company facts.

This task measures whether the frozen original page itself contains direct firm-size evidence. Production capability, facility square footage, revenue, years in business, production volume, family ownership, an owner's name, a team page, job openings, employee benefits, the word "employees", and customer or industry statistics do NOT establish headcount. A number near "employees" counts only when the text explicitly says it is the focal business's current or clearly stated employee/headcount total, range, lower bound, or upper bound. Do not infer company headcount by counting named people or openings. Use employee_range only when both numeric inclusive endpoints are stated or directly implied. Use employee_lower_bound for open-ended phrases such as "more than 70 employees" and employee_upper_bound for phrases such as "fewer than 50 employees"; never invent the missing endpoint.

owner_only_or_nonemployer_explicit requires explicit text that the focal business has no paid employees, is a nonemployer, or is operated only by the owner(s). "Family-owned" and "owned and operated by X" are insufficient. sba_self_certification_explicit requires an explicit small-business representation tied to SBA, SAM.gov, or an equivalent U.S. federal contracting registration; generic "small business" marketing is insufficient.

For supported evidence, copy a short exact quote from original_size_context. Do not add ellipses or paraphrase. For insufficient evidence, use null employee bounds, false support booleans, and an empty evidence_quote. Return exactly one result for every review_id, with no extras or omissions, matching the JSON schema.

FROZEN ORIGINAL-PAGE BATCH:
{json.dumps({"batch_id": payload["batch_id"], "rows": rows}, ensure_ascii=False)}
""".strip()


def validate(payload: dict, output: dict) -> None:
    inputs = {row["review_id"]: row for row in payload["rows"]}
    results = output.get("results")
    if not isinstance(results, list) or len(results) != len(inputs):
        raise ValueError("result count mismatch")
    actual = [row.get("review_id") for row in results]
    if len(actual) != len(set(actual)) or set(actual) != set(inputs):
        raise ValueError("review ID coverage mismatch")
    for row in results:
        status = row["size_evidence_status"]
        lower, upper = row["employee_lower"], row["employee_upper"]
        owner, sba = row["owner_only_supported"], row["sba_status_supported"]
        quote = row["evidence_quote"]
        if status == "insufficient":
            if lower is not None or upper is not None or owner or sba or quote.strip():
                raise ValueError(f"inconsistent insufficient result: {row['review_id']}")
            continue
        if not quote.strip() or normalize(quote) not in normalize(inputs[row["review_id"]]["original_size_context"]):
            raise ValueError(f"unsupported evidence quote: {row['review_id']}")
        if status == "exact_employee_count":
            if lower is None or upper is None or lower != upper:
                raise ValueError(f"invalid exact count: {row['review_id']}")
        elif status == "employee_range":
            if lower is None or upper is None or lower > upper:
                raise ValueError(f"invalid employee range: {row['review_id']}")
        elif status == "employee_lower_bound":
            if lower is None or upper is not None:
                raise ValueError(f"invalid employee lower bound: {row['review_id']}")
        elif status == "employee_upper_bound":
            if lower is not None or upper is None:
                raise ValueError(f"invalid employee upper bound: {row['review_id']}")
        elif status == "owner_only_or_nonemployer_explicit":
            if lower is not None or upper is not None or not owner:
                raise ValueError(f"invalid owner-only evidence: {row['review_id']}")
        elif status == "sba_self_certification_explicit":
            if lower is not None or upper is not None or not sba:
                raise ValueError(f"invalid SBA evidence: {row['review_id']}")


def run(path: Path, reviewer: str, timeout: int, retries: int) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    output_dir = PRIVATE / f"reviewer_{reviewer.lower()}"
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / path.name
    if target.exists():
        output = json.loads(target.read_text(encoding="utf-8"))
        validate(payload, output)
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
                input=make_prompt(reviewer, payload),
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
            )
            if result.returncode:
                raise RuntimeError(result.stderr[-2000:])
            output = json.loads(last.read_text(encoding="utf-8"))
            validate(payload, output)
            target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            last.unlink(missing_ok=True)
            return {"batch_id": payload["batch_id"], "status": "accepted", "attempt": attempt}
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            last.unlink(missing_ok=True)
            if attempt <= retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"{payload['batch_id']} reviewer {reviewer} failed: {' | '.join(errors)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer", choices=["A", "B"], required=True)
    parser.add_argument("--start", type=int, default=1)
    default_end = int(json.loads((PRIVATE / "manifest.json").read_text())["batches"])
    parser.add_argument("--end", type=int, default=default_end)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    paths = [PRIVATE / "batches" / f"batch-{number:03d}.json" for number in range(args.start, args.end + 1)]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing batches: {missing}")
    manifest = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run, path, args.reviewer, args.timeout, args.retries): path for path in paths}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            manifest.append(row)
            print(json.dumps({"completed": index, "total": len(paths), **row}), flush=True)
    manifest.sort(key=lambda row: row["batch_id"])
    (PRIVATE / f"reviewer_{args.reviewer.lower()}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
