"""
04_figure1_v2.py -- Figure 1: the ICANS/CRS partition is a property of the construct.

Panel A  R = ICANS/(ICANS + CRS) per product, with Wilson intervals, ordered and
         coloured by costimulatory class. Two CD28 products sit above every 4-1BB
         product; the bispecifics, which carry no costimulatory domain, sit below both.
Panel B  The two phenotypes are not independent: the fraction of a product's ICANS
         reports that also carry CRS. Coupling is high and varies by class, which is
         why the isolated-phenotype sensitivity in Panel C is not optional.
Panel C  The same contrast recomputed after discarding every report that carries both
         PTs. The direction survives; roughly a third of the magnitude does not.
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
COLC = {"CD28": C_CD28, "4-1BB": C_41BB, "none": C_BITE}
CLASS_LABEL = {"CD28": "CD28 costimulation", "4-1BB": "4-1BB costimulation",
               "none": "no costimulatory domain"}


def main():
    cg = json.load(open(os.path.join(OUT, "case_groups.json"), encoding="utf-8"))
    MIN = cg["min_phenotype_reports_for_eligibility"]
    t = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    t = t[t.n_pheno >= MIN].copy()
    t["costim"] = t.costim.fillna("none")
    t = t.sort_values("R")           # ascending -> highest at the top of the axis
    n = len(t)
    order = t.short.tolist()

    fig = plt.figure(figsize=(9.4, 2.85))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.3, 0.8, 1.0, 1.05], wspace=0.55)

    # ---------------- Panel A
    ax = fig.add_subplot(gs[0, 0])
    ytop = n + 1.9
    ax.set_ylim(-0.8, ytop)
    for i, (_, r) in enumerate(t.iterrows()):
        c = COLC[r.costim]
        ax.plot([r.R_lo, r.R_hi], [i, i], color=c, lw=1.0, alpha=0.45, zorder=2,
                solid_capstyle="round")
        ax.scatter(r.R, i, s=20, color=c, edgecolor="white", linewidth=0.4, zorder=4)
    ax.set_yticks(range(n))
    ax.set_yticklabels(order, fontsize=6.6)
    for lbl, (_, r) in zip(ax.get_yticklabels(), t.iterrows()):
        lbl.set_color(COLC[r.costim])
    ax.set_xlabel("partition  R = ICANS / (ICANS + CRS)", fontsize=7)
    ax.set_xlim(0.08, 0.57)
    ax.set_ylim(-0.8, ytop)
    # report counts live outside the plotting area so they cannot collide with data
    for i, (_, r) in enumerate(t.iterrows()):
        ax.text(1.02, i, f"{int(r.n_pheno):,}", transform=ax.get_yaxis_transform(),
                fontsize=5.6, va="center", ha="left", color="#777777", clip_on=False)
    ax.text(1.02, n + 0.55, "reports", transform=ax.get_yaxis_transform(),
            fontsize=5.6, va="center", ha="left", color="#777777", clip_on=False)
    handles = [plt.Line2D([], [], marker="o", ls="", color=COLC[k], ms=4,
                          label=CLASS_LABEL[k]) for k in ["CD28", "4-1BB", "none"]]
    ax.legend(handles=handles, fontsize=5.8, frameon=False, loc="upper left",
              handletextpad=0.25, borderpad=0.1, labelspacing=0.22,
              bbox_to_anchor=(-0.02, 1.0))
    ax.text(-0.46, 1.05, "A", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel B
    ax = fig.add_subplot(gs[0, 1])
    cor = cg["co_reporting_by_product"]
    ax.set_ylim(-0.8, ytop)
    for i, (_, r) in enumerate(t.iterrows()):
        if r.short not in cor:
            continue
        ax.barh(i, cor[r.short]["frac_with_crs"], height=0.6, color=COLC[r.costim],
                alpha=0.85, edgecolor="none", zorder=3)
    frac = cg["co_reporting"]["fraction_with_crs"]
    ax.axvline(frac, color="#444444", lw=0.8, ls=(0, (3, 2)), zorder=5)
    ax.text(frac - 0.03, ytop - 0.55, f"class mean {frac:.2f}", fontsize=5.8,
            ha="right", va="top", color="#444444")
    ax.set_yticks([])
    ax.set_xlim(0, 0.92)
    ax.set_xlabel("ICANS reports that also\ncarry the CRS term", fontsize=6.8)
    ax.tick_params(axis="x", labelsize=6)
    ax.text(-0.34, 1.05, "B", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel C
    ax = fig.add_subplot(gs[0, 2])
    iso = pd.read_csv(os.path.join(OUT, "case_products_isolated.csv"))
    iso = iso.set_index("short")
    ax.set_ylim(-0.8, ytop)
    for i, (_, r) in enumerate(t.iterrows()):
        if r.short not in iso.index:
            continue
        q = iso.loc[r.short]
        c = COLC[r.costim]
        ax.plot([q.R, r.R], [i, i], color=c, lw=1.1, alpha=0.5, zorder=2)
        ax.scatter(r.R, i, s=18, color=c, edgecolor="white", linewidth=0.4, zorder=4)
        ax.scatter(q.R, i, s=18, facecolor="white", edgecolor=c, lw=1.0, zorder=4)
    ax.set_yticks(range(n))
    ax.set_yticklabels([])
    ax.set_xlim(0, 0.46)
    ax.set_xlabel("R recomputed on single-PT\nreports (open) vs all (filled)",
                  fontsize=6.8)
    ip = cg["isolated_phenotype"]["perm_CD28_vs_41BB"]
    ax.text(0.98, 0.02, f"Δ = {ip['diff']:.3f}\none-sided p = {ip['p_one_sided']:.2f}",
            transform=ax.transAxes, fontsize=6.0, ha="right", va="bottom")
    ax.text(-0.14, 1.05, "C", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel D: the same partition in a second reporting system
    ax = fig.add_subplot(gs[0, 3])
    ev = json.load(open(os.path.join(OUT, "ev_replication.json"), encoding="utf-8"))
    lo, hi = 0.08, 0.47
    ax.plot([lo, hi], [lo, hi], color="#BBBBBB", lw=0.7, ls="--", zorder=1)
    for d in ev["table"]:
        if not d["analysable"]:
            continue
        c = COLC["none"] if d["costimulation"] is None else COLC[d["costimulation"]]
        ax.scatter(d["R_faers"], d["R_ev"], s=20, color=c, edgecolor="white",
                   linewidth=0.4, zorder=4)
    # label the two CD28 products and the two edges of the 4-1BB spread
    for d in ev["table"]:
        if d["product"] in ("brexu-cel", "axi-cel", "ide-cel", "glofitamab"):
            left = d["product"] == "brexu-cel"
            ax.annotate(d["product"].replace("-cel", ""), (d["R_faers"], d["R_ev"]),
                        textcoords="offset points", xytext=(-4 if left else 4, -1.5),
                        ha="right" if left else "left", fontsize=5.4, color="#555555")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel("R in FAERS", fontsize=7)
    ax.set_ylabel("R in EudraVigilance", fontsize=7)
    ax.text(0.04, 0.96, f"ρ = {ev['spearman_faers_vs_ev']:.2f}\n"
                        f"{ev['pairwise_sign_concordance']['concordant']}"
                        f"/{ev['pairwise_sign_concordance']['pairs']} pairs",
            transform=ax.transAxes, fontsize=6.0, va="top")
    ax.text(-0.30, 1.05, "D", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    fig.savefig(os.path.join(FIGS, "fig1_partition.png"), dpi=600)
    print("saved fig1 | products", n, "| co-report", round(frac, 3))


if __name__ == "__main__":
    main()
