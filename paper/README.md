# CLAIMS-Bench paper

| File | Purpose |
|------|---------|
| [`claims_bench_v2.md`](claims_bench_v2.md) | Full paper draft (markdown; convert to PDF via Pandoc or Overleaf) |
| [`FIGURES.md`](FIGURES.md) | Figure list and regeneration instructions |
| [`generate_figures.py`](generate_figures.py) | Build figures from `outputs/baseline_*` JSON reports |
| [`figures/`](figures/) | Generated PDF/PNG (re-run script after new baselines) |

## Build PDF (production)

```bash
cd paper
bash build_pdf.sh   # requires pandoc + tectonic (brew install pandoc tectonic)
```

Output: `paper/claims_bench_v2.pdf`

## Venue suggestions

- NeurIPS Datasets & Benchmarks track
- FAccT / AIES workshops
- arXiv cs.CL / cs.CY preprint → community release

## Before submission

- [ ] Human panel n$\geq$5 on 8-item survey (`data/panel/survey/`)
- [x] Temp=0.0 consistency comparison in §6.3 (mean CV 0.038 vs 0.113)
- [ ] Expand model count if reviewers request
- [ ] IRB / consent if paid panel
