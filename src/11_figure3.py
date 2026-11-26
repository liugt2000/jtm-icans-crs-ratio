"""
11_figure3.py -- Figure 5: the network-proximity contrast, and why it cannot answer
the question at this module size.

Panel A  the null distribution of the CD28-vs-4-1BB routing ratio (1000 matched pairs),
         with the observed ratio and the minimum detectable ratio marked. The observed
         value sits inside the null; the region where a difference would have been
         visible starts an order of magnitude to the right.
Panel B  module size available versus module size required to resolve the observed
         ratio at 80% power.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, FIGS = os.path.join(HERE, "out"), os.path.join(HERE, "figs")
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
C_OBS = "#B5443B"
C_MDR = "#4A4A4A"
C_FILL = "#D8D3CB"


def main():
    nr = json.load(open(os.path.join(OUT, "network_null_ratio.json"), encoding="utf-8"))
    pw = json.load(open(os.path.join(OUT, "power_network.json"), encoding="utf-8"))
    z = np.load(os.path.join(OUT, "network_null_ratio_samples.npz"))
    a, b = z["CNS_VASCULAR_A"], z["CNS_VASCULAR_B"]
    ratio = a / b
    ratio = ratio[np.isfinite(ratio) & (ratio > 0)]

    fig = plt.figure(figsize=(7.2, 2.25))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 0.85], wspace=0.34)

    ax = fig.add_subplot(gs[0, 0])
    lr = np.log10(ratio)
    bins = np.linspace(-2.2, 2.2, 90)
    ax.hist(np.clip(lr, -2.2, 2.2), bins=bins, color=C_FILL, edgecolor="none", zorder=2)
    ax.set_xlim(-2.25, 2.25)
    obs = np.log10(nr["CNS_VASCULAR"]["observed_ratio"])
    mdr = np.log10(pw["by_target"]["CNS_VASCULAR"]["min_detectable_ratio_80pct_power"])
    ax.axvline(obs, color=C_OBS, lw=1.4, zorder=5)
    ax.axvline(mdr, color=C_MDR, lw=1.0, ls=(0, (3, 2)), zorder=5)
    ax.axvspan(mdr, 2.25, color=C_MDR, alpha=0.07, zorder=1)
    ytop = ax.get_ylim()[1]
    ax.annotate(f"observed\n1.34×", xy=(obs, ytop * 0.62), xytext=(obs - 0.75, ytop * 0.80),
                fontsize=6.4, color=C_OBS, ha="center",
                arrowprops=dict(arrowstyle="-", color=C_OBS, lw=0.7))
    ax.text(mdr + 0.08, ytop * 0.45, f"smallest ratio this\ndesign could detect\n"
            f"({pw['by_target']['CNS_VASCULAR']['min_detectable_ratio_80pct_power']:.1f}×)",
            fontsize=6.2, color=C_MDR, va="center")
    ax.set_xlabel("log$_{10}$ (CD28 / 4-1BB routing ratio), matched null", fontsize=7)
    ax.set_ylabel("matched pairs", fontsize=7)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100"])
    ax.set_ylim(0, ax.get_ylim()[1] * 1.18)
    ax.text(-0.13, 1.10, "A", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    ax = fig.add_subplot(gs[0, 1])
    labels = ["Neurovascular", "Myeloid\ncytokine"]
    used = [19, 19]
    need = [pw["by_target"]["CNS_VASCULAR"]["module_size_needed_to_resolve_observed"],
            pw["by_target"]["MYELOID_CYTOKINE"]["module_size_needed_to_resolve_observed"]]
    x = np.arange(2)
    ax.bar(x - 0.19, used, width=0.34, color="#7FA9C4", label="available", zorder=3)
    ax.bar(x + 0.19, need, width=0.34, color="#C9C2B6", label="required", zorder=3)
    for i, (u, nd) in enumerate(zip(used, need)):
        ax.text(i - 0.19, u * 1.18, f"{u}", ha="center", va="bottom", fontsize=6.4)
        ax.text(i + 0.19, nd * 1.18, f"{nd:,}", ha="center", va="bottom", fontsize=6.4)
    ax.set_yscale("log")
    ax.set_ylim(8, 12000)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6.8)
    ax.set_ylabel("genes per module", fontsize=7)
    ax.legend(fontsize=6, frameon=False, loc="upper left", handlelength=1.0, borderpad=0.3)
    ax.text(-0.32, 1.10, "B", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    fig.savefig(os.path.join(FIGS, "fig5_network_power.png"), dpi=600)
    print("saved", os.path.join(FIGS, "fig5_network_power.png"),
          "| null pairs", len(ratio), "| median", round(float(np.median(ratio)), 3))


if __name__ == "__main__":
    main()
