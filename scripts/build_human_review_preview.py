#!/usr/bin/env python3
"""Build a local, read-only preview of the frozen human double-review subset."""
import csv
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "experiments/long_tail_benchmark/private/formal_v0_3"
OUTPUT = PRIVATE / "human_review_preview_v0_1"
FIELDS = ("review_id", "capability_id", "queried_state", "source_url", "page_title",
          "meta_description", "task", "evidence_excerpt", "page_sha256")

TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>人工标注材料 · 300 条双人复核样本</title>
<style>
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172c35;background:#f3f5f4;font-size:15px;line-height:1.65}*{box-sizing:border-box}body{margin:0}header{background:#153c42;color:white;padding:24px max(24px,calc((100vw - 1380px)/2))}h1{font-size:26px;margin:0 0 4px}header p{margin:0;color:#d3e5e2}main{max-width:1430px;margin:22px auto;padding:0 24px}.notice{padding:12px 16px;border-left:4px solid #d39633;background:#fff8e8;margin-bottom:18px}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0}.toolbar strong{margin-right:auto}button,select{font:inherit;padding:8px 14px;border:1px solid #b8ccc9;border-radius:8px;background:white;color:#153c42}button{cursor:pointer}button:hover{background:#e0efeb}button:disabled{opacity:.4;cursor:default}.grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(340px,1fr);gap:20px}.card{background:white;border:1px solid #dce5e2;border-radius:12px;padding:22px;min-width:0}h2{font-size:20px;margin:0 0 14px}h3{font-size:16px;margin:20px 0 6px}.tags{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.tag{padding:5px 10px;border-radius:6px;background:#e7f2ef;font-weight:600}.meta{font-size:13px;color:#55696e;overflow-wrap:anywhere}.source{display:block;margin:6px 0 12px;overflow-wrap:anywhere;color:#006757}.excerpt{white-space:pre-wrap;overflow-wrap:anywhere;font-family:Georgia,"Times New Roman",serif;font-size:16px;line-height:1.9;max-height:70vh;overflow:auto;padding:18px;background:#f8faf9;border:1px solid #e2eae6;border-radius:8px}.question{padding:11px 0;border-bottom:1px solid #e7eeeb}.question b{display:block}.question small{color:#65777b}.pills{font-size:12px;color:#637872;margin-top:5px}.pills span{display:inline-block;border:1px dashed #baccc5;border-radius:4px;margin-right:7px;padding:1px 8px}.final{margin-top:16px;padding:13px;background:#edf5f1}.muted{color:#5e7275;font-size:13px}details{margin-top:16px}summary{cursor:pointer;font-weight:600}ol{padding-left:22px}.empty{font-family:inherit;color:#805f2d}.foot{font-size:12px;color:#657b7d;overflow-wrap:anywhere;margin-top:14px}@media(max-width:880px){.grid{grid-template-columns:1fr}header{padding:20px 24px}.excerpt{max-height:60vh}main{padding:0 14px}}@media print{.toolbar,.notice{display:none}.grid{display:block}.excerpt{max-height:none;overflow:visible}.card{break-inside:auto;margin-bottom:15px}header{color:#153c42;background:white}}
</style>
<header><h1>人工标注材料</h1><p>300 条原定双人复核样本 · 逐条查看原文与判断要求</p></header>
<main>
<div class="notice"><b>当前是材料预览，还没有提交任何人工标签。</b> 页面不显示模型答案、搜索排名、查询意图或预测企业规模。先看几条，了解任务和每条所需时间。</div>
<div class="toolbar"><strong id="position"></strong><button id="prev">← 上一条</button><select id="jump" aria-label="选择样本"></select><button id="next">下一条 →</button></div>
<div class="grid"><section class="card"><h2 id="title"></h2><div class="tags"><span class="tag" id="capability"></span><span class="tag" id="state"></span></div>
<p><b>需要支持的工艺范围：</b><span id="scope"></span><br><b>任务明确排除：</b><span id="exclusions"></span></p>
<div class="meta">原始页面：<span id="pageTitle"></span></div><a id="source" class="source" target="_blank" rel="noopener noreferrer"></a>
<p class="muted">下面是原实验保留的证据摘录，未替你翻译或改写。<code>[...]</code> 表示摘录之间有省略。网页现在的内容可能已经变化；正式复核时需分别记录补充来源。</p>
<div id="excerpt" class="excerpt" tabindex="0"></div><div class="foot">材料编号：<span id="rid"></span><br>原网页指纹：<span id="hash"></span></div></section>
<aside class="card"><h2>每条需要你判断什么？</h2><p>核心问题：<b>这份证据是否支持一家商业企业，在目标州实际提供目标生产工艺？</b></p>
<div class="question"><b>1. 企业身份是否明确？</b><small>能否辨认一家实际经营的商业企业。</small><div class="pills"><span>是</span><span>否</span><span>信息不足</span></div></div>
<div class="question"><b>2. 它是否直接从事生产？</b><small>制造、加工、组装、翻新或代工；仅经销、咨询或宣传不够。</small><div class="pills"><span>是</span><span>否</span><span>信息不足</span></div></div>
<div class="question"><b>3. 是否符合目标工艺？</b><small>要有明确工艺支持；相邻工艺、泛泛行业描述需区分。</small><div class="pills"><span>是</span><span>部分符合</span><span>否</span><span>信息不足</span></div></div>
<div class="question"><b>4. 生产是否与目标州相连？</b><small>需填写生产场所类别和州。只有总部、销售办公室、仓库或未来计划不够。</small></div>
<div class="question"><b>5. 是否向外部客户商业提供？</b><small>区分对外产品／制造服务与内部研发、个人爱好、已经停止的业务。</small><div class="pills"><span>是</span><span>否</span><span>信息不足</span></div></div>
<div class="final"><b>最后填写：总体是／否／信息不足</b><br>记录原文短引句、生产所在地证据、主要排除理由、解释、补充来源和实际复核分钟数。</div>
<p class="muted">这里的选项仅展示字段，不是按钮，也没有默认答案。正式表中的英文值分别为 yes / no / unclear；“信息不足”不能靠猜测填成“否”。</p>
<details><summary>完整标注还包括哪些字段？</summary><p>来源当前状态、企业名称、置信程度、利益关系披露，以及独立的企业规模、法律形式和网络可见性等字段。规模判断不决定它是否是合格生产者。SBA 等额外判断须另有证据；不能凭名字猜。</p></details>
<details><summary>为什么是这 300 条？</summary><p>它们来自原先冻结的 1,200 条样本，沿用当时已经指定的双人复核标记，没有按照模型答案重新挑选。当前顺序沿用材料编号顺序，方便浏览；正式发放时应记录各标注人的顺序与分配。</p><p>这是原定双人子集的材料，不是针对 795 条边界样本的新过采样包，也不是独立的 200 对实体合并审计。</p></details>
<details><summary>独立复核与证据边界</summary><p>两位标注人提交前互不看答案。只复核指定企业；若需补证，应记录该企业的原始来源、查看时间，并区分冻结摘录与后来取得的证据。不寻找替代企业，不把搜索摘要当作证据。</p><p>不要记录私人住址、个人联系方式或与研究无关的个人信息。有业务往来、投资等利益关系时须披露。</p></details>
</aside></div></main>
<script type="application/json" id="dataset">__DATA__</script>
<script>
const rows=JSON.parse(document.getElementById('dataset').textContent);let index=0;
const byId=id=>document.getElementById(id);const put=(id,value)=>byId(id).textContent=value||'未提供';
rows.forEach((r,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`第 ${i+1} 条 · ${r.capability_id} · ${r.queried_state}`;byId('jump').append(o)});
function render(){const r=rows[index];put('position',`第 ${index+1} / ${rows.length} 条`);put('title',r.task.capability_label);put('capability',r.capability_id);put('state',`目标州：${r.queried_state}`);put('scope',r.task.positive_scope);put('exclusions',r.task.explicit_exclusions);put('pageTitle',r.page_title);put('rid',r.review_id);put('hash',r.page_sha256);put('excerpt',r.evidence_excerpt||'这条记录没有可用的冻结摘录。请在正式复核时记录证据缺失及补证需求。');byId('excerpt').classList.toggle('empty',!r.evidence_excerpt);byId('excerpt').scrollTop=0;const a=byId('source');a.removeAttribute('href');a.textContent=r.source_url;try{const url=new URL(r.source_url);if(['https:','http:'].includes(url.protocol))a.href=url.href}catch{}byId('jump').value=index;byId('prev').disabled=index===0;byId('next').disabled=index===rows.length-1;}
byId('prev').onclick=()=>{if(index>0){index--;render()}};byId('next').onclick=()=>{if(index<rows.length-1){index++;render()}};byId('jump').onchange=e=>{index=Number(e.target.value);render()};render();
</script></html>'''


def build():
    sample_path = PRIVATE / "review_sample_v0_1.csv"
    manifest = json.loads((PRIVATE / "review_sample_manifest_v0_1.json").read_text())
    if hashlib.sha256(sample_path.read_bytes()).hexdigest() != manifest["sample_sha256"]:
        raise ValueError("Frozen sample fingerprint changed")
    with sample_path.open(newline="") as handle:
        sample = list(csv.DictReader(handle))
    evidence = {}
    hashes = {}
    for path in sorted((PRIVATE / "ai_review_v0_1/batches").glob("*.json")):
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        for row in json.loads(path.read_text())["rows"]:
            if row["review_id"] in evidence:
                raise ValueError("Duplicate evidence ID")
            evidence[row["review_id"]] = row
    if len(sample) != 1200 or set(evidence) != {r["review_id"] for r in sample}:
        raise ValueError("Sample/evidence coverage mismatch")
    selected = [r for r in sample if r["double_review"] == "true"]
    if len(selected) != 300:
        raise ValueError("Expected the original 300 double-review IDs")
    rows = [{k: evidence[r["review_id"]][k] for k in FIELDS} for r in selected]
    if any(set(r["task"]) != {"capability_label", "positive_scope", "explicit_exclusions"} for r in rows):
        raise ValueError("Unexpected task fields")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.chmod(OUTPUT, 0o700)
    payload = json.dumps(rows, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    html = TEMPLATE.replace("__DATA__", payload)
    path = OUTPUT / "human_review_preview.html"
    path.write_text(html)
    os.chmod(path, 0o600)
    details = {"purpose": "Read-only material preview; no human labels collected", "rows": len(rows),
               "sample_sha256": manifest["sample_sha256"], "source_batch_hashes": hashes,
               "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "input_fields": FIELDS, "selection": "Original double_review=true; original order",
               "model_labels_read": False, "human_answers_prefilled": False,
               "source_evidence_changed": False, "row_level_data_public": False}
    (OUTPUT / "manifest.json").write_text(json.dumps(details, indent=2) + "\n")
    os.chmod(OUTPUT / "manifest.json", 0o600)
    print(json.dumps({"preview": str(path), "rows": len(rows), "labels_collected": 0}, ensure_ascii=False))


if __name__ == "__main__":
    build()
