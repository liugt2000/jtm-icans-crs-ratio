"""
Disproportionality analysis on report-level 2x2 tables.

Implements, per (substance, PT) cell:
  - ROR  and its lower 95% bound (log-normal, Haldane-corrected for zero cells)
  - EBGM and EB05: DuMouchel's multi-item gamma Poisson shrinker (two-component
    gamma mixture fitted by EM on the observed table, posterior mean + 5th pct)

Design notes
------------
* The 2x2 is built from margins: a = n_ij, row = n_i, col = n_j, total = N.
* EBGM hyperparameters are fitted on the cells of THIS table (31 substances x 16 PTs).
  That is an honest empirical-Bayes background for the current snapshot, not the full
  FAERS universe; the final manuscript refits with openEBGM on the complete table.
  A stability check over several initialisations is reported in out/ebgm_stability.csv.
* Zero cells are left as-is for EBGM (the prior shrinks them) and Haldane-corrected
  (+0.5) for ROR only, which is flagged in the output.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.special import gammaln

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")


# ----------------------------------------------------------------------------- 2x2
@dataclass
class Table:
    a: float   # drug & event
    b: float   # drug, not event
    c: float   # event, not drug
    d: float   # neither

    @classmethod
    def from_margins(cls, n_ij: float, n_i: float, n_j: float, n_tot: float) -> "Table":
        a = float(n_ij)
        b = float(n_i - n_ij)
        c = float(n_j - n_ij)
        d = float(n_tot - n_i - n_j + n_ij)
        return cls(max(a, 0), max(b, 0), max(c, 0), max(d, 0))


def ror(t: Table) -> tuple[float, float, float, bool]:
    """Reporting odds ratio with lower 95% bound. Haldane +0.5 only if a zero cell exists."""
    a, b, c, d = t.a, t.b, t.c, t.d
    corrected = min(a, b, c, d) == 0
    if corrected:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    est = (a * d) / (b * c) if b * c > 0 else np.inf
    se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    lo = float(np.exp(np.log(est) - 1.96 * se)) if np.isfinite(est) else np.inf
    hi = float(np.exp(np.log(est) + 1.96 * se)) if np.isfinite(est) else np.inf
    return float(est), lo, hi, corrected


# ------------------------------------------------------------------------- EBGM / MGPS
def _log_marginal(n: np.ndarray, e: np.ndarray, a: float, b: float) -> np.ndarray:
    """log P(n | a, b, e) for Poisson(e*lambda), lambda ~ Gamma(shape=a, rate=b)."""
    return (gammaln(n + a) - gammaln(a) - gammaln(n + 1)
            + a * np.log(b / (b + e)) + n * np.log(e / (b + e) + 1e-300))


def _neg_complete_ll(params: np.ndarray, n: np.ndarray, e: np.ndarray, w: np.ndarray) -> float:
    a, b = np.exp(params)
    return -float(np.sum(w * _log_marginal(n, e, a, b)))


def fit_mgps(n: np.ndarray, e: np.ndarray, pi1: float = 0.9,
             init=((0.25, 0.05), (1.0, 0.5)), n_iter: int = 200, tol: float = 1e-7):
    """EM fit of a two-component gamma mixture on (observed, expected) counts."""
    a1, b1 = init[0]
    a2, b2 = init[1]
    prev = -np.inf
    for _ in range(n_iter):
        l1 = _log_marginal(n, e, a1, b1)
        l2 = _log_marginal(n, e, a2, b2)
        m = np.logaddexp(np.log(pi1) + l1, np.log(1 - pi1) + l2)
        w1 = np.exp(np.log(pi1) + l1 - m)
        pi1 = float(np.clip(w1.mean(), 1e-4, 1 - 1e-4))
        r1 = optimize.minimize(_neg_complete_ll, np.log([a1, b1]), args=(n, e, w1),
                               method="Nelder-Mead",
                               options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
        r2 = optimize.minimize(_neg_complete_ll, np.log([a2, b2]), args=(n, e, 1 - w1),
                               method="Nelder-Mead",
                               options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
        a1, b1 = np.exp(r1.x)
        a2, b2 = np.exp(r2.x)
        ll = float(np.sum(m))
        if abs(ll - prev) < tol * max(1.0, abs(prev)):
            break
        prev = ll
    return dict(pi1=pi1, a1=a1, b1=b1, a2=a2, b2=b2, loglik=ll)


def mgps_posterior(n: np.ndarray, e: np.ndarray, hyp: dict):
    """Posterior mean (EBGM) and 5th percentile (EB05) of lambda for each cell."""
    l1 = _log_marginal(n, e, hyp["a1"], hyp["b1"])
    l2 = _log_marginal(n, e, hyp["a2"], hyp["b2"])
    m = np.logaddexp(np.log(hyp["pi1"]) + l1, np.log(1 - hyp["pi1"]) + l2)
    w1 = np.exp(np.log(hyp["pi1"]) + l1 - m)

    def mean(k):
        s1 = hyp["a1"] + n
        r1 = hyp["b1"] + e
        s2 = hyp["a2"] + n
        r2 = hyp["b2"] + e
        return w1 * s1 / r1 + (1 - w1) * s2 / r2

    def cdf(x, idx):
        f1 = stats.gamma.cdf(x, hyp["a1"] + n[idx], scale=1.0 / (hyp["b1"] + e[idx]))
        f2 = stats.gamma.cdf(x, hyp["a2"] + n[idx], scale=1.0 / (hyp["b2"] + e[idx]))
        return w1[idx] * f1 + (1 - w1[idx]) * f2

    mu_all = mean(None)
    eb05 = np.empty_like(n, dtype=float)
    for idx in range(len(n)):
        lo, hi = 0.0, max(10.0, float(20 * mu_all[idx] + 10))
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if cdf(mid, idx) < 0.05:
                lo = mid
            else:
                hi = mid
        eb05[idx] = 0.5 * (lo + hi)
    return mu_all, eb05, w1


# ---------------------------------------------------------------------------- driver
def main() -> int:
    df = pd.read_csv(os.path.join(OUT, "counts_long.csv"))
    # Normalise active-substance strings: FAERS carries a four-character suffix variant
    # (TECLISTAMAB vs TECLISTAMAB-CQYV, TARLATAMAB vs TARLATAMAB-DLLE, ...) for the same
    # biological. Counts must be SUMMED across the family, not merely relabelled, or the
    # product is split into two under-powered rows with two separate denominators.
    df["substance_raw"] = df["substance"]
    df["substance"] = df["substance"].str.replace(r"-[A-Z]{4}$", "", regex=True)
    df = (df.groupby(["substance", "pt", "event_label", "tier", "n_j", "N"], as_index=False)
            .agg(n_ij=("n_ij", "sum"), n_i=("n_i", "sum"),
                 n_variants=("substance_raw", "nunique")))
    rows = []
    for r in df.itertuples(index=False):
        t = Table.from_margins(r.n_ij, r.n_i, r.n_j, r.N)
        est, lo, hi, corr = ror(t)
        rows.append(dict(substance=r.substance, pt=r.pt, event_label=r.event_label,
                         tier=r.tier, a=t.a, n_i=r.n_i, n_j=r.n_j, N=r.N,
                         expected=r.n_i * r.n_j / r.N,
                         ror=est, ror025=lo, ror975=hi, ror_haldane=corr))
    sig = pd.DataFrame(rows)

    e = sig["expected"].to_numpy(dtype=float)
    n = sig["a"].to_numpy(dtype=float)
    keep = e > 0
    best = None
    stab = []
    inits = [((0.25, 0.05), (1.0, 0.5)), ((0.5, 0.2), (2.0, 1.0)),
             ((0.1, 0.02), (0.8, 0.4)), ((1.0, 0.5), (0.3, 0.1))]
    for i, init in enumerate(inits):
        hyp = fit_mgps(n[keep], e[keep], init=init)
        stab.append(dict(init=i, **hyp))
        if best is None or hyp["loglik"] > best["loglik"]:
            best = hyp
    pd.DataFrame(stab).to_csv(os.path.join(OUT, "ebgm_stability.csv"), index=False)

    ebgm = np.full(len(sig), np.nan)
    eb05 = np.full(len(sig), np.nan)
    w = np.full(len(sig), np.nan)
    ebgm[keep], eb05[keep], w[keep] = mgps_posterior(n[keep], e[keep], best)
    sig["ebgm"] = ebgm
    sig["eb05"] = eb05
    sig["ebgm_component1_weight"] = w

    sig = sig.sort_values(["event_label", "eb05"], ascending=[True, False])
    sig.to_csv(os.path.join(OUT, "signals.csv"), index=False)

    with open(os.path.join(OUT, "ebgm_hyperparameters.json"), "w", encoding="utf-8") as fh:
        import json
        json.dump(best, fh, indent=2)
    print(sig[["substance", "pt", "event_label", "a", "expected", "ror", "ror025", "ebgm", "eb05"]]
          .to_string(index=False, max_rows=40))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
