"""
22_specifications.py -- multiverse of the CD28-vs-4-1BB contrast.

A single p value hides every analytical choice behind it. This script recomputes the
same contrast under every defensible variant of the pipeline and writes the resulting
distribution, so that the reader can see whether the conclusion is a property of the
data or of one particular decision.

Variants: exposure role (primary suspect / any role), report set (all / monotherapy /
single-phenotype), eligibility threshold (20 / 50 phenotype reports), calendar window
(full / 2019-2022 / 2023-2026 / pre-2019 included), and one metric substitution
(EBGM ratio from the aggregate pipeline).

Output: out/specification_curve.csv
"""
from __future__ import annotations

import importlib.util
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")


def load_module():
    spec = importlib.util.spec_from_file_location(
        "case_analysis", os.path.join(HERE, "src", "21_cases.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def contrast(mod, df, subs_eng, role="primary", report_set="all",
             min_reports=20, drop=(), year_range=None) -> dict:
    d = df
    if year_range is not None:
        yr = pd.to_numeric(d.rdate, errors="coerce") // 10000
        d = d[(yr >= year_range[0]) & (yr <= year_range[1])]
    if report_set == "monotherapy":
        prod = mod.explode_products(d, subs_eng, role)
        mono = prod.groupby("sid").substance.nunique()
        prod = prod[prod.sid.isin(mono[mono == 1].index)]
        t = mod.product_table(prod, subs_eng, restriction="all")
    elif report_set == "single_phenotype":
        d = d[d.has_icans ^ d.has_crs]
        prod = mod.explode_products(d, subs_eng, role)
        t = mod.product_table(prod, subs_eng)
    else:
        prod = mod.explode_products(d, subs_eng, role)
        t = mod.product_table(prod, subs_eng)
    t = t[t.n_pheno >= min_reports]
    if drop:
        t = t[~t.short.isin(drop)]
    cart = t[t.costim.isin(["CD28", "4-1BB"])]
    if (cart.costim == "CD28").sum() < 2 or (cart.costim == "4-1BB").sum() < 2:
        return {"diff": np.nan, "p_one_sided": np.nan, "n_products": int(len(cart))}
    r = mod.exact_perm(cart.R.to_numpy(dtype=float),
                       (cart.costim == "CD28").astype(int).to_numpy())
    r["n_products"] = int(len(cart))
    r["CD28"] = float(cart.loc[cart.costim == "CD28", "R"].mean())
    r["4-1BB"] = float(cart.loc[cart.costim == "4-1BB", "R"].mean())
    return r


def main() -> int:
    mod = load_module()
    subs = mod.load_substances()
    subs_eng = subs[subs.group.isin(["CAR-T", "BiTE"])]
    df = mod.load_cases()
    fl = [mod.flag(r) for r in df.reacts]
    df["has_icans"] = [a for a, _ in fl]
    df["has_crs"] = [b for _, b in fl]
    dfw = df[pd.to_numeric(df.rdate, errors="coerce") >= 20190101].copy()

    specs = [
        ("primary (pre-specified)", dict()),
        ("any-role exposure", dict(role="any")),
        ("monotherapy only", dict(report_set="monotherapy")),
        ("single-phenotype reports", dict(report_set="single_phenotype")),
        ("exclude obe-cel (n=25)", dict(drop=("obe-cel",))),
        ("threshold 50 reports", dict(min_reports=50)),
        ("2019-2022 only", dict(year_range=(2019, 2022))),
        ("2023-2026 only", dict(year_range=(2023, 2026))),
    ]
    rows = []
    for name, kw in specs:
        r = contrast(mod, dfw, subs_eng, **kw)
        rows.append({"specification": name, "diff": r.get("diff"),
                     "p_one_sided": r.get("p_one_sided"),
                     "p_two_sided": r.get("p_two_sided"),
                     "n_products": r.get("n_products"),
                     "n_permutations": r.get("n_permutations"),
                     "CD28_mean_R": r.get("CD28"), "41BB_mean_R": r.get("4-1BB")})

    # include pre-2019 reports (all received dates)
    fl2 = df
    r = contrast(mod, fl2, subs_eng, year_range=None)
    rows.append({"specification": "including pre-2019 reports",
                 "diff": r.get("diff"), "p_one_sided": r.get("p_one_sided"),
                 "p_two_sided": r.get("p_two_sided"), "n_products": r.get("n_products"),
                 "n_permutations": r.get("n_permutations"),
                 "CD28_mean_R": r.get("CD28"), "41BB_mean_R": r.get("4-1BB")})

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "specification_curve.csv"), index=False)
    print(out.round(3).to_string(index=False))
    print("\ndirection preserved in",
          int((out["diff"] > 0).sum()), "/", len(out), "specifications")
    print("one-sided p < 0.05 in",
          int((out["p_one_sided"] < 0.05).sum()), "/", len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
