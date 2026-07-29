#!/usr/bin/env python3
"""Create a provider-blind, domain-deduplicated candidate review pack."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from html import unescape
import json
from pathlib import Path
import random
import re


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private"
AGGREGATOR_DOMAINS = {
    "abachy.com", "ensun.io", "factmr.com", "globalspec.com", "indexbox.io", "inven.ai",
    "jeez-semicon.com", "kokoquest.com", "marketsandmarkets.com", "marketgrowthreports.com",
    "marketresearchfuture.com", "metoree.com", "mordorintelligence.com", "patentpc.com",
    "researchandmarkets.com", "selectscience.net", "semiconductor.directory",
    "semiconductor-today.com", "semiconductorreview.com", "semiconductorx.com", "techinsights.com",
    "thomasnet.com", "trendforce.com", "verifiedmarketresearch.com", "wikipedia.org",
}
NON_COMPANY_DOMAINS = {
    "archives.gov", "bakersfield.com", "businesswire.com", "cnbc.com", "justia.com",
    "edn.com", "georgetown.edu", "nsf.gov", "substack.com", "unisco.com",
}
NON_COMPANY_HINTS = (
    "top ", "market", "companies", "manufacturers in", "directory", "suppliers", "report",
    "article", "news", "research", "overview", "ranking", "guide", "wikipedia",
)


def normalize_name(value: str) -> str:
    value = unescape(value).casefold()
    value = re.sub(r"\b(incorporated|inc|corp|corporation|company|co|llc|ltd|limited|group)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def load_baseline() -> list[dict]:
    path = ROOT / "data" / "processed" / "baseline_v0_1_sia" / "supplier_baseline.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def token_set(value: str) -> set[str]:
    return {token for token in normalize_name(value).split() if len(token) > 1}


def conservative_baseline_match(name: str, baseline: list[dict]) -> tuple[str, str, float]:
    normalized = normalize_name(name)
    if not normalized:
        return "", "", 0.0
    query_tokens = token_set(normalized)
    best = ("", "", 0.0)
    for row in baseline:
        candidate = normalize_name(row["canonical_name"])
        if normalized == candidate:
            return row["company_id"], "exact_normalized_name", 1.0
        candidate_tokens = token_set(candidate)
        if not query_tokens or not candidate_tokens:
            continue
        intersection = len(query_tokens & candidate_tokens)
        union = len(query_tokens | candidate_tokens)
        score = intersection / union
        if score > best[2]:
            best = (row["company_id"], "token_jaccard_review", score)
    if best[2] >= 0.80:
        return best
    return "", "", best[2]


def source_kind(domain: str, title: str, site_name: str) -> str:
    combined = f"{title} {site_name}".casefold()
    if domain in AGGREGATOR_DOMAINS:
        return "aggregator_or_directory"
    if domain in NON_COMPANY_DOMAINS:
        return "news_government_research_or_logistics"
    if any(hint in combined for hint in NON_COMPANY_HINTS):
        return "review_non_company_possible"
    return "direct_company_candidate"


def build(input_csv: Path, output_dir: Path, seed: int) -> dict:
    with input_csv.open(encoding="utf-8", newline="") as handle:
        pages = list(csv.DictReader(handle))
    baseline = load_baseline()
    by_domain: dict[str, list[dict]] = {}
    for row in pages:
        by_domain.setdefault(row["registrable_domain"], []).append(row)

    candidates = []
    for domain, rows in sorted(by_domain.items()):
        successful = [row for row in rows if 200 <= int(row["http_status"] or 0) < 400]
        evidence_rows = successful or rows
        evidence_rows.sort(
            key=lambda row: (
                str(row["semiconductor_signal"]) == "True",
                str(row["manufacturing_signal"]) == "True",
                str(row["us_presence_signal"]) == "True",
                len(json.loads(row["capability_groups"] or "[]")),
            ),
            reverse=True,
        )
        primary = evidence_rows[0]
        names = [row["candidate_company_name"] for row in successful if row["candidate_company_name"]]
        proposed_name = min(names, key=len) if names else primary["candidate_company_name"]
        baseline_id, match_method, match_score = conservative_baseline_match(proposed_name, baseline)
        candidate_key = f"{domain}|{normalize_name(proposed_name)}"
        candidates.append(
            {
                "review_id": f"review-{hashlib.sha256(candidate_key.encode()).hexdigest()[:20]}",
                "registrable_domain": domain,
                "proposed_company_name": proposed_name,
                "source_kind_prelabel": source_kind(domain, primary["page_title"], primary["site_name"]),
                "successful_page_count": len(successful),
                "source_page_count": len(rows),
                "primary_candidate_id": primary["candidate_id"],
                "primary_evidence_url": primary["canonical_url"],
                "primary_page_sha256": primary["page_sha256"],
                "page_title": primary["page_title"],
                "meta_description": primary["meta_description"],
                "semiconductor_signal": any(row["semiconductor_signal"] == "True" for row in successful),
                "manufacturing_signal": any(row["manufacturing_signal"] == "True" for row in successful),
                "us_presence_signal": any(row["us_presence_signal"] == "True" for row in successful),
                "capability_groups": json.dumps(
                    sorted({group for row in successful for group in json.loads(row["capability_groups"] or "[]")})
                ),
                "matched_baseline_company_id": baseline_id,
                "baseline_match_method": match_method,
                "baseline_match_score": f"{match_score:.3f}",
                "is_valid_supplier_strict": "",
                "is_valid_supplier_lenient": "",
                "is_us_presence_confirmed": "",
                "is_direct_manufacturer_confirmed": "",
                "sme_status": "",
                "canonical_company_name": "",
                "valid_relation_types": "",
                "independent_confirmation_url": "",
                "evidence_quote": "",
                "annotator_confidence": "",
                "adjudication_status": "unreviewed",
                "review_notes": "",
            }
        )
    random.Random(seed).shuffle(candidates)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "blind_review.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
        writer.writeheader()
        writer.writerows(candidates)
    summary = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "random_seed": seed,
        "source_pages": len(pages),
        "unique_domains": len(candidates),
        "direct_company_candidate_prelabels": sum(row["source_kind_prelabel"] == "direct_company_candidate" for row in candidates),
        "aggregator_or_directory_prelabels": sum(row["source_kind_prelabel"] == "aggregator_or_directory" for row in candidates),
        "news_government_research_or_logistics_prelabels": sum(
            row["source_kind_prelabel"] == "news_government_research_or_logistics" for row in candidates
        ),
        "baseline_matches": sum(bool(row["matched_baseline_company_id"]) for row in candidates),
        "provider_origin_in_review_pack": False,
    }
    (output_dir / "review_manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PRIVATE / "formal_24q" / "source_candidates.csv")
    parser.add_argument("--output", type=Path, default=PRIVATE / "formal_24q" / "review")
    parser.add_argument("--seed", type=int, default=20260729)
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output, args.seed), indent=2))


if __name__ == "__main__":
    main()
