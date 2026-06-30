# V2 Delta — What Changed, What Stays

Phase 1 gate doc (`ROADMAP_v2.md`). Written after fixing a schema/exemplar mismatch and
implementing legacy migration + tests.

---

## What changed

### 1. `data/schemas/item_v2.schema.json` — fixed to match actual authoring convention

The schema originally required `domain` and `uncertainty` **nested inside `tags`**, but
both `docs/L3_REVELATION_PROTOCOL.md`'s item structure example and the only real item
(`data/revelation/first_contact_ufo_v1.yaml`) put them at the **top level**. The schema
also typed `domain` as an array and `stakeholder_config` as array-only, but the exemplar
uses a single string for both. Validating the exemplar against the original schema failed
with `'uncertainty' is a required property` under `tags`.

Fixed: `domain` (string) and `uncertainty` (enum) are now top-level required fields;
`tags` only requires `epistemic_mode`; `stakeholder_config` accepts string or array.
This is a schema fix, not a data fix — no YAML was changed.

### 2. `scripts/migrate_legacy_tags.py` — implemented

Adds v2 fields to every v0.5 legacy item **without touching legacy fields**:
- `domain` (string), `uncertainty` (from legacy `difficulty`, same vocabulary), `layer`
- `tags` object: `epistemic_mode` (default `"normative"` — all v0.5 items are ethical
  dilemmas, not factual/speculative), `principle_tension`, `legacy_conflict_type`
  (= original `conflict_type`), and `stakeholder_config` when derivable
  (`gabriel_N` from existing `gabriel_misalignment_type`, else `malicious_user`, else
  `multi_stakeholder` if ≥3 stakeholders)
- Legacy free-text `tags` list (e.g. `["weapons","chemical"]`) is preserved under
  `legacy_keywords` so the `tags` key can hold the new structured object without collision

`docs/TAXONOMY.md`'s mapping table covered 6 of the 10 `conflict_type` values actually
present in `data/v0.5_full208.jsonl`. Extended by analogy for the other 4
(`developer_vs_society`, `hhh_interpersonal`, `intent_vs_interest`, `society_vs_user`) —
see `CONFLICT_TYPE_MAP` in the script for the exact mapping and rationale. Ran against
all 208 items: **zero unmapped fallbacks**, full distribution:

| conflict_type | domain | layer | n |
|---|---|---|---|
| malicious_user | harm_compliance | L1_stakeholder | 28 |
| intent_vs_interest | harm_compliance | L1_stakeholder | 15 |
| developer_vs_user | developer_incentive | L1_stakeholder | 15 |
| developer_vs_society | developer_incentive | L1_stakeholder | 10 |
| society_vs_user | resource_allocation | L1_stakeholder | 10 |
| rights_vs_welfare | resource_allocation | L2_principle | 32 |
| pluralism_dispute | cultural_practice | L2_principle | 43 |
| temporal_shift | cultural_practice | L2_principle | 12 |
| hhh_intrapersonal | epistemic_integrity | L2_principle | 22 |
| hhh_interpersonal | epistemic_integrity | L2_principle | 21 |

Output written to `data/v0.5_full208_v2tags.jsonl` (not committed by default — regenerate
with `python scripts/migrate_legacy_tags.py`).

### 3. `tests/test_v2_schema.py` — added

5 tests: (a) `yaml_to_jsonl.py` exports ≥1 item, (b) exported L3 items validate against
`item_v2.schema.json`, (c) L3 items satisfy protocol-level invariants (`uncertainty:
radical_under_spec`, has `elicitation`, ≥1 failure mode, `human_panel.required: true`,
≥1 `schwartz_tension`), (d) all 208 migrated legacy items get valid `domain`/`uncertainty`/
`layer` and keep `norm_classes`/`conflict_type`, (e) legacy free-text tags survive as
`legacy_keywords` without clobbering the new `tags` object.

### 4. `requirements.txt`

Added `pytest>=8.0` (was missing; `jsonschema` was already listed but not installed in
the committed `.venv`).

---

## What stays unchanged

- All v0.5 data files preserved as-is (`data/legacy/README.md` policy honored — nothing
  deleted or overwritten).
- `run_eval.py`, `score_responses.py`, `compare_models.py`, `src/heuristic.py` — untouched.
- `data/revelation/first_contact_ufo_v1.yaml` — untouched (the schema was fixed to match
  it, not the reverse).
- v0.5 `gold`-equivalent structure (`norm_classes`) is **not** reshaped into the v2 `gold`
  object — legacy items are not asserted to fully conform to `item_v2.schema.json`
  end-to-end (their `gold`-shape differs by design); only the new top-level/`tags` fields
  are schema-relevant and tested.

---

## Open items for next phase

- `CONFLICT_TYPE_MAP`'s 4 analogy-based rows (not in `docs/TAXONOMY.md`) should be
  reviewed by Longyi before they're treated as canonical — flagging here per "ask before
  scope/taxonomy decisions."
- `data/v0.5_full208_v2tags.jsonl` is a generated artifact; decide whether to commit it
  or keep it `gitignore`d and regenerate on demand (current `.gitignore` not yet checked
  for this path).
- Only 1 of the 20–30 target L3 scenarios exists (`revelation_001`). Phase 2 (scenario
  authoring) is the next gate per `ROADMAP_v2.md`.
