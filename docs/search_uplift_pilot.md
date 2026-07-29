# Brave × You MCP Supplier-Graph Uplift Pilot

## 1. 研究问题

Brave Search MCP 与 You Search MCP 能否在相同查询预算下，为现有 semiconductor-equipment supplier dataset 带来经原始网页验证、实体消歧后仍成立的净新增公司与关系？两者并集是否优于任一单独 provider？

“提升”分三层，必须分别报告：

1. Retrieval uplift：有效 supplier source pages 是否更多；
2. Dataset uplift：相对冻结 baseline，是否新增有效 company nodes 与 typed edges；
3. Downstream uplift：是否改善 held-out supplier recall、coverage estimate，或在无泄漏条件下改善 SME-HGT。

节点更多不自动等于模型更好。若新 supplier 没有 SBIR Phase-I/II label，只能证明 supplier-graph coverage 提升，不能宣称 SME-HGT AUPRC 提升。

## 2. 当前状态

- 论文报告最终 KG 为 664 entities、542 relations；
- approximate ground truth 为 195 semiconductor-equipment companies；
- 起点为 48 hand-curated seed URLs；
- arXiv source archive 只有 LaTeX 与图，没有 entity/relation snapshot；
- 本机未找到对应 graph snapshot 或 195-company ground-truth list。

因此计算真实 uplift 前，必须找回旧 snapshot，或按论文方法重建并冻结 Baseline v0。只有汇总数字而没有实体列表，无法判断 Brave/You 候选是否真正新增。

## 3. 预注册实验设计

### 3.1 Baseline v0

冻结并保存 SHA-256：

- companies.parquet：canonical companies、aliases、domains、US locations；
- products.parquet、sectors.parquet；
- relations.parquet：relation type、source/target、evidence URL/text hash、retrieval date；
- source_pages.parquet、seed_urls.csv、ground_truth_companies.csv；
- baseline_manifest.json：counts、schema、pipeline commit、generation time。

公司节点数必须单独报告。664 是所有 entity types 总数，不能作为 company-node denominator。

### 3.2 查询集

Pilot 使用 SEARCH_UPLIFT_QUERY_SET.csv 中冻结的 24 条查询：12 capability groups × 2 templates。

- Template A：直接行业供应商查询；
- Template B：强调 domestic、sub-tier、contract manufacturer 与 components；
- 不利用当前轮 Brave/You 结果改写同一轮查询；
- Full run 才增加由 KG structural gaps 生成的查询，并另行版本化。

### 3.3 对照 arms

| Arm | 输入 | 用途 |
|---|---|---|
| D0 | Frozen baseline | 当前覆盖 |
| B | Brave-only | Brave 边际贡献 |
| Y | You-only | You 边际贡献 |
| B∩Y | 两者都发现 | 高共识候选 |
| B∪Y | 两者并集 | 总增量与互补性 |

公平性要求：

- 完全相同的 query、country、language、safe-search 与 result count；
- 每条 query 取 top 10：24 queries × 10 results/provider；
- 第一阶段关闭 You live crawl，避免混淆搜索能力与抓取能力；
- provider snippet 只用于 transient URL discovery；
- 统一 independent page fetcher 获取原始网页并抽取事实；
- 记录 latency、失败与 rate-limit，但不公开保存/再分发 provider payload。

### 3.4 去重

1. canonicalize URL；
2. 去 tracking params、fragment、mirror；
3. 解析 registrable domain；
4. 从原网页抽取 company name、capability、location；
5. 按 domain/name/address 做 entity resolution；
6. 与 D0 aliases/domains/locations 比对；
7. 人工标注前隐藏 provider origin 和 rank。

搜索排名或 snippet 不能替代原网页证据。

## 4. 标注定义

### 4.1 Valid supplier

Strict positive 同时满足：

1. 页面识别到具体公司；
2. 有美国总部、办公室或制造设施证据；
3. 直接制造 semiconductor equipment/component/subsystem，或提供明确相关 contract manufacturing；
4. capability claim 可从原网页精确引用；
5. 不是纯 market-report listicle、聚合页、招聘页或 SEO 空页；
6. 独立 registry、association、government record 或第二可靠来源确认身份/美国存在。

Lenient positive 可只由可靠 first-party company page 支持。

### 4.2 SME status

供应商有效性与 SME status 分开标注：

- confirmed_sme：SAM/SBIR/SBA size 或可靠 employee/revenue evidence；
- probable_sme：一致但非权威的规模证据；
- unknown：证据不足；
- not_sme：明确超过适用 SBA size standard。

不能因为公司私营、名字陌生或网站简单就推断为 SME。

### 4.3 Relation policy

| Relation | 接受条件 |
|---|---|
| produces | 明确制造/生产目标产品或 capability |
| belongs_to_sector | 行业与产品证据明确 |
| located_in | 明确属于该公司的 HQ/facility |
| partners_with | 明确 partnership/JV/agreement，非共同参会 |
| supplies_to | 明确命名 supplier-customer relationship；“serves leading OEMs”不算 |

论文最终图只有 2 条 supplies_to，说明公开证据稀少。Pilot 不以制造大量此类关系为目标。

### 4.4 Blind review

- 所有去重候选一轮盲审；
- 至少 20% 双人独立复核；
- disagreement adjudication；
- 报告 Cohen's kappa 或 Krippendorff's alpha，目标 ≥ 0.70；
- 使用 SEARCH_UPLIFT_ANNOTATION_SCHEMA.csv。

## 5. Primary metrics

### 5.1 Provider retrieval

- StrictValid@10、LenientValid@10；
- 每条 query 的 unique valid companies；
- noise rate、duplicate rate、direct-company-page rate；
- first strict positive median rank；
- latency 与 calls per valid candidate。

### 5.2 Dataset uplift

- NetNewCompanies(a)：arm a 中不属于 baseline 的 strict valid companies；
- CompanyLift(a)：NetNewCompanies(a) / baseline company node count；
- NetNewEdges(a, relation type)；
- QualityAdjustedLift；
- BraveMarginal：Brave 独有 strict positives；
- YouMarginal：You 独有 strict positives；
- provider Jaccard overlap；
- B∩Y strict precision。

Precision 使用 Wilson 95% CI；per-query lift 使用 paired bootstrap 95% CI。Brave vs You 按 query 配对比较，不能把 URL 当完全独立样本。

### 5.3 Coverage

- raw union 与 source-incidence overlap；
- Chao/ACE/capture-recapture 只作 sensitivity analysis；
- Brave 与 You 并非独立采样源，不能把估计值当真实总体；
- 按 capability/location bucket 报告覆盖，而非只有总 coverage。

### 5.4 Downstream

Supplier discovery：从 approximate GT 预先 hold out 一组公司，比较 D0/B/Y/B∪Y 的 held-out recall。

SME-HGT：只把能链接到现有 SBIR company nodes、且满足 feature cutoff 的新关系纳入。Base/enriched graph 使用相同 labels、temporal split、seeds、hyperparameters；比较 AUPRC、P@100、calibration 和 subgroup performance。无 Phase-II outcome 的新 suppliers 不进入 supervised labels。

## 6. 决策门槛

### Pilot → Full run

同时满足：

- B∪Y 至少 25 家 net-new strict supplier companies；
- union strict precision 的 Wilson 95% CI 下界 ≥ 0.55；
- Brave/You 各至少贡献 5 家另一方未发现的 strict positives，或有证据淘汰一方；
- annotation agreement ≥ 0.70；
- entity-resolution audit precision ≥ 0.95；
- 无许可、robots、PII 或 employer-IP blocker。

### Full run → 正式数据集

- company-node lift 的 paired-bootstrap 95% CI 下界 > 0；
- produces / belongs_to_sector strict precision ≥ 0.75；
- supplies_to 若发布，strict precision ≥ 0.90；
- duplicate/false-merge rate ≤ 2%；
- 每个发布事实都有非搜索-provider的原始 evidence URL 与 provenance；
- provider raw payload 不进入公开 release；
- 长期保存 Brave results 前取得 storage-rights plan；You 同样完成条款复核。

未达门槛仍可形成有效结论，例如 MCP 适合人工验证但不适合扩图、单 provider 已足够、或 query design 比 provider 更关键。

## 7. Smoke-test 观察

- 宽泛查询主要返回 Applied Materials、Lam、KLA 等头部厂商和 listicles；
- 加入 contract manufacturer、sub-tier、precision components 后，Brave 返回 GPR、TCMG、PEKO、JACO、AccuRounds 等直接公司页；
- You 部分调用返回大量 live-crawled content 或 403，因此正式比较要关闭 live crawl，并分离 search 与 source fetch；
- 没有 D0 entity list，故目前不能计算净新增百分比。

结论：存在值得正式验证的方向性 signal，但尚无 dataset-uplift 结论。

## 8. 最小执行顺序

1. 找回或重建 D0；
2. 冻结 24 queries 与参数；
3. 运行 Brave/You search-only；
4. 统一 fetch 原始页面；
5. entity resolution；
6. blind annotation；
7. 计算 B/Y/union/marginal metrics 与 CI；
8. 通过 gate 后扩到 60+ gap-generated queries；
9. 最后做 SME-HGT enriched graph experiment。

