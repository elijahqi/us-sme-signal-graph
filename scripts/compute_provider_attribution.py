#!/usr/bin/env python3
"""Compute aggregate provider attribution from a transient URL-incidence CSV.

The input must contain query_id, provider, and canonical_url. It is deliberately
excluded from version control. This script emits aggregate counts only.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"


def registrable_domain(url: str) -> str:
    host = (urlsplit(url).hostname or "").casefold().removeprefix("www.")
    labels = host.split(".")
    suffix = ".".join(labels[-2:])
    if len(labels) > 2 and suffix in {"co.uk", "com.au", "co.jp", "com.br", "com.cn", "co.in"}:
        return ".".join(labels[-3:])
    return suffix


def compute(incidence_path: Path, verified_path: Path) -> dict:
    with incidence_path.open(encoding="utf-8", newline="") as handle:
        incidence = list(csv.DictReader(handle))
    if {row["provider"] for row in incidence} - {"brave", "you"}:
        raise ValueError("provider must be brave or you")
    with verified_path.open(encoding="utf-8", newline="") as handle:
        verified = list(csv.DictReader(handle))
    urls = defaultdict(set)
    query_urls = defaultdict(lambda: defaultdict(set))
    domains = defaultdict(set)
    for row in incidence:
        provider, url = row["provider"], row["canonical_url"]
        urls[provider].add(url); query_urls[row["query_id"]][provider].add(url)
        domains[provider].add(registrable_domain(url))
    strict = [row for row in verified if row.get("is_valid_supplier_strict") == "True"]
    net_new = [row for row in strict if row.get("baseline_disposition") == "novel_candidate"]

    def origin(row: dict[str, str]) -> str:
        brave = row["registrable_domain"] in domains["brave"]
        you = row["registrable_domain"] in domains["you"]
        return "both" if brave and you else "brave_only" if brave else "you_only" if you else "neither"

    origins = Counter(origin(row) for row in net_new)
    union = urls["brave"] | urls["you"]
    intersection = urls["brave"] & urls["you"]
    return {
        "formal_run": {"query_count": len(query_urls), "top_k": 10},
        "url_retrieval": {
            "brave_unique": len(urls["brave"]), "you_unique": len(urls["you"]),
            "union": len(union), "intersection": len(intersection),
            "jaccard": len(intersection) / len(union),
        },
        "provider_arms_net_new_strict": {
            "brave": origins["both"] + origins["brave_only"],
            "you": origins["both"] + origins["you_only"],
            "union": len(net_new), "intersection": origins["both"],
            "brave_marginal": origins["brave_only"], "you_marginal": origins["you_only"],
        },
        "per_query_url_counts": [
            {
                "query_id": query_id,
                "brave_unique_urls": len(values["brave"]),
                "you_unique_urls": len(values["you"]),
                "url_intersection": len(values["brave"] & values["you"]),
                "url_union": len(values["brave"] | values["you"]),
            }
            for query_id, values in sorted(query_urls.items())
        ],
        "provider_payloads_in_output": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidence", type=Path, required=True)
    parser.add_argument("--verified", type=Path, default=PRIVATE / "verification" / "verified_candidates.csv")
    parser.add_argument("--output", type=Path, default=PRIVATE / "metrics" / "provider_attribution.json")
    args = parser.parse_args()
    result = compute(args.incidence, args.verified)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
