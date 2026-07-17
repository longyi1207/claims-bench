# Model comparison pilot — cost & run summary (2026-07-17)

**Total estimated spend: ~$2.58** (budget cap was $20; well under).

| Model | Calls | Est. cost |
|---|---|---|
| gpt-4o-mini | 160 (16 items x 10 replicates) | $0.05 |
| gpt-4o | 160 | $0.93 |
| claude-sonnet-4-6 | 160 | $1.60 |

Cost estimated from actual response character counts / 4 (token approximation)
applied to approximate current per-model pricing — not pulled from provider
dashboards, since `run_eval.py`'s `generate_openai`/`generate_anthropic` don't
currently surface token usage from the API response (a real gap; patching
this would give exact rather than estimated costs for future runs).

## Scope

16-item "core" structured subset (`data/v2_core_structured16.jsonl` = WVS
everyday domains 021-030, epistemic integrity 013-016, isomorphic pairs
017-018) — the statistically-clean set scoped in `NEXT_STEPS_2026-07-15.md`,
deliberately excluding the 6 behavioral/implicit items (needs judge scoring,
deferred pending kappa) and all existential/temporal items (kept as a
separate descriptive section per the earlier scoping decision).

10 replicates per item per model, temperature 0.7, 3 models
(gpt-4o-mini/gpt-4o/claude-sonnet-4-6) = 480 generation calls total.

## Parse success

| Model | Parsed OK | Failures |
|---|---|---|
| gpt-4o-mini | 152/160 (95%) | 8 |
| gpt-4o | 160/160 (100%) | 0 |
| claude-sonnet-4-6 | 160/160 (100%) | 0 |

## Headline finding — revises the original pilot's claim

The original June 2026 pilot (paper §6.1, n=1 per item, no replicates, no
significance testing) reported "Claude shows highest universalism (0.82 vs.
0.63-0.71 for OpenAI models)," framed as a Claude-vs-GPT-4o difference.

**With replicates and proper statistics (bootstrap CI, permutation test,
Benjamini-Hochberg FDR correction across all 10 dimensions), that framing
does not hold up as stated:**

- `universalism` is the only dimension significant after FDR correction, and
  the real pattern is **gpt-4o-mini vs. the two larger models**, not
  Claude vs. GPT-4o specifically:
  - gpt-4o-mini vs gpt-4o: p=0.0007, d=-0.45 (mini lower)
  - gpt-4o-mini vs claude-sonnet-4-6: p=0.0003, d=-0.61 (mini lower)
  - **gpt-4o vs claude-sonnet-4-6: p=0.0956 — NOT significant after
    correction.** GPT-4o (0.720) and Claude (0.780) are not statistically
    distinguishable on universalism on this item set at this sample size.
- No other dimension survives FDR correction in any pairwise comparison.
- `stimulation` and `hedonism` are exactly 0.000 for all three models on
  every item — this core-16 set predates the hedonism/stimulation
  coverage-gap items (revelation_044-049) and doesn't include them; adding
  those items to a future core-set run would be needed to say anything
  about those two dimensions.

**Practical implication:** the original paper's §6.1 sentence "Claude
showing the highest universalism (0.82 vs. 0.63-0.71 for OpenAI models)"
should be corrected or qualified before being treated as a finding — the
gap that's actually statistically supported is small-vs-large model, not
specifically Claude vs. GPT-4o.

Full per-dimension results: `outputs/model_comparison_pilot/significance_report.json`.
Raw parsed profiles: `outputs/model_comparison_pilot/parsed_profiles.json`.

## What this pilot does not yet cover

- The 6 behavioral/implicit items (needs judge scoring — deferred pending
  kappa calibration, in progress this weekend).
- Existential/governance/temporal items (kept descriptive, not statistically
  compared, per earlier scoping decision).
- Mixed-effects modeling proper (used item-cluster bootstrap as a
  nonparametric stand-in — see `src/v2/significance.py` docstring).
- Exact (vs. estimated) cost tracking — `run_eval.py` doesn't currently
  surface API token usage; would need a small patch to `generate_openai`/
  `generate_anthropic` to return usage alongside the response text.
