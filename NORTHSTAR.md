# CLAIMS-Bench North Star (v2)

**Status:** Adopted 2026-06-28  
**Supersedes:** `VISION.md` as primary direction (VISION remains historical)

---

## One-line mission

> **Characterize models' implicit value commitments under conflict and under-specification — and compare to human pluralism — not certify moral correctness.**

---

## What we are building

A **community-facing normative eval** for AI assistants that outputs **multi-layer value profiles**, not a single alignment score.

| Layer | Name | Question | Theory anchor | Scenario types |
|-------|------|----------|---------------|----------------|
| **L1** | Stakeholder fairness | When claims conflict, *who* does the model favor? | Gabriel & Keeling (2025) | malicious_user, developer vs user, HIPAA, … |
| **L2** | Principle tension | *Which mid-level principles* dominate the reasoning? | Beauchamp & Childress principlism | medical tradeoffs, consent vs welfare, … |
| **L3** | Value revelation | *What implicit priorities* emerge under uncertainty? | Schwartz basic values + Berlin pluralism | first contact, longtermism, radical under-spec |

**L3 is the north star.** L1/L2 are supporting diagnostics with stronger normative grounding.

---

## What we claim vs do not claim

### We claim

- Models exhibit **distinct, stable-ish value profiles** across scenario families.
- Profiles can be **compared to human panel distributions** (descriptive distance).
- We detect **failure modes**: false certainty, cultural imposition, single-value collapse, precaution blindness.
- L1 stakeholder bias is a **useful orthogonal axis** to harm-refusal benchmarks.

### We do not claim

- A single "morally correct" answer per item (Berlin: right vs right).
- Our taxonomy is the true structure of human values (Schwartz is descriptive, not normative).
- Regex/LLM scores equal deep moral reasoning.
- Higher `western_index` or any pole = better alignment.
- Representative of all cultures without validated human panels.

---

## AGI-relevant framing

Under **radical uncertainty** (existential risk, first contact, singleton governance), stakeholder roles are unclear. The eval must probe:

- **Terminal values:** survival vs dignity vs autonomy vs knowledge
- **Epistemic priors:** precaution vs optimism; trust vs suspicion defaults
- **Time horizon:** present welfare vs long-term / intergenerational
- **Pluralism:** acknowledgment vs imposition of one cultural frame

Success = **characterization + human comparison**, not certification.

---

## Measurement philosophy

1. **Profile, not scalar** — publish vectors; resist leaderboard Goodhart (Ren et al. 2024 safetywashing).
2. **Structured elicitation for L3** — rankings, pairwise tradeoffs, forced choices; not open-ended chat only.
3. **Human panel baselines** — same protocol on same items; distance metrics, not accuracy.
4. **Multidimensional tags** — replace coarse single `conflict_type` with orthogonal taxonomy (`docs/TAXONOMY.md`).
5. **Heuristic + LLM judge** — automation for scale; human κ on calibration sets for validity.

---

## Relationship to v0.5 legacy

| v0.5 artifact | v2 disposition |
|---------------|----------------|
| `data/v0.5_full208.jsonl` | **Preserve** as L1/L2 legacy; retag with multidimensional taxonomy |
| 13-dim `values_ontology.json` | **Deprecate headline use**; migrate L2/L3 to Schwartz backbone (`data/schwartz_backbone.yaml`) |
| `western_index` / `eastern_relational` | **Remove** from public reports (essentialist + English bias) |
| Heuristic norm scorer | **Keep** as fast baseline; not publication metric without κ |
| Gabriel types 1–6 | **Keep** as L1 tags; label as non-exhaustive operationalization |

---

## v2 deliverables (community-useful, not PoC)

| Deliverable | Target |
|-------------|----------|
| L3 revelation tier | 20–30 scenarios with structured elicitation |
| Multidimensional item schema | JSON Schema + migration script for legacy items |
| Human panel protocol + tooling | Collect + aggregate panel responses |
| Model baseline report | ≥6 models on L3 + legacy L1 subset |
| Public docs | NORTHSTAR, TAXONOMY, scoring protocol, honest limitations |
| Budget | ≤$1000 total (see `BUDGET.md`) |

---

## References (starter)

- Gabriel & Keeling (2025). *A matter of principle?*
- Berlin, I. Value pluralism essays.
- Beauchamp & Childress. *Principles of Biomedical Ethics.*
- Schwartz, S. H. (2012). Overview of basic values theory.
- Inglehart & Welzel. WVS cultural evolution (human baseline context).
- Ren et al. (2024). Safetywashing.

Reading pack: `../../readings/values_foundations/` in parent monorepo.
