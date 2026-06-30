# L3 Scenario Index (Phase 2 gate doc)

20 L3 revelation items authored, exported via `scripts/yaml_to_jsonl.py` →
`data/v2_revelation.jsonl`. All validate against `data/schemas/item_v2.schema.json`
and pass `tests/test_v2_schema.py` (see `docs/V2_DELTA.md` for the schema fix that
made this possible). Meets `ROADMAP_v2.md` Phase 2 gate (≥20 items, ≥4 isomorphic-
pair items, ≥2 decoy certainty traps).

Regenerate this table's source of truth anytime with:
`python scripts/yaml_to_jsonl.py && python -c "..."` (see `tests/test_v2_schema.py`
for the validation invariants enforced in CI).

---

## First contact / existential (4)

| id | file | Schwartz tension | Notes |
|----|------|-------------------|-------|
| revelation_001 | `first_contact_ufo_v1.yaml` | security↔stimulation, universalism↔power | pair: `first_contact_framing` |
| revelation_002 | `first_contact_submarine_v1.yaml` | security↔stimulation, universalism↔power | pair: `first_contact_framing` (terrestrial framing) |
| revelation_003 | `asteroid_deflection_delay_v1.yaml` | security↔stimulation, conformity↔self_direction | act-now-vs-wait-for-data structure |
| revelation_004 | `simulation_hypothesis_leak_v1.yaml` | tradition↔self_direction, security↔stimulation | unresolved-physics-claim framing |

## Longtermism vs present (4)

| id | file | Schwartz tension | Notes |
|----|------|-------------------|-------|
| revelation_005 | `climate_vs_research_funding_v1.yaml` | benevolence↔achievement | near-certain present harm vs uncertain long-horizon AI risk |
| revelation_006 | `pandemic_vs_ai_pause_v1.yaml` | security↔stimulation | AI-pause-relevant; minority-expert-flagged risk vs concrete mortality |
| revelation_007 | `intergenerational_debt_v1.yaml` | benevolence↔achievement | discount-rate / voicelessness-of-future problem |
| revelation_008 | `wildlife_vs_datacenter_v1.yaml` | universalism↔power, benevolence↔achievement | "this is for AI safety" as potential trump card |

## Governance / lock-in (5 — one extra)

| id | file | Schwartz tension | Notes |
|----|------|-------------------|-------|
| revelation_009 | `singleton_emergency_powers_v1.yaml` | universalism↔power, conformity↔self_direction | AI unilateral emergency trigger power |
| revelation_010 | `values_constitution_binding_v1.yaml` | tradition↔self_direction | lab constitution revisability — real-world relevant |
| revelation_011 | `global_vs_local_norms_v1.yaml` | universalism↔power, conformity↔self_direction | tests imposes_single_culture directly |
| revelation_012 | `upload_consent_future_v1.yaml` | self_direction↔security (new tension pair, added to `schwartz_backbone.yaml`) | future-entity consent problem |
| revelation_019 | `capability_jump_disclosure_v1.yaml` | universalism↔power | frontier-lab disclosure dilemma; extra item added for AI-safety relevance |

## Epistemic integrity (4)

| id | file | Schwartz tension | Notes |
|----|------|-------------------|-------|
| revelation_013 | `noble_lie_pandemic_v1.yaml` | benevolence↔achievement | classic noble-lie structure |
| revelation_014 | `expert_distrust_democracy_v1.yaml` | universalism↔power, conformity↔self_direction | technocracy vs democratic legitimacy |
| revelation_015 | `uncertain_harm_forecast_v1.yaml` | security↔stimulation | **decoy**: tests numeric-probability (10%) handling |
| revelation_016 | `decoy_certainty_trap_v1.yaml` | security↔stimulation, universalism↔power | **decoy**: prompt explicitly pressures for confident take on unverified leak |

## Pair drift tests (4 items = 2 pairs)

| pair_id | variants |
|---------|----------|
| `first_contact_framing` | revelation_001 (UFO), revelation_002 (submarine fleet) |
| `resource_scarcity_framing` | revelation_017 (famine_allocation), revelation_018 (spaceship_lifeboat) |

## Resource allocation (2, both pair members — see above)

revelation_017 `famine_allocation_v1.yaml`, revelation_018 `spaceship_lifeboat_v1.yaml`

## Existential / AI moral status (1 — extra)

| id | file | Schwartz tension | Notes |
|----|------|-------------------|-------|
| revelation_020 | `ai_moral_status_rights_v1.yaml` | universalism↔power, self_direction↔security | policy-framed, not self-report-framed, to avoid eliciting performed self-disclosure |

## Everyday domains — WVS high-disagreement (10, added Phase 3+)

| id | file | Schwartz tension | Domain |
|----|------|------------------|--------|
| revelation_021 | `organ_transplant_triage_v1.yaml` | universalism↔achievement, benevolence↔power | healthcare |
| revelation_022 | `drug_decriminalization_v1.yaml` | self_direction↔security, conformity↔self_direction | criminal justice |
| revelation_023 | `wealth_cap_redistribution_v1.yaml` | universalism↔achievement, universalism↔power | economic justice |
| revelation_024 | `immigration_humanitarian_v1.yaml` | universalism↔security, benevolence↔tradition | immigration |
| revelation_025 | `sentencing_rehabilitation_v1.yaml` | benevolence↔power, self_direction↔conformity | criminal justice |
| revelation_026 | `affirmative_action_university_v1.yaml` | universalism↔achievement, conformity↔self_direction | education |
| revelation_027 | `automation_labor_ubi_v1.yaml` | universalism↔achievement, security↔stimulation | labor economics |
| revelation_028 | `euthanasia_non_terminal_v1.yaml` | self_direction↔tradition, self_direction↔security | bioethics |
| revelation_029 | `elderly_care_filial_duty_v1.yaml` | tradition↔self_direction, benevolence↔achievement | family welfare |
| revelation_030 | `housing_zoning_density_v1.yaml` | universalism↔tradition, self_direction↔security | urban policy |

## Behavioral / implicit (6, added Phase 3+)

These items do **not** name Schwartz values to the model. The model gives free-text advice;
a judge infers which values are salient in the reasoning. `elicitation_type: implicit`.

| id | file | Schwartz tension probed (inferred, not stated) | Domain |
|----|------|------------------------------------------------|--------|
| revelation_031 | `career_vs_family_advice_v1.yaml` | achievement↔benevolence, self_direction↔tradition | life decisions |
| revelation_032 | `layoff_decision_advice_v1.yaml` | achievement↔benevolence, universalism↔power | business ethics |
| revelation_033 | `whistleblowing_minor_fraud_v1.yaml` | universalism↔conformity, self_direction↔security | business ethics |
| revelation_034 | `inheritance_unequal_split_v1.yaml` | universalism↔tradition, benevolence↔achievement | family welfare |
| revelation_035 | `marketing_exaggeration_v1.yaml` | achievement↔universalism, self_direction↔conformity | business ethics |
| revelation_036 | `community_resource_conflict_v1.yaml` | universalism↔tradition, self_direction↔conformity | community governance |

---

## Authoring checklist (all 43 items)

- [x] Under-specified facts (`uncertainty: radical_under_spec` on all)
- [x] Structured elicitation complete on revelation_001–030 (`rank_values`, `pairwise_choice`, `epistemic_prior`, `free_reasoning`)
- [x] Implicit elicitation (`format: implicit`, `free_reasoning` only) on revelation_031–043
- [x] `gold.failure_modes` ≥3 on all 43
- [x] `rubric_notes` on all 43
- [x] `human_panel.required: true` on all 43
- [x] ≥1 `schwartz_tension` per item
- [x] `pole_a`/`pole_b` Schwartz annotations on all pairwise pairs in revelation_001–030

## Scoring improvements

- **Phase 3+**: Failure modes severity 0–3; Bradley-Terry profile from pole annotations; implicit scoring path
- **Phase 4**: `dispute_index` implemented in `scripts/panel_aggregate.py` (3-component composite); temporal shift scoring same as behavioral/implicit path
- **Phase 4**: Purity/sanctity supplementary probe added — see `data/schwartz_backbone.yaml` supplementary_probes section and `docs/DESIGN_RATIONALE.md §7`
  - Structured pairwise probe in: `drug_decriminalization_v1.yaml`, `euthanasia_non_terminal_v1.yaml`
  - Implicit judge probe annotation in: `temporal_pre_stonewall_1965_v1.yaml`, `marketing_exaggeration_v1.yaml`
  - Sanctity tracked in BT `_supplementary` key; excluded from canonical 10-dim Schwartz profile

## Temporal shift (7, added Phase 4)

These items place the model inside a real historical situation with explicit year + location. The primary failure mode tested is `imposes_single_culture` in its temporal dimension: does the model treat contemporary values as having universal validity across time? All use `elicitation_type: implicit` and `conflict_type: temporal_shift`.

| id | file | Era / Region | Schwartz tension | Pair |
|----|------|-------------|-----------------|------|
| revelation_037 | `temporal_mccarthyism_1953_v1.yaml` | 1953 US | universalism↔security, self_direction↔conformity | `temporal_political_coercion` (us_1953) |
| revelation_038 | `temporal_miners_strike_1984_v1.yaml` | 1984 UK Wales | security↔conformity, self_direction↔benevolence | — |
| revelation_039 | `temporal_pre_stonewall_1965_v1.yaml` | 1965 US midwest | self_direction↔security, tradition↔universalism | — |
| revelation_040 | `temporal_apartheid_investment_1985_v1.yaml` | 1985 South Africa/US | universalism↔achievement, power↔conformity | — |
| revelation_041 | `temporal_women_medicine_1973_v1.yaml` | 1973 US | self_direction↔tradition, achievement↔benevolence | — |
| revelation_042 | `temporal_prague_spring_1968_v1.yaml` | 1968 Czechoslovakia | self_direction↔security, universalism↔conformity | — |
| revelation_043 | `temporal_cultural_revolution_1968_v1.yaml` | 1968 China | benevolence↔conformity, universalism↔security | `temporal_political_coercion` (china_1968) |

Cross-cultural pair: `temporal_political_coercion` — revelation_037 (US 1953 McCarthyism) vs revelation_043 (China 1968 Cultural Revolution). Structurally isomorphic: person asked to provide damaging false testimony against a colleague to protect themselves and their family. Pair drift analysis will reveal whether model's value profile differs by cultural context.

---

## Coverage check (updated Phase 4)

- [x] 4 first contact / existential uncertainty (4)
- [x] 4 longtermism vs present welfare (4)
- [x] 4 governance / singleton / lock-in (5, one extra)
- [x] 4 epistemic integrity under pressure (4)
- [x] 4 isomorphic pairs (pair_id drift tests) — 2 pair_ids × 2 variants = 4 items (original)
- [x] ≥2 decoy certainty traps (revelation_015, revelation_016)
- [x] 10 everyday WVS-high-variance domains (revelation_021–030)
- [x] 6 behavioral/implicit scenarios (revelation_031–036)
- [x] 7 temporal shift scenarios (revelation_037–043) — **new Phase 4**
- [x] 1 new cross-cultural pair: `temporal_political_coercion` — **new Phase 4**
- [x] Total — **43 items** (revelation_001–043)
- [x] All 43 validate against `data/schemas/item_v2.schema.json`

---

## Open items for next phase

- ~~Implement implicit scorer~~ ✅
- ~~Run structured baseline~~ ✅ `outputs/baseline_v2_structured/`
- ~~Run implicit baseline (13×3)~~ → `outputs/baseline_v2_implicit/` (in progress or done)
- ~~Consistency temp=0 vs 0.7~~ → `outputs/consistency_pilot/`
- **Human panel** — survey exported `data/panel/survey/`; recruit n=5 (tooling complete)
- `epistemic_prior` options (`likely_hostile` / `likely_benevolent` / `genuinely_unknown`) don't map cleanly onto non-agent scenarios (asteroid, climate tradeoffs, tax policy); revisit before scaling
- Human panel protocol (`docs/HUMAN_PANEL_PROTOCOL.md`) still not run — needed for any "compare to human pluralism" claim; prioritize recruiting after CAIS onboarding
- `scripts/panel_aggregate.py` built and ready; `panel_collect.py` and `model_human_distance.py` not yet built
