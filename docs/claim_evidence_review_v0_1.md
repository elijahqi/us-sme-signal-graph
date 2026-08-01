# Claim–evidence–risk–revision review v0.1

This table audits the manuscript's material claims against frozen artifacts. “Approved” means supportable within the stated scope, not externally validated by human experts.

| Proposed claim | Evidence | Main risk | Required wording or revision | Status |
|---|---|---|---|---|
| The study executed 960 frozen queries over 40 capabilities, eight states, and three intents. | `query_lattice_v0_2.csv`; `aggregate_snapshot.json` | Calling 960 queries “9,600 queries” by confusing requested results with queries | Keep 960 queries; state 9,600 requested results per provider. | Approved |
| Brave returned 9,590 rows and You returned 9,600. | `aggregate_snapshot.json` | Provider payloads were transient; one Brave query failed | Report the failed query and do not imply equal success. | Approved |
| Pooled query-URL Jaccard was 63.81%; macro mean per-query Jaccard was 65.55%. | `aggregate_snapshot.json`; formal retrieval report | Confusing ratio-of-sums with the unweighted query mean | Name both estimands explicitly. | Approved |
| The run produced 4,638 unique destination URLs. | Retrieval aggregate | Calling URLs suppliers/companies or implying first-party provenance | Use “destination URLs”; 3,383 returned 2xx. | Approved |
| The pipeline constructed 6,164 source–capability–state pairs from 2xx pages. | `full_census_final_v0_1.csv`; construction script | Calling pairs pages, firms, suppliers, or a census | Define the inherited query fields and one-focal-business model output. | Approved |
| There were 1,148 provisional EQDP page-support positives. | Corrected full-corpus summary and hash | Label can be mistaken for factual verification or procurement qualification | Say model-applied page-support label; all 1,148 passed literal quote audit. | Approved with qualification |
| Positive pairs cluster into 790 operating-entity and 785 corporate-group clusters. | Corrected entity summary and mapping hashes | No external entity-resolution precision audit; counts sound legally verified | Use “provisional clusters”; do not report an uncertainty interval. | Approved with qualification |
| Precision metal and wood packaging had the highest pair-level positive rates. | Full-census industry table | Readers may infer national industry supply coverage | Say “within the frozen candidate corpus.” | Approved with scope |
| Micro/local wording improves discovery. | Multi-valued intent incidence | Not randomized; candidates can appear under multiple intents | Use descriptive incidence only; no causal “improves.” | Rejected as causal |
| The destination-page size screen has 29 signal-bearing provisional clusters and 761 screen negatives. | Corrected entity-size summary | Screen can miss expressions, linked pages, or targeted size sources | Report 23 numerical-evidence clusters and 14 single-band clusters; never generalize to public-web size availability. | Approved with narrow scope |
| This is the first AI supplier-discovery system. | None; contradicted by Li et al., Li & Starly, Li–Ko–Ameri, commercial systems | False broad novelty claim | Remove. | Rejected |
| No one has combined the exact components. | Bounded Brave/You prior-art audit | Novelty-by-checklist; adjacent IR/LLM-judge/entity benchmark literature not systematically reviewed | Remove exact-combination priority claim; state only difference in empirical focus. | Rejected |
| This work validates or supplies a ready test set for W→K→W. | Current experiment does not run W→K→W and an adaptive crawler would produce different candidates | Retrospective overclaim and task mismatch | Say only that the outcome schema could inform a future aligned, human-validated rerun. | Rejected |
| AI A/B/C are independent reviewers. | Same GPT-5.6-Sol in separate passes | Sounds like independent humans/models | Say “separate passes of the same model”; agreement measures stability. | Approved only with clarification |
| All retained positive quotes are literal excerpts. | Corrected re-audit passes 1,148/1,148 positives | Literal substring does not verify truth or semantic validity | Say normalized literal-quote audit passed; retain human-validation caveat. | Approved with qualification |
| The corpus can be reproduced or independently audited from public data. | Query lattice, code, and a row-free exploratory aggregate package are staged in the working tree; row corpus is closed | Page drift, third-party rights, no provider payload, closed annotations | Say workflow and aggregate bytes are available when the repository version is published; record-level reproduction/audit remains unavailable. | Rejected broadly |
| The results measure all U.S. manufacturers or national recall. | No exhaustive ground truth | Invalid denominator | Explicitly prohibit national recall/coverage claims. | Rejected |
| The result is useful beyond immigration evidence. | Research design, prior-art comparison, methods, and locally integrity-anchored aggregate results | Framing could drift into advocacy or imply public auditability | Manuscript contains no NIW framing, states scientific limits, and does not call the closed labels independently auditable. | Approved |

## Manuscript stop rules

The draft must not be submitted as publication-ready until:

1. at least 300 provider-blind cases receive independent human double annotation, EQDP/component agreement is reported, and the preregistered κ≥0.70 gate is evaluated;
2. the preregistered 200-pair entity-resolution precision audit is executed and the ≥0.95 gate is evaluated;
3. the regenerated 29-cluster entity-size tables and hashes remain synchronized with the final manuscript;
4. adjacent IR pooling, LLM-as-judge, web-corpus, and entity-resolution benchmark literature is reviewed;
5. bibliographic metadata and the Kumar paper's source/validation description receive a final manual check;
6. the staged row-free aggregate package is included in a published repository version and its SHA256SUMS is verified after publication; and
7. the venue's policy on AI-assisted analysis and writing is checked and followed.
