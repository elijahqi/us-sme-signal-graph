#!/usr/bin/env python3
"""Validate Baseline v0.1-SIA outputs and checksums."""

import csv
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "processed" / "baseline_v0_1_sia"


def table(name: str) -> list[dict]:
    with (BASELINE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = json.loads((BASELINE / "baseline_manifest.json").read_text())
    companies = table("companies.csv")
    facilities = table("facilities.csv")
    references = table("reference_nodes.csv")
    relations = table("relations.csv")
    source_pages = table("source_pages.csv")
    aliases = table("company_aliases.csv")
    suppliers = table("supplier_baseline.csv")
    assert manifest["baseline_version"] == "baseline_v0.1-sia"
    assert len(companies) == manifest["counts"]["companies"]
    assert len(facilities) == manifest["counts"]["facilities"]
    assert len(references) == manifest["counts"]["reference_nodes"]
    assert len(relations) == manifest["counts"]["relations"]
    assert len(source_pages) == 1
    assert len(aliases) == len(companies)
    assert len(suppliers) == manifest["counts"]["equipment_or_materials_companies"]

    company_ids = {row["company_id"] for row in companies}
    facility_ids = {row["facility_id"] for row in facilities}
    reference_ids = {row["node_id"] for row in references}
    assert len(company_ids) == len(companies)
    assert len(facility_ids) == len(facilities)
    assert len(reference_ids) == len(references)
    assert all(row["company_id"] in company_ids for row in facilities)
    valid_sources = company_ids | facility_ids
    valid_targets = company_ids | facility_ids | reference_ids
    assert all(row["source_id"] in valid_sources for row in relations)
    assert all(row["target_id"] in valid_targets for row in relations)
    assert all(row["page_sha256"] == manifest["page_sha256"] for row in companies + facilities + relations + source_pages)
    assert all(len(row["state"]) in (0, 2) for row in facilities)
    assert all(row["company_id"] in company_ids for row in aliases + suppliers)
    assert all(row["sme_status"] == "unknown" for row in suppliers)
    with gzip.open(BASELINE / "source_snapshot.html.gz", "rb") as handle:
        assert hashlib.sha256(handle.read()).hexdigest() == manifest["page_sha256"]

    counts: dict[str, int] = {}
    for row in relations:
        counts[row["relation_type"]] = counts.get(row["relation_type"], 0) + 1
    assert dict(sorted(counts.items())) == manifest["relation_type_counts"]
    for line in (BASELINE / "SHA256SUMS").read_text().splitlines():
        expected, filename = line.split("  ", 1)
        actual = hashlib.sha256((BASELINE / filename).read_bytes()).hexdigest()
        assert actual == expected, filename
    print(json.dumps({"status": "valid", "version": manifest["baseline_version"], "counts": manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()

