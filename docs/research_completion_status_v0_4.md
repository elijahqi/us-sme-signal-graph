# Research completion status — 2026-09-23 UTC

This status distinguishes executed evidence from proposed improvements. It does not certify submission readiness.

| Item | Verified status |
| --- | --- |
| Independent human gold labels | Not collected. GPT A/B/C are repeated passes of the same model. |
| Human annotation under protocol v0.3 | Unexecuted. The original plan calls for 1,200 first human annotations, at least 300 independently double annotated cases, agreement assessment, and adjudication. A new 300-only study would need an explicit amendment rather than a claim that the whole original plan was completed. |
| Human EQDP kappa >= 0.70 | Not evaluated; no independent human decisions are available. |
| Presampled 200 merge/non-merge pairs, precision >= 0.95 | Not executed. Existing model-assisted entity resolution does not satisfy this human accuracy gate. |
| 795 no-plus-evidence-gap cases | Deterministic output inconsistency signal verified; no human test yet. These are not 795 established errors. |
| Cross-model review | GLM-5.3/max submission finished: 309 batches, 6,164 planned records, 5,893 valid paired judgments, one invalid row, 50 omissions, 220 failed-batch records, zero unattempted. Primary agreement 77.53%, kappa 0.619; these are not accuracy or human validation. See the [results and execution accounting](glm_max_cross_review_results_v0_4.md). |
| Gemini comparison | Inputs prepared offline; no model evaluation executed. |
| Additional workflow/system comparison | Not executed. Changing the labeling model alone does not establish generality across complete retrieval/screening systems. |
| Workshop or other submission | No submission performed. Target-specific policy checks remain outstanding. |

The archived low-requested GLM pass has 254 schema-valid judgments, two invalid rows, and four omissions in 13 resolved 20-record batches. Batch 14 returned a complete response with duplicate or unexpected IDs and remains a preserved failed output. The remaining 5,884 records were not attempted under that profile. These counts describe the archived pass, not the max pass.

Oversampling the 795-case boundary stratum would be a new, outcome-informed sampling amendment. A useful human study must retain known inclusion probabilities, blind annotators to model outputs and stratum membership where feasible, and report both stratum-specific results and appropriately weighted overall estimates. It cannot silently replace the frozen probability sample or presume humans will disagree with the model. Recruiting independent human annotators remains necessary.

References: [original human-validation protocol](study_protocol_v0_3.md), [documented AI-only deviations](model_review_deviations_v0_1.md), and [max-pass protocol](glm_max_cross_review_protocol_v0_1.md).

The final execution audit verified every frozen input/reference/protocol, resolved output, closed failure and archived prior attempt, plus all 317 GLM-5.3/max wire requests. The local human-annotation collection contained zero saved record files at this check. Providing that interface did not collect gold labels or evaluate the original gates. Manuscript delivery and repository publication remain separate from research validation and submission.
