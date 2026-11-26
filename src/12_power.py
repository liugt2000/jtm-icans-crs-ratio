"""
12_power.py -- how large would a difference have to be for this design to see it?

08_network_null_ratio.py shows that the observed 1.34x routing difference between the
CD28 and 4-1BB signalosomes sits at the middle of the null distribution (z = -0.04,
p = 0.26). The temptation is to call the hypothesis unsupported. That is the wrong
reading: the design has almost no resolving power, and the correct statement is a
power statement, which this file computes.

Method: the null distribution of log(mass ratio) is approximately normal with standard
deviation sigma. From out/network_null_ratio.json the 5th and 95th percentiles of the
ratio are 0.233 and 4.27, which give sigma = [ln(4.27) - ln(0.233)] / (2 * 1.645).

  minimum detectable ratio at alpha=0.05, power 0.80 = exp((1.96 + 0.84) * sigma)
  module size needed to resolve a given ratio r: sigma scales as 1/sqrt(k), so
      k_needed = k * (sigma / (ln(r) / 2.80))^2

Both numbers are reported because both are needed to say honestly whether the negative
result is a refutation or a failure of resolution.
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
Z_A, Z_B = 1.959964, 0.8416212
K = 19        # module size used in 08
OBS_RATIO = 1.34


def main() -> int:
    nr = json.load(open(os.path.join(OUT, "network_null_ratio.json"), encoding="utf-8"))
    res = {}
    for target, d in nr.items():
        if not isinstance(d, dict):
            continue
        q = d["q"]
        lo, hi = q["0.05"], q["0.95"]
        sigma = (math.log(hi) - math.log(lo)) / (2 * 1.645)
        mdr = math.exp((Z_A + Z_B) * sigma)
        need = K * (sigma / (math.log(OBS_RATIO) / (Z_A + Z_B))) ** 2
        res[target] = {
            "sigma_log_ratio": round(sigma, 3),
            "min_detectable_ratio_80pct_power": round(mdr, 2),
            "observed_ratio": d["observed_ratio"],
            "observed_below_mdr": bool(d["observed_ratio"] < mdr),
            "module_size_needed_to_resolve_observed": int(round(need)),
            "module_size_used": K,
        }
    out = {"null_file": "network_null_ratio.json", "assumptions":
           {"alpha": 0.05, "power": 0.80, "sd_from_quantiles": "5th/95th percentiles",
            "sigma_scaling": "1/sqrt(k)"},
           "by_target": res,
           "verdict": ("The contrast is not refuted; it is unresolvable at this module size. "
                       "Only differences above the minimum detectable ratio could have been "
                       "detected, and the observed difference is far below it.")}
    with open(os.path.join(OUT, "power_network.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    for t, v in res.items():
        print(f"{t:18s} sigma_log={v['sigma_log_ratio']:.2f} "
              f"MDR={v['min_detectable_ratio_80pct_power']:.1f}x  "
              f"observed={v['observed_ratio']:.2f}x  "
              f"k_needed~{v['module_size_needed_to_resolve_observed']} genes (used {K})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
