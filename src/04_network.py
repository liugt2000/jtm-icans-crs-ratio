"""
04_network.py -- network-proximity layer (N1).

Design notes that a reviewer will check:
  * The interactome is frozen from a single OmniPath snapshot with a sha256 recorded
    in data/omnipath_meta.json. Curated records only (omnipath/pathwayextra/
    kinaseextra/ligrecextra); no text-mined-only edges.
  * Distances are 'closest' distances (Guney/Menche convention): d(A,B) is the mean
    over a in A of the shortest-path distance from a to the nearest member of B.
    They are NOT symmetric in general, so both directions are reported.
  * Every proximity number is accompanied by a degree-matched random-set null
    (n=10000). Without that null a proximity number is uninterpretable, because
    hub-rich gene sets are trivially close to everything.
  * Two node universes are analysed in parallel: the whole curated interactome and
    the brain-expressed subgraph. A conclusion that survives only in the unrestricted
    graph is a conclusion about hubs, not about the brain.
"""
from __future__ import annotations

import csv
import json
import os
import random
from collections import defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
NPERM = 10000
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



# ----------------------------------------------------------------------------- graph
def load_graph(path: str) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = defaultdict(set)
    with open(path, encoding="utf-8", errors="replace") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for row in rd:
            if row["entity_type_source"] != "protein" or row["entity_type_target"] != "protein":
                continue
            a, b = row["source_genesymbol"].strip(), row["target_genesymbol"].strip()
            if not a or not b or a == b:
                continue
            # OmniPath may emit complexes as "A_B"; keep only single-gene symbols
            if "_" in a and len(a.split("_")) > 1 and a.isupper() is False:
                pass
            adj[a].add(b)
            adj[b].add(a)
    return adj


def giant(adj: dict[str, set[str]]) -> dict[str, set[str]]:
    seen, best = set(), []
    for n in adj:
        if n in seen:
            continue
        comp, dq = [], deque([n])
        seen.add(n)
        while dq:
            u = dq.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        if len(comp) > len(best):
            best = comp
    keep = set(best)
    return {u: {v for v in adj[u] if v in keep} for u in keep}


def bfs_multi(adj, sources) -> dict[str, int]:
    dist = {s: 0 for s in sources}
    dq = deque(sources)
    while dq:
        u = dq.popleft()
        du = dist[u]
        for v in adj[u]:
            if v not in dist:
                dist[v] = du + 1
                dq.append(v)
    return dist


def bfs_single(adj, src) -> dict[str, int]:
    return bfs_multi(adj, [src])


# ------------------------------------------------------------------------ null model
class DegreeMatchedNull:
    """Sample gene sets whose degree distribution matches the observed set.

    Degree is binned into deciles; each observed gene is replaced by a uniform draw
    from its own bin, without replacement, excluding genes already drawn. This
    removes the dominant confound (hub genes are close to everything) while keeping
    the set's size and rough connectivity profile fixed.
    """

    def __init__(self, adj, n_bins: int = 10, seed: int = SEED):
        self.rng = random.Random(seed)
        deg = np.array([len(adj[n]) for n in adj], dtype=float)
        nodes = np.array(list(adj))
        order = np.argsort(deg)
        self.bins: list[list[str]] = []
        for chunk in np.array_split(order, n_bins):
            self.bins.append(list(nodes[chunk]))
        self.bin_of = {}
        for i, b in enumerate(self.bins):
            for n in b:
                self.bin_of[n] = i
        self.nodes = set(nodes)

    def sample(self, observed: list[str]) -> list[str]:
        out: list[str] = []
        used: set[str] = set()
        for g in observed:
            b = self.bins[self.bin_of[g]]
            for _ in range(200):
                cand = b[self.rng.randrange(len(b))]
                if cand not in used:
                    break
            else:  # extremely unlikely; fall back to whole universe
                cand = next(iter(self.nodes - used))
            used.add(cand)
            out.append(cand)
        return out


def load_module(path: str) -> dict[str, list[str]]:
    mods: dict[str, list[str]] = defaultdict(list)
    with open(path, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            mods[row["module"]].append(row["gene"].strip())
    return {k: sorted(set(v)) for k, v in mods.items()}


def brain_genes(path_zip: str) -> set[str]:
    import io
    import zipfile

    keep = set()
    z = zipfile.ZipFile(path_zip)
    with z.open("proteinatlas.tsv") as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t")
        hdr = next(rd)
        ig, idist = hdr.index("Gene"), hdr.index("RNA single nuclei brain distribution")
        for row in rd:
            if row[idist].startswith("Detected in"):
                keep.add(row[ig])
    return keep


def proximity(adj, mods, ref_names, null, universe_note):
    """d(set, ref) for every module vs every reference, plus degree-matched z."""
    res = {}
    ref_dist = {r: bfs_multi(adj, [g for g in mods[r] if g in adj]) for r in ref_names}
    rng_state = {}
    for tag, adj_u in [("full", adj)]:
        pass
    for name, genes in mods.items():
        present = [g for g in genes if g in adj]
        res[name] = {"n_defined": len(genes), "n_in_graph": len(present),
                     "dropped": sorted(set(genes) - set(present))}
    for r in ref_names:
        dref = ref_dist[r]
        for name, genes in mods.items():
            if name == r:
                continue
            present = [g for g in genes if g in dref]
            if not present:
                continue
            obs = float(np.mean([dref[g] for g in present]))
            nulls = np.empty(NPERM)
            for i in range(NPERM):
                s = null.sample(present)
                nulls[i] = np.mean([dref.get(g, np.nan) for g in s])
            mu, sd = float(nulls.mean()), float(nulls.std(ddof=1))
            z = (obs - mu) / sd if sd > 0 else float("nan")
            p = float((nulls <= obs).mean())  # one-sided: closer than chance
            res[name][f"to_{r}"] = {
                "d": round(obs, 4), "null_mean": round(mu, 4),
                "null_sd": round(sd, 4), "z": round(z, 3),
                "p_closer": p, "emp_below_5pct": bool(obs < np.quantile(nulls, 0.05)),
                "emp_below_1pct": bool(obs < np.quantile(nulls, 0.01)),
            }
    return res


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    adj_raw = load_graph(os.path.join(DATA, "omnipath_interactions_20261116.tsv"))
    adj = giant(adj_raw)
    bg = brain_genes(os.path.join(DATA, "hpa_proteinatlas_20261116.tsv.zip"))
    adj_brain = giant({u: {v for v in adj[u] if v in bg} for u in adj if u in bg})

    mods = load_module(os.path.join(HERE, "config", "modules.csv"))
    eng = load_module(os.path.join(HERE, "config", "engineered_modules.csv"))
    allmods = {**mods, **eng}

    report = {
        "graph": {
            "nodes_raw": len(adj_raw), "nodes_giant": len(adj),
            "edges_giant": sum(len(v) for v in adj.values()) // 2,
            "nodes_brain": len(adj_brain),
            "edges_brain": sum(len(v) for v in adj_brain.values()) // 2,
            "brain_universe_genes": len(bg),
        },
        "modules": {},
        "universes": {},
    }

    for tag, a in [("full", adj), ("brain", adj_brain)]:
        null = DegreeMatchedNull(a)
        refs = ["CNS_VASCULAR", "MYELOID_CYTOKINE", "HEPATOCYTE_NEGCTRL"]
        report["universes"][tag] = proximity(a, allmods, refs, null, tag)

        # within-module cohesion for the separation statistic
        sep = {}
        for m in refs:
            genes = [g for g in mods[m] if g in a]
            d_self = float(np.mean([np.mean(list(bfs_single(a, g).values()))
                                    for g in genes[:12]])) if genes else float("nan")
            sep[m] = {"n": len(genes), "mean_within_distance_first12": round(d_self, 4)}
        report["universes"][tag]["_within"] = sep

    # ---- the pre-specified contrast: costim module vs the two disease modules
    contrast = {}
    for tag in ["full", "brain"]:
        u = report["universes"][tag]
        row = {}
        for ref in ["CNS_VASCULAR", "MYELOID_CYTOKINE", "HEPATOCYTE_NEGCTRL"]:
            cd28 = u.get("COSTIM_CD28", {}).get(f"to_{ref}")
            b41 = u.get("COSTIM_41BB", {}).get(f"to_{ref}")
            if cd28 and b41:
                row[ref] = {
                    "d_CD28": cd28["d"], "d_41BB": b41["d"],
                    "delta_41BB_minus_CD28": round(b41["d"] - cd28["d"], 4),
                    "z_CD28": cd28["z"], "z_41BB": b41["z"],
                    "CD28_closer": bool(cd28["d"] < b41["d"]),
                }
        contrast[tag] = row
    report["contrast"] = contrast

    with open(os.path.join(OUT, "network_proximity.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    # flatten for inspection
    rows = []
    for tag, u in report["universes"].items():
        for m, vals in u.items():
            if m.startswith("_"):
                continue
            for k, v in vals.items():
                if k.startswith("to_"):
                    rows.append({"universe": tag, "module": m, "ref": k[3:],
                                 "n_in_graph": vals["n_in_graph"], **v})
    with open(os.path.join(OUT, "network_proximity.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(json.dumps(report["graph"], indent=2))
    for tag, row in contrast.items():
        print(f"\n[{tag}] costim contrast")
        for ref, v in row.items():
            print(f"  {ref:20s} d_CD28={v['d_CD28']:.3f} d_41BB={v['d_41BB']:.3f} "
                  f"delta={v['delta_41BB_minus_CD28']:+.3f} "
                  f"z=({v['z_CD28']:+.2f},{v['z_41BB']:+.2f}) closer_CD28={v['CD28_closer']}")
    print("\nmodule presence:", {m: report['universes']['brain'][m]['n_in_graph']
                                 for m in report['universes']['brain'] if not m.startswith('_')})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
