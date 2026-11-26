"""Is the paper's headline prediction actually decidable?

The prediction is "a future CD28 product shows R in [0.321, 0.415]; a value at or
below 0.320 refutes the account". Table 1 contains 4-1BB products at 0.320 (obe-cel)
and 0.318 (liso-cel), and CD28 products at 0.332 (axi-cel) and 0.390 (brexu-cel).
The gap between the highest 4-1BB value and the lowest CD28 value is therefore 0.012.
This script asks, for a product of true R, how many phenotype reports are needed before
a Wilson interval resolves the question - i.e. whether the decision rule is operational
or merely nominal.
"""
from __future__ import annotations

import json
import math

Z = 1.959963985
THRESHOLD = 0.320      # refutation boundary used in the manuscript
LOWER_WIN = 0.321
UPPER_WIN = 0.415


def wilson(p: float, n: int) -> tuple[float, float]:
    den = 1 + Z * Z / n
    ctr = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return ctr - half, ctr + half


def n_for(p: float, target: float, side: str, cap: int = 200000) -> int | None:
    """Smallest n whose Wilson bound crosses `target` on the requested side."""
    lo, hi = 1, cap
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        a, b = wilson(p, mid)
        ok = (b < target) if side == "upper" else (a > target)
        if ok:
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return best


obs = {"brexu-cel": (603, 1546), "axi-cel": (2159, 6500), "obe-cel": (8, 25),
       "liso-cel": (169, 531), "tisa-cel": (465, 2104), "cilta-cel": (387, 1310),
       "ide-cel": (195, 896)}


def r_of(k: int, n: int) -> float:
    return k / n


print("=== Do the 4-1BB products already straddle the window? ===")
covered = []
for name, (k, n) in obs.items():
    r = r_of(k, n)
    a, b = wilson(r, n)
    hits = a <= THRESHOLD <= b or a <= LOWER_WIN <= b or a <= UPPER_WIN <= b
    tag = "4-1BB" if name in ("obe-cel", "liso-cel", "tisa-cel", "cilta-cel", "ide-cel") else "CD28 "
    print(f"  {name:<10} {tag}  R={r:.3f}  CI {a:.3f}-{b:.3f}  covers 0.320={a <= THRESHOLD <= b}")
    if a <= THRESHOLD <= b:
        covered.append(name)

gap = 0.332 - 0.320
print(f"\n  discriminating gap (axi-cel - obe-cel) = {gap:.3f}")
print(f"  axi-cel CI lower bound                 = {0.321}  (= window lower bound)")

print("\n=== Report count needed for a decisive answer ===")
rows = []
for r_true in (0.150, 0.200, 0.250, 0.300, 0.320, 0.332, 0.360, 0.390, 0.420, 0.500):
    if r_true < THRESHOLD:
        n_need = n_for(r_true, THRESHOLD, "upper")
        verdict = "refutes"
    elif r_true > UPPER_WIN:
        n_need = n_for(r_true, UPPER_WIN, "lower")
        verdict = "beyond window (high)"
    else:
        n_need = n_for(r_true, THRESHOLD, "lower")
        verdict = "supports"
    rows.append({"true_R": r_true, "verdict": verdict, "min_reports": n_need})
    print(f"  true R={r_true:.3f}  -> {verdict:<22} min reports {n_need if n_need else '>200000 (undecidable)'}")

# the hardest case: a product whose true R sits just inside the window near the boundary
print("\n=== The boundary case ===")
for r_true in (0.325, 0.330, 0.335, 0.340):
    n_need = n_for(r_true, THRESHOLD, "lower")
    print(f"  true R={r_true:.3f}: needs {n_need if n_need else '>200000'} reports to be declared 'supports'")

print("\n  for reference, largest single product in Table 1 = 6,500 reports")

with open("out/prediction_decidability.json", "w", encoding="utf-8") as fh:
    json.dump({"threshold": THRESHOLD, "window": [LOWER_WIN, UPPER_WIN],
               "gap_to_4_1bb_ceiling": round(gap, 4),
               "products_whose_CI_covers_threshold": covered,
               "decidability": rows}, fh, indent=1)
print("\nwritten out/prediction_decidability.json")
