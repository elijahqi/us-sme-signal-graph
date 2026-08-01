# Corrected full constructed-corpus results v0.1

## Scope

This report aggregates the model-applied review of all 6,164 source–capability–state pairs constructed from 3,383 HTTP-2xx destination pages in the frozen retrieval corpus. The model assigns at most one focal business per pair. Counts are reported at their actual unit. A pair is not a page, domain, verified business, production site, supplier, or SME. Human validation and the external entity-resolution precision audit remain outstanding.

## Pair-level census

| Final label | Candidate pairs | Share |
|---|---:|---:|
| Provisional five-component producer page-support yes | 1,148 | 18.62% |
| No | 3,799 | 61.63% |
| Unclear | 1,217 | 19.74% |
| Total | 6,164 | 100% |

The 1,148 positive pairs represent 1,072 destination pages and 796 registrable domains. They do not represent 1,148 businesses. All retained positives passed the normalized literal-quote audit. Extension Reviewer A/B agreement on the legacy `eqdp` field was 4,050/4,964 (81.59%; nominal Cohen's κ = 0.609). A, B, and C were separate passes of GPT-5.6-Sol, not independent models or human experts; C was merged fieldwise only on A/B-disputed fields.

## Industry results

| Industry family | Yes | Total pairs | Positive rate |
|---|---:|---:|---:|
| Precision metal | 294 | 645 | 45.58% |
| Wood and industrial packaging | 223 | 601 | 37.10% |
| Remanufacturing | 139 | 533 | 26.08% |
| Electronics | 113 | 551 | 20.51% |
| Additive manufacturing/tooling | 126 | 715 | 17.62% |
| Polymers/composites | 110 | 622 | 17.68% |
| Contract consumer production | 61 | 582 | 10.48% |
| Industrial textiles | 50 | 605 | 8.26% |
| Semiconductor | 15 | 590 | 2.54% |
| Battery | 17 | 720 | 2.36% |

These are within-corpus model-label fractions. The selected capabilities and page ecologies are not exchangeable, so they are not estimates of industry effects, national supplier prevalence, or coverage.

## Leading exclusion reasons

| Primary reason | Nonpositive pairs | Share of 5,016 nonpositive pairs |
|---|---:|---:|
| Insufficient evidence | 1,712 | 34.13% |
| Wrong state / missing queried-state production proof | 1,102 | 21.97% |
| Capability mismatch | 568 | 11.32% |
| Distributor, reseller, or broker | 463 | 9.23% |
| Nonmanufacturing service | 324 | 6.46% |
| Source unavailable within excerpt | 290 | 5.78% |
| Foreign production only | 203 | 4.05% |
| Generic sector claim only | 133 | 2.65% |

## Entity resolution

The 1,148 positive pairs resolve under the model-assisted procedure to:

| Unit | Provisional clusters |
|---|---:|
| Operating-entity clusters | 790 |
| Corporate-group clusters | 785 |

All 11 fuzzy/alias candidate pairs received a yes/no model decision. These counts are not confidence intervals or verified entities; false-merge and false-split uncertainty remains unknown because the preregistered 200-pair external precision audit was not executed. Production sites were not equated with entity clusters.

## Corrected destination-page-only size evidence

The first size pass is invalid and excluded because it included earlier model rationales. The corrected pass uses only frozen destination-page visible text. On the corrected positive corpus, 446 pair contexts contain a size-related term and 702 are automatic screen negatives. Thirty-nine pair-level signals map to 29 provisional operating-entity clusters. Entity-level A/B/C review produced the following narrow screen results.

| Entity-level result | Provisional clusters | Share of 790 |
|---|---:|---:|
| Nonhistorical numerical employee evidence | 23 | 2.91% |
| Wholly within one descriptive employee band | 14 | 1.77% |
| Study band 10–99 | 10 | 1.27% |
| Study band 100–499 | 2 | 0.25% |
| Study band 500+ | 2 | 0.25% |
| Numerical bound/range crossing bands | 9 | 1.14% |
| Current owner-only support | 0 | 0% |
| Named-program or explicit SAM/SBA page representation | 3 | 0.38% |
| External SBA-small verification | Not performed | — |
| Descriptive employee band unknown | 767 | 97.09% |

The rows are nested or overlapping, not additive: 23 numerical-evidence clusters comprise 14 single-band and nine cross-band cases; the 14 single-band cases comprise 10, two, and two clusters in the listed bands; one single-band cluster also has an explicit federal page representation.

The study's employee bands are descriptive categories, not SBA legal definitions. The three named/explicit federal-representation clusters comprise two in the explicit SAM/SBA page-claim category and one in the named federal-program page-claim category. These remain page representations, not independent current determinations. The screen measures only these capability/location destination pages and cannot estimate firm-size-data availability across the public web. On 29 screen-positive clusters, A/B raw agreement was 89.66% (nominal κ = 0.859) for descriptive band and 100% for federal-representation category. Five semantic disagreements received fieldwise C adjudication. All 29 quote-audit-eligible reviews passed; quote audit was not applicable to 761 automatic screen negatives.

## Integrity anchors

- Full 6,164-pair final table SHA-256: `24bd429ac9b56cc2f02e693c9943f940608c896f9744a586cddac27a7d83497a`.
- Positive pair-to-entity mapping SHA-256: `93e202f3c6f91140c400150e2464e1035b92a67a3931167d5a579f3a6ad3951c`.
- Provisional operating-entity file SHA-256: `353f48166f561b9d4dd8d80f72ad040b20205e25c3786a9a464cdb81bf5d09db`.
- Pair-level corrected size table SHA-256: `115e973c6608d1e220c85548ff5efb9266f711d890da9882ff9f7a6daf17ce09`.
- Final 790-cluster size-screen table SHA-256: `aae83ef9e5d7ceb60c15e761a56962faaa752ea4f57d82b54bf078386704cf11`.

Private row-level files and fetched page bodies are excluded from public artifacts. A row-free exploratory aggregate package is staged at `release/public/long-tail-evidence-audit-v0.1-exploratory`; its fail-closed validator excludes company rows, URLs, page text, quotes, rationales, and provider payload content. The existing `release/public/v0.2.0-rc1` is an earlier semiconductor pilot. The new package is versioned in the working tree but has not been externally published.
