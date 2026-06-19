# CLAIMS-Bench — Baseline Findings (v0.3, n=160)

**Date:** 2026-06-18  
**Data:** `data/v0.3_full160.jsonl` (120 core + 40 pluralism)  
**Scorer:** heuristic v0 (fast baseline — **not paper-grade**; LLM judge + human κ needed)

## Models run

| Model | Backend | Status |
|-------|---------|--------|
| gpt-4o-mini | OpenAI | ✅ 160/160 |
| gpt-4o | OpenAI | ✅ 160/160 |
| deepseek-chat | DeepSeek API | ✅ 160/160 |
| Qwen2.5-7B-Instruct | HF local (MPS) | ✅ 160/160 |
| claude-3-5-haiku | Anthropic | ❌ credit balance too low |

## Headline norm profiles

| Metric | gpt-4o-mini | gpt-4o | deepseek-chat | Qwen2.5-7B |
|--------|-------------|--------|---------------|------------|
| acceptable_rate | 0.650 | 0.644 | 0.613 | 0.594 |
| primary_accuracy | 0.331 | 0.378 | 0.323 | 0.299 |
| blanket_refusal_rate | 0.006 | 0.013 | 0.006 | 0.013 |
| control_help_refusal_rate | 0.154 | 0.077 | 0.077 | **0.000** |
| malicious_user acceptable | 0.48 | 0.52 | **0.08** | 0.40 |
| rights_vs_welfare acceptable | 0.45 | 0.59 | 0.55 | 0.50 |
| developer_vs_society acceptable | 0.44 | 0.33 | 0.33 | **0.11** |

**First real open-vs-closed signal:** `malicious_user` gap (GPT ~50% vs DeepSeek 8% on heuristic). Verify with LLM judge — may be refusal wording differences.

## Pluralism tier (n=40)

| Metric | gpt-4o-mini | gpt-4o | deepseek-chat |
|--------|-------------|--------|---------------|
| imposition_rate | 0.025 | 0.025 | **0.075** |
| denies_disagreement_rate | 0.500 | 0.425 | **0.225** |
| dispute_acknowledgment_rate | 0.050 | 0.150 | 0.100 |
| pair_drift (behavior) | 0.529 | 0.471 | **0.706** |

DeepSeek: more behavior drift across cultural framing, fewer `denies_disagreement` flags, more `imposes_single_culture` on heuristic.

## Failure modes (Gabriel-inspired)

| Failure | mini | 4o | deepseek |
|---------|------|-----|----------|
| favors_user_over_society (type 3) | 11 | 9 | **1** |
| favors_developer_over_user (type 4) | 3 | 7 | 2 |
| denies_disagreement_exists | 20 | 17 | **9** |
| imposes_single_culture | 1 | 1 | **3** |

## Takeaways

1. **Four-model baselines complete** — closed (GPT) + open API (DeepSeek) + local OSS (Qwen).
2. **Heuristic scorer is intentional for v0.3** — we do not ship LLM-judge rankings as ground truth; community human labels on `calibration_subset24` are the path to v1.0.
3. **Discrimination exists** — especially `malicious_user`, pluralism imposition, pair_drift.
4. **OSS:** https://github.com/longyi1207/claims-bench — contributions welcome ([CONTRIBUTING.md](CONTRIBUTING.md)).

## Reproduce

```bash
cd code/claims_bench
set -a && source ../../.env && set +a
.venv/bin/python run_eval.py --model deepseek-chat --backend deepseek \
  --data data/v0.3_full160.jsonl --out outputs/deepseek-chat/responses.jsonl --resume
.venv/bin/python score_responses.py --data data/v0.3_full160.jsonl \
  --responses outputs/deepseek-chat/responses.jsonl --report outputs/deepseek-chat/report.json
.venv/bin/python compare_models.py --reports outputs/gpt-4o-mini/report.json \
  outputs/gpt-4o/report.json outputs/deepseek-chat/report.json \
  --markdown outputs/baseline_comparison.md
```

Outputs: `outputs/deepseek-chat/`, `outputs/baseline_comparison.md`
