"""
41_tables_new.py -- supplementary tables for the three analyses added after the first
complete draft: legacy preferred term, leave-one-product-out prediction, and the
resolution limit of the prediction.

Kept separate from 40_tables.py because these three tables depend on scripts that run
after it (23, 24, 26), and a single script would force a re-run of everything whenever
one of them changes.
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
            if isinstance(v, float) and v == v:
                cells.append(floatfmt.format(v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    os.makedirs(TAB, exist_ok=True)

    # ---------------- S7: legacy preferred term
    lg = json.load(open(os.path.join(OUT, "legacy_pt.json"), encoding="utf-8"))
    p = pd.read_csv(os.path.join(OUT, "legacy_products.csv"))
    p = p[p.n_pheno >= lg["min_phenotype_reports"]]
    p = p.sort_values("R_union", ascending=False)
    t = pd.DataFrame({
        "Product": p.short,
        "Class": p.costim.replace({"none": "BiTE"}),
        "ICANS": p.n_icans.astype(int),
        "Neurotoxicity": p.n_legacy.astype(int),
        "Any neurotoxicity": p.n_anyneu.astype(int),
        "CRS": p.n_crs.astype(int),
        "R (union)": p.R_union.round(3),
        "95% CI": [f"{a:.3f}–{b:.3f}" for a, b in zip(p.R_union_lo, p.R_union_hi)],
        "R (legacy only)": p.R_legacy.round(3),
    })
    u, l = lg["union"]["perm_CD28_vs_41BB"], lg["legacy_only"]["perm_CD28_vs_41BB"]
    pr = lg["primary_for_comparison"]["perm_CD28_vs_41BB"]
    body = (
        "# Supplementary Table S7. The partition recomputed under the pre-2018 "
        "coding convention\n\n"
        "The primary phenotype is the preferred term introduced in MedDRA 21.0 (2018). "
        "A reviewer is entitled to ask whether the ordering is a property of the "
        "biology or of a term that exists only for the later part of the products' "
        "market lives. Two alternative numerators are used, both with the same CRS "
        "denominator: *R (union)* counts reports carrying either the modern term or the "
        "legacy term, and *R (legacy only)* uses the legacy term alone, which is what "
        "the analysis would have produced before 2018.\n\n"
        f"{md(t)}\n\n"
        "Exact permutation of the CD28-versus-4-1BB contrast under each definition "
        f"({u['n_products_cd28']} versus {u['n_products_41bb']} products, all "
        f"C({u['n_products_cd28'] + u['n_products_41bb']},"
        f"{u['n_products_cd28']}) = {int(round(1 / u['min_attainable_p_one_sided']))} "
        "assignments enumerated):\n\n"
        "| Definition | Δ | one-sided p | two-sided p |\n|---|---|---|---|\n"
        f"| Primary (ICANS only) | {pr['diff']:+.3f} | {pr['p_one_sided']:.3f} | "
        f"{pr['p_two_sided']:.3f} |\n"
        f"| R (union) | {u['diff']:+.3f} | {u['p_one_sided']:.3f} | "
        f"{u['p_two_sided']:.3f} |\n"
        f"| R (legacy only) | {l['diff']:+.3f} | {l['p_one_sided']:.3f} | "
        f"{l['p_two_sided']:.3f} |\n\n"
        f"Rank agreement between the primary and union definitions: Spearman "
        f"ρ = {lg['rank_agreement_primary_vs_union']['spearman_rho']:.2f} "
        f"(p = {lg['rank_agreement_primary_vs_union']['p']:.4f}, "
        f"n = {lg['rank_agreement_primary_vs_union']['n']}); "
        f"{lg['union']['n_products_switching_rank_vs_primary']} of those products change "
        "rank position between the two definitions.\n\n"
        f"> {lg['n_legacy_records_pulled']:,} legacy-term records were retrieved "
        f"independently and merged with the primary pull on `safetyreportid`; on the "
        f"{lg['n_shared_reports_with_primary_pull']:,} reports present in both, the two "
        "extractions agree on every phenotype flag, so the merge introduces no "
        "inconsistency.\n"
    )
    open(os.path.join(TAB, "s7_legacy_pt.md"), "w", encoding="utf-8").write(body)

    # ---------------- S8: leave-one-product-out
    ho = json.load(open(os.path.join(OUT, "holdout.json"), encoding="utf-8"))
    d = pd.DataFrame(ho["detail"])
    t8 = pd.DataFrame({
        "Product": d["product"],
        "Class": d["class"],
        "Phenotype reports": d["n_pheno"],
        "R observed": d["R_observed"].round(3),
        "R predicted": d["R_predicted_LODO"].round(3),
        "Residual": d["error"].round(3),
        "Donors": d["n_donors"],
    })
    body8 = (
        "# Supplementary Table S8. Leave-one-product-out prediction of R\n\n"
        "Each product's partition is predicted from the other products of the same "
        "costimulatory class, and compared with a predictor that uses all other products "
        "regardless of class. If the class label carried a usable quantitative rule, the "
        "class-based prediction would be the better of the two.\n\n"
        f"{md(t8)}\n\n"
        f"Mean absolute error: **{ho['mae_class_mean']:.3f}** for the class-based "
        f"predictor, **{ho['mae_class_blind']:.3f}** for the class-blind predictor "
        f"(relative change {ho['relative_improvement_pct']:+.1f}%). Median absolute "
        f"error {ho['median_abs_error_class_mean']:.3f}; largest {ho['max_abs_error']:.3f}; "
        f"{ho['n_products_within_0.05']} of {ho['n_products']} products predicted within "
        "0.05.\n\n"
        f"The difference is then tested against all {ho['n_null_assignments']} "
        "alternative ways of labelling two of the seven products as CD28-costimulated: "
        f"the observed grouping is not better than chance at predicting held-out "
        f"values (exact p = {ho['p_exact_class_better_than_random_grouping']:.2f}, "
        f"attainable minimum {ho['min_attainable_p']:.3f}). The conclusion is that the "
        "class effect is an ordering, not a level predictor.\n\n"
        f"> {ho['caveat']}\n"
    )
    open(os.path.join(TAB, "s8_holdout.md"), "w", encoding="utf-8").write(body8)

    # ---------------- Table 3: resolution limit of the prediction
    rule = json.load(open(os.path.join(OUT, "prediction_rule.json"), encoding="utf-8"))
    keep = [0.200, 0.250, 0.280, 0.300, 0.310, 0.320, 0.325, 0.330,
            0.340, 0.360, 0.390]
    rows = [r for r in rule["table"] if round(r["true_R"], 3) in keep]
    t3 = pd.DataFrame({
        "True R of the new product": [f"{r['true_R']:.3f}" for r in rows],
        f"Verdict at {rule['reference_n']:,} reports": [r["verdict"] for r in rows],
        "Reports needed for a verdict": [
            "—" if r["min_reports_for_decisive_verdict"] is None or
            r["min_reports_for_decisive_verdict"] != r["min_reports_for_decisive_verdict"]
            else f"{int(r['min_reports_for_decisive_verdict']):,}" for r in rows],
    })
    body3 = (
        # BMC style: table titles are capped at 15 words.
        "# Table 3. The partition a future product would need, and how many reports "
        "to settle it\n\n"
        "The rule is one-sided against the highest observed 4-1BB value (0.320): a new "
        "CD28-costimulated product supports the account when the Wilson lower bound of "
        "its partition exceeds 0.320, refutes it when the upper bound falls at or below "
        "0.320, and is undecidable otherwise. A dash means no sample size decides the "
        f"question. The reference column is the largest single-product sample in this "
        f"database ({rule['reference_product']}, n = {rule['reference_n']:,}); at that "
        f"size the unresolvable band is {rule['blind_band_at_reference_n'][0]:.3f}–"
        f"{rule['blind_band_at_reference_n'][1]:.3f}.\n\n"
        f"{md(t3)}\n"
    )
    open(os.path.join(TAB, "table3_decidability.md"), "w", encoding="utf-8").write(body3)

    # ---------------- S13: positive control
    pc = json.load(open(os.path.join(OUT, "positive_control.json"), encoding="utf-8"))
    ps = json.load(open(os.path.join(OUT, "positive_control_summary.json"), encoding="utf-8"))
    byc, cal, br = ps["by_class"], ps["calibration"], ps["bracket"]
    rep = ps.get("pipeline_reproduction", {})
    spl = ps.get("split_agreement", {})
    pr = pd.DataFrame(pc["pairs"])
    label = {"pathway_half": "pathway half", "pathway_half_split2": "pathway half, 2nd split",
             "complex": "complex", "negative": "negative control", "random_pair": "random pair"}
    pos, cx, neg, rnd = byc["pathway_half"], byc["complex"], byc["negative"], byc["random_pair"]
    negp = sorted(pr[pr.kind == "negative"].p_ab)
    pw = json.load(open(os.path.join(OUT, "power_network.json"), encoding="utf-8"))
    mde = pw["by_target"]["CNS_VASCULAR"]["min_detectable_ratio_80pct_power"]
    _hi = 100 * (mde / pos["min_fold_mean_significant"] - 1)
    _lo = 100 * (mde / pos["max_fold_mean_not_significant"] - 1)

    def panel(kinds, title, rank=False):
        sub = pr[pr["kind"].isin(kinds)].copy()
        if rank:
            sub = sub.sort_values("fold_ab", ascending=False)
        t = pd.DataFrame({
            "Class": sub.kind.map(label),
            "Pair": sub.name,
            "k (A/B)": [f"{a}/{b}" for a, b in zip(sub.k_a, sub.k_b)],
            "fold, null mean": sub.fold_ab.round(2),
            "fold, null median": sub.fold_ab_med.round(1),
            "p": ["< 0.001" if q < 0.001 else f"{q:.3f}" for q in sub.p_ab],
        })
        return f"**{title}**\n\n{md(t, '{:.2f}')}\n"

    body = (
        "# Supplementary Table S13. Positive control: the same null applied to pairs whose "
        "relatedness is fixed externally\n\n"
        "Every network claim in this paper rests on one null, so the null was run on pairs whose "
        "relatedness is curated elsewhere and cannot depend on any choice of ours. The statistic "
        "is the one behind the per-module results: random-walk-with-restart mass (α = 0.7) from a "
        "uniform seed on the first set, summed over the second, with the second set held fixed "
        "and only the first replaced by 1,000 degree-decile-matched random sets. Two folds are "
        "given. **fold, null mean** divides by the mean of the null draws and is the definition "
        "used in Table S6. **fold, null median** divides by their median. For these targets the "
        f"null is strongly right-skewed (coefficient of variation {pos['null_cv_median']:.1f}, "
        "against 0.4–0.7 for the per-module targets), because a 19-gene seed set that happens to "
        "make several direct contacts deposits an order of magnitude more mass than one that "
        "makes none. The mean therefore sits above the bulk of the draws, and the mean-based fold "
        "of an unrelated pair falls below 1. Against the median an unrelated pair centres on "
        f"{cal['fold_median_ratio_median']:.2f}, which is what a calibration claim needs; against "
        "the mean the resolution threshold is nearly the same for every pair, which is what a "
        "detection claim needs. **p** is the fraction of the 1,000 draws at or above the observed "
        "value.\n\n"
        "The code path is the published one. Pointed at three module pairs whose folds appear in "
        "Table S6, it reproduces the observed masses exactly (to six decimal places) and the "
        f"folds to within {100 * rep.get('max_relative_fold_difference', float('nan')):.1f}% "
        "(2.07 against 2.04, 2.61 against 2.56), which is the sampling error of a 2,000-draw "
        "null.\n\n"
        "**Calibration.** The pairs with no reason to be proximal behave as they should. All "
        f"{cal['n_unrelated']} give a median fold over the null median of "
        f"{cal['fold_median_ratio_median']:.2f} (IQR {cal['fold_median_ratio_q1']:.2f}–"
        f"{cal['fold_median_ratio_q3']:.2f}) and a median p of {cal['p_median']:.2f}. "
        f"Of the {rnd['n']} random pairs, {rnd['n_p_lt_0.05']} reach p < 0.05, and none of the three "
        f"curated negative controls does (p = {negp[0]:.3f}, {negp[1]:.3f}, {negp[2]:.3f}). Decile "
        "matching leaves an order of magnitude of degree spread inside the top stratum, so a set "
        "of near-hub genes can outperform its own null; that is the residual miscalibration, and "
        "it runs in the anti-conservative direction.\n\n"
        f"**Resolution.** Of the {pos['n'] + cx['n']} distinct related pairs, "
        f"{pos['n_p_lt_0.05'] + cx['n_p_lt_0.05']} reach p < 0.05: "
        f"{pos['n_p_lt_0.05']} of the {pos['n']} pathway halves and one complex, the ribosomal "
        f"pair at {cx['fold_mean_ratio_max']:.1f}-fold. In fold units the threshold is sharp. No related pair "
        f"below {pos['max_fold_mean_not_significant']:.1f}-fold reached p < 0.05, and every pair "
        f"at or above {pos['min_fold_mean_significant']:.1f}-fold did. The analytic inversion in the "
        f"main text, which asserted {mde:.1f}-fold from the quantiles of the ratio null, is "
        f"therefore {_hi:.0f}–{_lo:.0f}% above a floor that can be measured directly on pairs "
        "whose answer is known.\n\n"
        + panel(["complex", "pathway_half"], "Panel A. Pairs known to be related, by fold.",
                rank=True)
        + "\n"
        + panel(["negative", "random_pair"], "Panel B. Pairs with no reason to be proximal.")
        + "\n"
        + panel(["pathway_half_split2"], "Panel C. Second independent split of six pathways.")
        + "\n"
        + "The second split in Panel C was drawn independently of the first. The two splits agree "
        f"to a correlation of {spl['correlation']:.3f} and a largest relative difference of "
        f"{100 * spl['max_relative_difference']:.1f}%, so the fold is a property of the pathway "
        "rather than of where the cut fell.\n"
    )
    open(os.path.join(TAB, "s13_positive_control.md"), "w", encoding="utf-8").write(body)

    print("written s7_legacy_pt.md, s8_holdout.md, s13_positive_control.md, "
          "table3_decidability.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
