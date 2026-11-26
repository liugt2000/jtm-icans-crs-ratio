"""
Minimal mechanistic model for the ICANS/CRS partition, and what it can be refuted by.

Model
-----
Three state variables:

    dA/dt = r*A*(1 - A/K) - dA*A            effector burden (CAR-T / engager)
    dC/dt = kC*A - lC*C                     systemic cytokine exposure   -> CRS
    dE/dt = kE*C*(1 - E/Emax) - lE*E        neurovascular endothelial injury -> ICANS

with the construct-level term carried on the endothelial gain

    kE = kE0 * (1 + beta * s)               s = costimulation strength
                                            CD28 = 1, 4-1BB = 0.5, BiTE = 0

The observable is the *partition*, not the magnitude:

    R = max_t E / max_t C

Analytic limit. If the endothelial compartment is slow relative to cytokine clearance
and far from its ceiling (E << Emax), E tracks kE*C/lE and

    R -> kE / lE

Every production-side parameter (r, K, dA, kC, lC, A0) cancels, because it rescales C
and E identically. That cancellation is the model's only non-trivial prediction: R
should be invariant to tumour burden, dose, expansion kinetics and cytokine clearance,
and therefore stable across calendar time and across products that differ only in those.

The ceiling term breaks the cancellation. This is measured, not assumed: the same sweep
is run with Emax far above the working range (unsaturated) and at the nominal value
(saturating), and the residual production-side variance is reported for both.

Outputs: out/model_invariance.json, out/model_sobol.json, out/model_beta.json,
         out/model_identity.csv
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")

DT = 0.05
T_END = 60.0

NOMINAL = dict(r=0.45, K=3.0, dA=0.09, kC=1.4, lC=6.0,
               kE0=0.22, lE=0.35, Emax=8.0, A0=0.01, beta=1.6, s=1.0)
UNSAT = dict(NOMINAL, Emax=1.0e4)

PRODUCTION = ["r", "K", "dA", "kC", "lC", "A0"]
AMPLIFICATION = ["kE0", "lE", "Emax", "beta"]

BOUNDS = {"r": (0.10, 1.20), "K": (0.30, 30.0), "dA": (0.02, 0.40),
          "kC": (0.10, 20.0), "lC": (1.0, 30.0), "A0": (1e-4, 1.0),
          "kE0": (0.05, 1.00), "lE": (0.05, 1.50), "Emax": (2.0, 30.0),
          "beta": (0.0, 4.0)}


def simulate(p: dict, n: int) -> tuple[np.ndarray, np.ndarray]:
    arr = {k: np.broadcast_to(np.asarray(p[k], dtype=float), (n,)).copy() for k in p}
    A, C, E = arr["A0"].copy(), np.zeros(n), np.zeros(n)
    Cmax, Emax_seen = np.zeros(n), np.zeros(n)

    def deriv(A, C, E):
        dA = arr["r"] * A * (1.0 - A / arr["K"]) - arr["dA"] * A
        dC = arr["kC"] * A - arr["lC"] * C
        kE = arr["kE0"] * (1.0 + arr["beta"] * arr["s"])
        dE = kE * C * (1.0 - E / arr["Emax"]) - arr["lE"] * E
        return dA, dC, dE

    for _ in range(int(round(T_END / DT))):
        k1 = deriv(A, C, E)
        k2 = deriv(A + 0.5 * DT * k1[0], C + 0.5 * DT * k1[1], E + 0.5 * DT * k1[2])
        k3 = deriv(A + 0.5 * DT * k2[0], C + 0.5 * DT * k2[1], E + 0.5 * DT * k2[2])
        k4 = deriv(A + DT * k3[0], C + DT * k3[1], E + DT * k3[2])
        A = np.maximum(A + DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), 0)
        C = np.maximum(C + DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]), 0)
        E = np.maximum(E + DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]), 0)
        np.maximum(Cmax, C, out=Cmax)
        np.maximum(Emax_seen, E, out=Emax_seen)
    return Cmax, Emax_seen


def ratio(p: dict, n: int | None = None) -> np.ndarray:
    if n is None:
        n = max(len(np.atleast_1d(p[k])) for k in p)
    Cm, Em = simulate(p, n)
    return Em / np.maximum(Cm, 1e-12)


def sweep(base: dict) -> dict:
    base_R = float(ratio(base)[0])
    out = {}
    for name, (lo, hi) in BOUNDS.items():
        vals = (np.linspace(lo, hi, 40) if lo == 0.0 else np.geomspace(lo, hi, 40))
        p = dict(base)
        p[name] = vals
        rs = ratio(p, n=40)
        out[name] = {"range": [lo, hi],
                     "R_min": float(rs.min()), "R_max": float(rs.max()),
                     "relative_change": float((rs.max() - rs.min()) / base_R),
                     "kind": "production" if name in PRODUCTION else "amplification"}
    out["_base_R"] = base_R
    prod = [v["relative_change"] for v in out.values()
            if isinstance(v, dict) and v["kind"] == "production"]
    amp = [v["relative_change"] for v in out.values()
           if isinstance(v, dict) and v["kind"] == "amplification"]
    out["_summary"] = {"production_max_rel_change": max(prod),
                       "amplification_max_rel_change": max(amp)}
    return out


def sobol(n_base: int = 512, seed: int = 20261116,
          fix: dict | None = None) -> dict:
    """Sobol decomposition. `fix` pins parameters that are being varied in a separate
    contrast (Emax), so that the two regimes differ only in the quantity under study."""
    fix = dict(fix or {})
    rng = np.random.default_rng(seed)
    names = [k for k in BOUNDS if k not in fix]
    A = rng.random((n_base, len(names)))
    B = rng.random((n_base, len(names)))
    for j, nm in enumerate(names):
        lo, hi = BOUNDS[nm]
        if lo == 0.0:
            A[:, j] = lo + (hi - lo) * A[:, j]
            B[:, j] = lo + (hi - lo) * B[:, j]
        else:
            A[:, j] = lo * (hi / lo) ** A[:, j]
            B[:, j] = lo * (hi / lo) ** B[:, j]

    def ev(mat):
        p = {nm: mat[:, j] for j, nm in enumerate(names)}
        p.update({k: np.full(len(mat), v) for k, v in fix.items()})
        p["s"] = np.ones(len(mat))
        return ratio(p, n=len(mat))

    yA, yB = ev(A), ev(B)
    var = float(np.var(np.concatenate([yA, yB])))
    si, sti = {}, {}
    for j, nm in enumerate(names):
        AB = A.copy(); AB[:, j] = B[:, j]
        BA = B.copy(); BA[:, j] = A[:, j]
        yAB, yBA = ev(AB), ev(BA)
        si[nm] = float(np.mean(yB * (yAB - yA)) / var)
        sti[nm] = float(0.5 * np.mean((yA - yAB) ** 2) / var)
    return {"n_base": n_base, "n_model_runs": 2 * n_base + 2 * n_base * len(names),
            "variance_of_R": var, "first_order": si, "total_order": sti,
            "production_total_order_sum":
                float(sum(sti[k] for k in PRODUCTION if k in sti)),
            "amplification_total_order_sum":
                float(sum(sti[k] for k in AMPLIFICATION if k in sti)),
            "fixed": fix}


def identity_sample(n: int = 2000, seed: int = 7) -> pd.DataFrame:
    """Sampled R against the analytic limit kE/lE, to show where they diverge."""
    rng = np.random.default_rng(seed)
    names = list(BOUNDS)
    mat = np.empty((n, len(names)))
    for j, nm in enumerate(names):
        lo, hi = BOUNDS[nm]
        u = rng.random(n)
        mat[:, j] = lo + (hi - lo) * u if lo == 0 else lo * (hi / lo) ** u
    p = {nm: mat[:, j] for j, nm in enumerate(names)}
    p["s"] = np.ones(n)
    R = ratio(p, n=n)
    kE = p["kE0"] * (1 + p["beta"] * p["s"])
    pred = kE / p["lE"]
    Cm, Em = simulate(p, n)
    return pd.DataFrame({"R_sim": R, "R_analytic": pred,
                         "E_peak": Em, "Emax": p["Emax"],
                         "saturation": Em / p["Emax"]})


def beta_inference(obs: dict) -> dict:
    s = {"CD28": 1.0, "4-1BB": 0.5, "BiTE": 0.0}
    out = {}
    for a, b in [("CD28", "4-1BB"), ("CD28", "BiTE"), ("4-1BB", "BiTE")]:
        rab = obs[a] / obs[b]
        if s[b] == 0.0:
            out[f"{a}_vs_{b}"] = {"ratio": rab, "beta": float((rab - 1.0) / s[a])}
        else:
            out[f"{a}_vs_{b}"] = {"ratio": rab,
                                  "beta": float((rab - 1.0) / (s[a] - s[b] * rab))}
    return out


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    inv_unsat = sweep(UNSAT)
    inv_nom = sweep(NOMINAL)
    json.dump({"unsaturated_Emax_1e4": inv_unsat, "nominal_Emax_8": inv_nom},
              open(os.path.join(OUT, "model_invariance.json"), "w", encoding="utf-8"),
              indent=2)

    sob_unsat = sobol(fix={"Emax": 1.0e4})
    sob_nom = sobol(fix={"Emax": 8.0})
    json.dump({"unsaturated": sob_unsat, "nominal": sob_nom},
              open(os.path.join(OUT, "model_sobol.json"), "w", encoding="utf-8"), indent=2)

    ident = identity_sample()
    ident.to_csv(os.path.join(OUT, "model_identity.csv"), index=False)

    t2 = pd.read_csv(os.path.join(OUT, "case_products.csv"))
    t2 = t2[(t2.n_pheno >= 20) & (t2.short != "afa-cel")]
    obs = {"CD28": float(t2.loc[t2.costim == "CD28", "R"].mean()),
           "4-1BB": float(t2.loc[t2.costim == "4-1BB", "R"].mean()),
           "BiTE": float(t2.loc[t2.costim == "none", "R"].mean())}
    bi = beta_inference(obs)
    json.dump({"observed_group_R": obs, "beta": bi},
              open(os.path.join(OUT, "model_beta.json"), "w", encoding="utf-8"), indent=2)

    print("unsaturated:", json.dumps(inv_unsat["_summary"], indent=2))
    print("nominal    :", json.dumps(inv_nom["_summary"], indent=2))
    for tag, s in [("unsaturated", sob_unsat), ("nominal", sob_nom)]:
        print(f"\nSobol {tag}: var(R)={s['variance_of_R']:.4g}")
        for k in s["first_order"]:
            print(f"  {k:6s} S1={s['first_order'][k]:+7.4f}  ST={s['total_order'][k]:7.4f}")
        print(f"  production ST sum={s['production_total_order_sum']:.4f}  "
              f"amplification ST sum={s['amplification_total_order_sum']:.4f}")
    print("\nidentity corr:", round(float(np.corrcoef(ident.R_sim, ident.R_analytic)[0, 1]), 4))
    print("observed group R:", {k: round(v, 4) for k, v in obs.items()})
    print("beta:", json.dumps({k: round(v["beta"], 3) for k, v in bi.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
