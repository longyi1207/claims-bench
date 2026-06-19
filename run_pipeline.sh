#!/usr/bin/env bash
# End-to-end CLAIMS-Bench pipeline.
# Usage:
#   ./run_pipeline.sh --model gpt-4o-mini --backend openai
#   ./run_pipeline.sh --model Qwen/Qwen2.5-7B-Instruct --backend hf --limit 10

set -euo pipefail
cd "$(dirname "$0")"

DATA="${DATA:-data/v0.2_core120.jsonl}"
MODEL="${MODEL:-}"
BACKEND="${BACKEND:-auto}"
LIMIT="${LIMIT:-0}"
SCORER="${SCORER:-heuristic}"
JUDGE_MODEL="${JUDGE_MODEL:-}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-512}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --backend) BACKEND="$2"; shift 2 ;;
    --data) DATA="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --scorer) SCORER="$2"; shift 2 ;;
    --judge-model) JUDGE_MODEL="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$MODEL" ]]; then
  echo "Usage: $0 --model <model_id> [--backend hf|openai|anthropic] [--limit N]"
  exit 1
fi

SLUG=$(echo "$MODEL" | tr '/:' '__')
OUT_DIR="outputs/${SLUG}"
mkdir -p "$OUT_DIR"

GEN_ARGS=(--data "$DATA" --model "$MODEL" --backend "$BACKEND" --out "$OUT_DIR/responses.jsonl" --max-new-tokens "$MAX_NEW_TOKENS" --resume)
SCORE_ARGS=(--data "$DATA" --responses "$OUT_DIR/responses.jsonl" --report "$OUT_DIR/report.json" --scored-out "$OUT_DIR/scored.jsonl" --scorer "$SCORER")

if [[ "$LIMIT" != "0" ]]; then
  GEN_ARGS+=(--limit "$LIMIT")
  SCORE_ARGS+=(--limit "$LIMIT")
fi

if [[ -n "$JUDGE_MODEL" ]]; then
  SCORE_ARGS+=(--judge-model "$JUDGE_MODEL")
fi

echo "=== Generate ==="
python3 run_eval.py "${GEN_ARGS[@]}"

echo "=== Score ==="
python3 score_responses.py "${SCORE_ARGS[@]}"

echo "=== Done ==="
echo "Report: $OUT_DIR/report.json"
