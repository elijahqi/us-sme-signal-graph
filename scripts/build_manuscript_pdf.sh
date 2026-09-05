#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tex_file="$repo_root/paper/search_visible_manufacturing_evidence_audit_v0_1.tex"
pdf_file="$repo_root/paper/search_visible_manufacturing_evidence_audit_v0_1.pdf"
build_dir="$repo_root/paper/build"
text_file="$build_dir/search_visible_manufacturing_evidence_audit_v0_1.txt"

mkdir -p "$build_dir"
python3 "$repo_root/scripts/prepare_manuscript_source.py"
tectonic --keep-logs --keep-intermediates --outdir "$build_dir" "$tex_file"
cp "$build_dir/search_visible_manufacturing_evidence_audit_v0_1.pdf" "$pdf_file"

pdfinfo "$pdf_file" | grep -q '^Pages:'
pdftotext "$pdf_file" "$text_file"
python3 - "$text_file" <<'PY'
from pathlib import Path
import re
import sys

def normalized(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())

text = normalized(Path(sys.argv[1]).read_text(encoding="utf-8"))
for required in (
    "1,148 positive page-support labels", "Evidence Screening", "Working Paper v0.2",
    "321", "31", "Submission Gates", "External SBA-small verification was not performed",
    "17.84%", "Texas", "10,000-replicate", "not presented as protocol-conformant",
):
    if normalized(required) not in text:
        raise SystemExit(f"Missing manuscript content: {required}")
print("manuscript content checks passed")
PY
if grep -Fq 'Overfull \hbox' "$build_dir/search_visible_manufacturing_evidence_audit_v0_1.log"; then
  echo "manuscript contains an overfull box" >&2
  exit 1
fi

echo "built $pdf_file"
