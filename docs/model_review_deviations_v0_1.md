# Model-review and analysis deviations v0.1

This log separates the executed exploratory AI review from the original human-validation plan.

## MRD-001 — Human audit replaced by exploratory same-model passes

- Original plan: provider-blind human review, at least 300 independently double annotated cases, EQDP κ at least 0.70, and a presampled entity-resolution audit of at least 200 merge/non-merge pairs with precision at least 0.95.
- Executed exploratory analysis: Reviewer A, Reviewer B, and Reviewer C were separate GPT-5.6-Sol passes. No external human or domain-expert labels were collected.
- Consequence: agreement measures prompt/order stability, not human reliability or label validity. The v0.3 human and entity-resolution gates remain unmet.

## MRD-002 — Full-corpus amendment timing

- Protocol v0.4 was committed as `e1b5bfe` after formal retrieval and the 1,200-pair AI calibration, but before review of the remaining 4,964 pairs.
- Consequence: v0.4 is a prospective amendment for the extension, not a pre-retrieval preregistration and not a substitute for v0.3.

## MRD-003 — Whole-record C overwrite corrected to fieldwise adjudication

- Initial analysis selected Reviewer C's entire record whenever A and B disagreed on any key field.
- Audit finding: C changed an A/B-agreed primary EQDP label from `no` to `unclear` in 283 extension rows and 38 calibration rows. No `yes` count changed, but no/unclear and exclusion distributions were distorted.
- Correction: A/B-agreed fields are locked; only A/B-disputed fields use C. The rule is applied to producer, pair-size, and entity-size adjudication. All downstream aggregates and hashes are regenerated.

## MRD-004 — Quote-audit denominator corrected

- Initial entity-size summary counted 774 automatic screen negatives with no quote as quote-audit passes.
- Correction: quote audit is `not_applicable` for automatic screen negatives. In the superseded 805-cluster run, the eligible denominator was 31 rather than 805. After literal-positive correction and full regeneration, the final denominator is 29 eligible reviews: 29 passed, zero failed, and 761 are not applicable.
- The same correction applies at pair-size level: 39 signal-bearing pair quotes are eligible and pass; 1,109 insufficient rows with empty quotes are `not_applicable`, not passes.

## MRD-005 — Retrieval overlap terminology corrected

- Initial reports called `sum(intersection) / sum(union) = 0.6381` a query-level Jaccard without distinguishing pooling.
- Correction: it is the pooled query-URL Jaccard. The unweighted macro mean of 960 per-query Jaccards is 0.6555. Both may be reported with explicit definitions.

## MRD-006 — Positive literal-quote re-audit

- Initial full-corpus result retained 71 positive rows whose evidence quotes were compressed, concatenated, or paraphrased rather than normalized literal substrings.
- Corrective analysis: blind A/B re-audit over the same frozen evidence excerpts with a mandatory contiguous literal quote for any positive; semantic disagreements received fieldwise C. Thirty-one rows were downgraded to unclear, leaving 1,148 provisional positive pair labels with 1,148 literal-quote passes. Entity and size analyses were regenerated from that table.

## MRD-007 — Probability-sample design and bootstrap implementation differ from protocol wording

- Protocol v0.3 said the 1,200-row probability sample would balance industry, intent, state, provider incidence, and rank band, and that confidence intervals would use stratified bootstrap resampling of query units.
- Executed sampler: proportional allocation across 30 industry-family × primary-intent strata, deterministic row selection within strata, and inverse-inclusion weights. State, provider incidence, and rank band were not sampling strata.
- Executed interval: 10,000 pair-row resamples within the implemented sampling strata, not query-unit resamples.
- Consequence: the weighted 17.84% positive-label estimate and 15.84%–19.86% bootstrap interval are retained only as exploratory diagnostics. The interval is not called protocol-conformant or confirmatory. Exact full-corpus model-label counts supersede sample inference for description of the 6,164 constructed pairs.
