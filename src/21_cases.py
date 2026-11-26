"""
Case-level analysis of the ICANS / CRS partition in FAERS.

This replaces the aggregate-endpoint analysis as the primary analysis. It is the only
route that permits the three corrections the aggregate data cannot express:

  1. duplicate follow-ups removed (one record per `safetyreportid`, highest version kept);
  2. exposure restricted to primary-suspect drugs (`drugcharacterization == 1`);
  3. exact co-reporting structure and per-report drug composition.

Primary observable (needs no external denominator):

    R_p = n_ICANS(p) / (n_ICANS(p) + n_CRS(p))

i.e. among the reports in which product p is the primary suspect and that carry one of
the two hallmark phenotypes, what fraction is the neurovascular one. R is a ratio of two
margin counts within one class's own phenotype reports, so it is not driven by how widely a
product is prescribed -- unlike a report-share or a disproportionality estimate, both of which
carry the market denominator. Because a report carrying both phenotypes enters both margins,
R is a monotone re-expression of the ICANS:CRS report ratio and is NOT the share of patients
with ICANS; see Methods, "What R is arithmetically".

Outputs: out/case_products.csv, out/case_groups.json, out/case_temporal.csv,
         out/case_bias_examples.csv
"""
from __future__ import annotations

import csv
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
CASES = os.path.join(HERE, "data", "cases_icans_crs.jsonl")

ICANS = "Immune effector cell-associated neurotoxicity syndrome"
CRS = "Cytokine release syndrome"


def load_substances() -> pd.DataFrame:
    s = pd.read_csv(os.path.join(HERE, "config", "substances.csv"), encoding="utf-8-sig")
    s["substance"] = s["substance"].str.upper()
    return s


def load_cases() -> pd.DataFrame:
    recs = []
    with open(CASES, encoding="utf-8") as fh:
        for line in fh:
            recs.append(json.loads(line))
    df = pd.DataFrame(recs)
    df["ver_i"] = pd.to_numeric(df["ver"], errors="coerce").fillna(0).astype(int)
    # 1) deduplicate follow-ups: keep the highest version per case
    n_raw = len(df)
    df = (df.sort_values("ver_i")
            .drop_duplicates("sid", keep="last")
            .reset_index(drop=True))
    df.attrs["n_raw"] = n_raw
    df.attrs["n_dedup"] = len(df)
    return df


def flag(row_reacts: list[str]) -> tuple[bool, bool]:
    rs = set(row_reacts)
    return (ICANS in rs, CRS in rs)


def explode_products(df: pd.DataFrame, subs: pd.DataFrame,
                     role: str) -> pd.DataFrame:
    """One row per (report, product) with the product flagged as in-role.

    role='primary'  -> drugcharacterization == 1 for that drug entry
    role='any'      -> any entry, regardless of characterisation
    """
    canon = dict(zip(subs.substance, subs.substance))
    rows = []
    for sid, rdate, drugs, ic, cr in zip(df.sid, df.rdate, df.drugs,
                                        df.has_icans, df.has_crs):
        hit: dict[str, str] = {}
        for d in drugs:
            if role == "primary" and str(d.get("char")) != "1":
                continue
            for nm in d.get("names") or []:
                if nm in canon:
                    hit[nm] = str(d.get("char"))
        for nm, ch in hit.items():
            rows.append({"sid": sid, "rdate": rdate, "substance": nm,
                         "char": ch, "icans": ic, "crs": cr})
    return pd.DataFrame(rows)


def product_table(prod: pd.DataFrame, subs: pd.DataFrame,
                  restriction: str = "all") -> pd.DataFrame:
    if restriction == "mono":
        # count only reports where this product is the sole engager present
        n_prod = prod.groupby("sid").substance.nunique()
        mono = set(n_prod[n_prod == 1].index)
        prod = prod[prod.sid.isin(mono)]
    g = (prod.groupby("substance")
              .agg(n_icans=("icans", "sum"), n_crs=("crs", "sum"),
                   n_reports=("sid", "nunique"))
              .reset_index())
    g["n_pheno"] = g.n_icans + g.n_crs
    g["R"] = g.n_icans / g.n_pheno.replace(0, np.nan)
    # Wilson score interval: R is a proportion of the class's own phenotype reports, and
    # the intervals are what decide whether a product-level ordering is real or nominal.
    z = 1.959963985
    n, k = g.n_pheno.to_numpy(float), g.n_icans.to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        p_ = k / n
        den = 1 + z**2 / n
        ctr = (p_ + z**2 / (2 * n)) / den
        half = z * np.sqrt(p_ * (1 - p_) / n + z**2 / (4 * n**2)) / den
    g["R_lo"], g["R_hi"] = ctr - half, ctr + half
    g = g.merge(subs[["substance", "short", "group", "costim", "target", "modality"]],
                on="substance", how="left")
    return g.sort_values("R", ascending=False)


def exact_perm(x: np.ndarray, labels: np.ndarray) -> dict:
    """Exact enumeration of all label permutations (n is tiny; no sampling).

    With 2 CD28 and 5 4-1BB products the null has C(7,2)=21 points. The one-sided p
    can reach 1/21 = 0.048, and only under complete separation. The two-sided p is
    NOT twice the one-sided one: the permuted group must have the size of the CD28
    group, so the mirror of an assignment (five products against two) is not itself a
    permutation, and the two tails are asymmetric. Its floor is therefore 1/n, not
    2/n -- one of the calendar-window specifications in Table 2 reaches 1/15. Both p
    values and the one-sided floor are reported; what the 21-point null rules out is a
    two-sided claim with any margin, not a two-sided claim as such.
    """
    import itertools
    obs = x[labels == 1].mean() - x[labels == 0].mean()
    # the permuted group must have the SAME size as the observed label-1 group, so that
    # mean(m) - mean(~m) reproduces the observed statistic under the identity permutation
    n1 = int((labels == 1).sum())
    idx = np.arange(len(x))
    diffs = []
    for combo in itertools.combinations(idx, n1):
        m = np.zeros(len(x), dtype=bool)
        m[list(combo)] = True
        diffs.append(x[m].mean() - x[~m].mean())
    diffs = np.array(diffs)
    return {"diff": float(obs),
            "p_one_sided": float((diffs >= obs - 1e-12).mean()),
            "p_two_sided": float((np.abs(diffs) >= abs(obs) - 1e-12).mean()),
            "min_attainable_p_one_sided": float(1.0 / len(diffs)),
            "min_attainable_p_two_sided": float(1.0 / len(diffs)),
            "n_permutations": int(len(diffs)),
            "attains_one_sided_minimum": bool(
                (diffs >= obs - 1e-12).sum() == 1),
            "note": "the observed grouping is the maximum of the permutation "
                    "distribution in the pre-specified direction; because the two "
                    "groups are unequal in size the two-sided p is not twice the "
                    "one-sided one and its floor is 2/n_permutations only when the "
                    "group sizes are equal."}


def main() -> int:
    subs = load_substances()
    df = load_cases()
    # phenotype flags
    fl = [flag(r) for r in df.reacts]
    df["has_icans"] = [a for a, _ in fl]
    df["has_crs"] = [b for _, b in fl]

    dedup_n = df.attrs["n_dedup"]
    raw_n = df.attrs["n_raw"]

    # 2) analysis window: ICANS entered MedDRA in 2018, so 2019-01-01 is the honest start
    n_pre_window = int((pd.to_numeric(df.rdate, errors="coerce") < 20190101).sum())
    dfw = df[pd.to_numeric(df.rdate, errors="coerce") >= 20190101].copy()
    dfw["year"] = pd.to_numeric(dfw.rdate, errors="coerce") // 10000

    subs_eng = subs[subs.group.isin(["CAR-T", "BiTE"])]

    prod_p = explode_products(dfw, subs_eng, "primary")
    prod_a = explode_products(dfw, subs_eng, "any")

    t_primary = product_table(prod_p, subs_eng)
    t_any = product_table(prod_a, subs_eng)
    t_any.to_csv(os.path.join(OUT, "case_products_anyrole.csv"), index=False)

    # products with too few phenotype reports cannot estimate R
    MIN = 20
    elig = t_primary[t_primary.n_pheno >= MIN].copy()
    t_primary.to_csv(os.path.join(OUT, "case_products.csv"), index=False)

    res: dict = {
        "n_reports_raw": raw_n,
        "n_reports_after_dedup": dedup_n,
        "n_duplicates_removed": raw_n - dedup_n,
        "pct_duplicates_removed": round(100 * (raw_n - dedup_n) / raw_n, 2),
        "n_unique_safetyreportid": int(df.sid.nunique()),
        "dedup_note": "openFDA exposes one record per case (latest safetyreportversion); "
                      "version-level duplication is therefore absent by construction, and "
                      "the residual risk is the same patient reported under two different "
                      "safetyreportid values, which the public interface cannot detect.",
        "n_reports_before_2019": n_pre_window,
        "n_reports_in_window": int(len(dfw)),
        "min_phenotype_reports_for_eligibility": MIN,
        "n_products_eligible": int(len(elig)),
    }

    # group contrast on R
    groups = {"CD28": elig[elig.costim == "CD28"],
              "4-1BB": elig[elig.costim == "4-1BB"],
              "BiTE": elig[elig.costim == "none"]}
    res["group_R"] = {k: {"n_products": int(len(v)),
                          "mean": float(v.R.mean()),
                          "min": float(v.R.min()),
                          "max": float(v.R.max()),
                          "products": v.short.tolist()}
                      for k, v in groups.items()}

    cart = elig[elig.costim.isin(["CD28", "4-1BB"])]
    labels = (cart.costim == "CD28").astype(int).to_numpy()
    res["perm_CD28_vs_41BB"] = exact_perm(cart.R.to_numpy(dtype=float), labels)

    # any-role sensitivity, same products
    t_any_elig = t_any[t_any.n_pheno >= MIN]
    cart_a = t_any_elig[t_any_elig.costim.isin(["CD28", "4-1BB"])]
    res["perm_CD28_vs_41BB_anyrole"] = exact_perm(
        cart_a.R.to_numpy(dtype=float),
        (cart_a.costim == "CD28").astype(int).to_numpy())

    # monotherapy-only sensitivity
    t_mono = product_table(prod_p, subs_eng, restriction="mono")
    t_mono_elig = t_mono[t_mono.n_pheno >= MIN]
    cart_m = t_mono_elig[t_mono_elig.costim.isin(["CD28", "4-1BB"])]
    res["perm_CD28_vs_41BB_monotherapy"] = exact_perm(
        cart_m.R.to_numpy(dtype=float),
        (cart_m.costim == "CD28").astype(int).to_numpy())
    res["monotherapy_group_R"] = {
        k: float(t_mono_elig[t_mono_elig.costim == c].R.mean())
        for k, c in [("CD28", "CD28"), ("4-1BB", "4-1BB")]}

    # 2b) isolated-phenotype sensitivity. If the CD28/4-1BB contrast were an artefact of
    # co-reporting -- CD28 products simply attracting more dual-coded narratives -- then
    # restricting to reports that carry exactly one of the two PTs should attenuate it.
    dfi = dfw[dfw.has_icans ^ dfw.has_crs]
    prod_i = explode_products(dfi, subs_eng, "primary")
    t_iso = product_table(prod_i, subs_eng)
    t_iso.to_csv(os.path.join(OUT, "case_products_isolated.csv"), index=False)
    t_iso_elig = t_iso[t_iso.n_pheno >= MIN]
    cart_i = t_iso_elig[t_iso_elig.costim.isin(["CD28", "4-1BB"])]
    res["isolated_phenotype"] = {
        "n_reports": int(len(dfi)),
        "n_icans_only": int(dfi.has_icans.sum()),
        "n_crs_only": int(dfi.has_crs.sum()),
        "n_products_eligible": int(len(t_iso_elig)),
        "group_R": {k: (float(t_iso_elig[t_iso_elig.costim == c].R.mean())
                        if len(t_iso_elig[t_iso_elig.costim == c]) else None)
                    for k, c in [("CD28", "CD28"), ("4-1BB", "4-1BB"), ("BiTE", "none")]},
        "perm_CD28_vs_41BB": exact_perm(cart_i.R.to_numpy(dtype=float),
                                        (cart_i.costim == "CD28").astype(int).to_numpy()),
    }

    # 2c) within-product drift. If R rises inside every product's own observation window,
    # the calendar drift is a maturation of reporting rather than a change in biology, and
    # cross-product comparisons are only valid between products of similar market age.
    drift = {}
    for _, row in elig.iterrows():
        sub = prod_p[prod_p.substance == row.substance]
        d = pd.to_numeric(sub.rdate, errors="coerce").dropna()
        if len(d) < 40:
            continue
        mid = d.median()
        a = sub[pd.to_numeric(sub.rdate, errors="coerce") <= mid]
        b = sub[pd.to_numeric(sub.rdate, errors="coerce") > mid]
        if len(a) and len(b):
            Ra = a.icans.sum() / max(a.icans.sum() + a.crs.sum(), 1)
            Rb = b.icans.sum() / max(b.icans.sum() + b.crs.sum(), 1)
            drift[row.short] = {"R_first_half": round(float(Ra), 4),
                                "R_second_half": round(float(Rb), 4),
                                "delta": round(float(Rb - Ra), 4),
                                "midpoint": str(int(mid))}
    res["within_product_drift"] = {
        "n_products": len(drift),
        "n_rising": int(sum(v["delta"] > 0 for v in drift.values())),
        "median_delta": float(np.median([v["delta"] for v in drift.values()]))
                        if drift else None,
        "detail": drift,
    }

    # 2d) year-stratified contrast: does CD28 exceed 4-1BB in every calendar year in
    # which both classes have a product with enough reports? This controls for era, and
    # era is the most obvious alternative explanation for a product-level ordering.
    strat = []
    for y in sorted(dfw.year.dropna().unique()):
        sub = dfw[dfw.year == y]
        pr = explode_products(sub, subs_eng, "primary")
        tb = product_table(pr, subs_eng)
        tb = tb[tb.n_pheno >= 30]
        cd = tb[tb.costim == "CD28"].R
        fb = tb[tb.costim == "4-1BB"].R
        if len(cd) and len(fb):
            strat.append({"year": int(y), "n_cd28": int(len(cd)),
                          "n_41bb": int(len(fb)),
                          "CD28": float(cd.mean()), "41BB": float(fb.mean()),
                          "delta": float(cd.mean() - fb.mean())})
    res["year_stratified"] = {
        "n_years": len(strat),
        "n_years_delta_positive": int(sum(s["delta"] > 0 for s in strat)),
        "detail": strat,
    }

    # 3) temporal hold-out: does R stay put while volumes move?
    dfw["year"] = pd.to_numeric(dfw.rdate, errors="coerce") // 10000
    rows = []
    # The primary temporal split starts in 2021, not 2019. ICANS entered MedDRA in 2018
    # and was adopted by reporters over the following two years; 2019 carries only 25
    # ICANS reports in the whole class, so including it measures the term's introduction
    # rather than the biology. The wider split is retained as a sensitivity analysis so
    # that the transient is visible instead of hidden.
    for period, lo, hi in [("2021-2023", 2021, 2023), ("2024-2026", 2024, 2026),
                           ("2019-2022", 2019, 2022), ("2023-2026", 2023, 2026)]:
        sub = dfw[(dfw.year >= lo) & (dfw.year <= hi)]
        pr = explode_products(sub, subs_eng, "primary")
        tb = product_table(pr, subs_eng)
        tb["period"] = period
        rows.append(tb)
    temp = pd.concat(rows)
    temp.to_csv(os.path.join(OUT, "case_temporal.csv"), index=False)
    res["temporal"] = {}
    for short in elig.short:
        a = temp[(temp.short == short) & (temp.period == "2021-2023")]
        b = temp[(temp.short == short) & (temp.period == "2024-2026")]
        if len(a) and len(b) and a.n_pheno.iloc[0] >= 10 and b.n_pheno.iloc[0] >= 10:
            res["temporal"][short] = {
                "R_early": float(a.R.iloc[0]), "R_late": float(b.R.iloc[0]),
                "n_early": int(a.n_pheno.iloc[0]), "n_late": int(b.n_pheno.iloc[0])}
    # rank agreement across periods
    from scipy.stats import spearmanr
    common = [s for s in res["temporal"]]
    if len(common) >= 5:
        rho, p = spearmanr([res["temporal"][s]["R_early"] for s in common],
                           [res["temporal"][s]["R_late"] for s in common])
        res["temporal_rank"] = {"spearman_rho": float(rho), "p": float(p),
                                "n_products": len(common),
                                "products": common}
    # group means by period
    res["temporal_group_R"] = {}
    for period in ["2021-2023", "2024-2026", "2019-2022", "2023-2026"]:
        tp = temp[temp.period == period]
        tp = tp[tp.n_pheno >= MIN]
        res["temporal_group_R"][period] = {
            k: (float(tp[tp.costim == c].R.mean()) if len(tp[tp.costim == c]) else None)
            for k, c in [("CD28", "CD28"), ("4-1BB", "4-1BB"), ("BiTE", "none")]}

    # Weber effect: annual volume and annual R for the class
    yr = []
    for y in sorted(dfw.year.dropna().unique()):
        sub = dfw[dfw.year == y]
        pr = explode_products(sub, subs_eng, "primary")
        n_ic = int(pr[pr.icans].sid.nunique()) if len(pr) else 0
        n_cr = int(pr[pr.crs].sid.nunique()) if len(pr) else 0
        yr.append({"year": int(y), "n_icans": n_ic, "n_crs": n_cr,
                   "R": n_ic / (n_ic + n_cr) if (n_ic + n_cr) else None})
    pd.DataFrame(yr).to_csv(os.path.join(OUT, "case_by_year.csv"), index=False)

    # 4) bias examples: what sits inside the ICANS reports
    icans_rows = dfw[dfw.has_icans]
    cnt: dict[str, int] = defaultdict(int)
    role_split: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for drugs in icans_rows.drugs:
        seen = set()
        for d in drugs:
            for nm in d.get("names") or []:
                if nm in seen:
                    continue
                seen.add(nm)
                cnt[nm] += 1
                role_split[nm][str(d.get("char"))] += 1
    top = sorted(cnt.items(), key=lambda kv: -kv[1])[:25]
    bias = pd.DataFrame([{"substance": k, "n_icans_reports": v,
                          "n_primary": role_split[k].get("1", 0),
                          "n_concomitant": role_split[k].get("2", 0)}
                         for k, v in top])
    bias.to_csv(os.path.join(OUT, "case_bias_examples.csv"), index=False)

    # co-reporting: does ICANS travel with CRS?
    n_ic = int(dfw.has_icans.sum())
    both = int((dfw.has_icans & dfw.has_crs).sum())
    res["co_reporting"] = {"n_icans_reports": n_ic, "n_with_crs_also": both,
                           "fraction_with_crs": round(both / n_ic, 4)}
    # per product
    res["co_reporting_by_product"] = {}
    for short in elig.short:
        s_ = elig.loc[elig.short == short, "substance"].iloc[0]
        sub = prod_p[(prod_p.substance == s_) & prod_p.icans]
        if len(sub):
            res["co_reporting_by_product"][short] = {
                "n_icans": int(len(sub)),
                "frac_with_crs": round(float(sub.crs.mean()), 4)}

    # 5) the one quantitative prediction a future launch can settle
    cd = elig[elig.costim == "CD28"]
    fb = elig[elig.costim == "4-1BB"]
    res["model_prediction"] = {
        "statement": "a future CD28-costimulated product should show R within the "
                     "union of the current CD28 Wilson intervals; a value at or below "
                     "the highest observed 4-1BB point estimate refutes the "
                     "construct-level account",
        "new_cd28_window": [round(float(cd.R_lo.min()), 3),
                            round(float(cd.R_hi.max()), 3)],
        "refutation_threshold": round(float(fb.R.max()), 3),
        "cd28_point_estimates": [round(float(v), 3) for v in cd.R],
        "four_1bb_range": [round(float(fb.R.min()), 3), round(float(fb.R.max()), 3)],
        "bite_range": [round(float(elig[elig.costim == "none"].R.min()), 3),
                       round(float(elig[elig.costim == "none"].R.max()), 3)],
    }

    with open(os.path.join(OUT, "case_groups.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(json.dumps(res, indent=2, ensure_ascii=False)[:6000])
    print()
    print(t_primary[["short", "modality", "costim", "n_pheno", "n_icans", "n_crs", "R"]]
          .to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
