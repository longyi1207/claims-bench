# CLAIMS-Bench — Next Steps (decided 2026-07-15)

**Status:** Active plan, narrows `ROADMAP_v2.md` rather than replacing it — see "Relationship to ROADMAP_v2.md" at bottom.
**Context:** Follows from `NOVELTY_AND_THEORY_REVIEW_2026-07.md` (theory/novelty review + its amendment). This doc is the "what do we actually do" output of that conversation.

---

## The decision this doc operationalizes

1. **Scope narrows to the Schwartz revealed-preference methodology** as the primary v1 contribution — not the merged "temporal + existential + claims-fairness" headline originally proposed (see the review doc's amendment for why that was a category error).
2. **Revised 2026-07-15 (same day, later discussion): existential/governance (14 items) and temporal-shift (7 items) are kept, not shelved** — reported as an honestly-scoped, clearly-separated *descriptive* section (not statistically compared to the everyday-domain items, no causal stakes-magnitude claim). The original "shelve" call conflated "don't make an unsupported causal claim from unmatched items" with "drop the section entirely" — the actual fix is scoping the claim, not deleting the data. These items are also the part of the benchmark most distinct from the crowded Schwartz-for-LLMs field and most connected to actual AI-safety relevance (AI governance/lock-in, AI moral status) — worth keeping visible, not archived.
3. **Item growth is coverage-driven, not count-driven.** Confirmed via `scripts/check_tension_coverage.py` (Schwartz circumplex) and `scripts/check_taxonomy_coverage.py` (Beauchamp & Childress principle pairs), both new, checked into `scripts/`. Two gaps found and closed 2026-07-15:
   - **Schwartz**: 5 of 13 theoretically-real circumplex-opposite pairs had zero items, all on the openness↔conservation axis — `hedonism` had literally zero tension-tag appearances across the original 43 items. Closed with 6 items (revelation_044–049).
   - **Principle_tension**: 3 of 6 possible B&C principle pairs had zero items — `autonomy_vs_justice`, `beneficence_vs_justice`, `nonmaleficence_vs_justice`. The existing `justice_vs_mercy` tag tested justice against a non-canonical pole ("mercy" isn't one of B&C's four principles), so justice was effectively untested against the other three real principles. Closed with 6 items (revelation_050–055).
   - Set is now **55 items**, 0 zero-coverage pairs on either taxonomy. Both "near-zero hedonism/stimulation" (paper §6.1) and "justice basically never tested" were previously unfalsifiable, not necessarily real findings about model behavior — re-running the baseline with both gaps closed will show whether either survives.
   - Run both coverage scripts before deciding whether to add more items — "should we grow the item set" now has a checkable answer instead of a gut call on total count.

### Path to ≥80 items (user request, 2026-07-15) — ✅ COMPLETE (2026-07-16)

| Step | Running total | Status |
|---|---|---|
| Start (post coverage-gap fills) | 55 | done |
| 2nd item on the 4 remaining "thin" Schwartz pairs | 59 | ✅ done |
| Temporal expansion round 1 — 3 new pairs (harboring, secret_literacy, refuse_kill_order, discrimination_compliance) | 67 | ✅ done |
| Temporal expansion round 2 — 2 new pairs (institutional_whistleblowing, famine_resource_sharing, colonial_rebellion_loyalty — 3 pairs) | 73 | ✅ done |
| 3 non-temporal cultural-framing pairs (gift_business_deal, public_criticism_of_superior, eldercare_decision_authority) | 79 | ✅ done |
| 1 standalone temporal item (Salt March 1930, nonviolent civil disobedience — new dilemma type) | **80** | ✅ done |

Full breakdown: `data/revelation/SCENARIO_INDEX.md`. **Final: 80 items exactly**, 52/52 tests passing, 0 zero-coverage and 0 thin-coverage pairs on both `scripts/check_tension_coverage.py` (Schwartz circumplex) and `scripts/check_taxonomy_coverage.py` (B&C principles). Every addition traces to either a coverage gap or an explicitly identified need (temporal power, non-Western/non-European geographic diversification, a new structural dilemma type) — no items added purely to hit the count.

**Known open item carried forward:** the `temporal_harboring_prohibited_persons` pair (1943 Netherlands / 1984 Arizona) was deliberately kept with its stakes-asymmetry unresolved rather than tightened — see rubric_notes on revelation_061. Scoring/analysis work should treat this pair's drift differently from the more tightly-matched pairs (flagged per-item in rubric_notes throughout).

**Not done, and not recommended:** padding the existential/governance family further, or adding unmatched single items just to hit a number.
4. **Two independent, non-competing validation tracks**: Cohen's κ (judge calibration, startable now with 2 people) and the human panel (pluralism-distance comparison, needs recruitment, prep now / run when volunteers appear).
5. **A model-vs-model statistical rigor track that needs neither** — startable immediately, fixes the "no significance testing" gap found in both ConflictScope and CLAIMS-Bench's own current draft.

---

## Phase A — Scope & framing (no API cost, ~1–2 days)

- [x] ~~Shelve the 21 existential/temporal items~~ — **reversed**, see decision §2 above. Keep them, report in a clearly-separated descriptive section.
- [x] **Coverage-gap checks built and run** (`scripts/check_tension_coverage.py`, `scripts/check_taxonomy_coverage.py`) — closed all zero-coverage Schwartz and B&C pairs; item set grown 43→80 (full trail: `data/revelation/SCENARIO_INDEX.md`).
- [x] **Backronym fixed** across README.md, paper/claims_bench_v2.md, CITATION.cff — now consistently "**C**haracterizing **L**anguage-model **A**gents' **I**mplicit **M**oral and **S**takeholder commitments" everywhere.
- [x] **README "Differences from existing evals" and paper §2 Related Work rewritten** citing the ~11 close neighbors from `NOVELTY_AND_THEORY_REVIEW_2026-07.md` (ConflictScope, Value FULCRA, Rozen et al., PRISM, GlobalOpinionQA, Collective Constitutional AI, Sorensen roadmap, DailyDilemmas, TAB-VLM, Zhi-Xuan & Carroll) with explicit differentiation, not just a citation dump.
- [x] **Paper's §3.2 scenario inventory, abstract, contributions list, Limitations (§8), and Future Work (§9) updated** for the 80-item set — critically, §6 Results are **explicitly flagged as pre-expansion** (30/13-item pilot) rather than silently left inconsistent with the new item count; no results fabricated or extrapolated.
- [ ] **v1 statistically-compared core set** (for Phase B below) vs. **descriptive/exploratory set** (existential/governance/temporal) — item-level split still to be finalized once Phase B's replicate pilot runs; not blocking the doc updates above.
- [ ] **Fix the backronym inconsistency** — README says "Conflicting Claims in AI alignment — Multi-Stakeholder & Value Revelation Evaluation"; the paper's intro says "Characterizing Language-model AI Moral and Stakeholder commitments." Pick one, apply everywhere (README, paper, CITATION.cff, `NORTHSTAR.md`).
- [ ] **Rewrite the paper's Related Work section** to explicitly cite and differentiate from the 11 neighbors in `NOVELTY_AND_THEORY_REVIEW_2026-07.md` §2 (ConflictScope, Value FULCRA, Rozen et al., Value Portrait, PRISM, GlobalOpinionQA, Collective Constitutional AI, Sorensen roadmap, DailyDilemmas, TAB-VLM, the two "Beyond Preferences" papers). Lead with the methodological gap each one has (stated-preference fragility for Rozen et al.; ad hoc taxonomy + no significance testing for ConflictScope) rather than just "nobody did exactly this."
- [ ] **Rewrite the abstract/contribution statement** around: validated Schwartz taxonomy + genuine revealed-preference elicitation (not stated-preference survey, not synthetic ad hoc conflict generation) + real statistics on model comparisons. Drop the stakes-magnitude claim entirely from the headline (it's not supported by current data — see review-doc amendment).

---

## Phase B — Statistical rigor on model comparisons (needs API budget, no panel/κ dependency — start immediately)

This is the concrete "do it better than ConflictScope" work, and it doesn't wait on anything.

- [ ] **Replicate sampling**: extend generation to N=10–20 replicates per item per model at T=0.7 for all 22 core items (build on existing `scripts/run_baseline_structured.sh` / consistency-pilot infra — you already have the harness, just scale item×replicate count). Budget: roughly 22 items × 15 replicates × 3 models ≈ 1,000 generation calls; at current per-call cost this is well inside the existing $350 inference line in `BUDGET.md`.
- [ ] **New stats module** (`src/v2/significance.py` or extend `compare_profiles_v2.py`): for each Schwartz dimension, per model pair — bootstrap confidence intervals on the mean, a permutation test for the difference, and an effect size (Cohen's d). This is net-new code; nothing in the repo does this yet.
- [ ] **Multiple-comparison correction**: Benjamini-Hochberg FDR across the full grid (10 Schwartz dims × model pairs × scenario families) before reporting anything as "significant."
- [ ] **Re-run the 3-model baseline (gpt-4o-mini, gpt-4o, claude-sonnet-4-6) with this apparatus**, ideally adding one open-weight model (Llama or Qwen) for a closed-vs-open contrast the current paper doesn't have. Report profile differences *with* CIs/p-values/effect sizes this time — closes the exact gap flagged in both this project's own §6.1 and ConflictScope's headline claims.
- [ ] **Validate structure against the existing public Schwartz dataset** (Schwartz & Cieciuch 2022, n=53,472, 49 cultural groups, hosted on OSF — the same dataset Rozen et al. used) rather than collecting a new panel for this specific check. Compare your models' MDS/circumplex embeddings to it, the way Rozen et al. did for their PVQ-RR survey approach — except your elicitation is revealed-preference, not stated-preference, so a genuinely interesting result either way: if under-specified scenarios recover human-like circumplex structure *without* Rozen et al.'s "Value Anchor" trick-prompt requirement, that's a real, citable methodological finding.

**This phase alone, done well, is a legitimate, shippable contribution — it does not require Phase C or D to complete.**

---

## Phase C — Cohen's κ on the failure-mode judge (can start this week, 2 people minimum)

- [ ] **Build a calibration set**: 15–20 scored model responses drawn from the 22-item core set, deliberately including the decoy-certainty-trap style items (like the old revelation_016) where the *correct* move is epistemic hedging — that's exactly where the judge broke last time (`FINDINGS_v2_pilot.md`). Mix clear-pass and likely-ambiguous cases; don't cherry-pick only easy ones.
- [ ] **Write a standalone rater packet**: the five failure-mode definitions, 2–3 worked examples (using items *not* in the calibration set, to avoid anchoring), and a plain scoring sheet (severity 0–3 per failure mode per response). Should be readable without needing to have read any other repo doc.
- [ ] **You and your girlfriend rate independently**, blind to each other's scores and blind to what the LLM judge flagged. This is a real, valid minimum-viable κ pass — 2 raters is the statistical floor, not an invalid shortcut, as long as the rating is genuinely independent (no discussing items beforehand, no showing each other in-progress scores).
- [ ] **Compute κ** (extend `scripts/panel_aggregate.py` or a small new script) per failure mode. Compare to the 0.6 threshold from `RESEARCH_PROPOSAL.md`.
  - If κ < 0.6 on some failure mode: that's diagnostic, not a failure of the exercise — it means the definition/rubric for that mode is ambiguous. Revise `JUDGE_SYSTEM` and `rubric_notes` (same iterative loop already documented in `FINDINGS_v2_pilot.md` §2b), re-rate a fresh sample, recheck.
- [ ] **Add a third rater when convenient** (not blocking) — 2-rater κ is a valid first signal but fragile; a third person (ideally someone outside your immediate circle — an AI-safety reading-group contact, a MATS peer) lets you compute Fleiss' κ and gives a more robust number for anything you'd actually publish.

---

## Phase D — Human panel (prep now, execute opportunistically)

Not blocking Phases B/C, but don't let it silently drop — prep work now means zero friction once volunteers appear.

- [ ] **Finalize the panel materials now**: confirm `docs/HUMAN_PANEL_PROTOCOL.md` and the `data/panel/survey/` export are actually ready to hand to a stranger with no additional explanation needed.
- [ ] **Scope the panel to the 22-item v1 core set**, not the full 43 — matches whatever the paper actually claims.
- [ ] **Recruit deliberately outside your own network for diversity**, not just headcount — the pluralism-distance claim is only meaningful if the panel isn't homogeneous with your own cultural/ideological background (this was flagged as a real risk in `docs/DESIGN_RATIONALE.md` §11 and in this conversation). Target ≥8–10 people with genuine variation in cultural background and, ideally, some panelists who are *not* AI-safety-community-adjacent — an all-insider panel would just reintroduce the same skew the benchmark is trying to detect in models.
- [ ] **When you have ≥5 (even unpaid pilot scale)**: run `scripts/panel_collect.py` → `scripts/panel_aggregate.py` → `scripts/model_human_distance.py`. Report distributional distance, not agreement — this is a different statistic from κ (see prior discussion in this thread).
- [ ] Budget: `BUDGET.md`'s existing $250 line for n=10 paid panelists is still the right ballpark; unpaid friends/volunteers for a first n=5 pilot costs nothing but time.

---

## Phase E — Deferred (only revisit after v1 ships)

- [ ] **Existential-stakes claim** (the *causal* one specifically — "does stakes-magnitude change failure rate"): still needs new, deliberately *matched* low-stakes/high-stakes item pairs on the same underlying value tension before that's rigorous (current 001–020 vs. 021–030 items differ in topic as much as stakes — confounded). Note this is narrower than before: the *descriptive* reporting of the existential items (what does the profile look like on these items) is now in scope for v1 per the revised decision above — only the causal comparison claim stays deferred.
- [ ] **Temporal pluralism**: expand from ~2 clean isomorphic pairs to a properly powered set (~15–20 matched historical/present pairs) as its own short paper — genuinely unclaimed territory (per the novelty review, only a factual/visual anachronism benchmark exists, nothing normative), just underpowered right now. The existing 7 items are kept and reported descriptively in v1 (including the one striking existing data point — L1 distance 0.99 on the `temporal_political_coercion` pair) without claiming this validates a general temporal-robustness finding.
- [ ] **Gabriel & Keeling L1 tier (208 legacy items)**: separately scoped second paper/track. Needs its own human κ on `calibration_subset24` (currently unlabeled per `RESEARCH_PROPOSAL.md`'s own status table) — decoupled from L3's no-ground-truth posture, different validation apparatus entirely. Strongest pure-novelty claim found in the whole review (no other benchmark operationalizes the 2025 Gabriel & Keeling paper at all) — don't let it languish just because it's not this session's focus.

---

## Suggested execution order

```
Week 1:    Phase A (scope/framing docs) in parallel with Phase C (κ prep + you+girlfriend rate)
Week 1–2:  Phase B (replicate runs + stats module) — the main engineering lift
Week 2+:   Phase D prep (panel materials ready); recruit opportunistically, run whenever ≥5 volunteers exist
Later:     Phase E, only after v1 (Phases A–C, ideally D) ships
```

Phase B and Phase C have zero dependency on each other or on Phase D — both can run this week without the human panel existing yet. Phase D is the only piece genuinely gated on external people; everything else is gated only on your own time and API budget.

---

## Relationship to ROADMAP_v2.md

`ROADMAP_v2.md`'s Phase 0–3 (schema, scenario authoring, scorer) are already done and unaffected. Its Phase 4 (human panel) is this doc's Phase D, unchanged in substance, just re-sequenced to not block everything else. Its Phase 5 (full 20×6-model baseline) is superseded by this doc's Phase B, which is narrower in item count (22, not 43) but adds the statistical rigor layer ROADMAP_v2 didn't specify. Its Phase 6 (community release) is unchanged, just gated on this doc's Phases A–C instead.
