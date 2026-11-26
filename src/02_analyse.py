"""
N2 built-in positive control + module-specificity analysis.

N2 (pre-specified): CD28-costimulated CAR-T products must show a higher
ICANS signal than 4-1BB products. If this fails, the model is declared invalid
and no predictive claim is made (Phase 0, failure criterion F3).

Because the class contains only a handful of products, no asymptotic test is
trustworthy. We therefore report:
  (a) the observed group contrast in mean log2(EBGM ICANS / EBGM CRS);
  (b) an exact permutation p-value over all label permutations (n is small enough
      that the permutation distribution is enumerated exactly, not sampled);
  (c) a leave-one-product-out stability count, so a single product cannot carry
      the result.

Outputs: out/table1_products.csv, out/n2_test.json, figs/fig1_icans_crs.png
"""
from __future__ import annotations

import itertools
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
FIGS = os.path.join(HERE, "figs")

ICANS_PT = "Immune effector cell-associated neurotoxicity syndrome"
CRS_PT = "Cytokine release syndrome"
NEG = ["Alopecia", "Rash", "Pruritus", "Neutropenia", "Thrombocytopenia",
       "Diarrhoea", "Constipation", "Oedema peripheral"]


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    sig = pd.read_csv(os.path.join(OUT, "signals.csv"))
    subs = pd.read_csv(os.path.join(HERE, "config", "substances.csv"),
                       encoding="utf-8-sig")
    subs["substance"] = subs["substance"].str.replace(r"-[A-Z]{4}$", "", regex=True)
    subs = subs.drop_duplicates("substance")
    return sig, subs


def build_table(sig: pd.DataFrame, subs: pd.DataFrame) -> pd.DataFrame:
    def pick(pt: str, col: str) -> pd.Series:
        s = sig[sig.pt == pt].set_index("substance")[col]
        return s

    t = pd.DataFrame({
        "ebgm_icans": pick(ICANS_PT, "ebgm"),
        "eb05_icans": pick(ICANS_PT, "eb05"),
        "ror_icans": pick(ICANS_PT, "ror"),
        "n_icans": pick(ICANS_PT, "a"),
        "ebgm_crs": pick(CRS_PT, "ebgm"),
        "eb05_crs": pick(CRS_PT, "eb05"),
        "ror_crs": pick(CRS_PT, "ror"),
        "n_crs": pick(CRS_PT, "a"),
        "n_reports": pick(CRS_PT, "n_i"),
    })
    neg = (sig[sig.pt.isin(NEG)]
           .groupby("substance")
           .agg(max_neg_eb05=("eb05", "max"), max_neg_pt=("pt", lambda s: "")))
    negmax = sig[sig.pt.isin(NEG)].sort_values("eb05").groupby("substance").tail(1)
    neg = negmax.set_index("substance")[["eb05", "pt"]].rename(
        columns={"eb05": "max_neg_eb05", "pt": "max_neg_pt"})
    t = t.join(neg).join(subs.set_index("substance")[["short", "group", "costim",
                                                      "target", "modality"]])
    t = t.reset_index().rename(columns={"index": "substance"})
    t["icans_share"] = t.n_icans / t.n_reports
    t["crs_share"] = t.n_crs / t.n_reports
    t["log2_icans_over_crs"] = np.log2(t.ebgm_icans / t.ebgm_crs)
    return t.sort_values("log2_icans_over_crs", ascending=False)


def perm_test(x: np.ndarray, labels: np.ndarray) -> dict:
    """Exact permutation test on the difference of group means."""
    obs = x[labels == 1].mean() - x[labels == 0].mean()   # positive = CD28 higher
    n0 = int((labels == 0).sum())
    idx = np.arange(len(x))
    diffs = []
    for combo in itertools.combinations(idx, n0):
        m = np.zeros(len(x), dtype=bool)
        m[list(combo)] = True
        diffs.append(x[m].mean() - x[~m].mean())
    diffs = np.array(diffs)
    p = float((np.abs(diffs) >= abs(obs) - 1e-12).mean())
    # With 2 CD28 vs 5 4-1BB products the exact permutation distribution has only
    # C(7,2)=21 points, so the smallest attainable two-sided p is 1/21 = 0.048, reached
    # only when the two groups are PERFECTLY separated. The N2 test is therefore a
    # separation check, not a powered significance test, and is reported as such.
    return {"observed_diff": float(obs), "p_two_sided": p,
            "min_attainable_p": 1.0 / len(diffs),
            "n_permutations": int(len(diffs)), "null_sd": float(diffs.std()),
            "interpretation": "directional check only; exact p is floored at min_attainable_p"}


def main() -> int:
    os.makedirs(FIGS, exist_ok=True)
    sig, subs = load()
    t = build_table(sig, subs)
    t.to_csv(os.path.join(OUT, "table1_products.csv"), index=False)

    cart = t[(t.modality == "CAR-T") & t.costim.isin(["CD28", "4-1BB"])].copy()
    res: dict = {"n_cart_products": int(len(cart)),
                 "cd28": cart.loc[cart.costim == "CD28", "short"].tolist(),
                 "four_1bb": cart.loc[cart.costim == "4-1BB", "short"].tolist()}

    for metric in ["log2_icans_over_crs", "icans_share"]:
        labels = (cart.costim == "CD28").astype(int).to_numpy()
        x = cart[metric].to_numpy(dtype=float)
        res[metric] = perm_test(x, labels)
        res[metric]["mean_cd28"] = float(x[labels == 1].mean())
        res[metric]["mean_4_1bb"] = float(x[labels == 0].mean())

    loo = []
    for drop in range(len(cart)):
        sub = cart.drop(cart.index[drop])
        labels = (sub.costim == "CD28").astype(int).to_numpy()
        loo.append(float(sub.log2_icans_over_crs.to_numpy()
                         [labels == 1].mean()
                         - sub.log2_icans_over_crs.to_numpy()[labels == 0].mean()))
    res["loo_sign_stable"] = int(sum(d > 0 for d in loo))
    res["loo_n"] = len(loo)
    res["loo_diffs"] = loo

    engager = t[t.modality.isin(["CAR-T", "BiTE"])]
    res["negctrl"] = {
        "scope": "T-cell-engaging products only (comparators excluded by design)",
        "n_products": int(len(engager)),
        "n_products_with_neg_eb05_gt_icans": int(
            (engager.max_neg_eb05 > engager.eb05_icans).sum()),
        "detail": engager.loc[engager.max_neg_eb05 > engager.eb05_icans,
                              ["substance", "max_neg_pt", "max_neg_eb05",
                               "eb05_icans"]].to_dict("records"),
    }
    with open(os.path.join(OUT, "n2_test.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "loo_diffs"},
                     indent=2, ensure_ascii=False))
    print(t[["substance", "group", "costim", "n_reports", "n_icans", "n_crs",
             "ebgm_icans", "ebgm_crs", "log2_icans_over_crs"]]
          .to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
