#!/usr/bin/env python3
"""Persist rights-safe aggregates and independently fetch provider-blind source pages."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ingest_source_urls import (
    PageParser,
    candidate_name,
    canonicalize_url,
    fetch_url,
    registrable_domain,
)


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
DEFAULT_OUTPUT = BENCHMARK / "private" / "formal_v0_3"
LATTICE = BENCHMARK / "query_lattice_v0_2.csv"
AGGREGATE_FIELDS = (
    "run_id", "query_id", "executed_at", "brave_call_status", "you_call_status",
    "brave_returned_count", "you_returned_count", "canonical_url_intersection_count",
    "canonical_url_union_count", "brave_unique_domain_count", "you_unique_domain_count",
    "domain_intersection_count", "original_pages_fetched_count", "fetch_success_count",
    "brave_raw_disposition", "you_raw_disposition", "notes",
)
SOURCE_FIELDS = (
    "candidate_id", "canonical_url", "registrable_domain", "http_status", "robots_status",
    "retrieved_at", "page_sha256", "page_title", "site_name", "meta_description",
    "candidate_business_name", "fetch_error",
)
LINK_FIELDS = ("query_id", "candidate_id", "canonical_url")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def parse_input(stream) -> list[dict]:
    records = []
    for line_number, line in enumerate(stream, 1):
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if not isinstance(record.get("union_urls"), list):
            raise ValueError(f"line {line_number}: union_urls must be a list")
        records.append(record)
    return records


def validate_records(records: list[dict]) -> None:
    valid_query_ids = {row["query_id"] for row in read_csv(LATTICE)}
    seen = set()
    for record in records:
        query_id = record.get("query_id", "")
        if query_id not in valid_query_ids:
            raise ValueError(f"query not in frozen lattice: {query_id}")
        if query_id in seen:
            raise ValueError(f"duplicate query in batch: {query_id}")
        seen.add(query_id)
        for forbidden in ("brave_results", "you_results", "titles", "snippets", "ranks"):
            if forbidden in record:
                raise ValueError(f"raw provider field is forbidden: {forbidden}")


def fetch_source(url: str, output: Path, timeout: int) -> dict[str, object]:
    status, body, error, robots_status = fetch_url(url, timeout)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    sha = hashlib.sha256(body).hexdigest() if body else ""
    parser = PageParser()
    try:
        parser.feed(body.decode("utf-8", "replace"))
    except Exception as exc:
        error = f"{error}; parser={exc}".strip("; ")
    domain = registrable_domain(url)
    candidate_id = f"source-{hashlib.sha256(url.encode()).hexdigest()[:20]}"
    if body:
        page_dir = output / "source_pages"
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / f"{candidate_id}.html").write_bytes(body)
    return {
        "candidate_id": candidate_id,
        "canonical_url": url,
        "registrable_domain": domain,
        "http_status": status,
        "robots_status": robots_status,
        "retrieved_at": retrieved_at,
        "page_sha256": sha,
        "page_title": " ".join(parser.title_parts)[:300],
        "site_name": parser.meta.get("og:site_name", "")[:200],
        "meta_description": (parser.meta.get("description") or parser.meta.get("og:description") or "")[:1000],
        "candidate_business_name": candidate_name(parser, domain),
        "fetch_error": error,
    }


def process(records: list[dict], output: Path, run_id: str, timeout: int, workers: int) -> dict:
    validate_records(records)
    output.mkdir(parents=True, exist_ok=True)
    sources_path = output / "source_candidates.csv"
    links_path = output / "query_source_links.csv"
    aggregates_path = output / "query_aggregates.csv"

    old_sources = {row["canonical_url"]: row for row in read_csv(sources_path)}
    all_urls = {
        canonicalize_url(url)
        for record in records
        for url in record["union_urls"]
        if canonicalize_url(url)
    }
    new_urls = sorted(all_urls - old_sources.keys())
    fetched = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {executor.submit(fetch_source, url, output, timeout): url for url in new_urls}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            fetched[row["canonical_url"]] = row
            print(
                f"[{index}/{len(new_urls)}] {row['http_status']} {row['registrable_domain']} {row['robots_status']}",
                file=sys.stderr,
            )
    sources = {**old_sources, **fetched}
    write_csv(sources_path, sorted(sources.values(), key=lambda row: row["candidate_id"]), SOURCE_FIELDS)

    old_links = {(row["query_id"], row["canonical_url"]): row for row in read_csv(links_path)}
    links = dict(old_links)
    fetch_counts = {}
    for record in records:
        canonical_urls = sorted({canonicalize_url(url) for url in record["union_urls"] if canonicalize_url(url)})
        successful = 0
        for url in canonical_urls:
            source = sources[url]
            links[(record["query_id"], url)] = {
                "query_id": record["query_id"],
                "candidate_id": source["candidate_id"],
                "canonical_url": url,
            }
            successful += 200 <= int(source["http_status"] or 0) < 300
        fetch_counts[record["query_id"]] = (len(canonical_urls), successful)
    write_csv(links_path, sorted(links.values(), key=lambda row: (row["query_id"], row["candidate_id"])), LINK_FIELDS)

    aggregates = {row["query_id"]: row for row in read_csv(aggregates_path)}
    for record in records:
        fetched_count, success_count = fetch_counts[record["query_id"]]
        aggregates[record["query_id"]] = {
            **{field: record.get(field, "") for field in AGGREGATE_FIELDS},
            "run_id": run_id,
            "original_pages_fetched_count": fetched_count,
            "fetch_success_count": success_count,
            "brave_raw_disposition": "destroyed_in_process_memory",
            "you_raw_disposition": record.get("you_raw_disposition", "not_persisted_pending_terms_review"),
        }
    write_csv(aggregates_path, sorted(aggregates.values(), key=lambda row: row["query_id"]), AGGREGATE_FIELDS)

    manifest = {
        "run_id": run_id,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "completed_query_count": len(aggregates),
        "source_url_count": len(sources),
        "query_source_link_count": len(links),
        "new_source_url_count": len(new_urls),
        "provider_payloads_stored": False,
        "brave_raw_lifecycle": "transient_process_memory_only",
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="NDJSON batch; default stdin")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--run-id", default="formal_v0_3")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    stream = args.input.open(encoding="utf-8") if args.input else sys.stdin
    try:
        records = parse_input(stream)
    finally:
        if args.input:
            stream.close()
    if not records:
        raise SystemExit("No query aggregate records provided")
    print(json.dumps(process(records, args.output, args.run_id, args.timeout, args.workers), indent=2))


if __name__ == "__main__":
    main()
