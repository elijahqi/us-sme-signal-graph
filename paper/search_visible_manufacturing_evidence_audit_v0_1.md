# Auditing LLM-Based Evidence Screening for Manufacturing Supplier Discovery

**Author:** Yijiashun Qi

**ORCID:** https://orcid.org/0009-0009-2129-6932

**Version:** Exploratory Working Paper v0.4

**Status:** A retrospective audit of model outputs on a frozen corpus. Independent human validation and the preregistered entity-resolution audit remain incomplete. This revision is not a validated benchmark or a publication-ready study.

## Abstract

LLM-assisted supplier discovery requires evidence that retrieved pages support specific business claims. We retrospectively audit a screening workflow on a frozen corpus from 960 U.S. manufacturing queries, comprising 3,383 HTTP-2xx pages and 6,164 source-capability-state pairs. Two passes of the same model assessed five producer-support conditions; disputed fields received a third pass. Final labels were 1,148 positive (18.62%), 3,799 no, and 1,217 unclear. Whole-record adjudication overwrote 321 of 2,145 agreed primary labels routed for other disputes (14.97%); fieldwise merging preserved those agreements. Among 1,179 pre-re-audit positives, 71 failed a normalized literal-quote check; targeted re-review changed 31 to unclear. A separate output audit found 795 no labels paired with evidence-gap reasons. A blinded GLM-5.3 max-effort pass submitted the full corpus and yielded 5,893 schema-valid paired judgments, with 77.53% primary-label agreement and nominal Cohen's kappa of 0.619 against the final GPT procedure. One invalid row, 50 omissions, and 220 failed-batch records remained excluded. These findings measure processing sensitivity and model concordance, not factual accuracy; the comparison also differs in review procedure. Public code and aggregate artifacts document the evidence boundary, corrections, and execution failures. Independent human validation remains necessary before benchmark use.

**Keywords:** LLM evaluation; supplier discovery; evidence screening; adjudication; web-corpus audit; provenance

## 1. Introduction

A manufacturing search may retrieve a company name, a capability description, and a state name without establishing that the company produces that capability in that state. A distributor can describe a product it does not make; an office address can be mistaken for a production site. An LLM can turn these partial observations into an apparently coherent assessment. Evaluating the assessment therefore requires an explicit unit of analysis and a record of how evidence and decisions were processed.

This paper studies an implemented LLM evidence-screening workflow. Its observational unit is one frozen source excerpt paired with a requested manufacturing capability and state. The outcome is the model's assessment of page support under a five-component rubric. It is not an externally verified statement about a business. We ask:

- **RQ1:** How are the constructed pairs labeled, and which evidence gaps dominate the nonpositive outputs?
- **RQ2:** How do fieldwise adjudication and literal-quote re-audit change those outputs on the same frozen corpus?
- **RQ3:** How concordant is a separate blinded GLM-5.3 pass with the final GPT procedure, and what fraction of the corpus supports that comparison?

We contribute a documented corpus construction and support rubric, a reconstruction of consequential processing corrections, and an account of what those corrections do and do not validate. The revisions were prompted by failures found during the study. They are retrospective process checks, not a preregistered comparison or a controlled accuracy experiment. The manuscript was refocused after results were known; subsequent revisions audit routing, label/reason alignment, and quotation coverage using unchanged stored decisions. The original protocols, deviations, and validation requirements remain part of the record.

## 2. Related Work

Manufacturing-service discovery already uses knowledge graphs, capability inference, and language models. Li, Liu, and Starly study GNN-based manufacturing capability prediction [1]; Li, Ko, and Ameri integrate graph retrieval with LLM supplier discovery [2]. Qi et al. describe a Web-Knowledge-Web pipeline in which an evolving graph guides subsequent acquisition [3]. The present study evaluates neither a GNN nor a graph-guided discovery policy. It examines the evidence-screening step that could support a later evaluation of such systems.

Search-engine overlap has been studied across thousands of queries [4]. Here it describes the collection boundary, rather than serving as a claim of retrieval quality. Buckley and Voorhees examine evaluation under incomplete relevance judgments [5]; our finite constructed corpus likewise cannot establish relevance outside the observed candidates. Dodge et al. show the importance of documenting web-corpus collection and filtering [6]. Our fetch ledger, excerpt construction, and deviation record expose related choices at a smaller, domain-specific scale.

Zheng et al. evaluate LLM judges against human preferences and document judge biases [7]. Repeated agreement from one model, reported here in Section 4.1, is distinct from external validity. Our contribution is not a new general theory of LLM judging or supplier discovery. It is an empirical audit of how quotation constraints and adjudication logic affected one implemented screening workflow.

## 3. Corpus and Screening Protocol

### 3.1 Frozen retrieval and acquisition

On July 30, 2026 (UTC), 40 capabilities from ten manufacturing families were crossed with eight states and three query intents, yielding 960 frozen queries. The intents were direct manufacturer wording, small-batch/job-shop wording, and mixed ownership/locality wording. The last category includes family-owned and local-workshop expressions and is not a firm-size label. The exact lattice, capability definitions, and state list are public.

Each query requested ten web results from Brave and You Search. Brave returned 9,590 ranked rows, with one failed query after the frozen retry policy; You returned 9,600. Transient processing produced 11,715 query-URL union links and 4,638 unique destination URLs. Provider payloads, titles, snippets, and ranks were not retained as the research dataset. The same robots and HTTP workflow was applied to union URLs, and independently fetched publisher-page material was retained in a closed corpus where permitted.

Of the 4,638 URLs, 3,383 returned HTTP 2xx and entered pair construction: 3,190 status-200 and 193 status-202 responses. The remaining URLs comprised 1,018 status-403 responses, 73 other non-2xx HTTP responses, and 164 records with no HTTP status. Separately, 129 robots-disallowed and nine hard-timeout flags were recorded; these flags are not additional disjoint URL categories. A 2xx response does not guarantee usable substantive text, first-party provenance, or factual corroboration. Access failures and response content shape the observation boundary. Retrieval overlap and descriptive subgroup counts appear in Appendix A.

### 3.2 Observation unit and evidence boundary

The pipeline inherited capability and state from each retrieving query and deduplicated on `(source ID, capability, state)`. Observed intent tags were aggregated. This produced 6,164 pairs from the 3,383 accessible pages. A page may appear in multiple pairs with different requested capabilities or states. Pairs must not be treated as independent companies, and one page need not receive the same label for every task.

Visible text was extracted from the frozen page body. Task keywords and business-context terms selected windows, which were merged and concatenated with omission markers. The extractor budgeted 9,000 source-text characters; separator characters were additional. The reviewer also received the task definition and source-page metadata. It could assign at most one focal business to each pair. Tools and browsing were disabled during review. The target is support in this bounded input, rather than support somewhere on the website or across all pages about the company.

### 3.3 Five-component support rubric

The retained schema field `eqdp` records whether the excerpt supports all five conditions:

1. A specific operating commercial business is identified.
2. The business directly produces, fabricates, assembles, processes, rebuilds, remanufactures, or performs contract manufacturing.
3. The offering explicitly matches the requested capability.
4. Eligible production presence is supported in the queried state.
5. The offering is current and commercial.

Eligible presence includes an industrial facility or job shop and, where supported, owner/home production. An office, warehouse, service area, registered address, planned plant, or U.S. sales presence with foreign-only production is insufficient. The original prompts direct empty, broken, or insufficient excerpts toward unclear, but do not exhaustively define the no/unclear boundary for mixed evidence. We retain the recorded outcomes and examine that boundary in Section 4.2. A no or unclear label does not establish that a business lacks the capability; the supplied excerpt may simply fail the evidence test. Literal wording also cannot establish the truth or currentness of the page's claim.

### 3.4 Repeated review and fieldwise adjudication

A 1,200-pair probability sample was reviewed first. Protocol v0.4 prospectively governed the remaining 4,964 pairs after retrieval and calibration; it was not a pre-retrieval preregistration. The calibration decisions were reused in the full-corpus analysis. Appendix C preserves the sampling and resampling deviations.

Reviewers A and B were separate GPT-5.6-Sol passes with different stance/order prompts. Provider identity, rank, and prior reviewer decisions were hidden from their review prompts. A disagreement on any of ten key fields triggered a third same-model pass, C: the primary label, four yes/no/unclear components, production-presence category, exclusion reason, scale band, legal form, or web visibility. C reviewed 631 calibration and 2,661 extension pairs. Execution failures were retried or requeued rather than assigned unclear labels. These passes were not independent models or human reviewers.

The initial merger selected C's whole record when any key field was disputed. This allowed C to overwrite other fields on which A and B agreed. For pair $i$ and key field $f$, the corrected rule is

$$
M_{if} = \begin{cases} A_{if}, & A_{if}=B_{if}, \\ C_{if}, & A_{if}\ne B_{if}. \end{cases}
$$

Every pair with a disputed key field must have a C record; the reconstruction confirmed exact C coverage of all 3,292 original disputed pairs, with no missing or extra records. This rule preserves agreed fields but can combine decisions from different passes into a hybrid record. We therefore distinguish agreement preservation from consistency across output fields. Neither establishes factual correctness. The merger is implemented in `analyze_ai_cross_review.py` and `analyze_full_census.py`; `audit_processing_sensitivity.py` reconstructs both merge rules from retained outputs.

### 3.5 Literal-quote re-audit and analysis

Among 1,179 pre-re-audit positives, a deterministic check identified 71 supplied quotes that failed normalized contiguous-substring matching against the frozen excerpt. The flagged quotes included compressed, concatenated, or paraphrased text. These rows received A/B re-audit from the same evidence with a mandatory contiguous literal quote for a positive decision. Semantic disagreements received fieldwise C adjudication. The string check applies Unicode NFKC normalization, boundary-quote stripping, selected punctuation normalization, whitespace collapse, and case folding. Matching verifies occurrence under these transformations, not exact byte identity, semantic entailment, or fidelity to the complete original page.

We report exact label counts for the constructed corpus and reconstruct the processing stages from stored decisions. The fieldwise merge comparison reuses the same A/B/C outputs; the quote stage includes new reviews of the flagged subset. Their differences cannot be interpreted as randomized treatment effects. A further deterministic audit counts primary-label agreement among C-routed pairs and checks whether final positives have four affirmative components, an eligible production-presence category, no exclusion reason, and a production-state field matching the query after abbreviation normalization. These are limited output checks, not a semantic review of the source. We report neither factual precision nor recall, and no confidence interval is used to generalize these finite-corpus counts to U.S. manufacturers.

The v0.4 output audit compares all 16 decision fields, including quotes and rationales, between reconstructed decisions and the final table. It also cross-tabulates recorded labels and primary reasons and applies the same quote-occurrence check to every final row. Nonpositive quote outcomes are descriptive: they do not trigger new review, exclusion, or relabeling.

### 3.6 Separate blinded cross-model review

A separate GLM-5.3 pass was specified after the original corpus had been analyzed. It submits the same 6,164 frozen pairs in a fixed permutation (seed 20260919), in 308 batches of 20 and a final batch of four. Inputs whitelist the original excerpts and task/source metadata; GPT decisions, rationales, adjudications, provider identity, and search ranks are withheld. Fresh sessions disable tools, browsing, and conversation persistence. The comparison concerns the five support conditions, the primary label, and evidence fields; it does not repeat the entity or size analysis.

The user requested a new full pass with max reasoning effort. The request body sets the model to `glm-5.3` and the `effort` field of `output_config` to `max`; the earlier low-requested partial pass is retained separately and excluded. The project runs one client at a time, with at least one second after each response or error, including continuations. A supervisor permits at most two additional attempts for eligible transient transport failures, with minimum backoffs of 30 and 60 seconds or a longer server-requested interval. Client and relay retries are disabled. Retry decisions never depend on a label or agreement with GPT.

Complete responses with unique requested IDs retain schema-valid records unchanged, quarantine invalid records, and count omissions explicitly. These rules originated in disclosed processing amendments to the earlier pass and were retained for the max pass. Subsequent identity and exhausted-transport failures required separate retrospective continuation amendments. Diagnosed batch failures retain all raw attempts and contribute no accepted labels or replacement calls; only unattempted batches continue. Original and amendment fingerprints remain distinct. Planned submissions, returned records, valid judgments, invalid rows, omissions, failed batches, and unattempted records therefore require separate denominators.

The planned comparison pairs valid GLM records with the final adjudicated and quote-re-audited GPT output, reporting the three-class confusion matrix, raw agreement, nominal Cohen's kappa, component agreement, and jointly positive records. It compares a single pass with a repeated-pass procedure, so differences mix model, prompt, batch context, and review history. It is neither a controlled model-effect estimate nor a second complete retrieval-and-screening workflow evaluation. Agreement and joint positives do not establish accuracy. Section 4.4 reports the completed submission pass and its incomplete valid coverage; Appendix D reports class coverage and component concordance.

## 4. Results

### 4.1 Final labels and repeat-evaluation stability

The final workflow retained **1,148 positive page-support labels**, corresponding to 18.62% of constructed pairs (Table 1). Positive pairs referenced 1,072 destination pages and 796 registrable domains. All retained positive quotes passed the normalized literal-substring check. The component and state-field checks defined in Section 3.5 found zero violations among those 1,148 positives. These checks establish agreement between recorded fields, not that a quoted passage supports production of the requested capability in the queried state. The counts remain model outputs, not verified suppliers.

Reconstruction matched all 16 decision fields for all 6,164 final rows. Among nonpositives, 3,549 of 3,799 no rows and 959 of 1,217 unclear rows had a nonempty matching quote. The remaining no rows had 124 empty and 126 nonmatching quotes; unclear rows had 221 empty and 37 nonmatching quotes. Thus 508 of 5,016 nonpositive rows lacked a nonempty normalized match. This limits textual traceability and is not a count of semantic labeling errors; an unavailable or uninformative excerpt can legitimately lack a supporting quotation.

| Final pair label | Count | Share |
|---|---:|---:|
| Page-support yes | 1,148 | 18.62% |
| No | 3,799 | 61.63% |
| Unclear | 1,217 | 19.74% |
| Total | 6,164 | 100% |

Table: Final labels on the complete constructed corpus. The denominator is pairs, not businesses.

On the original 4,964-pair extension reviews, before targeted quote re-audit, A/B agreed on `eqdp` for 4,050 pairs (81.59%; nominal Cohen's kappa = 0.609). This measures repeat-evaluation stability under prompt/order variation, not agreement with human experts. The 1,200-pair calibration and extension are kept separate for this stability statistic because they were executed in different stages.

### 4.2 Evidence gaps in nonpositive outputs

Among the 5,016 nonpositive pairs, insufficient evidence and wrong-state or missing state-production proof accounted for 2,814 primary reasons (56.10%; Table 2). This is a distribution of model-assigned reasons. It does not determine whether the corresponding firms actually lack production capacity or whether supplemental pages could resolve the gap.

| Primary exclusion reason | No | Unclear | Total |
|---|---:|---:|---:|
| Insufficient evidence | 704 | 1,008 | 1,712 |
| Wrong state / missing state-production proof | 1,102 | 0 | 1,102 |
| Capability mismatch | 566 | 2 | 568 |
| Distributor, reseller, or broker | 463 | 0 | 463 |
| Nonmanufacturing service | 324 | 0 | 324 |
| Source unavailable within excerpt | 91 | 199 | 290 |
| Foreign-only production | 203 | 0 | 203 |
| Generic sector claim | 129 | 4 | 133 |
| Other recorded reasons | 217 | 4 | 221 |
| Total | 3,799 | 1,217 | 5,016 |

Table: Primary model-assigned reasons cross-tabulated by recorded label. Other reasons group the remaining categories. The total row partitions all 5,016 nonpositive pairs.

Evidence-gap reasons occur under both nonpositive labels: 704 no rows cite insufficient evidence and 91 cite source unavailability, totaling 795 of 3,799 no labels (20.93%). Given the prompt's direction toward unclear for insufficient excerpts, this co-occurrence identifies a priority for semantic review. It does not prove that 795 labels are wrong: primary-reason text, other components, and mixed evidence require joint inspection. We do not recode these rows retrospectively or treat the no/unclear split as a validated distinction between absence and uncertainty.

### 4.3 Sensitivity to processing rules

Table 3 reconstructs the label trajectory. Whole-record C selection produced 321 unclear labels in fields where A and B had agreed on no: 38 in calibration and 283 in the extension. Fieldwise merging restored those no labels and left the positive count unchanged. These are changes to the primary `eqdp` field. Across all ten adjudicated key fields, 339 rows changed, including 18 with no change to the primary label.

| Processing stage | Yes | No | Unclear |
|---|---:|---:|---:|
| Whole-record C merge, before quote re-audit | 1,179 | 3,478 | 1,507 |
| Fieldwise merge, before quote re-audit | 1,179 | 3,799 | 1,186 |
| Fieldwise merge and literal-quote re-audit | 1,148 | 3,799 | 1,217 |

Table: Retrospectively reconstructed processing stages, each totaling 6,164 pairs. The first transition changes merge logic on stored reviews; the second includes re-review of 71 flagged positives. This is not an accuracy comparison.

The routing audit identifies the denominator exposed to unintended primary-label replacement (Table 4). Of 3,292 pairs sent to C, 1,147 had a primary-label disagreement; the remaining 2,145 agreed on the primary label but disagreed elsewhere. Whole-record selection changed 321 of those 2,145 agreed labels (14.97%), all from no to unclear. Other-field disputes justified adjudication; the failure was allowing their resolution to replace an agreed primary field. The corrected merger preserves all 2,145 primary agreements by construction.

| Review stage | All C-routed pairs | Primary agreed | Primary overwritten | Overwritten / agreed |
|---|---:|---:|---:|---:|
| Calibration | 631 | 398 | 38 | 9.55% |
| Extension | 2,661 | 1,747 | 283 | 16.20% |
| Combined | 3,292 | 2,145 | 321 | 14.97% |

Table: Primary agreement means A and B agreed on the primary label before C review. The last column conditions on primary-agreed C-routed pairs. Stages differ in execution history; their rates are descriptive, not a controlled comparison.

Of those 71 flagged positives, 40 remained yes with acceptable literal quotations and 31 became unclear. The positive count fell from 1,179 to 1,148. It would be incorrect to describe all 71 as false positives or to treat the 31 downgraded cases as independently established errors. The evidence supports a narrower result: enforcing the revised quote requirement, together with re-review, changed both the retained quotations and some labels.

A separate size-screen failure reinforced the need to distinguish source material from earlier model output: an initial pass included prior model rationales in its evidence context. That pass was discarded and regenerated from frozen page text. Because the input procedure changed, we do not interpret differences from the invalid run as measured accuracy gains. Its corrected, exploratory results remain in Appendix B.

### 4.4 Blinded GLM-5.3 max-effort concordance

All 309 planned batches were submitted between September 20 and 23, 2026 (UTC). Of these, 298 resolved batches covered 5,944 planned records and returned 5,894 uniquely identifiable records: 5,893 schema-valid judgments and one field-schema failure. Fifty requested records were omitted from complete responses. Eleven whole-batch failures excluded 220 planned records: 160 from eight identity-ambiguous outputs, 40 from two exhausted connection-failure batches, and 20 from an exhausted rate-limit/connection sequence. No batch remained unattempted (Table 5). All 317 wire requests, including retries and continuations, recorded GLM-5.3/max; the minimum observed response-or-error-to-next-request gap was 1.01 seconds. Original failed attempts and later continuation amendments remain separately fingerprinted.

| Mutually exclusive planned-record outcome | Records |
|---|---:|
| Schema-valid paired judgment | 5,893 |
| Schema-invalid returned record | 1 |
| Omitted from a complete response | 50 |
| Whole-batch identity failure | 160 |
| Exhausted connection-only failure | 40 |
| Exhausted rate-limit/connection failure | 20 |
| Unattempted | 0 |
| Total planned | 6,164 |

Table: Final max-pass record accounting. Complete submission is not complete valid coverage. Separately, identity-failed responses contained 140 raw output objects, none accepted; their unexpected IDs are not additional study records. Interrupted output counts and server-side usage remain unknown.

Concordance uses only the 5,893 valid pairs (95.60% of the planned corpus). The primary labels agree on 4,569 pairs (77.53%; nominal Cohen's kappa = 0.619; Table 6). On this same subset, GPT labels comprise 1,095 yes, 3,642 no, and 1,156 unclear; GLM labels comprise 1,362 yes, 3,022 no, and 1,509 unclear. Of 1,324 disagreements, 768 pair GPT no with GLM unclear and 247 pair GPT unclear with GLM no. These transitions locate disagreement, without establishing which label is correct. The 1,074 joint positives are model consensus, not verified suppliers.

| GPT final label | GLM yes | GLM no | GLM unclear | Total |
|---|---:|---:|---:|---:|
| Yes | 1,074 | 10 | 11 | 1,095 |
| No | 109 | 2,765 | 768 | 3,642 |
| Unclear | 179 | 247 | 730 | 1,156 |
| Total | 1,362 | 3,022 | 1,509 | 5,893 |

Table: Primary-label confusion matrix. Rows are the final GPT procedure and columns are the single GLM pass; neither axis is a human gold standard.

Schema-valid does not mean that every evidentiary instruction was satisfied. Among 1,362 GLM positives, 73 carried a nonliteral-positive-quote flag and five a production-state/query mismatch flag; flag categories can overlap. The frozen analysis retains these labels and flags without repair or a fresh review. This differs from the targeted quote re-audit applied to GPT positives and further limits direct model attribution. Class-specific coverage and component agreement appear in Appendix D. Whole-batch exclusions may affect the comparison's representativeness, and repeated pages/entities preclude treating pairs as independent observations.

## 5. Interpretation and Limitations

**Agreement, quotation integrity, and validity are different properties.** Fieldwise merging prevents an adjudicator from changing agreed fields under the stated rule. Literal matching checks whether the reported words occur in the supplied excerpt. Neither property establishes that the words entail all five support conditions, that the webpage is truthful, or that the model agrees with a domain expert. The corrections make specific processing failures inspectable without substituting internal checks for external validation.

**Adjudication needs an explicit scope and post-merge checks.** A structured workflow should record which fields triggered review, preserve agreed fields when adjudication is disagreement-only, and flag contradictions after merging. The 321 overwrites illustrate coupling between an auxiliary dispute and a primary decision. The absence of violations in our limited final-positive checks does not establish that every merged field is coherent or that no and unclear are consistently distinguished. Future human review should examine that boundary and capability-location entailment, retaining raw model outputs alongside flags rather than silently repairing them.

**The task definition limits downstream use.** A page can fail this single-excerpt test while another page supplies the missing location evidence. A future system that combines pages would require a multi-page reference task and identical evidence access for its baselines. Likewise, a graph-based candidate-ranking experiment would need an independent human test set and controls for extra text, simple graph statistics, and message passing. This corpus is not already a validated GNN benchmark.

**Collection and model scope are narrow.** The study uses two providers, selected capability/state templates, accessible top-10 destination pages, and a particular excerpt procedure. The main workflow uses repeated GPT passes; the additional GLM pass changes both model and review procedure. Repeated pages and entities induce dependence. Fetch failures, truncation, query wording, stale pages, and one-focal-business extraction shape the observed labels. Results do not estimate national coverage, industry prevalence, procurement readiness, actual buyer-supplier links, or SME status. Cross-model concordance supplies neither a causal model comparison nor a second complete retrieval-and-screening workflow comparison. No comparative accuracy claim against another model or reviewer is supported.

**The audit is retrospective and incompletely validated.** Processing failures motivated the corrections, and this manuscript refocus was made after results were known. The changes were not prespecified experimental arms. The original human double-annotation and entity-resolution precision gates remain unmet. Removing entity-level findings from the main narrative does not satisfy or waive those gates. The recorded calibration sampling mismatch remains a limitation; its exploratory interval is not a main result here.

**Public artifacts expose only part of the evidence chain.** The public repository contains code, schemas, queries, logs, and aggregate bytes, while the frozen page bodies and row-level decisions remain closed. Hashes establish byte identity, not factual correctness. Independent researchers can inspect the workflow and aggregates but cannot reproduce or audit individual frozen judgments from the public package alone.

## 6. Conclusion

On 6,164 constructed source-capability-state pairs, the final same-model workflow assigned 1,148 positive page-support labels. Retrospective reconstruction showed that whole-record adjudication overwrote 321 of 2,145 agreed primary labels routed to C (14.97%); fieldwise merging preserved those agreements. Literal-quote re-audit separately downgraded 31 flagged positives. A separate GLM-5.3 max-effort pass completed submission with 5,893 valid paired judgments and 77.53% agreement (kappa = 0.619), retaining 271 invalid, omitted, or failed planned records outside concordance. These findings identify concrete process sensitivities in LLM-assisted evidence screening. Human validation is required before interpreting the labels as benchmark judgments or measuring factual screening performance.

## Data, Code, and AI-Use Disclosure

Frozen queries, processing and review scripts, schemas, deviation logs, and the row-free aggregate package are publicly archived in the [US-SME Signal Graph repository](https://github.com/elijahqi/us-sme-signal-graph). The original aggregate package is anchored at [commit c036829](https://github.com/elijahqi/us-sme-signal-graph/commit/c036829224cbd600534623e7f751cd86514dbd1d); its eight published SHA-256 entries were checked after upload. The package remains versioned as *long-tail-evidence-audit-v0.1-exploratory* because this manuscript revision does not change its data. Search-provider payloads and fetched third-party page text are excluded from the public artifacts. The companion [processing-stage summary](https://github.com/elijahqi/us-sme-signal-graph/blob/main/paper/audit_processing_sensitivity_v0_2.json) records the reconstructed counts and input fingerprints. Its reconstruction script checks all 6,164 final rows across ten key fields against the stored final table and recomputes the 71 quote-check failures. Re-running that audit requires the closed corpus; the public summary does not enable record-level reproduction.

The additional [adjudication-contract summary](https://github.com/elijahqi/us-sme-signal-graph/blob/main/paper/adjudication_contracts_v0_3.json) records routing denominators, overwrite transitions, final-positive consistency counts, and input hashes. Its audit script requires complete C coverage of disputed pairs. Public synthetic regression tests illustrate the merge failure and consistency rules without exposing source records. They test the implementation, not the model's factual judgments.

The [output-integrity summary](https://github.com/elijahqi/us-sme-signal-graph/blob/main/paper/output_integrity_v0_4.json) records all-16-field verification, label/reason cross-tabulation, and quote coverage by final label. Its script uses unchanged frozen inputs and records their fingerprints. The public aggregate files contain no source rows or quotes. Stable manuscript filenames retain their initial version suffix; the displayed version and Git revision identify the current text.

The [max-pass comparison](https://github.com/elijahqi/us-sme-signal-graph/blob/main/paper/glm_max_cross_review_v0_4.json) and [execution audit](https://github.com/elijahqi/us-sme-signal-graph/blob/main/paper/glm_max_execution_audit_v0_4.json) publish only aggregate counts, confusion matrices, diagnostics, settings, and fingerprints. The execution audit independently recomputes concordance and checks request pacing across saved attempts. The protocol, max-effort/retry amendment, and three later failure-continuation amendments remain distinct records. The archived low-requested pass is excluded. Regenerating the comparison requires the closed inputs and raw outputs; public hashes do not reveal or validate individual judgments.

GPT-5.6-Sol generated the study's screening decisions through the disclosed repeated-pass workflow. An AI coding assistant assisted with analysis checks, manuscript revision, and formatting. For v0.4, GLM-5.3 provided serial manuscript and code critiques through Claude Code; two preliminary section reviews used GLM-5.3-Flash before the model was changed. Suggestions were checked against scripts, arithmetic, and source records before adoption, and unsupported suggestions were rejected. The editorial campaign generated no research annotations and is neither an independent validation study nor human review. The separately specified blinded GLM-5.3/max research pass did generate the comparison judgments in Section 4.4; no Flash outputs enter that comparison. Author review and the selected venue's AI-use requirements remain outstanding submission tasks. The revision record and claim audit preserve the research scope change and validation status.

## References

[1] Y. Li, X. Liu, and B. Starly. Manufacturing service capability prediction with Graph Neural Networks. *Journal of Manufacturing Systems*, 74, 291-301, 2024. <https://doi.org/10.1016/j.jmsy.2024.03.010>.

[2] Y. Li, H. Ko, and F. Ameri. Integrating Graph Retrieval-Augmented Generation With Large Language Models for Supplier Discovery. *Journal of Computing and Information Science in Engineering*, 25(2), 021010, 2025. <https://doi.org/10.1115/1.4067389>.

[3] Y. Qi, Y. Qi, and T. Wagh. Coverage-Aware Web Crawling for Domain-Specific Supplier Discovery via a Web-Knowledge-Web Pipeline. *arXiv:2602.24262v4*, 2026. <https://arxiv.org/abs/2602.24262v4>.

[4] N. Yagci, S. Sünkler, H. Häußler, and D. Lewandowski. A Comparison of Source Distribution and Result Overlap in Web Search Engines. *Proceedings of the Association for Information Science and Technology*, 59(1), 346-357, 2022. <https://doi.org/10.1002/pra2.758>.

[5] C. Buckley and E. M. Voorhees. Retrieval Evaluation with Incomplete Information. *SIGIR '04*, 25-32, 2004. <https://doi.org/10.1145/1008992.1009000>.

[6] J. Dodge, M. Sap, A. Marasović, W. Agnew, G. Ilharco, D. Groeneveld, M. Mitchell, and M. Gardner. Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus. *EMNLP*, 1286-1305, 2021. <https://aclanthology.org/2021.emnlp-main.98/>.

[7] L. Zheng et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems*, 36, 46595-46623, 2023. <https://papers.nips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html>.

## Appendix A. Collection Context and Descriptive Subgroups

The states were Massachusetts, Pennsylvania, Michigan, Ohio, North Carolina, Texas, Arizona, and California. Ten capability families supplied four capabilities each. Cross-query deduplication and pair construction mean that ranked rows, URLs, pairs, and businesses are different units. Query-URL overlap was 63.81% when pooled across all queries and 65.55% as the macro mean of per-query Jaccards. On the 959 dual-success queries, the corresponding values were 63.86% and 65.62%. Overlap measures returned-URL agreement, not producer recall or provider quality.

| Industry family | Yes | Pairs | Positive-label rate |
|---|---:|---:|---:|
| Precision metal | 294 | 645 | 45.58% |
| Wood / industrial packaging | 223 | 601 | 37.10% |
| Remanufacturing | 139 | 533 | 26.08% |
| Electronics | 113 | 551 | 20.51% |
| Additive manufacturing / tooling | 126 | 715 | 17.62% |
| Polymers / composites | 110 | 622 | 17.68% |
| Contract consumer production | 61 | 582 | 10.48% |
| Industrial textiles | 50 | 605 | 8.26% |
| Semiconductor | 15 | 590 | 2.54% |
| Battery | 17 | 720 | 2.36% |

Table: Descriptive label fractions in selected query families. They are not national industry estimates or controlled industry effects.

State-conditioned fractions ranged from 11.46% in Massachusetts to 24.68% in Texas. Intent tags overlap: direct-observed pairs had 674 positives among 3,164 incidences, mixed ownership/locality 695 among 3,009, and small-batch 491 among 2,745. These are descriptive incidences, not randomized wording effects. Full state and intent tables remain in the public aggregate package.

## Appendix B. Provisional Entities and Destination-Page Size Screen

These analyses are retained as exploratory context and are not primary contributions of this revision. Positive pairs were initially blocked by domain, normalized name, and state. Dedicated business domains could support initial grouping; shared third-party directories could not. Following quote correction, 89 flagged domain clusters and 11 fuzzy/alias candidate pairs received same-model review, alongside exact normalized-name/state consolidation across domains. The 1,148 positive pairs mapped to 790 provisional operating-entity clusters and 785 corporate-group clusters. False-merge and false-split uncertainty has not been measured externally, and clusters were not equated with production sites.

The corrected size screen used only frozen destination-page text around employee, workforce, owner-only, nonemployer, and federal-program terms. It replaced an invalid pass containing earlier model rationales. Empty contexts were screen-negative: 446 positive-pair contexts contained a size term and 702 did not. A same-model pair-level evidence screen then retained 39 non-insufficient size signals; a term match alone was insufficient, and numerical claims had to refer to the focal business rather than facilities, customers, or industry totals. Those 39 pairs mapped to 29 provisional clusters for entity-level A/B review and fieldwise C adjudication on five semantic disagreements. All 29 eligible entity-level quotations passed literal matching; 761 automatic screen negatives were not quote-audit eligible.

| Size-screen result | Provisional clusters |
|---|---:|
| Nonhistorical numerical employee evidence | 23 |
| Wholly within one descriptive employee band | 14 |
| Band 10-99 | 10 |
| Band 100-499 | 2 |
| Band 500+ | 2 |
| Numerical bounds crossing bands | 9 |
| Current owner-only support | 0 |
| Explicit SAM/SBA or named-program page representation | 3 |
| No nonhistorical numerical employee evidence | 767 |

Table: Nested or overlapping categories, not an additive partition. The 23 numerical cases comprise 14 single-band and nine cross-band cases. All counts depend on provisional entity resolution.

The three federal representations comprise two explicit SAM/SBA claims and one named-program claim; one overlaps a single-band case. They are page representations, not independent determinations. The descriptive employee bands are not SBA size definitions. External SBA-small verification was not performed. This narrow screen measures evidence on already retrieved destination pages under the term lexicon; it cannot estimate firm-size information availability across the public web.

## Appendix C. Deviations and Outstanding Validation

**Calibration.** The 1,200-pair calibration ended with 214 yes, 677 no, and 309 unclear labels. Its sampler used 30 industry-family by primary-intent strata, narrower than protocol v0.3's stated balancing dimensions. Its 10,000-replicate bootstrap resampled pairs within strata instead of query units. The reported weighted estimate, 17.84%, and interval, 15.84%-19.86%, remain historical exploratory diagnostics in the aggregate package; they are not presented as protocol-conformant or used as confirmatory evidence here.

**Audit trail.** Protocol v0.4 was committed after retrieval and calibration, before the 4,964-pair extension. The public model-review deviation log records the human-review substitution, amendment timing, whole-record merge, quote-denominator correction, overlap terminology, literal-quote re-audit, and sampling mismatch. The v0.2 and v0.3 revision records document the retrospective editorial refocus and routing audit; v0.4 documents model-assisted editorial review, further deterministic output checks, and the separate cross-model pass with its execution amendments. None converts the original study into a fully preregistered or human-validated experiment.

### Submission Gates

The existing study requirements remain in force. This draft is not publication-ready until the outstanding gates in the repository's claim audit are completed:

1. The original 1,200-case first human annotation is completed, with at least 300 cases independently double annotated under provider-blind conditions, component and overall agreement reported, adjudication performed, and the preregistered $\kappa \geq 0.70$ gate evaluated. A 300-case-only study would require an explicit amendment and would not complete the original plan. Model-versus-human comparison must include no and unclear cases, not only model positives.
2. The presampled 200-pair entity-resolution precision audit is executed and its $\geq 0.95$ gate is evaluated. Moving entity results to an appendix does not complete or waive this requirement.
3. Corrected entity-size tables and hashes remain synchronized; the selected venue's literature coverage, bibliography, and AI-use requirements are checked.
4. Any future confirmatory use of the calibration interval reconciles sampling and resampling with the declared protocol. This revision makes no such claim.
5. The public aggregate package and post-publication checksum verification remain documented. This archival step has been completed; it provides no substitute for human validation.

No new human labels, trained GNN, external entity verification, or submission outcome is reported in this revision.

## Appendix D. Cross-Model Coverage and Component Concordance

| GPT final class | Planned | Valid paired | Invalid | Omitted | Whole-batch failed |
|---|---:|---:|---:|---:|---:|
| Yes | 1,148 | 1,095 | 0 | 14 | 39 |
| No | 3,799 | 3,642 | 1 | 26 | 130 |
| Unclear | 1,217 | 1,156 | 0 | 10 | 51 |
| Total | 6,164 | 5,893 | 1 | 50 | 220 |

Table: Coverage of the original GPT labels. Invalid, omitted, and failed records contribute no paired judgments. No record was unattempted.

| Compared field | Paired n | Agreement | Nominal kappa |
|---|---:|---:|---:|
| Business identity | 5,893 | 87.07% | 0.525 |
| Direct production | 5,893 | 87.10% | 0.718 |
| Capability match | 5,893 | 85.34% | 0.720 |
| Production-presence category | 5,893 | 73.14% | 0.616 |
| Current commercial offering | 5,893 | 86.17% | 0.615 |
| Primary label | 5,893 | 77.53% | 0.619 |
| Primary exclusion reason | 5,893 | 70.47% | 0.646 |

Table: Exact-category agreement on fully schema-valid records. Capability match has four categories and production presence has seven; the latter is not a separate factual test of in-state location. No partial credit or independent-row confidence interval is used. Full component confusion matrices are in the public aggregate JSON. All agreement values measure recorded decisions, not human accuracy.
