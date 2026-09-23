# US-SME Signal Graph

Provenance-aware supplier-discovery research, including a reconstructed U.S. semiconductor graph and an exploratory audit of LLM-based evidence screening.

## Current milestone

The current manuscript is **Auditing LLM-Based Evidence Screening for Manufacturing Supplier Discovery**, revision **v0.4**. It studies the outputs and logged workflow corrections of an exploratory model audit over 960 frozen queries and 6,164 constructed source–capability–state pairs. Repeated GPT-5.6-Sol passes produced model-applied page-support labels; the final counts are 1,148 yes, 3,799 no, and 1,217 unclear. These are observations of a model-review protocol, not human ground truth or counts of verified suppliers.

The three research questions concern output and exclusion distributions, sensitivity to adjudication and literal-quote rules, and concordance with a separate blinded GLM-5.3/max pass. The manuscript refocus and processing audits are retrospective. The added comparison does not establish model accuracy or a second complete workflow evaluation. Entity resolution and firm-size screening remain exploratory appendix material; no GNN was trained.

Start with the [v0.4 manuscript PDF](paper/search_visible_manufacturing_evidence_audit_v0_1.pdf), [generated LaTeX source](paper/search_visible_manufacturing_evidence_audit_v0_1.tex), [editable Markdown manuscript](paper/search_visible_manufacturing_evidence_audit_v0_1.md), and [v0.4 revision record](docs/manuscript_revision_v0_4.md). The existing manuscript filenames remain stable. Supporting records include the [v0.2 editorial revision](docs/manuscript_revision_v0_2.md), [corrected aggregate results](docs/full_census_results_v0_1.md), [model-review deviations](docs/model_review_deviations_v0_1.md), and [claim audit](docs/claim_evidence_review_v0_1.md).

The [row-free aggregate package](release/public/long-tail-evidence-audit-v0.1-exploratory) was published to the GitHub repository in commit `c036829`; all eight listed artifact hashes were verified against the remote files after publication. Its v0.1 path and data are unchanged by the manuscript revision. It contains no company rows, provider payloads, fetched page text, URLs, quotes, or model rationales. The closed row-level corpus cannot be independently reproduced from this package.

Edit the Markdown manuscript and rebuild the LaTeX and PDF with `make manuscript-pdf`. The build requires Python 3, Pandoc, Tectonic, and Poppler (`pdfinfo` and `pdftotext`); it does not require the closed research corpus. The layout is defined in `paper/manuscript_template.tex`. The [processing-sensitivity summary](paper/audit_processing_sensitivity_v0_2.json) records the three-stage correction table. Researchers with access to the closed corpus can regenerate it using `python3 scripts/audit_processing_sensitivity.py`; `--private-root` and `--output` allow alternate paths.

The [v0.3 routing audit](paper/adjudication_contracts_v0_3.json) adds the denominator for agreement overwrites: whole-record adjudication changed 321 of 2,145 agreed primary labels routed to C (14.97%). Regenerate it with `python3 scripts/audit_adjudication_contracts.py` where the closed corpus is available. All 1,148 final positives satisfy the limited component and state-field checks; this is internal output consistency, not factual accuracy.

The [v0.4 supporting output audit](docs/output_integrity_audit_v0_4.md) verifies all 16 stored decision fields and reports label/reason and quote-coverage diagnostics on the unchanged GPT output. Its [row-free summary](paper/output_integrity_v0_4.json) is archived separately from the GLM comparison and does not establish human validation.

The [GLM-5.3 max comparison](docs/glm_max_cross_review_results_v0_4.md) completed all 309 planned batch submissions. Of 6,164 planned records, 5,893 yielded valid paired judgments, one was schema-invalid, 50 were omitted, and 220 remained in excluded failed batches. Primary agreement is 77.53% (kappa 0.619), with 1,074 joint positives. The [row-free comparison](paper/glm_max_cross_review_v0_4.json) and [execution audit](paper/glm_max_execution_audit_v0_4.json) report all denominators, component matrices, diagnostics, max settings, retry history and fingerprints. The archived low-requested pass is excluded. Concordance is not accuracy; single-pass GLM also differs from the adjudicated GPT procedure. The [Gemini plan](docs/cross_model_review_plan_v0_1.md) remains prepared but unexecuted. See the [current completion status](docs/research_completion_status_v0_4.md) for the outstanding human annotation and entity-resolution audits. Model concordance and editorial critique do not supply human validation.

The manuscript is not publication-ready or submitted. The original 1,200 first human annotations, at least 300 independent double annotations, and 200-pair entity-resolution precision audit remain incomplete; narrowing the manuscript does not waive them. Repository publication is separate from manuscript submission or peer review.

## Earlier semiconductor milestone

**v0.2.0-rc1** added a preregistered Brave × You search-uplift pilot to the frozen **Baseline v0.1-SIA**. The release is a verified candidate set, not a claim of complete U.S. supplier coverage or a completed SME dataset.

This is not the lost original paper snapshot. The paper reported 664 mixed-type entities and 542 relations from 48 seeds, but did not release the underlying entity/relation files. Baseline v0.1-SIA is a clean reconstruction starting point whose scope and limitations are explicit.

## Quick start

    python3 scripts/build_baseline.py
    python3 scripts/validate_baseline.py

To rebuild from the frozen local source page without a network request:

    make rebuild-frozen

Outputs are written to data/processed/baseline_v0_1_sia/:

- companies.csv
- facilities.csv
- relations.csv
- source_pages.csv
- company_aliases.csv
- supplier_baseline.csv
- baseline_manifest.json
- source_snapshot.html.gz
- SHA256SUMS

## Search uplift

The preregistered experiment is documented in [docs/search_uplift_pilot.md](docs/search_uplift_pilot.md). Search-provider results are not part of the baseline. Brave and You enter only after the baseline is frozen.

The first release candidate produced the following measured results:

- 24 frozen queries × top 10 × 2 providers;
- 219 Brave URLs, 220 You URLs, and 265 in the union;
- 75 provider-blind high-signal rows reviewed;
- 34 strict suppliers and 30 net-new strict suppliers relative to the 50-company SIA supplier baseline;
- Brave found 27 of the 30, You found 22, and the union found all 30;
- 11 strict suppliers have non-authoritative evidence consistent with the applicable size threshold and remain `probable_sme`;
- 0 companies are labeled `confirmed_sme`.

The strict precision estimate is 45.3% (Wilson 95% CI 34.6%–56.6%). The preregistered precision, double-review, and entity-resolution gates are not yet satisfied, so the pilot does not authorize an unattended full-scale graph expansion. See [docs/pilot_results_v0_2_rc1.md](docs/pilot_results_v0_2_rc1.md).

Public release artifacts are under [release/public/v0.2.0-rc1](release/public/v0.2.0-rc1). They contain provider-neutral facts, URLs, and page hashes—not provider payloads, snippets, ranks, or fetched page text.

Independent researchers and institutions can use the structured reproduction, correction, and pilot-interest templates described in [docs/external_validation.md](docs/external_validation.md). An issue or introductory conversation is not counted as adoption.

## Guardrails

- No ByteDance internal data, code, customers, or confidential records.
- Search payloads are transient unless explicit provider storage rights are obtained.
- Every published fact must point to an independent original source page.
- Counts distinguish source records, facilities, companies, and graph edges.
- A company is not labeled SME without separate size evidence.
- Search discovery, supplier validity, U.S. presence, baseline novelty, and SME status are separate labels.
- No stars, users, pilots, adoption, or government endorsement are claimed unless independently documented.
