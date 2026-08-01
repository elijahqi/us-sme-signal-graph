# From Search Results to Page-Supported Producer Candidates: An Evidence Audit Across Selected U.S. Manufacturing Queries

**Status:** internally consistent exploratory draft; not publication-ready until the human and entity-resolution validation gates in the claim audit are completed.

## Abstract

General web search can return pages about manufacturers, but a returned page is not yet a supplier, a production site, or a small business. We present an exploratory, model-applied evidence audit across selected U.S. manufacturing queries. A frozen lattice combines 40 manufacturing capabilities, eight states, and three query intents, yielding 960 provider-matched queries submitted to Brave and You Search. The providers returned 19,190 ranked rows. Transient processing produced 11,715 query-to-URL union links and 4,638 unique destination URLs; no provider payload was retained. Of those URLs, 3,383 returned HTTP 2xx. The construction pipeline crossed each such URL with capability and queried state inherited from retrieving queries, producing 6,164 source–capability–state pairs; the model assigned at most one focal business name per pair. Two GPT-5.6-Sol passes evaluated each pair against operating-business identity, direct production, capability match, production presence in the queried state, and current commercial offering. A third same-model pass was used fieldwise only where A and B disagreed. A mandatory literal-quote re-audit reduced the provisional positive labels to 1,148 (18.62%); all retained positives had a normalized literal quote in the frozen excerpt. The other labels were 3,799 no (61.63%) and 1,217 unclear (19.74%). Positive pairs resolved to 790 provisional operating-entity clusters and 785 provisional corporate-group clusters; these are not externally validated entity counts. A narrow destination-page size screen found nonhistorical numerical employee evidence for 23 clusters (2.91%); 14 (1.77%) fit wholly within one descriptive employee band. External SBA-small verification was not performed. The organizing observation is that retrieval output, model-applied page support, provisional entity clustering, and firm-size/SBA-status evidence are different measurement layers. Human validation and the preregistered entity-resolution precision audit remain outstanding.

## 1. Introduction

Manufacturing supplier discovery is usually presented as a search problem: a buyer specifies a capability, product, location, certification, or material and receives a list of candidate firms. Existing academic and operational systems already perform substantial parts of this task. Manufacturing-service knowledge graphs link thousands of companies to capabilities [1,2]; graph neural networks infer missing capability links [3]; Graph-RAG systems answer supplier-discovery questions [4]; localized supply-chain graphs support multi-condition SME discovery [5]; and NIST MEP and commercial platforms provide practical supplier scouting [8,9]. The question studied here is narrower: what support a bounded destination-page excerpt supplies under an explicit model-review protocol.

A page can name a company without showing that it directly produces anything. It can describe a capability without locating production in the queried state. It can refer to a distributor, an engineering office, a future plant, a customer, or an industry-wide employment statistic. Even when a page supports a producer claim, it may reveal nothing about employee count, affiliates, NAICS-specific size thresholds, or legal small-business status. A directory category, a service-area page, and a production facility are therefore not interchangeable evidence.

We therefore treat manufacturing discovery as a layered measurement problem:

1. **retrieval:** which URLs appear for a frozen capability–state–intent query;
2. **page-support labeling:** whether a frozen excerpt is judged to support a direct commercial producer of the requested capability in the queried state;
3. **provisional entity resolution:** how repeated pages and capability pairs cluster into putative operating entities and corporate groups; and
4. **firm-size evidence:** whether public text supports an employee band, owner-only operation, or a federal small-business representation.

The study answers four research questions:

- **RQ1:** How complementary are two general-web retrieval channels under identical frozen queries?
- **RQ2:** What fraction of the 6,164 pipeline-constructed pairs receives a positive page-support label, and why are other pairs labeled no or unclear?
- **RQ3:** How do those descriptive label fractions differ across the selected capability-query families, states, and query-intent incidence?
- **RQ4:** After provisional entity clustering, how often do the frozen destination pages support an employee band, owner-only operation, or a federal small-business representation under the narrow size screen?

Our contribution is the empirical evidence decomposition and the observed separation between its units. We make no first-of-kind claim. We do not claim that AI supplier discovery, manufacturing knowledge graphs, capability/location search, or SME discovery is new, and we do not claim exhaustive U.S. coverage, procurement qualification, available capacity, factual verification of page claims, or a known number of SBA-small firms.

## 2. Related Work and Novelty Boundary

### 2.1 Manufacturing-service knowledge graphs and capability inference

Li et al. constructed a manufacturing-services knowledge graph covering more than 8,000 manufacturers and proposed Schema.org extensions for web discoverability [1]. Li and Starly subsequently integrated a bottom-up ontology, manufacturing web footprints, graph embeddings, and ChatGPT; their public description reports more than 13,000 manufacturer web links with services, certifications, and locations [2]. Li, Liu, and Starly evaluated graph neural networks for capability prediction over a manufacturing-service knowledge graph built from more than 7,000 U.S. manufacturer websites [3]. These works establish large-scale web-derived manufacturing graphs and capability inference as prior art. Our study does not compete on graph size or infer a missing capability. It tests whether frozen destination-page excerpts support a multi-part producer claim under the specified model protocol.

Li, Ko, and Ameri integrated knowledge graphs, retrieval-augmented generation, and LLMs for supplier discovery [4]. Kumar demonstrated localized SME discovery over a curated Pennsylvania biopharma graph containing 488 enterprises, employee counts, and other structured fields [5]. AlMahri, Xu, and Brintrup used LLM extraction and knowledge graphs to reveal EV mineral and supplier relationships beyond tier 1 [6]. These studies demonstrate supplier discovery, SME-oriented graph search, and public-data supply-chain visibility. The reviewed manufacturing sources did not report the same corpus-conditional decomposition of retrieval, page-support labels, entity clustering, and original-page size evidence. This establishes a difference in empirical focus, not priority or superiority.

### 2.2 Search overlap and operational supplier scouting

Yagci et al. compared top-10 results from four search engines for 3,537 queries, showing that engine choice affects source diversity and overlap [7]. Multi-engine overlap measurement is therefore not new. We apply paired overlap measurement to a domain-specific query lattice and add original-page evidence review.

NIST MEP's Supplier Scouting service identifies U.S. manufacturers with requested production and technical capabilities through a national network [8]. Thomasnet supports search and filtering by capability, location, certifications, company type, and company size [9]. These systems show both the national demand and existing operational solutions. Our evidence audit is complementary: it measures what the same-model protocol labels as supported within frozen destination-page excerpts and makes failure modes explicit.

### 2.3 Evaluation, web-corpus, and entity-resolution context

Information-retrieval research has long treated incomplete relevance judgments as a measurement problem rather than assuming that unjudged documents are irrelevant [12]. The present corpus is not a pooled relevance collection: it evaluates the finite pairs constructed from two top-10 outputs and cannot estimate relevance outside that construction. Work on documenting C4 likewise shows how collection and filtering choices shape web corpora [13]. Our unit dictionary, fetch accounting, deviation log, and rights boundary expose those choices, although the closed row-level corpus limits independent audit.

LLM-as-judge research documents position, verbosity, self-enhancement, and reasoning biases and validates judges against human preferences rather than treating repeat-model agreement as ground truth [14]. This motivates our same-model wording and outstanding human-validation gate. Entity-resolution benchmarking also requires solution-quality measurement at an appropriate unit [15]; accordingly, provisional cluster counts are withheld from factual entity claims until the presampled precision audit is completed.

### 2.4 Relationship to the W→K→W pipeline

Qi et al. introduced an iterative Web–Knowledge–Web pipeline in which a knowledge graph guides subsequent crawling [10]. Its proof-of-concept comparison used unequal page counts and an approximate 195-company name reference; it did not establish SME status, buyer–supplier relationships, or in-state production. The present audit neither validates nor directly benchmarks that pipeline. A future comparison would need aligned candidate generation, equal budgets, sealed evaluation labels, and independent human validation.

A separate bounded prior-art audit documents the comparison matrix and claim boundary [11]. It is not a systematic review and does not support an exact-combination priority claim.

## 3. Methods

### 3.1 Frozen query lattice

The query lattice contains 40 capabilities across ten industry families: semiconductor equipment, batteries, precision metal, electronics, polymers/composites, additive manufacturing/tooling, industrial textiles, wood/industrial packaging, contract consumer production, and industrial repair/remanufacturing. Each capability is crossed with eight states—Massachusetts, Pennsylvania, Michigan, Ohio, North Carolina, Texas, Arizona, and California—and three intent templates:

- `direct`: ordinary manufacturer wording;
- `small_batch`: custom, job-shop, contract, or short-run wording; and
- `micro_local`: a heterogeneous mixed ownership/locality template containing small-business, family-owned, owner-operated, or local-workshop wording; it is not a firm-size category.

The Cartesian product yields 40 × 8 × 3 = 960 unique, provider-neutral queries. No result-aware rewriting, company-name rescue query, provider-specific synonym, or post-result capability substitution was permitted in the primary run. The frozen inputs and generated lattice are public repository artifacts.

### 3.2 Paired retrieval and rights boundary

Each exact query was submitted to Brave and You Search with ten web results requested. Brave returned 9,590 rows and failed one query after frozen retries; You returned 9,600 rows with no failed queries. Raw provider payloads, titles, snippets, and ranks were processed transiently and were not stored. Per-query URL aggregates and directly fetched destination-page provenance were retained. This boundary prevents the paper corpus from becoming a redistribution of provider search results.

At each query, canonical URL intersection and union were computed before transient provider data were discarded. Across all 960 frozen queries, the summed intersection was 7,475 and union 11,715. Their ratio is the pooled all-query URL Jaccard, 0.6381. The unweighted macro mean of 960 per-query Jaccards was 0.6555. The one query with a Brave failure was retained with a zero intersection rather than selectively rerun. As a sensitivity analysis limited to the 959 queries for which both calls succeeded, pooled Jaccard was 0.6386 and macro mean Jaccard 0.6562. Cross-query deduplication yielded 4,638 unique destination URLs.

### 3.3 Direct destination-page acquisition

Each union URL entered the same robots and HTTP workflow. Of 4,638 URLs, 3,383 returned HTTP 2xx, 1,018 returned HTTP 403, 129 were explicitly disallowed by robots, and nine hit a Python-enforced hard timeout. Robots and timeout counts are process flags and can overlap HTTP/status categories; they are not additional mutually exclusive URL counts. Access failures remained in the retrieval ledger but did not enter pair construction. The closed corpus stores directly fetched destination-page bodies where permitted, visible-text extracts, URLs, timestamps, and hashes—not search snippets. “Directly fetched” is separate from the search payload and does not imply first-party provenance or independent factual corroboration.

### 3.4 Candidate-pair construction and page-support label

Only HTTP-2xx destination pages entered candidate construction. For every query-to-page link, the pipeline inherited the query's capability and state, deduplicated on `(canonical source ID, capability, state)`, and aggregated observed intent tags. This produced 6,164 source–capability–state pairs from 3,383 pages. During review, the model assigned at most one focal business name to each pair; multi-company page extraction was not exhaustively evaluated. A pair receives the **five-component producer page-support label** only when the frozen excerpt is judged to support all five components. The retained schema field is named `eqdp` for compatibility with the frozen protocol; it is not a factual or legal qualification:

1. a specific operating commercial business;
2. direct production, fabrication, assembly, processing, rebuilding, remanufacturing, or contract manufacturing;
3. an explicit match to the requested capability;
4. eligible production presence in the queried state; and
5. a current commercial offering.

Eligible production presence includes an industrial facility, a job shop/workshop, or supported owner/home production. An office, warehouse, laboratory, service area, registered address, planned facility, or U.S. sales presence with foreign-only production is insufficient. The label measures textual support in a bounded excerpt; it does not independently verify the page's truth, current operational status, an actual buyer–supplier relationship, certification, capacity, financial health, willingness to quote, or procurement readiness.

### 3.5 Blinded model review and adjudication

The frozen 1,200-pair probability sample was evaluated first as an AI calibration. The implemented sampler proportionally allocated rows across 30 industry-family × primary-intent strata, selected rows deterministically within strata, and recorded inverse inclusion probabilities. This was narrower than protocol v0.3's stated balancing dimensions. The reported bootstrap resampled pairs within implemented sampling strata rather than query units; its interval is therefore an exploratory implementation diagnostic, not the protocol-conformant confirmatory interval. Those calibration decisions were retained. Protocol v0.4, committed after retrieval and calibration, prospectively governed the remaining 4,964-pair extension using the same substantive criteria. Reviewer A and Reviewer B were separate GPT-5.6-Sol passes using different stance/order prompts. Provider, rank, and prior decisions were absent. Browsing and tools were disabled. All 2,661 extension rows with a disagreement in any key field received a third same-model pass. In the corrected fieldwise merge, A/B-agreed key fields were locked and C was used only for A/B-disputed key fields. Execution failures were retried or requeued and were never converted to `unclear`.

These are separate passes of the same model, not independent models or human annotators. Agreement therefore measures repeat-evaluation stability under prompt/order variation. On the 4,964-pair extension, A/B agreement on the legacy `eqdp` field was 0.8159 and nominal Cohen's κ was 0.6092. The original v0.3 human double-annotation, κ≥0.70 release gate, reviewer-time measurement, and presampled 200-pair entity-resolution precision audit were not executed. The current results are exploratory and model-applied.

### 3.6 Entity resolution

Positive pairs were first blocked by domain, normalized name, and state. A dedicated business domain could support an initial cluster, but shared third-party directories could not. After literal-quote correction, 89 flagged domain clusters received same-model review for aliases, divisions, multiple operating entities, and unrelated businesses. Cross-domain exact normalized-name/state matches were consolidated; 11 fuzzy/alias candidate pairs received a separate same-model review. String similarity alone did not authorize a fuzzy merge.

We report 790 provisional operating-entity clusters and 785 provisional corporate-group clusters separately from production sites. All 11 reviewed fuzzy/alias pairs were resolved yes/no in the model pass, so there is no unresolved-pair sensitivity range. These counts are not accuracy estimates: they omit false-merge and false-split uncertainty because the preregistered external precision audit was not performed.

### 3.7 Firm-size evidence audit

Firm size was evaluated only after the page-support label and provisional entity clustering. An invalid first pass was discarded because its prompt included prior model rationales, creating circular model-to-model evidence. The corrected pipeline regenerated contexts solely from frozen destination-page visible text around employee, workforce, owner-only, nonemployer, SBA, SAM.gov, WOSB, and HUBZone terms. Empty contexts were automatically screen-negative.

After literal-quote correction, the pair-level size audit contains 446 nonempty contexts and 702 automatic screen negatives. Thirty-nine pair-level signals mapped to 29 provisional operating-entity clusters, which received A/B review and fieldwise C adjudication on five semantic disagreements. Every retained quote matched the frozen context after Unicode, quote, and whitespace normalization. The screen is deliberately narrow: it measures evidence present on capability/location destination pages under the specified term lexicon, not firm-size-data availability across the public web.

Employee bands are descriptive research categories: owner-only, 1–9, 10–99, 100–499, and 500+. They are not SBA determinations. A federal page claim is also not an external verification. A defensible SBA-small conclusion would additionally require activity-specific six-digit NAICS, the applicable current threshold, affiliate analysis, and current authoritative registration or other qualified evidence.

## 4. Results

### 4.1 Retrieval overlap

The all-query outputs had a 63.81% pooled query-URL Jaccard and a 65.55% macro mean of per-query Jaccards. Restricting to 959 dual-success queries produced 63.86% pooled and 65.62% macro overlap. In the all-query analysis, pooled values were 65.84% for direct, 63.77% for mixed ownership/locality, and 61.86% for small-batch queries; corresponding macro means were 67.37%, 65.75%, and 63.54%. Lower overlap indicates more distinct returned URLs within the requested top-10 outputs, not greater recall, better producers, or superior supplier discovery.

Source accessibility was itself a material filter: 72.94% of unique URLs returned 2xx, 21.95% returned 403, and 2.78% were robots-disallowed. The latter is a process flag rather than a mutually exclusive HTTP category. URLs without a 2xx response could not enter pair construction under the frozen workflow.

### 4.2 Constructed-corpus outcomes

Of 6,164 constructed pairs, 1,148 received the provisional five-component page-support label (18.62%), 3,799 were labeled no (61.63%), and 1,217 unclear (19.74%). Positive pairs represented 1,072 destination pages and 796 registrable domains before clustering. All 1,148 positive quotes passed the normalized literal-substring audit, and their model-produced production-state fields matched the queried state. These checks establish string and internal-field consistency, not the factual truth of the pages.

| Final pair label | Count | Share |
|---|---:|---:|
| Provisional five-component page-support yes | 1,148 | 18.62% |
| No | 3,799 | 61.63% |
| Unclear | 1,217 | 19.74% |
| Total | 6,164 | 100% |

In the earlier 1,200-pair probability sample, the corrected labels were 214 yes, 677 no, and 309 unclear. Inverse-inclusion weighting over the implemented strata yielded a 17.84% positive-label estimate. A 10,000-replicate pair-within-stratum bootstrap yielded 15.84%–19.86%. The full-corpus fraction, 18.62%, falls inside that diagnostic interval, but the interval is not presented as protocol-conformant because the frozen protocol specified query-unit resampling and broader balancing dimensions. Once all 6,164 model labels existed, exact constructed-corpus counts superseded sampling inference for this exploratory audit.

The leading model-assigned exclusion reasons among 5,016 nonpositive pairs were insufficient evidence (1,712; 34.13%), wrong state or missing queried-state production proof (1,102; 21.97%), capability mismatch (568; 11.32%), distributor/reseller/broker (463; 9.23%), nonmanufacturing service (324; 6.46%), source unavailable within the frozen excerpt (290; 5.78%), foreign-only production (203; 4.05%), and generic sector claims (133; 2.65%). Insufficient evidence and state-production categories together accounted for 56.10% of nonpositive model labels.

### 4.3 Industry, state, and intent incidence

Observed positive-label fractions differed by more than an order of magnitude across the selected capability-query families:

| Industry family | Page-support yes | Candidate pairs | Positive rate |
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

These descriptive fractions are not exchangeable industry effects. The selected capabilities, wording, page ecology, repeated entities, and fit to top-10 general search differ across families; the table does not estimate national industry coverage or causal discoverability.

State-conditioned constructed-corpus fractions ranged from 11.46% in Massachusetts to 24.68% in Texas:

| Queried state | Page-support yes | Candidate pairs | Positive rate |
|---|---:|---:|---:|
| Arizona | 127 | 709 | 17.91% |
| California | 184 | 769 | 23.93% |
| Massachusetts | 87 | 759 | 11.46% |
| Michigan | 147 | 767 | 19.17% |
| North Carolina | 118 | 765 | 15.42% |
| Ohio | 157 | 829 | 18.94% |
| Pennsylvania | 134 | 780 | 17.18% |
| Texas | 194 | 786 | 24.68% |

These are properties of selected state-query outputs and their page ecologies, not estimates of manufacturing prevalence or search quality by state.

Intent is multi-valued: one pair can be found through more than one query intent. The incidence counts therefore are descriptive and not causal arms. Direct-observed pairs were positive in 674 of 3,164 incidences (21.30%), mixed ownership/locality-observed pairs in 695 of 3,009 (23.10%), and small-batch-observed pairs in 491 of 2,745 (17.89%). A controlled experiment is required to estimate the causal effect of wording.

### 4.4 From positive pairs to entities

The 1,148 provisional positive pairs clustered into 790 provisional operating-entity clusters, a 31.18% reduction relative to the pair count, and 785 provisional corporate-group clusters. This illustrates why pair, page, domain, entity cluster, corporate-group cluster, and production site must remain separate units. Reporting 1,148 “companies” or “SMEs” would overstate the evidence. The cluster counts themselves remain unvalidated because no external precision audit has been completed.

### 4.5 Firm-size evidence screen

The corrected positive corpus contains 446 pair contexts with a size-related term and 702 automatic screen negatives. After pair review and entity mapping, 29 provisional clusters were reviewed at entity level; 761 had no surviving pair-level size signal and were not quote-audit eligible. This screen asks only whether the already retrieved capability/location pages contain usable employee, owner-only, or federal-program language. It is not a public-web search for firm size and cannot estimate overall firm-size-data availability.

| Entity-level size-screen result | Provisional clusters | Share of 790 |
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

The rows are nested or overlapping, not an additive partition: the 23 numerical-evidence clusters consist of 14 single-band and nine cross-band cases; the 14 single-band cases consist of 10, two, and two clusters in the listed bands; one of those clusters also has an explicit federal page representation.

The three federal-representation clusters comprised two in the explicit SAM/SBA page-claim category and one in the named federal-program page-claim category. They remain page representations, not independent current determinations. On the 29 screen-positive clusters, A/B raw agreement was 89.66% (nominal κ = 0.859) for descriptive band and 100% for federal-representation category. These small, selected-subset statistics measure same-model stability only. All 29 quote-audit-eligible reviews passed; quote audit was not applicable to 761 automatic screen negatives.

## 5. Discussion

### 5.1 The observed shortfall is evidentiary within this corpus

The reviewed literature and systems already discover suppliers by capability and location, build manufacturing knowledge graphs, infer latent capabilities, and expose company-size fields. The present audit asks a narrower question: how destination-page excerpts retrieved by the selected capability/location queries are labeled when producer, capability, state-production, commercial, and size evidence are separated. It does not establish what public systems generally report or what a targeted firm-size search would recover.

The largest model-assigned exclusion categories were insufficient evidence and missing queried-state production proof, not only clearly irrelevant pages. This illustrates why a retrieval evaluation based on clicks, domains, or company-name matches can count pages that do not contain the downstream evidence an analyst requests. A future validated benchmark should preserve component labels rather than compressing them into a single relevance score.

### 5.2 Size cannot be inferred from appearance

Family-owned language, an owner's biography, a small facility, low-volume capability, or a basic website does not itself establish employees, receipts, affiliates, or SBA status. Conversely, a local job shop can belong to a larger group. Under the narrow destination-page screen, 767 of 790 provisional clusters could not be placed wholly within one descriptive employee band.

A screen negative does not imply that an entity's size is unknowable or that it is not an SME. It means only that the frozen capability/location destination pages and term lexicon did not support the study's narrow classification. Authoritative registries, direct confirmation, commercial firmographics with disclosed provenance, or linked administrative data could produce different results.

### 5.3 Implications for graph-guided discovery

This audit does not supply an immediately reusable W→K→W test set because an adaptive crawler would generate different pages and pairs. It proposes an outcome schema that a future rerun could apply to W→K→W and static baselines under identical budgets. Such a study should construct candidates symmetrically, seal evaluation labels, and obtain independent human validation.

## 6. Limitations

First, this is a pipeline-constructed corpus under 960 frozen queries, not a census of U.S. manufacturers or search-visible firms. There is no exhaustive national entity ground truth, so national recall and completeness are unknown. Second, candidate retrieval used two general-web channels and top-10 outputs; other engines, directories, query formulations, dates, and provider failures could yield different populations. Third, only HTTP-2xx destination pages entered pair construction, and source-access outcomes may differ through other lawful channels.

Fourth, the full review uses repeated passes of one LLM. Blinding, varied prompts, structured validation, fieldwise adjudication, and quote audits reduce some failure modes, but they do not replace domain-expert or human validation. The original v0.3 human and entity-precision release gates remain unmet. Fifth, the calibration sampler and bootstrap implemented fewer balancing dimensions and a different resampling unit than protocol v0.3. Its interval is exploratory and is not used for a confirmatory claim. Sixth, the initial whole-record C merge distorted no/unclear labels, and the initial quote audit left 71 paraphrased positive quotes; both were corrected and logged before the current aggregates. Seventh, the 790 entity clusters remain provisional because model resolution has not been tested on the preregistered 200-pair external precision audit.

Eighth, the corrected size audit is keyword-window based. A page may contain size evidence expressed outside the term lexicon or on a linked page not present in the frozen corpus. Ninth, public page claims can be stale; only an external authoritative check can establish current legal status. Finally, the row-level corpus is not publicly released because it contains fetched third-party page content and provider-related rights constraints. Aggregate hashes show integrity of unavailable artifacts, not factual correctness, and the release does not permit record-level independent auditing.

## 7. Conclusion

Within the fixed top-10 outputs of 960 selected queries, the model protocol assigned 1,148 positive page-support labels, while most constructed pairs were no or unclear. Those positive pairs clustered into 790 provisional operating-entity clusters, not 1,148 verified firms. The central result is a separation principle: retrieval overlap, textual claim support, entity clustering, and firm-size/SBA-status evidence are different tasks and require different evidence.

This exploratory audit makes those layers explicit across ten selected capability families. Its value is not a claim that supplier discovery is new or that the labels are ground truth, but a concrete protocol and set of failure modes for subsequent human-validated study.

## Data and Artifact Availability

The working tree contains the frozen query lattice, capability/state/intent definitions, processing and review scripts, output schemas, aggregate reports, deviation logs, and integrity hashes. A row-free exploratory package is staged at `release/public/long-tail-evidence-audit-v0.1-exploratory`; its manifest explicitly states that it is not a validated benchmark and that human/entity-resolution gates remain incomplete. The older `release/public/v0.2.0-rc1` is a separate semiconductor pilot. Search-provider payloads, titles, snippets, and ranks were not retained. Directly fetched page bodies, row-level model decisions, and entity-level evidence remain in a closed research corpus. The aggregate package documents workflow and local byte integrity but does not permit record-level reproduction or independent auditing of the frozen labels, and it has not been externally published from this working tree.

## References

[1] Y. Li, S. Raman, P. Cohen, and B. Starly, “Design of Knowledge Graph in Manufacturing Services Discovery,” ASME MSEC, 2021. <https://doi.org/10.1115/MSEC2021-63766>.

[2] Y. Li and B. Starly, “Building a knowledge graph to enrich ChatGPT responses in manufacturing service discovery,” *Journal of Industrial Information Integration*, vol. 40, 100612, 2024. <https://doi.org/10.1016/j.jii.2024.100612>.

[3] Y. Li, X. Liu, and B. Starly, “Manufacturing service capability prediction with Graph Neural Networks,” *Journal of Manufacturing Systems*, 2024. <https://doi.org/10.1016/j.jmsy.2024.03.010>.

[4] Y. Li, H. Ko, and F. Ameri, “Integrating Graph Retrieval-Augmented Generation With Large Language Models for Supplier Discovery,” *Journal of Computing and Information Science in Engineering*, vol. 25, no. 2, 021010, 2025. <https://doi.org/10.1115/1.4067389>.

[5] V. Kumar, “Interoperable Knowledge Graphs for Localized Supply Chains: Leveraging Graph Databases and RDF Standards,” *Logistics*, vol. 9, no. 4, 144, 2025. <https://doi.org/10.3390/logistics9040144>.

[6] S. AlMahri, L. Xu, and A. Brintrup, “Enhancing supply chain visibility with knowledge graphs and large language models,” *International Journal of Production Research*, 2025. <https://doi.org/10.1080/00207543.2025.2575841>.

[7] N. Yagci, S. Sünkler, H. Häußler, and D. Lewandowski, “A Comparison of Source Distribution and Result Overlap in Web Search Engines,” *Proceedings of the Association for Information Science and Technology*, vol. 59, no. 1, pp. 346–357, 2022. <https://doi.org/10.1002/pra2.758>.

[8] NIST Manufacturing Extension Partnership, “Supplier Scouting.” <https://www.nist.gov/mep/supply-chain/supplier-scouting>.

[9] Thomas, “How to use Smart Search.” <https://help.thomasnet.com/search-for-suppliers>.

[10] Y. Qi, Y. Qi, and T. Wagh, “Coverage-Aware Web Crawling for Domain-Specific Supplier Discovery via a Web–Knowledge–Web Pipeline,” CIBDA 2026. <https://doi.org/10.1145/3813822.3814125>.

[11] “Prior-art and novelty audit v0.1,” project artifact, 2026.

[12] C. Buckley and E. M. Voorhees, “Retrieval Evaluation with Incomplete Information,” *Proceedings of SIGIR '04*, pp. 25–32, 2004. <https://doi.org/10.1145/1008992.1009000>.

[13] J. Dodge, M. Sap, A. Marasović, W. Agnew, G. Ilharco, D. Groeneveld, M. Mitchell, and M. Gardner, “Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus,” *Proceedings of EMNLP*, pp. 1286–1305, 2021. <https://aclanthology.org/2021.emnlp-main.98/>.

[14] L. Zheng et al., “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena,” *Advances in Neural Information Processing Systems*, vol. 36, pp. 46595–46623, 2023. <https://papers.nips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html>.

[15] J. W. Berry, C. A. Phillips, K. Kincher-Winoto, L. Getoor, and E. Augustine, “Entity Resolution at Large Scale: Benchmarking and Algorithmics,” Sandia National Laboratories, Technical Report SAND-2018-14090, 2018. <https://doi.org/10.2172/1493841>.
