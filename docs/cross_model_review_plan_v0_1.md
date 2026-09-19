# Cross-model review: prepared design, not executed

This is a prospective plan for an additional model comparison on an already analyzed corpus. It is not a preregistration of the original study and reports no new annotations. The default runner is deliberately blocked from live execution until an available model, current endpoint-specific prices, billing project, and usable budget have been verified.

## Sampling and interpretation

`scripts/gemini_cross_review.py prepare` selects the 300 previously designated double-review IDs from the calibration sample for evaluation. It draws 20 development pairs from separate registrable domains, using fixed seeds. Development and evaluation are domain-disjoint from each other; neither is a newly acquired corpus or an independent human reference set. Evaluation is a fixed selected-sample description, not a national prevalence estimate.

Only the original frozen excerpt, source metadata, task, and opaque review ID are supplied. Prior labels, rationales, provider identity, rank, and adjudication outputs are excluded. No browsing or tools are enabled. The input whitelist and hashes are saved before execution. The development stage must finish before freezing prompt, schema, implementation, model version, and settings for evaluation.

The primary comparison is a three-class confusion matrix, raw agreement, and nominal Cohen's kappa against the final GPT-generated labels, with component agreement as a descriptive supplement. These measure cross-model concordance, not accuracy. The GPT labels include adjudication and targeted quote re-review, whereas the proposed Gemini outputs are a single pass; this comparison cannot isolate model identity from the review procedure. A human-reference experiment would require a separate design and independent labels.

Literal-quote, component, and production-state checks are retained as quality flags alongside the unchanged model output. Invalid, incomplete, failed, and missing outputs must remain visible in denominators. If budget or availability stops the run, report the completed subset and planned denominator; do not present it as a completed 300-case experiment. Repeated pages and entities limit independence, so no ordinary independent-row inferential claim is planned.

## Execution controls

- This runner uses Vertex AI OAuth, not an AI Studio API key. Possessing a valid Developer API key does not configure this route or establish credit eligibility.
- The checked-in token rates are offline planning assumptions. They must be replaced with verified prices for the selected Vertex model before enabling live execution; the model is unselected by default.
- Calls are serial, with a project lock and no automatic retry. Each call reserves a deliberately conservative input/output allowance in a persisted ledger before being sent. Reasoning tokens are included in observed usage.
- Missing usage or an uncertain request outcome retains its reservation and stops the run. A changed billing project, model version, or frozen evaluation configuration also stops execution.
- The example local ceiling is USD 9. A local ledger does not cap account-wide spending, reserve shared credit against other projects, or prove actual promotional-credit deduction. Verify the shared remaining balance and billing route before beginning; no paid overage or account top-up is authorized by this plan.
- Evidence and responses stay in the Git-ignored private directory. API credentials belong in the operating-system credential store, never in the repository.

Offline preparation and planning are available through `prepare` and `plan`; neither sends network requests. Regression tests use synthetic inputs and mocked requests. At this revision, no Google generation ledger, completed development set, evaluation freeze, or cross-model result exists.

The separate `scripts/run_glm_quality_review.py` performs editorial/code critique through the supported Claude Code integration; it does not annotate research records. See Z.ai's [usage policy](https://docs.z.ai/devpack/usage-policy) and [supported-tool integration](https://docs.z.ai/devpack/tool/claude). It enforces concurrency one for this project and refuses silent reruns of an attempted request. Other clients using the same endpoint are outside this project lock.

On 2026-09-19 the user explicitly requested full-corpus GLM-5.3 evidence re-evaluation. That work is governed by the separate [GLM full-cross-review protocol](glm_full_cross_review_protocol_v0_1.md), uses the supported Claude Code client, and shares the same project-wide serial lock. It does not invoke the Coding Plan endpoint through a custom API client or execute this still-unrun Gemini plan.
