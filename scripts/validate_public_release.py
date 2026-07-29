#!/usr/bin/env python3
"""Fail closed when the public release violates scope or integrity contracts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_COLUMNS = {
    "provider", "provider_origin", "rank", "snippet", "evidence_quote",
    "source_evidence_windows", "review_notes",
}
FORBIDDEN_TEXT = ("/Users/", "byted.org", "bytedance.com", "BRAVE_API_KEY", "YOU_API_KEY")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(release: Path) -> dict:
    required = {
        "README.md", "DATA_LICENSE.md", "verified_supplier_candidates.csv",
        "pilot_metrics.json", "release_manifest.json", "SHA256SUMS",
    }
    missing = sorted(required - {path.name for path in release.iterdir() if path.is_file()})
    if missing:
        raise ValueError(f"missing public release files: {missing}")
    expected = {}
    for line in (release / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        expected[name] = digest
    checked = 0
    for name, digest in expected.items():
        path = release / name
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f"checksum mismatch: {name}")
        checked += 1
    with (release / "verified_supplier_candidates.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        rows = list(reader)
    forbidden = sorted(fields & FORBIDDEN_COLUMNS)
    if forbidden:
        raise ValueError(f"forbidden public columns: {forbidden}")
    if any(row["sme_evidence_status"] == "confirmed_sme" for row in rows):
        raise ValueError("confirmed_sme is not supported in this release")
    manifest = json.loads((release / "release_manifest.json").read_text())
    if len(rows) != manifest["candidate_rows"]:
        raise ValueError("candidate count differs from release manifest")
    for path in release.iterdir():
        if not path.is_file() or path.suffix not in {".md", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in FORBIDDEN_TEXT:
            if marker in text:
                raise ValueError(f"forbidden public marker in {path.name}: {marker}")
    return {"candidate_rows": len(rows), "checksums_verified": checked, "confirmed_sme_rows": 0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path, nargs="?", default=ROOT / "release" / "public" / "v0.2.0-rc1")
    args = parser.parse_args()
    print(json.dumps(validate(args.release), indent=2))


if __name__ == "__main__":
    main()
