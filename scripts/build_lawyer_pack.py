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
import re
import shutil
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile


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


def inline_markup(value: str) -> str:
    value = html.escape(value.strip())
    value = __import__("re").sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = __import__("re").sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def markdown_to_html(value: str) -> str:
    """Render the controlled memo subset into Word-friendly HTML."""
    lines = value.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_kind = ""
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline_markup(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = ""

    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and index + 1 < len(lines):
            separator = lines[index + 1].strip()
            if separator.startswith("|") and set(separator.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")) == set():
                flush_paragraph(); close_list()
                headers = [inline_markup(cell) for cell in stripped.strip("|").split("|")]
                index += 2
                body = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    body.append([inline_markup(cell) for cell in lines[index].strip().strip("|").split("|")])
                    index += 1
                out.append("<table><thead><tr>" + "".join(f"<th>{cell}</th>" for cell in headers) + "</tr></thead><tbody>")
                for row in body:
                    out.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
                out.append("</tbody></table>")
                continue
        if not stripped:
            flush_paragraph(); close_list(); index += 1; continue
        if stripped == "---" or stripped == "<hr>":
            flush_paragraph(); close_list(); out.append("<hr>"); index += 1; continue
        if stripped.startswith("#"):
            flush_paragraph(); close_list()
            level = min(3, len(stripped) - len(stripped.lstrip("#")))
            out.append(f"<h{level}>{inline_markup(stripped[level:])}</h{level}>")
            index += 1; continue
        if stripped.startswith("- "):
            flush_paragraph()
            if list_kind != "ul": close_list(); out.append("<ul>"); list_kind = "ul"
            out.append(f"<li>{inline_markup(stripped[2:])}</li>")
            index += 1; continue
        numbered = __import__("re").match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            flush_paragraph()
            if list_kind != "ol": close_list(); out.append("<ol>"); list_kind = "ol"
            out.append(f"<li>{inline_markup(numbered.group(1))}</li>")
            index += 1; continue
        close_list(); paragraph.append(stripped); index += 1
    flush_paragraph(); close_list()
    return "\n".join(out)


def plain_markup(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value.strip())
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", value)


def word_paragraph(text: str = "", style: str = "", page_break_before: bool = False) -> str:
    properties = []
    if style:
        properties.append(f'<w:pStyle w:val="{style}"/>')
    if page_break_before:
        properties.append("<w:pageBreakBefore/>")
    ppr = f"<w:pPr>{''.join(properties)}</w:pPr>" if properties else ""
    value = html.escape(plain_markup(text))
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{value}</w:t></w:r></w:p>'


def word_table(headers: list[str], body: list[list[str]]) -> str:
    rows = [headers, *body]
    xml = [
        "<w:tbl><w:tblPr><w:tblStyle w:val=\"EvidenceTable\"/>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders><w:top w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/>"
        "<w:left w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/>"
        "<w:right w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:color=\"9CAEBE\"/></w:tblBorders></w:tblPr>"
    ]
    for row_index, row in enumerate(rows):
        xml.append("<w:tr>")
        for cell in row:
            shading = '<w:shd w:fill="DCE9F4"/>' if row_index == 0 else ""
            run_properties = "<w:rPr><w:b/></w:rPr>" if row_index == 0 else ""
            xml.append(
                f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/>{shading}</w:tcPr>'
                f'<w:p><w:r>{run_properties}<w:t>{html.escape(plain_markup(cell))}</w:t></w:r></w:p></w:tc>'
            )
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def markdown_to_word_xml(value: str) -> str:
    lines = value.splitlines()
    body: list[str] = []
    paragraph: list[str] = []
    title_seen = False
    index = 0

    def flush() -> None:
        if paragraph:
            body.append(word_paragraph(" ".join(paragraph)))
            paragraph.clear()

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("|") and stripped.endswith("|") and index + 1 < len(lines):
            separator = lines[index + 1].strip()
            if separator.startswith("|") and set(separator.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")) == set():
                flush()
                headers = [cell.strip() for cell in stripped.strip("|").split("|")]
                index += 2
                rows = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                    index += 1
                body.append(word_table(headers, rows))
                continue
        if not stripped:
            flush(); index += 1; continue
        if stripped == "---" or stripped == "<hr>":
            flush(); body.append(word_paragraph("")); index += 1; continue
        if stripped.startswith("#"):
            flush()
            level = min(3, len(stripped) - len(stripped.lstrip("#")))
            body.append(word_paragraph(stripped[level:].strip(), f"Heading{level}", level == 1 and title_seen))
            title_seen = title_seen or level == 1
            index += 1; continue
        if stripped.startswith("- "):
            flush(); body.append(word_paragraph("• " + stripped[2:], "ListBullet")); index += 1; continue
        numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if numbered:
            flush(); body.append(word_paragraph(f"{numbered.group(1)}. {numbered.group(2)}", "ListNumber")); index += 1; continue
        paragraph.append(stripped); index += 1
    flush()
    section = (
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1008" w:right="1008" w:bottom="1008" w:left="1008"/>'
        '</w:sectPr>'
    )
    return "".join(body) + section


def write_native_docx(markdown: str, path: Path) -> None:
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{markdown_to_word_xml(markdown)}</w:body></w:document>'
    )
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="140"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:color w:val="173A5E"/><w:sz w:val="40"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:color w:val="285F8F"/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:color w:val="285F8F"/><w:sz w:val="23"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="ListNumber"><w:name w:val="List Number"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:style>
<w:style w:type="table" w:styleId="EvidenceTable"><w:name w:val="Evidence Table"/><w:tblPr><w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
</w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    document_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)
        archive.writestr("word/_rels/document.xml.rels", document_rels)


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
    full_memo = "\n\n---\n\n".join(
        (out / name).read_text() for name in (
            "00_COUNSEL_EXECUTIVE_MEMO.md", "01_FILING_DATE_CONTINUITY_CROSSWALK.md",
            "02_AAO_EVIDENCE_DESIGN.md", "03_TECHNICAL_EVIDENCE_MEMO.md",
            "04_CLAIM_BOUNDARIES.md", "05_DRAFT_FACTUAL_STATEMENTS.md",
        )
    )
    html_text = """<!doctype html><html><head><meta charset="utf-8"><style>
@page{margin:0.7in}body{font-family:Arial,sans-serif;font-size:10.5pt;line-height:1.42;color:#18212b}h1{font-size:20pt;color:#173a5e;border-bottom:2px solid #173a5e;padding-bottom:7px;page-break-before:always}h1:first-child{page-break-before:auto}h2{font-size:14pt;color:#285f8f;margin-top:18px}h3{font-size:11.5pt;color:#285f8f}p{margin:7px 0}table{border-collapse:collapse;width:100%;font-size:8.5pt;margin:10px 0 15px}th,td{border:1px solid #9caebe;padding:5px;vertical-align:top}th{background:#dce9f4;color:#173a5e}code{background:#eef2f5;padding:1px 3px;font-family:Menlo,monospace;font-size:8.5pt}li{margin:3px 0}hr{border:0;border-top:1px solid #9caebe;margin:24px 0}</style></head><body>""" + markdown_to_html(full_memo) + "</body></html>"
    write(out / "COUNSEL_MEMO_SOURCE.html", html_text)
    write_native_docx(full_memo, out / "COUNSEL_MEMO.docx")

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
