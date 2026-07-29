#!/usr/bin/env python3
"""Compute fail-closed pilot metrics from adjudicated and verified rows."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def compute(verified_path: Path, baseline_manifest_path: Path) -> dict:
    rows = read_csv(verified_path)
    reviewed = [row for row in rows if row.get("reviewer1_confidence")]
    strict = [row for row in reviewed if row.get("is_valid_supplier_strict") == "True"]
    net_new_strict = [row for row in strict if row.get("baseline_disposition") == "novel_candidate"]
    probable_smes = [row for row in strict if row.get("sme_status") == "probable_sme"]
    with baseline_manifest_path.open(encoding="utf-8") as handle:
        baseline = json.load(handle)
    denominator = int(baseline["counts"]["equipment_or_materials_companies"])
    low, high = wilson(len(strict), len(reviewed))
    output = {
        "metric_scope": "75 provider-blind direct-company rows with semiconductor and manufacturing signals",
        "reviewed_rows": len(reviewed),
        "strict_supplier_rows": len(strict),
        "strict_precision": len(strict) / len(reviewed),
        "strict_precision_wilson_95": [low, high],
        "net_new_strict_suppliers": len(net_new_strict),
        "baseline_supplier_denominator": denominator,
        "strict_company_lift": len(net_new_strict) / denominator,
        "probable_sme_strict_suppliers": len(probable_smes),
        "confirmed_sme_strict_suppliers": 0,
        "unreviewed_domain_rows": 186 - len(reviewed),
        "annotation_agreement": None,
        "pilot_gate": {
            "net_new_strict_at_least_25": len(net_new_strict) >= 25,
            "precision_lower_bound_at_least_0_55": low >= 0.55,
            "double_review_agreement_at_least_0_70": False,
            "entity_resolution_precision_at_least_0_95": None,
            "full_run_authorized_by_evidence": False,
        },
        "interpretation": (
            "The discovery arm clears the count gate but not the precision or independent-review gates. "
            f"The {len(net_new_strict)}-company strict set is a verified candidate release, "
            "not a completed full-run dataset."
        ),
    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, default=PRIVATE / "verification" / "verified_candidates.csv")
    parser.add_argument(
        "--baseline-manifest", type=Path,
        default=ROOT / "data" / "processed" / "baseline_v0_1_sia" / "baseline_manifest.json",
    )
    parser.add_argument("--output", type=Path, default=PRIVATE / "metrics" / "pilot_metrics.json")
    args = parser.parse_args()
    metrics = compute(args.verified, args.baseline_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
