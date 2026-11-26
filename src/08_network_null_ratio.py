"""
08_network_null_ratio.py -- what counts as a big routing difference?

05_network_rwr.py reports two numbers from size-matched subsampling:
    the CD28 signalosome puts 1.34x more random-walk mass on the neurovascular module
    than the 4-1BB signalosome does, and 0.81x as much on the myeloid module.

But 'two signalling modules differ by 1.34x' is only interpretable if 1.34x is unusual
for two arbitrary gene sets with the same degree profiles. This script supplies that
null -- the missing piece that turns a ratio into a test.

Null: set A is degree-matched to COSTIM_CD28 (19 genes), set B to COSTIM_41BB (19
genes); both are drawn independently and solved once each; the null distribution of
mass(A)/mass(B) on a fixed target module comes from pairing the draws. Under
exchangeability that ratio centres on 1, so the observed 1.34 and 0.81 are read
against it directly.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import random

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rwr", os.path.join(_here, "05_network_rwr.py"))
rwr_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rwr_mod)

HERE = os.path.dirname(_here)
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
NA, NB = 1000, 1000
K = 19
SEED = 20261116

def _hash_seed_guard() -> None:
    """Warn when the interpreter hash seed is free.

    The degree-matched sampler builds its population from sets, so the order in
    which genes are drawn from it — and with it every null mean, z and p — depends
    on the interpreter's string hash seed. Two runs on identical input differ by up
    to 0.15 in z unless the seed is fixed. Set PYTHONHASHSEED=0 to reproduce a run.
    """
    if os.environ.get("PYTHONHASHSEED") != "0":
        print("WARNING: PYTHONHASHSEED is not 0; null-model z and p are not "
              "reproducible run to run. Re-run as: PYTHONHASHSEED=0 python "
              f"src/{os.path.basename(__file__)}", flush=True)


if __name__ == "__main__":
    _hash_seed_guard()

BLOCK = 250
OBS = {"CNS_VASCULAR": 1.34, "MYELOID_CYTOKINE": 0.81}


def main() -> int:
    nodes, idx, A = rwr_mod.build(rwr_mod.load_edges(
        os.path.join(DATA, "omnipath_interactions_20261116.tsv")))
    keep, A = rwr_mod.giant(A)
    nodes = [nodes[i] for i in keep]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    deg = np.asarray(A.sum(1)).ravel()
    lu = rwr_mod.make_solver(A)

    def mod(path):
        out: dict[str, list[str]] = {}
        with open(path, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                g = row["gene"].strip()
                if g in idx:
                    out.setdefault(row["module"], []).append(g)
        return {k: sorted(set(v)) for k, v in out.items()}

    mods = mod(os.path.join(HERE, "config", "modules.csv"))
    eng = mod(os.path.join(HERE, "config", "engineered_modules.csv"))
    masks = {r: np.isin(np.arange(n), [idx[g] for g in mods[r]])
             for r in ["CNS_VASCULAR", "MYELOID_CYTOKINE"]}

    rng = random.Random(SEED)
    arr = np.array(nodes)
    bins = [list(arr[c]) for c in np.array_split(np.argsort(deg), 10)]
    bin_of = {g: i for i, b in enumerate(bins) for g in b}

    def matched(profile, k):
        out, used = [], set()
        for g in profile[:k]:
            b = bins[bin_of[g]]
            for _ in range(300):
                c = b[rng.randrange(len(b))]
                if c not in used:
                    break
            used.add(c)
            out.append(idx[c])
        return out

    prof_a = eng["COSTIM_CD28"][:K]
    prof_b = eng["COSTIM_41BB"][:K]
    sets = [(matched(prof_a, K), matched(prof_b, K)) for _ in range(max(NA, NB))]

    mass = {r: (np.empty(max(NA, NB)), np.empty(max(NA, NB))) for r in masks}
    done = 0
    while done < max(NA, NB):
        b = min(BLOCK, max(NA, NB) - done)
        first = [sets[i][0] for i in range(done, done + b)]
        second = [sets[i][1] for i in range(done, done + b)]
        P1 = rwr_mod.rwr_block(lu, n, first)
        P2 = rwr_mod.rwr_block(lu, n, second)
        for r, m in masks.items():
            mass[r][0][done:done + b] = P1[m, :].sum(0)
            mass[r][1][done:done + b] = P2[m, :].sum(0)
        done += b
        print(f"  {done}/{max(NA, NB)}", flush=True)

    np.savez_compressed(os.path.join(OUT, "network_null_ratio_samples.npz"),
                        **{f"{r}_{side}": mass[r][i]
                           for r in mass for i, side in enumerate(["A", "B"])})
    out = {"k": K, "n_pairs": NA}
    for r, (ma, mb) in mass.items():
        ratio = ma[:NA] / mb[:NB]
        ratio = ratio[np.isfinite(ratio)]
        obs = OBS[r]
        out[r] = {"null_median": float(np.median(ratio)),
                  "null_sd": float(ratio.std(ddof=1)),
                  "q": {str(q): float(np.quantile(ratio, q))
                        for q in (0.025, 0.05, 0.5, 0.95, 0.975)},
                  "observed_ratio": obs,
                  "z": float((obs - ratio.mean()) / ratio.std(ddof=1)),
                  "p_greater": float((ratio >= obs).mean()),
                  "p_less": float((ratio <= obs).mean())}
    with open(os.path.join(OUT, "network_null_ratio.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
