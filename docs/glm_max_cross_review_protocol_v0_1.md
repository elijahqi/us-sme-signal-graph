# GLM-5.3 max-effort full-pass amendment

On 2026-09-20 UTC the user authorized automatic retries and explicitly requested GLM-5.3 with max reasoning effort. This amendment precedes the first max-profile research request. It changes execution settings, not the evidence, schema, semantic instructions, fixed permutation, batch size, or GPT reference defined in [the original protocol](glm_full_cross_review_protocol_v0_1.md).

## Separate full pass

The model identifier remains `glm-5.3`; `max` is the reasoning effort, not a different model ID. All 6,164 frozen records are submitted in 309 batches to a new private `glm_full_cross_review_max_v0_1` directory. The earlier run requested low effort; actual historical wire effort was not captured. Its partial results and original failures remain archived separately and are excluded from the max-pass comparison. Re-evaluating that prefix is a user-requested configuration change, not selection based on agreement or preferred labels.

The official Claude Code client sets `--effort max` and advertises the custom model's documented effort and adaptive-thinking capabilities. The local relay refuses a research message unless its outgoing body names `glm-5.3` and `output_config.effort=max`. It does not rewrite messages. Before research execution, a synthetic local upstream test verified that the installed client emits those fields, adaptive thinking, and a 65,536-token output allowance. The provider, not the client's cost estimate, determines actual quota consumption. No Flash fallback is permitted.

The manifest freezes these settings and all input/reference hashes. Safe transport metadata records the model, effort, thinking control, output allowance, request-body digest, timestamps, HTTP status, and any Retry-After header. It contains no credentials or evidence text. Analysis verifies transport fingerprints and the minimum one-second gap between requests within each session. New sessions also wait at least one second before their first request. The project-wide exclusive process lock and single-thread relay keep concurrency at one, including client continuations. Other applications using the account are outside this limit.

## Bounded automatic retries

SDK and relay retries remain disabled. A separate journaled supervisor can retry a failed batch at most twice (three attempts total), waiting at least 30 and then 60 seconds, extended by a longer server Retry-After instruction. Only transient connection errors, timeouts, and HTTP 408/429/500/502/503/504/529 qualify. Authentication, exhausted quota, invalid requests, unexpected model identity, and successfully returned malformed research outputs require diagnosis. A started attempt with uncertain process termination is not blindly replayed.

Each retry preserves the previous journal and captured response/stream bytes with fingerprints, sends the unchanged frozen batch, and stores the new attempt separately. Interrupted attempts contribute no inferred labels. Their unknown server-side usage and any partial output remain retained. A complete response with invalid enums or omitted IDs uses the existing quarantine and omission rules; it does not trigger a fresh model call. Retry exhaustion stops the supervisor and requires diagnosis. Retrying is never conditional on the semantic label, concordance, or desired positive rate.

Response timeouts allow up to 3,000 seconds, with a 3,060-second client deadline. Timeout output is retained. All final denominators, confusion matrices, agreement, kappa, component concordance, joint positives, and failure counts follow the original analysis plan. Prior attempts and final transport/input/output/protocol fingerprints are checked before reporting.

This remains a cross-model concordance study. No human gold labels, human agreement gate, entity-resolution accuracy gate, or causal model comparison is supplied by this amendment.

Official configuration references: [Z.ai model switching and effort mapping](https://docs.z.ai/devpack/latest-model), [GLM thinking modes](https://docs.z.ai/guides/capabilities/thinking), and [Claude Code custom model capabilities](https://code.claude.com/docs/en/model-config#customize-pinned-model-display-and-capabilities).
