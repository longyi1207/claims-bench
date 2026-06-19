# CLAIMS-Bench

**Conflicting Claims in AI alignment — Multi-Stakeholder evaluation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: 160 scenarios](https://img.shields.io/badge/scenarios-160-blue.svg)](data/v0.3_full160.jsonl)

Normative eval for assistant models: not *"will it refuse harm?"* but **when stakeholders conflict, which norm does the model implicitly optimize?**

📄 [Research proposal](RESEARCH_PROPOSAL.md) · [Baseline findings](FINDINGS.md) · [Vision / roadmap](VISION.md) · [Schema](schema.md)

## Quick start

```bash
git clone https://github.com/longyi1207/claims-bench.git
cd claims-bench
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Generate responses (API)
export OPENAI_API_KEY=...
python run_eval.py --data data/v0.3_full160.jsonl \
  --model gpt-4o-mini --backend openai \
  --out outputs/my_run/responses.jsonl

# Score (heuristic v0)
python score_responses.py --data data/v0.3_full160.jsonl \
  --responses outputs/my_run/responses.jsonl \
  --report outputs/my_run/report.json

# Compare models
python compare_models.py --reports outputs/*/report.json \
  --markdown outputs/leaderboard.md
```

Local open-weight (example):

```bash
python run_eval.py --backend hf --model Qwen/Qwen2.5-7B-Instruct \
  --data data/v0.3_full160.jsonl --out outputs/qwen/responses.jsonl --dtype float16
```

## What makes this different

| Benchmark | Measures |
|-----------|----------|
| HarmBench | Harmful **compliance** |
| ACHEval | Anthropic **principle tier** priority |
| BIG-bench HHH | Pairwise HHH preference |
| **CLAIMS** | **Stakeholder × norm-class profile** + Gabriel failure modes + pluralism |

**Output is a profile, not one number:** `acceptable_rate`, `blanket_refusal_rate`, `welfare_aggregate_bias_rate`, `imposition_rate`, by `conflict_type`.

## Data (v0.3)

| File | Items | Description |
|------|-------|-------------|
| `data/v0.3_full160.jsonl` | 160 | **Default** — core + pluralism |
| `data/v0.2_core120.jsonl` | 120 | Gabriel/Askell stakeholder conflicts |
| `data/v0.3_pluralism40.jsonl` | 40 | Cross-culture + temporal pairs |
| `data/calibration_subset24.jsonl` | 24 | For human κ calibration ([CONTRIBUTING](CONTRIBUTING.md)) |

## Baselines (June 2026)

Four models, heuristic scorer — see [FINDINGS.md](FINDINGS.md) and [baselines/comparison.md](baselines/comparison.md).

| Model | acceptable | malicious_user | control_help_refusal |
|-------|------------|----------------|----------------------|
| gpt-4o-mini | 0.65 | 0.48 | 0.15 |
| gpt-4o | 0.64 | 0.52 | 0.08 |
| deepseek-chat | 0.61 | 0.08 | 0.08 |
| Qwen2.5-7B-Instruct | 0.59 | 0.40 | 0.00 |

*Heuristic scorer is a rough baseline only. We invite community labels on `calibration_subset24` before claiming definitive rankings.*

## Layout

```
claims-bench/
├── data/           # JSONL scenarios
├── src/            # heuristic, judge, aggregate
├── baselines/      # published norm-profile reports
├── run_eval.py
├── score_responses.py
├── compare_models.py
└── run_pipeline.sh
```

## Citation

```bibtex
@software{zhou2026claims,
  author = {Zhou, Longyi},
  title = {CLAIMS-Bench: Conflicting Claims in AI alignment},
  year = {2026},
  url = {https://github.com/longyi1207/claims-bench},
  version = {0.3.0}
}
```

Or use [CITATION.cff](CITATION.cff).

## Lineage

Gabriel & Keeling (2025) · Askell et al. (2021) · Bai et al. (2022) CAI

## License

MIT — see [LICENSE](LICENSE).
