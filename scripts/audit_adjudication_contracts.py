#!/usr/bin/env python3
"""Audit adjudication routing and positive-label contracts without model calls."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

from audit_processing_sensitivity import (
    DEFAULT_PRIVATE, KEY_FIELDS, LABELS, read_batches, read_final, require,
)

ROOT = Path(__file__).resolve().parents[1]


def routing(a, b, c):
    require(set(a) == set(b), "A/B coverage mismatch")
    expected_c = {rid for rid in a if any(a[rid][f] != b[rid][f] for f in KEY_FIELDS)}
    require(set(c) == expected_c, "C coverage mismatch")
    require(all(r["eqdp"] in LABELS for rs in (a, b, c) for r in rs.values()), "Invalid primary label")
    at_risk = {rid for rid in c if a[rid]["eqdp"] == b[rid]["eqdp"]}
    overwritten = {rid for rid in at_risk if c[rid]["eqdp"] != a[rid]["eqdp"]}
    return {
        "rows": len(a), "routed_to_c_any_field_disagreement": len(c),
        "routed_to_c_primary_disagreement": len(c) - len(at_risk),
        "routed_to_c_despite_primary_agreement": len(at_risk),
        "whole_record_primary_agreement_overwrites": len(overwritten),
        "whole_record_overwrite_fraction_among_agreed_primary_routed_rows": len(overwritten) / len(at_risk) if at_risk else None,
        "agreed_primary_labels_routed_to_c": {label: sum(a[rid]["eqdp"] == label for rid in at_risk) for label in LABELS},
        "overwritten_primary_transitions": {left: {right: sum(a[rid]["eqdp"] == left and c[rid]["eqdp"] == right for rid in overwritten) for right in LABELS} for left in LABELS},
        "trigger_field_disagreements_in_overwritten_rows": {
            f: sum(a[rid][f] != b[rid][f] for rid in overwritten) for f in KEY_FIELDS if f != "eqdp"
        },
    }


def positive_contracts(rows, state_names):
    positives = [r for r in rows.values() if r["eqdp"] == "yes"]
    eligible = {"industrial_facility_confirmed", "job_shop_or_workshop_confirmed", "owner_or_home_production_confirmed"}
    def state_name(value):
        value = value.strip().casefold()
        return state_names.get(value, value)
    return {
        "positive_rows": len(positives),
        "positive_component_violations": sum(
            not (all(r[f] == "yes" for f in ("identity_status", "direct_producer_status", "capability_match", "commercial_offering"))
                 and r["production_presence"] in eligible and r["primary_exclusion_reason"] == "none")
            for r in positives),
        "positive_state_field_mismatches": sum(state_name(r["production_state"]) != state_name(r["state_id"]) for r in positives),
    }


def audit(private):
    all_a, all_b, all_c, subsets, hashes = {}, {}, {}, {}, {}
    for name, folder in (("calibration", "ai_review_v0_1"), ("extension", "ai_census_v0_4")):
        a, ah = read_batches(private / folder / "reviewer_a")
        b, bh = read_batches(private / folder / "reviewer_b")
        c, ch = read_batches(private / folder / "adjudication/reviewer_c")
        require(not (set(all_a) & set(a)), "subset overlap")
        subsets[name] = routing(a, b, c)
        hashes[name] = {"a": ah, "b": bh, "c": ch}
        all_a.update(a); all_b.update(b); all_c.update(c)
    final_path = private / "ai_census_v0_4/full_census_final_v0_1.csv"
    final = read_final(final_path)
    require(set(final) == set(all_a), "Final coverage mismatch")
    geography = ROOT / "experiments/long_tail_benchmark/geographies_v0_1.csv"
    with geography.open(encoding="utf-8", newline="") as handle:
        states = {r["state_abbr"].casefold(): r["state_name"].casefold() for r in csv.DictReader(handle)}
    return {
        "schema_version": "adjudication_contracts_v0.3",
        "metadata": {
            "analysis": "Retrospective deterministic routing audit using original pre-quote A/B/C outputs",
            "unit": "source-capability-state pair",
            "human_ground_truth": False, "new_model_calls": 0, "row_level_data_included": False,
            "interpretation": "Agreement preservation and output-field consistency, not accuracy, factual validity, or causal improvement",
            "trigger_fields_overlap": True,
        },
        "combined": routing(all_a, all_b, all_c), "subsets": subsets,
        "final_positive_contracts": positive_contracts(final, states),
        "input_sha256": {**hashes, "final_csv": hashlib.sha256(final_path.read_bytes()).hexdigest(),
                         "geographies": hashlib.sha256(geography.read_bytes()).hexdigest()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--output", type=Path, default=ROOT / "paper/adjudication_contracts_v0_3.json")
    args = parser.parse_args()
    value = audit(args.private_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"combined": value["combined"], "final_positive_contracts": value["final_positive_contracts"]}, indent=2))
