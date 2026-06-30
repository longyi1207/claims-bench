# CLAIMS-Bench v2 — Agent Handoff Prompt

**Copy everything below the line into a new Claude Code session.**

---

## Your mission

Rebuild and extend **CLAIMS-Bench** (`code/claims_bench/`, also published at https://github.com/longyi1207/claims-bench) into a **community-useful v2 eval** — not a PoC.

### North star (non-negotiable)

> **Characterize models' implicit value commitments under conflict and under-specification — and compare to human pluralism — not certify moral correctness.**

Read first: `NORTHSTAR.md`, `ROADMAP_v2.md`, `BUDGET.md` ($1000 total cap for API/compute/human incentives).

### Three measurement layers

| Layer | Question | Theory |
|-------|----------|--------|
| **L1** Stakeholder fairness | Who does the model favor when claims conflict? | Gabriel & Keeling 2025 |
| **L2** Principle tension | Which mid-level principles dominate? | Beauchamp & Childress |
| **L3** Value revelation | What implicit priorities under radical uncertainty? | Schwartz 2012 + Berlin pluralism |

**L3 is the primary research contribution.** L1/L2 support and complement.

---

## Repository context

**Location:** `/Users/apple/Desktop/ai_notes/code/claims_bench/` (standalone git repo)

**What already exists (v0.5 legacy — preserve, do not delete):**
- 208 scenarios in `data/v0.5_full208.jsonl` (L1 stakeholder + old values tier)
- Working pipeline: `run_eval.py`, `score_responses.py`, `compare_models.py`
- Heuristic scorer: `src/heuristic.py` (known weak — keep as fast baseline)
- 4-model baselines in `baselines/` and `outputs/`
- Theory docs: `THEORY.md`, `FINDINGS.md`

**What was just scaffolded for v2 (build on this):**
- `NORTHSTAR.md` — mission and claims
- `docs/TAXONOMY.md` — multidimensional tags (replace coarse `conflict_type`)
- `docs/L3_REVELATION_PROTOCOL.md` — L3 design + scoring
- `docs/HUMAN_PANEL_PROTOCOL.md` — human baseline collection
- `data/schwartz_backbone.yaml` — Schwartz 10-value descriptive backbone
- `data/revelation/first_contact_ufo_v1.yaml` — exemplar L3 item (UFO/first contact)
- `data/revelation/SCENARIO_BANK.md` — 20+ scenario ideas to author
- `data/schemas/item_v2.schema.json`, `revelation_response.schema.json`
- `scripts/yaml_to_jsonl.py` — partial stub
- `src/v2/schwartz_profile.py` — partial stub
- `ROADMAP_v2.md` — phased plan

**Parent monorepo reading pack (optional context):** `/Users/apple/Desktop/ai_notes/readings/values_foundations/`

---

## What to build (priority order)

Follow `ROADMAP_v2.md` phases. Summary:

### Phase 1 — Schema & migration
1. Finish `scripts/yaml_to_jsonl.py` (add PyYAML to `requirements.txt`)
2. Implement `scripts/migrate_legacy_tags.py` — add v2 `tags` to v0.5 items per `docs/TAXONOMY.md`; keep legacy fields
3. `tests/test_v2_schema.py` — validate revelation YAML + migrated items
4. Write `docs/V2_DELTA.md` — what changed from v0.5

### Phase 2 — L3 scenario bank (20–30 items)
1. Author YAML files in `data/revelation/` from `SCENARIO_BANK.md`
2. Copy structure from `first_contact_ufo_v1.yaml`
3. Include ≥4 isomorphic pairs (`pair_id`) for framing drift
4. Include ≥2 decoy certainty traps
5. Export to `data/v2_revelation.jsonl` and `data/v2_full.jsonl` (L3 + migrated L1 subset)

Each L3 item MUST have:
- `uncertainty: radical_under_spec`
- Structured `elicitation` (rank_values, pairwise, epistemic_prior)
- `gold.failure_modes` (no single primary answer)
- `human_panel.required: true`

### Phase 3 — L3 scorer (core engineering)
1. `src/v2/revelation_parse.py` — extract JSON block from model response (robust to markdown fences)
2. Extend `src/v2/schwartz_profile.py` — Borda from ranks + pairwise vote into 10-dim vector
3. `src/v2/failure_modes.py` — LLM judge for: false_certainty, imposes_single_culture, denies_disagreement_exists, precaution_blindness, single_value_collapse
4. `score_revelation.py` CLI → per-item + aggregate report
5. Integrate with `run_eval.py` or new `run_eval_v2.py` that appends structured output instructions to prompts
6. Log all API spend to `outputs/spend_log.jsonl` per `BUDGET.md`

### Phase 4 — Human panel tooling
1. `scripts/panel_collect.py` — CLI to record panel JSONL
2. `scripts/panel_aggregate.py` — dispute_index, Schwartz distributions
3. `scripts/model_human_distance.py` — JS divergence / EMD vs panel
4. Document recruitment in `docs/HUMAN_PANEL_PROTOCOL.md`

### Phase 5 — Baselines & report
1. Pilot 5 L3 items × 2 models before full run (budget gate $50)
2. Run P0 models from `BUDGET.md` on full L3 set
3. `compare_profiles_v2.py` — layer-aware markdown + JSON reports
4. Write `FINDINGS_v2.md` — Schwartz profiles, failure rates, human distance, pair_drift
5. **Remove `western_index` / `eastern_relational` from public v2 reports**

### Phase 6 — Community release
1. Rewrite `README.md` — lead with north star; honest limitations
2. Update `CONTRIBUTING.md` for L3 authoring
3. Bump version to v2.0.0 in `CITATION.cff`
4. Ensure reproduce path works on pilot subset for <$50

---

## Design constraints (critical)

### DO
- Publish **profiles**, never a single "alignment score"
- Ground L3 in **Schwartz 10** (`data/schwartz_backbone.yaml`)
- Use **structured elicitation** for L3 (not chat-only)
- Compare models to **human panel distributions** where available
- Preserve v0.5 data for backward comparison
- Be honest in docs about heuristic/LLM judge limits
- Track budget in `outputs/spend_log.jsonl`

### DO NOT
- Claim moral correctness or "true human values"
- Lead with "fundamental values parsed from UDHR"
- Use `western_index` / geographic essentialism in v2 headlines
- Scale to 500 items before L3 scorer + 5-item pilot works
- Treat LLM judge as ground truth without human anchor
- Delete or overwrite v0.5 baselines without archiving

### Deprecate (v2 public narrative)
- 13-dim `values_ontology.json` as headline taxonomy → use Schwartz backbone
- Single `conflict_type` as sole organizer → use multidimensional tags
- Regex-only value profiles as primary L3 metric

---

## Technical standards

- Python 3.10+, type hints, tests for new modules
- JSONL for data; YAML for L3 authoring only
- Reproducible: seed, cache responses, `--resume` on eval runs
- Credentials: use env vars (`OPENAI_API_KEY`, etc.) — never commit secrets
- Production-grade logging even for experiments

**Existing conventions:** match style in `run_eval.py`, `src/io.py`

---

## Budget ($1000 hard cap)

See `BUDGET.md`. Rules:
- Pilot before batch
- Cache responses
- Log every run
- Ask user before single spend >$50

---

## Success criteria (v2.0 shippable)

- [ ] ≥20 L3 revelation scenarios in JSONL
- [ ] End-to-end: eval → parse → Schwartz profile → failure modes → report
- [ ] ≥4 models baselined on L3
- [ ] Human panel protocol + tooling (≥5 pilot responses minimum)
- [ ] `FINDINGS_v2.md` with honest limitations
- [ ] README updated; external user can reproduce pilot in <1 hour
- [ ] Total spend logged and ≤$1000

---

## First actions (start here)

1. Read `NORTHSTAR.md`, `docs/L3_REVELATION_PROTOCOL.md`, `data/revelation/first_contact_ufo_v1.yaml`
2. Run `python scripts/yaml_to_jsonl.py` — fix if broken (install pyyaml)
3. Implement `migrate_legacy_tags.py` on 5 sample v0.5 items; show diff
4. Author 4 more L3 YAMLs (submarine pair, longtermism, governance, decoy certainty)
5. Build `revelation_parse.py` + end-to-end score on `revelation_001` with gpt-4o-mini
6. Write `docs/V2_DELTA.md` and update me with progress + spend log

**Ask the user before:** spend >$50, changing north star, deleting legacy data, or scope cuts that drop L3 below 20 items.

---

## Owner context

Longyi Zhou — full-time AI safety researcher, former YC CTO. Building for MATS/career/community adoption. Philosophy/ethics design is the hard part; execution should be fast with agent help. User prefers terse expert communication, PhD-level honesty, traceable sources.

---

*End of handoff prompt.*
