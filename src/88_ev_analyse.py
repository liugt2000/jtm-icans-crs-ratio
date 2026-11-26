"""Does the ICANS/CRS partition reproduce in a second reporting system?

Reads out/ev_counts.json (written by 87_ev_counts.py) and compares it with the FAERS
partition in manuscript/tables/table1_products.md.

The comparison is deliberately narrow. We do not re-derive the mechanism, the network
or the model here; we ask only whether the ordering of R = ICANS/(ICANS+CRS) across
products, and the CD28-above-4-1BB grouping that the paper rests on, survives a change
of reporting system, a change of country mix and a change of time window.

Statistics carried over unchanged from the primary analysis: Wilson score intervals,
a two-sided Spearman correlation for the cross-system agreement, and the exact
enumeration of every 2-vs-(k-2) label assignment for the costimulation test, with the
attainable minimum reported alongside the p value.

Output: out/ev_replication.json
        manuscript/tables/s9_ev_replication.md
"""
from __future__ import annotations

import json
import math
import re
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
TAB = ROOT / "manuscript" / "tables"

# product label in ev_counts.json -> (display name, modality, costimulation, FAERS R)
# FAERS R is transcribed from table1_products.md (primary suspect, received >= 2019-01-01).
# tarlatamab is absent: no adrreports.eu substance entry.
PRODUCTS = {
    "tisa":  ("tisa-cel",     "CAR-T", "4-1BB", 0.221),
    "liso":  ("liso-cel",     "CAR-T", "4-1BB", 0.318),
    "obe":   ("obe-cel",      "CAR-T", "4-1BB", 0.320),
    "cilta": ("cilta-cel",    "CAR-T", "4-1BB", 0.295),
    "ide":   ("ide-cel",      "CAR-T", "4-1BB", 0.218),
    "axi":   ("axi-cel",      "CAR-T", "CD28",  0.332),
    "brexu": ("brexu-cel",    "CAR-T", "CD28",  0.390),
    "tecli": ("teclistamab",  "BiTE",  None,    0.273),
    "talq":  ("talquetamab",  "BiTE",  None,    0.256),
    "elran": ("elranatamab",  "BiTE",  None,    0.246),
    "blina": ("blina",        "BiTE",  None,    0.199),
    "epcor": ("epcoritamab",  "BiTE",  None,    0.163),
    "glofi": ("glofitamab",   "BiTE",  None,    0.150),
}
MIN_REPORTS = 20


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a: list[float], b: list[float]) -> float:
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


def load() -> dict[tuple[str, str], int]:
    rows = [json.loads(l) for l in (OUT / "ev_counts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return {(r["substance"], r["phenotype"]): r for r in rows if r.get("status") == "ok"}


def exact_perm(rs: dict[str, float], cd28: set[str], k_grp: int = 2) -> dict:
    """Enumerate every way of assigning k_grp of the products to the small group."""
    names = list(rs)
    obs = (sum(rs[p] for p in names if p in cd28) / max(1, len(cd28))
           - sum(rs[p] for p in names if p not in cd28) / max(1, len(names) - len(cd28)))
    diffs = []
    for combo in combinations(names, k_grp):
        a = [rs[p] for p in combo]
        b = [rs[p] for p in names if p not in combo]
        diffs.append(sum(a) / len(a) - sum(b) / len(b))
    ge = sum(1 for d in diffs if d >= obs - 1e-12)
    le = sum(1 for d in diffs if d <= obs + 1e-12)
    n = len(diffs)
    return {"diff": obs, "n_assignments": n,
            "p_one_sided": ge / n, "p_two_sided": min(1.0, 2 * min(ge, le) / n),
            "min_p_one_sided": 1 / n, "attains_minimum": ge == 1}


def main() -> int:
    rec = load()
    rows, missing = [], []
    for lab, (disp, modality, costim, faers_r) in PRODUCTS.items():
        ic, cr = rec.get((lab, "icans")), rec.get((lab, "crs"))
        ntx = rec.get((lab, "neurotox"))
        if not ic or not cr:
            missing.append(disp)
            continue
        ni, nc = ic["n"], cr["n"]
        phen = ni + nc
        r = ni / phen if phen else float("nan")
        lo, hi = wilson(ni, phen)
        rows.append({
            "product": disp, "modality": modality, "costimulation": costim,
            "total_icsr": ic.get("total_icsr"),
            "icans": ni, "crs": nc, "phenotype_reports": phen,
            "R_ev": r, "ci": [lo, hi], "R_faers": faers_r,
            "delta_ev_minus_faers": r - faers_r,
            "n_neurotox": ntx["n"] if ntx else None,
            "R_ev_legacy": (ntx["n"] / (ntx["n"] + nc)) if ntx and (ntx["n"] + nc) else None,
            "analysable": phen >= MIN_REPORTS,
        })

    rows.sort(key=lambda d: -d["R_ev"])
    ok = [d for d in rows if d["analysable"]]

    # cross-system agreement, restricted to analysable products
    rho = spearman([d["R_faers"] for d in ok], [d["R_ev"] for d in ok]) if len(ok) > 2 else float("nan")
    # sign concordance: does EV put FAERS' upper product higher?
    concord = sum(1 for a, b in combinations(ok, 2)
                  if (a["R_faers"] - b["R_faers"]) * (a["R_ev"] - b["R_ev"]) > 0)
    pairs = len(ok) * (len(ok) - 1) // 2

    # costimulation test on the CAR-T subset that EV can resolve
    cart = {d["product"]: d["R_ev"] for d in ok if d["modality"] == "CAR-T"}
    cd28 = {p for p, d in ((x["product"], x) for x in ok) if d["costimulation"] == "CD28"}
    perm = exact_perm(cart, cd28) if len(cd28) == 2 and len(cart) >= 4 else None
    # obe-cel clears the threshold on 31 European reports; including it moves the design
    # from six to seven CAR-T products and therefore lowers the attainable one-sided
    # minimum from 1/15 to 1/21. The p value must not be bought by that inclusion, so the
    # six-product version is reported alongside it.
    cart_no_obe = {k: v for k, v in cart.items() if k != "obe-cel"}
    perm_no_obe = (exact_perm(cart_no_obe, cd28)
                   if len(cd28) == 2 and len(cart_no_obe) >= 4 else None)
    faers_cart_mean = {
        "CD28": sum(PRODUCTS[k][3] for k in ("axi", "brexu")) / 2,
        "4-1BB": sum(PRODUCTS[k][3] for k in ("tisa", "liso", "obe", "cilta", "ide")) / 5,
    }

    out = {
        "n_products_queried": len(PRODUCTS), "missing": missing,
        "n_analysable": len(ok), "min_reports": MIN_REPORTS,
        "totals": {
            "n_products": len(ok),
            "total_icsr": sum(d["total_icsr"] or 0 for d in ok),
            "phenotype_reports": sum(d["phenotype_reports"] for d in ok),
            "icans": sum(d["icans"] for d in ok),
            "crs": sum(d["crs"] for d in ok),
            "n_lower_in_ev": sum(1 for d in ok if d["delta_ev_minus_faers"] < 0),
            "cart_41bb_mean_drop": (
                sum(-d["delta_ev_minus_faers"] for d in ok
                    if d["costimulation"] == "4-1BB") /
                max(1, sum(1 for d in ok if d["costimulation"] == "4-1BB"))),
            "cart_cd28_mean_delta": (
                sum(d["delta_ev_minus_faers"] for d in ok
                    if d["costimulation"] == "CD28") /
                max(1, sum(1 for d in ok if d["costimulation"] == "CD28"))),
            "cd28_mean_R": (sum(d["R_ev"] for d in ok if d["costimulation"] == "CD28") /
                            max(1, sum(1 for d in ok if d["costimulation"] == "CD28"))),
            "41bb_mean_R": (sum(d["R_ev"] for d in ok if d["costimulation"] == "4-1BB") /
                            max(1, sum(1 for d in ok if d["costimulation"] == "4-1BB"))),
        },
        "table": rows,
        "spearman_faers_vs_ev": rho, "n_pairs": len(ok),
        "pairwise_sign_concordance": {"concordant": concord, "pairs": pairs,
                                      "fraction": concord / pairs if pairs else None},
        "costimulation_ev": perm,
        "costimulation_ev_without_obe": perm_no_obe,
        "costimulation_faers_reference": {"CD28_mean": faers_cart_mean["CD28"],
                                          "4-1BB_mean": faers_cart_mean["4-1BB"],
                                          "diff": faers_cart_mean["CD28"] - faers_cart_mean["4-1BB"]},
        "cart_products_in_ev": len(cart),
        "median_abs_delta": sorted(abs(d["delta_ev_minus_faers"]) for d in ok)[len(ok) // 2] if ok else None,
    }
    (OUT / "ev_replication.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- markdown table ---------------------------------------------------
    TAB.mkdir(parents=True, exist_ok=True)
    L = ["# Supplementary table S9. The partition in EudraVigilance", "",
         ("Case counts returned by the EudraVigilance data analysis system for each "
          "substance, restricted to the two phenotype preferred terms, and the resulting "
          "R = ICANS/(ICANS+CRS). R(FAERS) is the corresponding value from Table 1. "
          f"Products with fewer than {MIN_REPORTS} phenotype reports in EV are listed but "
          "not analysed."), "",
         "| Product | Modality | Costimulation | EV total ICSRs | ICANS | CRS | R(EV) | 95% CI | R(FAERS) | Δ |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for d in rows:
        dl = d["delta_ev_minus_faers"]
        dlt = ("+" if dl >= 0 else "\u2212") + f"{abs(dl):.3f}"
        L.append("| {product} | {modality} | {co} | {tot:,} | {ni:,} | {nc:,} | {r:.3f} | "
                 "{lo:.3f}–{hi:.3f} | {fr:.3f} | {dlt} |".format(
                     product=d["product"], modality=d["modality"], co=d["costimulation"] or "—",
                     tot=d["total_icsr"], ni=d["icans"], nc=d["crs"], r=d["R_ev"],
                     lo=d["ci"][0], hi=d["ci"][1], fr=d["R_faers"], dlt=dlt))
    L += ["", f"Spearman ρ between R(FAERS) and R(EV) over the {len(ok)} analysable products: "
              f"**{rho:.3f}**; {concord} of {pairs} pairs ordered the same way.", ""]
    if perm:
        L += [f"Costimulation test in EV over {len(cart)} resolvable CAR-T products "
              f"(all {perm['n_assignments']} label assignments enumerated): "
              f"Δ = {perm['diff']:+.3f}, one-sided p = {perm['p_one_sided']:.3f}, "
              f"two-sided p = {perm['p_two_sided']:.3f} "
              f"(attainable minimum {perm['min_p_one_sided']:.3f}).", ""]
    (TAB / "s9_ev_replication.md").write_text("\n".join(L), encoding="utf-8")

    print(f"products queried {len(PRODUCTS)}, missing {missing}, analysable {len(ok)}")
    for d in rows:
        print(f"  {d['product']:<14}{d['icans']:>6}{d['crs']:>7}  R={d['R_ev']:.3f} "
              f"[{d['ci'][0]:.3f}-{d['ci'][1]:.3f}]  FAERS={d['R_faers']:.3f}  "
              f"d={d['delta_ev_minus_faers']:+.3f}")
    print(f"\nSpearman rho = {rho:.3f}   concordant {concord}/{pairs}")
    if perm:
        print(f"costimulation: diff={perm['diff']:+.3f} p1={perm['p_one_sided']:.3f} "
              f"p2={perm['p_two_sided']:.3f} n_assign={perm['n_assignments']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
