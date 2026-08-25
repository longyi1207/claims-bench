#!/usr/bin/env bash
# Step 3 — full 80-item, significance-testable baseline via Inspect.
#
# Providers: OpenAI models go through the Azure OpenAI deployments (repo policy:
# Azure credits, not a personal card — ../../docs/AZURE.md). Anthropic models go
# direct, because claude-sonnet-4-6 is not offered on this Foundry resource.
#
# Three runs per model, because the judge only carries signal where it is needed:
#   A) structured (52 items) x N epochs, NO judge  -> Borda + Bradley-Terry profiles
#   B) implicit   (28 items) x N epochs, judge ON  -> the salience judge IS the profile
#   C) structured x 1 epoch,  judge ON             -> failure-mode severities
#
# Usage: bash scripts/run_full80_inspect.sh [EPOCHS] [MAX_CONNECTIONS] [MODEL...]
set -uo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh

EPOCHS="${1:-10}"
CONN="${2:-12}"
shift 2 2>/dev/null || true
if [ "$#" -gt 0 ]; then MODELS=("$@"); else
  MODELS=("openai-api/azure/gpt-4o-mini" "openai-api/azure/gpt-4o" "anthropic/claude-sonnet-4-6")
fi
JUDGE=gpt-4o          # routed to Azure by src/providers.py
LOGDIR=logs/full80
mkdir -p "$LOGDIR"

run_one() {  # $1=model  $2=tag  $3..=extra args
  local model="$1"; local tag="$2"; shift 2
  local slug="${model##*/}"
  .venv/bin/inspect eval inspect_task.py \
    --model "$model" \
    --max-connections "$CONN" \
    --log-dir "$LOGDIR/$tag" \
    --tags "claims-bench-full80,$tag,$slug" \
    --no-log-realtime \
    "$@" > "$LOGDIR/${tag}_${slug}.log" 2>&1
  echo "done: $tag / $slug (exit $?)"
}

echo "=== A: structured x $EPOCHS epochs (no judge) ==="
for m in "${MODELS[@]}"; do run_one "$m" structured --epochs "$EPOCHS" -T subset=structured & done
wait

echo "=== B: implicit x $EPOCHS epochs (judge=$JUDGE) ==="
for m in "${MODELS[@]}"; do run_one "$m" implicit --epochs "$EPOCHS" -T subset=implicit -T judge_model="$JUDGE" & done
wait

echo "=== C: structured x 1 epoch, failure-mode judge=$JUDGE ==="
for m in "${MODELS[@]}"; do run_one "$m" failuremodes -T subset=structured -T judge_model="$JUDGE" & done
wait

echo "=== export .eval logs -> legacy jsonl ==="
for tag in structured implicit failuremodes; do
  ls "$LOGDIR/$tag"/*.eval >/dev/null 2>&1 || continue
  .venv/bin/python scripts/eval_log_to_jsonl.py \
    --log "$LOGDIR/$tag"/*.eval --out-dir "outputs/full80/$tag" --log-spend
done
echo "ALL DONE"
