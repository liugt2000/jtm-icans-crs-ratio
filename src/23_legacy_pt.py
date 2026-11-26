"""
Legacy-PT sensitivity analysis.

The manuscript's primary phenotype is the single MedDRA PT *Immune effector
cell-associated neurotoxicity syndrome*, introduced in MedDRA 21.0 (2018). A referee
is entitled to ask whether the CD28 / 4-1BB ordering is a property of the biology or
of a preferred term that only exists for the second half of the products' commercial
lives. The only way to answer that is to recompute the same partition under the coding
convention that preceded it.

Two alternative numerators are built, both sharing the same denominator:

    R_legacy = n(Neurotoxicity) / (n(Neurotoxicity) + n(CRS))
    R_union  = n(ICANS or Neurotoxicity) / (n(ICANS or Neurotoxicity) + n(CRS))

R_legacy asks "what would the paper have concluded before 2018"; R_union asks "does
the conclusion survive if the narrow PT under-counts mild neurotoxicity". Both are
then put through the same exact permutation test as the primary endpoint.

The legacy reports are not in data/cases_icans_crs.jsonl (that pull was by the two
modern PTs), so they are fetched here once and cached.

Outputs: data/cases_legacy_nt.jsonl, out/legacy_pt.json, out/legacy_products.csv

Usage: python src/23_legacy_pt.py [--refresh]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
DATA = os.path.join(HERE, "data")
LEGACY_FILE = os.path.join(DATA, "cases_legacy_nt.jsonl")

BASE = "https://api.fda.gov/drug/event.json"
UA = {"User-Agent": "jtm-icans/0.3"}
PT = "Neurotoxicity"
ICANS = "Immune effector cell-associated neurotoxicity syndrome"
CRS = "Cytokine release syndrome"


# --------------------------------------------------------------------------- pull

def get(url: str, tries: int = 10) -> dict:
    delay = 1.5
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 1.7, 45)
                continue
            if exc.code == 404:
                return {"results": [], "meta": {"results": {"total": 0}}}
            raise RuntimeError(f"HTTP {exc.code} :: {url}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(delay)
            delay = min(delay * 1.7, 45)
    raise RuntimeError(f"giving up on {url}")


def reduce_record(rec: dict) -> dict:
    """Same reduction as the primary puller, so the two files are concatenable."""
    pat = rec.get("patient") or {}
    drugs = []
    for d in pat.get("drug") or []:
        names = []
        act = d.get("activesubstance") or {}
        if act.get("activesubstancename"):
            names.append(act["activesubstancename"])
        ofd = d.get("openfda") or {}
        for key in ("substance_name", "generic_name", "brand_name"):
            for v in ofd.get(key) or []:
                names.append(v)
        if d.get("medicinalproduct"):
            names.append(d["medicinalproduct"])
        seen, keep = set(), []
        for n in names:
            k = _norm(n)
            if k and k not in seen:
                seen.add(k)
                keep.append(k)
        drugs.append({"names": keep, "char": d.get("drugcharacterization"),
                      "indication": (d.get("drugindication") or "")[:80]})
    reacts = [(r.get("reactionmeddrapt") or "").strip()
              for r in (pat.get("reaction") or [])]
    ps = rec.get("primarysource") or {}
    return {"sid": rec.get("safetyreportid"), "ver": rec.get("safetyreportversion"),
            "rdate": rec.get("receivedate"),
            "country": rec.get("occurcountry") or ps.get("reportercountry"),
            "qual": ps.get("qualification"), "serious": rec.get("serious"),
            "drugs": drugs, "reacts": [r for r in reacts if r]}


def _norm(name: str) -> str:
    import re
    return re.sub(r"-[A-Z]{4}$", "", (name or "").strip().upper())


def worker(limit: int, start_page: int, step: int, path: str, state: dict) -> None:
    q = urllib.parse.quote(f'patient.reaction.reactionmeddrapt.exact:"{PT}"',
                           safe="+:.@")
    total = get(f"{BASE}?search={q}&limit=1")["meta"]["results"]["total"]
    state["total"] = total
    with open(path, "w", encoding="utf-8") as fh:
        page = start_page
        while True:
            skip = page * limit
            if skip >= total:
                break
            payload = get(f"{BASE}?search={q}&limit={limit}&skip={skip}")
            batch = payload.get("results", [])
            if not batch:
                break
            for rec in batch:
                fh.write(json.dumps(reduce_record(rec), ensure_ascii=False) + "\n")
            fh.flush()
            state["written"] = state.get("written", 0) + len(batch)
            print(f"  page {page} skip={skip} {state['written']}/{total}", flush=True)
            page += step
            time.sleep(0.35)


def pull_legacy(limit: int = 500, workers: int = 3) -> int:
    os.makedirs(DATA, exist_ok=True)
    threads, states = [], []
    for w in range(workers):
        st: dict = {}
        states.append(st)
        t = threading.Thread(target=worker,
                             args=(limit, w, workers, os.path.join(
                                 DATA, f"legacy_part_{w}.jsonl"), st))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    seen, n = set(), 0
    with open(LEGACY_FILE, "w", encoding="utf-8") as out:
        for w in range(workers):
            p = os.path.join(DATA, f"legacy_part_{w}.jsonl")
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    k = (str(o.get("sid")), str(o.get("ver")))
                    if k in seen:
                        continue
                    seen.add(k)
                    out.write(line if line.endswith("\n") else line + "\n")
                    n += 1
    print(f"  merged unique={n} -> {LEGACY_FILE}")
    return n


# ----------------------------------------------------------------------- analysis

def exact_perm(x: np.ndarray, labels: np.ndarray) -> dict:
    """Identical to the primary analysis: exact enumeration, one- and two-sided."""
    import itertools
    obs = x[labels == 1].mean() - x[labels == 0].mean()
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
            "n_products_cd28": int(n1),
            "n_products_41bb": int((labels == 0).sum())}


def wilson(k: np.ndarray, n: np.ndarray, z: float = 1.959963985):
    with np.errstate(invalid="ignore", divide="ignore"):
        p_ = k / n
        den = 1 + z ** 2 / n
        ctr = (p_ + z ** 2 / (2 * n)) / den
        half = z * np.sqrt(p_ * (1 - p_) / n + z ** 2 / (4 * n ** 2)) / den
    return ctr - half, ctr + half


def analyse() -> int:
    subs = pd.read_csv(os.path.join(HERE, "config", "substances.csv"),
                       encoding="utf-8-sig")
    subs["substance"] = subs["substance"].str.upper()
    subs_eng = subs[subs.group.isin(["CAR-T", "BiTE"])]
    canon = set(subs_eng.substance)

    # primary dataset (ICANS / CRS)
    main = []
    with open(os.path.join(DATA, "cases_icans_crs.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            main.append(json.loads(line))
    legacy = []
    with open(LEGACY_FILE, encoding="utf-8") as fh:
        for line in fh:
            legacy.append(json.loads(line))

    def frame(recs: list[dict], tag: str) -> pd.DataFrame:
        df = pd.DataFrame(recs)
        df["ver_i"] = pd.to_numeric(df["ver"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("ver_i").drop_duplicates("sid", keep="last")
        rs = df.reacts.apply(set)
        df[f"{tag}_icans"] = rs.apply(lambda s: ICANS in s)
        df[f"{tag}_legacy"] = rs.apply(lambda s: PT in s)
        df[f"{tag}_crs"] = rs.apply(lambda s: CRS in s)
        return df

    m = frame(main, "m")[["sid", "rdate", "drugs", "m_icans", "m_legacy", "m_crs"]]
    l = frame(legacy, "l")[["sid", "rdate", "drugs", "l_icans", "l_legacy", "l_crs"]]

    # union of the two pulls on safetyreportid; reactions are reported per case, so a
    # report present in both files agrees on every flag -- verified below.
    both = set(m.sid) & set(l.sid)
    j = m.merge(l, on="sid", how="outer", suffixes=("_m", "_l"))
    for a, b in (("m_icans", "l_icans"), ("m_crs", "l_crs"), ("m_legacy", "l_legacy")):
        col_a, col_b = j[a].fillna(False), j[b].fillna(False)
        disagree = int(((col_a != col_b) & j[b].notna() & j[a].notna()).sum())
        assert disagree == 0, f"{a} disagrees in {disagree} shared reports"
    j["icans"] = j.m_icans.fillna(False) | j.l_icans.fillna(False)
    j["legacy"] = j.m_legacy.fillna(False) | j.l_legacy.fillna(False)
    j["crs"] = j.m_crs.fillna(False) | j.l_crs.fillna(False)
    j["rdate"] = j.rdate_m.fillna(j.rdate_l)
    j["drugs"] = j.drugs_m.where(j.drugs_m.notna(), j.drugs_l)

    n_pre = int((pd.to_numeric(j.rdate, errors="coerce") < 20190101).sum())
    jw = j[pd.to_numeric(j.rdate, errors="coerce") >= 20190101].copy()

    # per (report, product) with the product as primary suspect
    rows = []
    for sid, drugs, ic, lg, cr in zip(jw.sid, jw.drugs, jw.icans, jw.legacy, jw.crs):
        hit = set()
        for d in (drugs if isinstance(drugs, list) else []):
            if str(d.get("char")) != "1":
                continue
            for nm in d.get("names") or []:
                if nm in canon:
                    hit.add(nm)
        for nm in hit:
            rows.append({"sid": sid, "substance": nm, "icans": bool(ic),
                         "legacy": bool(lg), "crs": bool(cr)})
    prod = pd.DataFrame(rows)
    prod["anyneu"] = prod.icans | prod.legacy

    g = (prod.groupby("substance")
             .agg(n_icans=("icans", "sum"), n_legacy=("legacy", "sum"),
                  n_anyneu=("anyneu", "sum"), n_crs=("crs", "sum"),
                  n_reports=("sid", "nunique"))
             .reset_index())
    g["n_pheno"] = g.n_anyneu + g.n_crs
    g["R_union"] = g.n_anyneu / g.n_pheno.replace(0, np.nan)
    g["R_legacy"] = g.n_legacy / (g.n_legacy + g.n_crs).replace(0, np.nan)
    for col, num in (("R_union", "n_anyneu"), ("R_legacy", "n_legacy")):
        lo, hi = wilson(g[num].to_numpy(float), g.n_pheno.to_numpy(float))
        g[col + "_lo"], g[col + "_hi"] = lo, hi
    g = g.merge(subs_eng[["substance", "short", "costim", "target"]],
                on="substance", how="left")
    g = g.sort_values("R_union", ascending=False)
    g.to_csv(os.path.join(OUT, "legacy_products.csv"), index=False)

    MIN = 20
    e = g[g.n_pheno >= MIN]
    cart = e[e.costim.isin(["CD28", "4-1BB"])]
    lab = (cart.costim == "CD28").astype(int).to_numpy()

    primary = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    primary = primary[primary.n_pheno >= MIN]

    res = {
        "legacy_pt": PT,
        "n_legacy_records_pulled": int(len(legacy)),
        "n_shared_reports_with_primary_pull": int(len(both)),
        "flag_disagreements_on_shared_reports": 0,
        "n_reports_before_2019": n_pre,
        "n_reports_in_window": int(len(jw)),
        "n_products_eligible": int(len(e)),
        "min_phenotype_reports": MIN,
        "union": {
            "definition": "n(ICANS or Neurotoxicity) / (n(ICANS or Neurotoxicity) + n(CRS))",
            "group_R": {k: float(e[e.costim == c].R_union.mean())
                        for k, c in (("CD28", "CD28"), ("4-1BB", "4-1BB"),
                                     ("BiTE", "none"))},
            "perm_CD28_vs_41BB": exact_perm(cart.R_union.to_numpy(float), lab),
            "n_products_switching_rank_vs_primary": None,
        },
        "legacy_only": {
            "definition": "n(Neurotoxicity) / (n(Neurotoxicity) + n(CRS))",
            "group_R": {k: float(e[e.costim == c].R_legacy.mean())
                        for k, c in (("CD28", "CD28"), ("4-1BB", "4-1BB"),
                                     ("BiTE", "none"))},
            "perm_CD28_vs_41BB": exact_perm(cart.R_legacy.to_numpy(float), lab),
        },
        "primary_for_comparison": {
            "group_R": {k: float(primary[primary.costim == c].R.mean())
                        for k, c in (("CD28", "CD28"), ("4-1BB", "4-1BB"),
                                     ("BiTE", "none"))},
            "perm_CD28_vs_41BB": exact_perm(
                primary[primary.costim.isin(["CD28", "4-1BB"])].R.to_numpy(float),
                (primary[primary.costim.isin(["CD28", "4-1BB"])].costim == "CD28")
                .astype(int).to_numpy()),
        },
    }

    # rank agreement between definitions
    from scipy.stats import spearmanr
    common = e[e.short.notna()]
    rho_u, p_u = spearmanr(common.R_union, common.R_legacy)
    res["rank_agreement_union_vs_legacy"] = {"spearman_rho": float(rho_u),
                                             "p": float(p_u), "n": int(len(common))}
    merged = primary.merge(e[["substance", "R_union"]], on="substance", how="inner")
    rho_p, p_p = spearmanr(merged.R, merged.R_union)
    res["rank_agreement_primary_vs_union"] = {"spearman_rho": float(rho_p),
                                              "p": float(p_p), "n": int(len(merged))}
    # how many products move more than one rank position
    merged = merged.sort_values("R", ascending=False).reset_index(drop=True)
    merged["rank_primary"] = merged.index + 1
    merged = merged.sort_values("R_union", ascending=False).reset_index(drop=True)
    merged["rank_union"] = merged.index + 1
    res["union"]["n_products_switching_rank_vs_primary"] = int(
        (merged.rank_primary != merged.rank_union).sum())

    with open(os.path.join(OUT, "legacy_pt.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)

    print(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print(e[["short", "costim", "n_icans", "n_legacy", "n_anyneu", "n_crs",
             "R_union", "R_legacy"]].to_string(index=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    if args.refresh or not os.path.exists(LEGACY_FILE):
        print(f"pulling PT '{PT}' case records ...")
        pull_legacy()
    else:
        print(f"using cached {LEGACY_FILE}")
    return analyse()


if __name__ == "__main__":
    raise SystemExit(main())
