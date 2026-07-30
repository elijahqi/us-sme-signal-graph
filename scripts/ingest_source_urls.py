#!/usr/bin/env python3
"""Fetch original source URLs and build a provider-blind local review corpus."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from urllib import robotparser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private"
TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
CAPABILITIES = {
    "lithography": ("lithography", "photoresist", "euv"),
    "etch": ("etch", "plasma chamber", "reactive ion"),
    "deposition": ("deposition", "cvd", "pvd", "ald", "mocvd"),
    "cmp": ("chemical mechanical", "cmp", "polishing"),
    "metrology": ("metrology", "inspection", "measurement"),
    "wafer_handling": ("wafer handling", "wafer automation", "wafer robot"),
    "vacuum": ("vacuum chamber", "vacuum pump", "ultra-high vacuum", "uhv"),
    "gas_delivery": ("gas delivery", "gas system", "ultra high purity gas"),
    "wet_processing": ("wet process", "wet bench", "wafer cleaning"),
    "thermal_processing": ("thermal process", "furnace", "rapid thermal"),
    "packaging": ("semiconductor packaging", "assembly equipment", "packaging equipment"),
    "test": ("semiconductor test", "probe card", "test socket", "handler"),
}
MANUFACTURING_TERMS = (
    "manufacturer", "manufacturing", "fabrication", "fabricator", "machining",
    "machine shop", "contract manufacturing", "we manufacture", "production facility",
)
SEMICONDUCTOR_TERMS = ("semiconductor", "wafer fab", "microchip", "chipmaking")
US_TERMS = (
    "united states", "u.s.", "usa", "american manufacturer", "new jersey", "california",
    "arizona", "texas", "massachusetts", "new york", "pennsylvania", "ohio", "michigan",
    "minnesota", "oregon", "washington", "connecticut", "colorado", "florida", "illinois",
    "north carolina", "south carolina", "virginia", "wisconsin", "indiana", "georgia",
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.in_title = False
        self.skip_depth = 0
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
        if tag in {"script", "style", "svg", "noscript"}:
            self.skip_depth += 1
        if tag == "meta":
            key = (attr.get("property") or attr.get("name") or "").lower()
            if key and attr.get("content"):
                self.meta[key] = attr["content"]

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag in {"script", "style", "svg", "noscript"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", unescape(data)).strip()
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        if not self.skip_depth:
            self.text_parts.append(value)


def canonicalize_url(value: str) -> str:
    value = value.strip()
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    host = parts.hostname.casefold() if parts.hostname else ""
    if parts.port and parts.port not in {80, 443}:
        host = f"{host}:{parts.port}"
    query = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_") and key.casefold() not in TRACKING_PARAMS
    ]
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.casefold(), host, path, urlencode(query), ""))


def registrable_domain(url: str) -> str:
    host = (urlsplit(url).hostname or "").casefold().removeprefix("www.")
    labels = host.split(".")
    if len(labels) <= 2:
        return host
    common_second_level = {"co.uk", "com.au", "co.jp", "com.br", "com.cn", "co.in"}
    suffix2 = ".".join(labels[-2:])
    return ".".join(labels[-3:]) if suffix2 in common_second_level else suffix2


def normalize_name(value: str) -> str:
    value = unescape(value).casefold()
    value = re.sub(r"\b(incorporated|inc|corp|corporation|company|co|llc|ltd|limited)\b", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def candidate_name(parser: PageParser, domain: str) -> str:
    choices = [parser.meta.get("og:site_name", ""), " ".join(parser.title_parts)]
    for choice in choices:
        choice = re.split(r"\s+[|—–-]\s+", unescape(choice))[0].strip()
        if 1 < len(choice) < 120 and choice.casefold() not in {"home", "homepage"}:
            return choice
    return domain.split(".")[0].replace("-", " ").title()


def load_baseline() -> dict[str, str]:
    path = ROOT / "data" / "processed" / "baseline_v0_1_sia" / "supplier_baseline.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {normalize_name(row["canonical_name"]): row["company_id"] for row in csv.DictReader(handle)}


ROBOTS_CACHE: dict[str, tuple[bool, str]] = {}
ROBOTS_LOCK = threading.Lock()


def robots_allowed(url: str, timeout: int) -> tuple[bool, str]:
    parts = urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    with ROBOTS_LOCK:
        if origin in ROBOTS_CACHE:
            return ROBOTS_CACHE[origin]
    robots_url = f"{origin}/robots.txt"
    try:
        result = subprocess.run(
            ["curl", "-LsS", "--max-time", str(min(timeout, 15)), "-A", "US-SME-Signal-Graph/0.1 public-research", robots_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=min(timeout, 15) + 5,
        )
    except subprocess.TimeoutExpired:
        decision = (True, "robots_hard_timeout_allow")
        with ROBOTS_LOCK:
            ROBOTS_CACHE[origin] = decision
        return decision
    if result.returncode:
        decision = (True, "robots_unavailable_allow")
    else:
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(result.stdout.decode("utf-8", "replace").splitlines())
        decision = (
            parser.can_fetch("US-SME-Signal-Graph", url),
            "robots_allowed" if parser.can_fetch("US-SME-Signal-Graph", url) else "robots_disallowed",
        )
    with ROBOTS_LOCK:
        ROBOTS_CACHE[origin] = decision
    return decision


def fetch_url(url: str, timeout: int) -> tuple[int, bytes, str, str]:
    allowed, robots_status = robots_allowed(url, timeout)
    if not allowed:
        return 0, b"", "robots_disallowed", robots_status
    last = (0, b"", "")
    for attempt in range(2):
        try:
            result = subprocess.run(
                [
                    "curl", "-LsS", "--retry", "1", "--retry-delay", "1", "--max-time", str(timeout),
                    "-A", "Mozilla/5.0 (compatible; US-SME-Signal-Graph/0.1; public research)",
                    "-H", "Accept: text/html,application/xhtml+xml", "-w", "\n__HTTP_STATUS__:%{http_code}", url,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + 10,
            )
        except subprocess.TimeoutExpired:
            last = (0, b"", f"subprocess_hard_timeout_after_{timeout + 10}s")
            if attempt == 0:
                time.sleep(1)
                continue
            break
        payload = result.stdout
        marker = b"\n__HTTP_STATUS__:"
        if marker not in payload:
            last = (0, b"", result.stderr.decode("utf-8", "replace")[-500:])
        else:
            body, status = payload.rsplit(marker, 1)
            try:
                code = int(status.strip())
            except ValueError:
                code = 0
            error = result.stderr.decode("utf-8", "replace")[-500:] if result.returncode else ""
            last = (code, body, error)
            if 200 <= code < 400:
                return (*last, robots_status)
        if attempt == 0:
            time.sleep(1)
    return (*last, robots_status)


def process_url(url: str, output: Path, timeout: int, baseline: dict[str, str]) -> dict:
    status, body, error, robots_status = fetch_url(url, timeout)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    sha = hashlib.sha256(body).hexdigest() if body else ""
    parser = PageParser()
    try:
        parser.feed(body.decode("utf-8", "replace"))
    except Exception as exc:
        error = f"{error}; parser={exc}".strip("; ")
    text = " ".join(parser.text_parts).casefold()[:500_000]
    usable = 200 <= status < 400
    domain = registrable_domain(url)
    name = candidate_name(parser, domain)
    normalized = normalize_name(name)
    groups = [group for group, terms in CAPABILITIES.items() if any(term in text for term in terms)]
    candidate_id = f"candidate-{hashlib.sha256(url.encode()).hexdigest()[:20]}"
    raw_dir = output / "source_pages"
    if body:
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"{candidate_id}.html").write_bytes(body)
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
        "candidate_company_name": name,
        "semiconductor_signal": usable and any(term in text for term in SEMICONDUCTOR_TERMS),
        "manufacturing_signal": usable and any(term in text for term in MANUFACTURING_TERMS),
        "us_presence_signal": usable and any(term in text for term in US_TERMS),
        "capability_groups": json.dumps(groups if usable else []),
        "matched_baseline_company_id": baseline.get(normalized, ""),
        "baseline_match_method": "exact_normalized_name" if normalized in baseline else "",
        "review_status": "needs_review",
        "fetch_error": error,
    }


def ingest(urls: list[str], output: Path, timeout: int, workers: int = 8) -> dict:
    canonical_urls = sorted({canonicalize_url(url) for url in urls if canonicalize_url(url)})
    baseline = load_baseline()
    rows = []
    output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {executor.submit(process_url, url, output, timeout, baseline): url for url in canonical_urls}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            print(f"[{index}/{len(canonical_urls)}] {row['http_status']} {row['registrable_domain']} {row['robots_status']}", file=sys.stderr)
    rows.sort(key=lambda row: row["candidate_id"])
    output.mkdir(parents=True, exist_ok=True)
    with (output / "source_candidates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    manifest = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_url_count": len(urls),
        "canonical_url_count": len(canonical_urls),
        "fetched_2xx": sum(200 <= int(row["http_status"]) < 300 for row in rows),
        "semiconductor_signal": sum(bool(row["semiconductor_signal"]) for row in rows),
        "manufacturing_signal": sum(bool(row["manufacturing_signal"]) for row in rows),
        "us_presence_signal": sum(bool(row["us_presence_signal"]) for row in rows),
        "exact_baseline_matches": sum(bool(row["matched_baseline_company_id"]) for row in rows),
        "robots_disallowed": sum(row["robots_status"] == "robots_disallowed" for row in rows),
        "provider_results_stored": False,
    }
    (output / "source_candidate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Newline-delimited original source URLs; default stdin")
    parser.add_argument("--url", action="append", default=[], help="Original source URL; repeatable")
    parser.add_argument("--output", type=Path, default=PRIVATE / "current_run")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    content = args.input.read_text() if args.input else ("" if args.url else sys.stdin.read())
    urls = list(args.url) + [
        line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")
    ]
    if not urls:
        raise SystemExit("No source URLs provided")
    print(json.dumps(ingest(urls, args.output, args.timeout, args.workers), indent=2))


if __name__ == "__main__":
    main()
