#!/usr/bin/env bash
# Consistency at temperature=0.0 (deterministic) — compare to temp=0.7 pilot.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f ../../.env ]]; then
  set -a && source ../../.env && set +a
fi

DATA=data/v2_revelation.jsonl
OUT=outputs/consistency_pilot_temp0
MODEL="${1:-gpt-4o-mini}"
JUDGE="${2:-gpt-4o}"
N_REPS=5
LIMIT=5
mkdir -p "$OUT"

slug="${MODEL//\//_}"
merged="$OUT/${slug}_all_scored.jsonl"
: > "$merged"

for i in $(seq 1 "$N_REPS"); do
  echo "=== Replicate $i / $N_REPS (temp=0.0) ==="
  python3 run_eval_v2.py \
    --data "$DATA" \
    --model "$MODEL" \
    --structured-only \
    --limit "$LIMIT" \
    --replicate "$i" \
    --temperature 0.0 \
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
