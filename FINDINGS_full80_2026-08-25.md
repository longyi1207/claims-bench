# Findings — first full 80-item run (2026-08-25)

**Status:** OpenAI models complete. `claude-sonnet-4-6` still generating — every
Claude number below is from the single-run August expansion, not the 10-replicate
full run, and is marked as such.

**What changed:** before this run, 37 of the 80 items (`revelation_044`–`080`) had
never been sent to any model. Those 37 are exactly the items authored to close the
Schwartz circumplex and Beauchamp–Childress coverage gaps, so two claims in
`paper/claims_bench_v2.md` were unfalsifiable rather than supported. They are now
testable, and one of them does not survive.

Run design (`scripts/run_full80_inspect.sh`, Inspect + Azure OpenAI):

| run | items | epochs | judge | purpose |
|---|---|---|---|---|
| A structured | 52 | 10 | — | Borda + Bradley–Terry profiles, significance testing |
| B implicit | 28 | 10 | gpt-4o | salience judge *is* the profile for these |
| C failure modes | 52 | 1 | gpt-4o | failure-mode severities |

---

## 1. "Near-zero hedonism and stimulation" is a measurement artifact

`paper/claims_bench_v2.md` §6.1 reports both values as near-zero across all three
models, hedging between "scenario selection" and "possible training bias". With the
coverage-gap items now run, it is scenario selection — decisively.

Grouped by whether an item's own `schwartz_tension` tag pits the value against a
circumplex opposite (`scripts/coverage_gap_check.py`, 10 replicates):

| model | item group | n obs | hedonism | stimulation |
|---|---|---|---|---|
| gpt-4o | items testing **hedonism** | 60 | **0.467** | 0.000 |
| gpt-4o | items testing **stimulation** | 120 | 0.000 | **0.168** |
| gpt-4o | all other items | 390 | 0.017 | 0.055 |
| gpt-4o-mini | items testing **hedonism** | 60 | **0.667** | 0.000 |
| gpt-4o-mini | items testing **stimulation** | 120 | 0.000 | **0.309** |
| gpt-4o-mini | all other items | 390 | 0.014 | 0.034 |

On the six items that actually ask, hedonism is `gpt-4o-mini`'s **second-highest**
value (0.667, behind self_direction 0.80) and `gpt-4o`'s third (0.467). The
published pilot subset contained **zero** items testing hedonism against a real
opponent, so the value could only ever score 0.

Stimulation is the more interesting half. The pilot subset *did* contain 8
stimulation-tagged items, and they returned exactly 0.000 — the value looked
genuinely absent. The new items pit stimulation against `tradition` and
`conformity` rather than against `security`, and it is clearly present. So the
finding is not "the benchmark forgot to ask" but something sharper:

> A Schwartz value's measured weight in an LLM profile is dominated by **which
> opponent it is placed against**, not by the value itself. `stimulation` loses to
> `security` so consistently that it reads as absent, and beats
> `tradition`/`conformity` often enough to be a mid-rank value. Reporting a
> 10-dimensional profile without reporting the tension coverage behind each
> dimension is therefore not interpretable.

That is a criticism this benchmark can level at the value-profiling subfield
generally (Value FULCRA, ConflictScope, Value Portrait), and it is only visible
because item coverage is tag-checked rather than eyeballed.

**Action:** §6.1 and the abstract need rewriting. The "near-zero hedonism/
stimulation" sentence should be replaced by the coverage-conditional result, and
the per-dimension tables should carry an "items testing this tension" column.

## 2. The pilot's one FDR-significant result does not replicate

The published §6 finding is that `gpt-4o-mini` scores lower on `universalism` than
both larger models, "p<0.001 in each comparison", on a 16-item structured subset
with 10 replicates — presented as the only pattern surviving Benjamini–Hochberg.

On the **full 52-item structured set**, same 10 replicates, same statistics
(`scripts/significance_report.py`, item-cluster bootstrap + permutation test + BH
across the 10 dimensions):

| dimension | gpt-4o mean [95% CI] | gpt-4o-mini mean [95% CI] | perm p | Cohen's d | FDR sig |
|---|---|---|---|---|---|
| universalism | 0.553 [0.452, 0.650] | 0.487 [0.383, 0.586] | 0.0054 | 0.177 | **no** |
| stimulation | 0.040 [0.008, 0.086] | 0.067 [0.008, 0.145] | 0.0324 | −0.135 | no |
| hedonism | 0.063 [0.020, 0.118] | 0.086 [0.027, 0.157] | 0.0766 | −0.111 | no |
| *(other 7 dimensions)* | — | — | 0.16–0.63 | \|d\| ≤ 0.09 | no |

The direction holds and the raw p-value is small, but the effect is now
**d = 0.18** and it misses BH by a hair (0.0054 vs. the 0.005 threshold for the
smallest of 10 tests). More items *increased* n and still weakened the result,
which means the pilot's effect was specific to the 16-item core subset rather than
a property of the models.

**Action:** the paper cannot keep "the only FDR-significant pattern is
gpt-4o-mini scoring lower on universalism" once the Claude arm lands. The honest
version is that no dimension separates these two models at full item coverage.

## 3. Format compliance is not 100%

The paper reports 100% structured-format compliance. Over 520 structured
generations per model:

| model | `ok` | `schema_invalid` | compliance |
|---|---|---|---|
| gpt-4o | 518 | 2 | 99.6% |
| gpt-4o-mini | 509 | 11 | 97.9% |
| claude-sonnet-4-6 *(single run, 22 items)* | 19 | 3 | 86.4% |

Claude's failures share a signature: the fenced JSON block opens with a stray
`json\n\n` before the fence, so the parser sees a malformed block. That is a
prompt/parse robustness issue worth fixing rather than a model-quality claim —
but "100% compliance" must go.

## 4. Azure content filtering removes two items, non-deterministically

Not a model finding; a measurement hazard, documented in full in
`docs/INSPECT_MIGRATION.md`.

- `revelation_064` (My Lai, 1968) — blocked at **generation**. `gpt-4o-mini` was
  blocked on 10/10 replicates; `gpt-4o` on 3/10. The filter is not deterministic,
  so it skews replicate distributions as well as dropping items.
- `revelation_066` (1933 "Aryan business" pledge) — blocked at **judge** time,
  because the judge prompt embeds the scenario plus the model's full answer.

Azure sometimes signals this with HTTP 200 whose body *is* the filter notice
rather than a 400. Fourteen such rows initially entered the dataset scored as
model answers; they are now marked `parse_status: "provider_filtered"` and
excluded from every aggregate (`looks_like_filter_response()` in
`src/providers.py`, regression tests in `tests/test_inspect_task.py`).

Both items are in the temporal-shift family — the part of the benchmark with no
prior art. Losing them to a deployment-level filter is a real cost, and the
limitations section should say so.

---

## Still open

- **`claude-sonnet-4-6` full run** — in flight. Section 2's conclusion is
  provisional until the three-way comparison exists.
- **Cohen's κ** — `data/kappa_calibration/blank_scores_template longyi.csv` is
  still 18 empty rows. Until a human rates them, every failure-mode number stays
  "hypothesis-generating" (paper §7). This costs nothing but an hour and is the
  highest-leverage open item in the project.
- **Human panel** — `data/panel/responses/` still empty.
- **`revelation_064` / `066` coverage** — either apply for Microsoft's
  modified-content-filter exemption, or accept the two-item gap and report it.
