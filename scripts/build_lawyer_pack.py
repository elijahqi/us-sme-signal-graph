#!/usr/bin/env python3
"""Build a private, counsel-reviewable evidence pack from frozen artifacts."""

from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments" / "search_uplift" / "private" / "formal_24q"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def table(rows: list[tuple[str, str]]) -> str:
    return "\n".join(f"| {left} | {right} |" for left, right in rows)


def build(args: argparse.Namespace) -> dict:
    out = args.output
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    verified = read_csv(args.verified)
    strict = [row for row in verified if row.get("is_valid_supplier_strict") == "True"]
    net_new = [row for row in strict if row.get("baseline_disposition") == "novel_candidate"]
    probable = [row for row in net_new if row.get("sme_status") == "probable_sme"]
    pilot = json.loads(args.pilot_metrics.read_text())
    provider = json.loads(args.provider_metrics.read_text())
    aao = json.loads(args.aao_failure_coding.read_text()) if args.aao_failure_coding else {}
    head_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE
    ).stdout.strip()
    baseline_commit = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.splitlines()[0]

    summary = f"""# Counsel executive memo: US-SME Signal Graph

Prepared {date.today().isoformat()} for attorney review. This is a technical evidence memorandum, not legal advice. Counsel must decide whether and how post-filing evidence may be used.

## Bottom line

The project now supplies a concrete, public, auditable continuation of the two workstreams described before filing: coverage-aware U.S. supplier discovery and heterogeneous-graph SME analysis. A frozen comparison baseline, preregistered dual-search experiment, provider-blind adjudication, independent source verification, public candidate release, and immutable Git history now exist.

Measured result: {pilot['net_new_strict_suppliers']} net-new strict U.S. semiconductor supplier candidates relative to the frozen 50-company SIA Equipment/Materials comparison baseline, a {pilot['strict_company_lift']:.0%} comparison-set lift. Brave contributed {provider['provider_arms_net_new_strict']['brave']} strict net-new candidates, You contributed {provider['provider_arms_net_new_strict']['you']}, and the union contributed {provider['provider_arms_net_new_strict']['union']}.

## Material limitations counsel should see first

- This is post-filing engineering evidence of continued work, not proof that eligibility first arose after filing.
- The public RC labels {len(probable)} companies `probable_sme` based on non-authoritative size evidence; it labels **0** `confirmed_sme`.
- No external user, institutional pilot, independent reproduction, recommendation letter, star count, citation, or adoption is claimed.
- Only 75 of 186 domain-level review rows received full Reviewer-1 adjudication; 111 lower-signal rows remain.
- Strict precision in the 75-row high-signal scope is {pilot['strict_precision']:.1%}, Wilson 95% CI {pilot['strict_precision_wilson_95'][0]:.1%}–{pilot['strict_precision_wilson_95'][1]:.1%}. The preregistered precision lower-bound gate was not met.
- A second independent annotator, agreement score, and entity-resolution audit remain incomplete.
- The SIA baseline is known incomplete and is not licensed for row-level redistribution.
- Search-provider payloads, ranks, and snippets are not in the public release.

## Evidence that exists now

| Evidence | Status |
|---|---|
| Pre-filing supplier-discovery workstream began December 2025 | In signed proposed endeavor statement |
| Pre-filing heterogeneous-graph workstream began January 2026 | In signed proposed endeavor statement |
| Related first-authored preprints | Identified in filing evidence |
| Reproducible baseline | 555 records, 239 companies, 50 supplier-denominator companies, 2,150 provenance relations |
| Frozen Brave × You protocol | 24 queries, top 10, same parameters |
| Formal retrieval | 219 Brave URLs, 220 You URLs, 265 union, 174 intersection |
| Provider-blind review | 75 high-signal domain rows |
| Independent-source verification | 34 strict suppliers, 30 net-new |
| Public release candidate | Provider-neutral facts, URLs, hashes, metrics, manifests |
| Confirmed external adoption | None yet |

## Safe proposed characterization

Subject to counsel review: this release documents continued execution of pre-existing plans to develop and disseminate graph-based methods for identifying overlooked U.S. SMEs and supplier relationships in sparse data. It should not be characterized as a replacement endeavor, a completed national deployment, an SBA-certified SME database, or proof of external adoption.
"""
    write(out / "00_COUNSEL_EXECUTIVE_MEMO.md", summary)

    continuity = f"""# Filing-date continuity crosswalk

| Pre-filing statement | Pre-filing anchor | Current continuation artifact | What it can show | What it cannot show |
|---|---|---|---|---|
| Coverage-aware web crawling for U.S. supplier and partner coverage; began December 2025 | Signed PES and supplier-discovery preprint | Frozen 24-query experiment, provider-neutral fetcher, 186-row blind pack, 30 net-new strict suppliers | Same technical object, measurable progress, reproducible dissemination | That post-filing work created filing-date eligibility |
| Heterogeneous GNN mapping investor, supply-chain, and market associations; initiated January 2026 | Signed PES and SME-HGT preprint | Provenance-aware graph schema, entity-resolution controls, SME status separation | Engineering implementation of the same graph-based program | Model performance uplift or completed SME-HGT reproduction |
| Identify overlooked high-value U.S. SMEs and supplier relationships | Petition formulation | Public verified-candidate table and evidence hashes | Concrete, cross-employer public deliverable | Authoritative SME certification or complete national coverage |
| Validated decision-support tools for investors, public agencies, and analysts | Petition formulation | Preregistered validation protocol, negative results, public RC | Serious validation design and progress | Actual users, institutional pilots, or adoption |

## Immutable technical anchors

- Baseline commit: `{baseline_commit}`.
- Current release-candidate commit: `{head_commit}`.
- Petition hash: `{args.petition_sha256}`.
- Proposed endeavor statement hash: `{args.pes_sha256}`.
- Evidence memo hash: `{args.evidence_memo_sha256}`.
- Public release manifest hash: `{sha256(args.public_release / 'release_manifest.json')}`.

Counsel should verify the actual I-140 filing date, receipt record, and which versions of the PES and preprints were submitted before relying on this crosswalk.
"""
    write(out / "01_FILING_DATE_CONTINUITY_CROSSWALK.md", continuity)

    counts = aao.get("counts", {})
    aao_memo = f"""# AAO-informed evidence design memo

The local review covered a rolling-year B5 repository snapshot and then isolated 463 texts explicitly referencing NIW or Matter of Dhanasar. This is an appeals/motions corpus and must not be presented as an approval-rate sample.

For 402 dismissed NIW decisions, conservative non-exclusive phrase coding found at least:

| Failure signal | Decisions | Project response | Remaining gap |
|---|---:|---|---|
| National importance not established | {counts.get('national_importance', 306)} | Concrete public supplier dataset, measured cross-company scope | No independent national-scale use yet |
| Weak letters | {counts.get('weak_letters', 177)} | Future letters can cite a release, rows, hashes, and actual use | No user letter exists yet |
| Well-positioned not established | {counts.get('well_positioned', 113)} | Immutable code, data methods, validation and release progress | External reproduction/adoption incomplete |
| On-balance prong failure | {counts.get('on_balance', 104)} | Open cross-employer dissemination can be documented | Counsel must connect facts to the legal balancing test |
| Unsupported broad impact | {counts.get('unsupported_broad_impact', 91)} | Claims are limited to measured candidate discovery and lift | Economic or policy outcome not measured |
| Field importance substituted for specific endeavor | {counts.get('field_not_specific_endeavor', 88)} | Deliverables, scope, query set, metrics, and failure gates are specific | Broader impact still needs users |
| Endeavor detail insufficient | {counts.get('insufficient_endeavor_detail', 76)} | Schemas, provenance, release boundaries, and validation workflow exist | Long-term graph/model phases remain future work |
| Post-filing or changed endeavor issue | {counts.get('post_filing_or_changed_endeavor', 43)} | Explicit PES-to-artifact continuity crosswalk | Counsel must decide admissible use in an RFE |

The AAO coding is research support, not legal precedent or a prediction of the petition outcome.
"""
    write(out / "02_AAO_EVIDENCE_DESIGN.md", aao_memo)

    tech = f"""# Technical evidence memo

## Frozen baseline

- 555 source/facility records; 239 exact-name companies.
- 50 Equipment/Materials companies form the supplier comparison denominator.
- 2,150 basic provenance relations.
- Raw SIA HTML and row-level derived tables remain private because an open-data license was not established.

## Formal discovery experiment

- 24 frozen capability queries, top 10, Brave and You under matched parameters.
- 219 Brave unique URLs; 220 You; 265 union; 174 intersection; Jaccard 65.66%.
- Provider responses were not stored in the project release.
- Original pages were independently fetched with robots checks and hashes.

## Adjudication and verification

- 186 domain rows after deduplication.
- 75 direct-company/high-signal rows received provider-blind Reviewer-1 adjudication.
- All 42 first-party lenient positives received an independent-source decision.
- Generic shells, security pages, foreign-only entities, distributors, associations, and baseline duplicates were explicitly rejected or separated.
- 34 strict suppliers; 30 net-new; 11 probable SMEs; 0 confirmed SMEs.

## Provider attribution

- Brave: 27 net-new strict suppliers.
- You: 22.
- Intersection: 19.
- Brave-only: 8.
- You-only: 3.
- Union: 30.

The union improved yield over either provider alone. You did not meet the preregistered five-unique-positive threshold.

## Scientific conclusion

The pilot supports the proposition that dual search can increase long-tail supplier recall when coupled to provider-neutral fetching, entity resolution, and independent verification. It rejects the proposition that search output can be ingested directly as a high-precision dataset.
"""
    write(out / "03_TECHNICAL_EVIDENCE_MEMO.md", tech)

    boundaries = """# Claim boundaries

## Supported now

- A public, reproducible, provenance-aware supplier-discovery release candidate exists.
- It is continuous with the filed supplier-discovery and graph workstreams.
- The formal union discovered 30 independently verified net-new supplier candidates against a frozen comparison baseline.
- Search union improved strict yield over either provider alone.
- The project reports failures, rights limits, and uncertainty.

## Do not claim yet

- Complete U.S. supplier or SME coverage.
- SBA certification or 11 confirmed SMEs.
- External adoption, government use, pilots, users, stars, citations, or recommendation support.
- National economic impact, jobs created, procurement savings, or policy outcomes.
- SME-HGT downstream model uplift.
- Independent annotation agreement.
- That post-filing work independently cured filing-date eligibility.

## Counsel decision required

- Whether current evidence is continuation evidence permissible in an RFE.
- Whether the public RC should be cited in a refile instead.
- Which facts belong under each Dhanasar prong.
- Whether an updated personal statement should preserve the current endeavor wording exactly.
"""
    write(out / "04_CLAIM_BOUNDARIES.md", boundaries)

    facts = f"""# Draft factual statements for counsel editing

These are technical fact formulations, not proposed legal argument.

1. The petitioner documented before filing that his coverage-aware U.S. supplier-discovery project began in December 2025 and that his heterogeneous-graph market-association project began in January 2026.
2. On July 29, 2026, the project produced a public release candidate implementing a frozen baseline, source-provenance schema, preregistered dual-search experiment, provider-blind review, independent-source verification, and release integrity manifests.
3. Under 24 frozen queries and matched top-10 retrieval budgets, Brave returned 219 unique canonical URLs and You returned 220; their union contained 265 and their intersection contained 174.
4. Within a provider-blind, high-signal review scope of 75 domain-level candidates, 34 satisfied the project's strict supplier criteria after independent-source verification. Thirty were absent from the frozen 50-company SIA Equipment/Materials comparison baseline.
5. Brave found 27 of the 30 net-new strict suppliers, You found 22, and the union found 30.
6. The release deliberately does not represent any candidate as an SBA-certified SME. Eleven have non-authoritative size evidence consistent with a possible applicable threshold and are marked probable; zero are marked confirmed.
7. The project publicly reports that its precision and double-review gates remain incomplete and does not claim external adoption.

Counsel should add filing and receipt dates only after checking the official record.
"""
    write(out / "05_DRAFT_FACTUAL_STATEMENTS.md", facts)

    candidate_fields = [
        "review_id", "canonical_company_name", "registrable_domain", "capability_groups",
        "sme_status", "size_evidence", "primary_evidence_url", "primary_page_sha256",
        "independent_confirmation_url", "independent_source_sha256", "verification_confidence",
    ]
    with (out / "06_STRICT_CANDIDATE_EVIDENCE_INDEX.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_fields)
        writer.writeheader(); writer.writerows({key: row.get(key, "") for key in candidate_fields} for row in net_new)
    with (out / "07_PROBABLE_SME_REVIEW_QUEUE.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_fields)
        writer.writeheader(); writer.writerows({key: row.get(key, "") for key in candidate_fields} for row in probable)

    exhibits = [
        ("A", "Signed proposed endeavor statement", args.pes_sha256, "Pre-filing continuity; source file retained outside this pack"),
        ("B", "Current petition letter", args.petition_sha256, "Current legal narrative; source file retained outside this pack"),
        ("C", "Evidence memo", args.evidence_memo_sha256, "Paper-to-prong mapping; source file retained outside this pack"),
        ("D1", "Baseline Git commit", baseline_commit, "Frozen baseline implementation anchor"),
        ("D2", "Release-candidate Git commit", head_commit, "Search-uplift and public RC implementation anchor"),
        ("E", "Public v0.2.0-rc1", sha256(args.public_release / "release_manifest.json"), "Public code/data evidence"),
        ("F", "AAO failure coding", sha256(args.aao_failure_coding) if args.aao_failure_coding else "", "Research aid; not a rate or legal authority"),
    ]
    with (out / "08_EXHIBIT_INDEX.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["exhibit", "artifact", "sha256_or_commit", "purpose"]); writer.writerows(exhibits)

    shutil.copytree(args.public_release, out / "public_release_v0.2.0-rc1")
    full_memo = "\n<hr>\n".join(
        (out / name).read_text() for name in (
            "00_COUNSEL_EXECUTIVE_MEMO.md", "01_FILING_DATE_CONTINUITY_CROSSWALK.md",
            "02_AAO_EVIDENCE_DESIGN.md", "03_TECHNICAL_EVIDENCE_MEMO.md",
            "04_CLAIM_BOUNDARIES.md", "05_DRAFT_FACTUAL_STATEMENTS.md",
        )
    )
    html_text = """<!doctype html><html><head><meta charset="utf-8"><style>
body{font-family:-apple-system,BlinkMacSystemFont,Arial,sans-serif;max-width:900px;margin:40px auto;line-height:1.45;color:#18212b}h1{color:#173a5e;border-bottom:2px solid #173a5e;padding-bottom:8px}h2{color:#285f8f}table{border-collapse:collapse;width:100%;font-size:12px}th,td{border:1px solid #aab7c4;padding:6px;vertical-align:top}th{background:#eaf1f7}code{background:#eef2f5;padding:1px 3px}li{margin:4px 0}</style></head><body>""" + "<pre style='white-space:pre-wrap;font-family:inherit'>" + html.escape(full_memo) + "</pre></body></html>"
    write(out / "COUNSEL_MEMO_SOURCE.html", html_text)
    textutil = shutil.which("textutil")
    if textutil:
        subprocess.run([textutil, "-convert", "docx", "-output", str(out / "COUNSEL_MEMO.docx"), str(out / "COUNSEL_MEMO_SOURCE.html")], check=True)

    files = sorted(path for path in out.rglob("*") if path.is_file() and path.name != "SHA256SUMS")
    write(out / "SHA256SUMS", "\n".join(f"{sha256(path)}  {path.relative_to(out)}" for path in files))
    return {
        "output": str(out), "net_new_strict_suppliers": len(net_new),
        "probable_smes": len(probable), "confirmed_smes": 0, "files": len(files) + 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified", type=Path, default=PRIVATE / "verification" / "verified_candidates.csv")
    parser.add_argument("--pilot-metrics", type=Path, default=PRIVATE / "metrics" / "pilot_metrics.json")
    parser.add_argument("--provider-metrics", type=Path, default=PRIVATE / "metrics" / "provider_attribution.json")
    parser.add_argument("--public-release", type=Path, default=ROOT / "release" / "public" / "v0.2.0-rc1")
    parser.add_argument("--aao-failure-coding", type=Path)
    parser.add_argument("--petition-sha256", required=True)
    parser.add_argument("--pes-sha256", required=True)
    parser.add_argument("--evidence-memo-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2))


if __name__ == "__main__":
    main()
