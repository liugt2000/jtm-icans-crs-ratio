"""Figure 1: the ICANS/CRS dissociation across T-cell-engaging products."""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
FIGS = os.path.join(HERE, "figs")

COL = {"CD28": "#A32D2D", "4-1BB": "#185FA5", "none": "#5F5E5A"}


def main() -> int:
    os.makedirs(FIGS, exist_ok=True)
    t = pd.read_csv(os.path.join(OUT, "table1_products.csv"))
    t = t[t.modality.isin(["CAR-T", "BiTE"])].copy()
    t = t.sort_values("log2_icans_over_crs")
    t["costim"] = t.costim.fillna("none")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), dpi=220,
                             gridspec_kw={"width_ratios": [1.35, 1]})
    for ax in axes:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors="#2C2C2A", labelsize=9, length=3)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#B4B2A9")

    ax = axes[0]
    y = range(len(t))
    colors = [COL.get(c, "#5F5E5A") for c in t.costim]
    ax.hlines(y, 0, t.log2_icans_over_crs, color=colors, linewidth=1.4, alpha=0.55)
    ax.scatter(t.log2_icans_over_crs, y, c=colors, s=46, zorder=3,
               edgecolors="white", linewidths=0.8)
    ax.axvline(0, color="#5F5E5A", linewidth=0.9)
    ax.set_yticks(list(y))
    ax.set_yticklabels(t.short, fontsize=9)
    ax.set_xlabel("log$_2$ (EBGM$_{ICANS}$ / EBGM$_{CRS}$)", fontsize=9.5, color="#2C2C2A")
    ax.set_title("A  Phenotype preference of each product", fontsize=10.5,
                 loc="left", color="#2C2C2A", pad=8)
    lo = t.log2_icans_over_crs.min()
    hi = t.log2_icans_over_crs.max()
    pad = 0.07 * (hi - lo)
    ax.set_xlim(lo - pad, hi + pad)
    ax.text(0.985, 0.70, "CNS-dominant", transform=ax.transAxes, ha="right",
            fontsize=8, color="#A32D2D", style="italic")
    ax.text(0.015, 0.70, "CRS-dominant", transform=ax.transAxes, ha="left",
            fontsize=8, color="#185FA5", style="italic")

    ax = axes[1]
    for i, r in enumerate(t.itertuples()):
        c = COL.get(r.costim, "#5F5E5A")
        ax.plot([r.crs_share, r.icans_share], [i, i], color=c, linewidth=1.0, alpha=0.35)
        ax.scatter(r.crs_share, i, s=34, facecolors="none", edgecolors=c, linewidths=1.2)
        ax.scatter(r.icans_share, i, s=34, color=c, zorder=3)
    ax.set_yticks([])
    ax.set_ylim(-0.8, len(t) - 0.2)
    ax.set_xlabel("Share of the product's reports carrying the PT", fontsize=9.5,
                  color="#2C2C2A")
    ax.set_title("B  Report composition (open circle = CRS, filled = ICANS)",
                 fontsize=10.5, loc="left", color="#2C2C2A", pad=8)

    handles = [plt.Line2D([], [], marker="o", linestyle="", color=v,
                          label={"CD28": "CD28 costimulation",
                                 "4-1BB": "4-1BB costimulation",
                                 "none": "Bispecific, no costimulatory domain"}[k])
               for k, v in COL.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = os.path.join(FIGS, "fig1_icans_crs_dissociation.png")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    print("saved", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
