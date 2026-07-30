#!/usr/bin/env python3
"""Build a deterministic provider-blind probability sample from the closed corpus."""

from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3"
SEED = 20260730
TARGET = 1200
DOUBLE_TARGET = 300


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def stable_pick(rows: list[dict], n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    values = list(rows)
    rng.shuffle(values)
    return values[:n]


def build() -> tuple[list[dict], dict]:
    lattice = {row["query_id"]: row for row in read_csv(BENCHMARK / "query_lattice_v0_2.csv")}
    sources = {row["candidate_id"]: row for row in read_csv(PRIVATE / "source_candidates.csv")}
    links = read_csv(PRIVATE / "query_source_links.csv")
    candidates = {}
    for link in links:
        source = sources[link["candidate_id"]]
        query = lattice[link["query_id"]]
        key = (link["candidate_id"], query["capability_id"], query["state_id"])
        current = candidates.setdefault(key, {
            "review_id": "review-" + hashlib.sha256("|".join(key).encode()).hexdigest()[:20],
            "candidate_id": link["candidate_id"],
            "capability_id": query["capability_id"],
            "industry_family": query["industry_family"],
            "state_id": query["state_id"],
            "query_intents": set(),
            "source_url": source["canonical_url"],
            "registrable_domain": source["registrable_domain"],
            "http_status": source["http_status"],
            "robots_status": source["robots_status"],
            "page_sha256": source["page_sha256"],
            "sampling_stratum": "",
            "inclusion_probability": "",
            "double_review": "false",
        })
        current["query_intents"].add(query["intent_id"])

    eligible = []
    for row in candidates.values():
        if not (200 <= int(row["http_status"] or 0) < 300):
            continue
        row["query_intents"] = "|".join(sorted(row["query_intents"]))
        primary_intent = (
            "micro_local" if "micro_local" in row["query_intents"]
            else "small_batch" if "small_batch" in row["query_intents"]
            else "direct"
        )
        row["sampling_stratum"] = f"{row['industry_family']}|{primary_intent}"
        eligible.append(row)

    strata = defaultdict(list)
    for row in eligible:
        strata[row["sampling_stratum"]].append(row)
    allocation = {}
    fractions = []
    for stratum, rows in strata.items():
        exact = TARGET * len(rows) / len(eligible)
        allocation[stratum] = min(len(rows), math.floor(exact))
        fractions.append((exact - math.floor(exact), stratum))
    remaining = TARGET - sum(allocation.values())
    for _, stratum in sorted(fractions, reverse=True):
        if remaining <= 0:
            break
        if allocation[stratum] < len(strata[stratum]):
            allocation[stratum] += 1
            remaining -= 1
    if remaining:
        raise ValueError("unable to allocate target sample")

    sample = []
    for index, (stratum, rows) in enumerate(sorted(strata.items())):
        picked = stable_pick(rows, allocation[stratum], SEED + index)
        probability = allocation[stratum] / len(rows)
        for row in picked:
            row["inclusion_probability"] = f"{probability:.12f}"
        sample.extend(picked)
    sample.sort(key=lambda row: row["review_id"])
    double = {row["review_id"] for row in stable_pick(sample, DOUBLE_TARGET, SEED + 999)}
    for row in sample:
        row["double_review"] = str(row["review_id"] in double).lower()

    if len(sample) != TARGET or len(double) != DOUBLE_TARGET:
        raise ValueError("sample-size invariant failed")
    manifest = {
        "seed": SEED,
        "eligible_company_capability_state_pairs": len(eligible),
        "sample_rows": len(sample),
        "double_review_rows": len(double),
        "stratum_population": {key: len(value) for key, value in sorted(strata.items())},
        "stratum_sample": dict(sorted(allocation.items())),
        "provider_columns_in_sample": False,
    }
    return sample, manifest


def main() -> None:
    sample, manifest = build()
    output = PRIVATE / "review_sample_v0_1.csv"
    fields = list(sample[0])
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(sample)
    manifest["sample_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    (PRIVATE / "review_sample_manifest_v0_1.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
