# GLM-5.3 full-corpus cross-review protocol v0.1

The user requested a full GLM-5.3 evidence re-evaluation on 2026-09-19, clarifying that editorial/code critique alone was not the intended cross-model review. This protocol is frozen before the first GLM research-label request. It is an additional comparison on an already analyzed corpus, not a preregistration of the original study.

## Population and evidence

Review all 6,164 original source-capability-state pairs: the 1,200 calibration and 4,964 extension inputs. Preserve the exact original frozen excerpts and task/source metadata. Exclude provider identity, ranks, prior model labels, rationales, adjudications, final tables, and entity/size inferences from the model prompt. Whitelist input fields and hash each frozen batch. Store the original GPT final labels separately for analysis; never include them in the model client workspace.

Use a fixed permutation (seed 20260919) and batches of 20, with the last batch retaining its natural size. Every call starts a fresh Claude Code print session with no tools, browsing, MCP, or conversation persistence. The first batch is an operational check under the same frozen protocol, not a development set used to tune semantic judgments. No prompt selection based on agreement with GPT is permitted.

## Model and output

Request `glm-5.3`, low effort, through the official Claude Code integration at the user-provided Z.ai Anthropic-compatible endpoint. Record reported model identity and client usage. The plan does not switch to a separate paid API, top up an account, or authorize paid overages. Client dollar estimates are not treated as actual Coding Plan billing.

Assess the same five evidence-support conditions: business identity, direct production, capability, in-state eligible production, and a current commercial offering. Ask for the overall yes/no/unclear decision, component fields, a primary exclusion reason, production state, a literal supporting quotation, and a short rationale. Require every requested ID exactly once. Size/legal-form/web-visibility judgments are outside this cross-review's scope. Freeze the exact instructions, schema, settings and input hashes in the private manifest before execution.

Schema failures and incomplete responses are execution failures, not `unclear` judgments. Preserve raw responses. Retain semantic/quote/state quality flags alongside unchanged valid model labels; do not force GLM labels to match GPT or silently repair them. No fresh A/B/C adjudication is part of this first GLM pass.

## Execution and stopping

Only one project GLM client may be active, sharing the editorial runner's project lock. Requests are serial; configure zero automatic API-error retries. A client may sequentially continue a length-limited response, so capture all streamed assistant messages. Other applications using this endpoint are outside the project lock. Persist an attempt journal before sending each batch, then response/result fingerprints and usage after completion. Stop on a rate limit, timeout, changed model, malformed result, or unresolved previous attempt. Reconcile uncertain outcomes before any explicit retry; do not rerun completed batches.

## Analysis

Report planned, completed, failed/uncertain, and unattempted row counts; coverage within each original GPT label; GLM label frequencies; a three-class confusion matrix; raw agreement and nominal Cohen's kappa; and component agreement with explicit pairwise denominators. Retain quality-flag counts and joint-positive counts as diagnostics. A partial run must be labeled partial, including its missing denominator. No independent-row confidence interval is planned because pages/entities repeat.

The primary comparison is single-pass GLM against the final adjudicated and quote-re-audited GPT output. Consequently, differences mix model identity, prompt wording, batch context and review procedure. They do not isolate a causal model effect or establish factual accuracy. Agreement is not human validation; disagreement is not evidence that either model is correct. Both-positive cases are model consensus, not verified suppliers. Preserve original GPT labels and keep all new GLM decisions separate.

The prior 20-development/300-evaluation Gemini plan remains unexecuted and separate. This user-authorized full-corpus GLM protocol supersedes the earlier editorial-only scope for the current GLM task, while retaining the human-validation and entity-resolution gates of the study.

## Processing amendment after batch 3 (2026-09-19)

The first two batches returned 40 schema-valid records. Batch 3 returned all 20 requested IDs, but one record used `partial` for `direct_producer_status`, whose allowed values are yes/no/unclear; the original strict batch validator stopped. Before sending batch 4, processing was amended to retain schema-valid rows and quarantine invalid rows individually when a complete, uniquely identified batch response is available. The 19 valid and one invalid batch-3 records are recovered from the saved response without another model call. The original failure journal and raw response remain preserved.

Prompts, model, schema, input batches, original reference, and input order remain frozen. Invalid records are not relabeled, repaired, or silently omitted: all planned/received/valid/schema-invalid denominators and coverage by original GPT class are reported. Agreement calculations use only fully schema-valid paired records and disclose the exclusion count. A run with responses for every planned ID but some schema-invalid records is `complete_with_invalid_rows`, not 6,164 valid judgments. API errors, incomplete batches, duplicate/missing IDs, timeouts and rate limits still stop execution; no automatic model retry is introduced. This amendment is retrospective to the first three batches and must not be described as fully prespecified.
