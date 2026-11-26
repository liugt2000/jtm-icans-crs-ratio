"""
93_null_reproduction.py -- does the positive-control code path reproduce the published folds?

The positive control in 92 is only worth anything if it runs the same null as the results it
is meant to support. That is easy to assert and easy to get wrong: a different rng call order,
a different treatment of genes missing from the graph, or a target mask built from the wrong
module would all produce a plausible-looking control that validates a different pipeline.

So the same functions, on the same graph, are pointed at three module pairs whose folds are
already published in out/network_rwr.json (Table S6):
    COSTIM_CD28  -> CNS_VASCULAR     1.177   (published per-module table)
    COSTIM_CD28  -> MYELOID_CYTOKINE 2.040
    COSTIM_41BB  -> MYELOID_CYTOKINE 2.565
Each is recomputed from scratch with 2,000 fresh degree-decile-matched draws. Agreement within
Monte Carlo error means 92 measures the null the paper actually uses; disagreement means it
does not, and the control should not be reported.

Note that the rng stream differs from 05 (that script advances one generator across modules),
so the null draws are not identical, only drawn from the same construction. The comparison is
therefore fold and p, with the sampling error of each.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import random
from collections import defaultdict

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""),
                                                  os.path.join(_here, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rwr_mod = load("05_network_rwr.py")

HERE = os.path.dirname(_here)
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
ALPHA = 0.70
NPERM = 2000
SEED = 20261116          # same seed as 05, different call order
BLOCK = 1                # single-column solves are faster than blocks on this graph

PAIRS = [("COSTIM_CD28", "CNS_VASCULAR"),
         ("COSTIM_CD28", "MYELOID_CYTOKINE"),
         ("COSTIM_41BB", "MYELOID_CYTOKINE")]


def main() -> int:
    nodes, idx, A = rwr_mod.build(rwr_mod.load_edges(
        os.path.join(DATA, "omnipath_interactions_20261116.tsv")))
    keep, A = rwr_mod.giant(A)
    nodes = [nodes[i] for i in keep]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    deg = np.asarray(A.sum(1)).ravel()
    lu = rwr_mod.make_solver(A)

    def field(seeds):
        b = np.zeros(n)
        b[seeds] = 1.0 / len(seeds)
        return np.maximum(lu.solve((1.0 - ALPHA) * b), 0.0)

    def mod(path):
        out: dict[str, list[str]] = defaultdict(list)
        with open(path, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                g = row["gene"].strip()
                if g in idx:
                    out[row["module"]].append(g)
        return {k: sorted(set(v)) for k, v in out.items()}

    mods = {**mod(os.path.join(HERE, "config", "modules.csv")),
            **mod(os.path.join(HERE, "config", "engineered_modules.csv"))}

    arr = np.array(nodes)
    bins = [list(arr[c]) for c in np.array_split(np.argsort(deg), 10)]
    bin_of = {g: i for i, b in enumerate(bins) for g in b}

    published = json.load(open(os.path.join(OUT, "network_rwr.json"), encoding="utf-8"))

    rows = []
    for src, tgt in PAIRS:
        genes = mods[src]
        mask = np.isin(np.arange(n), [idx[g] for g in mods[tgt]])
        obs = float(field([idx[g] for g in genes])[mask].sum())
        rng = random.Random(SEED)
        null = np.empty(NPERM)
        for i in range(NPERM):
            out, used = [], set()
            for g in genes:
                b = bins[bin_of[g]]
                for _ in range(300):
                    c = b[rng.randrange(len(b))]
                    if c not in used:
                        break
                used.add(c)
                out.append(idx[c])
            null[i] = float(field(out)[mask].sum())
        mu, sd = float(null.mean()), float(null.std(ddof=1))
        pub = published["proximity"][src][f"to_{tgt}"]
        rows.append({"source": src, "target": tgt, "n_in_graph": len(genes),
                     "mass_now": obs, "mass_published": pub["mass"],
                     "fold_now": obs / mu, "fold_published": pub["fold"],
                     "p_now": float((null >= obs).mean()), "p_published": pub["p_enriched"],
                     "null_mean_now": mu, "null_mean_published": pub["null_mean"],
                     "se_rel_fold": sd / mu / np.sqrt(NPERM)})
        r = rows[-1]
        print(f"{src:12s} -> {tgt:16s} mass {obs:.6f} vs {pub['mass']:.6f}  "
              f"fold {r['fold_now']:.2f} vs {pub['fold']:.2f}  "
              f"p {r['p_now']:.3f} vs {pub['p_enriched']:.3f}", flush=True)

    ok = all(abs(r["mass_now"] - r["mass_published"]) < 1e-6 for r in rows)
    folds = np.array([abs(r["fold_now"] - r["fold_published"]) / r["fold_published"] for r in rows])
    verdict = {
        "observed_mass_matches": bool(ok),
        "max_relative_fold_difference": float(folds.max()),
        "within_monte_carlo": bool(folds.max() < 0.15),
        "n_perm": NPERM,
        "note": "observed masses are deterministic and must match the published values exactly; "
                "folds carry 2,000-draw sampling error and are compared only for agreement.",
    }
    json.dump({"pairs": rows, "verdict": verdict},
              open(os.path.join(OUT, "null_reproduction.json"), "w", encoding="utf-8"),
              indent=2)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
