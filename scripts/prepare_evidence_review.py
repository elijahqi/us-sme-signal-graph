#!/usr/bin/env python3
"""Add provider-blind evidence windows from independently fetched pages."""

from __future__ import annotations

import argparse
import csv
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"
TERMS = (
    "semiconductor", "wafer", "manufactur", "fabricat", "contract manufactur", "machine shop",
    "vacuum", "metrology", "lithography", "etch", "deposition", "cmp", "gas delivery",
    "wet process", "thermal process", "packaging", "test socket", "probe", "united states",
    "u.s.", "usa", "headquartered", "facility", "located in",
)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "svg", "noscript", "nav", "footer"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg", "noscript", "nav", "footer"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        value = re.sub(r"\s+", " ", unescape(data)).strip()
        if len(value) >= 3:
            self.parts.append(value)


def evidence_windows(text: str, limit: int = 4, radius: int = 240) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    lowered = normalized.casefold()
    hits = []
    for term in TERMS:
        start = 0
        while len(hits) < 80:
            index = lowered.find(term, start)
            if index < 0:
                break
            hits.append(index)
            start = index + len(term)
    windows = []
    for index in sorted(set(hits)):
        window = normalized[max(0, index - radius) : min(len(normalized), index + radius)].strip()
        if window and all(window[:100] not in existing for existing in windows):
            windows.append(window)
        if len(windows) >= limit:
            break
    return windows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, default=PRIVATE / "review" / "blind_review.csv")
    parser.add_argument("--pages", type=Path, default=PRIVATE / "source_pages")
    parser.add_argument("--output", type=Path, default=PRIVATE / "review" / "blind_review_with_evidence.csv")
    args = parser.parse_args()
    with args.review.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    output_rows = []
    for row in rows:
        page = args.pages / f"{row['primary_candidate_id']}.html"
        windows = []
        if page.exists():
            visible = VisibleText()
            visible.feed(page.read_text(encoding="utf-8", errors="replace"))
            windows = evidence_windows(" ".join(visible.parts))
        output_rows.append(
            {**row, "source_evidence_windows": json.dumps(windows, ensure_ascii=False), "evidence_window_count": len(windows)}
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(json.dumps({"rows": len(output_rows), "with_evidence": sum(bool(row["evidence_window_count"]) for row in output_rows)}, indent=2))


if __name__ == "__main__":
    main()
