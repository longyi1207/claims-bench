#!/usr/bin/env bash
# Consistency pilot: 5 structured items × 5 replicates × 1 model (temp=0.7).
# Budget: ~$3-8 depending on model.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f ../../.env ]]; then
  set -a && source ../../.env && set +a
fi

DATA=data/v2_revelation.jsonl
OUT=outputs/consistency_pilot
MODEL="${1:-gpt-4o-mini}"
JUDGE="${2:-gpt-4o}"
N_REPS=5
LIMIT=5
mkdir -p "$OUT"

slug="${MODEL//\//_}"
merged="$OUT/${slug}_all_scored.jsonl"
: > "$merged"

for i in $(seq 1 "$N_REPS"); do
  echo "=== Replicate $i / $N_REPS ==="
  python3 run_eval_v2.py \
    --data "$DATA" \
    --model "$MODEL" \
    --structured-only \
    --limit "$LIMIT" \
    --replicate "$i" \
    --temperature 0.7 \
    --out "$OUT/${slug}_run${i}_responses.jsonl" \
    --resume

  python3 score_revelation.py \
    --data "$DATA" \
    --responses "$OUT/${slug}_run${i}_responses.jsonl" \
    --structured-only \
    --judge-model "$JUDGE" \
    --scored-out "$OUT/${slug}_run${i}_scored.jsonl" \
    --report "$OUT/${slug}_run${i}_report.json"

  cat "$OUT/${slug}_run${i}_scored.jsonl" >> "$merged"
done

python3 scripts/consistency_report.py \
  --scored "$merged" \
  --out "$OUT/${slug}_consistency.json"

echo "Done. See $OUT/${slug}_consistency.json"
