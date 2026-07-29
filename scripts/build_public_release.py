#!/usr/bin/env python3
"""Build a redistributable aggregate release without provider payloads or page text."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"
PUBLIC_FIELDS = (
    "candidate_id", "canonical_company_name", "registrable_domain", "capability_groups",
    "sme_evidence_status", "size_evidence", "primary_evidence_url", "primary_page_sha256",
    "independent_confirmation_url", "independent_source_sha256", "verification_confidence",
    "verified_at",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(verified_path: Path, pilot_metrics_path: Path, provider_metrics_path: Path, output_dir: Path) -> dict:
    rows = read_csv(verified_path)
    public = []
    for row in rows:
        if row.get("is_valid_supplier_strict") != "True" or row.get("baseline_disposition") != "novel_candidate":
            continue
        public.append({
            "candidate_id": row["review_id"],
            "canonical_company_name": row["canonical_company_name"],
            "registrable_domain": row["registrable_domain"],
            "capability_groups": row["capability_groups"],
            "sme_evidence_status": row["sme_status"],
            "size_evidence": row["size_evidence"],
            "primary_evidence_url": row["primary_evidence_url"],
            "primary_page_sha256": row["primary_page_sha256"],
            "independent_confirmation_url": row["independent_confirmation_url"],
            "independent_source_sha256": row["independent_source_sha256"],
            "verification_confidence": row["verification_confidence"],
            "verified_at": "2026-07-29",
        })
    public.sort(key=lambda row: row["canonical_company_name"].casefold())
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = output_dir / "verified_supplier_candidates.csv"
    with candidate_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PUBLIC_FIELDS, lineterminator="\n")
        writer.writeheader(); writer.writerows(public)
    metrics = {
        "pilot": json.loads(pilot_metrics_path.read_text()),
        "provider_attribution": json.loads(provider_metrics_path.read_text()),
    }
    metrics_path = output_dir / "pilot_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    manifest = {
        "release_version": "v0.2.0-rc1",
        "candidate_rows": len(public),
        "confirmed_sme_rows": 0,
        "provider_payloads_in_release": False,
        "third_party_page_text_in_release": False,
        "sia_row_level_data_in_release": False,
        "files": {candidate_path.name: sha256(candidate_path), metrics_path.name: sha256(metrics_path)},
    }
    manifest_path = output_dir / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksums = [f"{sha256(path)}  {path.name}" for path in sorted(output_dir.iterdir()) if path.name != "SHA256SUMS"]
    (output_dir / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, default=PRIVATE / "verification" / "verified_candidates.csv")
    parser.add_argument("--pilot-metrics", type=Path, default=PRIVATE / "metrics" / "pilot_metrics.json")
    parser.add_argument("--provider-metrics", type=Path, default=PRIVATE / "metrics" / "provider_attribution.json")
    parser.add_argument("--output", type=Path, default=ROOT / "release" / "public" / "v0.2.0-rc1")
    args = parser.parse_args()
    print(json.dumps(build(args.verified, args.pilot_metrics, args.provider_metrics, args.output), indent=2))


if __name__ == "__main__":
    main()
