#!/usr/bin/env python3
"""Validate a completed long-tail run and produce a rights-safe aggregate snapshot."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3"
LATTICE = BENCHMARK / "query_lattice_v0_2.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize(private: Path = PRIVATE) -> dict:
    lattice = read_csv(LATTICE)
    aggregates = read_csv(private / "query_aggregates.csv")
    sources = read_csv(private / "source_candidates.csv")
    links = read_csv(private / "query_source_links.csv")
    expected = [row["query_id"] for row in lattice]
    actual = [row["query_id"] for row in aggregates]
    if len(actual) != len(set(actual)):
        raise ValueError("duplicate aggregate query IDs")
    if set(actual) != set(expected):
        raise ValueError(
            f"query coverage mismatch: missing={sorted(set(expected)-set(actual))}, "
            f"extra={sorted(set(actual)-set(expected))}"
        )
    source_ids = [row["candidate_id"] for row in sources]
    source_urls = [row["canonical_url"] for row in sources]
    if len(source_ids) != len(set(source_ids)) or len(source_urls) != len(set(source_urls)):
        raise ValueError("duplicate source ID or canonical URL")
    source_id_set = set(source_ids)
    if any(row["candidate_id"] not in source_id_set for row in links):
        raise ValueError("query link references unknown source")
    if any(row["query_id"] not in set(expected) for row in links):
        raise ValueError("query link references unknown query")

    lattice_by_id = {row["query_id"]: row for row in lattice}
    dimensions = {
        "industry_family": defaultdict(lambda: Counter()),
        "intent_id": defaultdict(lambda: Counter()),
        "state_id": defaultdict(lambda: Counter()),
    }
    for row in aggregates:
        metadata = lattice_by_id[row["query_id"]]
        for dimension in dimensions:
            counter = dimensions[dimension][metadata[dimension]]
            counter["queries"] += 1
            counter["brave_rows"] += int(row["brave_returned_count"])
            counter["you_rows"] += int(row["you_returned_count"])
            counter["url_intersection"] += int(row["canonical_url_intersection_count"])
            counter["url_union"] += int(row["canonical_url_union_count"])
            counter["domain_intersection"] += int(row["domain_intersection_count"])
            union = int(row["canonical_url_union_count"])
            if union:
                counter["query_jaccard_sum"] += int(row["canonical_url_intersection_count"]) / union

    statuses = Counter(row["http_status"] or "0" for row in sources)
    robots = Counter(row["robots_status"] for row in sources)
    brave_rows = sum(int(row["brave_returned_count"]) for row in aggregates)
    you_rows = sum(int(row["you_returned_count"]) for row in aggregates)
    url_intersection = sum(int(row["canonical_url_intersection_count"]) for row in aggregates)
    url_union = sum(int(row["canonical_url_union_count"]) for row in aggregates)
    per_query_jaccard = [
        int(row["canonical_url_intersection_count"]) / int(row["canonical_url_union_count"])
        for row in aggregates if int(row["canonical_url_union_count"])
    ]
    summary = {
        "run_id": "formal_v0_3",
        "frozen_commit": "9fb6d4280ec42aa858f8219c4f4dc310a880f41a",
        "query_count": len(aggregates),
        "brave_returned_rows": brave_rows,
        "you_returned_rows": you_rows,
        "brave_failed_queries": sum(row["brave_call_status"] != "success" for row in aggregates),
        "you_failed_queries": sum(row["you_call_status"] != "success" for row in aggregates),
        "query_level_url_intersection_sum": url_intersection,
        "query_level_url_union_sum": url_union,
        "pooled_query_url_jaccard": url_intersection / url_union if url_union else None,
        "macro_mean_query_url_jaccard": (sum(per_query_jaccard) / len(per_query_jaccard)) if per_query_jaccard else None,
        "unique_original_source_urls": len(sources),
        "query_source_links": len(links),
        "source_fetch_2xx": sum(200 <= int(row["http_status"] or 0) < 300 for row in sources),
        "source_http_status_counts": dict(sorted(statuses.items())),
        "robots_status_counts": dict(sorted(robots.items())),
        "source_hard_timeouts": sum("hard_timeout" in row["fetch_error"] for row in sources),
        "provider_payloads_stored": False,
        "brave_raw_lifecycle": "transient_process_memory_only",
        "dimensions": {
            dimension: {
                key: {
                    **dict(value),
                    "pooled_url_jaccard": value["url_intersection"] / value["url_union"] if value["url_union"] else None,
                    "macro_mean_query_url_jaccard": value["query_jaccard_sum"] / value["queries"] if value["queries"] else None,
                }
                for key, value in sorted(groups.items())
            }
            for dimension, groups in dimensions.items()
        },
        "private_artifact_sha256": {
            filename: sha256_file(private / filename)
            for filename in ("query_aggregates.csv", "query_source_links.csv", "source_candidates.csv")
        },
        "frozen_input_sha256": {
            filename: sha256_file(BENCHMARK / filename)
            for filename in (
                "capability_set_v0_2.csv", "geographies_v0_1.csv",
                "intent_templates_v0_1.csv", "query_lattice_v0_2.csv",
            )
        },
    }
    return summary


def main() -> None:
    summary = summarize()
    output = PRIVATE / "aggregate_snapshot.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
