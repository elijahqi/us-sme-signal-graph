#!/usr/bin/env python3
"""Build and validate the frozen long-tail manufacturing query lattice."""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "experiments" / "long_tail_benchmark"
CAPABILITIES = BENCHMARK / "capability_set_v0_2.csv"
GEOGRAPHIES = BENCHMARK / "geographies_v0_1.csv"
INTENTS = BENCHMARK / "intent_templates_v0_1.csv"
OUTPUT = BENCHMARK / "query_lattice_v0_2.csv"
FIELDS = (
    "query_id", "capability_id", "industry_family", "capability_label",
    "state_id", "state_name", "census_region", "intent_id", "query", "status",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(
    capabilities: list[dict[str, str]],
    geographies: list[dict[str, str]],
    intents: list[dict[str, str]],
) -> list[dict[str, str]]:
    if len(capabilities) != 40:
        raise ValueError(f"expected 40 capabilities, found {len(capabilities)}")
    if len({row['industry_family'] for row in capabilities}) != 10:
        raise ValueError("expected exactly 10 industry families")
    if len(geographies) != 8 or len({row['census_region'] for row in geographies}) != 4:
        raise ValueError("expected eight states across four Census regions")
    if len(intents) != 3:
        raise ValueError("expected three intent templates")

    rows: list[dict[str, str]] = []
    for capability in capabilities:
        for geography in geographies:
            for intent in intents:
                query = intent["query_template"].format(
                    state_name=geography["state_name"],
                    state_abbr=geography["state_abbr"],
                    search_phrase=capability["search_phrase"],
                )
                rows.append({
                    "query_id": f"LTQ{len(rows) + 1:04d}",
                    "capability_id": capability["capability_id"],
                    "industry_family": capability["industry_family"],
                    "capability_label": capability["capability_label"],
                    "state_id": geography["state_id"],
                    "state_name": geography["state_name"],
                    "census_region": geography["census_region"],
                    "intent_id": intent["intent_id"],
                    "query": " ".join(query.split()),
                    "status": "freeze_v2",
                })

    if len(rows) != 960:
        raise ValueError(f"expected 960 queries, found {len(rows)}")
    queries = [row["query"].casefold() for row in rows]
    if len(queries) != len(set(queries)):
        raise ValueError("duplicate query strings in lattice")
    return rows


def render(rows: list[dict[str, str]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated output differs")
    args = parser.parse_args()
    rows = build_rows(read_csv(CAPABILITIES), read_csv(GEOGRAPHIES), read_csv(INTENTS))
    generated = render(rows)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != generated:
            raise SystemExit(f"stale generated query lattice: {OUTPUT}")
        print(f"validated {len(rows)} frozen queries; 9,600 requested rows per provider")
        return
    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"wrote {len(rows)} frozen queries to {OUTPUT}")


if __name__ == "__main__":
    main()
