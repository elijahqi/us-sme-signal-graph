# Brave × You uplift pilot: v0.2.0-rc1 results

## Outcome

The union of Brave and You materially increased the verified supplier candidate set, but the pilot did not clear every preregistered gate. The correct decision is to publish a reviewable release candidate and continue human validation—not to run an unattended full expansion.

## Frozen retrieval

| Metric | Brave | You | Union / overlap |
|---|---:|---:|---:|
| Queries | 24 | 24 | same frozen strings |
| Top-k per query | 10 | 10 | 480 raw incidences |
| Unique canonical URLs | 219 | 220 | 265 union |
| URL intersection | — | — | 174 |
| URL Jaccard | — | — | 65.66% |

Provider responses were used transiently. The public repository contains aggregate counts and provider-neutral source facts, not search payloads, snippets, ranks, or provider-to-URL mappings.

## Review and verification

- 265 original URLs were fetched through a provider-neutral, robots-aware client.
- Domain deduplication produced 186 review rows.
- Reviewer-1 adjudicated the 75 direct-company rows with semiconductor and manufacturing signals.
- Every one of the 42 first-party lenient positives entered independent-source verification.
- Content-level review rejected generic shells, security pages, non-U.S. entities, distributors, and baseline duplicates.
- 34 rows satisfied strict supplier validity.
- 30 were net-new relative to the 50-company SIA Equipment/Materials supplier baseline.
- 11 strict suppliers had non-authoritative size evidence below a plausible applicable threshold and are labeled `probable_sme`.
- 0 are labeled `confirmed_sme`; affiliation and authoritative status evidence remain unresolved.

## Provider contribution

| Strict net-new arm | Companies |
|---|---:|
| Brave | 27 |
| You | 22 |
| Brave ∩ You | 19 |
| Brave only | 8 |
| You only | 3 |
| Brave ∪ You | 30 |

The union adds three strict suppliers beyond Brave alone and eight beyond You alone. This supports a real union uplift. It does not satisfy the preregistered requirement that each provider contribute at least five unique strict positives, because You contributed three.

## Precision and lift

- Strict precision within the 75-row high-signal review scope: **34/75 = 45.3%**.
- Wilson 95% interval: **34.6%–56.6%**.
- Net-new strict suppliers: **30**.
- Lift against the known-incomplete 50-company supplier baseline: **60%**.

The lift denominator is not an estimate of the total U.S. supplier population. It is the frozen SIA comparison set.

## Gate decision

| Preregistered gate | Result |
|---|---|
| At least 25 net-new strict suppliers | Pass: 30 |
| Wilson precision lower bound at least 0.55 | Fail: 0.346 |
| At least five unique strict positives per provider | Fail: You=3 |
| Annotation agreement at least 0.70 | Not measured |
| Entity-resolution audit precision at least 0.95 | Not measured |
| Rights/robots blocker | Public boundary passes; individual inaccessible pages were not accepted |

`full_run_authorized_by_evidence` remains false.

## What this result proves—and does not prove

It proves that dual search can discover verified U.S. semiconductor supplier candidates that are absent from a frozen public baseline, and that independent-source and entity-resolution gates are necessary. It does not prove complete coverage, model uplift, external adoption, SME certification, national economic impact, or a supplier-customer relationship for any company.

The next scientific step is a blinded second annotation of at least 20% of the complete 186-row pack, followed by agreement and entity-resolution audits. The next evidence step is independent reproduction or use by an outside researcher or institution.
