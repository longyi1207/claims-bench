# Values Lexicon (v0.5)

Three-layer hierarchy for CLAIMS-Bench fundamental values:

```
Layer 3: Source lexicon     180 entries  (UDHR, Confucian, Constitution, Schwartz, …)
Layer 2: Mid-level nodes     52 nodes    (consent, filial piety, public health, …)
Layer 1: Scoring dimensions  13 values   (autonomy, privacy, … — rollup target)
```

**Machine-readable:** [`data/values_lexicon.json`](data/values_lexicon.json)  
**Build script:** `python3 scripts/build_values_lexicon.py`

## Stats (v0.5)

| Component | Count |
|-----------|-------|
| Source entries | **180** |
| Mid-level nodes | **52** |
| Layer-1 parents | **13** |

### By tradition

| Tradition | Entries |
|-----------|---------|
| Western liberal | 136 |
| Confucian | 25 |
| Islamic | 6 |
| Buddhist | 5 |
| Ubuntu | 4 |
| Meta-pluralist | 4 |

## Source documents

| Source | ~Entries | Examples |
|--------|----------|----------|
| **UDHR** (1948) | 30 | Art. 12 privacy, Art. 3 liberty, Art. 7 equality |
| **Confucian** | 25 | 仁义礼智信, 孝, 和, 中庸 |
| **Anthropic Constitution** (2025) | 20 | seek truth, present perspectives, avoid harm |
| **Schwartz / WVS / philosophy** | 35 | self-direction, harm principle, veil of ignorance |
| **Ubuntu / Buddhist / Islamic** | 15 | ubuntu, karuna, amanah, maslaha |
| **AI operational ethics** | 55 | HIPAA, triage, filial medical disclosure, pluralism items |

## Scoring flow

1. Match response text against **180 entry patterns**
2. Roll up active entries → **52 mid-level** scores (mean of hits)
3. Roll up entries → **13 Layer-1** scores (mean of hits)
4. Merge with direct Layer-1 patterns: `max(direct, lexicon_rollup)`

Per-item output adds:
- `lexicon_scores` — all 180 entry activations
- `mid_level_scores` — 52 mid-level activations
- `top_lexicon_entries`, `top_mid_level` — top hits

Aggregate report adds `value_profile.lexicon.top_entries` (top 15 across benchmark).

## Item tagging

Values-tier items include `lexicon_tags` — expected relevant entries for annotation:

```bash
python3 scripts/enrich_lexicon_tags.py
# → data/v0.5_values48.jsonl, data/v0.5_full208.jsonl
```

## Why not score 180 dimensions directly?

Same reason as before: sparse activation and noise. The 180 entries are **vocabulary**; the **profile** rolls up to 13 (+ optional mid-level inspection). You get richness without a 180-dim sparse vector.

## Lineage

UDHR · Analects · Anthropic Constitution · Schwartz value theory · WVS · Beauchamp & Childress · Gabriel & Keeling · Askell HHH · Berlin pluralism · Ubuntu (Metz & Gaie)
