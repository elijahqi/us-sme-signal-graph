#!/usr/bin/env python3
"""Audit stored decision fields, quote coverage, and label/reason alignment offline."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_processing_sensitivity import (
    DEFAULT_PRIVATE, LABELS, normalized_quote, quote_matches, read_batches,
    read_final, reconstruct, require,
)
from positive_quote_reaudit_utils import FINAL_FIELDS

ROOT = Path(__file__).resolve().parents[1]


def verify_final_fields(rebuilt, final):
    require(set(rebuilt) == set(final), "Rebuilt/final coverage mismatch")
    mismatches = {f: sum(rebuilt[rid][f] != final[rid][f] for rid in rebuilt) for f in FINAL_FIELDS}
    require(not any(mismatches.values()), "Final decision fields differ from reconstructed decisions")
    return {"rows": len(final), "fields": list(FINAL_FIELDS), "field_count": len(FINAL_FIELDS),
            "mismatch_counts": mismatches}


def summarize_outputs(final, evidence):
    require(set(final) == set(evidence), "Final/evidence coverage mismatch")
    require(all(row["eqdp"] in LABELS for row in final.values()), "Invalid primary label")
    reasons = sorted({r["primary_exclusion_reason"] for r in final.values()})
    table = {reason: {label: sum(r["eqdp"] == label and r["primary_exclusion_reason"] == reason
                                for r in final.values()) for label in LABELS} for reason in reasons}
    quotes = {label: Counter(rows=0, literal_pass=0, empty=0, nonempty_literal_fail=0) for label in LABELS}
    for rid, row in final.items():
        group = quotes[row["eqdp"]]
        group["rows"] += 1
        kind = "empty" if not normalized_quote(row["evidence_quote"]) else (
            "literal_pass" if quote_matches(row, evidence[rid]) else "nonempty_literal_fail")
        group[kind] += 1
    return {"label_reason_counts": table, "quote_check_by_label": dict(quotes),
            "no_with_evidence_gap_primary_reason": sum(
                r["eqdp"] == "no" and r["primary_exclusion_reason"] in
                {"insufficient_evidence", "source_unavailable"} for r in final.values())}


def audit(private):
    rebuilt, evidence, hashes = {}, {}, {}
    for name, folder in (("calibration", "ai_review_v0_1"), ("extension", "ai_census_v0_4")):
        _, decisions, _, review_hashes = reconstruct(private / folder)
        source, source_hash = read_batches(private / folder / "batches", "rows")
        require(not set(rebuilt) & set(decisions), "Review subsets overlap")
        require(set(decisions) == set(source), "Decision/evidence coverage mismatch")
        rebuilt.update(decisions)
        evidence.update(source)
        hashes[name] = {**review_hashes, "evidence_batches": source_hash}
    _, corrected, _, quote_hashes = reconstruct(private / "ai_census_v0_4/positive_quote_reaudit_v0_1")
    failed = {rid for rid, row in rebuilt.items() if row["eqdp"] == "yes" and not quote_matches(row, evidence[rid])}
    require(set(corrected) == failed, "Quote re-audit coverage mismatch")
    rebuilt.update(corrected)
    final_path = private / "ai_census_v0_4/full_census_final_v0_1.csv"
    final = read_final(final_path)
    return {
        "schema_version": "output_integrity_v0.4",
        "metadata": {"analysis": "Retrospective deterministic checks on unchanged stored decisions",
                     "unit": "source-capability-state pair", "new_model_calls": 0,
                     "human_ground_truth": False, "row_level_data_included": False,
                     "interpretation": "Field identity, normalized quote occurrence, and label/reason co-occurrence; not semantic errors or accuracy",
                     "normalization": "NFKC, boundary quotes, selected quotation/dash variants, whitespace collapse, case folding",
                     "negative_quote_policy": "Nonpositive quote outcomes are descriptive; no new acceptance or relabeling rule applied"},
        "final_field_verification": verify_final_fields(rebuilt, final),
        **summarize_outputs(final, evidence),
        "input_sha256": {**hashes, "quote_reaudit": quote_hashes,
                         "full_census_final": hashlib.sha256(final_path.read_bytes()).hexdigest()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--output", type=Path, default=ROOT / "paper/output_integrity_v0_4.json")
    args = parser.parse_args()
    result = audit(args.private_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("final_field_verification", "quote_check_by_label", "no_with_evidence_gap_primary_reason")}, indent=2))
