#!/usr/bin/env python3
"""Prepare provider-blind evidence batches for all non-calibration census pairs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import prepare_ai_review_batches as evidence_tools


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3"
OUTPUT = PRIVATE / "ai_census_v0_4"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_pairs() -> list[dict]:
    lattice = {row["query_id"]: row for row in read_csv(BENCHMARK / "query_lattice_v0_2.csv")}
    sources = {row["candidate_id"]: row for row in read_csv(PRIVATE / "source_candidates.csv")}
    capabilities = {row["capability_id"]: row for row in read_csv(BENCHMARK / "capability_set_v0_2.csv")}
    states = {row["state_id"]: row for row in read_csv(BENCHMARK / "geographies_v0_1.csv")}
    sampled = {row["review_id"] for row in read_csv(PRIVATE / "review_sample_v0_1.csv")}
    pairs = {}
    for link in read_csv(PRIVATE / "query_source_links.csv"):
        query = lattice[link["query_id"]]
        source = sources[link["candidate_id"]]
        if not 200 <= int(source["http_status"] or 0) < 300:
            continue
        key = (link["candidate_id"], query["capability_id"], query["state_id"])
        row = pairs.setdefault(key, {
            "review_id": "review-" + hashlib.sha256("|".join(key).encode()).hexdigest()[:20],
            "candidate_id": link["candidate_id"], "capability_id": query["capability_id"],
            "industry_family": query["industry_family"], "state_id": query["state_id"],
            "query_intents": set(), "source_url": source["canonical_url"],
            "registrable_domain": source["registrable_domain"], "page_sha256": source["page_sha256"],
        })
        row["query_intents"].add(query["intent_id"])
    if len(pairs) != 6164:
        raise ValueError(f"expected 6164 eligible pairs, got {len(pairs)}")
    rows = []
    for row in pairs.values():
        if row["review_id"] in sampled:
            continue
        source = sources[row["candidate_id"]]; capability = capabilities[row["capability_id"]]; state = states[row["state_id"]]
        text = evidence_tools.visible_text(PRIVATE / "source_pages" / f"{row['candidate_id']}.html")
        keywords = capability["search_phrase"].split() + [capability["capability_label"], state["state_name"], state["state_abbr"]]
        rows.append({
            "review_id": row["review_id"], "candidate_id": row["candidate_id"],
            "capability_id": row["capability_id"], "industry_family": row["industry_family"],
            "queried_state_id": row["state_id"], "queried_state": state["state_name"],
            "query_intents": "|".join(sorted(row["query_intents"])),
            "source_url": row["source_url"], "registrable_domain": row["registrable_domain"],
            "page_title": source["page_title"], "meta_description": source["meta_description"],
            "task": {"capability_label": capability["capability_label"], "positive_scope": capability["positive_scope"], "explicit_exclusions": capability["explicit_exclusions"]},
            "evidence_excerpt": evidence_tools.evidence_window(text, keywords), "page_sha256": row["page_sha256"],
        })
    rows.sort(key=lambda row: row["review_id"])
    if len(rows) != 4964:
        raise ValueError(f"expected 4964 new census rows, got {len(rows)}")
    return rows


def main() -> None:
    rows = build_pairs(); OUTPUT.mkdir(parents=True, exist_ok=True); batches = OUTPUT / "batches"; batches.mkdir(exist_ok=True)
    for old in batches.glob("batch-*.json"): old.unlink()
    for index in range(0, len(rows), 10):
        number = index // 10 + 1
        (batches / f"batch-{number:03d}.json").write_text(json.dumps({"batch_id": f"census-{number:03d}", "rows": rows[index:index+10]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"total_eligible_pairs": 6164, "reused_calibration_rows": 1200, "new_rows": len(rows), "batches": (len(rows)+9)//10, "last_batch_size": len(rows)%10, "provider_fields_in_evidence": False}
    (OUTPUT / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n"); print(json.dumps(manifest, indent=2))


if __name__ == "__main__": main()
