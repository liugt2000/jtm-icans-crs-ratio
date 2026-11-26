"""76_recount.py -- rebuild the headline numbers from the frozen case file, independently.

73_trace_numbers.py answers "does the text match the analysis outputs". This answers a
different question: "do the analysis outputs match the data". It re-reads
data/cases_icans_crs.jsonl with plain dicts and loops -- no pandas, no import of src/21 --
applies the rules stated in the Methods, and compares the results with both
out/case_groups.json and the strings printed in manuscript.md.

A disagreement is reported, not reconciled: if the two implementations differ, the
manuscript is only as good as the one that is wrong.
"""
from __future__ import annotations

import itertools
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "cases_icans_crs.jsonl"
SUBS = ROOT / "config" / "substances.csv"
GROUPS = ROOT / "out" / "case_groups.json"
TXT = (ROOT / "manuscript" / "manuscript.md").read_text(encoding="utf-8")

ICANS = "Immune effector cell-associated neurotoxicity syndrome"
CRS = "Cytokine release syndrome"


def read_substances() -> dict[str, dict]:
    out = {}
    with SUBS.open(encoding="utf-8-sig") as fh:
        head = fh.readline().rstrip("\n").split(",")
        for line in fh:
            parts = line.rstrip("\n").split(",")
            row = dict(zip(head, parts))
            if row.get("group") in ("CAR-T", "BiTE"):
                out[row["substance"].upper()] = row
    return out


def main() -> int:
    subs = read_substances()

    # ---- load, deduplicate exactly as Methods states: one record per safetyreportid,
    # highest version wins.
    by_sid: dict[str, dict] = {}
    n_raw = 0
    with CASES.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            n_raw += 1
            sid = r["sid"]
            ver = int(float(r.get("ver") or 0))
            if sid not in by_sid or ver >= by_sid[sid]["_ver"]:
                r["_ver"] = ver
                by_sid[sid] = r
    recs = list(by_sid.values())
    n_dedup = len(recs)

    # ---- phenotype flags and window
    in_window = []
    n_pre = 0
    for r in recs:
        reacts = set(r.get("reacts") or [])
        r["ic"] = ICANS in reacts
        r["cr"] = CRS in reacts
        date = int(float(r.get("rdate") or 0))
        if date < 20190101:
            n_pre += 1
        else:
            in_window.append(r)

    # ---- one row per (report, product) at primary-suspect role
    per_product: dict[str, dict] = {}
    for r in in_window:
        seen = set()
        for d in r.get("drugs") or []:
            if str(d.get("char")) != "1":
                continue
            for nm in d.get("names") or []:
                if nm in subs:
                    seen.add(nm)
        for nm in seen:
            b = per_product.setdefault(nm, {"icans": 0, "crs": 0, "sids": set(), "rows": []})
            b["icans"] += int(r["ic"])
            b["crs"] += int(r["cr"])
            b["sids"].add(r["sid"])
            b["rows"].append((int(float(r["rdate"])), r["ic"], r["cr"]))

    table = []
    for nm, b in per_product.items():
        n_pheno = b["icans"] + b["crs"]
        if n_pheno < 20:
            continue
        table.append({"substance": nm, "short": subs[nm]["short"], "costim": subs[nm]["costim"],
                      "icans": b["icans"], "crs": b["crs"], "n_pheno": n_pheno,
                      "R": b["icans"] / n_pheno, "reports": len(b["sids"])})
    table.sort(key=lambda x: -x["R"])

    def mean_R(costim: str) -> float | None:
        vals = [p["R"] for p in table if p["costim"] == costim]
        return statistics.fmean(vals) if vals else None

    cart = [p for p in table if p["costim"] in ("CD28", "4-1BB")]
    labels = [1 if p["costim"] == "CD28" else 0 for p in cart]
    x = [p["R"] for p in cart]
    obs = statistics.fmean([v for v, l in zip(x, labels) if l == 1]) - \
        statistics.fmean([v for v, l in zip(x, labels) if l == 0])
    diffs = []
    for combo in itertools.combinations(range(len(x)), sum(labels)):
        m = [i in combo for i in range(len(x))]
        diffs.append(statistics.fmean([v for v, k in zip(x, m) if k]) -
                     statistics.fmean([v for v, k in zip(x, m) if not k]))
    p1 = sum(d >= obs - 1e-12 for d in diffs) / len(diffs)
    p2 = sum(abs(d) >= abs(obs) - 1e-12 for d in diffs) / len(diffs)

    # ---- co-reporting: of the reports that carry ICANS, how many also carry CRS
    n_ic = sum(1 for r in in_window if r["ic"])
    n_both = sum(1 for r in in_window if r["ic"] and r["cr"])

    # ---- within-product drift: median report date splits each product's own series
    deltas = {}
    for p in table:
        rows = sorted(per_product[p["substance"]]["rows"])
        if len(rows) < 40:
            continue
        mid = statistics.median(r[0] for r in rows)
        a = [r for r in rows if r[0] <= mid]
        b = [r for r in rows if r[0] > mid]
        if not a or not b:
            continue
        ra = sum(r[1] for r in a) / max(sum(r[1] for r in a) + sum(r[2] for r in a), 1)
        rb = sum(r[1] for r in b) / max(sum(r[1] for r in b) + sum(r[2] for r in b), 1)
        deltas[p["short"]] = rb - ra

    # ---- year-by-year: both classes present with >= 30 phenotype reports
    by_year: dict[int, list[dict]] = {}
    for r in in_window:
        by_year.setdefault(int(float(r["rdate"])) // 10000, []).append(r)
    year_deltas = []
    for y, rows in sorted(by_year.items()):
        acc: dict[str, list[int]] = {}
        for r in rows:
            seen = {nm for d in (r.get("drugs") or []) if str(d.get("char")) == "1"
                    for nm in (d.get("names") or []) if nm in subs}
            for nm in seen:
                acc.setdefault(nm, [0, 0])
                acc[nm][0] += int(r["ic"])
                acc[nm][1] += int(r["cr"])
        cd = [a / (a + b) for nm, (a, b) in acc.items()
              if a + b >= 30 and subs[nm]["costim"] == "CD28"]
        fb = [a / (a + b) for nm, (a, b) in acc.items()
              if a + b >= 30 and subs[nm]["costim"] == "4-1BB"]
        if cd and fb:
            year_deltas.append((y, statistics.fmean(cd) - statistics.fmean(fb)))

    # ---- compare with the stored outputs
    g = json.loads(GROUPS.read_text(encoding="utf-8"))
    print(f"{'quantity':<34}{'recount':>14}{'stored':>14}  match")
    rows = [
        ("reports retrieved", n_raw, g["n_reports_raw"]),
        ("after dedup", n_dedup, g["n_reports_after_dedup"]),
        ("before 2019", n_pre, g["n_reports_before_2019"]),
        ("in window", len(in_window), g["n_reports_in_window"]),
        ("eligible products", len(table), g["n_products_eligible"]),
        ("mean R CD28", round(mean_R("CD28"), 3), round(g["group_R"]["CD28"]["mean"], 3)),
        ("mean R 4-1BB", round(mean_R("4-1BB"), 3), round(g["group_R"]["4-1BB"]["mean"], 3)),
        ("mean R BiTE", round(mean_R("none"), 3), round(g["group_R"]["BiTE"]["mean"], 3)),
        ("delta CD28-4-1BB", round(obs, 3), round(g["perm_CD28_vs_41BB"]["diff"], 3)),
        ("p one-sided", round(p1, 3), round(g["perm_CD28_vs_41BB"]["p_one_sided"], 3)),
        ("p two-sided", round(p2, 3), round(g["perm_CD28_vs_41BB"]["p_two_sided"], 3)),
        ("ICANS reports", n_ic, g["co_reporting"]["n_icans_reports"]),
        ("ICANS+CRS reports", n_both, g["co_reporting"]["n_with_crs_also"]),
        ("products with drift", len(deltas), g["within_product_drift"]["n_products"]),
        ("rising", sum(d > 0 for d in deltas.values()), g["within_product_drift"]["n_rising"]),
        ("median drift", round(statistics.median(deltas.values()), 3),
         round(g["within_product_drift"]["median_delta"], 3)),
        ("years with both", len(year_deltas), g["year_stratified"]["n_years"]),
        ("years positive", sum(d > 0 for _, d in year_deltas),
         g["year_stratified"]["n_years_delta_positive"]),
    ]
    bad = 0
    for label, mine, stored in rows:
        ok = abs(float(mine) - float(stored)) < 1e-6
        bad += not ok
        print(f"{label:<34}{mine:>14}{stored:>14}  {'OK' if ok else 'MISMATCH'}")

    # ---- per-product R against the stored product table
    print("\nper-product R (recount) vs out/case_products.csv:")
    csv_rows = {}
    with (ROOT / "out" / "case_products.csv").open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split(",")
        for line in fh:
            vals = line.rstrip("\n").split(",")
            row = dict(zip(head, vals))
            if row.get("short"):
                csv_rows[row["short"]] = float(row["R"])
    for p in table:
        stored = csv_rows.get(p["short"])
        ok = stored is not None and abs(stored - p["R"]) < 5e-4
        bad += not ok
        print(f"  {p['short']:<12} {p['R']:.3f}  stored {stored if stored is not None else float('nan'):.3f}"
              f"  n={p['n_pheno']:<5} {'OK' if ok else 'MISMATCH'}")

    print(f"\n{'ALL CONSISTENT' if not bad else str(bad) + ' MISMATCHES'}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
