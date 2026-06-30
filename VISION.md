# CLAIMS-Bench vision — normative eval in the spirit of Humanity's Last Exam

## What we're building

**Humanity's Last Exam (HLE)** set an upper bound for *capability*: expert-written, frontier-discriminating, community-owned.

**CLAIMS-Bench** aims at an upper bound for *value alignment taste*: when stakeholders conflict, **which norm does the model optimize?**

This is **not** a single-accuracy exam. It is a **multi-axis diagnostic** with expert-grounded items and failure-mode typing (Gabriel & Keeling 2025).

## Three layers (roadmap)

| Layer | Target size | Status | Purpose |
|-------|-------------|--------|---------|
| **Core** | 200 | v0.2: 120 public | Stakeholder × conflict → norm class + Gabriel types |
| **Pluralism** | 80 | v0.3: 40 public | Cross-culture / temporal dispute; imposition & pair drift |
| **Values** | 48 | v0.4: 48 public | Source-derived fundamental values; tradeoff pairs; tradition indices |
| **Adversarial** | 200 | planned | Template-generated variants; anti-memorization; anti-blanket-refusal |
| **Holdout** | 100 | private | Rotating private set; no train-on-test |

Public repo ships **Core** only. Holdout lives offline until v1.0 release process exists.

## Scoring philosophy (not MMLU)

```
                    ┌─────────────────────┐
  HarmBench  ──────►│ harm compliance     │  one axis
  ACHEval    ──────►│ principle tier      │  orthogonal
  CoVal      ──────►│ prompt-local rubrics│  complementary
  CLAIMS     ──────►│ norm profile vector │  primary
                    │ + value profile     │  v0.4: fundamental values
                    └─────────────────────┘
                           │
     acceptable_rate, welfare_bias, blanket_refusal,
     gabriel_type_rates, western/eastern indices,
     utilitarian/deontological indices, by_conflict_type
```

**Success metric for the benchmark:** frontier models **separate** on norm profile — not that everyone scores 95%.

## v0.2 deliverables (current milestone)

- [x] 120 core items (`data/v0.2_core120.jsonl`)
- [x] 40 pluralism items (`data/v0.3_pluralism40.jsonl`)
- [x] HF + API generation (`run_eval.py`)
- [x] Heuristic + optional LLM judge (`score_responses.py`)
- [x] Multi-model comparison (`compare_models.py`)
- [ ] Human calibration (κ on 24-item subset) — v0.3
- [ ] Adversarial generator — v0.4

## Anti-Goodhart design rules

1. **Never** optimize a single scalar — publish profiles, not one leaderboard rank
2. **Bind** `acceptable_rate` with `blanket_refusal_rate` on legitimate-help items
3. **Rotate** holdout; cap public set leakage in training corpora (honor system + private tests)
4. **Ambiguous** items (~15%) — score set overlap, not exact match

## Lineage

Gabriel & Keeling (2025), Askell et al. (2021), Bai et al. (2022), Conitzer et al. (2024) — aggregation limits inform why we use **norm classes**, not one utility.
