"""91_severity.py -- is the costimulation ordering an ordering of severity?

Why this exists
---------------
FAERS records ICANS as a single preferred term. It carries no grade, so the primary
endpoint treats grade 1 confusion and grade 4 coma alike, and a reviewer is entitled to
ask whether the costimulation ordering is an ordering of severity rather than of
phenotype mix.

Two proxies are built, and the first is reported as a failure.

  1. **The `serious` flag.** Present on every record, but with 98.7% of phenotype reports
     flagged serious it has almost no variance. A binary with 278 negatives cannot
     stratify anything, and saying so is the honest answer to "use the seriousness
     field". `seriousnesslifethreatening` and the hospitalisation flags were not retained
     in the frozen extract, so they cannot be added without changing the dataset and
     every digest in the paper.

  2. **A PT-level acuity proxy.** ASTCT grade 3-4 has term-level signatures that are
     recorded: encephalopathy, depressed level of consciousness, coma, brain oedema,
     seizure, status epilepticus and paresis for ICANS; shock, respiratory failure,
     capillary leak, haemophagocytic lymphohistiocytosis / macrophage activation and
     multiple organ dysfunction for CRS. Mild ICANS is coded as *Confusional state* or
     *Somnolence*, and mild CRS as *Pyrexia* or *Hypotension*; those are deliberately
     excluded, so the proxy is conservative rather than broad.

The terms were fixed before the contrast was computed and are listed in the output, so a
reader can redefine them. Two endpoints are then recomputed exactly as in the primary
analysis -- same de-duplication, same 2019 window, same primary-suspect restriction, same
eligibility threshold, same exhaustive C(7,2) permutation:

  (a) the share of a product's ICANS reports that are high-acuity (severity composition);
  (b) R recomputed with both phenotypes restricted to their high-acuity forms (R_hi).

Outputs: out/case_severity.csv, out/case_severity.json
"""
from __future__ import annotations

import csv
import itertools
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
CASES = os.path.join(HERE, "data", "cases_icans_crs.jsonl")
SUBS = os.path.join(HERE, "config", "substances.csv")

ICANS = "Immune effector cell-associated neurotoxicity syndrome"
CRS = "Cytokine release syndrome"

ACUITY_ICANS = [
    "Encephalopathy",
    "Depressed level of consciousness",
    "Coma",
    "Brain oedema",
    "Cerebral oedema",
    "Seizure",
    "Status epilepticus",
    "Hemiparesis",
    "Paraparesis",
    "Quadriparesis",
    "Quadriplegia",
    "Intracranial pressure increased",
]
ACUITY_CRS = [
    "Shock",
    "Septic shock",
    "Distributive shock",
    "Circulatory collapse",
    "Respiratory failure",
    "Acute respiratory failure",
    "Capillary leak syndrome",
    "Haemophagocytic lymphohistiocytosis",
    "Macrophage activation syndrome",
    "Multiple organ dysfunction syndrome",
]

MIN_PHENO = 20      # primary eligibility rule
MIN_HI = 20         # same rule applied to the acuity denominator


def load() -> list[dict]:
    best: dict[str, dict] = {}
    with open(CASES, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            try:
                v = int(r.get("ver") or 0)
            except ValueError:
                v = 0
            k = str(r.get("sid"))
            if k not in best or v > best[k]["_v"]:
                r["_v"] = v
                best[k] = r
    return list(best.values())


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else float("nan")


def exact_contrast(cd28: list[float], bb: list[float]) -> dict:
    """Exhaustive C(n, n_cd28) permutation of the group label, as in the primary test."""
    vals = cd28 + bb
    n1 = len(cd28)
    obs = mean(cd28) - mean(bb)
    diffs = []
    for idx in itertools.combinations(range(len(vals)), n1):
        a = [vals[i] for i in idx]
        b = [vals[i] for i in range(len(vals)) if i not in idx]
        diffs.append(mean(a) - mean(b))
    ge = sum(1 for d in diffs if d >= obs - 1e-12)
    return {"cd28": mean(cd28), "bb": mean(bb), "delta": obs,
            "p_one": ge / len(diffs), "p_two": min(1.0, 2 * ge / len(diffs)),
            "min_p_one": 1.0 / len(diffs), "n_assign": len(diffs),
            "n_cd28": n1, "n_bb": len(bb)}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963985
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / den
    return (ctr - half, ctr + half)


def main() -> int:
    subs = {}
    with open(SUBS, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            subs[row["substance"].strip().upper()] = row

    recs = load()
    serious = defaultdict(int)
    for r in recs:
        serious[str(r.get("serious"))] += 1
    win = [r for r in recs if (r.get("rdate") or "") >= "20190101"]
    serious_w = defaultdict(int)
    for r in win:
        serious_w[str(r.get("serious"))] += 1

    ic_set, cr_set = set(ACUITY_ICANS), set(ACUITY_CRS)
    per = defaultdict(lambda: defaultdict(int))
    for r in win:
        rs = set(r.get("reacts") or [])
        has_i, has_c = ICANS in rs, CRS in rs
        if not (has_i or has_c):
            continue
        hi_i = int(has_i and bool(rs & ic_set))
        hi_c = int(has_c and bool(rs & cr_set))
        ser = int(str(r.get("serious")) == "1")
        named = {nm for d in (r.get("drugs") or []) if str(d.get("char")) == "1"
                 for nm in (d.get("names") or []) if nm in subs}
        for nm in named:
            p = per[nm]
            p["icans"] += has_i
            p["crs"] += has_c
            p["icans_hi"] += hi_i
            p["crs_hi"] += hi_c
            p["icans_serious"] += has_i and ser

    rows = []
    for nm, p in per.items():
        s = subs[nm]
        if s["group"] not in ("CAR-T", "BiTE"):
            continue
        n_pheno = p["icans"] + p["crs"]
        if n_pheno < MIN_PHENO:
            continue
        n_hi = p["icans_hi"] + p["crs_hi"]
        lo, hi = wilson(p["icans_hi"], p["icans"])
        rows.append({
            "substance": nm, "short": s["short"], "group": s["group"],
            "costim": s["costim"], "target": s["target"],
            "n_icans": p["icans"], "n_crs": p["crs"], "n_pheno": n_pheno,
            "R": p["icans"] / n_pheno,
            "n_icans_hi": p["icans_hi"], "n_crs_hi": p["crs_hi"], "n_hi": n_hi,
            "share_icans_hi": p["icans_hi"] / p["icans"] if p["icans"] else "",
            "share_icans_hi_lo": lo, "share_icans_hi_hi": hi,
            "share_icans_serious": p["icans_serious"] / p["icans"] if p["icans"] else "",
            "R_hi": (p["icans_hi"] / n_hi) if n_hi >= MIN_HI else "",
        })
    rows.sort(key=lambda r: -r["R"])

    # Report classes inside the analysed set: the arithmetic that makes R a margin ratio
    # rather than a share of patients. Included here because it is the definitional point
    # reviewers raise first.
    eligible = {r["substance"] for r in rows}
    classes = {"icans_only": 0, "crs_only": 0, "both": 0}
    for r in win:
        if not any(str(d.get("char")) == "1"
                   and any(nm in eligible for nm in (d.get("names") or []))
                   for d in (r.get("drugs") or [])):
            continue
        rs = set(r.get("reacts") or [])
        if ICANS in rs and CRS in rs:
            classes["both"] += 1
        elif ICANS in rs:
            classes["icans_only"] += 1
        elif CRS in rs:
            classes["crs_only"] += 1
    n_set = sum(classes.values())
    a = classes["icans_only"] + classes["both"]
    b = classes["crs_only"] + classes["both"]
    classes.update({
        "n": n_set,
        "n_icans_reports": a, "n_crs_reports": b,
        "R_margin": a / (a + b),
        "patient_share_icans": (classes["icans_only"] + classes["both"]) / n_set,
        "dual_share_of_icans": classes["both"] / a,
    })

    # The same three classes over the whole window, all products: the numbers quoted in the
    # Results corpus paragraph.
    corpus = {"icans_only": 0, "crs_only": 0, "both": 0}
    for r in win:
        rs = set(r.get("reacts") or [])
        if ICANS in rs and CRS in rs:
            corpus["both"] += 1
        elif ICANS in rs:
            corpus["icans_only"] += 1
        elif CRS in rs:
            corpus["crs_only"] += 1
    corpus["n"] = sum(corpus.values())
    corpus["dual_share_of_icans"] = corpus["both"] / (corpus["icans_only"] + corpus["both"])

    def groups(key: str) -> tuple[list[float], list[float]]:
        cd28 = [r[key] for r in rows if r["costim"] == "CD28" and r[key] != ""]
        bb = [r[key] for r in rows if r["costim"] == "4-1BB" and r[key] != ""]
        return cd28, bb

    cd28, bb = groups("R")
    primary = exact_contrast(cd28, bb)

    out = {
        "dedup_reports": len(recs), "window_reports": len(win),
        "serious_flag_all": dict(serious), "serious_flag_window": dict(serious_w),
        "serious_share_window": serious_w.get("1", 0) / len(win),
        "acuity_terms": {"icans": ACUITY_ICANS, "crs": ACUITY_CRS},
        "min_pheno": MIN_PHENO, "min_hi": MIN_HI,
        "n_products": len(rows),
        "report_classes_in_analysed_set": classes,
        "corpus_classes_window": corpus,
        "primary_contrast_check": primary,
        "contrast_share_icans_hi": exact_contrast(*groups("share_icans_hi")),
        "contrast_R_hi": exact_contrast(*groups("R_hi")),
    }
    tot_i = sum(r["n_icans"] for r in rows)
    tot_hi = sum(r["n_icans_hi"] for r in rows)
    out["share_icans_hi_pooled"] = tot_hi / tot_i
    out["n_icans_pooled"] = tot_i
    out["n_icans_hi_pooled"] = tot_hi
    out["share_icans_serious_pooled"] = (
        sum(r["share_icans_serious"] * r["n_icans"] for r in rows) / tot_i)

    with open(os.path.join(OUT, "case_severity.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v)
                        for k, v in r.items()})
    with open(os.path.join(OUT, "case_severity.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, default=str)

    print(json.dumps(out, indent=2, default=str))
    print("\nper product:")
    for r in rows:
        rhi = f"{r['R_hi']:.3f}" if r["R_hi"] != "" else "  —  "
        print(f"  {r['short']:<10} {r['costim']:<6} R={r['R']:.3f} R_hi={rhi} "
              f"share_hi={r['share_icans_hi']:.3f} "
              f"icans={r['n_icans']:>5} hi={r['n_icans_hi']:>4} "
              f"crs_hi={r['n_crs_hi']:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
