#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tex_file="$repo_root/paper/search_visible_manufacturing_evidence_audit_v0_1.tex"
pdf_file="$repo_root/paper/search_visible_manufacturing_evidence_audit_v0_1.pdf"
build_dir="$repo_root/paper/build"
text_file="$build_dir/search_visible_manufacturing_evidence_audit_v0_1.txt"

mkdir -p "$build_dir"
tectonic --keep-logs --keep-intermediates --outdir "$build_dir" "$tex_file"
cp "$build_dir/search_visible_manufacturing_evidence_audit_v0_1.pdf" "$pdf_file"

pdfinfo "$pdf_file" | grep -q '^Pages:'
pdftotext "$pdf_file" "$text_file"
grep -Fq '1,148 positive page-support labels' "$text_file"
grep -Fq 'Submission Gates' "$text_file"
grep -Fq 'External SBA-small verification was not performed' "$text_file"
grep -Fq '17.84%' "$text_file"
grep -Fq 'Texas' "$text_file"
grep -Fq '10,000-replicate' "$text_file"
grep -Fq 'not presented as protocol-conformant' "$text_file"
if grep -Fq 'Overfull \hbox' "$build_dir/search_visible_manufacturing_evidence_audit_v0_1.log"; then
  echo "manuscript contains an overfull box" >&2
  exit 1
fi

echo "built $pdf_file"
