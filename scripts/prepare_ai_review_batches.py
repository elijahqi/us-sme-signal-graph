#!/usr/bin/env python3
"""Prepare frozen, provider-blind evidence packs for TraeCLI headless review."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ingest_source_urls import PageParser


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
PRIVATE = BENCHMARK / "private" / "formal_v0_3"
OUTPUT = PRIVATE / "ai_review_v0_1"
BATCH_SIZE = 10
MAX_EVIDENCE_CHARS = 9000


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def visible_text(path: Path) -> str:
    if not path.exists():
        return ""
    parser = PageParser()
    try:
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return ""
    text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip()
    boilerplate_patterns = (
        r"we use cookies.{0,5000}?(?=(?:products|services|about us|capabilities|home)\b)",
        r"this website uses cookies.{0,5000}?(?=(?:products|services|about us|capabilities|home)\b)",
        r"cookie settings.{0,3000}?(?=(?:products|services|about us|capabilities|home)\b)",
    )
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def evidence_window(text: str, keywords: list[str], limit: int = MAX_EVIDENCE_CHARS) -> str:
    if not text:
        return ""
    lowered = text.casefold()
    spans = []
    useful = [
        keyword.casefold() for keyword in keywords
        if len(keyword) >= 4 and keyword.casefold() not in {
            "manufacturer", "manufacturing", "small", "business", "custom"
        }
    ]
    useful += [
        "about us", "capabilities", "our facility", "our facilities",
        "located in", "headquartered", "family owned", "employees",
        "production", "fabrication", "contract manufacturing",
    ]
    for keyword in useful:
        start = 0
        found = 0
        while found < 3:
            index = lowered.find(keyword, start)
            if index < 0:
                break
            spans.append((max(0, index - 450), min(len(text), index + len(keyword) + 900)))
            start = index + len(keyword)
            found += 1
    if not spans:
        spans = [(0, min(len(text), 1800))]
    spans.sort()
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1] + 100:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    chunks = []
    used = 0
    for start, end in merged:
        chunk = text[start:end].strip()
        if not chunk:
            continue
        remaining = limit - used
        if remaining <= 0:
            break
        chunks.append(chunk[:remaining])
        used += min(len(chunk), remaining)
    return "\n[...]\n".join(chunks)


def prepare() -> dict:
    sample = read_csv(PRIVATE / "review_sample_v0_1.csv")
    if len(sample) != 1200:
        raise ValueError(f"expected 1200 review rows, got {len(sample)}")
    sources = {row["candidate_id"]: row for row in read_csv(PRIVATE / "source_candidates.csv")}
    capabilities = {row["capability_id"]: row for row in read_csv(BENCHMARK / "capability_set_v0_2.csv")}
    states = {row["state_id"]: row for row in read_csv(BENCHMARK / "geographies_v0_1.csv")}
    evidence = []
    for row in sample:
        source = sources[row["candidate_id"]]
        capability = capabilities[row["capability_id"]]
        state = states[row["state_id"]]
        text = visible_text(PRIVATE / "source_pages" / f"{row['candidate_id']}.html")
        keywords = capability["search_phrase"].split() + [
            capability["capability_label"], state["state_name"], state["state_abbr"]
        ]
        evidence.append({
            "review_id": row["review_id"],
            "capability_id": row["capability_id"],
            "industry_family": row["industry_family"],
            "queried_state": state["state_name"],
            "query_intents": row["query_intents"],
            "source_url": row["source_url"],
            "registrable_domain": row["registrable_domain"],
            "page_title": source["page_title"],
            "meta_description": source["meta_description"],
            "task": {
                "capability_label": capability["capability_label"],
                "positive_scope": capability["positive_scope"],
                "explicit_exclusions": capability["explicit_exclusions"],
            },
            "evidence_excerpt": evidence_window(text, keywords),
            "page_sha256": row["page_sha256"],
        })
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evidence_path = OUTPUT / "evidence_rows.jsonl"
    evidence_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in evidence),
        encoding="utf-8",
    )
    batches = OUTPUT / "batches"
    batches.mkdir(exist_ok=True)
    for index in range(0, len(evidence), BATCH_SIZE):
        number = index // BATCH_SIZE + 1
        payload = {
            "batch_id": f"batch-{number:03d}",
            "rows": evidence[index:index + BATCH_SIZE],
        }
        (batches / f"batch-{number:03d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    manifest = {
        "rows": len(evidence),
        "batches": len(evidence) // BATCH_SIZE,
        "batch_size": BATCH_SIZE,
        "max_evidence_chars": MAX_EVIDENCE_CHARS,
        "rows_with_empty_evidence": sum(not row["evidence_excerpt"] for row in evidence),
        "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "provider_fields_in_evidence": False,
    }
    (OUTPUT / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return manifest


def main() -> None:
    print(json.dumps(prepare(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
