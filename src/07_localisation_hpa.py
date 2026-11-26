"""
07_localisation_hpa.py -- is the "neurovascular module" actually neurovascular?

This is the audit that decides whether the paper's two modules are two modules or
one word for 'inflammation'. It uses Human Protein Atlas single-nuclei brain data
(proteinatlas.tsv, one row per gene, brain cell-type nCPM for the top cell types),
which is a primary resource that nobody curated for this question.

Statistic, per gene:
    endo   = nCPM in 'Vascular endothelial cells'         (0 if not listed)
    myelo  = max nCPM in {'Microglia','Macrophages & Monocytes'}  (0 if not listed)
    score  = log2((endo+1)/(myelo+1))

Read the missingness honestly: HPA lists only the cell types in which a gene is
enriched, so a missing entry means 'not among the top cell types', not 'not
expressed'. Genes with no brain entry at all score 0 (neutral). Both conventions are
reported -- 'annotated_only' conditions on being cell-type-enriched and is therefore
the optimistic one.

The claim under test is an INTERACTION, not a level: the endothelial-over-myeloid
score should be higher for CNS_VASCULAR than for MYELOID_CYTOKINE. Either module
being 'expressed in brain' proves nothing; the contrast between them is the claim.
"""
from __future__ import annotations

import csv
import io
import json
import os
import random
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
NPERM = 10000
SEED = 20261116
ENDO = {"Vascular endothelial cells"}
MYELO = {"Microglia", "Macrophages & Monocytes"}


def load_hpa():
    z = zipfile.ZipFile(os.path.join(DATA, "hpa_proteinatlas_20261116.tsv.zip"))
    out = {}
    with z.open("proteinatlas.tsv") as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t")
        hdr = next(rd)
        ig = hdr.index("Gene")
        ib = hdr.index("RNA single nuclei brain specific nCPM")
        for row in rd:
            s = row[ib].strip()
            d = {}
            for part in s.split(";"):
                if ":" in part:
                    k, v = part.rsplit(":", 1)
                    try:
                        d[k.strip()] = float(v)
                    except ValueError:
                        pass
            out[row[ig]] = d
    return out


def score(d: dict) -> float | None:
    if not d:
        return 0.0
    endo = max((d.get(k, 0.0) for k in ENDO), default=0.0)
    myelo = max((d.get(k, 0.0) for k in MYELO), default=0.0)
    return float(np.log2((endo + 1.0) / (myelo + 1.0)))


def annotated(d: dict) -> bool:
    return bool(d)


class StratifiedNull:
    """Random gene sets matched on (has brain annotation, expression decile)."""

    def __init__(self, hpa: dict, seed=SEED):
        self.rng = random.Random(seed)
        genes = list(hpa)
        expr = np.array([max(hpa[g].values()) if hpa[g] else 0.0 for g in genes])
        ann = np.array([bool(hpa[g]) for g in genes])
        order = np.argsort(expr)
        self.strata: dict[tuple, list[str]] = {}
        rank = np.empty(len(genes), int)
        rank[order] = np.arange(len(genes))
        dec = (rank / len(genes) * 10).astype(int).clip(0, 9)
        for g, a, d in zip(genes, ann, dec):
            self.strata.setdefault((bool(a), int(d)), []).append(g)
        self.key = {g: (bool(a), int(d)) for g, a, d in zip(genes, ann, dec)}
        self.all = set(genes)

    def sample(self, obs):
        out, used = [], set()
        for g in obs:
            pool = self.strata.get(self.key[g]) or list(self.all)
            for _ in range(300):
                c = pool[self.rng.randrange(len(pool))]
                if c not in used:
                    break
            used.add(c)
            out.append(c)
        return out


def load_modules():
    mods: dict[str, list[str]] = {}
    for f in ["modules.csv", "engineered_modules.csv"]:
        with open(os.path.join(HERE, "config", f), encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                mods.setdefault(row["module"], set()).add(row["gene"].strip())
    return {k: sorted(v) for k, v in mods.items()}


def main() -> int:
    hpa = load_hpa()
    mods = load_modules()
    null = StratifiedNull(hpa)
    sc = {g: score(d) for g, d in hpa.items()}

    def stat(genes, annotated_only=False):
        g = [x for x in genes if x in sc and (annotated(hpa[x]) or not annotated_only)]
        if not g:
            return None, 0
        return float(np.mean([sc[x] for x in g])), len(g)

    report = {"n_hpa_genes": len(hpa),
              "n_genes_with_brain_annotation": int(sum(1 for d in hpa.values() if d)),
              "modules": {}}

    for m, genes in mods.items():
        # HPA's main table covers ~20k genes with protein evidence; a handful of module
        # genes (e.g. G6PC) are absent and cannot be scored. They are dropped and counted,
        # never silently imputed.
        missing = [g for g in genes if g not in hpa]
        genes = [g for g in genes if g in hpa]
        obs, k = stat(genes)
        obs_ao, k_ao = stat(genes, annotated_only=True)
        if obs is None:
            continue
        nulls = np.empty(NPERM)
        nulls_ao = np.empty(NPERM)
        for i in range(NPERM):
            s = null.sample(genes)
            vals = [sc[x] for x in s if x in sc]
            nulls[i] = np.mean(vals)
            va = [sc[x] for x in s if x in sc and annotated(hpa[x])]
            nulls_ao[i] = np.mean(va) if va else np.nan
        report["modules"][m] = {
            "n_genes": len(genes), "n_scored": k, "n_missing_from_hpa": len(missing),
            "missing": missing,
            "n_annotated": k_ao,
            "score_all": round(obs, 3),
            "score_annotated_only": round(obs_ao, 3) if obs_ao is not None else None,
            "null_mean_all": round(float(nulls.mean()), 3),
            "null_sd_all": round(float(nulls.std(ddof=1)), 3),
            "z_all": round(float((obs - nulls.mean()) / nulls.std(ddof=1)), 3),
            "p_high_all": float((nulls >= obs).mean()),
            "p_low_all": float((nulls <= obs).mean()),
            "null_mean_annotated": round(float(np.nanmean(nulls_ao)), 3),
            "z_annotated": round(float((obs_ao - np.nanmean(nulls_ao)) / np.nanstd(nulls_ao, ddof=1)), 3)
            if obs_ao is not None else None,
            "p_high_annotated": float((nulls_ao >= obs_ao).mean()) if obs_ao is not None else None,
        }

    # ---- the interaction claim: CNS_VASCULAR vs MYELOID_CYTOKINE
    a = [g for g in mods["CNS_VASCULAR"] if g in hpa]
    b = [g for g in mods["MYELOID_CYTOKINE"] if g in hpa]
    sa, _ = stat(a)
    sb, _ = stat(b)
    delta = sa - sb
    nulls_a = np.empty(NPERM)
    nulls_b = np.empty(NPERM)
    for i in range(NPERM):
        nulls_a[i] = np.mean([sc[x] for x in null.sample(a) if x in sc])
        nulls_b[i] = np.mean([sc[x] for x in null.sample(b) if x in sc])
    dnull = nulls_a - nulls_b
    report["interaction_CNS_minus_MYELOID"] = {
        "delta": round(float(delta), 3),
        "null_mean": round(float(dnull.mean()), 3),
        "null_sd": round(float(dnull.std(ddof=1)), 3),
        "z": round(float((delta - dnull.mean()) / dnull.std(ddof=1)), 3),
        "p_one_sided": float((dnull >= delta).mean()),
        "n_perm": NPERM,
    }

    # ---- per-gene audit table
    rows = []
    for m, genes in mods.items():
        for g in genes:
            d = hpa.get(g, {})
            rows.append({"module": m, "gene": g,
                         "endo_ncpm": d.get("Vascular endothelial cells", 0.0),
                         "microglia_ncpm": d.get("Microglia", 0.0),
                         "mono_macro_ncpm": d.get("Macrophages & Monocytes", 0.0),
                         "pericyte_ncpm": d.get("Pericytes", 0.0),
                         "score": round(sc.get(g, float("nan")), 3),
                         "annotated": bool(d),
                         "top_cell_types": ";".join(sorted(d))})
    with open(os.path.join(OUT, "localisation_per_gene.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(OUT, "localisation_hpa.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print(f"HPA genes {report['n_hpa_genes']}, with brain cell-type annotation "
          f"{report['n_genes_with_brain_annotation']}\n")
    print(f"{'module':16s} {'n':>3s} {'ann':>4s} {'score':>7s} {'null':>7s} {'z':>7s} {'p_high':>7s} {'p_low':>7s}")
    for m, v in report["modules"].items():
        print(f"{m:16s} {v['n_genes']:3d} {v['n_annotated']:4d} {v['score_all']:7.3f} "
              f"{v['null_mean_all']:7.3f} {v['z_all']:7.2f} {v['p_high_all']:7.4f} {v['p_low_all']:7.4f}")
    it = report["interaction_CNS_minus_MYELOID"]
    print(f"\ninteraction CNS - MYELOID = {it['delta']:+.3f}  z={it['z']:+.2f} "
          f"p={it['p_one_sided']:.4f}  (null {it['null_mean']:+.3f} +/- {it['null_sd']:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
