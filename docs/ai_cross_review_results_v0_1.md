# AI cross-review calibration results v0.2

**Supersession note:** fieldwise adjudication and mandatory literal-quote re-audit supersede the initial whole-record merge reported in v0.1. The corrected 1,200-row calibration numbers below are current. These are same-model exploratory labels, not human validation.

## Bottom line

The complete 1,200-record probability sample has been reviewed in two provider-blind GPT-5.6-Sol passes; A/B-agreed key fields are locked and disputed fields receive a third same-model pass. Literal-quote re-audit downgraded six provisional positives. The corrected result contains **214 provisional EQDP page-support pairs**, 677 no pairs, and 309 unclear pairs. The sampling-weighted positive-label rate is **17.84%** with a stratified bootstrap 95% interval of **15.84%–19.86%**.

This is a model-applied estimate within the sample of constructed pairs. It is not evidence of 214 distinct companies, SMEs, procurement qualification, available production capacity, national supplier coverage, or factual verification of page claims.

## Review design

- Probability sample: 1,200 company-capability-state pairs from 6,164 eligible pairs.
- Reviewer A: GPT-5.6-Sol, conservative evidence-first prompt, 1,200 rows.
- Reviewer B: GPT-5.6-Sol, independently shuffled batches and adversarial-falsification prompt, 1,200 rows.
- Adjudication: all 631 rows with any disagreement across ten key fields received Reviewer C re-evaluation from the same frozen evidence; only A/B-disputed fields use C in the corrected merge.
- Search provider and rank were absent from all review inputs.
- Browsing and tools were disabled; reviewers could use only frozen original-page excerpts.
- The model, evidence generation, prompts, schema, and batch size were frozen before the full run.

These are independent passes of the **same model**, not three independent human experts. Agreement statistics measure prompt/order stability under blinded repeat evaluation; they must not be described as human inter-annotator agreement or external expert validation.

### Execution reliability

| Stage | Batches | Rows | Retried batches | Permanent failures |
|---|---:|---:|---:|---:|
| Reviewer A | 120 | 1,200 | 2 | 0 |
| Reviewer B | 120 | 1,200 | 3 | 0 |
| Reviewer C | 64 | 631 | 2 | 0 |

Execution failures were retried and never converted to an `unclear` label.

## A/B stability

| Field | Agreement | Raw agreement | Cohen's kappa |
|---|---:|---:|---:|
| Final EQDP | 967/1,200 | 80.58% | 0.638 |
| Identity | 1,141/1,200 | 95.08% | see machine summary |
| Direct producer | 1,135/1,200 | 94.58% | see machine summary |
| Capability match | 1,116/1,200 | 93.00% | see machine summary |
| Queried-state production presence | 971/1,200 | 80.92% | see machine summary |
| Commercial offering | 1,119/1,200 | 93.25% | see machine summary |
| Scale band | 1,188/1,200 | 99.00% | see machine summary |
| Legal form | 1,165/1,200 | 97.08% | see machine summary |

Queried-state production presence was the main substantive source of disagreement. A business could clearly offer the requested product but still fail EQDP because the page did not prove that production occurred in the queried state.

## Final EQDP outcome

| Final label | Sample count | Share of sample |
|---|---:|---:|
| Yes | 214 | 17.83% |
| No | 677 | 56.42% |
| Unclear | 309 | 25.75% |

The weighted yes rate is 17.84%. Positive rows represent 211 unique destination pages and 194 unique registrable domains. Repeated domains can legitimately represent different capability-state pairs.

### Positive production presence

| Production evidence class | Positive pairs |
|---|---:|
| Industrial facility confirmed | 141 |
| Job shop or workshop confirmed | 71 |
| Owner/home production confirmed | 2 |

All 214 positive rows passed an internal state-field check: the model-produced production state matched the queried state. This is not external factual verification.

### Superseded general-review scale fields

The general-review scale fields are not used as firm-size results. The corrected destination-page-only size pipeline and entity-level currentness/scope review are reported in `docs/full_census_results_v0_1.md`.

### Positive legal form

| Legal form | Positive pairs |
|---|---:|
| Corporation | 63 |
| LLC | 16 |
| Other supported | 4 |
| Unknown | 131 |
| Sole proprietor explicitly supported | 0 |

Absence of an explicit sole-proprietor label must not be interpreted as proof that none of the producers are sole proprietors. It means the frozen pages did not establish that legal form.

## Industry variation

| Industry family | Sample rows | Final yes | Weighted yes rate |
|---|---:|---:|---:|
| Precision metal | 125 | 57 | 45.61% |
| Wood and industrial packaging | 117 | 33 | 28.18% |
| Electronics | 108 | 25 | 23.16% |
| Remanufacturing | 103 | 20 | 19.40% |
| Polymers and composites | 122 | 25 | 20.50% |
| Additive manufacturing/tooling | 139 | 27 | 19.44% |
| Industrial textiles | 117 | 11 | 9.40% |
| Contract consumer products | 113 | 11 | 9.72% |
| Battery | 141 | 3 | 2.13% |
| Semiconductor | 115 | 2 | 1.74% |

These sample-weighted fractions differ across selected tasks but are not estimates of national industry effects or factual producer prevalence.

## Query-intent association

The sampling design assigns a candidate to the micro/local stratum if it was found by a micro/local query, then to small-batch if found there but not micro/local, and otherwise direct. Candidates can appear through multiple intents, so these are associations and not causal provider-arm comparisons.

| Sampling stratum | Sample rows | Yes | Weighted yes rate |
|---|---:|---:|---:|
| Direct only | 275 | 43 | 15.60% |
| Mixed ownership/locality observed | 586 | 128 | 21.84% |
| Small-batch observed without mixed ownership/locality | 339 | 43 | 12.68% |

Mixed ownership/locality-observed pairs had the highest descriptive weighted positive-label rate. A future controlled experiment is needed before making any causal wording claim.

## Why candidates failed

The leading final exclusion reasons were:

| Exclusion reason | Non-positive pairs |
|---|---:|
| Insufficient evidence | 355 |
| Wrong state / no queried-state production proof | 219 |
| Capability mismatch | 110 |
| Source unavailable | 75 |
| Distributor/reseller/broker | 67 |
| Nonmanufacturing service | 62 |
| Foreign production only | 33 |
| Generic sector claim only | 29 |
| Other reasons | 36 |

The largest model-assigned categories were insufficient excerpt evidence and missing queried-state production support.

## Citation and evidence QA

- 214/214 positive rows had a model-produced production state matching the queried state.
- 214/214 positive evidence quotes passed the normalized literal-substring audit after re-audit.
- These checks establish internal and string consistency, not factual truth or human validity.
- The row-level corpus, model outputs, and source pages remain private. Public artifacts may include methods, schemas, aggregate tables, hashes, and approved illustrative cases only.

## What can and cannot be claimed

### Supported by the corrected exploratory version

- A 960-query Brave/You process produced 4,638 unique destination URLs, of which 3,383 returned HTTP 2xx.
- In the provider-blind 1,200-pair sample, the model-applied weighted positive-label rate was 17.84% (95% bootstrap 15.84%–19.86%).
- The result is corpus-conditional and exploratory; selected task fractions and query-intent associations are descriptive only.
- Firm-size claims must use the separately regenerated destination-page-only entity-size screen.

### Not supported yet

- The number or share of all U.S. suppliers discovered.
- That 214 unique companies were found; the unit is a source–capability–state pair with at most one model-assigned focal business.
- That most positives are SMEs, microbusinesses, sole proprietors, procurement-ready, available, or interested.
- That Brave or You has higher qualified-supplier precision; provider incidence was not retained through human review under the ordinary Brave terms.
- Human expert validation, user adoption, economic impact, or improved procurement outcomes.

## Required next validation

The strongest next step is not another search expansion. It is a domain-expert audit of a stratified subset containing positives, negatives, and unclear cases, followed by the preregistered entity-resolution precision audit, authoritative size/affiliate verification, and a small real-user producer-scouting pilot. Until that occurs, this document is an **exploratory same-model calibration result**, not a validated benchmark or external validation.

