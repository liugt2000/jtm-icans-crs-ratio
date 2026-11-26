"""
05_network_rwr.py -- the discriminating network statistic.

Why this file exists
--------------------
The Guney/Menche 'closest distance' is the textbook proximity measure, but on a
curated interactome with mean degree ~16 and a 36-gene reference module it
SATURATES: almost every gene is 1 or 2 hops from the module. Its null mean is 1.65
and the observed value 1.46 -- a difference on a quantity whose support is {1,2,3}
(out/network_proximity.csv). So we report it, but we do not build a claim on it.

Random-walk-with-restart (RWR) mass is the primary statistic instead: it is
continuous, cannot saturate, and is the standard proximity operator in this
literature.

Two corrections a methods referee would demand, both applied here:
  * SIZE MATCHING. COSTIM_CD28 has 26 genes in the graph, COSTIM_41BB has 19. A
    larger seed set accumulates more mass on any target purely by size, so every
    CD28-vs-41BB contrast is recomputed on 1000 random 19-gene subsets of COSTIM_CD28.
    The unadjusted ratio is reported too, flagged as size-confounded.
  * DEGREE MATCHING. Seeds are replaced by degree-decile-matched random genes.

Implementation note: splu factorisation of (I - alpha*W^T) costs ~54 s; individual
solves cost ~76 ms each, so 13000 per-permutation solves would take hours. All
right-hand sides are therefore batched into dense blocks and solved in one call.
"""
from __future__ import annotations

import csv
import json
import os
import random
import warnings

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import splu

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
ALPHA = 0.70
NPERM = 2000
NSUB = 1000
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


def load_edges(path):
    edges = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["entity_type_source"] != "protein" or row["entity_type_target"] != "protein":
                continue
            a, b = row["source_genesymbol"].strip(), row["target_genesymbol"].strip()
            if a and b and a != b:
                edges.add((a, b))
                edges.add((b, a))
    return edges


def build(edges):
    nodes = sorted({x for e in edges for x in e})
    idx = {n: i for i, n in enumerate(nodes)}
    rows = np.fromiter((idx[a] for a, _ in edges), dtype=np.int32, count=len(edges))
    cols = np.fromiter((idx[b] for _, b in edges), dtype=np.int32, count=len(edges))
    A = sp.csr_matrix((np.ones(len(edges)), (rows, cols)),
                      shape=(len(nodes), len(nodes)))
    A.data[:] = 1.0
    return nodes, idx, A


def giant(A):
    n = A.shape[0]
    S = A + A.T
    S.data[:] = 1.0
    seen = np.zeros(n, bool)
    best: list[int] = []
    for s in range(n):
        if seen[s]:
            continue
        stack, comp = [s], []
        seen[s] = True
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in S.indices[S.indptr[u]:S.indptr[u + 1]]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        if len(comp) > len(best):
            best = comp
    sub = np.array(sorted(best))
    return sub, A[sub][:, sub]


def make_solver(A, alpha=ALPHA):
    deg = np.asarray(A.sum(1)).ravel()
    deg[deg == 0] = 1.0
    WT = (sp.diags(1.0 / deg) @ A).T.tocsr()
    M = (sp.identity(A.shape[0], format="lil") - alpha * WT).tocsr().astype(np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return splu(M)


def rwr_block(lu, n, seeds_list, alpha=ALPHA):
    """Solve RWR for a block of seed sets at once. Returns n x len(seeds_list)."""
    B = np.zeros((n, len(seeds_list)))
    for j, s in enumerate(seeds_list):
        B[s, j] = 1.0 / len(s)
    return np.maximum(lu.solve((1 - alpha) * B), 0.0)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    nodes, idx, A = build(load_edges(os.path.join(DATA, "omnipath_interactions_20261116.tsv")))
    keep, A = giant(A)
    nodes = [nodes[i] for i in keep]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    deg = np.asarray(A.sum(1)).ravel()
    print(f"graph: {n} nodes, {A.nnz // 2} undirected edges, mean degree {deg.mean():.1f}", flush=True)
    lu = make_solver(A)
    print("factorisation done", flush=True)

    def mod(path):
        out: dict[str, list[str]] = {}
        with open(path, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                g = row["gene"].strip()
                if g in idx:
                    out.setdefault(row["module"], []).append(g)
        return {k: sorted(set(v)) for k, v in out.items()}

    mods = {**mod(os.path.join(HERE, "config", "modules.csv")),
            **mod(os.path.join(HERE, "config", "engineered_modules.csv"))}
    print("modules in graph:", {k: len(v) for k, v in mods.items()}, flush=True)

    rng = random.Random(SEED)
    order = np.argsort(deg)
    arr = np.array(nodes)
    bins = [list(arr[c]) for c in np.array_split(order, 10)]
    bin_of = {g: i for i, b in enumerate(bins) for g in b}

    def sample(observed):
        out, used = [], set()
        for g in observed:
            b = bins[bin_of[g]]
            for _ in range(300):
                c = b[rng.randrange(len(b))]
                if c not in used:
                    break
            used.add(c)
            out.append(idx[c])
        return out

    refs = ["CNS_VASCULAR", "MYELOID_CYTOKINE", "HEPATOCYTE_NEGCTRL"]
    mask = {r: np.isin(np.arange(n), [idx[g] for g in mods[r]]) for r in refs}

    res: dict[str, dict] = {}
    for name, genes in mods.items():
        seeds = [idx[g] for g in genes]
        p = rwr_block(lu, n, [seeds])[:, 0]
        nulls = {r: np.empty(NPERM) for r in refs}
        done = 0
        while done < NPERM:
            b = min(BLOCK, NPERM - done)
            sets = [sample(genes) for _ in range(b)]
            P = rwr_block(lu, n, sets)
            for r in refs:
                nulls[r][done:done + b] = P[mask[r], :].sum(0)
            done += b
            print(f"  {name} null {done}/{NPERM}", flush=True)
        row = {"n_in_graph": len(genes)}
        for r in refs:
            if r == name:
                continue
            obs = float(p[mask[r]].sum())
            mu, sd = float(nulls[r].mean()), float(nulls[r].std(ddof=1))
            row[f"to_{r}"] = {
                "mass": round(obs, 6), "null_mean": round(mu, 6), "null_sd": round(sd, 6),
                "z": round((obs - mu) / sd if sd > 0 else float("nan"), 3),
                "fold": round(obs / mu, 3) if mu > 0 else None,
                "p_enriched": float((nulls[r] >= obs).mean()),
                "p_depleted": float((nulls[r] <= obs).mean()),
            }
        res[name] = row

    # ---- size-matched CD28 vs 41BB
    cd28, b41 = mods["COSTIM_CD28"], mods["COSTIM_41BB"]
    k = min(len(cd28), len(b41))
    contrast = {}
    for r in refs:
        m = mask[r]
        p41 = float(rwr_block(lu, n, [[idx[g] for g in b41]])[m, 0].sum())
        pfull = float(rwr_block(lu, n, [[idx[g] for g in cd28]])[m, 0].sum())
        subs = []
        for _ in range(0, NSUB, BLOCK):
            sets = [[idx[g] for g in rng.sample(cd28, k)]
                    for _ in range(min(BLOCK, NSUB - len(subs)))]
            subs.extend(rwr_block(lu, n, sets)[m, :].sum(0).tolist())
        subs = np.array(subs)
        contrast[r] = {
            "mass_41BB": round(p41, 6),
            "mass_CD28_full26": round(pfull, 6),
            "mass_CD28_sizematched_mean": round(float(subs.mean()), 6),
            "ci95_sizematched": [round(float(np.quantile(subs, .025)), 6),
                                 round(float(np.quantile(subs, .975)), 6)],
            "ratio_sizematched_CD28_over_41BB": round(float(subs.mean() / p41), 3),
            "frac_subsets_exceeding_41BB": round(float((subs > p41).mean()), 3),
            "ratio_size_confounded": round(pfull / p41, 3),
        }

    out = {"params": {"alpha": ALPHA, "n_perm": NPERM, "n_subsets": NSUB, "seed": SEED,
                      "n_nodes": n, "mean_degree": float(deg.mean()),
                      "interactome_sha256_prefix": "2bb2bbfb88472247"},
           "proximity": res, "costim_contrast": contrast,
           "size_matched_k": k}
    with open(os.path.join(OUT, "network_rwr.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print("\nRWR proximity (z vs degree-matched null, n=%d)" % NPERM)
    print(f"{'module':16s} {'ref':20s} {'mass':>10s} {'null':>10s} {'z':>7s} {'fold':>6s} {'p_enr':>7s}")
    for name, vals in res.items():
        for kk, v in vals.items():
            if kk.startswith("to_"):
                print(f"{name:16s} {kk[3:]:20s} {v['mass']:10.3e} {v['null_mean']:10.3e} "
                      f"{v['z']:7.2f} {v['fold']:6.2f} {v['p_enriched']:7.4f}")
    print("\nSize-matched CD28 vs 41BB (k=%d)" % k)
    for r, v in contrast.items():
        print(f"  {r:20s} r={v['ratio_sizematched_CD28_over_41BB']:.2f} "
              f"CI={v['ci95_sizematched']} frac>={v['frac_subsets_exceeding_41BB']:.3f} "
              f"(size-confounded r={v['ratio_size_confounded']:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
