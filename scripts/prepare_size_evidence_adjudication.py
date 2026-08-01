#!/usr/bin/env python3
"""Prepare Reviewer C batches for semantic A/B size-evidence disagreements."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = (
    ROOT / "experiments" / "long_tail_benchmark" / "private" / "formal_v0_3"
    / "ai_census_v0_4" / "size_evidence_v0_2"
)
SEMANTIC_FIELDS = (
    "size_evidence_status", "employee_lower", "employee_upper",
    "owner_only_supported", "sba_status_supported",
)


def load_reviews(directory: Path) -> dict[str, dict]:
    reviews = {}
    for path in sorted(directory.glob("batch-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["results"]:
            if row["review_id"] in reviews:
                raise ValueError(f"duplicate review ID: {row['review_id']}")
            reviews[row["review_id"]] = row
    return reviews


def main() -> None:
    source_rows = {}
    for path in sorted((PRIVATE / "batches").glob("batch-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]:
            source_rows[row["review_id"]] = row
    reviewer_a = load_reviews(PRIVATE / "reviewer_a")
    reviewer_b = load_reviews(PRIVATE / "reviewer_b")
    if set(reviewer_a) != set(source_rows) or set(reviewer_b) != set(source_rows):
        raise ValueError("A/B coverage does not match nonempty original-page contexts")
    disagreements = []
    field_counts = {field: 0 for field in SEMANTIC_FIELDS}
    for review_id in sorted(source_rows):
        differing = [field for field in SEMANTIC_FIELDS if reviewer_a[review_id][field] != reviewer_b[review_id][field]]
        if not differing:
            continue
        for field in differing:
            field_counts[field] += 1
        disagreements.append({
            **source_rows[review_id],
            "differing_fields": differing,
            "reviewer_a": reviewer_a[review_id],
            "reviewer_b": reviewer_b[review_id],
        })
    adjudication = PRIVATE / "adjudication"
    batches = adjudication / "batches"
    batches.mkdir(parents=True, exist_ok=True)
    for old in batches.glob("batch-*.json"):
        old.unlink()
    for index in range(0, len(disagreements), 10):
        number = index // 10 + 1
        payload = {"batch_id": f"size-c-{number:03d}", "rows": disagreements[index:index + 10]}
        (batches / f"batch-{number:03d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    manifest = {
        "nonempty_context_rows": len(source_rows),
        "semantic_disagreements": len(disagreements),
        "semantic_agreements": len(source_rows) - len(disagreements),
        "field_disagreement_counts": field_counts,
        "batches": (len(disagreements) + 9) // 10,
        "last_batch_size": len(disagreements) % 10 if disagreements else 0,
    }
    (adjudication / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
