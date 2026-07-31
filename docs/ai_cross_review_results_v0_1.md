# AI cross-review results v0.1

## Bottom line

The complete 1,200-record probability sample has been reviewed in two independent, provider-blind GPT-5.6-Sol passes and every key-field disagreement has received a third adjudication pass. The final result contains **220 evidence-qualified domestic producer (EQDP) company-capability-state pairs**, 639 negative pairs, and 341 unresolved pairs. The sampling-weighted EQDP rate is **18.35%** with a stratified bootstrap 95% interval of **16.33%–20.35%**.

This is evidence that the cross-industry search process surfaced a meaningful number of source pages that support a specific manufacturing capability and production presence in the queried state. It is not evidence of 220 distinct companies, 220 SMEs, procurement qualification, available production capacity, or national supplier coverage.

## Review design

- Probability sample: 1,200 company-capability-state pairs from 6,164 eligible pairs.
- Reviewer A: GPT-5.6-Sol, conservative evidence-first prompt, 1,200 rows.
- Reviewer B: GPT-5.6-Sol, independently shuffled batches and adversarial-falsification prompt, 1,200 rows.
- Adjudication: all 631 rows with any disagreement across ten key fields received Reviewer C re-evaluation from the same frozen evidence.
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
| Yes | 220 | 18.33% |
| No | 639 | 53.25% |
| Unclear | 341 | 28.42% |

The weighted yes rate is 18.35%. Positive rows represent 217 unique source pages and 200 unique registrable domains. Repeated domains can legitimately represent different capability-state pairs.

### Positive production presence

| Production evidence class | Positive pairs |
|---|---:|
| Industrial facility confirmed | 145 |
| Job shop or workshop confirmed | 73 |
| Owner/home production confirmed | 2 |

All 220 positive rows passed a deterministic state check: the adjudicated production state matched the queried state.

### What the evidence says about microbusinesses

| Supported scale band | Positive pairs |
|---|---:|
| Owner-only/nonemployer | 0 |
| Micro employer, 1–9 | 1 |
| Small employer, 10–99 | 4 |
| 100+ supported | 0 |
| Unknown | 215 |

The search process surfaced small-looking and owner-operated businesses, but public web evidence almost never proved employee count or formal nonemployer status. Therefore the present study supports **producer discovery**, not a claim that it discovered a known number of SMEs or sole proprietors. This missing-size-evidence problem is itself a central finding and motivates linkage to authoritative registries or direct business confirmation.

### Positive legal form

| Legal form | Positive pairs |
|---|---:|
| Corporation | 65 |
| LLC | 16 |
| Other supported | 4 |
| Unknown | 135 |
| Sole proprietor explicitly supported | 0 |

Absence of an explicit sole-proprietor label must not be interpreted as proof that none of the producers are sole proprietors. It means the frozen pages did not establish that legal form.

## Industry variation

| Industry family | Sample rows | Final yes | Weighted yes rate |
|---|---:|---:|---:|
| Precision metal | 125 | 57 | 45.61% |
| Wood and industrial packaging | 117 | 34 | 29.03% |
| Electronics | 108 | 26 | 24.09% |
| Remanufacturing | 103 | 22 | 21.34% |
| Polymers and composites | 122 | 25 | 20.50% |
| Additive manufacturing/tooling | 139 | 28 | 20.16% |
| Industrial textiles | 117 | 12 | 10.23% |
| Contract consumer products | 113 | 11 | 9.72% |
| Battery | 141 | 3 | 2.13% |
| Semiconductor | 115 | 2 | 1.74% |

The low semiconductor and battery rates do not prove those sectors lack domestic suppliers. They show that this broad web-search and evidence protocol rarely established a capability-specific producer **and production presence in the queried state** for those advanced-sector tasks. Precision metal and local production services were far easier to verify from public pages.

## Query-intent association

The sampling design assigns a candidate to the micro/local stratum if it was found by a micro/local query, then to small-batch if found there but not micro/local, and otherwise direct. Candidates can appear through multiple intents, so these are associations and not causal provider-arm comparisons.

| Sampling stratum | Sample rows | Yes | Weighted yes rate |
|---|---:|---:|---:|
| Direct only | 275 | 44 | 15.96% |
| Micro/local observed | 586 | 132 | 22.55% |
| Small-batch observed without micro/local | 339 | 44 | 13.03% |

Micro/local-observed candidates had the highest evidence-qualified rate. A future controlled experiment is needed before claiming that micro/local wording causes the improvement.

## Why candidates failed

The leading final exclusion reasons were:

| Exclusion reason | Non-positive pairs |
|---|---:|
| Insufficient evidence | 351 |
| Wrong state / no queried-state production proof | 218 |
| Capability mismatch | 109 |
| Source unavailable | 75 |
| Distributor/reseller/broker | 67 |
| Nonmanufacturing service | 62 |
| Foreign production only | 33 |
| Generic sector claim only | 29 |
| Other reasons | 36 |

The dominant problem was not merely irrelevant search results. It was the inability to prove all required elements—especially state-level production—from public evidence.

## Citation and evidence QA

- 220/220 positive rows had an adjudicated production state matching the queried state.
- 203/220 positive evidence quotes could be traced as normalized exact substrings of the frozen evidence excerpt.
- 17/220 quotes contained model compression, concatenation, or light paraphrase and are marked `quote_audit_pass=false`. They must not be used as verbatim quotations in a paper or exhibit without returning to the frozen page.
- The row-level corpus, model outputs, and source pages remain private. Public artifacts may include methods, schemas, aggregate tables, hashes, and approved illustrative cases only.

## What can and cannot be claimed

### Supported by this first version

- A 960-query, cross-industry Brave/You search process produced 4,638 unique source URLs.
- A provider-blind, weighted 1,200-record sample yielded an estimated 18.35% evidence-qualified domestic producer rate.
- Public evidence quality varies sharply by industry; local production services are easier to verify than advanced-sector capability-and-location pairs.
- Micro/local-observed candidates were more likely to pass than the other descriptive strata, but the design is not causal.
- Public pages are inadequate for reliable named-business micro/nonemployer classification in most cases.

### Not supported yet

- The number or share of all U.S. suppliers discovered.
- That 220 unique companies were found; the unit is a company-capability-state pair.
- That most positives are SMEs, microbusinesses, sole proprietors, procurement-ready, available, or interested.
- That Brave or You has higher qualified-supplier precision; provider incidence was not retained through human review under the ordinary Brave terms.
- Human expert validation, user adoption, economic impact, or improved procurement outcomes.

## Required next validation

The strongest next step is not another search expansion. It is a domain-expert audit of a stratified subset containing positives, negatives, and unclear cases, followed by authoritative size/affiliate verification and a small real-user supplier-scouting pilot. Until that occurs, this document is an **AI cross-review result**, not external validation.

