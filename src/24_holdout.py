"""
Leave-one-product-out validation of the costimulation effect.

The manuscript reports a class contrast on seven CAR-T products and then uses it to
make a prediction. Between those two steps sits an untested assumption: that the class
label generalises to a product the model has not seen. This script tests exactly that,
with no new data.

For each eligible product i:

    prediction from class   p_i = mean(R of the other products in i's class)
    prediction without class q_i = mean(R of all other eligible products)

and the error is |R_i - p_i|. The quantity of interest is the *improvement*
MAE(q) - MAE(p): how much knowing the costimulatory class buys on a held-out product.

That improvement is then tested against every other way of splitting the same seven
products into groups of the same sizes -- an exact enumeration over C(7,2)=21 label
assignments, the same null construction used for the primary endpoint. Without this
step the comparison is close to tautological, since any grouping with different group
means will beat the grand mean on its own members.

Outputs: out/holdout.json, out/holdout_products.csv
"""
from __future__ import annotations

import itertools
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
MIN = 20


def loo_mae(x: np.ndarray, labels: np.ndarray, mask: np.ndarray | None = None) -> float:
    """MAE of the leave-one-out class-mean predictor.

    `mask` selects which products are assigned the label; for the observed grouping it
    is the CD28 indicator, for a null assignment it is an arbitrary 2-subset.
    """
    n = len(x)
    errs = []
    for i in range(n):
        same = [j for j in range(n) if j != i and mask[j] == mask[i]]
        if not same:                       # a class of one cannot predict itself
            same = [j for j in range(n) if j != i]
        errs.append(abs(x[i] - float(np.mean([x[j] for j in same]))))
    return float(np.mean(errs))


def loo_mae_global(x: np.ndarray) -> float:
    n = len(x)
    return float(np.mean([abs(x[i] - float(np.mean([x[j] for j in range(n) if j != i])))
                          for i in range(n)]))


def main() -> int:
    df = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    df = df[(df.n_pheno >= MIN) & df.costim.isin(["CD28", "4-1BB"])].copy()
    df = df.sort_values("R", ascending=False).reset_index(drop=True)
    x = df.R.to_numpy(float)
    lab = (df.costim == "CD28").to_numpy().astype(int)
    n1 = int(lab.sum())

    obs_class = loo_mae(x, lab, lab.astype(bool))
    glob = loo_mae_global(x)
    improvement = glob - obs_class

    # every alternative grouping of the same shape
    alts = []
    for combo in itertools.combinations(range(len(x)), n1):
        m = np.zeros(len(x), dtype=bool)
        m[list(combo)] = True
        alts.append(loo_mae(x, m.astype(int), m))
    alts = np.array(alts)
    p_exact = float((alts <= obs_class + 1e-12).mean())   # as good as, or better than, observed

    # per-product detail
    rows = []
    for i, r in df.iterrows():
        same = [j for j in range(len(x)) if j != i and lab[j] == lab[i]]
        pred = float(np.mean([x[j] for j in same]))
        rows.append({"product": r.short, "class": r.costim, "n_pheno": int(r.n_pheno),
                     "R_observed": round(float(r.R), 4),
                     "R_predicted_LODO": round(pred, 4),
                     "error": round(float(r.R) - pred, 4),
                     "abs_error": round(abs(float(r.R) - pred), 4),
                     "n_donors": len(same)})
    det = pd.DataFrame(rows)
    det.to_csv(os.path.join(OUT, "holdout_products.csv"), index=False)

    res = {
        "n_products": int(len(x)),
        "n_cd28": n1, "n_41bb": int(len(x) - n1),
        "mae_class_mean": round(obs_class, 4),
        "mae_class_blind": round(glob, 4),
        "mae_improvement": round(improvement, 4),
        "relative_improvement_pct": round(100 * improvement / glob, 1),
        "median_abs_error_class_mean": round(float(det.abs_error.median()), 4),
        "max_abs_error": round(float(det.abs_error.max()), 4),
        "n_products_within_0.05": int((det.abs_error <= 0.05).sum()),
        "null": "every C(7,2)=21 assignment of two products to the CD28 label",
        "n_null_assignments": int(len(alts)),
        "p_exact_class_better_than_random_grouping": p_exact,
        "min_attainable_p": round(1.0 / len(alts), 4),
        "null_mae_quantiles": {"q05": round(float(np.quantile(alts, 0.05)), 4),
                               "q50": round(float(np.quantile(alts, 0.50)), 4),
                               "q95": round(float(np.quantile(alts, 0.95)), 4)},
        "detail": rows,
        "caveat": "the CD28 class contains two products, so its leave-one-out "
                  "prediction rests on a single donor and its error is not an "
                  "independent estimate of generalisation within that class.",
    }
    with open(os.path.join(OUT, "holdout.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)

    print(json.dumps({k: v for k, v in res.items() if k != "detail"},
                     indent=2, ensure_ascii=False))
    print()
    print(det.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
