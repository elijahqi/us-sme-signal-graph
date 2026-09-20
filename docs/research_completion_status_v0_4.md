# Research completion status — 2026-09-20 UTC

This status distinguishes executed evidence from proposed improvements. It does not certify submission readiness.

| Item | Verified status |
| --- | --- |
| Independent human gold labels | Not collected. GPT A/B/C are repeated passes of the same model. |
| Human annotation under protocol v0.3 | Unexecuted. The original plan calls for 1,200 first human annotations, at least 300 independently double annotated cases, agreement assessment, and adjudication. A new 300-only study would need an explicit amendment rather than a claim that the whole original plan was completed. |
| Human EQDP kappa >= 0.70 | Not evaluated; no independent human decisions are available. |
| Presampled 200 merge/non-merge pairs, precision >= 0.95 | Not executed. Existing model-assisted entity resolution does not satisfy this human accuracy gate. |
| 795 no-plus-evidence-gap cases | Deterministic output inconsistency signal verified; no human test yet. These are not 795 established errors. |
| Cross-model review | Partial GLM research judgments exist. A user-requested max-effort full pass is separately configured under the new execution amendment. Full-corpus results are not yet available. |
| Gemini comparison | Inputs prepared offline; no model evaluation executed. |
| Additional workflow/system comparison | Not executed. Changing the labeling model alone does not establish generality across complete retrieval/screening systems. |
| Workshop or other submission | No submission performed. Target-specific policy checks remain outstanding. |

The archived low-requested GLM pass has 254 schema-valid judgments, two invalid rows, and four omissions in 13 resolved 20-record batches. Batch 14 returned a complete response with duplicate or unexpected IDs and remains a preserved failed output. The remaining 5,884 records were not attempted under that profile. These counts describe the archived pass, not the max pass.

Oversampling the 795-case boundary stratum would be a new, outcome-informed sampling amendment. A useful human study must retain known inclusion probabilities, blind annotators to model outputs and stratum membership where feasible, and report both stratum-specific results and appropriately weighted overall estimates. It cannot silently replace the frozen probability sample or presume humans will disagree with the model. Recruiting independent human annotators remains necessary.

References: [original human-validation protocol](study_protocol_v0_3.md), [documented AI-only deviations](model_review_deviations_v0_1.md), and [max-pass protocol](glm_max_cross_review_protocol_v0_1.md).
