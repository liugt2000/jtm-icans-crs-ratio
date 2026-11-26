"""
92_positive_control.py -- does the degree-matched null actually work on a known positive?

WHY THIS FILE EXISTS
--------------------
Every network claim in this paper rests on one null: gene set A is replaced by a
degree-decile-matched random set, the same for B, and the observed RWR mass is read
against that null. That construction is only worth something if it is calibrated
(it centres on 1 for unrelated sets) and sensitive (it separates related sets from
unrelated ones). Neither property has been demonstrated. A referee is entitled to
ask: has this null ever been run on a pair that is known to be proximal?

So we run it on pairs whose relatedness is fixed by an external curation we did not
write, and we score them with exactly the statistic and exactly the null used in
05_network_rwr.py and 08_network_null_ratio.py: alpha = 0.70, seeds uniform over the
set, degree-decile matching, 1,000 draws.

PAIRS
-----
PC-A  Reactome pathway, split into two disjoint halves of k = 19. A pathway is a
      connected functional module, so its two halves are related by construction.
      40 pathways, taken at even intervals from the non-redundant candidates (see
      below) so that the choice is fixed before any statistic is computed.
PC-B  Subunits of one physical complex, split into two groups: 40S vs 60S ribosomal
      proteins, 20S proteasome alpha vs beta, 19S ATPase vs base. These are the
      tightest relatedness the interactome can express, so they give the ceiling.
PC-C  HEPATOCYTE_NEGCTRL against a pathway half. This is the floor: two sets with no
      reason to be proximal should land on 1.00.
PC-D  Ten independent random pairs, scored the same way. The p-values should be
      roughly uniform; we report how many fall below 0.05 as an implementation audit.
PC-E  A second, independent split of six pathways. If the fold moved with the split,
      the first splits would be doing the work rather than the biology.

STATISTIC
---------
Two are reported, because they answer different questions.

The primary one is the statistic of 05_network_rwr.py: m(A->B), the RWR mass from a
uniform seed on A summed over B, with B held fixed and only A replaced by a
degree-decile-matched random set. That is exactly the quantity behind every
enrichment fold in the paper (COSTIM_CD28 onto MYELOID_CYTOKINE = 2.04), so a
positive control has to use it or it controls something else.

The secondary one symmetrises the pair, S = sqrt(m(A->B) * m(B->A)) with both sets
randomised, since the restart sits at the seed and the two directions are not equal.
It is much noisier (the geometric mean of two small masses), so it is reported as a
robustness check and not as the headline.

Fold is observed over the null mean; p is the fraction of null draws at or above the
observed value. Fold is the quantity of interest because it does not depend on 1,000
draws the way p does. fold_ab_med divides by the null median instead of the mean,
which is the fold an unrelated pair centres on (1.00) rather than the right-skewed
mean.

WHAT THIS CAN AND CANNOT SAY
----------------------------
This calibrates the proximity statistic used for the enrichment results. It does not
transfer to the CD28-vs-4-1BB contrast, which is a ratio of two proximities and
carries the variance of both (sigma_log = 0.884 at k = 19, hence the 11.9x minimum
detectable ratio in out/power_network.json). The two quantities are reported
separately and are not interchangeable.

Numerics: SPLU factorisation of (I - alpha*W^T) fills in 147x, so each solve costs
~40 ms and batching columns is slower per column than looping single vectors. All
solves are therefore single-column; 1,000 null draws cost about 80 s per pair.
Results are checkpointed after every pair so an interrupted run resumes.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import time
from collections import defaultdict

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rwr", os.path.join(_here, "05_network_rwr.py"))
rwr_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rwr_mod)

HERE = os.path.dirname(_here)
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
GMT = os.path.join(DATA, "reactome_pathways_v98_20261125.gmt")

ALPHA = 0.70
K = 19
NPERM = 1000
SEED = 20261125

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

MIN_GENES, MAX_GENES = 60, 120          # pathway window, in-graph genes
N_PATHWAY = 40
N_AUDIT = 10
DUP_SPLITS = 6
JACCARD = 0.5

CKPT = os.path.join(OUT, "positive_control_partial.json")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pathways(nodes: set[str]) -> list[tuple[int, str, str, list[str]]]:
    """Reactome GMT -> (n_in_graph, id, name, genes), non-redundant, evenly spaced.

    Candidates are pathways with 60-120 genes present in the interactome. Two
    pathways are treated as redundant when their Jaccard overlap exceeds 0.5, which
    removes the near-duplicate cascade families (nine TLR variants, the HIV phase
    pathways) that would otherwise dominate the count. Of the survivors we take 40 at
    even intervals in Reactome-ID order. The interval rule is fixed here, before any
    statistic exists, so the selection cannot depend on the result.
    """
    cand: list[tuple[int, str, str, frozenset[str]]] = []
    with open(GMT, encoding="utf-8") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 3:
                continue
            genes = frozenset(g for g in f[2:] if g in nodes)
            if MIN_GENES <= len(genes) <= MAX_GENES:
                cand.append((len(genes), f[1], f[0], genes))
    cand.sort(key=lambda r: r[1])

    kept: list[tuple[int, str, str, frozenset[str]]] = []
    for row in cand:
        if all(len(row[3] & o[3]) / len(row[3] | o[3]) < JACCARD for o in kept):
            kept.append(row)

    if len(kept) <= N_PATHWAY:
        pick = kept
    else:
        idx = [round(i * (len(kept) - 1) / (N_PATHWAY - 1)) for i in range(N_PATHWAY)]
        pick = [kept[i] for i in dict.fromkeys(idx)]
    return [(n, rid, name, sorted(genes)) for n, rid, name, genes in pick], len(cand), len(kept)


def regex_set(nodes: list[str], pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return sorted(g for g in nodes if rx.match(g))


def main() -> int:
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)

    nodes, idx, A = rwr_mod.build(rwr_mod.load_edges(
        os.path.join(DATA, "omnipath_interactions_20261116.tsv")))
    keep, A = rwr_mod.giant(A)
    nodes = [nodes[i] for i in keep]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    nodeset = set(nodes)
    deg = np.asarray(A.sum(1)).ravel()
    lu = rwr_mod.make_solver(A)
    print(f"graph {n} nodes, {A.nnz // 2} edges, mean degree {deg.mean():.2f} "
          f"({time.time() - t0:.0f}s)", flush=True)

    # degree-decile bins, identical construction to 05/08
    order = np.argsort(deg)
    arr = np.array(nodes)
    bins = [list(arr[c]) for c in np.array_split(order, 10)]
    bin_of = {g: i for i, b in enumerate(bins) for g in b}

    def field(seeds: list[int]) -> np.ndarray:
        b = np.zeros(n)
        b[seeds] = 1.0 / len(seeds)
        return np.maximum(lu.solve((1.0 - ALPHA) * b), 0.0)

    def mass(a: list[int], b: list[int]) -> float:
        return float(field(a)[b].sum())

    def stat(a: list[int], b: list[int]) -> float:
        m_ab, m_ba = mass(a, b), mass(b, a)
        return math.sqrt(max(m_ab, 0.0) * max(m_ba, 0.0))

    def matched(profile: list[str], rng: random.Random) -> list[int]:
        out, used = [], set()
        for g in profile:
            b = bins[bin_of[g]]
            for _ in range(300):
                c = b[rng.randrange(len(b))]
                if c not in used:
                    break
            used.add(c)
            out.append(idx[c])
        return out

    def split_half(genes: list[str], k: int, rng: random.Random) -> tuple[list[str], list[str]]:
        """Balance the two halves on degree decile so the split itself is not a confound."""
        by_bin: dict[int, list[str]] = defaultdict(list)
        for g in genes:
            by_bin[bin_of[g]].append(g)
        order_: list[str] = []
        for bi in sorted(by_bin):
            lst = by_bin[bi][:]
            rng.shuffle(lst)
            order_.extend(lst)
        a = order_[0::2][:k]
        b = order_[1::2][:k]
        return a, b

    # ---- pair definitions -------------------------------------------------
    pathways, n_cand, n_kept = load_pathways(nodeset)
    print(f"pathways: {n_cand} candidates, {n_kept} non-redundant, "
          f"{len(pathways)} used", flush=True)

    pairs: list[dict] = []
    for i, (n_g, rid, name, genes) in enumerate(pathways, 1):
        rng = random.Random(f"{SEED}:pathway:{rid}")
        a, b = split_half(genes, K, rng)
        pairs.append({"id": f"PCA{i:02d}", "kind": "pathway_half",
                      "name": f"{name} ({rid})", "a": a, "b": b, "note": ""})
        if i <= DUP_SPLITS:
            rng2 = random.Random(f"{SEED}:pathway2:{rid}")
            a2, b2 = split_half(genes, K, rng2)
            pairs.append({"id": f"PCA{i:02d}s", "kind": "pathway_half_split2",
                          "name": f"{name} ({rid})", "a": a2, "b": b2,
                          "note": "second independent split"})

    def rnd(lst: list[str], k: int, seed: str) -> list[str]:
        r = random.Random(f"{SEED}:{seed}")
        out = lst[:]
        r.shuffle(out)
        return out[:k]

    rps = regex_set(nodes, r"^RPS\d+[A-Z]?$")
    rpl = regex_set(nodes, r"^RPL\d+[A-Z]?$")
    psma = regex_set(nodes, r"^PSMA\d+$")
    psmb = regex_set(nodes, r"^PSMB\d+$")
    psmc = regex_set(nodes, r"^PSMC\d+$")
    psmd = regex_set(nodes, r"^PSMD\d+$")

    pairs += [
        {"id": "PCB1", "kind": "complex", "name": "Ribosome: 40S (RPS) vs 60S (RPL)",
         "a": rnd(rps, K, "rps"), "b": rnd(rpl, K, "rpl"),
         "note": f"{len(rps)} RPS / {len(rpl)} RPL in graph, subsampled to k={K}"},
        {"id": "PCB2", "kind": "complex", "name": "20S proteasome: alpha (PSMA) vs beta (PSMB)",
         "a": psma, "b": psmb, "note": f"natural size {len(psma)}/{len(psmb)}"},
        {"id": "PCB3", "kind": "complex", "name": "19S proteasome: ATPase (PSMC) vs base (PSMD)",
         "a": psmc, "b": psmd, "note": f"natural size {len(psmc)}/{len(psmd)}"},
    ]

    hep = sorted({r["gene"].strip() for r in csv.DictReader(
        open(os.path.join(HERE, "config", "modules.csv"), encoding="utf-8-sig"))
        if r["module"] == "HEPATOCYTE_NEGCTRL" and r["gene"].strip() in idx})
    first_halves = [p for p in pairs if p["kind"] == "pathway_half"][:3]
    for j, ref in enumerate(first_halves, 1):
        pairs.append({"id": f"PCC{j}", "kind": "negative",
                      "name": f"HEPATOCYTE_NEGCTRL vs half of {ref['name']}",
                      "a": hep, "b": ref["a"],
                      "note": f"natural size {len(hep)}/{len(ref['a'])}"})

    rng = random.Random(f"{SEED}:audit")
    allg = list(nodes)
    for j in range(1, N_AUDIT + 1):
        a = rng.sample(allg, K)
        b = rng.sample(allg, K)
        pairs.append({"id": f"PCD{j:02d}", "kind": "random_pair",
                      "name": "independent random pair", "a": a, "b": b,
                      "note": "type-I audit"})

    # ---- run ---------------------------------------------------------------
    done: dict[str, dict] = {}
    if os.path.exists(CKPT):
        done = json.load(open(CKPT, encoding="utf-8"))
        print(f"resuming with {len(done)} pairs already scored", flush=True)

    samples: dict[str, list[float]] = {}
    for p in pairs:
        if p["id"] in done:
            continue
        a = [idx[g] for g in p["a"]]
        b = [idx[g] for g in p["b"]]
        a_genes = [g for g in p["a"]]
        b_genes = [g for g in p["b"]]
        s_obs = stat(a, b)
        m_ab = mass(a, b)
        m_ba = mass(b, a)
        rng_p = random.Random(f"{SEED}:null:{p['id']}")
        n_ab = np.empty(NPERM)
        n_ba = np.empty(NPERM)
        tp = time.time()
        for i in range(NPERM):
            a2 = matched(a_genes, rng_p)
            b2 = matched(b_genes, rng_p)
            n_ab[i] = mass(a2, b)          # target fixed, seed randomised: the 05 statistic
            n_ba[i] = mass(b2, a)
        n_sym = np.sqrt(n_ab * n_ba)
        mu, sd = float(n_ab.mean()), float(n_ab.std(ddof=1))
        mu2 = float(n_ba.mean())
        mus, sds = float(n_sym.mean()), float(n_sym.std(ddof=1))
        row = {"id": p["id"], "kind": p["kind"], "name": p["name"], "note": p["note"],
               "k_a": len(a), "k_b": len(b),
               "mass_ab": m_ab, "null_ab_mean": mu, "null_ab_sd": sd,
               "fold_ab": m_ab / mu if mu > 0 else float("nan"),
               "z_ab": (m_ab - mu) / sd if sd > 0 else float("nan"),
               "p_ab": float((n_ab >= m_ab).mean()),
               "fold_ab_med": m_ab / float(np.median(n_ab)) if np.median(n_ab) > 0 else float("nan"),
               "mass_ba": m_ba, "null_ba_mean": mu2,
               "fold_ba": m_ba / mu2 if mu2 > 0 else float("nan"),
               "p_ba": float((n_ba >= m_ba).mean()),
               "s_obs": s_obs, "null_sym_mean": mus, "null_sym_sd": sds,
               "fold_sym": s_obs / mus if mus > 0 else float("nan"),
               "z_sym": (s_obs - mus) / sds if sds > 0 else float("nan"),
               "p_sym": float((n_sym >= s_obs).mean()),
               "null_ab_q025": float(np.quantile(n_ab, 0.025)),
               "null_ab_q50": float(np.median(n_ab)),
               "null_ab_q975": float(np.quantile(n_ab, 0.975))}
        done[p["id"]] = row
        samples[p["id"]] = n_ab.tolist()
        json.dump(done, open(CKPT, "w", encoding="utf-8"), indent=1)
        print(f"  {p['id']:6s} {p['kind']:22s} fold {row['fold_ab']:6.2f}/{row['fold_ba']:6.2f}  "
              f"p {row['p_ab']:.3f}/{row['p_ba']:.3f}  k {row['k_a']}/{row['k_b']}  "
              f"[{time.time() - tp:.0f}s, total {time.time() - t0:.0f}s] {p['name'][:40]}",
              flush=True)

    rows = [done[p["id"]] for p in pairs if p["id"] in done]
    order_id = {p["id"]: i for i, p in enumerate(pairs)}
    rows.sort(key=lambda r: order_id[r["id"]])

    # fold of the pathway prior (negative control should sit at 1)
    def summarise(kind: str) -> dict:
        v = [r for r in rows if r["kind"] == kind]
        if not v:
            return {}
        folds = np.array([r["fold_ab"] for r in v], dtype=float)
        ps = np.array([r["p_ab"] for r in v], dtype=float)
        meds = np.array([r["fold_ab_med"] for r in v], dtype=float)
        sig = folds[ps < 0.05]
        return {"n": len(v),
                "fold_median": float(np.median(folds)),
                "fold_q1": float(np.quantile(folds, 0.25)),
                "fold_q3": float(np.quantile(folds, 0.75)),
                "fold_min": float(folds.min()),
                "fold_max": float(folds.max()),
                "fold_vs_null_median_median": float(np.median(meds)),
                "n_p_lt_0.05": int((ps < 0.05).sum()),
                "frac_p_lt_0.05": float((ps < 0.05).mean()),
                "frac_p_lt_0.01": float((ps < 0.01).mean()),
                "min_fold_significant": float(sig.min()) if len(sig) else None,
                "max_fold_not_significant": (float(folds[ps >= 0.05].max())
                                             if (ps >= 0.05).any() else None),
                "p_median": float(np.median(ps))}

    # empirical detection floor: smallest fold at which 80% of pathway pairs clear 0.05
    pw = sorted([r for r in rows if r["kind"] == "pathway_half"],
                key=lambda r: r["fold_ab"])
    floor80 = None
    if pw:
        for i in range(len(pw)):
            tail = pw[i:]
            if np.mean([1.0 if r["p_ab"] < 0.05 else 0.0 for r in tail]) >= 0.8:
                floor80 = pw[i]["fold_ab"]
                break

    summary = {"pathway_half": summarise("pathway_half"),
               "complex": summarise("complex"),
               "negative": summarise("negative"),
               "random_pair": summarise("random_pair"),
               "pathway_half_split2": summarise("pathway_half_split2"),
               "empirical_fold_for_80pct_detection": floor80}

    out = {"params": {"alpha": ALPHA, "k": K, "n_perm": NPERM, "seed": SEED,
                      "pathway_window_genes": [MIN_GENES, MAX_GENES],
                      "n_pathways": len(pathways), "jaccard_max": JACCARD,
                      "n_nodes": n, "mean_degree": float(deg.mean()),
                      "gmt": os.path.basename(GMT), "gmt_sha256": sha256(GMT),
                      "reactome_version": "98",
                      "interactome_sha256": sha256(
                          os.path.join(DATA, "omnipath_interactions_20261116.tsv"))},
           "summary": summary, "pairs": rows}

    with open(os.path.join(OUT, "positive_control.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    with open(os.path.join(OUT, "positive_control.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        cols = ["id", "kind", "name", "note", "k_a", "k_b",
                "mass_ab", "null_ab_mean", "null_ab_sd", "fold_ab", "fold_ab_med",
                "z_ab", "p_ab", "mass_ba", "null_ba_mean", "fold_ba", "p_ba",
                "fold_sym", "p_sym", "null_ab_q025", "null_ab_q50", "null_ab_q975"]
        w.writerow(cols)
        for r in rows:
            w.writerow([f"{r[c]:.6g}" if isinstance(r[c], float) else r[c] for c in cols])

    if samples:
        np.savez_compressed(os.path.join(OUT, "positive_control_samples.npz"),
                            **{k: np.array(v) for k, v in samples.items()})

    print("\nSUMMARY")
    for k, v in summary.items():
        print(f"  {k:22s} {json.dumps(v) if isinstance(v, dict) else v}")
    print(f"\nwrote out/positive_control.csv/.json in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
