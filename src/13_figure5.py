"""
13_figure5.py -- Figure 6: what the mechanistic model does and does not constrain.

Panel A  one-at-a-time change in R when each parameter is swept over its stated range,
         separated into production-side parameters (which the algebra says must cancel)
         and amplification-side parameters, in an unsaturated and a saturating regime.
Panel B  Saltelli-Sobol total-order indices for the same ten parameters, same two regimes.
Panel C  simulated R against the analytic limit kE/lE, coloured by how close the
         endothelial compartment comes to its ceiling. Deviation from the identity line
         is the only route by which a production-side parameter can reach R.
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
C_PROD = "#9A9185"
C_AMP = "#2E6E8E"

LABEL = {"r": "r", "K": "K", "dA": "d$_A$", "kC": "k$_C$", "lC": "λ$_C$", "A0": "A$_0$",
         "kE0": "k$_{E0}$", "lE": "λ$_E$", "Emax": "E$_{max}$", "beta": "β"}


def main():
    inv = json.load(open(os.path.join(OUT, "model_invariance.json"), encoding="utf-8"))
    sob = json.load(open(os.path.join(OUT, "model_sobol.json"), encoding="utf-8"))
    ident = pd.read_csv(os.path.join(OUT, "model_identity.csv"))

    unsat, nom = inv["unsaturated_Emax_1e4"], inv["nominal_Emax_8"]
    params = [k for k in unsat if not k.startswith("_")]
    params.sort(key=lambda k: (unsat[k]["kind"] != "production",
                               -nom[ k]["relative_change"]))

    fig = plt.figure(figsize=(7.4, 2.75))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1.0, 0.95], wspace=0.52)

    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(params))
    for i, k in enumerate(params):
        c = C_PROD if unsat[k]["kind"] == "production" else C_AMP
        ax.barh(i + 0.19, unsat[k]["relative_change"], height=0.34,
                color=c, alpha=0.35, edgecolor="none", zorder=2)
        ax.barh(i - 0.19, nom[k]["relative_change"], height=0.34,
                color=c, edgecolor="none", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([LABEL[k] for k in params], fontsize=7)
    ax.set_xlabel("relative change in R over the swept range", fontsize=7)
    ax.set_xlim(0, max(nom[k]["relative_change"] for k in params) * 1.12)
    ax.axhline(5.5, color="#BBBBBB", lw=0.6, ls=(0, (2, 2)))
    ax.text(0.97, 0.94, "amplification", transform=ax.transAxes, fontsize=6.4,
            ha="right", va="top", color=C_AMP)
    ax.text(0.97, 0.36, "production", transform=ax.transAxes, fontsize=6.4,
            ha="right", va="top", color=C_PROD)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#8A8A8A", alpha=0.35, label="unsaturated"),
                       Patch(facecolor="#8A8A8A", label="saturating")],
              fontsize=6, frameon=False, loc="center right", handlelength=1.0,
              borderpad=0.2)
    ax.text(-0.34, 1.08, "A", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    ax = fig.add_subplot(gs[0, 1])
    # Emax is the parameter being contrasted between the two regimes, so it is fixed
    # in each Sobol run rather than sampled; indices exist for the remaining nine.
    sob_keys = [k for k in params if k in sob["nominal"]["total_order"]]
    order = sorted(sob_keys, key=lambda k: sob["nominal"]["total_order"][k])
    y = np.arange(len(order))
    for i, k in enumerate(order):
        c = C_PROD if k in ("r", "K", "dA", "kC", "lC", "A0") else C_AMP
        ax.barh(i + 0.19, sob["unsaturated"]["total_order"][k], height=0.34,
                color=c, alpha=0.35, edgecolor="none", zorder=2)
        ax.barh(i - 0.19, sob["nominal"]["total_order"][k], height=0.34,
                color=c, edgecolor="none", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([LABEL[k] for k in order], fontsize=7)
    ax.set_xlabel("total-order Sobol index", fontsize=7)
    ax.set_xlim(0, max(max(sob["nominal"]["total_order"].values()),
                       max(sob["unsaturated"]["total_order"].values())) * 1.18)
    ax.text(0.97, 0.03, "E$_{max}$ fixed at 10$^4$ (open)\nvs 8 (filled)",
            transform=ax.transAxes, fontsize=5.8, ha="right", va="bottom",
            color="#555555")
    ax.text(-0.42, 1.08, "B", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    ax = fig.add_subplot(gs[0, 2])
    sc = ax.scatter(ident.R_analytic, ident.R_sim, c=ident.saturation, s=3.5,
                    cmap="viridis", vmin=0, vmax=1, linewidths=0, alpha=0.75)
    lim = [ident[["R_analytic", "R_sim"]].min().min() * 0.7,
           ident[["R_analytic", "R_sim"]].max().max() * 1.1]
    ax.plot(lim, lim, color="#555555", lw=0.8, ls=(0, (3, 2)), zorder=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("analytic limit  k$_E$/λ$_E$", fontsize=7)
    ax.set_ylabel("simulated R", fontsize=7)
    cb = fig.colorbar(sc, ax=ax, fraction=0.045, pad=0.03)
    cb.set_label("E$_{peak}$ / E$_{max}$", fontsize=6.2)
    cb.ax.tick_params(labelsize=5.6)
    ax.text(-0.40, 1.08, "C", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    fig.savefig(os.path.join(FIGS, "fig6_model_constraints.png"), dpi=600)
    print("saved fig5 | prod", round(unsat["_summary"]["production_max_rel_change"], 4),
          "amp", round(unsat["_summary"]["amplification_max_rel_change"], 4),
          "| corr", round(float(np.corrcoef(ident.R_sim, ident.R_analytic)[0, 1]), 4))


if __name__ == "__main__":
    main()
