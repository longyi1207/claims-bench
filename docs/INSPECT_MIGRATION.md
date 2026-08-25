# Migrating the generation layer to Inspect (`inspect_ai`)

**Date:** 2026-08-24
**Scope:** generation + per-sample scoring only. Cross-sample aggregation stays where it is.

---

## Why

The hand-rolled provider layer (`run_eval.py`, `run_eval_v2.py`) had four costs that
grow with the size of the runs still ahead of us:

| Problem | Where | Consequence |
|---|---|---|
| Serial `for` loop, `--sleep` as the only rate control | `run_eval_v2.py:160`, `:196` | The 044–080 expansion run took **3 min** on `gpt-4o` and **10 min** on `claude-sonnet-4-6` for the same 37 items — purely serialisation. The full 80 × 10 replicates × 3 models run is 2,400 calls. |
| No retry, no 429 backoff | `run_eval.py:85-134` | A transient failure writes `[GENERATION_ERROR: …]` into the results file and moves on. |
| Four backends hand-written | `run_eval.py:30-134` | Every new provider is new code. |
| Spend logged by hand-copying a dashboard number into `--est-usd` | `src/v2/spend_log.py:1-6` | Of 82 rows in `outputs/spend_log.jsonl`, **one** has a real dollar figure. |

**One caveat on that last row:** generation tokens now come from the eval log, but
**judge tokens do not**. The judges call the raw OpenAI/Anthropic SDKs from inside
the scorer rather than going through Inspect's model layer, so they never reach
`log.stats.model_usage`. Routing them through `inspect_ai.model.get_model()` would
close the gap; until then, cost figures in `FINDINGS_full80_2026-08-25.md` cover
generation only.

Inspect solves all four (`--max-connections`, `max_retries`, one `--model` string
across providers, token usage in the eval log) and adds `--epochs N` for replicates,
`inspect view` for per-sample transcript inspection, and `inspect score` for
re-scoring an existing log without regenerating.

## What moved, and what deliberately did not

**Moved into Inspect** (`inspect_task.py`):
- prompt assembly → `record_to_sample()`, which calls the existing
  `run_eval_v2.build_messages_v2()` rather than reimplementing it
- model calls → `generate()`
- per-sample scoring → `revelation_scorer()`, which calls the existing
  `parse_response` / `infer_full_profile` / `extract_pairwise_comparisons` /
  `run_failure_mode_judge` / `run_implicit_judge`. **Judge prompts are unchanged**,
  so the Cohen's κ calibration packet (`docs/KAPPA_RATER_PACKET.md`) stays valid.

**Deliberately left outside Inspect:**

Inspect's metric protocol is `list[SampleScore] -> float` (multi-value reporting is
done by composing `grouped()` / `aggregate()`), which does not fit analyses that
pool information across samples and across models:

- **Bradley–Terry** (`src/v2/schwartz_profile.py`) — fits a model over pairwise
  comparisons pooled across every sample; not a per-key mean.
- **Significance testing** (`src/v2/significance.py`) — bootstrap CIs, permutation
  tests, Cohen's *d*, BH–FDR, all *across models*, i.e. across eval logs.
- **Consistency** (`scripts/consistency_report.py`), **human-panel distance**
  (`scripts/model_human_distance.py`, `scripts/panel_aggregate.py`) — panel
  responses are not model outputs at all.

These keep reading `responses.jsonl` / `scored.jsonl`. The seam is
`scripts/eval_log_to_jsonl.py`, which exports an `.eval` log back into exactly that
shape (Inspect `--epochs N` → the legacy `_run{epoch}` id suffix, so a multi-epoch
log drops straight into `consistency_report.py` and `significance.py`).

## Regression evidence

**Prompt parity, all 80 items, $0** — `tests/test_inspect_task.py` asserts that the
chat messages `record_to_sample()` produces are byte-identical to what
`generate_one_v2()` actually sends today (which goes through
`run_eval.build_messages()`, *not* `build_messages_v2()` — the test pins both paths
against each other too, since they are separate code in the legacy pipeline).
165 tests, all passing. Silent prompt drift was the migration risk that mattered:
it would have made every published number non-comparable without raising an error.

**Live parity** — the same 37 items (revelation_044–080) run twice: reference =
legacy loop + api.openai.com `gpt-4o`; new = Inspect + Azure `gpt-4o`
(`scripts/provider_parity_check.py`, report in
`outputs/expansion_044_080_azure/parity_report.json`):

| metric | result |
|---|---|
| items compared | 37 |
| parse-status flips | **0** |
| mean per-item L1 profile distance (0–20 scale) | **0.62** (~3%, within temp-0 sampling noise) |
| one-sided refusal/filter markers | **1** — `revelation_064`, Azure only |

The single outlier is not a harness problem: it is Azure's content filter, and it
is the largest per-item profile difference in the run (4.67 vs. a 0.62 mean).

## Provider: Azure OpenAI, not api.openai.com

Repo policy (`../../docs/AZURE.md`) is Azure credits over a personal card, so every
OpenAI call — generation *and* judges — routes through `src/providers.py`.
Deployments `gpt-4o` (2024-11-20) and `gpt-4o-mini` (2024-07-18) were created in
the project's Azure AI Services resource so model identity matches the
published pilot (resource/deployment specifics live in the private ops doc, not here).
Anthropic stays direct: that Foundry resource offers `claude-opus-5`,
`claude-sonnet-5`, `claude-opus-4-8`, `claude-haiku-4-5` — but **not**
`claude-sonnet-4-6`, the model in the published baseline.

For Inspect, the Azure route is the OpenAI-compatible provider:
`--model openai-api/azure/<deployment>` with `AZURE_API_KEY` / `AZURE_BASE_URL`
(derived from `AZURE_OPENAI_*` by `scripts/env.sh`).

### Content filtering is a measurement hazard, and it bites

Measured across all 80 items (`outputs/azure_content_filter_scan.json`,
`outputs/azure_judge_filter_scan.json`):

| stage | blocked | item |
|---|---|---|
| generation | 1/80 | `revelation_064` — My Lai, 1968 (`jailbreak` detect + `violence` medium) |
| judge | 1/80 | `revelation_066` — 1933 "Aryan business" pledge (`hate` medium) |

A custom RAI policy (`research-permissive`: all four categories at severity
`High`, jailbreak/indirect-attack disabled) was created and attached to both
deployments. It helped — `gpt-4o` then answered `revelation_064` — but did not
fully lift the block: relaxing Azure filters below the default requires
Microsoft's modified-content-filter approval, which is an application, not a
setting.

**Two traps worth knowing about:**

1. **Filtering is not always an error.** Azure sometimes returns HTTP 200 whose
   *completion body is the filter notice*. Detecting only the 400 path let 14 such
   rows into the dataset scored as if the model had answered them
   (`looks_like_filter_response()` in `src/providers.py`; regression tests in
   `tests/test_inspect_task.py`).
2. **Filtering is not deterministic.** On the same prompt and deployment,
   `gpt-4o` passed 7 of 10 replicates of `revelation_064` and was blocked on 3,
   while `gpt-4o-mini` was blocked on 10 of 10. So it skews replicate
   distributions, not just item coverage.

Filtered rows are marked `parse_status: "provider_filtered"` — deliberately
*not* `generation_error`, and never an empty-profile "answer". A deployment
refusing to discuss My Lai is not a value commitment of the model, and this
benchmark exists to keep those two things apart.

## Running it

```bash
# generation only, structured items, 10 replicates, 8-way concurrency
inspect eval inspect_task.py --model openai/gpt-4o \
    --epochs 10 --max-connections 8 -T subset=structured

# implicit items — the salience judge *is* the profile, so a judge is required
inspect eval inspect_task.py --model anthropic/claude-sonnet-4-6 \
    -T subset=implicit -T judge_model=gpt-4o

# inspect a single sample's transcript
inspect view --log-dir logs/full80/structured

# export back to the legacy shape that every analysis script reads
python scripts/eval_log_to_jsonl.py --log logs/full80/structured/*.eval \
    --out-dir outputs/full80/structured --log-spend
```

`scripts/run_full80_inspect.sh` wires all of this together for the full baseline.

## Rollback

`run_eval_v2.py` and `score_revelation.py` are untouched and still work; the
Inspect path is additive. Nothing in the 52 pre-existing tests touches the
generation layer, which is why the blast radius here is small.

## Dependency note

`inspect-ai` requires `openai>=3.1.0`; the repo was on 2.43.0. openai 3.0's only
breaking change is HTTPX2 becoming the default HTTP client
([changelog](https://github.com/openai/openai-python/blob/main/CHANGELOG.md)) —
this repo constructs no custom `httpx` client, so `judge_openai` /
`_judge_openai` / `generate_openai` are unaffected. Verified by re-running the
full test suite and a live one-item generation and judge call after the upgrade.
