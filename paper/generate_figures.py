#!/usr/bin/env python3
"""Generate paper figures from baseline JSON reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = Path(__file__).resolve().parent / "figures"
STRUCTURED = ROOT / "outputs/baseline_v2_structured"
IMPLICIT = ROOT / "outputs/baseline_v2_implicit"
CONSISTENCY = ROOT / "outputs/consistency_pilot/gpt-4o-mini_consistency.json"

VALUES = [
    "self_direction",
    "stimulation",
    "hedonism",
    "achievement",
    "power",
    "security",
    "conformity",
    "tradition",
    "benevolence",
    "universalism",
]
LABELS = [v.replace("_", "\n") for v in VALUES]


def _load_reports(directory: Path) -> list[tuple[str, dict]]:
    rows = []
    for path in sorted(directory.glob("*_report.json")):
        data = json.loads(path.read_text())
        model = data.get("model") or path.name.replace("_report.json", "")
        prof = data["summary"]["mean_schwartz_profile"]
        rows.append((model, prof))
    return rows


def _heatmap(models_profiles: list[tuple[str, dict]], title: str, out: Path) -> None:
    mat = np.array([[p.get(v, 0.0) for v in VALUES] for _, p in models_profiles])
    fig, ax = plt.subplots(figsize=(10, 3.5))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(len(VALUES)))
    ax.set_xticklabels(LABELS, fontsize=8)
    ax.set_yticks(range(len(models_profiles)))
    ax.set_yticklabels([m for m, _ in models_profiles])
    ax.set_title(title)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, fraction=0.02)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_pipeline(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 2.2))
    ax.axis("off")
    boxes = [
        "Under-specified\nscenario",
        "Structured or\nimplicit elicitation",
        "Model\nresponse",
        "Borda / BT or\nimplicit judge",
        "10-dim Schwartz\nprofile",
    ]
    xs = np.linspace(0.05, 0.95, len(boxes))
    for x, label in zip(xs, boxes):
        ax.add_patch(plt.Rectangle((x - 0.08, 0.35), 0.16, 0.3, fill=False, lw=1.5))
        ax.text(x, 0.5, label, ha="center", va="center", fontsize=9)
        if x < xs[-1]:
            ax.annotate("", xy=(x + 0.09, 0.5), xytext=(x + 0.11, 0.5),
                        arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("L3 value revelation measurement pipeline")
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_consistency(path: Path, out: Path) -> None:
    data = json.loads(path.read_text())
    items = data.get("per_item", [])
    if not items:
        return
    ids = [x["item_id"].replace("revelation_", "") for x in items]
    cvs = [x["mean_cv_nonzero_dims"] for x in items]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(ids, cvs, color="#4C72B0")
    ax.axhline(0.15, color="red", ls="--", lw=1, label="high instability (0.15)")
    ax.axhline(data.get("mean_cv_across_items", 0), color="black", ls=":", lw=1,
               label=f"mean CV={data.get('mean_cv_across_items')}")
    ax.set_xlabel("Item")
    ax.set_ylabel("Mean CV (non-zero dims)")
    ax.set_title("Profile stability under resampling (gpt-4o-mini, T=0.7, n=5)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_failure_modes(directory: Path, out: Path) -> None:
    modes: set[str] = set()
    per_model: dict[str, dict[str, float]] = {}
    for path in sorted(directory.glob("*_report.json")):
        data = json.loads(path.read_text())
        model = data.get("model") or path.stem
        rates = data["summary"].get("failure_mode_rates", {})
        per_model[model] = rates
        modes.update(rates.keys())
    modes = sorted(modes)
    if not modes:
        return
    models = list(per_model.keys())
    x = np.arange(len(modes))
    width = 0.25
    fig, ax = plt.subplots(figsize=(7, 2.8))
    for i, model in enumerate(models):
        vals = [per_model[model].get(m, 0) for m in modes]
        ax.bar(x + i * width, vals, width, label=model)
    ax.set_xticks(x + width)
    ax.set_xticklabels(modes, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Trigger rate (judge severity ≥1)")
    ax.set_title("Failure-mode rates (structured baseline; exploratory)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_pipeline(FIG_DIR / "fig1_pipeline")
    if STRUCTURED.exists():
        _heatmap(
            _load_reports(STRUCTURED),
            "Mean Schwartz profiles — structured elicitation (n=30)",
            FIG_DIR / "fig2_structured_heatmap",
        )
        fig_failure_modes(STRUCTURED, FIG_DIR / "fig5_failure_modes")
    if IMPLICIT.exists():
        _heatmap(
            _load_reports(IMPLICIT),
            "Mean Schwartz profiles — implicit judge (n=13)",
            FIG_DIR / "fig3_implicit_heatmap",
        )
    if CONSISTENCY.exists():
        fig_consistency(CONSISTENCY, FIG_DIR / "fig4_consistency_cv")
    print(f"Wrote figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
