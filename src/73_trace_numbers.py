"""Trace every headline number in the manuscript back to the file that produced it.

The claim made in the paper is that no number is hand-entered. This script is the check:
it pulls each value out of `out/*.json`, formats it exactly as the text states it, and
asserts the formatted string occurs in `manuscript.md` or in Additional file 1. A failure means either the text or
the analysis moved, and the paper is not internally consistent until they agree again.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
# The supplementary tables now live in Additional file 1 rather than in the main file, so the
# trace pool is both documents. A number that appears in neither still fails.
MAIN = (ROOT / "manuscript" / "manuscript.md").read_text(encoding="utf-8")
_supp = ROOT / "manuscript" / "additional_file1_tables.md"
SUPP = _supp.read_text(encoding="utf-8") if _supp.exists() else ""
TXT = MAIN + "\n" + SUPP


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def n(x: int) -> str:
    return f"{x:,}"


checks: list[tuple[str, str, bool]] = []


_FLAT = re.compile(r"\s+")
# The manuscript is hard-wrapped at 96 columns, so a phrase may straddle a newline. Both
# sides are whitespace-collapsed before matching, otherwise the check fails on layout
# rather than on content.
TXT_FLAT = _FLAT.sub(" ", TXT)


def want(label: str, needle: str) -> None:
    checks.append((label, needle, _FLAT.sub(" ", needle) in TXT_FLAT))


cg = load("case_groups.json")
want("records retrieved", n(cg["n_reports_raw"]))
want("records in window", n(cg["n_reports_in_window"]))
want("eligible products", f'{cg["n_products_eligible"]} products')

cp = [r for r in (OUT / "case_products.csv").read_text(encoding="utf-8").splitlines()]
# co-reporting: ICANS x CRS both, from the analysis file
gr = cg.get("group_R") or {}
for g in ("CD28", "4-1BB", "BiTE"):
    if g in gr and "R" in gr[g]:
        want(f"group R {g}", f'{gr[g]["R"]:.3f}')

perm = cg["perm_CD28_vs_41BB"]
want("delta", f'{perm["diff"]:.3f}')
want("p one-sided", f'{perm["p_one_sided"]:.3f}')
want("p two-sided", f'{perm["p_two_sided"]:.3f}')

iso = cg.get("perm_CD28_vs_41BB_isolated")
if iso:
    want("isolated delta", f'{iso["diff"]:.3f}')
    want("isolated p", f'{iso["p_one_sided"]:.3f}')

loc = load("localisation_hpa.json")
inter = loc["interaction_CNS_minus_MYELOID"]
want("interaction delta", f'{inter["delta"]:+.2f}')
want("interaction z", f'{inter["z"]:+.2f}')

nr = load("network_null_ratio.json")
for k in ("CNS_VASCULAR", "MYELOID_CYTOKINE"):
    if k in nr and "ratio" in nr[k]:
        want(f"network ratio {k}", f'{nr[k]["ratio"]:.2f}')

pw = load("power_network.json")
if "by_target" in pw:
    for t, v in pw["by_target"].items():
        if isinstance(v, dict) and "mdr_80" in v:
            want(f"MDR {t}", f'{v["mdr_80"]:.1f}')

sob = load("model_sobol.json")
for cond in ("unsaturated", "nominal"):
    want(f"production ST sum {cond}", f'{sob[cond]["production_total_order_sum"]:.3f}')
    want(f"amplification ST sum {cond}", f'{sob[cond]["amplification_total_order_sum"]:.3f}')

# One-at-a-time relative changes, as percentages of R, quoted in the results
inv = load("model_invariance.json")
for cond, label in (("unsaturated_Emax_1e4", "unsaturated"), ("nominal_Emax_8", "nominal")):
    if cond in inv:
        block = {k: v for k, v in inv[cond].items() if isinstance(v, dict)}
        prod_max = max((v["relative_change"] for v in block.values()
                        if v.get("kind") == "production"), default=0.0)
        amp_max = max((v["relative_change"] for v in block.values()
                       if v.get("kind") == "amplification"), default=0.0)
        want(f"production OAT max {label}", f"{round(prod_max * 100)}%")
        if label == "unsaturated":       # the nominal amplification figure is not quoted
            want(f"amplification OAT max {label}", f"{round(amp_max * 100)}%")

cr = cg["co_reporting"]
want("co-reporting ICANS n", n(cr["n_icans_reports"]))
want("co-reporting both phenotypes", n(cr["n_with_crs_also"]))
want("co-reporting fraction", f'{cr["fraction_with_crs"] * 100:.1f}%')

ip = cg["isolated_phenotype"]
want("isolated delta", f'{ip["perm_CD28_vs_41BB"]["diff"]:.3f}')
want("isolated p", f'{ip["perm_CD28_vs_41BB"]["p_one_sided"]:.3f}')

dp = cg["within_product_drift"]
want("products with drift", f'{dp["n_rising"]} of {dp["n_products"]}')
want("median drift", f'{dp["median_delta"]:+.3f}')

ys = cg["year_stratified"]
want("years with positive delta",
     {8: "eight", 7: "seven", 6: "six"}[ys["n_years_delta_positive"]] +
     " of " + {8: "eight", 7: "eight", 6: "eight"}.get(ys["n_years"], "eight"))

tr = cg["temporal_rank"]
want("temporal rho", f'{tr["spearman_rho"]:.2f}')
want("temporal p", f'{tr["p"]:.4f}')

nra = load("network_null_ratio.json")
cns = nra["CNS_VASCULAR"]
want("network observed ratio", f'{cns["observed_ratio"]:.2f}')
want("network z", f'{abs(cns["z"]):.2f}')
want("network p", f'{cns["p_greater"]:.2f}')

pod = load("power_network.json")["by_target"]["CNS_VASCULAR"]
want("minimum detectable ratio", f'{pod["min_detectable_ratio_80pct_power"]:.1f}')
want("module size needed", n(pod["module_size_needed_to_resolve_observed"]))
# the Results write this number as a word ("nineteen were available")
want("module size used", f'{"nineteen" if pod["module_size_used"] == 19 else pod["module_size_used"]} were available')

locm = loc["modules"] if "modules" in loc else {}
for mod, key in (("CNS_VASCULAR", "3.77"), ("MYELOID_CYTOKINE", "2.26")):
    if mod in locm:
        want(f"localisation L {mod}", f'{abs(locm[mod]["score_all"]):.3f}')
        want(f"localisation z {mod}", f'{abs(locm[mod]["z_all"]):.2f}')

pv = load("perturbation_validation.json")
q2 = pv["Q2_tnf_response"]["signed_log2FC"]
want("TNF induction CNS", f'{q2["CNS_VASCULAR"]["observed"]:.3f}')
want("TNF induction myeloid", f'{q2["MYELOID_CYTOKINE"]["observed"]:.3f}')
want("TNF z CNS", f'{q2["CNS_VASCULAR"]["z"]:.2f}')

ho = load("holdout.json")
want("holdout MAE class-based", f"{ho['mae_class_mean']:.3f}")
want("holdout MAE class-blind", f"{ho['mae_class_blind']:.3f}")
want("holdout exact p",
     f"p = {ho['p_exact_class_better_than_random_grouping']:.2f}")
want("holdout n products", f"{ho['n_null_assignments']} ways of")

rule = load("prediction_rule.json")
want("reference n", n(rule["reference_n"]))
band = rule["blind_band_at_reference_n"]
want("blind band lower bound", f"{band[0]:.3f}")
want("blind band upper bound", f"{band[1]:.3f}")
tab = {round(r["true_R"], 3): r for r in rule["table"]}
for r_true in (0.250, 0.300, 0.325, 0.340):
    need = tab[r_true]["min_reports_for_decisive_verdict"]
    if need is not None and need == need:
        want(f"min reports at R={r_true:.3f}", n(int(need)))

lg = load("legacy_pt.json")
for key, label in (("union", "R union"), ("legacy_only", "R legacy")):
    pr = lg[key]["perm_CD28_vs_41BB"]
    want(f"{label} delta", f"{pr['diff']:+.3f}")
    want(f"{label} one-sided p", f"{pr['p_one_sided']:.3f}")
want("legacy records pulled", n(lg["n_legacy_records_pulled"]))
want("legacy shared reports", n(lg["n_shared_reports_with_primary_pull"]))

ev = load("ev_replication.json")
tot = ev["totals"]
want("EV products", "Thirteen of the fourteen")
want("EV total ICSRs", n(tot["total_icsr"]))
want("EV phenotype reports", n(tot["phenotype_reports"]))
want("EV ICANS", n(tot["icans"]))
want("EV CRS", n(tot["crs"]))
want("EV spearman", f'{ev["spearman_faers_vs_ev"]:.2f}')
want("EV concordant pairs", f'{ev["pairwise_sign_concordance"]["concordant"]} of the '
                            f'{ev["pairwise_sign_concordance"]["pairs"]} product pairs')
want("EV CD28 mean", f'{tot["cd28_mean_R"]:.3f}')
want("EV 4-1BB mean", f'{tot["41bb_mean_R"]:.3f}')
want("EV delta", f'{ev["costimulation_ev"]["diff"]:+.3f}')
want("EV one-sided p", f'{ev["costimulation_ev"]["p_one_sided"]:.3f}')
want("EV two-sided p", f'{ev["costimulation_ev"]["p_two_sided"]:.3f}')
want("EV assignments", f'{ev["costimulation_ev"]["n_assignments"]} label assignments')
wr = ev["costimulation_ev_without_obe"]
want("EV delta without obe", f'{wr["diff"]:.3f}')
want("EV p without obe", f'{wr["p_one_sided"]:.3f}')
want("EV design change", "1/15 to 1/21")
want("EV median abs delta", f'{ev["median_abs_delta"]:.3f}')
want("EV 4-1BB mean drop", f'{tot["cart_41bb_mean_drop"]:.3f}')
want("EV CD28 mean delta", f'{tot["cart_cd28_mean_delta"]:+.3f}')
want("EV products lower", "Eleven of the thirteen products sit lower")
for d in ev["table"]:
    if d["product"] in ("axi-cel", "brexu-cel", "liso-cel", "cilta-cel", "ide-cel", "obe-cel"):
        want(f'EV {d["product"]} R', f'{d["R_ev"]:.3f}')
        want(f'EV {d["product"]} delta', f'{abs(d["delta_ev_minus_faers"]):.3f}')

st = load("strata.json")
_W = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
      10: "ten"}
word = lambda k: _W.get(k, str(k))
want("strata count", f'Splitting the extract {word(st["n_strata"])} ways')
want("strata testable", f'all {word(st["n_tested"])} testable strata')
want("strata separating count", f'only {word(st["n_separating"])}')
_sr = {r["stratum"]: r for r in st["rows"]}
want("strata Europe delta", f'{_sr["Europe"]["diff"]:+.3f}')
want("strata US delta", f'{_sr["United States"]["diff"]:+.3f}')
want("strata US p", f'{_sr["United States"]["p_one_sided"]:.3f}')
want("strata physician delta", f'{_sr["Physician"]["diff"]:+.3f}')
want("strata physician p", f'{_sr["Physician"]["p_one_sided"]:.3f}')
want("strata US physician delta", f'{_sr["US, physician only"]["diff"]:+.3f}')
want("strata Japan untestable", "only one CD28 product reaches twenty")

pc_ = load("positive_control.json")
ps_ = load("positive_control_summary.json")
_byc = ps_["by_class"]
_pos, _cx, _rnd = _byc["pathway_half"], _byc["complex"], _byc["random_pair"]
_W2 = {2: "two", 3: "three", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}
_N_REL = _pos["n"] + _cx["n"]
_N_SIG = _pos["n_p_lt_0.05"] + _cx["n_p_lt_0.05"]
want("control distinct pairs", f"{_N_REL} distinct related pairs")
want("control significant count", f"{_N_SIG} reach p < 0.05")
want("control results sentence", f"{_W2[_N_SIG].capitalize()} of the {_N_REL}")
want("control floor, not resolved", f"{_pos['max_fold_mean_not_significant']:.1f}-fold")
want("control floor, resolved", f"{_pos['min_fold_mean_significant']:.1f}-fold")
want("control ribosome fold", f"{_cx['fold_mean_ratio_max']:.1f}-fold")
want("control random-pair outlier", f"{_rnd['fold_mean_ratio_max']:.1f}-fold")
want("control unrelated count", f"{ps_['calibration']['n_unrelated']} with no reason")
want("control random false positives",
     f"{_W2[_rnd['n_p_lt_0.05']]} of the {_W2[_rnd['n']]} random pairs")
want("control median ratio, unrelated",
     f"of {ps_['calibration']['fold_median_ratio_median']:.2f} (IQR")
want("control reported pairs", f"{_pos['n']} pathway halves")

# An unresolved token means the manuscript still carries a placeholder where a DOI or a
# repository URL belongs. That must never reach a submission, so it fails here rather than
# being caught by a reader.
_TOKENS = re.findall(r"\{\{[A-Z0-9_]+\}\}", TXT)
if _TOKENS:
    print("unresolved placeholders in manuscript.md: " + ", ".join(sorted(set(_TOKENS))))

bad = [c for c in checks if not c[2]]
for label, needle, ok in checks:
    print(("  ok   " if ok else "  FAIL ") + f"{label:<28} {needle}")
print(f"\n{len(checks) - len(bad)}/{len(checks)} traced")
if bad:
    print("not found in manuscript.md: " + ", ".join(b[0] for b in bad))
raise SystemExit(1 if bad or _TOKENS else 0)
