#!/usr/bin/env python3
"""Reconstruct processing sensitivity and export only row-free aggregate counts.

The original whole-record merge and the pre-quote fieldwise merge are rebuilt
from retained A/B/C results. No model is called and no private input is changed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE = ROOT / "experiments/long_tail_benchmark/private/formal_v0_3"
DEFAULT_OUTPUT = ROOT / "paper/audit_processing_sensitivity_v0_2.json"
KEY_FIELDS = (
    "identity_status", "direct_producer_status", "capability_match",
    "production_presence", "commercial_offering", "eqdp",
    "primary_exclusion_reason", "scale_band", "legal_form", "web_visibility",
)
LABELS = ("yes", "no", "unclear")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_batches(directory: Path, collection: str = "results") -> tuple[dict, str]:
    """Keep identifiers private; fingerprint the ordered file names and bytes."""
    rows = {}
    digest = hashlib.sha256()
    paths = sorted(directory.glob("batch-*.json"))
    require(bool(paths), f"No input batches in {directory}")
    for path in paths:
        raw = path.read_bytes()
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(raw).digest())
        payload = json.loads(raw)
        require(isinstance(payload.get(collection), list), "Invalid batch collection")
        for row in payload[collection]:
            identifier = row["review_id"]
            require(identifier not in rows, "Duplicate private review identifier")
            rows[identifier] = row
    return rows, digest.hexdigest()


def read_final(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        result = {}
        for row in csv.DictReader(handle):
            require(row["review_id"] not in result, "Duplicate final review identifier")
            result[row["review_id"]] = row
    return result


def label_counts(rows: dict) -> dict[str, int]:
    counts = Counter(row["eqdp"] for row in rows.values())
    require(set(counts) <= set(LABELS), "Unexpected primary-label enum")
    return {label: counts[label] for label in LABELS}


def normalized_quote(value: str) -> str:
    # Mirrors the existing census and quote re-audit normalization exactly.
    value = unicodedata.normalize("NFKC", value).strip().strip('“”"‘’\'')
    value = value.replace("…", "...").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).casefold()


def quote_matches(row: dict, evidence: dict) -> bool:
    quote = normalized_quote(row["evidence_quote"])
    return bool(quote) and quote in normalized_quote(evidence["evidence_excerpt"])


def reconstruct(directory: Path) -> tuple[dict, dict, dict, dict]:
    a, a_sha = read_batches(directory / "reviewer_a")
    b, b_sha = read_batches(directory / "reviewer_b")
    c, c_sha = read_batches(directory / "adjudication/reviewer_c")
    require(set(a) == set(b), "A/B review coverage differs")
    disputed = {
        identifier for identifier in a
        if any(a[identifier][field] != b[identifier][field] for field in KEY_FIELDS)
    }
    require(set(c) == disputed, "C coverage does not equal key-field disagreements")
    whole = {identifier: dict(c.get(identifier, a[identifier])) for identifier in a}
    fieldwise = {}
    for identifier in a:
        row = dict(whole[identifier])
        for field in KEY_FIELDS:
            row[field] = (
                a[identifier][field] if a[identifier][field] == b[identifier][field]
                else c[identifier][field]
            )
        fieldwise[identifier] = row
    # Validate enums before they are used as output transition values.
    label_counts(whole)
    label_counts(fieldwise)
    counts = {"a_rows": len(a), "b_rows": len(b), "c_rows": len(c)}
    hashes = {"reviewer_a": a_sha, "reviewer_b": b_sha, "reviewer_c": c_sha}
    return whole, fieldwise, counts, hashes


def changes(before: dict, after: dict) -> dict:
    require(set(before) == set(after), "Processing-stage row coverage differs")
    transitions = Counter(
        (before[identifier]["eqdp"], after[identifier]["eqdp"])
        for identifier in before
        if before[identifier]["eqdp"] != after[identifier]["eqdp"]
    )
    primary = sum(transitions.values())
    any_key = sum(
        any(before[identifier][field] != after[identifier][field] for field in KEY_FIELDS)
        for identifier in before
    )
    return {
        "primary_label_changed_rows": primary,
        "any_key_field_changed_rows": any_key,
        "nonprimary_only_changed_rows": any_key - primary,
        "primary_label_transitions": [
            {"from": left, "to": right, "rows": count}
            for (left, right), count in sorted(transitions.items())
        ],
        "changed_rows_by_key_field": {
            field: sum(before[identifier][field] != after[identifier][field] for identifier in before)
            for field in KEY_FIELDS
        },
    }


def audit(private: Path) -> dict:
    whole, fieldwise, evidence = {}, {}, {}
    subset_ids, subsets, hashes = {}, {}, {}
    for name, folder in (
        ("calibration", "ai_review_v0_1"), ("extension", "ai_census_v0_4"),
    ):
        old, corrected, review_counts, review_hashes = reconstruct(private / folder)
        excerpts, evidence_sha = read_batches(private / folder / "batches", "rows")
        require(set(old) == set(excerpts), "Review/evidence coverage differs")
        require(not (set(old) & set(whole)), "Calibration and extension overlap")
        subset_ids[name] = set(old)
        subsets[name] = {
            "rows": len(old),
            "review_counts": review_counts,
            "stages": {
                "whole_record_c_merge": label_counts(old),
                "fieldwise_before_quote_reaudit": label_counts(corrected),
            },
            "fieldwise_correction": changes(old, corrected),
        }
        hashes[name] = {**review_hashes, "evidence_batches": evidence_sha}
        whole.update(old)
        fieldwise.update(corrected)
        evidence.update(excerpts)

    failed = {
        identifier for identifier, row in fieldwise.items()
        if row["eqdp"] == "yes" and not quote_matches(row, evidence[identifier])
    }
    quote_root = private / "ai_census_v0_4/positive_quote_reaudit_v0_1"
    _, quote_final, quote_review_counts, quote_hashes = reconstruct(quote_root)
    require(failed == set(quote_final), "Quote re-audit coverage differs from recomputed failures")
    quote_manifest = json.loads((quote_root / "manifest.json").read_text(encoding="utf-8"))
    require(quote_manifest["failed_positive_pairs"] == len(failed), "Quote manifest count differs")
    final_path = private / "ai_census_v0_4/full_census_final_v0_1.csv"
    observed_final = read_final(final_path)
    rebuilt_final = {**fieldwise, **quote_final}
    require(set(rebuilt_final) == set(observed_final), "Rebuilt/final row coverage differs")
    require(
        all(rebuilt_final[identifier][field] == observed_final[identifier][field]
            for identifier in rebuilt_final for field in KEY_FIELDS),
        "Reconstructed final key fields differ from the frozen final table",
    )
    final_positive = {
        identifier: row for identifier, row in rebuilt_final.items() if row["eqdp"] == "yes"
    }
    final_quote_passes = sum(
        quote_matches(row, evidence[identifier]) for identifier, row in final_positive.items()
    )
    require(final_quote_passes == len(final_positive), "A retained positive fails literal-quote audit")
    for name, identifiers in subset_ids.items():
        subset_final = {identifier: rebuilt_final[identifier] for identifier in identifiers}
        subset_reaudit = {identifier: quote_final[identifier] for identifier in identifiers & failed}
        subsets[name]["stages"]["after_literal_quote_reaudit"] = label_counts(subset_final)
        subsets[name]["quote_reaudit"] = {
            "reviewed_rows": len(subset_reaudit), "final_labels": label_counts(subset_reaudit),
        }

    positive_before = label_counts(fieldwise)["yes"]
    return {
        "schema_version": "processing_sensitivity_v0.2",
        "metadata": {
            "unit": "constructed source-capability-state pair",
            "analysis": "retrospective reconstruction of processing stages from retained A/B/C outputs",
            "first_two_stages": "reconstructed, not separately preserved historical result tables",
            "labels": "same-model page-support judgments; not human ground truth or factual error rates",
            "human_ground_truth": False,
            "row_level_data_included": False,
            "input_fingerprint_method": "SHA-256 over sorted batch basenames, NUL, and SHA-256 file digests",
            "quote_check": "nonempty normalized contiguous substring of the original frozen excerpt",
        },
        "rows": len(rebuilt_final),
        "stages": {
            "whole_record_c_merge": label_counts(whole),
            "fieldwise_before_quote_reaudit": label_counts(fieldwise),
            "after_literal_quote_reaudit": label_counts(rebuilt_final),
        },
        "fieldwise_correction": changes(whole, fieldwise),
        "quote_reaudit": {
            "positive_rows_before": positive_before,
            "literal_quote_passes_before": positive_before - len(failed),
            "literal_quote_failures_before": len(failed),
            "review_counts": quote_review_counts,
            "final_labels_of_reaudited_rows": label_counts(quote_final),
            "primary_label_transitions": changes(fieldwise, rebuilt_final)["primary_label_transitions"],
            "final_positive_rows": len(final_positive),
            "final_positive_literal_quote_passes": final_quote_passes,
        },
        "subsets": subsets,
        "verification": {
            "a_b_coverage_equal": True,
            "c_coverage_equals_key_field_disagreements": True,
            "reaudit_ids_equal_recomputed_quote_failures": True,
            "reconstructed_final_matches_all_key_fields": True,
            "verified_key_field_count": len(KEY_FIELDS),
            "verified_final_rows": len(rebuilt_final),
        },
        "input_sha256": {
            **hashes,
            "quote_reaudit": quote_hashes,
            "full_census_final": hashlib.sha256(final_path.read_bytes()).hexdigest(),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    # Only explicitly selected aggregate fields above enter this serialization.
    result = audit(args.private_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows_verified": result["rows"], "stages": result["stages"]}, sort_keys=True))


if __name__ == "__main__":
    main()
