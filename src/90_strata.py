"""Country and reporter-type stratification of the costimulation contrast.

The manuscript previously listed country and reporter qualification as things the design
"cannot separate". Both fields are in the deposited extract, so that claim was checkable
and wrong. This script tests the contrast inside each stratum.

Two questions are asked separately, because they can disagree:
  1. is the direction preserved (mean CD28 > mean 4-1BB)?
  2. is the perfect product-level separation preserved (min CD28 > max 4-1BB)?
The second is what the exact permutation test actually measures: with two CD28 products
the attainable one-sided p is 1/C(n,2), and it is attained only under complete separation.

Reconciliation is enforced: the ALL stratum must reproduce the published 0.3611 / 0.2745 /
0.0866 / 0.0476, or the script refuses to write.
"""
from __future__ import annotations

import json
import os
from itertools import combinations

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICANS = "Immune effector cell-associated neurotoxicity syndrome"
CRS = "Cytokine release syndrome"
MIN = 20

EUROPE = {"EU", "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
          "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI",
          "ES", "SE", "NO", "IS", "CH", "GB", "UK"}


def load():
    subs = pd.read_csv(os.path.join(HERE, "config", "substances.csv"), encoding="utf-8-sig")
    subs["substance"] = subs["substance"].str.upper()
    subs = subs[subs.group.isin(["CAR-T", "BiTE"])].copy()
    recs = [json.loads(l) for l in
            open(os.path.join(HERE, "data", "cases_icans_crs.jsonl"), encoding="utf-8")
            if l.strip()]
    df = pd.DataFrame(recs)
    df["ver_i"] = pd.to_numeric(df["ver"], errors="coerce").fillna(0).astype(int)
    df = (df.sort_values("ver_i").drop_duplicates("sid", keep="last")
            .reset_index(drop=True))
    df = df[pd.to_numeric(df.rdate, errors="coerce") >= 20190101].reset_index(drop=True)
    df["icans"] = df.reacts.apply(lambda r: ICANS in set(r))
    df["crs"] = df.reacts.apply(lambda r: CRS in set(r))
    return df, subs


def explode(df, subs):
    canon = set(subs.substance)
    rows = []
    for sid, country, qual, drugs, ic, cr in zip(df.sid, df.country, df.qual,
                                                 df.drugs, df.icans, df.crs):
        hit = set()
        for d in drugs:
            if str(d.get("char")) != "1":
                continue
            for nm in d.get("names") or []:
                if nm in canon:
                    hit.add(nm)
        for nm in hit:
            rows.append({"sid": sid, "country": country, "qual": qual,
                         "substance": nm, "icans": ic, "crs": cr})
    return pd.DataFrame(rows)


def product_table(prod, subs):
    g = (prod.groupby("substance")
              .agg(n_icans=("icans", "sum"), n_crs=("crs", "sum"))
              .reset_index())
    g["n_pheno"] = g.n_icans + g.n_crs
    g["R"] = g.n_icans / g.n_pheno.replace(0, np.nan)
    return g.merge(subs[["substance", "short", "costim"]], on="substance", how="left")


def exact_perm(cd, fb):
    """Exact one-sided and two-sided p over all label assignments."""
    obs = float(np.mean(cd) - np.mean(fb))
    pool = np.concatenate([cd, fb])
    k = len(cd)
    ge_one, ge_abs, total = 0, 0, 0
    for idx in combinations(range(len(pool)), k):
        mask = np.zeros(len(pool), bool)
        mask[list(idx)] = True
        d = float(np.mean(pool[mask]) - np.mean(pool[~mask]))
        total += 1
        if d >= obs - 1e-12:
            ge_one += 1
        if abs(d) >= abs(obs) - 1e-12:
            ge_abs += 1
    return {"diff": obs, "p_one_sided": ge_one / total,
            "p_two_sided": ge_abs / total, "n_assignments": total}


def spearman(a, b):
    def rank(x):
        x = np.asarray(x, float)
        order = x.argsort()
        r = np.empty(len(x), float)
        r[order] = np.arange(len(x), dtype=float)
        # average ties
        vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
        for i, c in enumerate(cnt):
            if c > 1:
                r[inv == i] = r[inv == i].mean()
        return r
    ra, rb = rank(a), rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def strata(prod):
    us = prod.country == "US"
    eu = prod.country.isin(EUROPE)
    jp = prod.country == "JP"
    return [
        ("All reports", prod, ""),
        ("United States", prod[us], ""),
        ("Europe", prod[eu], "EU aggregate code plus European country codes"),
        ("Japan", prod[jp], ""),
        ("Non-US", prod[~us], ""),
        ("Physician", prod[prod.qual.astype(str) == "1"], "primary-source qualification 1"),
        ("Other health professional", prod[prod.qual.astype(str) == "3"], "qualification 3"),
        ("Consumer", prod[prod.qual.astype(str) == "5"], "qualification 5"),
        ("US, physician only", prod[us & (prod.qual.astype(str) == "1")], ""),
    ]


def main() -> int:
    df, subs = load()
    prod = explode(df, subs)
    ref_tbl = product_table(prod, subs)
    ref_R = dict(zip(ref_tbl.substance, ref_tbl.R))

    published = json.load(open(os.path.join(HERE, "out", "case_groups.json"), encoding="utf-8"))
    pub_cd = published["group_R"]["CD28"]["mean"]
    pub_fb = published["group_R"]["4-1BB"]["mean"]
    pub_p = published["perm_CD28_vs_41BB"]["p_one_sided"]

    rows, detail = [], {}
    for name, sub, note in strata(prod):
        t = product_table(sub, subs)
        elig = t[t.n_pheno >= MIN]
        cd = elig[elig.costim == "CD28"].sort_values("short")
        fb = elig[elig.costim == "4-1BB"].sort_values("short")
        rec = {"stratum": name, "note": note,
               "n_reports": int(sub.sid.nunique()),
               "n_products_eligible": int(len(elig)),
               "n_CD28": int(len(cd)), "n_4_1BB": int(len(fb)),
               "mean_CD28": float(cd.R.mean()) if len(cd) else None,
               "mean_4_1BB": float(fb.R.mean()) if len(fb) else None,
               "products": list(elig.short)}
        if len(cd) >= 2 and len(fb) >= 2:
            rec.update(exact_perm(cd.R.to_numpy(), fb.R.to_numpy()))
            rec["separates"] = bool(cd.R.min() > fb.R.max())
            rec["min_CD28"] = float(cd.R.min())
            rec["max_4_1BB"] = float(fb.R.max())
            common = [s for s in elig.substance if s in ref_R]
            rec["rho_vs_all"] = spearman(
                [float(elig[elig.substance == s].R.iloc[0]) for s in common],
                [ref_R[s] for s in common]) if len(common) >= 3 else None
            rec["n_common"] = len(common)
        else:
            rec.update({"diff": None, "p_one_sided": None, "p_two_sided": None,
                        "n_assignments": None, "separates": None,
                        "min_CD28": None, "max_4_1BB": None,
                        "rho_vs_all": None, "n_common": 0})
            if len(cd) < 2:
                rec["why_untestable"] = (f"only {len(cd)} CD28 product(s) reach "
                                         f"{MIN} phenotype reports")
            else:
                rec["why_untestable"] = (f"only {len(fb)} 4-1BB product(s) reach "
                                         f"{MIN} phenotype reports")
        rows.append(rec)
        detail[name] = {r.short: (round(float(r.R), 4), int(r.n_pheno))
                        for _, r in elig.iterrows()}

    allrow = rows[0]
    ok = (abs(allrow["mean_CD28"] - pub_cd) < 1e-9
          and abs(allrow["mean_4_1BB"] - pub_fb) < 1e-9
          and abs(allrow["p_one_sided"] - pub_p) < 1e-9)
    print(f"reconcile: CD28 {allrow['mean_CD28']:.6f} vs {pub_cd:.6f} | "
          f"4-1BB {allrow['mean_4_1BB']:.6f} vs {pub_fb:.6f} | "
          f"p {allrow['p_one_sided']:.6f} vs {pub_p:.6f} -> {'OK' if ok else 'MISMATCH'}")
    if not ok:
        return 3

    n_pos = sum(1 for r in rows if r["diff"] is not None and r["diff"] > 0)
    n_tested = sum(1 for r in rows if r["diff"] is not None)
    n_sep = sum(1 for r in rows if r["separates"])
    out = {"min_reports": MIN, "europe_codes": sorted(EUROPE),
           "n_strata": len(rows), "n_tested": n_tested,
           "n_positive_direction": n_pos, "n_separating": n_sep,
           "rows": rows}

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "out", "strata.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)

    # ---- supplementary table S10 ----
    L = ["# Supplementary table S10. The costimulation contrast inside reporting strata",
         "",
         "Same endpoint, same eligibility rule (>= 20 phenotype reports) and same exact "
         "permutation test as Table 1 and Figure 1, recomputed on subsets of the FAERS "
         "extract defined by reporting country and by reporter qualification. "
         "*Separation* means the lowest CD28 product exceeds the highest 4-1BB product; "
         "the one-sided p can only reach its floor 1/C(n,2) when separation holds, so the "
         "two columns carry the same information and are both shown. "
         "rho is the Spearman correlation of product-level R against the all-report value, "
         "over the products eligible in that stratum.",
         "",
         "| Stratum | Reports | Products | n CD28 | n 4-1BB | Mean R CD28 | Mean R 4-1BB | "
         "Δ | One-sided p | Separation | ρ vs all |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["diff"] is None:
            d = p1 = sep = rho = "not testable"
            cd_m = f"{r['mean_CD28']:.3f}" if r["mean_CD28"] is not None else "—"
            fb_m = f"{r['mean_4_1BB']:.3f}" if r["mean_4_1BB"] is not None else "—"
        else:
            d = f"{r['diff']:+.3f}"
            p1 = f"{r['p_one_sided']:.3f}"
            sep = "yes" if r["separates"] else "no"
            rho = f"{r['rho_vs_all']:.3f}" if r["rho_vs_all"] is not None else "—"
            cd_m, fb_m = f"{r['mean_CD28']:.3f}", f"{r['mean_4_1BB']:.3f}"
        L.append(f"| {r['stratum']} | {r['n_reports']:,} | {r['n_products_eligible']} | "
                 f"{r['n_CD28']} | {r['n_4_1BB']} | {cd_m} | {fb_m} | {d} | {p1} | "
                 f"{sep} | {rho} |")
    L += ["",
          f"Direction is positive in {n_pos} of the {n_tested} testable strata; perfect "
          f"separation survives in {n_sep}. Japan is not testable because only one CD28 "
          "product reaches the eligibility threshold there. Strata are nested rather than "
          "independent (the United States is a subset of all reports, non-US its "
          "complement), so these p values are not a testing family and no multiplicity "
          "adjustment is applied to them.",
          ""]
    open(os.path.join(HERE, "manuscript", "tables", "s10_strata.md"), "w",
         encoding="utf-8").write("\n".join(L))

    print(f"strata={len(rows)} testable={n_tested} positive={n_pos} separating={n_sep}")
    for r in rows:
        print(f"  {r['stratum']:<26} rep={r['n_reports']:>6} prod={r['n_products_eligible']:>3} "
              f"d={r['diff'] if r['diff'] is None else round(r['diff'],3)} "
              f"p={r['p_one_sided'] if r['p_one_sided'] is None else round(r['p_one_sided'],3)} "
              f"sep={r['separates']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
