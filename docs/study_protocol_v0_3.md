# Study protocol v0.3: mapping the search-visible U.S. manufacturing long tail

**Status:** frozen pre-retrieval protocol and original human-validation plan. The 960-query retrieval was executed as specified, but the downstream human double-annotation, reviewer-time, and 200-pair entity-resolution precision gates in Sections 7–9 were not executed. The later full-corpus GPT-5.6-Sol review is an exploratory AI-only amendment documented in `docs/full_census_protocol_v0_4.md`; it must not be represented as satisfying this protocol's human-validation gates.
**Frozen design inputs:** `experiments/long_tail_benchmark/`  
**Annotation instructions:** `docs/external_annotator_guide_v0_3.md`

## 1. Objective and paper framing

**Working title:** *Mapping the Search-Visible Long Tail of U.S. Manufacturing: A Cross-Industry, Provenance-Aware Comparison of Brave and You Search*

This study measures how two web-search channels expose small, micro, owner-operated, and otherwise low-visibility U.S. producers across diverse manufacturing capabilities. It does not claim to enumerate every U.S. manufacturer, replace government or commercial supplier systems, or infer procurement readiness. It measures the **search-visible population produced by a frozen query lattice**, the providers' complementarity, the evidence needed to verify a direct producer, and the degree to which smaller businesses remain difficult to identify.

The study uses Brave Search MCP and You Search MCP only for candidate discovery. Search snippets are not factual evidence. Every positive record must be supported by independently fetched original business, government, or industry pages.

### Research questions

- **RQ1 — Retrieval complementarity:** How many URLs and business domains does each provider expose per frozen query, and how much do the providers overlap at retrieval time?
- **RQ2 — Long-tail visibility:** What share of verified producers falls into owner-only/nonemployer, micro-employer, small-employer, and larger size bands, and how often is size or legal form impossible to verify?
- **RQ3 — Query strategy:** How do direct, small-batch/job-shop, and micro/local query intents change producer yield, noise, source type, and business-size distribution?
- **RQ4 — Heterogeneity and cost:** Within the provider-blind union corpus, how do discovery yield, verification precision, and reviewer minutes vary across industry families, states, query intent, and rank band?

## 2. Scope and query lattice

The benchmark contains 40 capability definitions in ten industry families:

1. semiconductor equipment and subsystems;
2. battery and energy-storage manufacturing;
3. precision machining and metal fabrication;
4. electronics contract manufacturing;
5. plastics, rubber, and composites;
6. additive manufacturing and rapid tooling;
7. industrial textiles and sewn products;
8. wood products and custom industrial packaging;
9. food, beverage, cosmetics, and nutraceutical contract production; and
10. industrial repair and remanufacturing.

This mix deliberately contains both advanced-manufacturing capabilities and activities commonly supplied by micro-enterprises or owner-operated shops. The industry families are analytic strata, not a claim that they exhaust U.S. manufacturing.

Eight states are frozen before retrieval, with two from each Census region and a mix of advanced and legacy manufacturing bases:

- Northeast: Massachusetts and Pennsylvania;
- Midwest: Michigan and Ohio;
- South: North Carolina and Texas; and
- West: Arizona and California.

Each capability-state pair receives three frozen query intents:

- `direct`: ordinary manufacturer search;
- `small_batch`: custom, job-shop, contract, or short-run search; and
- `micro_local`: small-business, family-owned, owner-operated, or local-workshop search.

The deterministic lattice therefore contains `40 capabilities × 8 states × 3 intents = 960 queries`. Each exact query is sent unchanged to both providers with ten web results requested. The target maximum is **9,600 ranked results per provider** and 19,200 total provider-result rows before within-provider and cross-provider deduplication. Actual returned counts, missing calls, duplicate rates, and provider errors are study outcomes.

Breadth across capability, geography, and intent is used instead of attempting to paginate a single query thousands of results. Brave web search returns at most 20 results per page and has limited offsets; deep pages also create unstable and highly repetitive samples. No result-aware query rewriting, company-name query, manual rescue query, provider-specific synonym, or post-result capability substitution is allowed in the primary run.

The frozen components are:

- `capability_set_v0_2.csv`;
- `geographies_v0_1.csv`;
- `intent_templates_v0_1.csv`;
- `scripts/build_query_lattice.py`; and
- the generated `query_lattice_v0_2.csv`.

An external domain reviewer may flag an incoherent capability before retrieval. Any accepted correction creates a new version and resets the freeze. After formal retrieval begins, changes are deviations and cannot replace the intention-to-test result.

## 3. Formal retrieval and rights boundary

Brave parameters are `count=10`, `country=US`, `search_lang=en`, `safesearch=moderate`, `spellcheck=false`, with no summary. You parameters are `count=10`, `country=US`, `language=EN`, `safesearch=moderate`, using ordinary web search without live-crawl candidate generation. Only the web-results section is analyzed.

Calls are paired by `query_id`; provider order is randomized. Paired calls should complete within 15 minutes and the full run within seven days. A failed call may be retried twice with identical parameters. A query is never replaced because it returns few or poor results. Formal analysis requires at least 90% successful calls and at least 8,000 returned ranked results from each provider; otherwise the run is reported as incomplete and repeated only as a newly versioned run.

The providers do not currently have identical public terms. Brave's Search API Terms of Use, updated February 11, 2026, expressly prohibit storing, caching, or creating a database of Search Results except for transient operational storage, and prohibit redistribution, absent different rights in an Order Form. You.com's public general Terms do not contain the same express search-database prohibition; they assign You.com's rights, if any, in Outputs to the user but exclude Third Party Output, and allow service-specific supplemental terms. The applicable You API account, Order Form, MSA, and supplemental terms must therefore be checked before persistent raw-result storage. Dataset size does not change either contractual analysis.

Unless the applicable provider grants explicit storage rights:

1. provider payloads, titles, snippets, answer text, and ranks are processed transiently;
2. URLs are independently fetched from their original publishers;
3. persisted research facts come from those original pages, with retrieval timestamps and hashes;
4. row-level provider attribution is used only transiently to calculate frozen aggregate counts; and
5. durable provider comparison is limited to query-level URL/domain counts and overlap computed while both responses are transient; and
6. the public release contains queries, code, aggregate provider metrics, schemas, and integrity manifests—not provider payloads, fetched third-party page text, or a row-level company dataset.

For the ordinary Brave plan, each batch is written only to an operating-system temporary directory, parsed, used to initiate independent original-page fetches, and reduced to rights-safe aggregates. After the batch aggregate and fetch ledger pass validation, the raw JSON, titles, snippets, ranks, and provider-attribution rows are deleted immediately. They are not retained until manuscript completion. The deletion event records only batch ID, completion time, raw row count, aggregate hash, and deletion status. A failed batch is discarded and rerun under a new batch ID; raw payloads are not retained as debugging fixtures.

For Brave, provider-specific row-level reproducibility requires a plan or Order Form with storage rights; keeping a raw response only on a local machine does not avoid the express storage restriction. Consequently, the ordinary-plan study does not report provider-specific EQDP precision or provider-marginal qualified entities: those metrics would require durable candidate-to-provider incidence through the later human-review stage. For You, the study records whether the governing account terms or written provider confirmation permit research storage; until then, it applies the same conservative no-raw-payload boundary without claiming that You publicly imposes the same express prohibition. If storage rights are later obtained, provider-specific qualification analysis is a separately versioned extension, not a silent addition to this protocol.

This study is **paper-first, not dataset-release-first**. A closed local research corpus may retain independently fetched original-source provenance, extracted business facts, entity-resolution decisions, and human annotations to the extent allowed by each original source and privacy rules. The paper reports aggregate analyses and approved illustrative cases. No public row-level business corpus is required, and nonpublication is disclosed as a reproducibility limitation rather than described as open data.

## 4. From thousands of results to organized entities

The processing pipeline separates scale from evidentiary certainty:

1. **Transient capture:** parse the web results and compute per-query returned counts.
2. **URL normalization:** remove fragments and tracking parameters, normalize hosts, and retain the original publisher URL for independent fetch.
3. **Source classification:** label likely company page, directory, government page, association, marketplace, news, social profile, or noise.
4. **Independent fetch:** apply robots and HTTP checks; persist permitted source metadata, hashes, and derived business facts rather than search snippets.
5. **Candidate extraction:** identify business name, domain, claimed capability, city/state, commercial offering, and possible legal form.
6. **Entity resolution:** block on normalized domain/name/location; preserve aliases and parent/subsidiary evidence; do not merge on name similarity alone.
7. **Visibility stratification:** record whether the candidate has a dedicated domain, only a directory/social/business-registry presence, or insufficient web evidence.
8. **Human audit:** provider-blind reviewers determine evidence-qualified status on the frozen probability sample and on a separately labeled tail-case queue.

All retrieved records receive machine-generated organizational fields, but no unreviewed row may be called qualified. The primary human audit is a reproducible stratified probability sample of **1,200 resolved company-capability pairs**, balanced across industry family, intent, state, provider-incidence stratum, and rank band. At least 25% is independently double annotated. A separate discovery queue may prioritize up to 1,000 likely owner-operated or micro-producer cases for descriptive follow-up; it is not used for provider precision estimates unless sampling weights make it part of the probability sample.

## 5. Evidence-qualified domestic producer

The primary positive unit is a company-capability pair labeled an **evidence-qualified domestic producer (EQDP)**. It must satisfy all of the following:

1. a specific operating business is resolved;
2. the business directly makes, fabricates, assembles, processes, rebuilds, remanufactures, or contract-produces the requested item or capability;
3. the requested capability is explicitly supported by current original-page evidence;
4. evidence supports U.S. production presence in the queried state; and
5. the producer offers products or manufacturing services commercially.

A sole proprietor, owner-operated workshop, or home-based producer can qualify. It does not need a conventional factory or paid employees. A distributor, reseller, hobby-only page, design consultancy, software-only vendor, marketplace, or U.S. sales office with foreign-only production fails. EQDP status does not establish capacity, certification, willingness to accept an order, financial health, or procurement qualification.

### U.S. production presence

Production presence is classified as:

- `industrial_facility_confirmed`;
- `job_shop_or_workshop_confirmed`;
- `owner_or_home_production_confirmed`;
- `us_made_claim_site_unresolved`;
- `office_warehouse_or_lab_only`;
- `foreign_only`; or
- `unknown`.

Only the first three satisfy EQDP. For an owner/home producer, a public business source must connect commercial production to the city/state; the study does not require or publish a residential street address. A planned facility does not count until operational evidence exists.

## 6. Size and business-form strata

The study distinguishes descriptive scale bands from legal SBA size status. Census defines a nonemployer business as one with no paid employees, subject to federal income tax, and meeting the applicable receipts threshold. Public entity-level proof of nonemployer status is often unavailable; aggregate Census Nonemployer Statistics cannot be used to label a named company.

Analytic scale bands are:

- `owner_only_or_nonemployer_supported`;
- `micro_employer_1_9_supported`;
- `small_employer_10_99_supported`;
- `mid_employer_100_499_supported`;
- `large_500_plus_supported`; and
- `unknown`.

These bands are research categories, not federal legal definitions. LinkedIn, LeadIQ, ZoomInfo, marketplace, or directory estimates may support a provisional band only when their provenance is disclosed; they cannot prove nonemployer status or SBA eligibility. Legal form is separately recorded as `sole_proprietor`, `single_member_llc`, `other_llc`, `partnership`, `corporation`, `other`, or `unknown`.

For SBA analysis, assign the candidate's activity-specific six-digit NAICS, retrieve the current threshold from 13 CFR 121.201, and account for known affiliates. The only statuses are `sba_self_certified_small`, `size_consistent_unverified`, `not_small`, and `unknown`. A current entity-matched SAM/SBA representation may support `sba_self_certified_small`; it is still a representation, not an independent SBA size determination.

## 7. Annotation, privacy, and entity quality

Provider, rank, query intent, and machine-predicted scale are hidden during the first-pass human decision. The second reviewer independently annotates at least 300 probability-sampled cases. Cohen's kappa and raw agreement are reported for EQDP and component labels. All disagreements and all proposed name/domain merges with material impact receive adjudication. Entity-resolution precision must be at least 0.95 on a presampled audit of at least 200 merge/non-merge pairs.

Review time and supplemental source requests are recorded. Reviewers may find evidence about the supplied company but may not discover replacement companies. Search snippets cannot support a positive.

Only public business facts necessary for the study are collected. Personal phone numbers, personal emails, names of household members, and residential street addresses are excluded from the public dataset. For a home-based or sole-proprietor business, public output is limited to business name, capability, city/state where supportable, source URL, evidence status, and non-sensitive provenance. A takedown and correction channel applies to every release.

## 8. Metrics and analysis

The primary provider-retrieval metrics, computed and retained only at query-aggregate level, are:

- raw ranked results and successful queries;
- unique canonical URLs per 1,000 results;
- unique candidate domains per 1,000 returned results;
- URL and domain intersection and union counts; and
- call failure, partial-return, and duplicate rates.

Provider-specific EQDP precision, provider-marginal qualified entities, and rank-specific qualified yield are outside the ordinary-plan confirmatory analysis because row-level provider incidence is not retained. The provider-blind union corpus is used for all human-reviewed outcomes. Its primary outcomes are weighted estimated EQDPs per 1,000 independently fetched source URLs and reviewer minutes per EQDP.

Long-tail outcomes are the weighted proportions of EQDPs in each scale band, legal-form category, production-presence category, and web-visibility tier. Query-intent effects compare direct, small-batch, and micro/local strata. Results are reported overall and by industry family and state, without attributing a reviewed company to a provider.

Confidence intervals use stratified bootstrap resampling of query units with 10,000 replicates. Aggregate retrieval comparisons are paired by exact query. Probability-sample estimates for the union corpus use inverse inclusion weights; the enriched tail queue is descriptive only. Multiple hypothesis tests are secondary and Holm-adjusted. Effect sizes and intervals, not isolated p-values, control interpretation.

There is no exhaustive entity ground truth, so the study does not report national supplier recall, total U.S. coverage, or the percentage of all U.S. micro-manufacturers found. Census Nonemployer Statistics and County Business Patterns may be used as aggregate context or plausibility checks, never as entity-level ground truth.

## 9. Gates and release rules

The benchmark is eligible for a formal paper and aggregate-artifact release only if:

- at least 90% of the 960 queries succeed for both providers;
- each provider returns at least 8,000 raw ranked results;
- every EQDP has original-page provenance;
- double-review EQDP kappa is at least 0.70;
- entity-resolution precision is at least 0.95;
- probability-sampling weights and the deviation log reproduce; and
- provider and original-source rights checks pass.

The default release does not include a row-level company dataset.

Failing a gate is a result and does not authorize redefining the task set, scale bands, or positive label. The study may conclude that one or both engines poorly expose micro-producers, that micro-targeted queries increase noise more than yield, that provider complementarity varies by industry, or that public evidence cannot reliably establish business scale.

## 10. Source anchors

- Brave Search API, [web-search pagination and count](https://api-dashboard.search.brave.com/api-reference/web/search/get).
- Brave Search API, [Search API Terms of Use](https://api-dashboard.search.brave.com/terms-of-service) (updated February 11, 2026).
- You.com, [Terms and Conditions](https://you.com/legal/terms); any account-specific API Order Form or supplemental terms control where applicable.
- U.S. Census Bureau, [2022 NAICS Manual](https://www.census.gov/naics/reference_files_tools/2022_NAICS_Manual.pdf), [Understanding NAICS](https://www.census.gov/programs-surveys/economic-census/year/2022/guidance/understanding-naics.html), and [Nonemployer Statistics methodology](https://www.census.gov/programs-surveys/nonemployer-statistics/technical-documentation/methodology.html).
- Electronic Code of Federal Regulations, [13 CFR 121.201](https://www.ecfr.gov/current/title-13/part-121/section-121.201), and SBA [basic size requirements](https://www.sba.gov/federal-contracting/contracting-guide/basic-requirements).
- NIST MEP, [Supplier Scouting](https://www.nist.gov/mep/supply-chain/supplier-scouting).
- U.S. Department of Energy, [National Blueprint for Lithium Batteries](https://www.energy.gov/sites/default/files/2021-06/FCAB%20National%20Blueprint%20Lithium%20Batteries%200621_0.pdf).
- SEMI, [Semiconductor Components, Instruments and Subsystems overview](https://www.semi.org/sites/semi.org/files/2023-02/SCIS%20Overview%20and%20Activity%20Status%202023.pdf).

