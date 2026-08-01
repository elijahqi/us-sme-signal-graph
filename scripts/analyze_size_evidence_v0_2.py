#!/usr/bin/env python3
"""Merge the original-page-only size review and audit every positive quote."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

from audit_positive_size_evidence import normalize
from prepare_size_evidence_adjudication import SEMANTIC_FIELDS, load_reviews


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = (
    ROOT / "experiments" / "long_tail_benchmark" / "private" / "formal_v0_3"
    / "ai_census_v0_4" / "size_evidence_v0_2"
)
LABELS = (
    "exact_employee_count", "employee_range", "employee_lower_bound",
    "employee_upper_bound",
    "owner_only_or_nonemployer_explicit", "sba_self_certification_explicit",
    "insufficient",
)


def kappa(left: list[str], right: list[str]) -> float:
    observed = sum(a == b for a, b in zip(left, right)) / len(left)
    count_left, count_right = Counter(left), Counter(right)
    expected = sum(count_left[label] / len(left) * count_right[label] / len(right) for label in LABELS)
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def main() -> None:
    source_rows = [json.loads(line) for line in (PRIVATE / "rows.jsonl").read_text(encoding="utf-8").splitlines() if line]
    source = {row["review_id"]: row for row in source_rows}
    nonempty = {review_id for review_id, row in source.items() if row["original_size_context"]}
    reviewer_a = load_reviews(PRIVATE / "reviewer_a")
    reviewer_b = load_reviews(PRIVATE / "reviewer_b")
    if set(reviewer_a) != nonempty or set(reviewer_b) != nonempty:
        raise ValueError("A/B review coverage mismatch")
    disagreements = {
        review_id for review_id in nonempty
        if any(reviewer_a[review_id][field] != reviewer_b[review_id][field] for field in SEMANTIC_FIELDS)
    }
    reviewer_c = load_reviews(PRIVATE / "adjudication" / "reviewer_c")
    if set(reviewer_c) != disagreements:
        raise ValueError("Reviewer C coverage mismatch")
    results = []
    for review_id in sorted(source):
        original = source[review_id]
        if review_id not in nonempty:
            decision = {
                "size_evidence_status": "insufficient", "employee_lower": None,
                "employee_upper": None, "owner_only_supported": False,
                "sba_status_supported": False, "evidence_quote": "",
                "confidence": "high",
                "rationale": "No size-related term occurred in the frozen original-page visible text.",
            }
            final_source = "automatic_empty_context"
        elif review_id in reviewer_c:
            decision = dict(reviewer_c[review_id])
            for field in SEMANTIC_FIELDS:
                decision[field] = (
                    reviewer_a[review_id][field]
                    if reviewer_a[review_id][field] == reviewer_b[review_id][field]
                    else reviewer_c[review_id][field]
                )
            final_source = "fieldwise_C_adjudication"
        else:
            decision = reviewer_a[review_id]
            final_source = "AB_semantic_agreement"
        quote = decision["evidence_quote"]
        if decision["size_evidence_status"] == "insufficient":
            quote_status = "not_applicable"
            quote_pass = not quote.strip()
        else:
            quote_status = "pass"
            quote_pass = bool(normalize(quote)) and normalize(quote) in normalize(original["original_size_context"])
        if not quote_pass:
            raise ValueError(f"final quote audit failed: {review_id}")
        results.append({
            **{key: original[key] for key in ("review_id", "candidate_id", "business_name", "state", "source_url", "page_sha256")},
            **{key: decision[key] for key in ("size_evidence_status", "employee_lower", "employee_upper", "owner_only_supported", "sba_status_supported", "evidence_quote", "confidence", "rationale")},
            "final_source": final_source,
            "quote_audit_status": quote_status,
        })
    expected_count = json.loads((PRIVATE / "manifest.json").read_text())["positive_pairs"]
    if len(results) != expected_count or len({row["review_id"] for row in results}) != expected_count:
        raise ValueError("final positive-pair coverage mismatch")
    output = PRIVATE / "final_size_evidence_v0_2.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    left = [reviewer_a[review_id]["size_evidence_status"] for review_id in sorted(nonempty)]
    right = [reviewer_b[review_id]["size_evidence_status"] for review_id in sorted(nonempty)]
    supported = [row for row in results if row["size_evidence_status"] != "insufficient"]
    summary = {
        "positive_pairs": len(results),
        "nonempty_original_size_contexts": len(nonempty),
        "automatic_empty_context_insufficient": len(results) - len(nonempty),
        "ab_semantic_disagreements": len(disagreements),
        "ab_status_raw_agreement": sum(a == b for a, b in zip(left, right)) / len(left),
        "ab_status_cohen_kappa": kappa(left, right),
        "final_status_counts": dict(Counter(row["size_evidence_status"] for row in results)),
        "supported_size_evidence_pairs": len(supported),
        "supported_employee_number_pairs": sum(row["size_evidence_status"] in {"exact_employee_count", "employee_range", "employee_lower_bound", "employee_upper_bound"} for row in results),
        "employee_evidence_with_finite_upper_bound_pairs": sum(row["employee_upper"] not in {None, ""} for row in results),
        "supported_owner_only_or_nonemployer_pairs": sum(row["owner_only_supported"] == "True" or row["owner_only_supported"] is True for row in results),
        "supported_sba_representation_pairs": sum(row["sba_status_supported"] == "True" or row["sba_status_supported"] is True for row in results),
        "quote_audit_eligible_pairs": len(supported),
        "final_quote_audit_pass": sum(row["quote_audit_status"] == "pass" for row in results),
        "final_quote_audit_fail": sum(row["quote_audit_status"] == "fail" for row in results),
        "final_quote_audit_not_applicable": sum(row["quote_audit_status"] == "not_applicable" for row in results),
        "unit_warning": "Counts are positive candidate pairs, not unique firms, operating entities, corporate groups, establishments, or SBA-qualified SMEs.",
        "final_table_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    (PRIVATE / "final_size_evidence_summary_v0_2.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
