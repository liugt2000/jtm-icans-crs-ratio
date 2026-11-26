# Supplementary Table S12. Parameters of the mechanistic model, their ranges and their side

The model is a plausibility model, not a fitted one. Every range below is a stated order of magnitude, swept in full; nothing is estimated from the FAERS data, no objective function is minimized, and no goodness of fit is reported. The model's own R sits between 1.43 and 1.63 in the unsaturated regime — it is a ratio of two peak values with no units — and is not compared with the observed 0.15–0.39; only the ordering it produces and the structure of its sensitivity are used.

| Parameter | Meaning | Range swept | Side |
|---|---|---|---|
| r | net effector expansion rate, d⁻¹ | 0.10 – 1.20 | production |
| K | effector carrying capacity | 0.30 – 30.0 | production |
| d_A | effector contraction rate, d⁻¹ | 0.02 – 0.40 | production |
| k_C | cytokine production per effector unit | 0.10 – 20.0 | production |
| λ_C | cytokine clearance, d⁻¹ | 1.0 – 30.0 | production |
| A₀ | initial effector dose | 10⁻⁴ – 1.0 | production |
| k_E0 | base endothelial injury rate per unit cytokine | 0.05 – 1.00 | amplification |
| λ_E | endothelial recovery rate, d⁻¹ | 0.05 – 1.50 | amplification |
| β | costimulation gain on k_E (s = 1 CD28, 0.5 4-1BB, 0 BiTE) | 0.0 – 4.0 | amplification |
| E_max | endothelial injury ceiling | 2.0 – 30.0; held at 10⁴ (unsaturated) or 8 (saturating) | amplification |

Ranges are swept in two ways. One-at-a-time sweeps use 40 log-spaced points per parameter in both regimes, which gives the production-side maximum of 12% (unsaturated) and 68% (saturating) of relative change in R. The Sobol decomposition uses nine parameters with E_max held fixed, a base sample of 512 and 10,240 model evaluations per regime, and returns the first- and total-order indices quoted in Results. The nominal parameter set is not a calibration: it was chosen to place the model in the clinical regime — expansion over days, cytokine clearance over hours to days, endothelial recovery over days — and the sensitivity analysis is over the whole range, not around a privileged point.
