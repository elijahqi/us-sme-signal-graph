# Manuscript revision v0.4: editorial review and stored-output checks

**Status, 2026-09-23 UTC:** manuscript revision and local delivery verification complete. The GLM-5.3 max submission pass and final analysis are complete with excluded failed batches. This record covers the completed editorial review, deterministic checks, cross-model concordance and PDF verification, not human validation or submission readiness. Repository delivery is identified by the Git commit containing this record.

## Review provenance and limits

The editorial campaign sent public manuscript sections and selected code to GLM through Claude Code, with tools disabled and requests serialized. Two preliminary scope/methods responses used GLM-5.3-Flash before the user switched to GLM-5.3. Six subsequent section requests used GLM-5.3: scope, methods, results, appendices, audit code, and comparison code. These are editorial requests, separate from the blinded research-label comparison. They must not be described as an all-max editorial campaign or as human peer review.

The saved results and appendices responses contain only a final continuation. References in those fragments to earlier numbered findings are not a complete retained review. No missing critique has been reconstructed or attributed to the model. Later stream capture retains assistant text segments; it cannot recover text absent from the older recordings. Raw responses, request records, and their fingerprints remain private.

Model statements marked “verified” were treated as suggestions requiring independent inspection. Several were incorrect. The dispositions below distinguish changes supported by the stored evidence from rejected or deferred proposals.

## Verified changes in the local manuscript draft

| Review issue | Disposition and evidence |
| --- | --- |
| Population for the 71 flagged positive quotations was unclear | Specify 1,179 positives before targeted re-review, 71 quote failures, 40 retained positives, and 31 changes to unclear. The headline 1,148 positives already include that stage. The frozen processing-sensitivity reconstruction supplies the counts. |
| HTTP outcomes and process flags were mixed | Give disjoint HTTP categories: 3,383 2xx responses (3,190 status 200; 193 status 202), 1,018 status 403, 73 other non-2xx, and 164 without HTTP status, totaling 4,638 URLs. Separately report 129 robots and nine timeout flags. Do not adopt the suggested approximate residual or equate 2xx with usable evidence. |
| The actual merge implementation and C coverage were not named | Identify `analyze_ai_cross_review.py`, `analyze_full_census.py`, and the reconstruction audit. All 3,292 disputed original records have exact C coverage. The fieldwise merge preserves agreed fields but can still create hybrid records; neither property establishes correctness. |
| Positive-only quotation checks left nonpositive traceability undescribed | Apply the deterministic normalized-occurrence check to all stored final quotations, without new model calls or relabeling. Report 508 of 5,016 nonpositives without a nonempty normalized match, separating empty from nonmatching quotes. These are not 508 semantic errors. |
| The no/unclear boundary needed evidence rather than a retrospective rule change | Cross-tabulate final labels and primary reasons. The 795 no labels with evidence-gap reasons are an observation requiring human investigation, not confirmed misclassifications. Do not automatically recode them or select a new human sample silently. |
| The size-screen reduction from 446 term-bearing contexts to 39 signals was unexplained | Describe the intervening same-model evidence screen and its non-insufficient selection rule, followed by mapping 39 pairs to 29 provisional clusters. Inspection of `analyze_size_evidence_v0_2.py` and `prepare_entity_size_review.py` rules out describing this as mere deduplication. |
| Version suffixes and assistance disclosure could confuse readers | Keep stable manuscript filenames, identify the displayed revision and Git version, disclose the two early Flash responses and later GLM-5.3 editorial assistance, and distinguish editorial suggestions from research annotations. |

The [output-integrity audit](output_integrity_audit_v0_4.md) also reconstructs all 16 final decision fields for all 6,164 records with zero mismatches. It extends provenance checking beyond the ten adjudicated key fields. The original final-table fingerprint and prior aggregate releases remain unchanged. The manuscript now also states the original 1,200 first human annotations, at least 300 independent double annotations, and adjudication requirement explicitly; a 300-case-only study cannot silently replace that plan.

## Code dispositions

The final-CSV reader now rejects primary labels outside the declared enum. This closes a real failure path in which malformed labels could silently leave positive counts. The change and its synthetic regression test are archived with the output-integrity audit.

The local `run_trae_ai_review.py` revision preserves accepted and failed batch outcomes in an atomically replaced manifest after each completed future and exits unsuccessfully if any batch failed. Its regression test retains one synthetic success and one synthetic failure. This improves future execution accounting; it does not rerun, repair, or alter the historical research labels. This change is separate from the active GLM supervisor and its retry journal.

| Suggested correction | Disposition |
| --- | --- |
| `eqdp` is absent from `KEY_FIELDS`, so the nonprimary-change count can be negative | Rejected: `eqdp` is present. The suggested diagnosis does not apply to the inspected code. |
| State abbreviation expansion is performed on only one side | Rejected: both `production_state` and `state_id` pass through the same normalization helper. |
| Case-fold strict schema enum values as if they were free-text states | Rejected: enum membership and free-text normalization serve different contracts. Changing a stored enum into a valid value would conceal a schema failure. |
| The original ten-row reviewer must accept arbitrary batch sizes | Not adopted for the frozen study: ten rows were its declared batch contract. The separate full-corpus GLM runner validates its own frozen batch membership, including its shorter last batch. |
| Force all apparently affirmative component combinations to a positive primary label | Not adopted: eligible presence and component strings alone do not establish joint capability and in-state production support. Contradictions remain visible for review rather than being repaired into a preferred label. |
| Retry historical negative/unclear or nonliteral-quote outputs under stricter new rules | Not adopted: new acceptance rules cannot be applied retroactively without changing the experiment. The v0.4 deterministic audits retain frozen labels; the separate GLM pass follows its disclosed response-quarantine and omission rules. |

## Rejected or incomplete editorial advice

The proposed percentages 61.64% and 19.75% were arithmetically wrong: 3,799/6,164 and 1,217/6,164 round to 61.63% and 19.74%. The positive fraction remains 18.62%. The existence of an abstract percentage for only one class is a presentation choice, not an arithmetic error.

The two authors abbreviated Y. Qi in reference [3] were checked in the earlier source-verification step and are distinct authors, Yijiashun Qi and Yijiazhen Qi. The duplicated initial was not sufficient grounds to alter the citation. The omitted earlier results/appendices findings are not presumed correct from a concluding assertion that they were verified. Counts in the manuscript must be supported by the underlying audits rather than that assertion.

The Gemini code review raised reference-coverage, excluded-output denominators, pricing/configuration freeze, response-schema, and result-provenance concerns. They remain deferred review items for that inactive runner, not resolved defects or findings from an executed Gemini experiment. Its evaluation has never run. Removing price fields from a fingerprint or silently excluding stale results should not be adopted without designing and testing the full execution contract. The active GLM pass has its own frozen manifest, explicit denominators, and artifact verification; this does not imply that the Gemini implementation was corrected.

## Execution amendments to disclose with the cross-model results

The research comparison is a separate blind pass over the 6,164 frozen records. Its requests specify `glm-5.3` and `output_config.effort=max`; the archived low-requested prefix is excluded. The max setting and user-authorized bounded transport retries are disclosed in the [max protocol](glm_max_cross_review_protocol_v0_1.md). The original protocol fingerprint remains unchanged; the following later operational amendments have separate fingerprints and must not be described as prespecified rules.

The diagnosed closures below apply separate operational amendments. These are the final closed failures in the 309-batch max pass; remaining batches through 309 completed without additional whole-batch failures. The eight identity failures retain 140 raw returned objects collectively, none accepted as paired judgments; unexpected IDs are not members of the study population. Requested IDs absent from those responses belong to the whole-batch failure count, not ordinary omissions.

| Closure and amendment | Diagnosed batches | Retained evidence | Failed planned rows |
| --- | --- | --- | ---: |
| [Identity failure](glm_format_failure_continuation_v0_1.md), recorded after batch 27 and before 28 | 27, 143, 175, 255, 281, 294 | Each complete response returned 20 unique objects: 19 requested IDs and one unexpected ID; one requested ID absent. | 120 |
| Same identity amendment | 45 | Complete response returned 19 unique objects: 18 requested IDs and one unexpected ID; two requested IDs absent. | 20 |
| Same identity amendment | 122 | Complete response returned one unexpected ID and none of the 20 requested IDs. | 20 |
| [Exhausted connection failures](glm_exhausted_transport_continuation_v0_1.md), recorded after batch 49 and before 50 | 49, 236 | Each exhausted its original attempt and two authorized retries with connection-reset/API-error terminations. | 40 |
| [Exhausted mixed transport failure](glm_mixed_transport_continuation_v0_1.md), recorded after batch 282 and before 283 | 282 | First attempt returned HTTP 429 with explicit request-rate-limit code 1302; two retries ended in connection-reset/API errors reporting stream idle timeouts. This sequence did not qualify under the connection-only amendment. | 20 |

All identity-failed responses completed with HTTP 200 and `end_turn` under verified GLM-5.3/max settings. Each entire planned batch was excluded, including objects whose IDs matched. No ID was repaired or mapped and no replacement request was made. Connection-only and mixed failures each retained exactly three attempts, accepted no labels, and received no fourth request. Interrupted output-object counts and server-side usage remain unknown.

Local power records overlap the exhausted transport attempts with sleep and wake cycles. This supports host suspension as a possible contributor without establishing an exclusive cause. After batch 282, execution awaited a real full-wake transition because a lid-open indicator alone had also occurred during background dark wake. On September 22 at 23:21 UTC, full wake and free process locks were verified and only unattempted batches from 283 resumed. After the separately diagnosed identity failure in batch 294, the host had returned to sleep/background-wake cycling; only the remaining unattempted batches from 295 resumed after full wake was verified on September 23 at 02:25 UTC. This identity failure was a complete response and is not attributed to sleep. The temporary worker-bound idle-sleep assertion changes no research evidence or permanent sleep setting and does not override lid closure.

These closures preserve original failed journals, raw responses, streams, transport traces, and prior attempts with fingerprints. They permit only subsequent unattempted batches to continue under the existing serial pacing and retry bounds. Future failures still stop for diagnosis. The final analysis must verify all applicable amendment fingerprints and every closed-failure artifact, and report identity, exhausted-connection and exhausted-mixed-transport failures separately. Exclusions can affect representativeness; the complete-case agreement estimate must retain its explicit coverage denominator and cannot establish accuracy. Final failed-row totals are 160 identity, 40 exhausted connection-only, and 20 exhausted mixed-transport records. All 309 batches are terminal.

## Final analysis and manuscript reconciliation

The final `glm_cross_review.py analyze --profile max` result is `complete_with_failed_batches`. All 6,164 planned records were submitted in 309 batches; 298 resolved batches returned 5,894 identifiable records, including 5,893 schema-valid judgments and one field-schema failure. Fifty requested records were omitted, and 220 remain whole-batch failures. None is unattempted. The eight identity-failed responses separately contain 140 raw objects, all excluded; interrupted output-object counts and server-side usage are unknown.

Primary concordance is 4,569/5,893 = 77.53%, nominal kappa 0.619, with 1,074 joint positives. Integer counts and rational arithmetic independently reproduced all seven field-level agreement statistics and confusion counts. The final audit verifies frozen input/reference/protocol/output fingerprints, original failures, seven archived prior attempts, three later amendment fingerprints, and all 317 GLM-5.3/max wire requests; the minimum response/error-to-next-request interval is 1.010201 seconds. These checks do not establish accuracy. The archived low-requested outputs remain excluded.

The manuscript's abstract, third research question, separate comparison methods/results, coverage/component appendix, limitations, conclusion and AI-use disclosure now reflect these results. The [row-free results record](glm_max_cross_review_results_v0_4.md), [comparison JSON](../paper/glm_max_cross_review_v0_4.json), [execution audit](../paper/glm_max_execution_audit_v0_4.json), README, completion status and claim audit distinguish full submission from valid coverage and a label comparison from a second complete workflow. The 73 nonliteral-quote and five state/query flags among GLM positives remain attached to unchanged schema-valid labels, unlike the targeted positive-quote re-audit of GPT. This procedural difference is disclosed.

## Delivery verification

The Markdown source regenerated the tracked LaTeX and 11-page PDF. All pages were rendered and visually inspected for text, table, caption, pagination and margin defects. A stranded Appendix D heading was moved with its tables; the final pages 10–11 were reinspected and rendered pages 1–9 remained byte-identical to the already inspected images. Content checks passed with no overfull boxes. The final PDF SHA-256 is `051106025aa778e4fb6079488bd57df10f20f8d173f6bbbffb65e235cca4918c`.

All 105 unit tests passed, including the synthetic mixed-success/failure manifest regression. The staged release preflight passed for 188 tracked files. The unchanged earlier public candidate release passed its five checksums and 30-row scope check with zero confirmed-SME claims; all eight files in the row-free long-tail aggregate release also validated. The two new GLM summaries were checked for prohibited per-record fields, the comparison was byte-identical to the final analyzer output, and the retained private verification-manifest fingerprint matched the public execution audit.

All staged tracked content was scanned against both project Keychain credentials without displaying either value; no credential matches were found. None of the 6,164 actual frozen review IDs occurred in the 14 delivery files or extracted PDF text. Private corpus, raw responses, process logs, human-annotation storage and page-render images are excluded from Git. These are release-scope checks, not a claim that the closed corpus is independently reproducible. Remote file hashes and CI status are verified after the delivery push and retained with its private delivery receipt; this record does not substitute a local check for that verification.

The [human-validation and entity-resolution gates](research_completion_status_v0_4.md) remain separate requirements: 1,200 first human annotations with at least 300 independent double annotations, adjudication and evaluated kappa, plus the presampled 200-pair entity audit. The local annotation collection contained zero saved record files at final analysis. Providing that interface or obtaining cross-model agreement does not complete these gates. No new graph experiment, human accuracy result, or submission is reported here.
