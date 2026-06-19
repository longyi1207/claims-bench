# Contributing to CLAIMS-Bench

## What we need most

1. **Human labels** on `data/calibration_subset24.jsonl` — submit PRs with `data/calibration_labels/<your_name>.jsonl`
2. **New scenarios** — follow `schema.md`; prefer ambiguous / pluralism items with `pair_id` pairs
3. **Scorer improvements** — we ship heuristic v0; better rubrics welcome with justification

## Item quality bar

- Real stakeholder conflict (user / third_party / developer / society)
- `acceptable` set must admit ≥2 defensible norms on hard items
- No gotcha trick questions; tag `control_help` for legitimate-help controls
- Cite source in `source` field (paper, policy doc, or `claims_bench_community`)

## PR checklist

- [ ] JSONL validates against `schema.md`
- [ ] `rubric_notes` explains scoring intent
- [ ] No copyrighted prompt copying from proprietary evals
- [ ] Run `python score_responses.py` on a sample if you change schema

## Calibration label format

```json
{"id": "claims_001", "annotator": "alice", "predicted_norm_class": "refuse_user", "acceptable_match": true, "failure_modes_triggered": [], "notes": ""}
```

We will compute inter-annotator κ before promoting scorer changes.
