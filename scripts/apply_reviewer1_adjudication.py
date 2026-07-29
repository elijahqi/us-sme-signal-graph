#!/usr/bin/env python3
"""Apply a frozen, provider-blind Reviewer-1 decision file.

The script deliberately separates first-party supplier validity from strict
validity, which requires an independent source. It also fails closed when a
candidate in the predefined 44-row review scope has no decision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"
SIGNAL_TRUE = "True"
DECISION_FIELDS = (
    "canonical_company_name",
    "supplier_valid_lenient",
    "us_presence_first_party",
    "direct_manufacturer_first_party",
    "baseline_disposition",
    "matched_baseline_entity_id",
    "sme_status_reviewer1",
    "second_source_selected",
    "verification_role",
    "reviewer1_confidence",
    "reason_codes",
    "reviewer1_notes",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def bool_value(value: str, field: str) -> bool:
    normalized = value.strip().casefold()
    if normalized not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false, got {value!r}")
    return normalized == "true"


def in_review_scope(row: dict[str, str], scope: str = "direct_semiconductor_manufacturing") -> bool:
    if scope not in {"direct_semiconductor_manufacturing", "us_signal_subset"}:
        raise ValueError(f"unknown review scope: {scope}")
    return (
        row["source_kind_prelabel"] == "direct_company_candidate"
        and row["semiconductor_signal"] == SIGNAL_TRUE
        and row["manufacturing_signal"] == SIGNAL_TRUE
        and (scope != "us_signal_subset" or row["us_presence_signal"] == SIGNAL_TRUE)
    )


def validate_decisions(
    rows: list[dict[str, str]], decisions: list[dict[str, str]], scope: str = "direct_semiconductor_manufacturing"
) -> dict[str, dict[str, str]]:
    row_ids = {row["review_id"] for row in rows}
    scope_ids = {row["review_id"] for row in rows if in_review_scope(row, scope)}
    decision_ids = [decision["review_id"] for decision in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError("decision file contains duplicate review_id values")
    unknown = set(decision_ids) - row_ids
    missing = scope_ids - set(decision_ids)
    outside = set(decision_ids) - scope_ids
    if unknown:
        raise ValueError(f"decision file contains unknown review IDs: {sorted(unknown)}")
    if missing or outside:
        raise ValueError(
            f"decision coverage mismatch: missing={sorted(missing)}, outside_scope={sorted(outside)}"
        )
    for decision in decisions:
        for field in ("supplier_valid_lenient", "second_source_selected"):
            bool_value(decision[field], field)
        if decision["baseline_disposition"] not in {
            "novel_candidate", "baseline_duplicate", "out_of_scope", "not_a_company"
        }:
            raise ValueError(f"invalid baseline_disposition in {decision['review_id']}")
        if decision["sme_status_reviewer1"] not in {"probable_sme", "unknown", "not_sme"}:
            raise ValueError(f"invalid reviewer-1 SME status in {decision['review_id']}")
        if bool_value(decision["second_source_selected"], "second_source_selected") and not decision["verification_role"]:
            raise ValueError(f"selected row lacks verification_role: {decision['review_id']}")
    return {decision["review_id"]: decision for decision in decisions}


def apply(
    review_path: Path, decision_path: Path, output_path: Path, manifest_path: Path,
    scope: str = "direct_semiconductor_manufacturing",
) -> dict:
    rows = read_csv(review_path)
    decisions = read_csv(decision_path)
    by_id = validate_decisions(rows, decisions, scope)
    output_rows: list[dict[str, str]] = []
    for row in rows:
        decision = by_id.get(row["review_id"])
        if not decision:
            output_rows.append(row)
            continue
        lenient = bool_value(decision["supplier_valid_lenient"], "supplier_valid_lenient")
        selected = bool_value(decision["second_source_selected"], "second_source_selected")
        updated = {**row}
        updated.update({field: decision[field] for field in DECISION_FIELDS})
        updated.update(
            {
                "is_valid_supplier_lenient": str(lenient),
                "is_valid_supplier_strict": "pending_second_source" if selected else "False",
                "is_us_presence_confirmed": decision["us_presence_first_party"],
                "is_direct_manufacturer_confirmed": decision["direct_manufacturer_first_party"],
                "sme_status": decision["sme_status_reviewer1"],
                "canonical_company_name": decision["canonical_company_name"],
                "matched_baseline_company_id": decision["matched_baseline_entity_id"],
                "annotator_confidence": decision["reviewer1_confidence"],
                "adjudication_status": "reviewer1_complete",
                "review_notes": decision["reviewer1_notes"],
            }
        )
        output_rows.append(updated)

    fieldnames = list(output_rows[0])
    for field in DECISION_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    reviewed = [row for row in output_rows if row.get("adjudication_status") == "reviewer1_complete"]
    manifest = {
        "review_scope_rows": len(reviewed),
        "review_scope": scope,
        "lenient_positive_rows": sum(row["is_valid_supplier_lenient"] == "True" for row in reviewed),
        "second_source_selected_rows": sum(row["second_source_selected"] == "true" for row in reviewed),
        "baseline_duplicate_rows": sum(row["baseline_disposition"] == "baseline_duplicate" for row in reviewed),
        "out_of_scope_or_non_company_rows": sum(
            row["baseline_disposition"] in {"out_of_scope", "not_a_company"} for row in reviewed
        ),
        "review_input_sha256": sha256_file(review_path),
        "decision_input_sha256": sha256_file(decision_path),
        "output_sha256": sha256_file(output_path),
        "provider_origin_visible_to_reviewer1": False,
        "strict_positive_claimed_at_reviewer1": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--review", type=Path, default=PRIVATE / "review" / "blind_review_with_evidence.csv"
    )
    parser.add_argument(
        "--decisions", type=Path, default=PRIVATE / "review" / "reviewer1_decisions.csv"
    )
    parser.add_argument(
        "--output", type=Path, default=PRIVATE / "review" / "reviewer1_adjudicated.csv"
    )
    parser.add_argument(
        "--manifest", type=Path, default=PRIVATE / "review" / "reviewer1_manifest.json"
    )
    parser.add_argument(
        "--scope", choices=("direct_semiconductor_manufacturing", "us_signal_subset"),
        default="direct_semiconductor_manufacturing",
    )
    args = parser.parse_args()
    print(json.dumps(apply(args.review, args.decisions, args.output, args.manifest, args.scope), indent=2))


if __name__ == "__main__":
    main()
