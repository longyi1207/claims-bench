# CLAIMS-Bench v2 — Status (2026-06-29)

## Claude Code delivered (review)

| Area | Status | Notes |
|------|--------|-------|
| **43 L3 scenarios** | ✅ | 30 structured + 6 behavioral + 7 temporal |
| **Bradley-Terry** | ✅ | `pole_a`/`pole_b` on pairwise; BT in report |
| **Implicit judge module** | ✅ written | `src/v2/implicit_judge.py` — salience 0-3 × 10 values |
| **Implicit → scorer wiring** | ❌ was missing | **Fixed this session** |
| **run_eval_v2 implicit prompts** | ❌ was wrong (asked for JSON) | **Fixed** |
| **Pilot baseline** | ⚠️ | 5 items × 2 models; judge calibration doc'd in FINDINGS_v2_pilot.md |
| **Full 30×3 baseline** | ❌ not run | script added: `scripts/run_baseline_structured.sh` |
| **Consistency metric** | ❌ not run | `scripts/consistency_report.py` + `--replicate` / `--temperature` |
| **Human panel** | ❌ | tooling partial (`panel_aggregate.py` exists) |

## Grading stack (current)

### Structured items (revelation_001–030)

1. **Borda** — `rank_values` → 10-dim profile (5 ranked, rest 0 in aggregate)
2. **Bradley-Terry** — pairwise with `pole_a`/`pole_b` annotations
3. **Failure modes** — LLM judge on free reasoning (`gpt-4o` recommended)
4. **Epistemic prior** — categorical from JSON

### Implicit + temporal (revelation_031–043)

1. **Implicit judge** — LLM rates salience 0-3 on all 10 Schwartz values from free text
2. **Profile** — salience / 3 → same 10-dim vector space as structured
3. **Failure modes** — same 5 modes, severity 0-3 from judge
4. **No JSON** — `parse_status: implicit` (not non_compliant)

## Commands

```bash
# Structured baseline (Table 1)
bash scripts/run_baseline_structured.sh

# Score implicit only (needs judge)
python3 score_revelation.py \
  --data data/v2_revelation.jsonl \
  --responses outputs/.../responses.jsonl \
  --implicit-only \
  --judge-model gpt-4o \
  --report outputs/implicit_report.json

# Consistency (5 runs, temp=0.7)
for i in 1 2 3 4 5; do
  python3 run_eval_v2.py --structured-only --model gpt-4o-mini \
    --replicate $i --temperature 0.7 \
    --out outputs/consistency/run${i}.jsonl --resume
done
# merge scored runs then:
python3 scripts/consistency_report.py --scored outputs/consistency/all_scored.jsonl --out outputs/consistency/report.json
```

## Next actions (priority)

1. ~~Run structured baseline~~ ✅ `outputs/baseline_v2_structured/comparison_table.md` (30×3, 100% compliance)
2. **Consistency pilot** — running / see `outputs/consistency_pilot/`
3. **Implicit batch** — score all 13 implicit items (generate + judge ~$5-8)
4. **Human panel n=5** — same 8 L3 items
5. Fix `epistemic_prior` schema for non-agent scenarios (v2.1)

## Table 1 snapshot (2026-06-29)

| Model | top-3 (Borda mean) |
|-------|---------------------|
| gpt-4o-mini | security=0.71, universalism=0.63, benevolence=0.57 |
| gpt-4o | security=0.74, universalism=0.71, benevolence=0.55 |
| claude-sonnet-4-6 | **universalism=0.82**, security=0.67, benevolence=0.57 |

Claude skews higher universalism; all three near-zero stimulation/hedonism (expected for safety-framed scenarios).

## Credentials

- Vault `OPENAI_API_KEY` is **stale (401)** — use repo root `../../.env` (scripts now auto-source)
