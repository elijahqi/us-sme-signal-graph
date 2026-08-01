# Full constructed-corpus evaluation protocol v0.4

**Status and timing:** exploratory AI-only amendment, committed as `e1b5bfe` after the retrieval run and the 1,200-pair AI calibration, but before launching the remaining 4,964-pair full-corpus extension. It is not a replacement for the unexecuted human-validation gates in protocol v0.3 and is not described as a preregistration.

## Objective

The v0.4 extension applies a model-review protocol to all 6,164 source/capability/state pairs constructed from HTTP-2xx destination pages in the frozen v0.3 retrieval corpus. The goal is a several-thousand-record exploratory evidence audit, not an inflated claim about several thousand businesses or SMEs.

## Units

- `query-source link`: a frozen query returning a canonical source URL;
- `source page`: one destination URL fetched directly, separately from the search-provider response;
- `candidate pair`: one canonical source URL crossed with one capability and queried state inherited from at least one retrieving query; the model assigns at most one focal business name to that pair during review;
- `domain`: a registrable web domain; and
- `resolved business`: an entity formed only after name/domain/location resolution.

Counts at one level must not be relabeled as another. EQDP is assessed at the candidate-pair level. SME or microbusiness status is a separate evidence field and is never inferred from EQDP.

## Review extension

The existing 1,200-row probability sample remains the frozen AI calibration subset. Its two GPT-5.6-Sol passes and third-pass adjudication are reused, subject to fieldwise merge correction: A/B-agreed key fields are locked and Reviewer C is used only for key fields on which A and B disagree. The remaining 4,964 pairs receive the same provider-blind evidence criteria, structured labels, and execution-failure retry rules. All rows with any disagreement across the ten key fields receive Reviewer C, but C cannot overwrite an A/B-agreed key field.

The census evidence contains no provider, search rank, or previous sample decision. Reviewers may use only the frozen original-page excerpt. The same model is used in independent prompt/order passes; this measures repeat-evaluation stability, not human expert agreement.

## Analysis

The full-census result reports exact observed counts within the frozen search-visible corpus. It no longer needs probability weights to describe those 6,164 pairs. The original probability sample remains useful for checking whether sample-weighted estimates anticipated the census result.

Primary results:

- final EQDP yes/no/unclear counts over all 6,164 pairs;
- unique positive source pages and domains;
- resolved-business count after entity audit;
- industry, state, capability, and query-intent incidence;
- production-presence classes;
- exclusion-reason distribution;
- explicit scale/legal-form evidence; and
- quote and state QA.

The paper must still avoid national-recall, total-supplier-population, procurement-readiness, confirmed-SME, human-validation, and benchmark-ground-truth claims. Entity counts remain provisional until the v0.3 external precision audit is performed.

