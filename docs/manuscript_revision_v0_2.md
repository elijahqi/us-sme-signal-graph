# Manuscript editorial revision v0.2

## Purpose and scope

The manuscript is retitled **Auditing LLM-Based Evidence Screening for Manufacturing Supplier Discovery**. The existing Markdown, TeX, and PDF paths under `paper/search_visible_manufacturing_evidence_audit_v0_1.*` remain stable; v0.2 identifies the manuscript's editorial revision, not a new corpus or public aggregate release.

The revision focuses the paper on a narrower contribution: an exploratory audit of the outputs and workflow failures of an LLM-based page-evidence screening protocol within a frozen manufacturing-query corpus. It uses the existing 960 queries, 6,164 source–capability–state pairs, same-model review passes, and logged corrections. It adds no GNN, retrieval run, independent annotation, or new performance experiment.

This is a **post hoc editorial refocus**, made after the results and deviations were known. It is not a new preregistration or a prospective test of hypotheses. Protocol v0.3, the v0.4 extension amendment, and the existing deviation records retain their original chronology and status.

## Research questions and presentation changes

The paper now centers on two questions:

1. What page-support label and exclusion distributions does the fixed model protocol produce over the constructed corpus?
2. How do adjudication and literal-quote rules affect those outputs, and which workflow consistency failures do the logged corrections expose?

The main text retains the query and acquisition design, the distinction between pages and constructed pairs, the five page-support components, and the final model-label and exclusion distributions. Logged workflow corrections become a central result. Retrieval overlap describes the corpus's construction. Detailed industry, state, and intent incidence, provisional entity clustering, and destination-page size screening become supporting or appendix analyses. The earlier probability-sample interval is not used for a confirmatory claim.

This structure concentrates the argument on observations supported by the current artifacts. It does not present the workflow corrections as a controlled ablation study or use them to claim a measured gain in semantic accuracy.

## Interpretation of the existing corrections

- **Fieldwise adjudication:** the earlier whole-record C merge changed A/B-agreed `no` labels to `unclear` in 283 extension rows and 38 calibration rows. Restoring the agreed fields changes 321 primary-label merge outcomes; 339 rows change in at least one of the ten key fields, including 18 with no primary-label change. No positive count changed in this correction. Agreement with A/B is not independent proof that the restored labels are correct.
- **Literal-quote requirement:** 71 initially positive rows lacked a normalized contiguous literal quote. Same-model re-audit relabeled 31 rows as `unclear`, reducing the provisional positive count from 1,179 to 1,148. These are label changes under a stricter review rule, not 31 independently confirmed false positives. All 1,148 retained positive quotes pass the normalized literal check; literal matching does not establish support for every component or factual truth.
- **Evidence-context circularity:** the invalid first firm-size pass included prior model rationales. It remains excluded from substantive size findings. The corrected analysis uses original destination-page text, and no invalid-pass numerical finding is reinstated.

The [model-review deviation log](model_review_deviations_v0_1.md) and [size-evidence deviation record](size_evidence_audit_deviation.md) remain the source records for these changes.

## Limits retained

The final 1,148 yes, 3,799 no, and 1,217 unclear decisions are model-applied labels for a finite, pipeline-constructed corpus. They are not a count of verified suppliers, a prevalence estimate for U.S. manufacturers, or a legal SME determination. `Unclear` reflects unresolved page evidence; it is not factual ineligibility.

A/B/C are separate passes of GPT-5.6-Sol. Their agreement describes repeat-evaluation stability under prompt and order variation, not human agreement or validated accuracy. Quote matching and internal-field checks cannot independently verify a page's meaning, truth, or current operational claims.

The 790 operating-entity and 785 corporate-group clusters remain provisional. The destination-page size screen remains limited to selected fetched excerpts and its term lexicon. Moving these analyses to an appendix does not validate them or remove their existing gates.

The row-level corpus remains closed. The public artifacts support inspection of the workflow and aggregate-byte integrity, not record-by-record reproduction of the original labels. The manuscript makes no GNN-performance, W→K→W-validation, national recall, or first-of-kind supplier-discovery claim.

## Validation and submission status

The scope change does **not** waive, replace, or mark complete the existing [manuscript stop rules](claim_evidence_review_v0_1.md). The next substantive work is:

1. Complete at least 300 provider-blind cases with independent human double annotation, report component and overall agreement, and evaluate the existing κ≥0.70 gate. Report model-versus-human errors separately from human inter-annotator agreement; a positive-only audit cannot measure missed positives.
2. Execute the preregistered 200-pair entity-resolution precision audit and evaluate the existing ≥0.95 gate. Entity and size appendix claims retain this dependency.
3. After those audits, revise the claims to match the observed results, synchronize tables and hashes, and adapt the manuscript to an appropriate venue after checking its current scope, format, bibliography, and AI-use policy. A failed gate must be reported and addressed; completion of annotation does not itself mean the threshold was met or that publication is assured.

No human or entity-resolution validation is completed by this editorial revision. No submission, acceptance, or peer review is implied. The manuscript remains an exploratory draft and is not publication-ready.

## Public artifact status

The existing row-free package at `release/public/long-tail-evidence-audit-v0.1-exploratory` was published to the GitHub repository in commit `c036829`. All eight listed artifact hashes were verified against the remote files after publication. Its data, version, and path remain unchanged in this revision. This satisfies the aggregate-publication check for that package; it does not satisfy the human-validation or entity-resolution gates and does not constitute manuscript submission.

## Revision artifacts and local verification

The canonical Markdown now generates the tracked LaTeX through `scripts/prepare_manuscript_source.py` and `paper/manuscript_template.tex`; `make manuscript-pdf` builds and checks the PDF. This avoids maintaining divergent manuscript text in two source formats. Python 3, Pandoc, Tectonic, and Poppler are required to rebuild the manuscript, but the closed corpus is not.

The companion `paper/audit_processing_sensitivity_v0_2.json` is an additional row-free reconstruction summary, separate from the unchanged v0.1 release package. `scripts/audit_processing_sensitivity.py` rebuilds the three processing stages from retained A/B/C outputs, recomputes the 71 literal-quote failures, and verifies all 6,164 final rows across ten key fields. It can only be rerun where the closed corpus is available. The public summary contains counts and input fingerprints, not identifiers or source text; it does not resolve the record-level reproducibility limitation.

Seven focused prior-work references were checked against publisher, author-institution, or official proceedings/arXiv records. The W-K-W citation explicitly uses arXiv v4; differing v1 and v4 crawl budgets and graph counts are version changes, not evidence that this corpus reproduces that graph. Target-venue literature review, author review, and AI-use checks remain outstanding.
