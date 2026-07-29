#!/usr/bin/env python3
"""Join frozen independent-source decisions to Reviewer-1 adjudication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"
DECISION_FIELDS = (
    "strict_supplier_valid", "independent_confirmation_url", "independent_source_sha256",
    "independent_http_status", "independent_robots_status", "identity_confirmed",
    "us_presence_confirmed", "size_evidence", "sme_status_verified",
    "verification_confidence", "verification_notes",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def as_bool(value: str, field: str) -> bool:
    value = value.strip().casefold()
    if value not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false")
    return value == "true"


def apply(
    review_path: Path, decision_path: Path, fetched_paths: list[Path], output_path: Path, manifest_path: Path
) -> dict:
    rows = read_csv(review_path)
    decisions = read_csv(decision_path)
    fetched: dict[str, list[dict[str, str]]] = {}
    for path in fetched_paths:
        for row in read_csv(path):
            fetched.setdefault(row["canonical_url"], []).append(row)
    selected_ids = {row["review_id"] for row in rows if row.get("second_source_selected") == "true"}
    ids = [row["review_id"] for row in decisions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate verification decision review_id")
    if set(ids) != selected_ids:
        raise ValueError(
            f"verification coverage mismatch: missing={sorted(selected_ids-set(ids))}, extra={sorted(set(ids)-selected_ids)}"
        )
    by_id = {row["review_id"]: row for row in decisions}
    for decision in decisions:
        for field in ("strict_supplier_valid", "identity_confirmed", "us_presence_confirmed"):
            as_bool(decision[field], field)
        if decision["sme_status_verified"] not in {"probable_sme", "unknown", "not_sme"}:
            raise ValueError(f"invalid verified SME status: {decision['review_id']}")
        url = decision["independent_confirmation_url"]
        if url:
            sources = fetched.get(url, [])
            source = next(
                (row for row in sources if row["page_sha256"] == decision["independent_source_sha256"]),
                None,
            )
            if not source:
                raise ValueError(f"verification URL was not fetched: {url}")
            for target, source_field in (
                ("independent_source_sha256", "page_sha256"),
                ("independent_http_status", "http_status"),
                ("independent_robots_status", "robots_status"),
            ):
                if decision[target] != source[source_field]:
                    raise ValueError(f"source metadata mismatch for {decision['review_id']}: {target}")
            if as_bool(decision["strict_supplier_valid"], "strict_supplier_valid") and not (
                200 <= int(source["http_status"]) < 300 and source["robots_status"] == "robots_allowed"
            ):
                raise ValueError(f"strict positive lacks allowed 2xx source: {decision['review_id']}")
        elif as_bool(decision["strict_supplier_valid"], "strict_supplier_valid"):
            raise ValueError(f"strict positive lacks confirmation URL: {decision['review_id']}")

    out = []
    for row in rows:
        decision = by_id.get(row["review_id"])
        updated = {**row}
        if decision:
            updated.update({field: decision[field] for field in DECISION_FIELDS})
            updated["is_valid_supplier_strict"] = str(
                as_bool(decision["strict_supplier_valid"], "strict_supplier_valid")
            )
            updated["independent_confirmation_url"] = decision["independent_confirmation_url"]
            updated["sme_status"] = decision["sme_status_verified"]
            updated["adjudication_status"] = "verification_complete"
        out.append(updated)
    fields = list(out[0])
    for field in DECISION_FIELDS:
        if field not in fields:
            fields.append(field)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(out)
    verified = [row for row in out if row.get("adjudication_status") == "verification_complete"]
    manifest = {
        "selected_rows": len(verified),
        "strict_positive_rows": sum(row["is_valid_supplier_strict"] == "True" for row in verified),
        "net_new_strict_positive_rows": sum(
            row["is_valid_supplier_strict"] == "True" and row["baseline_disposition"] == "novel_candidate"
            for row in verified
        ),
        "probable_sme_rows": sum(row["sme_status"] == "probable_sme" for row in verified),
        "confirmed_sme_rows": 0,
        "decision_input_sha256": sha256_file(decision_path),
        "fetched_source_index_sha256": [sha256_file(path) for path in fetched_paths],
        "output_sha256": sha256_file(output_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, default=PRIVATE / "review" / "reviewer1_adjudicated.csv")
    parser.add_argument("--decisions", type=Path, default=PRIVATE / "verification" / "verification_decisions.csv")
    parser.add_argument(
        "--fetched", type=Path, action="append",
        default=None, help="Fetched source index; repeatable for immutable batches",
    )
    parser.add_argument("--output", type=Path, default=PRIVATE / "verification" / "verified_candidates.csv")
    parser.add_argument("--manifest", type=Path, default=PRIVATE / "verification" / "verification_manifest.json")
    args = parser.parse_args()
    fetched = args.fetched or [PRIVATE / "verification" / "fetched_v5" / "source_candidates.csv"]
    print(json.dumps(apply(args.review, args.decisions, fetched, args.output, args.manifest), indent=2))


if __name__ == "__main__":
    main()
