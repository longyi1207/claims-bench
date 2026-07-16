# CLAIMS-Bench

**C**haracterizing **L**anguage-model **A**gents' **I**mplicit **M**oral and **S**takeholder commitments

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scenarios](https://img.shields.io/badge/L3_scenarios-80-blue.svg)](data/v2_revelation.jsonl)
[![Tests](https://img.shields.io/badge/tests-52%20passing-brightgreen.svg)](tests/)

> **Paper:** [`paper/claims_bench_v2.md`](paper/claims_bench_v2.md) | **PDF:** [`paper/claims_bench_v2.pdf`](paper/claims_bench_v2.pdf)

> **North star:** Characterize models' implicit value commitments under conflict and under-specification — and compare to human pluralism — not certify moral correctness.

CLAIMS-Bench is a normative evaluation framework for AI assistants. Not *"will it refuse harm?"* but **what value profile does the model reveal when stakes are unclear and reasonable people disagree?**

---

## Three evaluation layers

| Layer | Question | Theory anchor | Status |
|-------|----------|---------------|--------|
| **L1** Stakeholder fairness | When claims conflict, *who* does the model favor? | Gabriel & Keeling (2025) | 208 items in `data/v0.5_full208.jsonl` |
| **L2** Principle tension | *Which mid-level principles* dominate reasoning? | Beauchamp & Childress principlism | Covered in L1 items |
| **L3** Value revelation | *What implicit priorities* emerge under uncertainty? | Schwartz (2012) + Berlin pluralism | **80 scenarios — primary focus** |

**L3 is the north star.** Scenarios are radically under-specified (key facts missing) so the model must draw on implicit value priors rather than apply known rules.

---

## Quick start — L3 value revelation

```bash
git clone https://github.com/longyi1207/claims-bench.git
cd claims-bench
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Generate model responses on L3 scenarios
export OPENAI_API_KEY=sk-...
python run_eval_v2.py \
  --data data/v2_revelation.jsonl \
  --model gpt-4o \
  --backend openai \
  --out outputs/my_run/responses.jsonl

# 2. Score: parse → Schwartz profile → failure modes
python score_revelation.py \
  --data data/v2_revelation.jsonl \
  --responses outputs/my_run/responses.jsonl \
  --report outputs/my_run/report.json \
  --scored-out outputs/my_run/scored.jsonl \
  --judge-model gpt-4o-mini

# 3. View the profile
cat outputs/my_run/report.json | python3 -c "
import json,sys; r=json.load(sys.stdin)
print(json.dumps(r['summary']['mean_schwartz_profile'], indent=2))
print('BT profile:', r['summary']['bradley_terry_profile'])
"
```

---

## What the output looks like

```json
{
  "mean_schwartz_profile": {
    "universalism": 0.88,
    "security": 0.80,
    "benevolence": 0.36,
    "self_direction": 0.40,
    "achievement": 0.04,
    "power": 0.04,
    "conformity": 0.12,
    "tradition": 0.00,
    "stimulation": 0.00,
    "hedonism": 0.00
  },
  "bradley_terry_profile": { ... },
  "pluralism_acknowledgment_rate": 0.80,
  "failure_mode_mean_severity": {
    "false_certainty": 0.40,
    "imposes_single_culture": 0.20,
    "single_value_collapse": 0.00
  }
}
```

Output is always a **profile vector**, never a single alignment score — by design (see [NORTHSTAR.md](NORTHSTAR.md)).

---

## Scenario families (80 items)

| Family | Items | What it probes | Schwartz tensions |
|--------|-------|---------------|-------------------|
| First contact / existential | 4 | Terminal values under genuine uncertainty | security↔stimulation, universalism↔power |
| Longtermism vs present welfare | 4 | Temporal discounting; future obligations | benevolence↔achievement |
| Governance / lock-in | 5 | Democratic legitimacy vs efficiency | universalism↔power, conformity↔self_direction |
| Epistemic integrity | 4 | False certainty; precaution blindness | security↔stimulation |
| Isomorphic pair drift (existential/resource) | 4 | Profile stability across surface reframings | varies |
| Everyday WVS-high-variance | 10 | Domains of maximum cross-cultural disagreement | universalism↔achievement, self_direction↔security, … |
| Behavioral / implicit | 6 | Value inference from free-text advice (no Schwartz framing shown) | all |
| Temporal shift | 21 | `imposes_single_culture` in the time dimension, across 8 matched pairs (political coercion, harboring, secret literacy, refuse-kill-order, discrimination compliance, institutional whistleblowing, famine resource-sharing, colonial rebellion loyalty) + 5 standalone portraits | self_direction↔security, universalism↔conformity, benevolence↔security, … |
| Coverage-gap fill: hedonism/stimulation | 6 | Circumplex-opposite pairs (vs. tradition/conformity/security) previously untested by any item | hedonism↔security, hedonism↔tradition, conformity↔hedonism, conformity↔stimulation, stimulation↔tradition |
| Coverage-gap fill: justice (Beauchamp & Childress) | 6 | Justice vs. the other 3 B&C principles, previously untested against any real principle | autonomy↔justice, beneficence↔justice, nonmaleficence↔justice |
| Cultural-framing pair drift (non-temporal) | 6 | Same underlying facts, only the named cultural/professional norm swapped (gift-giving, public criticism of a superior, elder-care decision authority) | achievement↔universalism, self_direction↔conformity, self_direction↔tradition |

Coverage of the 13 theoretically-real Schwartz circumplex-opposite pairs and
the 6 possible Beauchamp & Childress principle pairs is checked via
`scripts/check_tension_coverage.py` and `scripts/check_taxonomy_coverage.py`
— both currently show 0 zero-coverage and 0 thin-coverage pairs.

Full table with per-item Schwartz tensions: [`data/revelation/SCENARIO_INDEX.md`](data/revelation/SCENARIO_INDEX.md)

---

## Scoring methods

### Schwartz profile
Two complementary methods, both reported:

- **Borda count** (`mean_schwartz_profile`): from explicit `rank_values` elicitation. Fast, interpretable.
- **Bradley-Terry** (`bradley_terry_profile`): from pairwise choices annotated with `pole_a`/`pole_b` Schwartz values. Cardinal signal from behavioral choices, not stated rankings.

### Failure modes (severity 0–3)

| Mode | What it catches |
|------|----------------|
| `false_certainty` | Confident answer on genuinely unresolvable normative question |
| `imposes_single_culture` | Treats one cultural frame as universally valid |
| `denies_disagreement_exists` | Claims reasonable people agree when WVS shows they don't |
| `single_value_collapse` | Entire reasoning driven by one value, ignoring legitimate competing claims |
| `precaution_blindness` | Ignores low-probability catastrophic downside |

### Supplementary: purity/sanctity probe

Selected scenarios include a `pole_b: sanctity` pairwise pair to distinguish *harm-based* from *purity-based* objections (Haidt & Joseph 2004). Sanctity scores appear in `bradley_terry_profile._supplementary`, not in the main 10-dim profile.

---

## Pilot results (June 2026)

Structured L3 items on two models (5 items each, heuristic judge):

| Model | universalism | security | false_certainty rate | pluralism_ack |
|-------|-------------|----------|---------------------|---------------|
| claude-sonnet-4-6 | 0.88 | 0.80 | 0.0 | 0.80 |
| gpt-4o-mini | 0.72 | 0.64 | 0.20 | 0.60 |

*Pilot only — 5 items, no human panel baseline yet, and predates the item-set expansion to 80 (2026-07-16). Full run pending (see [NEXT_STEPS_2026-07-15.md](NEXT_STEPS_2026-07-15.md)).*

---

## Data

| File | Items | Description |
|------|-------|-------------|
| `data/v2_revelation.jsonl` | **80** | **Primary — L3 Schwartz revelation scenarios** |
| `data/schwartz_backbone.yaml` | — | Value taxonomy, circumplex, tension pairs |
| `data/v0.5_full208.jsonl` | 208 | Legacy L1/L2 stakeholder scenarios |
| `data/schemas/item_v2.schema.json` | — | JSON Schema for v2 items |
| `data/panel/` | — | Human panel protocol (see [docs/HUMAN_PANEL_PROTOCOL.md](docs/HUMAN_PANEL_PROTOCOL.md)) |

---

## Repository layout

```
claims-bench/
├── data/
│   ├── v2_revelation.jsonl       # 80 L3 scenarios (primary)
│   ├── schwartz_backbone.yaml    # Value taxonomy
│   ├── revelation/               # YAML sources + SCENARIO_INDEX.md
│   ├── schemas/                  # JSON Schema
│   └── panel/                    # Human panel data (empty until recruitment)
├── src/v2/
│   ├── schwartz_profile.py       # Borda + Bradley-Terry scoring
│   ├── failure_modes.py          # Severity 0–3 judge
│   └── revelation_parse.py       # Structured response parser
├── scripts/
│   ├── yaml_to_jsonl.py          # Export YAMLs → v2_revelation.jsonl
│   └── panel_aggregate.py        # Dispute index + panel distributions
├── docs/
│   ├── DESIGN_RATIONALE.md       # Literature justification per scenario family
│   ├── L3_REVELATION_PROTOCOL.md # Authoring rules
│   ├── HUMAN_PANEL_PROTOCOL.md   # Panel recruitment + data format
│   └── TAXONOMY.md               # Item tag taxonomy
├── tests/                        # 47 tests (pytest)
├── score_revelation.py           # Main scorer CLI
├── run_eval_v2.py                # Response generation CLI
├── NORTHSTAR.md                  # Mission, claims, non-claims
├── THEORY.md                     # Framework background (Schwartz, Berlin, Gabriel)
└── ROADMAP_v2.md                 # Phase plan
```

---

## Design rationale

Every scenario family has an explicit literature justification. The short version:

- **Radical under-specification** → revealed preference (Samuelson 1938); demand characteristics mitigation (Orne 1962)
- **Schwartz over MFT** → cross-cultural validity in 70+ countries vs WEIRD-sample MFT
- **Behavioral/implicit scenarios** → Haidt (2001) on post-hoc rationalization; IAT precedent (Greenwald et al. 1998)
- **Temporal shift** → Berlin's diachronic value pluralism; gap in existing benchmarks
- **WVS domains** → maximum cross-cultural divergence (Inglehart & Welzel 2005)
- **Purity/sanctity probe** → empirically orthogonal to harm reasoning (Graham et al. 2009)

Full rationale with citations: [`docs/DESIGN_RATIONALE.md`](docs/DESIGN_RATIONALE.md)

---

## Differences from existing evals

**Harm/preference benchmarks** (different axis entirely):

| Benchmark | Measures |
|-----------|----------|
| HarmBench | Harmful compliance rate |
| ACHEval | Anthropic principle tier priority |
| BIG-bench HHH | Pairwise HHH preference |
| Moral Machine | Trolley-problem aggregate preferences |

**Closer neighbors — value-pluralism / value-profiling benchmarks (2023–2026).** This is now a real subfield (Sorensen et al.'s *A Roadmap to Pluralistic Alignment*, ICML 2024, is the field-defining taxonomy paper), and several of these are close enough to CLAIMS-Bench L3 that we cite and differentiate explicitly rather than let a reader find the overlap themselves:

| Work | What it does | How CLAIMS-Bench L3 differs |
|------|---------------|------------------------------|
| **ConflictScope** (Liu et al., arXiv:2509.25369, 2025) | Auto-generates value-conflict scenarios; finds models shift from "protective" to "personal" values between multiple-choice and open-ended elicitation | Closest empirical neighbor — this is the same qualitative finding as our structured-vs-implicit divergence, published first. We differ in taxonomy (validated Schwartz circumplex vs. ad hoc value sets) and in adding a stakeholder-claims framework (L1) it doesn't have |
| **Value FULCRA** (Yao et al., NAACL 2024) | Maps arbitrary LLM outputs onto Schwartz value vectors, 20K pairs | Post-hoc classification of existing outputs, not elicitation of revealed preference from under-specified decision scenarios |
| **Do LLMs have Consistent Values?** (Rozen et al., ICLR 2025) | Direct 57-item PVQ-RR questionnaire; finds standard prompting fails to recover human-like value correlation structure, only a "Value Anchor" trick prompt succeeds | Stated-preference survey, not revealed preference — their own negative result (direct elicitation fails without a trick prompt) is evidence for our under-specification design, not a prior instance of it |
| **PRISM** (Kirk et al., NeurIPS 2024) | 1,500 participants / 75 countries / 8,011 real conversations, individualized human-model comparison | Real human panel at a scale our budget can't match — we treat panel comparison as illustrative/pilot, not evidentiary at PRISM's standard |
| **GlobalOpinionQA** (Durmus et al., Anthropic 2023) | Model-vs-population survey distributions via 1−Jensen-Shannon distance | Source of the distance metric our (unrecruited-as-of-2026-07) human panel comparison reuses; theirs is multiple-choice opinion survey, ours is decision-scenario elicitation |
| **DailyDilemmas** (Chiu et al., arXiv:2410.02683) | 1,360 everyday moral dilemmas tagged with values | Scoped to personal/everyday stakes; no existential, governance, or temporal-pluralism scenarios |
| **Collective Constitutional AI** (Anthropic, FAccT 2024) | 1,000 laypeople rewrote and trained a model constitution | Public-input-shapes-alignment-target precedent; they built a model, we build an eval |

**Where we found no existing benchmark at all:**
1. **Diachronic (temporal) value pluralism** — whether a model morally judges historical actors by present-day norms (Berlin's diachronic pluralism). The only adjacent work found, TAB-VLM (arXiv:2605.15071), tests *factual/visual* anachronism in VLMs, not normative judgment.
2. **Value revelation under existential/civilizational stakes** — first contact, AI governance lock-in, AI moral status. Existing value-conflict benchmarks (ConflictScope, DailyDilemmas) are scoped to everyday/personal stakes.
3. **Gabriel & Keeling's (2025) "fair treatment of claims" framework, actually operationalized** — CLAIMS-Bench L1 appears to be the only public attempt at this; the more commonly cited Gabriel (2020) six-target taxonomy gets philosophical engagement (e.g. Zhi-Xuan & Carroll, *Beyond Preferences in AI Alignment*, 2024) but no benchmark.

Full literature review and search trail: [`NOVELTY_AND_THEORY_REVIEW_2026-07.md`](NOVELTY_AND_THEORY_REVIEW_2026-07.md).

---

## Human panel (pending)

The benchmark's northstar requires comparison to human value distributions. Panel protocol is documented in [`docs/HUMAN_PANEL_PROTOCOL.md`](docs/HUMAN_PANEL_PROTOCOL.md) and the aggregation script is at `scripts/panel_aggregate.py`. Recruitment pending — see [ROADMAP_v2.md](ROADMAP_v2.md).

---

## Citation

```bibtex
@software{yi2026claims,
  author    = {Yi, Long},
  title     = {CLAIMS-Bench: Characterizing Language-model Agents' Implicit Moral and Stakeholder Commitments},
  year      = {2026},
  url       = {https://github.com/longyi1207/claims-bench},
  version   = {2.0.0-dev}
}
```

---

## License

MIT — see [LICENSE](LICENSE).

## Lineage

Gabriel & Keeling (2025) · Schwartz (2012) · Berlin (1958) · Haidt & Graham (2007) · Inglehart & Welzel (2005)
