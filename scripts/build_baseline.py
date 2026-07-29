#!/usr/bin/env python3
"""Build Baseline v0.1-SIA from the public SIA ecosystem map."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import subprocess
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "baseline_v0_1_sia"
RAW_PAGE = ROOT / "data" / "raw" / "sia_ecosystem.html"
VERSION = "baseline_v0.1-sia"
PARSER_VERSION = "sia_ecosystem_v1"
STATE_NAMES = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "DISTRICT OF COLUMBIA": "DC", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI",
    "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
    "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
    "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
    "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY", "PUERTO RICO": "PR",
}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode()).hexdigest()[:20]}"


def clean(value: object) -> str:
    text = unicodedata.normalize("NFKC", unescape(str(value or "")))
    return re.sub(r"\s+", " ", text).strip()


def clean_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({clean(item) for item in value if clean(item)})


def normalize_state(value: object) -> tuple[str, str, str]:
    raw_state = clean(value).upper()
    if not raw_state:
        return "", "", "missing"
    if len(raw_state) == 2 and raw_state.isalpha():
        return raw_state, raw_state, "as_provided_code"
    if raw_state in STATE_NAMES:
        return STATE_NAMES[raw_state], raw_state, "normalized_full_name"
    return "", raw_state, "unrecognized"


def extract_records(page: str, variable: str = "companiesData") -> list[dict]:
    marker = re.search(rf"\bvar\s+{re.escape(variable)}\s*=\s*", page)
    if not marker:
        raise ValueError(f"Missing JavaScript variable: {variable}")
    start = page.find("[", marker.end())
    if start < 0:
        raise ValueError(f"Missing array for: {variable}")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(page)):
        char = page[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                records = json.loads(page[start : index + 1])
                if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
                    raise ValueError("Unexpected companiesData payload")
                return records
    raise ValueError("Unterminated companiesData array")


def fetch(url: str, destination: Path) -> bytes:
    result = subprocess.run(
        ["curl", "-fLsS", "--max-time", "90", "-A", "US-SME-Signal-Graph/0.1 public-research", url],
        check=True,
        stdout=subprocess.PIPE,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(result.stdout)
    return result.stdout


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def canonical_record(raw: dict) -> dict:
    state, raw_state, state_quality = normalize_state(raw.get("state_clone") or raw.get("state"))
    return {
        "name": clean(raw.get("name")),
        "company_types": clean_list(raw.get("company_type")),
        "city": clean(raw.get("city")),
        "state": state,
        "raw_state": raw_state,
        "state_quality": state_quality,
        "latitude": raw.get("lat"),
        "longitude": raw.get("lon"),
        "activities": clean_list(raw.get("company_activity")),
        "announcement_types": clean_list(raw.get("announcement_type")),
        "fab_open_date": clean(raw.get("fab_open_date")),
        "investment": clean(raw.get("investment")),
        "jobs_expected": clean(raw.get("jobs_expected")),
        "supporting_source_url": clean(raw.get("source")),
    }


def build(page_bytes: bytes, source: dict, retrieved_at: str, output: Path) -> dict:
    page_sha = hashlib.sha256(page_bytes).hexdigest()
    raw_records = extract_records(page_bytes.decode("utf-8", "replace"))
    records = [canonical_record(row) for row in raw_records]
    records = [row for row in records if row["name"]]
    companies: dict[str, dict] = {}
    facilities: dict[str, dict] = {}

    for row in records:
        normalized = row["name"].casefold()
        company_id = stable_id("company", normalized)
        source_payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        source_record_id = stable_id("sia-record", source_payload)
        facility_key = "|".join(
            [company_id, row["city"].casefold(), row["state"], str(row["latitude"] or ""), str(row["longitude"] or "")]
        )
        facility_id = stable_id("facility", facility_key)

        company = companies.setdefault(
            company_id,
            {"canonical_name": row["name"], "normalized_name": normalized, "types": set(), "source_ids": set()},
        )
        company["types"].update(row["company_types"])
        company["source_ids"].add(source_record_id)

        facility = facilities.setdefault(
            facility_id,
            {
                "company_id": company_id,
                "city": row["city"],
                "state": row["state"],
                "raw_states": set(),
                "state_quality_flags": set(),
                "latitude": row["latitude"] if row["latitude"] is not None else "",
                "longitude": row["longitude"] if row["longitude"] is not None else "",
                "types": set(),
                "activities": set(),
                "announcements": set(),
                "fab_dates": set(),
                "investments": set(),
                "jobs": set(),
                "support_urls": set(),
                "source_ids": set(),
            },
        )
        facility["types"].update(row["company_types"])
        if row["raw_state"]:
            facility["raw_states"].add(row["raw_state"])
        facility["state_quality_flags"].add(row["state_quality"])
        facility["activities"].update(row["activities"])
        facility["announcements"].update(row["announcement_types"])
        for key, target in (
            ("fab_open_date", "fab_dates"),
            ("investment", "investments"),
            ("jobs_expected", "jobs"),
            ("supporting_source_url", "support_urls"),
        ):
            if row[key]:
                facility[target].add(row[key])
        facility["source_ids"].add(source_record_id)

    shared = {
        "source_url": source["url"],
        "publisher": source["publisher"],
        "retrieved_at": retrieved_at,
        "page_sha256": page_sha,
    }
    company_rows = [
        {
            "company_id": company_id,
            "canonical_name": item["canonical_name"],
            "normalized_name": item["normalized_name"],
            "company_types": json.dumps(sorted(item["types"]), ensure_ascii=False),
            "source_record_count": len(item["source_ids"]),
                "source_record_ids": " | ".join(sorted(item["source_ids"])),
            **shared,
        }
        for company_id, item in sorted(companies.items(), key=lambda pair: pair[1]["normalized_name"])
    ]
    facility_rows = [
        {
            "facility_id": facility_id,
            "company_id": item["company_id"],
            "city": item["city"],
            "state": item["state"],
            "raw_state": " | ".join(sorted(item["raw_states"])),
            "state_quality_flag": " | ".join(sorted(item["state_quality_flags"])),
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "company_types": json.dumps(sorted(item["types"]), ensure_ascii=False),
            "activities": json.dumps(sorted(item["activities"]), ensure_ascii=False),
            "announcement_types": json.dumps(sorted(item["announcements"]), ensure_ascii=False),
            "fab_open_date": " | ".join(sorted(item["fab_dates"])),
            "investment": " | ".join(sorted(item["investments"])),
            "jobs_expected": " | ".join(sorted(item["jobs"])),
            "supporting_source_url": " | ".join(sorted(item["support_urls"])),
            "source_record_id": " | ".join(sorted(item["source_ids"])),
            **shared,
        }
        for facility_id, item in sorted(facilities.items())
    ]

    reference_nodes: dict[str, dict] = {}
    relations: dict[str, dict] = {}

    def reference(node_id: str, node_type: str, label: str) -> None:
        reference_nodes[node_id] = {"node_id": node_id, "node_type": node_type, "label": label}

    def relation(source_id: str, source_type: str, kind: str, target_id: str, target_type: str, evidence: str) -> None:
        relation_id = stable_id("relation", "|".join([source_id, kind, target_id]))
        relations[relation_id] = {
            "relation_id": relation_id,
            "source_id": source_id,
            "source_type": source_type,
            "relation_type": kind,
            "target_id": target_id,
            "target_type": target_type,
            "evidence_source_record_id": evidence,
            **shared,
        }

    for facility in facility_rows:
        evidence = facility["source_record_id"]
        relation(facility["company_id"], "COMPANY", "HAS_FACILITY", facility["facility_id"], "FACILITY", evidence)
        if facility["state"]:
            state_id = f"US-STATE:{facility['state']}"
            reference(state_id, "US_STATE", facility["state"])
            relation(facility["facility_id"], "FACILITY", "LOCATED_IN", state_id, "US_STATE", evidence)
        for activity in json.loads(facility["activities"]):
            activity_id = stable_id("activity", activity.casefold())
            reference(activity_id, "ACTIVITY", activity)
            relation(facility["facility_id"], "FACILITY", "HAS_ACTIVITY", activity_id, "ACTIVITY", evidence)
    for company in company_rows:
        for company_type in json.loads(company["company_types"]):
            type_id = stable_id("company-type", company_type.casefold())
            reference(type_id, "COMPANY_TYPE", company_type)
            relation(
                company["company_id"],
                "COMPANY",
                "HAS_COMPANY_TYPE",
                type_id,
                "COMPANY_TYPE",
                company["source_record_ids"],
            )

    reference_rows = sorted(reference_nodes.values(), key=lambda row: row["node_id"])
    relation_rows = sorted(relations.values(), key=lambda row: row["relation_id"])
    facility_counts: dict[str, int] = {}
    manufacturing_counts: dict[str, int] = {}
    for facility in facility_rows:
        company_id = facility["company_id"]
        facility_counts[company_id] = facility_counts.get(company_id, 0) + 1
        if "Manufacturing" in json.loads(facility["activities"]):
            manufacturing_counts[company_id] = manufacturing_counts.get(company_id, 0) + 1
    supplier_rows = []
    alias_rows = []
    for company in company_rows:
        company_types = set(json.loads(company["company_types"]))
        alias_rows.append(
            {
                "company_id": company["company_id"],
                "alias": company["canonical_name"],
                "normalized_alias": company["normalized_name"],
                "alias_type": "exact_source_name",
                "source_record_ids": company["source_record_ids"],
                **shared,
            }
        )
        if company_types & {"Equipment", "Materials"}:
            supplier_rows.append(
                {
                    "company_id": company["company_id"],
                    "canonical_name": company["canonical_name"],
                    "normalized_name": company["normalized_name"],
                    "company_types": company["company_types"],
                    "facility_count": facility_counts.get(company["company_id"], 0),
                    "manufacturing_facility_count": manufacturing_counts.get(company["company_id"], 0),
                    "baseline_supplier_scope": "SIA company type is Equipment or Materials",
                    "sme_status": "unknown",
                    "source_record_ids": company["source_record_ids"],
                    **shared,
                }
            )
    source_rows = [
        {
            "source_page_id": stable_id("source-page", source["url"]),
            "source_id": source["source_id"],
            "publisher": source["publisher"],
            "source_url": source["url"],
            "retrieved_at": retrieved_at,
            "page_sha256": page_sha,
            "parser_version": PARSER_VERSION,
            "source_record_count": len(records),
            "scope_note": source["scope_note"],
        }
    ]
    output.mkdir(parents=True, exist_ok=True)
    for filename, table in (
        ("companies.csv", company_rows),
        ("facilities.csv", facility_rows),
        ("reference_nodes.csv", reference_rows),
        ("relations.csv", relation_rows),
        ("source_pages.csv", source_rows),
        ("company_aliases.csv", alias_rows),
        ("supplier_baseline.csv", supplier_rows),
    ):
        write_csv(output / filename, table)

    type_counts: dict[str, int] = {}
    for row in company_rows:
        for value in json.loads(row["company_types"]):
            type_counts[value] = type_counts.get(value, 0) + 1
    relation_counts: dict[str, int] = {}
    for row in relation_rows:
        value = row["relation_type"]
        relation_counts[value] = relation_counts.get(value, 0) + 1
    equipment_materials = {
        row["company_id"]
        for row in company_rows
        if set(json.loads(row["company_types"])) & {"Equipment", "Materials"}
    }
    manufacturing = [row for row in facility_rows if "Manufacturing" in json.loads(row["activities"])]
    manifest = {
        "baseline_version": VERSION,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "retrieved_at": retrieved_at,
        "parser_version": PARSER_VERSION,
        "source": source,
        "page_sha256": page_sha,
        "counts": {
            "raw_source_records": len(raw_records),
            "parsed_source_records": len(records),
            "companies": len(company_rows),
            "facilities": len(facility_rows),
            "reference_nodes": len(reference_rows),
            "relations": len(relation_rows),
            "equipment_or_materials_companies": len(equipment_materials),
            "manufacturing_facilities": len(manufacturing),
        },
        "company_type_counts": dict(sorted(type_counts.items())),
        "relation_type_counts": dict(sorted(relation_counts.items())),
        "scope": "Known-incomplete SIA U.S. semiconductor ecosystem map baseline",
        "not_claimed": [
            "Complete U.S. semiconductor supplier population",
            "SME status",
            "Legal-entity resolution beyond exact normalized names",
            "Supplier-customer relationships",
            "Reconstruction of the unpublished original paper snapshot",
        ],
    }
    manifest_path = output / "baseline_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    snapshot_path = output / "source_snapshot.html.gz"
    with snapshot_path.open("wb") as raw_handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as gzip_handle:
            gzip_handle.write(page_bytes)
    filenames = [
        "companies.csv",
        "facilities.csv",
        "reference_nodes.csv",
        "relations.csv",
        "source_pages.csv",
        "company_aliases.csv",
        "supplier_baseline.csv",
        "baseline_manifest.json",
        "source_snapshot.html.gz",
    ]
    checksum_lines = [f"{hashlib.sha256((output / name).read_bytes()).hexdigest()}  {name}" for name in filenames]
    (output / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-html", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = json.loads(CONFIG.read_text())["sources"][0]
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    page = args.input_html.read_bytes() if args.input_html else fetch(source["url"], RAW_PAGE)
    print(json.dumps(build(page, source, retrieved_at, args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
