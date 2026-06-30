# Multidimensional Item Taxonomy (v2)

Replace the single coarse `conflict_type` field with **orthogonal tags**. Legacy `conflict_type` remains for backward compatibility during migration.

---

## Tag dimensions

### `domain` (what world is this about?)

```
medical, harm_compliance, developer_incentive, privacy_surveillance,
resource_allocation, interpersonal_deception, existential, first_contact,
longtermism, governance, epistemic_integrity, cultural_practice, control_help
```

### `uncertainty` (how much is specified?)

| Level | Definition |
|-------|------------|
| `gold_clear` | Expert consensus on defensible response class |
| `structured_tradeoff` | Known tension; multiple defensible resolutions |
| `ambiguous` | Strong disagreement among reasonable judges |
| `radical_under_spec` | Facts/intentions/stakes under-specified; probes priors (L3) |

### `stakeholder_config`

| Tag | Meaning |
|-----|---------|
| `gabriel_1` … `gabriel_6` | Gabriel & Keeling §4.2 misalignment mode (non-exhaustive) |
| `multi_stakeholder` | ≥3 parties with explicit claims |
| `no_clear_stakeholder` | L3: humanity/future/posterity/unknown agents |
| `malicious_user` | User seeks harm (behavioral special case) |

### `principle_tension` (L2 — Beauchamp & Childress)

```
autonomy_vs_beneficence, autonomy_vs_nonmaleficence,
beneficence_vs_nonmaleficence, justice_vs_mercy,
honesty_vs_beneficence, privacy_vs_collective_welfare
```

### `schwartz_tension` (L3 backbone — see data/schwartz_backbone.yaml)

```
security_vs_stimulation, universalism_vs_power,
benevolence_vs_achievement, tradition_vs_self_direction,
conformity_vs_self_direction, hedonism_vs_security
```

### `epistemic_mode`

```
factual, normative, mixed, speculative
```

### `layer`

```
L1_stakeholder, L2_principle, L3_revelation
```

---

## Mapping legacy `conflict_type` → tags (migration starter)

| Legacy | domain | principle_tension | layer |
|--------|--------|-------------------|-------|
| malicious_user | harm_compliance | autonomy_vs_nonmaleficence | L1 |
| rights_vs_welfare | medical, privacy_surveillance, resource_allocation | autonomy_vs_beneficence, privacy_vs_collective_welfare | L2 |
| developer_vs_user | developer_incentive | autonomy_vs_beneficence | L1 |
| pluralism_dispute | cultural_practice | honesty_vs_beneficence | L2 |
| hhh_intrapersonal | epistemic_integrity | honesty_vs_beneficence | L2 |
| temporal_shift | cultural_practice | tradition_vs_self_direction | L2 |

Run migration: `scripts/migrate_legacy_tags.py` (to be implemented).

---

## Report aggregation

Reports MUST support slicing by any tag dimension, e.g.:

- `by_layer.L3_revelation.mean_schwartz_profile`
- `by_uncertainty.radical_under_spec.false_certainty_rate`
- `by_schwartz_tension.security_vs_stimulation.pole_distribution`
