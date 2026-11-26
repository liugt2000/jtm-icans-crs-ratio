"""
12_figure4.py -- Figure 3: the level drifts, the ordering does not.

Panel A  Annual phenotype volumes and the class-level partition. Volume triples across
         the window; the partition leaves its 2019 floor within two years and then sits
         on a plateau.
Panel B  Each product's partition recomputed in the first and second half of its own
         observation window. Eleven of thirteen products rise. The drift is a maturation
         of reporting, not a change in biology, and it is why R may only be compared
         between products of similar market age.
Panel C  The CD28-minus-4-1BB difference recomputed inside each calendar year. It is
         positive in every year in which both classes have a product with at least
         thirty phenotype reports, so the ordering is not an artefact of era.
"""
from __future__ import annotations

import json
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
C_BITE = "#7A7468"


def main():
    cg = json.load(open(os.path.join(OUT, "case_groups.json"), encoding="utf-8"))
    year = pd.read_csv(os.path.join(OUT, "case_by_year.csv"))
    meta = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    col = dict(zip(meta.short, [{"CD28": C_CD28, "4-1BB": C_41BB}.get(c, C_BITE)
                                for c in meta.costim.fillna("none")]))

    fig = plt.figure(figsize=(7.4, 2.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.95], wspace=0.86)

    # ---------------- Panel A
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(year))
    ax.bar(x, year.n_crs, width=0.66, color="#CFC9BF", label="CRS", zorder=2)
    ax.bar(x, year.n_icans, width=0.66, color="#8FA9B8", label="ICANS", zorder=3)
    ax.set_ylabel("reports per year", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(v))[2:] for v in year.year], fontsize=6.2)
    ax.set_xlabel("year", fontsize=7)
    ax.set_ylim(0, year.n_crs.max() * 1.30)
    ax.legend(fontsize=5.8, frameon=False, loc="upper left", handlelength=0.9,
              borderpad=0.2, labelspacing=0.2)
    ax2 = ax.twinx()
    ax2.plot(x, year.R, color=C_CD28, lw=1.2, marker="o", ms=3, zorder=5)
    ax2.set_ylabel("class R", fontsize=6.4, color=C_CD28, labelpad=1)
    ax2.tick_params(axis="y", labelsize=5.8, colors=C_CD28, pad=1)
    ax2.set_ylim(0, 0.42)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(C_CD28)
    ax2.spines["top"].set_visible(False)
    ax2.annotate("PT introduced\n2018", xy=(0, year.R.iloc[0]), xytext=(0.6, 0.12),
                 fontsize=5.6, color="#666666",
                 arrowprops=dict(arrowstyle="-", color="#999999", lw=0.6))
    ax.text(-0.30, 1.07, "A", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel B
    ax = fig.add_subplot(gs[0, 1])
    w = cg["within_product_drift"]["detail"]
    order = sorted(w, key=lambda k: w[k]["delta"])
    for i, s in enumerate(order):
        a, b = w[s]["R_first_half"], w[s]["R_second_half"]
        c = col.get(s, C_BITE)
        ax.plot([a, b], [i, i], color=c, lw=1.0, alpha=0.5, zorder=2)
        ax.scatter([a], [i], s=16, facecolor="white", edgecolor=c, lw=0.9, zorder=3)
        ax.scatter([b], [i], s=16, color=c, edgecolor="none", zorder=4)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=6.2)
    for lbl, s_ in zip(ax.get_yticklabels(), order):
        lbl.set_color(col.get(s_, C_BITE))
    ax.tick_params(axis="y", pad=1)
    ax.set_ylim(-0.8, len(order) + 1.5)
    ax.set_xlim(0.0, 0.48)
    ax.set_xlabel("R in first vs second half of\nthe product's own observation window",
                  fontsize=6.8)
    ax.text(0.98, 0.98,
            f"{cg['within_product_drift']['n_rising']}/"
            f"{cg['within_product_drift']['n_products']} rise\n"
            f"median Δ = {cg['within_product_drift']['median_delta']:+.3f}",
            transform=ax.transAxes, fontsize=6.0, ha="right", va="top")
    ax.text(-0.40, 1.07, "B", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel C
    ax = fig.add_subplot(gs[0, 2])
    ys = cg["year_stratified"]["detail"]
    x = np.arange(len(ys))
    d = [s["delta"] for s in ys]
    ax.bar(x, d, width=0.62, color=[C_CD28 if v > 0 else "#BBBBBB" for v in d],
           edgecolor="none", zorder=3)
    ax.axhline(0, color="#333333", lw=0.8, zorder=4)
    for i, s in enumerate(ys):
        ax.text(i, d[i] + (0.012 if d[i] >= 0 else -0.012),
                f"{s['n_cd28']}/{s['n_41bb']}", ha="center",
                va="bottom" if d[i] >= 0 else "top", fontsize=5.2, color="#666666")
    ax.set_xticks(x)
    ax.set_xticklabels([str(s["year"])[2:] for s in ys], fontsize=6.2)
    ax.set_xlabel("year", fontsize=7)
    ax.set_ylabel("Δ (CD28 − 4-1BB) within year", fontsize=6.8)
    ax.set_ylim(min(d) - 0.09, max(d) * 1.45)
    ax.text(0.03, 0.97,
            f"Δ > 0 in {cg['year_stratified']['n_years_delta_positive']}"
            f"/{cg['year_stratified']['n_years']} years",
            transform=ax.transAxes, fontsize=6.0, va="top")
    ax.text(-0.36, 1.07, "C", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    fig.savefig(os.path.join(FIGS, "fig3_temporal_invariance.png"), dpi=600)
    print("saved fig4 | drift rising",
          cg["within_product_drift"]["n_rising"], "/",
          cg["within_product_drift"]["n_products"],
          "| year-strat positive",
          cg["year_stratified"]["n_years_delta_positive"], "/",
          cg["year_stratified"]["n_years"])


if __name__ == "__main__":
    main()
