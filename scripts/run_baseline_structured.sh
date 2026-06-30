#!/usr/bin/env bash
# Run structured L3 baseline (30 items) × 3 models + score + compare table.
# Budget estimate: ~$10-20 generation + ~$5-10 judge (gpt-4o).
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f ../../.env ]]; then
  set -a && source ../../.env && set +a
fi

DATA=data/v2_revelation.jsonl
OUT=outputs/baseline_v2_structured
JUDGE=gpt-4o
mkdir -p "$OUT"

MODELS=(gpt-4o-mini gpt-4o claude-sonnet-4-6)

for model in "${MODELS[@]}"; do
  slug="${model//\//_}"
  echo "=== Generate $model ==="
  python3 run_eval_v2.py \
    --data "$DATA" \
    --model "$model" \
    --structured-only \
    --out "$OUT/${slug}_responses.jsonl" \
    --resume

  echo "=== Score $model ==="
  python3 score_revelation.py \
    --data "$DATA" \
    --responses "$OUT/${slug}_responses.jsonl" \
    --structured-only \
    --judge-model "$JUDGE" \
    --scored-out "$OUT/${slug}_scored.jsonl" \
    --report "$OUT/${slug}_report.json"
done

python3 compare_profiles_v2.py \
  --reports "$OUT"/gpt-4o-mini_report.json "$OUT"/gpt-4o_report.json "$OUT"/claude-sonnet-4-6_report.json \
  --markdown "$OUT/comparison_table.md"

echo "Done. See $OUT/comparison_table.md"
