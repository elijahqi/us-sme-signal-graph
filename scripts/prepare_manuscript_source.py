#!/usr/bin/env python3
"""Generate the tracked LaTeX manuscript from its canonical Markdown source."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
STEM = "search_visible_manufacturing_evidence_audit_v0_1"


def main() -> None:
    source = (ROOT / "paper" / f"{STEM}.md").read_text(encoding="utf-8")
    front, rest = source.split("## Abstract\n\n", 1)
    abstract, rest = rest.split("\n\n**Keywords:** ", 1)
    keywords, body = rest.split("\n\n", 1)
    metadata = {"title": front.splitlines()[0].removeprefix("# "),
                "abstract": abstract.strip(), "keywords": keywords.strip()}
    for field in ("Author", "Version", "Status"):
        prefix = f"**{field}:** "
        metadata[field.lower()] = next(
            line.removeprefix(prefix).strip()
            for line in front.splitlines() if line.startswith(prefix)
        )
    # Keep references compact and start the exploratory appendices on a new page.
    body = body.replace("## References\n", "\\begingroup\n\\small\n\n## References\n", 1)
    body = body.replace("## Appendix A.", "\\endgroup\n\\clearpage\n\n## Appendix A.", 1)
    build = ROOT / "paper" / "build"
    build.mkdir(exist_ok=True)
    metadata_path = build / "manuscript_metadata.json"
    body_path = build / "manuscript_body.md"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    body_path.write_text(body, encoding="utf-8")
    subprocess.run([
        "pandoc", str(body_path), "--from=markdown", "--to=latex", "--standalone",
        "--template", str(ROOT / "paper" / "manuscript_template.tex"),
        "--metadata-file", str(metadata_path), "--wrap=none",
        "--output", str(ROOT / "paper" / f"{STEM}.tex"),
    ], check=True)
    latex_path = ROOT / "paper" / f"{STEM}.tex"
    latex = latex_path.read_text(encoding="utf-8")
    # Every manuscript table is short. Reserve enough space to keep its caption
    # and rows together rather than splitting a three-stage result across pages.
    latex = latex.replace("\\begin{longtable}", "\\Needspace{17\\baselineskip}\n\\begin{longtable}")
    latex_path.write_text(latex, encoding="utf-8")
    print(f"generated paper/{STEM}.tex from Markdown")


if __name__ == "__main__":
    main()
