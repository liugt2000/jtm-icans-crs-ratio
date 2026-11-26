"""
Turn the prediction into a decision rule with a stated resolution limit.

The manuscript predicts "a future CD28 product shows R between 0.321 and 0.415, and a
value at or below 0.320 refutes the account". That is a nominal interval. Whether it is
a usable test depends on how many reports a new product would need before its interval
resolves the question, and on whether that number is reachable in practice.

The decision rule adopted here is one-sided against the 4-1BB ceiling:

    supports   if the Wilson lower bound at the observed pi exceeds 0.320
    refutes    if the Wilson upper bound falls at or below 0.320
    undecidable otherwise, whatever the sample size

For a grid of true values of R, the minimum report count at which the rule stops being
undecidable is computed by bisection. The blind band at a reference sample size is the
set of true R values that remain undecidable there. The reference is the largest single
product in Table 1, which is what "reachable in practice" means for this database.

Outputs: out/prediction_rule.json
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
Z = 1.959963985


def wilson(p: float, n: float) -> tuple[float, float]:
    den = 1 + Z * Z / n
    ctr = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return ctr - half, ctr + half


def verdict(p: float, n: float, threshold: float) -> str:
    a, b = wilson(p, n)
    if b <= threshold:
        return "refutes"
    if a > threshold:
        return "supports"
    return "undecidable"


def min_n(p: float, threshold: float, cap: int = 2_000_000) -> int | None:
    lo, hi, best = 1, cap, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if verdict(p, mid, threshold) != "undecidable":
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return best


def main() -> int:
    df = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    df = df[df.n_pheno >= 20]

    four = df[df.costim == "4-1BB"]
    cd = df[df.costim == "CD28"]
    threshold = round(float(four.R.max()), 3)          # 0.320, the 4-1BB ceiling
    window = [round(float(cd.R_lo.min()), 3), round(float(cd.R_hi.max()), 3)]

    n_ref = int(df.n_pheno.max())                      # largest single product
    ref_product = str(df.loc[df.n_pheno.idxmax(), "short"])

    # the blind band at the reference sample size
    grid = np.arange(0.260, 0.4601, 0.0005)
    blind = [g for g in grid if verdict(float(g), n_ref, threshold) == "undecidable"]
    band = [round(min(blind), 3), round(max(blind), 3)] if blind else None

    # minimum reports needed, on a grid of plausible true values
    table = []
    for p in (0.150, 0.200, 0.250, 0.280, 0.300, 0.310, 0.320, 0.325,
              0.330, 0.335, 0.340, 0.360, 0.390, 0.415, 0.450):
        need = min_n(p, threshold)
        table.append({"true_R": p, "verdict": verdict(p, n_ref, threshold),
                      "min_reports_for_decisive_verdict": need})

    # the two numbers that state the rule compactly: at the reference sample size,
    # which true values can be resolved at all?
    resolvable = [t for t in table if t["min_reports_for_decisive_verdict"]
                  and t["min_reports_for_decisive_verdict"] <= n_ref]

    # negative control region: a product with a BiTE-like R is decidable almost at once
    bite = df[df.costim == "none"].R
    res = {
        "refutation_threshold": threshold,
        "observed_cd28_window": window,
        "observed_cd28_points": [round(float(v), 3) for v in cd.R],
        "observed_41bb_points": [round(float(v), 3) for v in four.R],
        "reference_n": n_ref,
        "reference_product": ref_product,
        "blind_band_at_reference_n": band,
        "blind_band_width": round(band[1] - band[0], 3) if band else None,
        "rule": ("supports if the Wilson lower bound exceeds "
                 f"{threshold}; refutes if the Wilson upper bound falls at or below "
                 f"{threshold}; otherwise undecidable at any sample size"),
        "table": table,
        "n_true_values_resolvable_at_reference_n": len(resolvable),
        "bite_reference": {"point_estimates": [round(float(v), 3) for v in bite],
                           "min_reports_to_refute_at_0.20": min_n(0.20, threshold)},
        "why_this_replaces_the_interval": (
            "the interval [0.321, 0.415] is a restatement of the two CD28 intervals and "
            "cannot be checked against a single new product, because the gap to the "
            "4-1BB ceiling (0.012) is smaller than the half-width of any product in the "
            "table except the largest. Stating the rule with its resolution limit makes "
            "the prediction falsifiable in a way a reader can actually compute."),
    }
    with open(os.path.join(OUT, "prediction_rule.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)

    print(json.dumps(res, indent=2, ensure_ascii=False)[:2600])
    print()
    print(pd.DataFrame(table).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
