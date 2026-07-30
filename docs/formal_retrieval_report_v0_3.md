# Formal retrieval report v0.3

## Status

The frozen 960-query Brave/You retrieval run and independent original-page fetch stage are complete. This report is limited to retrieval and source-access outcomes. It does **not** report businesses, qualified suppliers, microbusinesses, or SMEs; those labels require the preregistered provider-blind human review.

## Frozen execution

- Protocol anchor: Git commit `9fb6d4280ec42aa858f8219c4f4dc310a880f41a`.
- Query lattice: 40 capabilities × 8 states × 3 intents = 960 exact queries.
- Requested results: 10 per provider per query.
- Brave returned rows: 9,590; one query failed after the frozen retries.
- You returned rows: 9,600; no failed query.
- The incomplete Brave query was `LTQ0850`, “Ohio manufacturer small batch supplement capsule tablet contract manufacturing.” It is retained as a provider failure and is not selectively rerun.
- Provider raw payloads retained: 0. Brave results were processed transiently.

## Retrieval overlap

Across the 960 paired queries:

| Metric | Count |
|---|---:|
| Query-level URL intersection, summed | 7,475 |
| Query-level URL union, summed | 11,715 |
| Query-level URL Jaccard | 63.81% |
| Cross-query unique canonical source URLs | 4,638 |
| Query-to-source links | 11,715 |

The 4,638 URLs are source pages, not unique companies. A page may be a directory, association, news item, government page, marketplace, duplicate business representation, irrelevant result, or unavailable source.

### Overlap by query intent

| Intent | Queries | Brave rows | You rows | URL intersection | URL union | Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| Direct | 320 | 3,190 | 3,200 | 2,537 | 3,853 | 65.84% |
| Micro/local | 320 | 3,200 | 3,200 | 2,492 | 3,908 | 63.77% |
| Small-batch/job-shop | 320 | 3,200 | 3,200 | 2,446 | 3,954 | 61.86% |

Lower overlap for small-batch and micro/local queries is consistent with greater provider complementarity in long-tail retrieval. It does not yet establish higher qualified-producer yield.

### Overlap by industry family

| Industry family | Queries | URL intersection | URL union | Jaccard |
|---|---:|---:|---:|---:|
| Semiconductor | 96 | 789 | 1,131 | 69.76% |
| Contract consumer products | 96 | 780 | 1,130 | 69.03% |
| Remanufacturing | 96 | 781 | 1,139 | 68.57% |
| Wood and industrial packaging | 96 | 771 | 1,149 | 67.10% |
| Polymers and composites | 96 | 751 | 1,169 | 64.24% |
| Precision metal | 96 | 746 | 1,174 | 63.54% |
| Electronics | 96 | 739 | 1,181 | 62.57% |
| Industrial textiles | 96 | 731 | 1,189 | 61.48% |
| Battery | 96 | 699 | 1,221 | 57.25% |
| Additive manufacturing and tooling | 96 | 688 | 1,232 | 55.84% |

These are query-level retrieval overlaps. They do not rank industries by supplier coverage.

## Independent source access

Every union URL was independently processed under the same robots/HTTP workflow. Cross-query duplicates were fetched once.

| Outcome | Count |
|---|---:|
| Unique source URLs processed | 4,638 |
| HTTP 2xx | 3,383 |
| HTTP 403 | 1,018 |
| HTTP 404 | 57 |
| Other HTTP/status 0 | 180 |
| Robots explicitly disallowed | 129 |
| Python-enforced hard timeout | 9 |

An inaccessible or disallowed page remains in the retrieval denominator and cannot become a positive without permitted independent evidence. Source failures are not silently dropped.

## Deviations and integrity

Engineering deviations before or between complete checkpoints are documented in `experiments/long_tail_benchmark/deviations.md`. No affected partial batch entered the completed aggregate table. The final aggregate table contains every frozen query ID exactly once, with no extras. Source IDs and canonical URLs are unique, and every query-source link resolves to an existing source record.

The closed corpus stores independently fetched source metadata, permitted source bodies, hashes, and query-to-source links. It does not store Brave or You raw search payloads. The paper package will publish methods, queries, schemas, aggregate statistics, and integrity manifests—not a row-level company dataset.

## Next stage

The retrieval run does not answer whether either intent finds more qualified micro-producers. The next preregistered step is provider-blind human review of a reproducible 1,200-record probability sample, with at least 300 independently double annotated. Only that review can estimate:

- evidence-qualified domestic producers per 1,000 source URLs;
- owner-only, micro-employer, small-employer, and unknown scale distributions;
- noise and exclusion reasons;
- review minutes per qualified producer; and
- differences by industry, state, and query intent.

