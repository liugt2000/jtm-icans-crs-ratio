"""Scoping probe: can the ordering be tested *within* FAERS strata?

The Discussion currently says country and reporter type are "not modelled". Both fields
are in the deposited extract, so that sentence is checkable. This script asks whether the
CD28-versus-4-1BB contrast survives inside each stratum, before any of it is written up.

Nothing here is a manuscript result yet; it writes to cache/scoping/ so the data registry
is untouched.
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
OUTDIR = os.path.join(HERE, "cache", "scoping")
os.makedirs(OUTDIR, exist_ok=True)


def load():
    subs = pd.read_csv(os.path.join(HERE, "config", "substances.csv"), encoding="utf-8-sig")
    subs["substance"] = subs["substance"].str.upper()
    subs = subs[subs.group.isin(["CAR-T", "BiTE"])].copy()
    recs = [json.loads(l) for l in open(os.path.join(HERE, "data", "cases_icans_crs.jsonl"),
                                        encoding="utf-8") if l.strip()]
    df = pd.DataFrame(recs)
    df["ver_i"] = pd.to_numeric(df["ver"], errors="coerce").fillna(0).astype(int)
    df = df.sort_values("ver_i").drop_duplicates("sid", keep="last").reset_index(drop=True)
    # the manuscript's analysis window: ICANS entered MedDRA in 2018, so 2019-01-01
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


def table(prod, subs):
    g = (prod.groupby("substance")
              .agg(n_icans=("icans", "sum"), n_crs=("crs", "sum"))
              .reset_index())
    g["n_pheno"] = g.n_icans + g.n_crs
    g["R"] = g.n_icans / g.n_pheno.replace(0, np.nan)
    return g.merge(subs[["substance", "short", "costim"]], on="substance", how="left")


def perm_p(cd, fb):
    """Exact one-sided permutation over all C(n,2) label assignments."""
    obs = np.mean(cd) - np.mean(fb)
    pool = np.concatenate([cd, fb])
    k = len(cd)
    hits = 0
    total = 0
    for idx in combinations(range(len(pool)), k):
        mask = np.zeros(len(pool), bool)
        mask[list(idx)] = True
        d = np.mean(pool[mask]) - np.mean(pool[~mask])
        total += 1
        if d >= obs - 1e-12:
            hits += 1
    return obs, hits / total, total


def report(name, prod, subs, log):
    t = table(prod, subs)
    elig = t[t.n_pheno >= MIN]
    cd = elig[elig.costim == "CD28"]
    fb = elig[elig.costim == "4-1BB"]
    rec = {"stratum": name, "n_reports": int(prod.sid.nunique()),
           "n_products_eligible": int(len(elig)),
           "n_CD28": int(len(cd)), "n_4-1BB": int(len(fb)),
           "mean_CD28": round(float(cd.R.mean()), 4) if len(cd) else None,
           "mean_4_1BB": round(float(fb.R.mean()), 4) if len(fb) else None}
    if len(cd) >= 2 and len(fb) >= 2:
        d, p, tot = perm_p(cd.R.to_numpy(), fb.R.to_numpy())
        rec.update({"delta": round(float(d), 4), "p_one_sided": round(float(p), 4),
                    "n_assignments": tot})
        # does the mean ordering still separate the two classes at the product level?
        rec["min_CD28"] = round(float(cd.R.min()), 4)
        rec["max_4_1BB"] = round(float(fb.R.max()), 4)
        rec["separates"] = bool(cd.R.min() > fb.R.max())
    else:
        rec.update({"delta": None, "p_one_sided": None, "separates": None})
    log.append(rec)
    print(f"{name:<22} rep={rec['n_reports']:>6}  elig={rec['n_products_eligible']}  "
          f"CD28={rec['mean_CD28']} 4-1BB={rec['mean_4_1BB']} "
          f"d={rec['delta']} p={rec['p_one_sided']} sep={rec['separates']}")
    return t


def main():
    df, subs = load()
    prod = explode(df, subs)
    log = []

    report("ALL", prod, subs, log)

    # country: US, JP, EU-pseudo-code + individual European codes pooled, rest
    us = prod[prod.country == "US"]
    jp = prod[prod.country == "JP"]
    eu_codes = {"EU", "FR", "ES", "DE", "IT", "NL", "BE", "SE", "DK", "AT", "PL",
                "IE", "PT", "FI", "NO", "CZ", "HU", "GR", "RO", "CH"}
    eu = prod[prod.country.isin(eu_codes)]
    nonus = prod[prod.country != "US"]
    for nm, sub in [("US", us), ("JP", jp), ("EU-codes", eu), ("non-US", nonus)]:
        report(nm, sub, subs, log)

    # reporter qualification: 1 physician, 2 pharmacist, 3 other HCP, 5 consumer
    for code, nm in [("1", "reporter=physician"), ("3", "reporter=other-HCP"),
                     ("5", "reporter=consumer")]:
        report(nm, prod[prod.qual.astype(str) == code], subs, log)

    # the two together: US + physician (the most homogeneous slice)
    report("US & physician", prod[(prod.country == "US") & (prod.qual.astype(str) == "1")],
           subs, log)

    json.dump(log, open(os.path.join(OUTDIR, "strata.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print("\nwrote", os.path.join(OUTDIR, "strata.json"))


if __name__ == "__main__":
    main()
