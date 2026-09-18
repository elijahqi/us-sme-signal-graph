# Manuscript revision v0.3: adjudication routing audit

This revision adds a deterministic analysis of existing decisions to *Auditing LLM-Based Evidence Screening for Manufacturing Supplier Discovery*. It does not change the frozen labels, original aggregate release, study protocol, or validation gates. The filenames of the canonical Markdown, generated LaTeX, and PDF remain stable.

## Scientific changes

- The routing denominator is explicit: 3,292 of 6,164 pairs reached C for at least one key-field disagreement. Of these, 1,147 disagreed on the primary label and 2,145 agreed on that label but disagreed elsewhere.
- Whole-record C selection overwrote 321 of those 2,145 primary agreements (14.97%), all from `no` to `unclear`. Calibration contributed 38/398 (9.55%); the extension contributed 283/1,747 (16.20%). The rates condition on primary-agreed, C-routed pairs and are not accuracy estimates or a controlled comparison between stages.
- The methods state the fieldwise merge rule and complete-C-coverage requirement. The discussion explains why preserving agreement can still create hybrid records needing cross-field checks.
- All 1,148 final positives satisfy the limited component and state-field checks. This establishes internal output consistency only; it does not establish that the quoted evidence jointly entails capability and in-state production, or resolve the `no`/`unclear` boundary.
- Public synthetic tests illustrate routing, missing-adjudicator failure, and the distinction between a production-presence category and a matching state field.

The companion `paper/adjudication_contracts_v0_3.json` contains only aggregate counts and hashes. Regenerate it with `python3 scripts/audit_adjudication_contracts.py` where the closed corpus is available. The existing `paper/audit_processing_sensitivity_v0_2.json` and the original public v0.1 package remain unchanged. Neither summary permits independent reconstruction of private individual judgments.

## Model-assistance status

A limited Z.ai trial through Claude Code used only selected public code and manuscript text, with tools disabled, concurrency one, and no automatic retry. The GLM-5.3 attempt returned HTTP 429; a minimal GLM-5.3-Flash connectivity prompt succeeded; the subsequent manuscript/code critique timed out. The timeout's server-side quota consumption is unknown. No usable critique or research annotation resulted, and none of the v0.3 findings are attributed to GLM. No further calls were made after the timeout.

A Gemini comparison runner and offline 20-case development / 300-case evaluation split were prepared. No Gemini generation or evaluation has run. Its live execution is disabled pending verification of model availability, endpoint-specific pricing, authentication, and billing/credit applicability. See [the comparison plan](cross_model_review_plan_v0_1.md). Model agreement, if later measured, cannot replace human validation.

## Verification and remaining work

The new routing analysis uses the same original pre-quote A/B/C input hashes and final-table hash as the processing audit; these fingerprints were compared directly. The final label counts remain 1,148 yes, 3,799 no, and 1,217 unclear. All 63 regression tests passed, as did the release preflight, public-release validator, manuscript content checks, and overfull-box check. All eight PDF pages were rendered and visually inspected. An exact-value credential scan of public files passed without displaying the keys; private corpus, responses, and account notes remain excluded from Git.

The independent 300-case human double-annotation gate and 200-pair entity-resolution audit remain incomplete. Target-venue review, author review, and AI-use requirements remain outstanding. This revision is an exploratory working paper, not a submitted or accepted paper.
