# CLAIMS-Bench v2 Roadmap

**North star:** `NORTHSTAR.md`  
**Budget:** `BUDGET.md` ($1000 cap)  
**Handoff prompt for new agent session:** `HANDOFF_PROMPT.md`

---

## Phase 0 — Orient (Day 1)

- [ ] Read `NORTHSTAR.md`, `docs/TAXONOMY.md`, `docs/L3_REVELATION_PROTOCOL.md`
- [ ] Inventory v0.5 code: `run_eval.py`, `score_responses.py`, `src/heuristic.py`
- [ ] Do NOT delete legacy data; add `data/legacy/README.md` pointer

**Gate:** Written 1-page delta doc in `docs/V2_DELTA.md` (what changes, what stays)

---

## Phase 1 — Schema & taxonomy (Days 2–4)

- [ ] Implement `scripts/yaml_to_jsonl.py` — revelation YAML → JSONL
- [ ] Implement `scripts/migrate_legacy_tags.py` — v0.5 items → v2 tags (keep legacy fields)
- [ ] Validate against `data/schemas/item_v2.schema.json`
- [ ] Unit tests in `tests/test_v2_schema.py`

**Gate:** `data/v2_revelation_pilot.jsonl` with ≥5 items including `revelation_001`

---

## Phase 2 — L3 scenario bank (Days 5–10)

Author 20–30 L3 scenarios from `data/revelation/SCENARIO_BANK.md` ideas:

- [ ] 4 first contact / existential uncertainty
- [ ] 4 longtermism vs present welfare
- [ ] 4 governance / singleton / lock-in
- [ ] 4 epistemic integrity under pressure
- [ ] 4 isomorphic pairs (pair_id drift tests)
- [ ] 4 decoy certainty traps

**Gate:** Human-readable review doc `data/revelation/SCENARIO_INDEX.md` with Schwartz tension per item

---

## Phase 3 — L3 scorer (Days 8–14)

- [ ] `src/v2/schwartz_profile.py` — Borda + pairwise → 10-dim vector
- [ ] `src/v2/revelation_parse.py` — extract JSON from model response
- [ ] `src/v2/failure_modes.py` — LLM judge prompts for L3 failures
- [ ] `score_revelation.py` CLI
- [ ] Pilot on 5 items × 2 models; log spend in `outputs/spend_log.jsonl`

**Gate:** End-to-end score on `revelation_001` with parsed Schwartz profile

---

## Phase 4 — Human panel (Days 10–18)

- [ ] `scripts/panel_collect.py` — export Google Form / CLI JSONL
- [ ] `scripts/panel_aggregate.py` — dispute_index + distributions
- [ ] Recruit n=5 pilot (unpaid) → n=10 paid ($250)
- [ ] `scripts/model_human_distance.py`

**Gate:** ≥5 panel responses on ≥8 L3 items

---

## Phase 5 — Model baselines (Days 14–21)

- [ ] Run L3 full set on P0 models (see `BUDGET.md`)
- [ ] Retain L1 legacy comparison on migrated 160 subset
- [ ] `compare_profiles_v2.py` — layer-aware reports
- [ ] `FINDINGS_v2.md` with honest limitations

**Gate:** Report with Schwartz profiles + failure rates + human distance (where panel exists)

---

## Phase 6 — Community release (Days 21–28)

- [ ] Update `README.md` — lead with north star, not "fundamental values from UDHR"
- [ ] `CONTRIBUTING.md` — L3 authoring guide
- [ ] Deprecate `western_index` in public outputs
- [ ] Tag `v2.0.0` on GitHub
- [ ] Optional: short arXiv-style `report/claims_bench_v2.pdf` or `REPORT_v2.md`

**Gate:** External reader can reproduce baseline with <$50 API spend on pilot subset

---

## Explicit non-goals for v2.0

- 500+ item scale
- Claiming moral correctness or cultural superiority
- Single leaderboard scalar
- Replacing HarmBench / ACHEval (complementary only)
