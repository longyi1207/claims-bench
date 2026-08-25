# Findings — first full 80-item run (2026-08-25)

**Run:** 80 items × 10 replicates × 3 models = 2,556 generations, 0 generation
errors. Reproduce with `scripts/run_full80_inspect.sh`; artifacts in
`outputs/full80/`.

**Why it matters:** before this run, 37 of the 80 items (`revelation_044`–`080`)
had never been sent to any model. They are exactly the items authored to close the
Schwartz circumplex and Beauchamp–Childress coverage gaps, so two claims in
`paper/claims_bench_v2.md` were *unfalsifiable* rather than supported. Both are now
resolved, and both go against the published text.

| run | items | epochs | judge | purpose |
|---|---|---|---|---|
| A structured | 52 | 10 | — | Borda + Bradley–Terry profiles, significance testing |
| B implicit | 28 | 10 | gpt-4o | the salience judge *is* the profile for these |
| C failure modes | 52 | 1 | gpt-4o | failure-mode severities |

---

## 1. "Near-zero hedonism and stimulation" is an artifact of item coverage

§6.1 reports both values as near-zero across all three models and hedges between
"scenario selection" and "possible training bias". It is scenario selection.

Grouped by whether an item's own `schwartz_tension` tag pits the value against a
circumplex opposite (`scripts/coverage_gap_check.py`, 10 replicates):

| model | hedonism, on the 6 items testing it | stimulation, on the 12 items testing it | both, on all other items |
|---|---|---|---|
| gpt-4o-mini | **0.667** (its #2 value) | **0.283** | 0.014 / 0.034 |
| gpt-4o | **0.467** (its #3 value) | **0.168** | 0.016 / 0.054 |
| claude-sonnet-4-6 | **0.350** | **0.123** | 0.015 / 0.049 |

The published pilot subset contained **zero** items testing hedonism against a real
opponent, so it could only ever score 0.

Stimulation is the sharper half. The pilot subset *did* contain 8
stimulation-tagged items and they returned exactly 0.000 — the value looked
genuinely absent. Those items pit stimulation against `security`; the new ones pit
it against `tradition` and `conformity`, and it is clearly present. So the finding
is not "the benchmark forgot to ask":

> **A Schwartz dimension's measured weight is dominated by which opponent it is
> placed against, not by the dimension itself.** `stimulation` reads as exactly
> absent against `security` and as a mid-rank value against `tradition`/`conformity`.
> A 10-dimensional value profile is therefore uninterpretable without the tension
> coverage behind each dimension.

This is a criticism the benchmark can level at the value-profiling subfield
generally (Value FULCRA, ConflictScope, Value Portrait), and it is visible only
because coverage here is tag-checked (`scripts/check_tension_coverage.py`) rather
than eyeballed.

**Action:** rewrite §6.1 and the abstract; add an "items testing this tension"
column to every per-dimension table.

## 2. The pilot's headline comparison is reversed at full coverage

Published §6: the Claude-vs-GPT-4o universalism gap does **not** survive correction
(p=0.096), and "the only FDR-significant pattern is GPT-4o-mini scoring lower on
universalism than *both* larger models, not a Claude-specific effect."

Full 52-item structured set, 10 replicates, same statistics (item-cluster
bootstrap + permutation test + Benjamini–Hochberg across the 10 dimensions,
`scripts/significance_report.py`, full tables in
`outputs/full80/significance_structured.json`):

**Universalism separates all three models, monotonically:**

| comparison | means | perm p | Cohen's d | FDR |
|---|---|---|---|---|
| claude-sonnet-4-6 vs gpt-4o-mini | 0.645 vs 0.481 | 0.0002 | **0.422** | ✔ |
| claude-sonnet-4-6 vs gpt-4o | 0.645 vs 0.559 | 0.0004 | 0.218 | ✔ |
| gpt-4o vs gpt-4o-mini | 0.559 vs 0.481 | 0.0014 | 0.210 | ✔ |

The Claude-specific effect the pilot ruled out is real, and it is the **largest
effect in the study**. Achievement is a clean second axis running the other way
(Claude 0.200 < gpt-4o 0.263 < gpt-4o-mini 0.281; Claude-vs-both survives FDR).
Against `gpt-4o-mini`, Claude also separates on stimulation (d=−0.200), hedonism
(d=−0.191) and benevolence (d=0.163).

The coherent reading: Claude weights universalism/benevolence and downweights
achievement and the openness values; `gpt-4o-mini` is its mirror image; `gpt-4o`
sits between them on every axis.

**Action:** §6's conclusion must be replaced, not amended.

## 3. The parser was rejecting valid answers, and the rejection was model-correlated

Initially `claude-sonnet-4-6` showed 23 `schema_invalid` rows out of 520 (all 10
replicates of `revelation_071`, 8 of `revelation_046`) against 2 for `gpt-4o`. That
looked like a compliance finding. It was not — it was three renderings of the same
answer, only one of which the parser accepted:

| form | example | who emitted it |
|---|---|---|
| `{value: rank}` (schema) | `{"security": 1, "universalism": 2}` | all models, most of the time |
| `{rank: value}` | `{"1": "security", "2": "universalism"}` | claude-sonnet-4-6, 23 rows |
| positional array | `[1, 4, 3, 5, 2]` against the item's ordered value list | gpt-4o-mini, 11 rows |

All three are defensible readings of a field named `rank_values`, and the last two
are deterministically recoverable (`normalize_rank_orientation()` in
`src/v2/schwartz_profile.py`; the array form needs the item's `schwartz_values`
order, so `parse_response()` now takes it). After the fix, re-scoring the *existing*
responses at zero API cost:

| model | before | after |
|---|---|---|
| claude-sonnet-4-6 | 497/520 (95.6%) | **520/520 (100%)** |
| gpt-4o | 518/520 (99.6%) | **520/520 (100%)** |
| gpt-4o-mini | 509/520 (97.9%) | **520/520 (100%)** |

This mattered for the result, not just for tidiness: on the dropout-contaminated
data, `gpt-4o` vs `gpt-4o-mini` on universalism was p=0.0054 and **failed** FDR;
with the recovered rows it is p=0.0014 and passes. Differential dropout that
correlates with the model under test changed a published-level conclusion.

The paper's "100% format compliance" claim now holds — but it should say what it
means: 100% of responses were *parseable*, under a parser that accepts three
orientations. Regression tests: `tests/test_v2_scorer.py`.

## 4. Azure content filtering removes two items, non-deterministically

A measurement hazard, not a model finding. Full detail in
`docs/INSPECT_MIGRATION.md`.

- `revelation_064` (My Lai, 1968) — blocked at **generation**: `gpt-4o-mini` on
  10/10 replicates, `gpt-4o` on 3/10. The filter is not deterministic, so it skews
  replicate distributions as well as dropping items. Claude (Anthropic direct) is
  unaffected.
- `revelation_066` (1933 "Aryan business" pledge) — blocked at **judge** time,
  because the judge prompt embeds the scenario plus the model's full answer.

Azure sometimes signals this with HTTP 200 whose body *is* the filter notice rather
than a 400. Fourteen such rows initially entered the dataset scored as model
answers; they are now `parse_status: "provider_filtered"` and excluded from every
aggregate. A deployment refusing to discuss My Lai is not a value commitment of
the model — keeping those two things apart is the entire point of this benchmark.

Both items are in the temporal-shift family, the part of the benchmark with no
prior art. The limitations section should say so.

## Cost

Generation only (from the Inspect eval logs):

| model | input | output | est. USD | billed to |
|---|---|---|---|---|
| claude-sonnet-4-6 | 380,675 | 443,865 | 7.80 | Anthropic account |
| gpt-4o (Azure) | 348,080 | 370,581 | 4.58 | Azure credits |
| gpt-4o-mini (Azure) | 346,456 | 315,857 | 0.24 | Azure credits |
| **total** | | | **12.62** | |

**Caveat:** judge calls do not appear here. They go through the raw OpenAI SDK
inside the scorer rather than Inspect's model layer, so their tokens are not in
`log.stats.model_usage` — the one piece of the "Inspect gives you token
accounting" claim that is not yet true for this repo. Routing the judge through
`inspect_ai.model.get_model()` would close it.

---

## Still open

- **Cohen's κ** — `data/kappa_calibration/blank_scores_template longyi.csv` is 18
  empty rows. Until a human rates them, every failure-mode number stays
  "hypothesis-generating" (paper §7). No API cost, no code, ~1 hour; the
  highest-leverage open item in the project.
- **Human panel** — `data/panel/responses/` still empty.
- **Bradley–Terry at full coverage** — computed per-run, not yet compared across
  models with significance testing the way Borda now is.
- **`revelation_064` / `066`** — apply for Microsoft's modified-content-filter
  exemption, or accept the two-item gap and report it.
- **Paper rewrite** — §6, §6.1, the abstract, and the compliance claim all now
  contradict the data.
