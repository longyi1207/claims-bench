#!/usr/bin/env bash
# Run all remaining v2 eval jobs: implicit batch, consistency temp=0, comparisons.
set -euo pipefail
cd "$(dirname "$0")/.."
LOG=outputs/run_all_remaining.log
mkdir -p outputs
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) run_all_remaining start ==="

bash scripts/run_implicit_batch.sh
bash scripts/run_consistency_temp0.sh gpt-4o-mini gpt-4o

python3 scripts/compare_consistency.py \
  --a outputs/consistency_pilot_temp0/gpt-4o-mini_consistency.json \
  --label-a temp0.0 \
  --b outputs/consistency_pilot/gpt-4o-mini_consistency.json \
  --label-b temp0.7 \
  --out outputs/consistency_pilot/temp0_vs_temp07.json

python3 scripts/export_panel_survey.py

echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) run_all_remaining done ==="
