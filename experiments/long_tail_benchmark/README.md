# Cross-industry long-tail manufacturing benchmark

This directory freezes the design inputs for study protocol v0.3. The generated lattice contains 960 exact queries. Each is sent to Brave and You with ten web results requested, targeting up to 9,600 ranked results per provider before deduplication. No formal result collection begins until the inputs and generated lattice are committed and hashed.

## Inputs and generated artifact

- `capability_set_v0_2.csv`: 40 capabilities in ten industry families.
- `geographies_v0_1.csv`: eight states across four Census regions.
- `intent_templates_v0_1.csv`: direct, small-batch/job-shop, and micro/local intents.
- `scripts/build_query_lattice.py`: deterministic Cartesian-product generator.
- `query_lattice_v0_2.csv`: generated 960-query freeze artifact.
- `annotation_schema_v0_2.csv`: provider-blind entity and qualification review.
- `query_aggregate_schema_v0_1.csv`: rights-safe per-query aggregate output.

Run:

    python3 scripts/build_query_lattice.py
    python3 scripts/build_query_lattice.py --check

## Search parameters

- Brave: `count=10`, `country=US`, `search_lang=en`, `safesearch=moderate`, `spellcheck=false`, no summary.
- You: `count=10`, `country=US`, `language=EN`, `safesearch=moderate`, ordinary web search without live-crawl candidate generation.
- Only web results are counted. Queries are identical across providers.
- Provider order is randomized by query and paired calls should finish within 15 minutes.

## Rights-aware collection

Brave ordinary terms expressly permit only transient operational storage of Search Results unless an Order Form grants storage rights. You's public general terms do not contain the same express search-database ban, but account-specific or supplemental API terms and third-party content rights still apply. Until reviewed, raw titles, snippets, ranks, and payloads are not retained as the research dataset.

The collector should compute provider aggregates transiently, independently fetch original publisher URLs, and persist only rights-reviewed original-source provenance and derived business facts in the closed research corpus. Keeping a Brave raw response only on a local machine is still storage and is not permitted by the ordinary terms. The default paper package contains code, frozen queries, aggregate tables, schemas, and manifests; it does not publish a row-level company dataset, provider payloads, or fetched third-party page text.

Under the ordinary-plan design, provider comparison stops at query-level URL/domain counts and overlap. The later human-reviewed union corpus is provider-blind; the study does not calculate provider-specific EQDP precision or provider-marginal qualified entities without documented storage rights.

Brave batches must use an operating-system temporary directory rather than a repository path. Validate the batch aggregate and independent-fetch ledger, then delete raw JSON, titles, snippets, ranks, and provider-attribution rows immediately. The durable deletion ledger stores counts and hashes only. Retaining Brave raw responses until the paper is written requires documented Storage Rights.

