# Human Panel Recruitment (v2 pilot)

## Target
- **n=5** unpaid friends first (protocol debug)
- **n=10** paid ($25/session) after protocol stable

## Diversity axes (self-report)
Culture/regions lived, professional background, age, religious/secular.

## Session flow
1. Consent + framing (2 min) — see `survey/panel_survey.md` intro
2. Training item optional: `revelation_001` (not in main packet)
3. Main: 8 items in `survey/panel_survey.md` (~20 min)
4. Debrief notes optional

## Recording responses
```bash
cd code/claims_bench
python3 scripts/panel_collect.py record --panelist-id p01
# or import from Google Form export:
python3 scripts/panel_collect.py import --panelist-id p02 --file form_export.jsonl
```

## After collection
```bash
python3 scripts/panel_aggregate.py --responses-dir data/panel/responses
python3 scripts/model_human_distance.py \
  --panel data/panel/panel_aggregate.json \
  --model-report outputs/baseline_v2_structured/gpt-4o_report.json
```

Store responses in `data/panel/responses/<panelist_id>.jsonl` (gitignore if PII).
