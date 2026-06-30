#!/usr/bin/env bash
# Build production PDF from claims_bench_v2.md
set -euo pipefail
cd "$(dirname "$0")"

FIG_SCRIPT=generate_figures.py
if [[ -f "$FIG_SCRIPT" ]]; then
  python3 "$FIG_SCRIPT" 2>/dev/null || true
fi

if ! command -v pandoc >/dev/null; then
  echo "pandoc required" >&2; exit 1
fi
if ! command -v tectonic >/dev/null; then
  echo "tectonic required (brew install tectonic)" >&2; exit 1
fi

# Body: skip duplicate title/abstract block in md (lines 1–16); metadata.yaml supplies them
BODY=claims_bench_v2_body.md
tail -n +18 claims_bench_v2.md > "$BODY"

pandoc \
  metadata.yaml \
  "$BODY" \
  --from=markdown+smart+tex_math_dollars+raw_tex-yaml_metadata_block \
  --to=pdf \
  --pdf-engine=tectonic \
  --resource-path=.:figures \
  --include-in-header=header.tex \
  --number-sections \
  --syntax-highlighting=tango \
  -V block-headings \
  -o claims_bench_v2.pdf

rm -f "$BODY"
echo "Wrote $(pwd)/claims_bench_v2.pdf"
ls -lh claims_bench_v2.pdf
