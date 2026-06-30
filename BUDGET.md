# CLAIMS-Bench v2 — Budget Plan ($1000)

**Owner:** Longyi Zhou  
**Purpose:** Guide API/compute/human-incentive spend for v2 build. Confirm before any single purchase >$50.

---

## Allocation (recommended)

| Category | Budget | Notes |
|----------|--------|-------|
| **Model inference (eval runs)** | $350 | 6–8 models × ~250 items × structured elicitation (longer outputs) |
| **LLM judge / label assist** | $200 | Calibrated judge on L3 + spot-check L1; not sole ground truth |
| **Human panel incentives** | $250 | 10 panelists × $25 gift cards OR 5 × $50 for 30-min sessions |
| **Re-runs / iteration buffer** | $150 | Failed runs, prompt revisions, ablations |
| **Compute (local/cloud)** | $50 | Optional HF inference if local MPS insufficient |
| **Reserve** | $0 | Folded into buffer |

---

## Cost control rules

1. **Log every run** to `outputs/spend_log.jsonl`: `{date, provider, model, items, est_usd, notes}`
2. **Pilot on 5 items** before full batch per model.
3. **Cache responses** — never re-run unchanged prompts.
4. **Prefer mini/small models** for judge development; frontier only for final baseline table.
5. **Human panel** — start n=5 unpaid friends for protocol debug; paid panel only after protocol stable.

---

## Model priority list (baseline table)

| Priority | Model | Rationale |
|----------|-------|-----------|
| P0 | gpt-4o-mini | Cheap anchor; legacy comparison |
| P0 | gpt-4o | Closed frontier |
| P0 | claude-sonnet-4 (or latest available) | Anthropic stack |
| P1 | deepseek-chat | Open API diversity |
| P1 | Qwen2.5-7B-Instruct (local) | OSS local |
| P2 | gemini-2.0-flash | Google stack |
| P2 | llama-3.1-8b-instruct | OSS API/local |

---

## Spend milestones (gates)

| Milestone | Max cumulative spend | Gate |
|-----------|---------------------|------|
| M1: Schema + 5 L3 pilots scored | $50 | Protocol works end-to-end |
| M2: 20 L3 items × 4 models | $200 | Human panel protocol ready |
| M3: Human panel n=10 | $450 | κ or distance metrics computed |
| M4: Full baseline + report | $800 | Docs complete |
| M5: Community release v2.0 | $1000 | README + citation updated |
