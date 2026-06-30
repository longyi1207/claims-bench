# Figure specifications

Generate with: `python paper/generate_figures.py`  
Outputs → `paper/figures/*.pdf` and `*.png`

| ID | File | Description | Paper section |
|----|------|-------------|---------------|
| **Fig 1** | `fig1_pipeline.pdf` | L3 measurement pipeline: scenario → elicitation → profile extraction | §4 |
| **Fig 2** | `fig2_structured_heatmap.pdf` | 3×10 heatmap: mean Schwartz profile (structured, n=30) | §6.1 |
| **Fig 3** | `fig3_implicit_heatmap.pdf` | 3×10 heatmap: mean profile (implicit judge, n=13) | §6.2 |
| **Fig 4** | `fig4_consistency_cv.pdf` | Per-item mean CV across 5 replicates (temp=0.7) | §6.3 |
| **Fig 5** | `fig5_failure_modes.pdf` | Failure-mode trigger rates (structured; exploratory) | §6.4 |

**Status:** Run `generate_figures.py` after any baseline re-run; embed in paper with:

```markdown
![Structured profiles](figures/fig2_structured_heatmap.png)
```

---

## TODO after figure generation

- [ ] Replace `<!-- FIGURE:N -->` placeholders in `claims_bench_v2.md`
- [ ] Re-export PDF if submitting to venue with figure limits
