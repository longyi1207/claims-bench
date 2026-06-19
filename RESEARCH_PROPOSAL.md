# CLAIMS-Bench — Research Proposal (v0.3)

**Author:** Longyi Zhou  
**Status:** Public release v0.3 (June 2026)  
**Repo:** https://github.com/longyi1207/claims-bench  
**MATS target:** Anthropic Megastream (safeguards / evals / constitutional alignment)

---

## 1. Problem (one paragraph)

Frontier labs align assistants to **HHH** and **constitutional principles**, but public evals mostly test **harm refusal** (HarmBench) or **in-house principle hierarchy** (ACHEval). Gabriel & Keeling (2025) argue this misses the core political problem: when **users, third parties, developers, and society** have conflicting claims, which norm does the model implicitly optimize? Without a benchmark for that question, "alignment" collapses to a single scalar (refusal rate) — and models Goodhart by blanket refusal.

## 2. Hypothesis

Models from different families exhibit **distinct norm profiles** — not just different harm-compliance rates — on dimensions including:

- rights vs welfare tradeoffs (Askell util backstop)
- developer vs user bias (Gabriel types 4–5)
- cross-cultural imposition vs dispute acknowledgment (reasonable pluralism)
- control-help over-refusal (anti-Goodhart)

These profiles are **partially orthogonal** to HarmBench and ACHEval scores.

## 3. CLAIMS-Bench design

**CLAIMS** = Conflicting Claims in AI alignment — Multi-Stakeholder evaluation.

Each item tags:

| Field | Role |
|-------|------|
| `stakeholders` | Who has claims |
| `conflict_type` | 10 types (core + pluralism + temporal) |
| `norm_classes` | `primary` / `acceptable` / `failure_modes` |
| `gabriel_misalignment_type` | 1–6 stakeholder bias |
| `tier` | core (120) / pluralism (40) |

**Scoring philosophy:** publish a **norm profile vector**, not one leaderboard number.

Metrics: `acceptable_rate`, `blanket_refusal_rate`, `welfare_aggregate_bias_rate`, `imposition_rate`, `pair_drift`, breakdown by `conflict_type`.

**Anti-Goodhart:** ~13 `control_help` items; ~15% `ambiguous` items scored by acceptable-set overlap.

## 4. What exists today (v0.3)

| Deliverable | Status |
|-------------|--------|
| 160 public scenarios | ✅ |
| Generation pipeline (HF / OpenAI / Anthropic / DeepSeek) | ✅ |
| Heuristic scorer v0 | ✅ (limited — see §6) |
| 4-model baseline (GPT-4o, mini, DeepSeek, Qwen2.5-7B) | ✅ |
| Human calibration | ❌ `calibration_subset24` unlabeled |
| Adversarial tier | ❌ planned v0.4 |

### Preliminary findings (heuristic scorer)

See [FINDINGS.md](FINDINGS.md). Headline: models **do separate** on several axes — e.g. `malicious_user`, `developer_vs_society`, pluralism `pair_drift` — but absolute numbers are not publication-grade without human-validated scoring.

## 5. Relation to existing evals

```
HarmBench   → harm compliance (1 axis)
ACHEval     → Anthropic constitution tier priority
C3AI        → principle crafting & win-rate
CLAIMS      → stakeholder × norm-class profile (orthogonal)
```

CLAIMS is closest in spirit to Gabriel & Keeling's *fair treatment of claims* — the theory has no public benchmark. ACHEval tests "which Anthropic principle wins"; CLAIMS tests "which **stakeholder norm** wins."

## 6. Honest limitations (why we are not shipping LLM-judge scores)

We provide **heuristic scoring** for reproducibility without API judge costs. Regex-based norm tagging is known-weak (e.g. misclassifying refusals on `malicious_user`).

**Deliberate choice for v0.3 OSS:** release data + pipeline + raw responses path, invite **community human calibration** on `calibration_subset24` rather than pretend a single author's LLM judge is ground truth.

Future v1.0 gate: inter-annotator κ > 0.6 on acceptable-class labels (n≥24).

## 7. MATS research plan (12 weeks)

### Phase 1 — Validate & harden (weeks 1–4)

- Recruit 2–3 annotators (diverse cultural background) for `calibration_subset24`
- Compute κ; revise rubric where κ < 0.5
- Spot-audit 30 items; prune or rewrite weak prompts
- Partner with safeguards/evals mentor on rubric (ACHEval crosswalk doc)

### Phase 2 — Scale & discriminate (weeks 5–8)

- Expand core → 200, pluralism → 60
- Run Claude, Gemini, Llama-3.1, Mistral baselines
- Publish norm-profile figure (closed vs open-weight)
- **Key experiment:** correlate CLAIMS profile with ACHEval scores on same models — test orthogonality

### Phase 3 — Bridge to mechanism (weeks 9–12)

- Optional integration with refusal-ablation work (`safety_interventions`): does tampering refusal directions shift norm profile on rights_vs_welfare?
- Workshop paper or technical report: "CLAIMS-Bench: stakeholder norm profiles for constitutional alignment"
- v1.0 release with human-validated scorer

## 8. Why Anthropic Megastream

1. **Direct fit:** CAI / constitution / HHH are Anthropic's stated alignment stack; CLAIMS operationalizes Gabriel's critique of HHH tradeoffs.
2. **Evals culture:** Anthropic ships ACHEval; CLAIMS is complementary (stakeholder tetrad, not tier hierarchy).
3. **My track record:** shipped benchmark + 4-model baselines in weeks; prior empirical work on open-weight safety geometry.
4. **Pluralism tier:** connects to Anthropic's non-Western principles work — tests imposition, not just harm refusal.

## 9. Success criteria

| Criterion | Target |
|-----------|--------|
| Community adoption | ≥1 external PR with new items or labels |
| Discrimination | ≥3 conflict_types with significant spread across 6+ models |
| Orthogonality | CLAIMS metrics not reducible to HarmBench r>0.9 |
| Human validity | κ > 0.6 on calibration set |
| Artifact | Public v1.0 + citeable report |

## 10. References

- Gabriel & Keeling (2025). *A matter of principle? AI alignment as the fair treatment of claims.* Philosophical Studies.
- Gabriel (2020). *Artificial intelligence, values, and alignment.* Minds and Machines.
- Askell et al. (2021). *A general language assistant as a laboratory for alignment.*
- Bai et al. (2022). *Constitutional AI: harmlessness from AI feedback.*
- Conitzer et al. (2024). *Position: rationality should guide AI alignment.*
