# GLM-5.3 max full-pass results — v0.4

**Completed submission:** 2026-09-23 03:36:43 UTC. Status: `complete_with_failed_batches`. This is a cross-model concordance audit, not an accuracy evaluation or human validation.

The comparison uses only the separate max pass. Every research request used `glm-5.3` and `output_config.effort=max`; no Flash or archived low-requested labels are included. Frozen excerpts/task metadata were whitelisted and GPT reference labels/rationales withheld. The final GPT reference is unchanged.

## Record and request accounting

| Quantity | Count |
| --- | ---: |
| Planned and submitted batches | 309 |
| Planned and submitted records | 6,164 |
| Resolved batches | 298 |
| Planned records in resolved batches | 5,944 |
| Identifiable returned records | 5,894 |
| Schema-valid paired judgments | 5,893 |
| Schema-invalid returned records | 1 |
| Omitted records in complete responses | 50 |
| Whole-batch identity-failed records | 160 |
| Exhausted connection-only records | 40 |
| Exhausted rate-limit/connection records | 20 |
| All failed planned records | 220 |
| Unattempted records | 0 |
| Raw objects in complete identity-failed responses (excluded) | 140 |
| Wire requests including retries and continuations | 317 |
| Archived prior attempts | 7 |
| Batches with automatic retries | 4 |

Only the disjoint valid + invalid + omitted + failed + unattempted categories sum to 6,164. Returned counts and request counts are overlapping or different units. The 5,894 identifiable records and 140 identity-failed raw objects total 6,034 objects in complete retained outputs, but 140 have no usable whole-batch identity mapping. Interrupted output objects and server-side usage remain unknown. Client token counters are partial reported usage, not actual billing.

Valid coverage is 95.60% (5,893/6,164). The one invalid record has an output-field mismatch and is not repaired. The 317 captured requests pass model/effort checks; minimum response/error-to-next-request interval is 1.010201 seconds. Concurrency is one for this project. Retries were capped at two per batch with 30/60-second minimum backoff and longer Retry-After honored; SDK/relay retries were disabled.

## Agreement and coverage

The primary matrix below has final GPT labels in rows and single-pass GLM labels in columns. Both are model outputs.

| GPT / GLM | Yes | No | Unclear | Total |
| --- | ---: | ---: | ---: | ---: |
| Yes | 1,074 | 10 | 11 | 1,095 |
| No | 109 | 2,765 | 768 | 3,642 |
| Unclear | 179 | 247 | 730 | 1,156 |
| Total | 1,362 | 3,022 | 1,509 | 5,893 |

Exact primary agreement is 4,569/5,893 = 77.532666%; nominal Cohen's kappa is 0.619129619. Joint positives number 1,074; they are not verified suppliers. The 1,324 disagreements include 768 GPT-no/GLM-unclear and 247 GPT-unclear/GLM-no cases. No semantic labels were changed to improve agreement.

| Field | n | Agreement | Kappa |
| --- | ---: | ---: | ---: |
| Business identity | 5,893 | 87.07% | 0.524947 |
| Direct production | 5,893 | 87.10% | 0.717883 |
| Capability match | 5,893 | 85.34% | 0.719997 |
| Production-presence category | 5,893 | 73.14% | 0.616279 |
| Current commercial offering | 5,893 | 86.17% | 0.614723 |
| Primary label | 5,893 | 77.53% | 0.619130 |
| Primary exclusion reason | 5,893 | 70.47% | 0.645995 |

| GPT class | Planned | Valid | Invalid | Omitted | Failed |
| --- | ---: | ---: | ---: | ---: | ---: |
| yes | 1148 | 1095 | 0 | 14 | 39 |
| no | 3799 | 3642 | 1 | 26 | 130 |
| unclear | 1217 | 1156 | 0 | 10 | 51 |

Among 1,362 GLM positives, 73 have a nonliteral-quote flag and five a production-state/query mismatch flag; categories may overlap. They remain in schema-valid concordance with flags attached. Schema validity does not certify semantic or quotation compliance. The GPT procedure included a targeted positive-quote re-audit; the GLM pass did not. Model, prompt, batch context and review procedure are therefore confounded. Whole-batch exclusions can affect representativeness, and no independent-row confidence interval is claimed.

## Failure handling and amendments

Eight identity-failed batches (27, 45, 122, 143, 175, 255, 281, 294) were closed only after offline diagnosis of complete responses. All 160 planned records were excluded; no IDs were repaired and no replacement call was made. Batches 49 and 236 each exhausted three connection-reset attempts, excluding 40 records without fourth calls. Batch 282 had HTTP 429 request-rate code 1302 then two connection-reset/API-error attempts, excluding 20 records under a separate mixed-transport amendment. Local sleep/wake evidence supports suspension as a possible contributor to interrupted attempts, not an exclusive cause or an explanation of complete identity failures.

See the [frozen original protocol](glm_full_cross_review_protocol_v0_1.md), [max-effort and bounded-retry amendment](glm_max_cross_review_protocol_v0_1.md), [identity continuation](glm_format_failure_continuation_v0_1.md), [connection-only continuation](glm_exhausted_transport_continuation_v0_1.md), and [mixed-transport continuation](glm_mixed_transport_continuation_v0_1.md). Later amendments have separate fingerprints and are not described as prespecified. Raw attempts, original failures, inputs, reference, output, protocol and transport fingerprints were verified, including seven archived prior attempts. All seven field-level agreement statistics were independently recomputed from the retained valid records using integer counts and rational arithmetic; they matched the analyzer to numerical precision.

## Public artifacts and scope

The [comparison JSON](../paper/glm_max_cross_review_v0_4.json) is a byte-exact copy of `glm_cross_review.py analyze --profile max` output at final verification. The [execution audit JSON](../paper/glm_max_execution_audit_v0_4.json) gives denominator reconciliation, request checks, independent metric recomputation, and provenance fingerprints. Neither includes per-record IDs, source URLs, quotes, names, rationales, or credentials. Reanalysis requires the closed corpus. The original public aggregate package is unchanged; these are separate v0.4 companion artifacts.

Independent human gold labels remain uncollected. The original 1,200 first-human-annotation plan, at least 300 independent double annotations, human kappa gate, and 200-pair entity audit remain unexecuted. The 795 GPT boundary cases are unvalidated leads. Gemini evaluation, a second complete workflow comparison, and graph experiments remain unexecuted. No paper submission is reported.
