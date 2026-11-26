"""
40_tables.py -- emit the manuscript tables and supplementary tables from out/.

Every number in the manuscript tables comes from a file in out/, so the tables cannot
drift from the analysis. Run after 21_cases.py and 30_model.py.
"""
from __future__ import annotations

import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
TAB = os.path.join(HERE, "manuscript", "tables")


def md(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = df.columns.tolist()
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append(floatfmt.format(v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    os.makedirs(TAB, exist_ok=True)
    cg = json.load(open(os.path.join(OUT, "case_groups.json"), encoding="utf-8"))
    MIN = cg["min_phenotype_reports_for_eligibility"]

    # ---------------- Table 1
    t = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    t["costim"] = t.costim.fillna("none")
    t = t.sort_values("R", ascending=False)
    cor = cg["co_reporting_by_product"]
    t1 = pd.DataFrame({
        "Product": t.short,
        "Modality": t.modality,
        "Costimulation": t.costim.replace({"none": "—"}),
        "Target": t.target,
        "Phenotype reports": t.n_pheno.astype(int),
        "ICANS": t.n_icans.astype(int),
        "CRS": t.n_crs.astype(int),
        "R": t.R,
        "95% CI": [f"{a:.3f}–{b:.3f}" for a, b in zip(t.R_lo, t.R_hi)],
        "Also CRS": [f"{cor[s]['frac_with_crs']:.3f}" if s in cor else "—"
                     for s in t.short],
    })
    (open(os.path.join(TAB, "table1_products.md"), "w", encoding="utf-8")
     .write("# Table 1. Partition of the two hallmark phenotypes by product\n\n"
            "Reports in which the product is the primary suspect, received 2019-01-01 or "
            "later, carrying either phenotype preferred term. R = ICANS/(ICANS + CRS); "
            "intervals are Wilson score intervals. \"Also CRS\" is the fraction of the "
            "product's ICANS reports that carry the CRS term as well. Products with "
            f"fewer than {MIN} phenotype reports are shown but are not analysed.\n\n"
            + md(t1)))

    # ---------------- Table 2
    spec = pd.read_csv(os.path.join(OUT, "specification_curve.csv"))
    spec = spec.rename(columns={
        "specification": "Specification", "diff": "Δ", "p_one_sided": "one-sided p",
        "p_two_sided": "two-sided p", "n_products": "products",
        "n_permutations": "permutations", "CD28_mean_R": "mean R, CD28",
        "41BB_mean_R": "mean R, 4-1BB"})
    (open(os.path.join(TAB, "table2_specifications.md"), "w", encoding="utf-8")
     .write("# Table 2. The CD28-versus-4-1BB contrast under nine analytic specifications\n\n"
            "Δ is the difference in mean R. Both p values are exact, obtained by "
            "enumerating every label permutation. The one-sided value is 1/21 in a "
            "two-versus-five design, reached only under complete separation. The two-sided "
            "value counts assignments at least as extreme in absolute value; because the "
            "two groups are unequal in size, the mirror of an assignment is not itself a "
            "permutation, so it is not twice the one-sided value and can fall to "
            "1/permutations — as it does in the two calendar-window rows.\n\n"
            + md(spec, "{:.3f}")))

    # ---------------- S1 substance normalisation
    raw = pd.read_csv(os.path.join(HERE, "config", "substances.csv"),
                      encoding="utf-8-sig")
    s1 = raw[raw.substance.str.contains("-")][["substance", "short", "modality"]]
    s1 = s1.rename(columns={"substance": "Variant as reported",
                            "short": "Merged to", "modality": "Modality"})
    (open(os.path.join(TAB, "s1_normalisation.md"), "w", encoding="utf-8")
     .write("# Supplementary Table S1. Suffix variants merged to a single substance key\n\n"
            "Four-character FDA suffix codes are stripped before counting, so that one "
            "biologic is not split across two rows with two denominators.\n\n" + md(s1)))

    # ---------------- S2 role sensitivity
    s2 = pd.DataFrame([
        {"Analysis": "primary suspect only", "Δ": cg["perm_CD28_vs_41BB"]["diff"],
         "one-sided p": cg["perm_CD28_vs_41BB"]["p_one_sided"]},
        {"Analysis": "any drug role", "Δ": cg["perm_CD28_vs_41BB_anyrole"]["diff"],
         "one-sided p": cg["perm_CD28_vs_41BB_anyrole"]["p_one_sided"]},
        {"Analysis": "monotherapy reports only",
         "Δ": cg["perm_CD28_vs_41BB_monotherapy"]["diff"],
         "one-sided p": cg["perm_CD28_vs_41BB_monotherapy"]["p_one_sided"]},
        {"Analysis": "single-phenotype reports only",
         "Δ": cg["isolated_phenotype"]["perm_CD28_vs_41BB"]["diff"],
         "one-sided p": cg["isolated_phenotype"]["perm_CD28_vs_41BB"]["p_one_sided"]},
    ])
    (open(os.path.join(TAB, "s2_role.md"), "w", encoding="utf-8")
     .write("# Supplementary Table S2. Exposure-role and report-set sensitivity\n\n"
            + md(s2)))

    # ---------------- S3 EBGM hyperparameters
    hp = json.load(open(os.path.join(OUT, "ebgm_hyperparameters.json"),
                        encoding="utf-8"))
    s3 = pd.DataFrame([{"Parameter": k, "Value": v} for k, v in hp.items()])
    (open(os.path.join(TAB, "s3_ebgm.md"), "w", encoding="utf-8")
     .write("# Supplementary Table S3. EBGM mixture hyperparameters\n\n"
            "Two-component gamma-Poisson shrinker fitted by EM on the cells of the "
            "present table. Reported as secondary evidence; the primary endpoint does "
            "not depend on these values.\n\n" + md(s3, "{:.4g}")))

    # ---------------- S5 module gene lists
    mods = pd.read_csv(os.path.join(HERE, "config", "engineered_modules.csv"),
                       encoding="utf-8-sig")
    lines = ["# Supplementary Table S5. Gene modules\n"]
    for m, g in mods.groupby("module"):
        lines.append(f"\n**{m}** (n = {len(g)}): " + ", ".join(sorted(g.gene)) + "\n")
    open(os.path.join(TAB, "s5_modules.md"), "w", encoding="utf-8").write("\n".join(lines))

    # ---------------- S6 network statistics
    rwr = json.load(open(os.path.join(OUT, "network_rwr.json"), encoding="utf-8"))
    rows = []
    for src, d in rwr["proximity"].items():
        for tgt, v in d.items():
            if not isinstance(v, dict) or "mass" not in v:
                continue
            rows.append({"From": src, "To": tgt.replace("to_", ""),
                         "RWR mass": v["mass"], "null mean": v["null_mean"],
                         "z": v["z"], "fold": v["fold"],
                         "p enriched": v["p_enriched"]})
    (open(os.path.join(TAB, "s6_network.md"), "w", encoding="utf-8")
     .write("# Supplementary Table S6. Random-walk-with-restart proximity, all pairs\n\n"
            "α = 0.7; each null is 2,000 degree-decile-matched random gene sets.\n\n"
            + md(pd.DataFrame(rows), "{:.4g}")))

    print("tables written:", sorted(os.listdir(TAB)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
