"""
14_figure6.py -- Figure 2: what survives one decision, and what can actually be predicted

Panel A  the CD28-minus-4-1BB difference recomputed under nine defensible variants of
         the pipeline. The direction never reverses; the pre-specified one-sided p
         clears 0.05 in four of the nine, and the two that do not are exactly the ones
         that remove information (single-phenotype reports, pre-2019 reports).
Panel B  leave-one-product-out prediction. If the class label carried a usable
         quantitative rule, a held-out product would land near the diagonal. It does
         not: the leave-one-out error is as large as the between-class gap, so the
         effect is ordinal and not a level predictor.
Panel C  the resolution limit of the prediction. Minimum report count at which a new
         product's partition resolves against the 4-1BB ceiling, as a function of its
         true value. V-shaped around the ceiling: far below it a handful of reports
         refutes, far above it a handful supports, and within 0.022 of it no sample
         size available in this database decides anything.
"""
from __future__ import annotations

import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, FIGS = os.path.join(HERE, "out"), os.path.join(HERE, "figs")
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
C_CD28 = "#B5443B"
C_41BB = "#2E6E8E"
Z = 1.959963985


def min_reports(p: float, threshold: float) -> float:
    """Smallest n at which the Wilson interval clears the threshold on either side."""
    if p <= 0:
        return float("nan")
    lo, hi = 1, 2_000_000
    def decided(n: int) -> bool:
        den = 1 + Z * Z / n
        ctr = (p + Z * Z / (2 * n)) / den
        half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
        return (ctr + half) <= threshold or (ctr - half) > threshold
    if not decided(hi):
        return float("nan")
    while lo < hi:
        mid = (lo + hi) // 2
        if decided(mid):
            hi = mid
        else:
            lo = mid + 1
    return float(lo)


def main():
    spec = pd.read_csv(os.path.join(OUT, "specification_curve.csv"))
    ho = json.load(open(os.path.join(OUT, "holdout.json"), encoding="utf-8"))
    rule = json.load(open(os.path.join(OUT, "prediction_rule.json"), encoding="utf-8"))

    spec = spec.iloc[::-1].reset_index(drop=True)
    fig = plt.figure(figsize=(7.3, 2.75))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.45, 0.95, 1.05], wspace=0.52)

    # ---------------------------------------------------------------- Panel A
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(spec))
    for i, r in spec.iterrows():
        sig = r.p_one_sided < 0.05
        ax.plot([0, r["diff"]], [i, i], color="#CCCCCC", lw=0.7, zorder=1)
        ax.scatter(r["diff"], i, s=26, zorder=4,
                   color=C_CD28 if sig else "white",
                   edgecolor=C_CD28, linewidth=0.9)
        ax.text(r["diff"] + 0.008, i, f"p={r.p_one_sided:.3f}".replace("0.", "."),
                fontsize=5.4, va="center", color="#555555")
    ax.axvline(0, color="#333333", lw=0.8, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(spec.specification, fontsize=6.2)
    ax.set_xlim(-0.005, max(spec["diff"]) * 1.45)
    ax.set_xlabel("Δ = mean R (CD28) − mean R (4-1BB)", fontsize=7)
    ax.set_ylim(-0.7, len(spec) + 1.5)
    ax.text(0.004, len(spec) + 1.05,
            f"direction preserved {int((spec['diff'] > 0).sum())}/{len(spec)}",
            fontsize=5.8, ha="left", va="center", color="#333333")
    ax.text(0.004, len(spec) + 0.40,
            f"one-sided p < 0.05 in {int((spec['p_one_sided'] < 0.05).sum())}/{len(spec)}",
            fontsize=5.8, ha="left", va="center", color="#333333")
    ax.text(-0.62, 1.06, "A", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------------------------------------------------------- Panel B
    ax = fig.add_subplot(gs[0, 1])
    det = pd.DataFrame(ho["detail"])
    for _, r in det.iterrows():
        c = C_CD28 if r["class"] == "CD28" else C_41BB
        ax.plot([r.R_observed, r.R_predicted_LODO],
                [r.R_observed, r.R_predicted_LODO],
                color=c, lw=0.6, alpha=0.55, zorder=2)
        ax.scatter(r.R_observed, r.R_predicted_LODO, s=22, color=c,
                   edgecolor="white", linewidth=0.5, zorder=4)
    ax.plot([0.19, 0.41], [0.19, 0.41], color="#888888", lw=0.8, ls=(0, (3, 2)),
            zorder=1)
    ax.set_xlim(0.19, 0.41)
    ax.set_ylim(0.19, 0.41)
    ticks = [0.20, 0.25, 0.30, 0.35, 0.40]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xlabel("observed R", fontsize=7)
    ax.set_ylabel("predicted R\n(other products only)", fontsize=6.6, labelpad=1)
    ax.tick_params(labelsize=6.2)
    ax.text(0.04, 0.96,
            f"MAE {ho['mae_class_mean']:.3f}\nclass-blind {ho['mae_class_blind']:.3f}\n"
            f"exact p = {ho['p_exact_class_better_than_random_grouping']:.2f}",
            transform=ax.transAxes, fontsize=5.9, va="top", ha="left", linespacing=1.3)
    ax.text(-0.30, 1.12, "B", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------------------------------------------------------- Panel C
    ax = fig.add_subplot(gs[0, 2])
    thr = rule["refutation_threshold"]
    n_ref = rule["reference_n"]
    grid = np.arange(0.16, 0.451, 0.0025)
    need = np.array([min_reports(float(g), thr) for g in grid])
    band = rule["blind_band_at_reference_n"]
    ax.axvspan(band[0], band[1], facecolor="#D8D8D8", edgecolor="#9A9A9A",
               lw=0.5, zorder=0)
    ax.semilogy(grid, need, color="#333333", lw=1.0, zorder=3)
    ax.axhline(n_ref, color=C_CD28, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.text(0.168, n_ref * 0.50, f"largest current product\n(n = {n_ref:,})",
            fontsize=5.6, color=C_CD28, va="top", ha="left", linespacing=1.2,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.annotate(f"undecidable\n{band[0]:.3f}–{band[1]:.3f}",
                xy=((band[0] + band[1]) / 2, 4.0e4), xytext=(0.196, 9.0e4),
                fontsize=5.6, color="#333333", ha="left", va="center",
                linespacing=1.25,
                arrowprops=dict(arrowstyle="-", color="#777777", lw=0.6,
                                shrinkA=1, shrinkB=2))
    ax.text(0.232, 8.5, "refutes", fontsize=6.2, color="#444444", ha="center")
    ax.text(0.408, 8.5, "supports", fontsize=6.2, color="#444444", ha="center")
    ax.set_xlim(0.16, 0.45)
    ax.set_ylim(2, 3e5)
    ax.set_xlabel("true partition R of a new CD28 product", fontsize=7)
    ax.set_ylabel("reports needed for a verdict", fontsize=6.6, labelpad=1)
    ax.tick_params(labelsize=6.2)
    ax.text(-0.34, 1.12, "C", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    fig.savefig(os.path.join(FIGS, "fig2_specification_falsification.png"), dpi=600)
    print("saved fig6 | specs", len(spec), "| blind band", band)


if __name__ == "__main__":
    main()
