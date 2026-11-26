"""
10_figure2.py -- Figure 4: the two modules are anatomically distinct.

Panel A  per-gene endothelial-over-myeloid score in HPA single-nucleus brain data,
         module by module, with the annotation- and expression-matched null mean as a
         dashed reference. The hepatocyte module is carried as a negative control and
         sits on the null mean.
Panel B  the same contrast in an independent, non-cerebral endothelium (GSE195519,
         HDMEC versus iPSC-derived endothelial progenitors), so that "endothelial"
         can be distinguished from "cerebral".
Panel C  TNF-alpha response of the same modules in human brain microvascular
         endothelium (GSE211439): where the module lives, and whether it moves when
         the endothelium is insulted.
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
os.makedirs(FIGS, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "figure.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

C_CNS = "#B5443B"
C_MYE = "#2E6F9E"
C_HEP = "#8C8C8C"
C_NULL = "#D8D3CB"
MODS = [("CNS_VASCULAR", C_CNS, "Neuro-\nvascular"),
        ("MYELOID_CYTOKINE", C_MYE, "Myeloid\ncytokine"),
        ("HEPATOCYTE_NEGCTRL", C_HEP, "Hepatocyte\n(control)")]


def main():
    loc = json.load(open(os.path.join(OUT, "localisation_hpa.json"), encoding="utf-8"))
    per = pd.read_csv(os.path.join(OUT, "localisation_per_gene.csv"))
    pert = json.load(open(os.path.join(OUT, "perturbation_validation.json"), encoding="utf-8"))

    fig = plt.figure(figsize=(7.5, 2.45))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 0.95, 0.9], wspace=0.62)

    # ---------------- Panel A
    ax = fig.add_subplot(gs[0, 0])
    rng = np.random.default_rng(7)
    for i, (m, col, _) in enumerate(MODS):
        v = per.loc[per.module == m, "score"].dropna().values
        jit = rng.uniform(-0.15, 0.15, len(v))
        ax.scatter(np.full(len(v), i) + jit, v, s=8, color=col, alpha=0.55,
                   linewidths=0, zorder=3)
        ax.plot([i - 0.25, i + 0.25], [v.mean()] * 2, color="black", lw=1.2, zorder=4)
        nm = loc["modules"][m]["null_mean_all"]
        ax.plot([i - 0.29, i + 0.29], [nm, nm], color="#666666", lw=0.9,
                ls=(0, (3, 2)), zorder=2)
    ax.axhline(0, color="#BDBDBD", lw=0.6, zorder=1)
    ax.set_xticks(range(len(MODS)))
    ax.set_xticklabels([lbl for _, _, lbl in MODS], fontsize=6.6)
    ax.set_ylabel("log$_2$ (endothelial / myeloid nCPM + 1)", fontsize=7)
    ax.set_ylim(-11.5, 12.2)
    ax.set_xlim(-0.55, 2.55)
    it = loc["interaction_CNS_minus_MYELOID"]
    ax.text(0.02, 0.035, f"Δ = {it['delta']:+.2f},  z = {it['z']:+.1f}",
            transform=ax.transAxes, fontsize=6.2, va="bottom")
    ax.plot([], [], color="#666666", ls=(0, (3, 2)), lw=0.9, label="matched null")
    ax.plot([], [], color="black", lw=1.2, label="module mean")
    ax.legend(fontsize=5.8, frameon=False, loc="upper center", handlelength=1.1,
              borderpad=0.2, labelspacing=0.2, bbox_to_anchor=(0.52, 1.02))
    ax.text(-0.36, 1.04, "A", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel B
    ax = fig.add_subplot(gs[0, 1])
    q1 = pert["Q1_localisation"]["HDMEC_minus_iPC"]
    ys = np.arange(len(MODS))[::-1]
    for y, (m, col, _) in zip(ys, MODS):
        v = q1[m]
        ax.barh(y, v["observed"], height=0.55, color=col, alpha=0.9, edgecolor="none",
                zorder=3)
        ax.text(2.55, y, f"z = {v['z']:+.1f}", va="center", ha="right",
                fontsize=5.8, color="#444444")
    ax.axvline(0, color="black", lw=0.7, zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels([lbl.replace("\n", " ") for _, _, lbl in MODS], fontsize=6.0)
    ax.set_xlabel("HDMEC − iPSC endothelial\n(module score)", fontsize=6.8)
    ax.set_xlim(-0.95, 2.65)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=1)
    ax.text(0.97, 0.06, "GSE195519", transform=ax.transAxes, fontsize=5.8, ha="right",
            va="bottom", color="#5B5B5B", style="italic")
    ax.text(-0.52, 1.04, "B", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    # ---------------- Panel C
    ax = fig.add_subplot(gs[0, 2])
    q2 = pert["Q2_tnf_response"]["signed_log2FC"]
    vals, cols, pv, labs = [], [], [], []
    for m, col, lbl in MODS:
        v = q2.get(m)
        if v:
            vals.append(v["observed"])
            cols.append(col)
            pv.append(v["p_enriched"])
            labs.append({"Neuro-\nvascular": "Neuro", "Myeloid\ncytokine": "Myeloid",
                         "Hepatocyte\n(control)": "Hepato.\n(ctrl)"}[lbl])
    bars = ax.bar(range(len(vals)), vals, color=cols, width=0.58, zorder=3)
    for b, p in zip(bars, pv):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05,
                "p < 10$^{-4}$" if p < 1e-4 else "p < 0.01" if p < 0.01 else f"p = {p:.2f}",
                ha="center", va="bottom", fontsize=5.8)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, fontsize=5.9)
    ax.set_ylabel("module mean log$_2$FC\n(TNF-α vs control)", fontsize=6.9)
    ax.set_ylim(0, max(vals) * 1.38)
    ax.text(-0.40, 1.04, "C", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")
    ax.text(0.5, -0.34, "hBMEC, GSE211439", transform=ax.transAxes, ha="center",
            va="top", fontsize=5.8, color="#5B5B5B", style="italic")

    fig.savefig(os.path.join(FIGS, "fig4_module_localisation.png"), dpi=600)
    print("saved fig2 |", {m: round(q1[m]["z"], 2) for m, _, _ in MODS})


if __name__ == "__main__":
    main()
