"""
94_positive_control_summary.py -- summarise the positive control without re-running it.

92_positive_control.py takes about 70 s per pair, so the 62-pair run is over an hour. The
summary definition, by contrast, is the part most likely to change while the text is being
written: which fold to headline, how to define the detection bracket, whether the calibration
claim survives a median-based rather than mean-based fold. Keeping the summary here means the
nulls are computed once and summarised as often as needed.

Two folds are carried through because the null is not symmetric for dense targets.
  fold_ab      observed mass over the null MEAN. This is the definition used in Table S6, where
               the null is close to symmetric (CV 0.4-0.7) and the two agree.
  fold_ab_med  observed mass over the null MEDIAN. For a dense 19-gene target the null is
               bimodal -- a seed set that happens to make several direct contacts deposits an
               order of magnitude more mass than one that makes none -- so the mean sits between
               the modes and understates the fold. Against the median an unrelated pair centres
               on 1.00 by construction, which is what a calibration claim needs.

The detection bracket is the interval between the largest fold that failed to reach p < 0.05 and
the smallest fold that reached it, over the pairs known to be related. That interval is the
empirical counterpart of the analytic 11.9-fold minimum detectable ratio in out/power_network.json.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
POSITIVE = ("pathway_half", "pathway_half_split2", "complex")
UNRELATED = ("negative", "random_pair")


def class_summary(sub: pd.DataFrame) -> dict:
    if not len(sub):
        return {}
    p = sub.p_ab.to_numpy(float)
    fm = sub.fold_ab_med.to_numpy(float)
    fa = sub.fold_ab.to_numpy(float)
    return {"n": int(len(sub)),
            "fold_median_of_median_ratio": float(np.median(fm)),
            "fold_median_q1": float(np.quantile(fm, 0.25)),
            "fold_median_q3": float(np.quantile(fm, 0.75)),
            "fold_mean_ratio_median": float(np.median(fa)),
            "fold_mean_ratio_q1": float(np.quantile(fa, 0.25)),
            "fold_mean_ratio_q3": float(np.quantile(fa, 0.75)),
            "fold_mean_ratio_min": float(fa.min()),
            "fold_mean_ratio_max": float(fa.max()),
            "max_fold_mean_not_significant": float(fa[p >= 0.05].max()) if (p >= 0.05).any() else None,
            "min_fold_mean_significant": float(fa[p < 0.05].min()) if (p < 0.05).any() else None,
            "null_cv_median": float(np.median(sub.null_ab_sd / sub.null_ab_mean)),
            "n_p_lt_0.05": int((p < 0.05).sum()),
            "n_p_lt_0.01": int((p < 0.01).sum()),
            "p_median": float(np.median(p)),
            "p_min": float(p.min())}


def main() -> int:
    df = pd.read_csv(os.path.join(OUT, "positive_control.csv"))
    out = {"by_class": {k: class_summary(df[df.kind == k])
                        for k in ("pathway_half", "pathway_half_split2", "complex",
                                  "negative", "random_pair")}}

    pos = df[df.kind.isin(POSITIVE)]
    sig = pos[pos.p_ab < 0.05]
    nsig = pos[pos.p_ab >= 0.05]
    out["bracket"] = {
        "max_fold_median_ratio_not_significant": float(nsig.fold_ab_med.max()) if len(nsig) else None,
        "min_fold_median_ratio_significant": float(sig.fold_ab_med.min()) if len(sig) else None,
        "n_related_pairs": int(len(pos)),
        "n_significant": int(len(sig)),
        "analytic_mde_11_9_inside": bool(
            len(sig) and len(nsig)
            and nsig.fold_ab_med.max() <= 11.9 <= sig.fold_ab_med.min()),
    }

    unr = df[df.kind.isin(UNRELATED)]
    out["calibration"] = {
        "n_unrelated": int(len(unr)),
        "fold_median_ratio_median": float(np.median(unr.fold_ab_med)),
        "fold_median_ratio_q1": float(np.quantile(unr.fold_ab_med, 0.25)),
        "fold_median_ratio_q3": float(np.quantile(unr.fold_ab_med, 0.75)),
        "n_p_lt_0.05": int((unr.p_ab < 0.05).sum()),
        "p_median": float(np.median(unr.p_ab)),
    }

    # split-to-split agreement on the six pathways that were split twice
    s1 = df[df.kind == "pathway_half"].set_index("name").fold_ab_med
    s2 = df[df.kind == "pathway_half_split2"].set_index("name").fold_ab_med
    both = s1.index.intersection(s2.index)
    if len(both):
        a, b = s1.loc[both].to_numpy(float), s2.loc[both].to_numpy(float)
        out["split_agreement"] = {
            "n": int(len(both)),
            "correlation": float(np.corrcoef(a, b)[0, 1]) if len(both) > 2 else None,
            "max_relative_difference": float(np.abs(a - b).max() / np.abs(a).max()),
            "pairs": [{"name": k, "split1": float(x), "split2": float(y)}
                      for k, x, y in zip(both, a, b)],
        }

    rep = os.path.join(OUT, "null_reproduction.json")
    if os.path.exists(rep):
        out["pipeline_reproduction"] = json.load(open(rep, encoding="utf-8"))["verdict"]

    with open(os.path.join(OUT, "positive_control_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
