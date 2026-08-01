# Prior-art and novelty audit v0.1

**Audit date:** 2026-07-31

**Scope:** public scholarly literature, official public programs, and representative commercial supplier-discovery interfaces

**Purpose:** falsify broad novelty claims and define the narrow contribution that the present study can support

## Bottom line

Supplier discovery, manufacturing knowledge graphs, capability inference, SME discovery, location-aware search, and multi-engine overlap measurement all have substantial prior art. The present study therefore must not claim to be the first supplier-discovery system, the first AI or knowledge-graph approach, the first system for finding small manufacturers, or the first capability/location search tool.

The defensible contribution is a **corpus-conditional evidence audit**: a frozen cross-industry and cross-state query lattice, paired general-web retrieval, direct destination-page fetching, model review of 6,164 pipeline-constructed source–capability–state pairs, explicit decomposition of producer/capability/location/commercial/size evidence, provisional entity clustering, and measurement of how often frozen excerpts support each required element. It does not yet constitute a validated benchmark and does not claim national supplier coverage or a new supplier-search function.

The reviewed manufacturing sources did not report the same corpus-conditional evidence decomposition. We make no exact-combination or first-of-kind claim; adjacent literatures on information-retrieval pooling, LLM-as-judge validation, web-corpus construction, and entity-resolution benchmarks require targeted review before submission.

## Search and verification method

Brave Web Search and You Search were used for discovery with query families covering manufacturing supplier discovery, manufacturing-service knowledge graphs, Graph-RAG and LLM supplier discovery, capability prediction, SME/localized supply-chain graphs, NIST supplier scouting, commercial capability/location search, web-search overlap, long-tail manufacturer discovery, and exact-phrase searches for the proposed benchmark concepts. Searches included 2025–2026 date terms and deliberately sought work that could defeat the proposed novelty claim.

Search payloads and snippets were not retained as research evidence. Bibliographic metadata were checked against DOI/Crossref or publisher pages. Functional claims were checked against the paper, official program page, or official product help page where accessible. The audit is reproducible at the concept and source level, but it is not a systematic review with database-specific export files because ordinary search-provider payloads were processed transiently.

## Comparison matrix

Legend: **Yes** means explicitly demonstrated in the reviewed source; **Partial** means present but narrower or supported by curated/proprietary inputs; **Not shown** means the reviewed public source did not demonstrate the feature, not that the authors or vendor could not do it.

| Work or system | What it already establishes | Scale/input in reviewed source | Cross-industry public-web retrieval benchmark | Producer + capability + state-production evidence separated | Firm-size evidence audited separately | Full candidate review and entity resolution | Consequence for this paper |
|---|---|---|---|---|---|---|---|
| Li et al. (2021), *Design of Knowledge Graph in Manufacturing Services Discovery* | Manufacturing-service KG and Schema.org/SEO extensions for discoverability | 8,000+ manufacturers linked to manufacturing services and Wikidata definitions | No | Not shown | Not shown | Not shown | KG-based manufacturing discovery and web discoverability are prior art. |
| Li & Starly (2024), *Building a Knowledge Graph to Enrich ChatGPT Responses in Manufacturing Service Discovery* | Bottom-up manufacturing-service KG plus ChatGPT/embedding-based querying | Public dataset described as 13,000+ manufacturer web links, services, certifications, and locations | No paired search-engine benchmark | Partial: capability/location represented as KG fields, not the present evidence test | Not shown as an original-page size audit | Not shown as a complete review of a general-search candidate census | Large-scale web-derived manufacturer KGs and LLM supplier discovery are prior art. |
| Li, Liu & Starly (2024), *Manufacturing Service Capability Prediction with Graph Neural Networks* | GNN inference of latent manufacturing capabilities | Text from 7,000+ U.S. manufacturer sites; 7,052 nodes and 112,873 relationships; four capability targets | No | Capability prediction evaluated, but not state-production evidence qualification | No | Graph train/test evaluation, not the present candidate/entity audit | Capability inference at larger website scale is prior art; this paper measures explicit evidence instead of inferring missing capability links. |
| Li, Ko & Ameri (2025), *Integrating Graph Retrieval-Augmented Generation With Large Language Models for Supplier Discovery* | Ontology-driven KG construction and Graph-RAG/LLM supplier discovery | Detailed supplier-discovery case study over harmonized capability data | No | Partial | Not shown | Not shown | Graph-RAG supplier discovery and SME visibility are prior art. |
| Kumar (2025), *Interoperable Knowledge Graphs for Localized Supply Chains* | Localized SME discovery, multi-condition graph queries, RDF/Schema.org interoperability | 488 Pennsylvania NAICS 3254 enterprises from Mergent Intellect/Dun & Bradstreet; employee count and sales fields; 11,520 edges | No; one curated commercial source and one sector/state | Partial: structured company/product/location fields | Employee count is an input field, not an open-page evidence-availability audit | Curated records; targeted manual query validation | Local/SME KG discovery and company-size filtering are prior art; the open-web evidence gap remains a separate question. |
| AlMahri, Xu & Brintrup (2025), *Enhancing Supply Chain Visibility with Knowledge Graphs and Large Language Models* | LLM extraction and KG mapping beyond tier 1 for EV minerals and suppliers | Selected EV, battery, and mining companies using public Wikipedia pages | No | Supply-chain links/material/location, not the present producer-state test | No | Proof-of-concept selected-company graph | Public-web LLM/KG supply-chain visibility is prior art, but it studies network links rather than broad candidate qualification. |
| Yagci et al. (2022), *A Comparison of Source Distribution and Result Overlap in Web Search Engines* | Multi-engine top-10 overlap and source-distribution measurement | 3,537 Google Trends queries; Google, Bing, DuckDuckGo, and MetaGer | Yes, but not manufacturing supplier qualification | No | No | No | Search-engine complementarity itself is prior art; this paper adds domain-specific evidence review. |
| NIST MEP National Network Supplier Scouting | National/regional/local identification of U.S. manufacturers with requested production and technical capabilities, using the MEP network | Official process distributes requests to MEP centers and typically returns results in 30–45 days | Operational service, not a published paired general-search benchmark | Capability and business interest are part of the service | SMMs are a target population, but the page does not publish the present entity-level evidence audit | Human/network-based process; no public full-census benchmark located | The national need and an existing solution are established; the paper must be positioned as complementary measurement, not replacement. |
| Thomasnet Smart Search | Supplier search by products, services, capabilities, certifications and location; sorting by company size/revenue/year; company-type and other filters | Official commercial platform and supplier profiles | No public paired general-web benchmark located | Partial through profile/search fields | Company size can be sorted, but public help does not establish the provenance/error rate required here | Proprietary platform process | Capability/location/size search functions already exist commercially. Novelty cannot be a feature checklist. |
| Qi et al. (2026), W→K→W v4 | Iterative KG-guided crawling and coverage estimation in semiconductor equipment | 144 crawled pages; 115 unique company names; 19 true positives against a curated 195-company reference; one NAICS sector | No cross-industry paired-search benchmark | No strict EQDP decomposition; relation precision used model annotation | No independent firm-size audit | Limited name normalization and proof-of-concept evaluation | The present benchmark is an evaluation foundation and extension, not evidence that W→K→W feedback already generalizes. |
| Present study | Model-applied page-support and evidence-availability decomposition in a frozen query-output corpus | 960 queries, 19,190 returned rows, 4,638 destination URLs, 6,164 constructed pairs, 1,148 provisional positive pair labels, and 790 provisional operating-entity clusters | Paired top-10 overlap audit | **Model-applied, not human validated** | Original-page-only screen, separate from producer label | Full constructed-pair review; entity precision gate still unmet | Contribution is the empirical separation of units and failure modes, not a validated benchmark, new search feature, or exhaustive directory. |

## Claim boundary

### Claims the evidence can support

- This is an exploratory cross-industry audit of how one model protocol labels page support in a fixed query-output corpus.
- It quantifies retrieval overlap, provisional positive-label yield, model-assigned exclusion causes, provisional entity-count collapse, and the availability of size evidence within frozen destination pages.
- It proposes an outcome schema for a future human-validated graph-guided discovery evaluation; it does not supply ground labels for W→K→W.

### Claims to remove or rewrite

- **Remove:** “No one has built supplier discovery for small manufacturers.”
- **Remove:** “The first AI/KG supplier-discovery system.”
- **Remove:** “Existing platforms cannot search by capability, location, or size.”
- **Remove:** “The audit discovered 1,148 SMEs,” “790 SMEs,” or any earlier 1,179/805 formulation. Pair labels and provisional entity clusters are not SME counts.
- **Rewrite:** “fills a market gap” → “measures an evidence and evaluation gap not reported by the reviewed systems.”
- **Rewrite:** “proves long-tail coverage” → “describes the search-visible population under a frozen query lattice; national recall is unknown.”
- **Rewrite:** “validates W→K→W” → “creates a cross-industry evidence benchmark that can support a future controlled W→K→W evaluation.”

## Recommended novelty sentence

> Prior work has built manufacturing-service knowledge graphs, inferred supplier capabilities, integrated KGs with LLMs, compared web-search overlap, and deployed public or commercial supplier-scouting systems. The reviewed manufacturing sources did not report the same corpus-conditional separation of retrieval output, page-support labels, provisional entity clusters, and destination-page size evidence. Our contribution is the empirical application of that separation and its observed failure modes; we make no first-of-kind claim, and the model labels require independent human validation before benchmark use.

## Verified source anchors

1. Li, Y., Raman, S., Cohen, P., & Starly, B. (2021). “Design of Knowledge Graph in Manufacturing Services Discovery.” ASME MSEC. <https://doi.org/10.1115/MSEC2021-63766>.
2. Li, Y., & Starly, B. (2024). “Building a knowledge graph to enrich ChatGPT responses in manufacturing service discovery.” *Journal of Industrial Information Integration*, 40, 100612. <https://doi.org/10.1016/j.jii.2024.100612>.
3. Li, Y., Liu, X., & Starly, B. (2024). “Manufacturing service capability prediction with Graph Neural Networks.” *Journal of Manufacturing Systems*. <https://doi.org/10.1016/j.jmsy.2024.03.010>.
4. Li, Y., Ko, H., & Ameri, F. (2025). “Integrating Graph Retrieval-Augmented Generation With Large Language Models for Supplier Discovery.” *Journal of Computing and Information Science in Engineering*, 25(2), 021010. <https://doi.org/10.1115/1.4067389>.
5. Kumar, V. (2025). “Interoperable Knowledge Graphs for Localized Supply Chains: Leveraging Graph Databases and RDF Standards.” *Logistics*, 9(4), 144. <https://doi.org/10.3390/logistics9040144>.
6. AlMahri, S., Xu, L., & Brintrup, A. (2025). “Enhancing supply chain visibility with knowledge graphs and large language models.” *International Journal of Production Research*. <https://doi.org/10.1080/00207543.2025.2575841>.
7. Yagci, N., Sünkler, S., Häußler, H., & Lewandowski, D. (2022). “A Comparison of Source Distribution and Result Overlap in Web Search Engines.” *Proceedings of the Association for Information Science and Technology*, 59(1), 346–357. <https://doi.org/10.1002/pra2.758>.
8. NIST MEP. “Supplier Scouting.” <https://www.nist.gov/mep/supply-chain/supplier-scouting>.
9. Thomas. “How to use Smart Search.” <https://help.thomasnet.com/search-for-suppliers>.
10. Qi, Y., Qi, Y., & Wagh, T. (2026). “Coverage-Aware Web Crawling for Domain-Specific Supplier Discovery via a Web–Knowledge–Web Pipeline.” <https://doi.org/10.1145/3813822.3814125>.

## Residual novelty risks

- Commercial vendors may have unpublished validation studies or internal evidence pipelines.
- Search indexing is imperfect; differently worded work may not have appeared in either provider.
- The study uses repeated passes of one model before external expert validation.
- The closed row-level corpus limits independent record-by-record reproduction.
- The combined design can be novel while individual components are not; the manuscript must attribute each component's prior art separately.
