"""
06_perturbation.py -- orthogonal validation that does not depend on FAERS at all.

Two questions, both answerable from primary expression data with the two GEO series
already downloaded:

  Q1 (localisation, GSE195519)  Are the two modules expressed in the cell types the
     model says they belong to? CNS_VASCULAR should sit in brain endothelial cells
     and not in undifferentiated iPSC; MYELOID_CYTOKINE should not be endothelial-
     restricted. If both modules look the same in endothelium, the "two distinct
     modules" premise is false and the paper has to be rewritten, not patched.

  Q2 (responsiveness, GSE211439)  In human brain microvascular endothelial cells
     stimulated with TNF-alpha, does the neurovascular module move more than the
     myeloid module? This is the FALSIFICATION test: if the myeloid module responds
     just as strongly in endothelium, then the modules are not separable in the
     relevant cell type and the dissociation claim collapses.

Null model: each module's statistic is compared with 10000 random gene sets of the
same size, drawn from genes matched on mean-expression decile. Expression matching
matters because module genes are deliberately chosen to be well expressed; without
it any module would "respond" more than a random set.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import os
import random

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
NPERM = 10000
SEED = 20261116


def read_matrix(path, gene_header):
    """Read a gene x sample matrix, tolerating a header that lacks a gene-column name.

    GSE211439 ships a header of bare sample IDs with no label for the gene column,
    while GSE195519 labels both 'ENTREZ ID' and 'gene symbol'. The column count of the
    first data line is what decides, not the header text.
    """
    opener = gzip.open if path.endswith(".gz") else open
    id_like = {"entrez id", "gene", "gene symbol", "gene id", "id", "probe id"}
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        first = fh.readline().rstrip("\n")
        sep = "\t" if first.count("\t") > first.count(",") else ","
        header = [f.strip().strip('"') for f in first.split(sep)]
        probe = fh.readline().rstrip("\n").split(sep)
        ncol = len(probe)
        if len(probe) == len(header) + 1:
            # gene column carries no header label -> it is column 0
            gene_col, sample_idx = 0, list(range(1, ncol))
        elif len(probe) == len(header):
            gene_col = next((i for i, h in enumerate(header)
                             if h.lower().startswith(gene_header.lower())), 0)
            sample_idx = [i for i, h in enumerate(header)
                          if i != gene_col and h.lower() not in id_like]
        else:
            raise ValueError(f"unexpected column count in {path}: "
                             f"header={len(header)} first_row={len(probe)}")
        samples = [header[i] if len(header) == ncol else header[i - 1] for i in sample_idx]
        rows, genes = [], []
        for line in [sep.join(probe)] + fh.readlines():
            p = line.rstrip("\n").split(sep)
            if len(p) != ncol:
                continue
            g = p[gene_col].strip().strip('"')
            if not g:
                continue
            try:
                v = [float(p[i]) for i in sample_idx]
            except ValueError:
                continue
            genes.append(g)
            rows.append(v)
    return samples, genes, np.array(rows, dtype=float)


def log_cpm(X):
    lib = X.sum(0)
    lib[lib == 0] = 1.0
    return np.log2(X / lib * 1e6 + 1.0)


def load_modules():
    mods: dict[str, list[str]] = {}
    for f in ["modules.csv", "engineered_modules.csv"]:
        with open(os.path.join(HERE, "config", f), encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                mods.setdefault(row["module"], set()).add(row["gene"].strip())
    return {k: sorted(v) for k, v in mods.items()}


class ExprMatchedNull:
    """Random gene sets matched on mean-expression decile and set size."""

    def __init__(self, mean_expr: np.ndarray, genes: list[str], seed=SEED):
        self.rng = random.Random(seed)
        order = np.argsort(mean_expr)
        self.bins = [[genes[i] for i in c] for c in np.array_split(order, 10)]
        self.bin_of = {g: i for i, b in enumerate(self.bins) for g in b}
        self.all = set(genes)

    def sample(self, obs):
        out, used = [], set()
        for g in obs:
            b = self.bins[self.bin_of[g]]
            for _ in range(300):
                c = b[self.rng.randrange(len(b))]
                if c not in used:
                    break
            used.add(c)
            out.append(c)
        return out


def module_test(values: dict[str, float], observed_genes: list[str], null: ExprMatchedNull,
                higher_is_better: bool = True):
    present = [g for g in observed_genes if g in values]
    if len(present) < 3:
        return None
    v = np.array([values[g] for g in present])
    obs = float(v.mean())
    nulls = np.empty(NPERM)
    for i in range(NPERM):
        s = null.sample(present)
        nulls[i] = np.mean([values[g] for g in s])
    mu, sd = float(nulls.mean()), float(nulls.std(ddof=1))
    p_hi = float((nulls >= obs).mean())
    p_lo = float((nulls <= obs).mean())
    return {"n_genes": len(present), "observed": round(obs, 4),
            "gene_mean_ci95": [round(float(np.quantile(v, .025)), 4),
                               round(float(np.quantile(v, .975)), 4)],
            "null_mean": round(mu, 4), "null_sd": round(sd, 4),
            "z": round((obs - mu) / sd if sd else float("nan"), 3),
            "p_enriched": p_hi, "p_depleted": p_lo,
            "per_gene": dict(zip(present, np.round(v, 4).tolist()))}


def main() -> int:
    mods = load_modules()
    report: dict = {"modules": {k: len(v) for k, v in mods.items()}}

    # ---------------- Q1: cell-type localisation (GSE195519) -------------------
    samples, genes, X = read_matrix(os.path.join(DATA, "GSE195519_raw_counts.csv.gz"), "gene symbol")
    L = log_cpm(X)
    keep = L.mean(1) > 1.0
    genes_k = [g for g, k in zip(genes, keep) if k]
    L = L[keep]
    gidx = {g: i for i, g in enumerate(genes_k)}
    print(f"GSE195519: {len(genes_k)} expressed genes x {len(samples)} samples")
    groups = {"iBMEC": [i for i, s in enumerate(samples) if "iBMEC" in s],
              "iPSC": [i for i, s in enumerate(samples) if "iPSC" in s],
              "iPC": [i for i, s in enumerate(samples) if "iPC" in s],
              "HDMEC": [i for i, s in enumerate(samples) if "HDMEC" in s]}
    print("group sizes:", {k: len(v) for k, v in groups.items() if v})
    null1 = ExprMatchedNull(L.mean(1), genes_k)
    q1 = {}
    if groups["iBMEC"] and groups["iPSC"]:
        delta = L[:, groups["iBMEC"]].mean(1) - L[:, groups["iPSC"]].mean(1)
        dvals = dict(zip(genes_k, delta))
        q1["iBMEC_minus_iPSC"] = {m: module_test(dvals, g, null1) for m, g in mods.items()}
    if groups["HDMEC"] and groups["iPC"]:
        delta = L[:, groups["HDMEC"]].mean(1) - L[:, groups["iPC"]].mean(1)
        dvals = dict(zip(genes_k, delta))
        q1["HDMEC_minus_iPC"] = {m: module_test(dvals, g, null1) for m, g in mods.items()}
    report["Q1_localisation"] = q1

    # ---------------- Q2: TNF-alpha response in hBMEC (GSE211439) --------------
    samples2, genes2, X2 = read_matrix(os.path.join(DATA, "GSE211439_processed_count.txt.gz"), "gene")
    L2 = log_cpm(X2)
    keep2 = L2.mean(1) > 1.0
    genes2k = [g for g, k in zip(genes2, keep2) if k]
    L2 = L2[keep2]
    print(f"GSE211439: {len(genes2k)} expressed genes x {len(samples2)} samples {samples2}")
    ctrl = [i for i, s in enumerate(samples2) if s.upper().startswith("M")]
    tnf = [i for i, s in enumerate(samples2) if s.upper().startswith("T")]
    print(f"  control={len(ctrl)} TNF-alpha={len(tnf)}")
    lfc = L2[:, tnf].mean(1) - L2[:, ctrl].mean(1)
    lvals = dict(zip(genes2k, lfc))
    absvals = {g: abs(v) for g, v in lvals.items()}
    null2 = ExprMatchedNull(L2.mean(1), genes2k, seed=SEED + 1)
    q2 = {"signed_log2FC": {m: module_test(lvals, g, null2) for m, g in mods.items()},
          "absolute_log2FC": {m: module_test(absvals, g, null2) for m, g in mods.items()}}
    report["Q2_tnf_response"] = q2

    with open(os.path.join(OUT, "perturbation_validation.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print("\nQ1  iBMEC - iPSC (module mean log2CPM difference)")
    for m, v in (q1.get("iBMEC_minus_iPSC") or {}).items():
        if v:
            print(f"  {m:16s} n={v['n_genes']:2d} delta={v['observed']:+7.3f} "
                  f"null={v['null_mean']:+7.3f} z={v['z']:+6.2f} p_hi={v['p_enriched']:.4f} "
                  f"p_lo={v['p_depleted']:.4f}")
    print("\nQ2  TNF-alpha response in hBMEC (module mean |log2FC|)")
    for m, v in (q2["absolute_log2FC"] or {}).items():
        if v:
            print(f"  {m:16s} n={v['n_genes']:2d} |lfc|={v['observed']:7.3f} "
                  f"null={v['null_mean']:7.3f} z={v['z']:+6.2f} p_hi={v['p_enriched']:.4f}")
    print("\nQ2  signed (up vs down)")
    for m, v in (q2["signed_log2FC"] or {}).items():
        if v:
            print(f"  {m:16s} n={v['n_genes']:2d} lfc={v['observed']:+7.3f} "
                  f"null={v['null_mean']:+7.3f} z={v['z']:+6.2f} p_hi={v['p_enriched']:.4f} "
                  f"p_lo={v['p_depleted']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
