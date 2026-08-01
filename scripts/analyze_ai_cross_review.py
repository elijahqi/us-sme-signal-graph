#!/usr/bin/env python3
"""Merge A/B/C review traces and produce the first complete AI cross-review results."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys
import unicodedata
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from positive_quote_reaudit_utils import final_decisions as load_quote_reaudit, FINAL_FIELDS as QUOTE_FINAL_FIELDS


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "long_tail_benchmark" / "private" / "formal_v0_3"
AI = BASE / "ai_review_v0_1"
KEY_FIELDS = ("identity_status", "direct_producer_status", "capability_match", "production_presence", "commercial_offering", "eqdp", "primary_exclusion_reason", "scale_band", "legal_form", "web_visibility")
FINAL_FIELDS = ("candidate_business_name",) + KEY_FIELDS + ("production_city", "production_state", "confidence", "evidence_quote", "rationale")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json_results(directory: Path, expected: int | None = None) -> dict[str, dict]:
    rows = {}
    for path in sorted(directory.glob("batch-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["results"]:
            if row["review_id"] in rows:
                raise ValueError(f"duplicate review ID: {row['review_id']}")
            rows[row["review_id"]] = row
    if expected is not None and len(rows) != expected:
        raise ValueError(f"{directory} has {len(rows)} results, expected {expected}")
    return rows


def cohen_kappa(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("invalid kappa inputs")
    observed = sum(left == right for left, right in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    categories = set(ca) | set(cb)
    expected = sum((ca[key] / len(a)) * (cb[key] / len(b)) for key in categories)
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def weighted_rate(rows: list[dict], predicate) -> float:
    weights = [1 / float(row["inclusion_probability"]) for row in rows]
    return sum(weight for row, weight in zip(rows, weights) if predicate(row)) / sum(weights)


def stratified_bootstrap_ci(rows: list[dict], predicate, replicates: int = 10000) -> list[float]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["sampling_stratum"]].append(row)
    rng = random.Random(20260730)
    estimates = []
    for _ in range(replicates):
        sample = []
        for group in groups.values():
            sample.extend(rng.choice(group) for _ in range(len(group)))
        estimates.append(weighted_rate(sample, predicate))
    estimates.sort()
    return [estimates[math.floor(0.025 * (replicates - 1))], estimates[math.floor(0.975 * (replicates - 1))]]


def count_manifest_retries(path: Path) -> tuple[int, int]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return len(rows), sum(int(row.get("attempt", 1)) > 1 for row in rows)


def normalize_quote(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    value = value.strip("\u201c\u201d\"\u2018\u2019'")
    value = value.replace("…", "...").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).casefold().strip()


def fieldwise_adjudication(left: dict, right: dict, adjudicator: dict) -> tuple[dict, list[str]]:
    """Lock A/B-agreed key fields and use C only for disputed key fields."""
    disputed = [field for field in KEY_FIELDS if left[field] != right[field]]
    decision = dict(adjudicator if disputed else left)
    for field in KEY_FIELDS:
        decision[field] = left[field] if left[field] == right[field] else adjudicator[field]
    return decision, disputed


def analyze() -> tuple[list[dict], dict]:
    sample = {row["review_id"]: row for row in read_csv(BASE / "review_sample_v0_1.csv")}
    states = {row["state_id"]: row for row in read_csv(ROOT / "experiments" / "long_tail_benchmark" / "geographies_v0_1.csv")}
    a = load_json_results(AI / "reviewer_a", 1200)
    b = load_json_results(AI / "reviewer_b", 1200)
    c = load_json_results(AI / "adjudication" / "reviewer_c", 631)
    evidence = {}
    for path in sorted((AI / "batches").glob("batch-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]:
            evidence[row["review_id"]] = row
    if set(sample) != set(a) or set(a) != set(b):
        raise ValueError("sample/A/B ID coverage mismatch")
    disagreements = {review_id for review_id in a if any(a[review_id][field] != b[review_id][field] for field in KEY_FIELDS)}
    if disagreements != set(c):
        raise ValueError(f"C coverage mismatch: expected {len(disagreements)}, got {len(c)}")

    final_rows = []
    quote_reaudit = load_quote_reaudit(BASE / "ai_census_v0_4" / "positive_quote_reaudit_v0_1")
    for review_id in sorted(sample):
        decision, disputed = fieldwise_adjudication(
            a[review_id], b[review_id], c.get(review_id, a[review_id])
        )
        if decision["eqdp"] == "yes" and not (
            decision["identity_status"] == "yes"
            and decision["direct_producer_status"] == "yes"
            and decision["capability_match"] == "yes"
            and decision["production_presence"] in {
                "industrial_facility_confirmed", "job_shop_or_workshop_confirmed",
                "owner_or_home_production_confirmed",
            }
            and decision["commercial_offering"] == "yes"
            and decision["primary_exclusion_reason"] == "none"
        ):
            raise ValueError(f"fieldwise adjudication produced inconsistent positive: {review_id}")
        row = {**sample[review_id], **{field: decision[field] for field in FINAL_FIELDS}}
        row["final_source"] = "fieldwise_C_adjudication" if disputed else "AB_agreement"
        row["adjudicated_fields"] = "|".join(disputed)
        row["a_eqdp"] = a[review_id]["eqdp"]
        row["b_eqdp"] = b[review_id]["eqdp"]
        quote = normalize_quote(row["evidence_quote"])
        excerpt = normalize_quote(evidence[review_id]["evidence_excerpt"])
        row["quote_audit_pass"] = str(bool(quote) and quote in excerpt).lower()
        if review_id in quote_reaudit:
            corrected=quote_reaudit[review_id]
            for field in QUOTE_FINAL_FIELDS:row[field]=corrected[field]
            row["final_source"] = "literal_quote_reaudit"
            row["adjudicated_fields"] = corrected["adjudicated_fields"]
            quote=normalize_quote(row["evidence_quote"]);row["quote_audit_pass"]=str(bool(quote) and quote in excerpt).lower()
        final_rows.append(row)

    field_agreement = {}
    for field in KEY_FIELDS:
        left = [a[review_id][field] for review_id in sorted(a)]
        right = [b[review_id][field] for review_id in sorted(a)]
        field_agreement[field] = {
            "agree": sum(x == y for x, y in zip(left, right)),
            "raw_agreement": sum(x == y for x, y in zip(left, right)) / len(left),
            "cohen_kappa": cohen_kappa(left, right),
        }

    eqdp_counts = Counter(row["eqdp"] for row in final_rows)
    yes_ci = stratified_bootstrap_ci(final_rows, lambda row: row["eqdp"] == "yes")
    dimension_tables = {}
    for dimension in ("industry_family", "sampling_stratum"):
        table = {}
        for value in sorted({row[dimension] for row in final_rows}):
            subset = [row for row in final_rows if row[dimension] == value]
            table[value] = {
                "sample_rows": len(subset),
                "yes": sum(row["eqdp"] == "yes" for row in subset),
                "no": sum(row["eqdp"] == "no" for row in subset),
                "unclear": sum(row["eqdp"] == "unclear" for row in subset),
                "weighted_yes_rate": weighted_rate(subset, lambda row: row["eqdp"] == "yes"),
            }
        dimension_tables[dimension] = table

    positive = [row for row in final_rows if row["eqdp"] == "yes"]
    state_mismatches = []
    for row in positive:
        expected = states[row["state_id"]]
        actual = row["production_state"].casefold().strip().replace(".", "")
        accepted = {expected["state_name"].casefold(), expected["state_abbr"].casefold()}
        if actual not in accepted:
            state_mismatches.append(row["review_id"])
    if state_mismatches:
        raise ValueError(f"positive production-state mismatch: {state_mismatches}")
    a_batches, a_retries = count_manifest_retries(AI / "reviewer_a_manifest_001_120.json")
    b_batches, b_retries = count_manifest_retries(AI / "reviewer_b_manifest_001_120.json")
    c_batches, c_retries = count_manifest_retries(AI / "adjudication" / "reviewer_c_manifest.json")
    summary = {
        "label_unit_warning": (
            "The legacy eqdp field is a model-applied five-component page-support label, "
            "not factual verification, procurement qualification, or legal status. "
            "Production-presence enum names ending in _confirmed mean page-supported "
            "under the model protocol."
        ),
        "method": {
            "model": "GPT-5.6-Sol",
            "reviewer_a_rows": 1200,
            "reviewer_b_rows": 1200,
            "key_field_disagreements_adjudicated": len(disagreements),
            "separate_same_model_passes": True,
            "independent_models": False,
            "human_expert_validation": False,
            "a_batches": a_batches, "a_retry_batches": a_retries,
            "b_batches": b_batches, "b_retry_batches": b_retries,
            "c_batches": c_batches, "c_retry_batches": c_retries,
        },
        "ab_field_agreement": field_agreement,
        "eqdp": {
            "unweighted_counts": dict(eqdp_counts),
            "weighted_yes_rate": weighted_rate(final_rows, lambda row: row["eqdp"] == "yes"),
            "weighted_yes_rate_bootstrap_95": yes_ci,
            "unique_positive_source_pages": len({row["candidate_id"] for row in positive}),
            "unique_positive_domains": len({row["registrable_domain"] for row in positive}),
            "positive_quote_audit_pass": sum(row["quote_audit_pass"] == "true" for row in positive),
            "positive_quote_audit_fail": sum(row["quote_audit_pass"] != "true" for row in positive),
            "positive_production_state_mismatches": len(state_mismatches),
        },
        "positive_scale_band": dict(Counter(row["scale_band"] for row in positive)),
        "positive_legal_form": dict(Counter(row["legal_form"] for row in positive)),
        "positive_production_presence": dict(Counter(row["production_presence"] for row in positive)),
        "all_exclusion_reasons": dict(Counter(row["primary_exclusion_reason"] for row in final_rows if row["eqdp"] != "yes")),
        "dimensions": dimension_tables,
    }
    return final_rows, summary


def main() -> None:
    rows, summary = analyze()
    output = AI / "final_cross_review_v0_1.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary["final_table_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    (AI / "cross_review_summary_v0_1.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__": main()
