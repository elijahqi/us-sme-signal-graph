#!/usr/bin/env python3
"""Prepare all key-field A/B disagreements for a third blinded evidence adjudication."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "long_tail_benchmark" / "private" / "formal_v0_3" / "ai_review_v0_1"
KEY_FIELDS = ("identity_status", "direct_producer_status", "capability_match", "production_presence", "commercial_offering", "eqdp", "primary_exclusion_reason", "scale_band", "legal_form", "web_visibility")


def load_results(reviewer: str) -> dict[str, dict]:
    results = {}
    for path in sorted((PRIVATE / f"reviewer_{reviewer}").glob("batch-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["results"]:
            if row["review_id"] in results:
                raise ValueError(f"duplicate {reviewer} review ID: {row['review_id']}")
            results[row["review_id"]] = row
    if len(results) != 1200:
        raise ValueError(f"reviewer {reviewer} has {len(results)} rows, expected 1200")
    return results


def prepare() -> dict:
    evidence = {}
    for path in sorted((PRIVATE / "batches").glob("batch-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload["rows"]:
            if row["review_id"] in evidence:
                raise ValueError(f"duplicate evidence review ID: {row['review_id']}")
            evidence[row["review_id"]] = row
    if len(evidence) != 1200:
        raise ValueError(f"evidence batches contain {len(evidence)} rows, expected 1200")
    a, b = load_results("a"), load_results("b")
    if set(a) != set(b) or set(a) != set(evidence):
        raise ValueError("A/B/evidence ID coverage mismatch")
    rows = []
    for review_id in sorted(a):
        differences = [field for field in KEY_FIELDS if a[review_id][field] != b[review_id][field]]
        if not differences:
            continue
        rows.append({
            "review_id": review_id,
            "differences": differences,
            "evidence": evidence[review_id],
            "reviewer_a": a[review_id],
            "reviewer_b": b[review_id],
        })
    output = PRIVATE / "adjudication" / "batches"
    output.mkdir(parents=True, exist_ok=True)
    for old in output.glob("batch-*.json"):
        old.unlink()
    for index in range(0, len(rows), 10):
        number = index // 10 + 1
        payload = {"batch_id": f"adjudication-{number:03d}", "rows": rows[index:index+10]}
        (output / f"batch-{number:03d}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "disagreement_rows": len(rows),
        "eqdp_disagreement_rows": sum(a[row["review_id"]]["eqdp"] != b[row["review_id"]]["eqdp"] for row in rows),
        "batches": (len(rows) + 9) // 10,
        "key_fields": list(KEY_FIELDS),
        "evidence_source": "frozen_batch_json",
    }
    (PRIVATE / "adjudication" / "input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
