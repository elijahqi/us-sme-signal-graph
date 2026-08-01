# Full-census evaluation protocol v0.4

## Objective

The v0.4 extension upgrades the 1,200-pair probability sample to a complete review of all 6,164 accessible source/company-capability-state candidate pairs produced by the frozen v0.3 retrieval corpus. The goal is a several-thousand-record benchmark, not an inflated claim about several thousand SMEs.

## Units

- `query-source link`: a frozen query returning a canonical source URL;
- `source page`: one independently fetched canonical URL;
- `candidate pair`: a source/company-capability-state combination;
- `domain`: a registrable web domain; and
- `resolved business`: an entity formed only after name/domain/location resolution.

Counts at one level must not be relabeled as another. EQDP is assessed at the candidate-pair level. SME or microbusiness status is a separate evidence field and is never inferred from EQDP.

## Review extension

The existing 1,200-row probability sample remains the frozen calibration subset. Its two independent GPT-5.6-Sol reviews and third-pass adjudication are reused unchanged. The remaining 4,964 pairs receive the same provider-blind evidence extraction, Reviewer A and Reviewer B prompts, structured labels, and execution-failure retry rules. All rows with any disagreement across the ten key fields receive Reviewer C adjudication.

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

The paper must still avoid national-recall, total-supplier-population, procurement-readiness, and confirmed-SME claims.

