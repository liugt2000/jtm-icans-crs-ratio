# Additional file 1: Supplementary tables S1–S13

**Article title.** The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in
BCMA

**Contents.** S1 substance-key normalisation; S2 exposure-role and report-set sensitivity; S3
EBGM mixture hyperparameters; S4 quality gate on the induced-brain-endothelium dataset; S5 gene
modules and provenance; S6 random-walk-with-restart proximity for all ordered pairs; S7 the
partition under the pre-2018 coding convention; S8 leave-one-product-out prediction of R; S9 the
partition in EudraVigilance; S10 the costimulation contrast inside reporting strata; S11 the
severity proxy and the contrast within high-acuity reports; S12 parameters of the mechanistic
model; S13 positive control for the network null.

Each table is cited in the main text as *Additional file 1: Table Sn*. The numbering groups the
tables by what they support rather than by order of first mention: data preparation (S1–S3), the
endothelial quality gate (S4), modules and proximity (S5–S6), sensitivity and replication
(S7–S10), severity (S11), the model (S12) and the network null (S13). Tables are provided as
editable text rather than images so that every value can be copied out.

# Table S1. Suffix variants merged to a single substance key

Four-character FDA suffix codes are stripped before counting, so that one biologic is not split across two rows with two denominators.

| Variant as reported | Merged to | Modality |
|---|---|---|
| TECLISTAMAB-CQYV | teclistamab-cqyv | BiTE |
| TALQUETAMAB-TGVS | talquetamab-tgvs | BiTE |
| TARLATAMAB-DLLE | tarlatamab-dlle | BiTE |
| GLOFITAMAB-GXBM | glofitamab-gxbm | BiTE |
| EPCORITAMAB-BYSP | epcoritamab-bysp | BiTE |
| ELRANATAMAB-BCMM | elranatamab-bcmm | BiTE |

# Table S2. Exposure-role and report-set sensitivity

| Analysis | Δ | one-sided p |
|---|---|---|
| primary suspect only | 0.087 | 0.048 |
| any drug role | 0.089 | 0.048 |
| monotherapy reports only | 0.091 | 0.048 |
| single-phenotype reports only | 0.058 | 0.200 |

# Table S3. EBGM mixture hyperparameters

Two-component gamma-Poisson shrinker fitted by EM on the cells of the present table. Reported as secondary evidence; the primary endpoint does not depend on these values.

| Parameter | Value |
|---|---|
| pi1 | 0.8129 |
| a1 | 0.6605 |
| b1 | 0.1994 |
| a2 | 0.5842 |
| b2 | 0.003204 |
| loglik | -2272 |

# Table S4. Quality gate on the induced-brain-endothelium dataset

> GSE195519. Mean log₂ CPM per group. The iBMEC arm expresses the barrier genes *SLC2A1* and *OCLN* but not *CLDN5*, *PECAM1* or *VWF*, a pattern inconsistent with a differentiated endothelial monolayer; the HDMEC arm expresses all of them. The iBMEC samples were therefore excluded from all localization claims, because including them would have made the neurovascular module appear absent from brain endothelium.

| Gene | iBMEC | iPSC-EC | HDMEC | iPC |
|---|---|---|---|---|
| CLDN5 | 0.18 | 0.58 | 9.22 | 0.05 |
| CDH5 | 5.35 | 0.15 | 10.36 | 0.31 |
| PECAM1 | 0.13 | 0.06 | 10.32 | 0.16 |
| SLC2A1 | 9.05 | 7.87 | 5.53 | 8.40 |
| OCLN | 4.19 | 4.69 | 1.03 | 1.11 |
| VWF | 0.68 | 0.24 | 12.39 | 0.45 |
| KDR | 2.41 | 4.87 | 7.77 | 1.39 |
| ABCB1 | 0.95 | 0.89 | 4.83 | 0.94 |
| PDGFRB | 3.58 | 3.03 | 0.42 | 6.75 |
| RGS5 | 5.04 | 4.90 | 1.84 | 3.69 |
| DES | n.d. | n.d. | n.d. | n.d. |
| IL6 | n.d. | n.d. | n.d. | n.d. |
| CXCL8 | 0.87 | 0.22 | 6.73 | 3.09 |
| TNF | n.d. | n.d. | n.d. | n.d. |
| IL1B | n.d. | n.d. | n.d. | n.d. |
| CD14 | n.d. | n.d. | n.d. | n.d. |
| LYZ | n.d. | n.d. | n.d. | n.d. |

# Table S5. Gene modules


**COSTIM_41BB** (n = 19): BIRC2, BIRC3, IL2, MAP3K14, MAP3K7, MAPK14, MAPK8, MAPK9, NFKB1, NFKB2, RELA, RELB, TAB1, TAB2, TNFRSF9, TNFSF9, TRAF1, TRAF2, TRAF3


**COSTIM_CD28** (n = 26): AKT1, BCL10, CARD11, CD28, CD80, CD86, FYN, GRAP2, GRB2, IL2, LAT, LCK, LCP2, MALT1, NFATC1, NFATC2, NFKB1, PDPK1, PIK3CA, PIK3CD, PIK3R1, PLCG1, PRKCQ, RELA, VAV1, ZAP70

# Table S6. Random-walk-with-restart proximity, all pairs

α = 0.7, 2,000 degree-preserving rewiring permutations per statistic.

| From | To | RWR mass | null mean | z | fold | p enriched |
|---|---|---|---|---|---|---|
| CNS_VASCULAR | MYELOID_CYTOKINE | 0.0228 | 0.01937 | 0.519 | 1.177 | 0.286 |
| CNS_VASCULAR | HEPATOCYTE_NEGCTRL | 0.002439 | 0.002108 | 0.127 | 1.157 | 0.1565 |
| MYELOID_CYTOKINE | CNS_VASCULAR | 0.006988 | 0.01086 | -0.624 | 0.643 | 0.5825 |
| MYELOID_CYTOKINE | HEPATOCYTE_NEGCTRL | 0.001569 | 0.002168 | -0.203 | 0.724 | 0.2645 |
| HEPATOCYTE_NEGCTRL | CNS_VASCULAR | 0.009662 | 0.007574 | 0.326 | 1.276 | 0.1475 |
| HEPATOCYTE_NEGCTRL | MYELOID_CYTOKINE | 0.01836 | 0.016 | 0.297 | 1.148 | 0.23 |
| COSTIM_CD28 | CNS_VASCULAR | 0.007547 | 0.01107 | -0.48 | 0.681 | 0.4615 |
| COSTIM_CD28 | MYELOID_CYTOKINE | 0.04772 | 0.02339 | 2.499 | 2.04 | 0.0195 |
| COSTIM_CD28 | HEPATOCYTE_NEGCTRL | 0.000807 | 0.002185 | -0.405 | 0.369 | 0.8855 |
| COSTIM_41BB | CNS_VASCULAR | 0.005608 | 0.01083 | -0.639 | 0.518 | 0.801 |
| COSTIM_41BB | MYELOID_CYTOKINE | 0.05919 | 0.02307 | 3.103 | 2.565 | 0.008 |
| COSTIM_41BB | HEPATOCYTE_NEGCTRL | 0.000896 | 0.002309 | -0.319 | 0.388 | 0.748 |

# Table S7. The partition recomputed under the pre-2018 coding convention

The primary phenotype is the preferred term introduced in MedDRA 21.0 (2018). A reviewer is entitled to ask whether the ordering is a property of the biology or of a term that exists only for the later part of the products' market lives. Two alternative numerators are used, both with the same CRS denominator: *R (union)* counts reports carrying either the modern term or the legacy term, and *R (legacy only)* uses the legacy term alone, which is what the analysis would have produced before 2018.

| Product | Class | ICANS | Neurotoxicity | Any neurotoxicity | CRS | R (union) | 95% CI | R (legacy only) |
|---|---|---|---|---|---|---|---|---|
| brexu-cel | CD28 | 603 | 205 | 781 | 943 | 0.453 | 0.430–0.477 | 0.179 |
| liso-cel | 4-1BB | 169 | 108 | 276 | 362 | 0.433 | 0.395–0.471 | 0.230 |
| axi-cel | CD28 | 2159 | 1175 | 3239 | 4341 | 0.427 | 0.416–0.438 | 0.213 |
| blina | BiTE | 239 | 402 | 637 | 962 | 0.398 | 0.375–0.423 | 0.295 |
| cilta-cel | 4-1BB | 387 | 221 | 573 | 923 | 0.383 | 0.359–0.408 | 0.193 |
| obe-cel | 4-1BB | 8 | 2 | 9 | 17 | 0.346 | 0.194–0.538 | 0.105 |
| tisa-cel | 4-1BB | 465 | 385 | 813 | 1639 | 0.332 | 0.313–0.350 | 0.190 |
| teclistamab | BiTE | 342 | 55 | 383 | 912 | 0.296 | 0.272–0.321 | 0.057 |
| tarlatamab | BiTE | 377 | 17 | 393 | 1022 | 0.278 | 0.255–0.302 | 0.016 |
| talquetamab | BiTE | 188 | 24 | 205 | 545 | 0.273 | 0.243–0.306 | 0.042 |
| ide-cel | 4-1BB | 195 | 76 | 260 | 701 | 0.271 | 0.243–0.300 | 0.098 |
| elranatamab | BiTE | 134 | 17 | 146 | 411 | 0.262 | 0.227–0.300 | 0.040 |
| epcoritamab | BiTE | 210 | 14 | 222 | 1076 | 0.171 | 0.152–0.192 | 0.013 |
| glofitamab | BiTE | 152 | 9 | 160 | 861 | 0.157 | 0.136–0.180 | 0.010 |

Exact permutation of the CD28-versus-4-1BB contrast under each definition (2 versus 5 products, all C(7,2) = 21 assignments enumerated):

| Definition | Δ | one-sided p | two-sided p |
|---|---|---|---|
| Primary (ICANS only) | +0.087 | 0.048 | 0.095 |
| R (union) | +0.087 | 0.095 | 0.190 |
| R (legacy only) | +0.033 | 0.333 | 0.667 |

Rank agreement between the primary and union definitions: Spearman ρ = 0.76 (p = 0.0015, n = 14); 9 of those products change rank position between the two definitions.

> 17,537 legacy-term records were retrieved independently and merged with the primary pull on `safetyreportid`; on the 1,909 reports present in both, the two extractions agree on every phenotype flag, so the merge introduces no inconsistency.

# Table S8. Leave-one-product-out prediction of R

Each product's partition is predicted from the other products of the same costimulatory class, and compared with a predictor that uses all other products regardless of class. If the class label carried a usable quantitative rule, the class-based prediction would be the better of the two.

| Product | Class | Phenotype reports | R observed | R predicted | Residual | Donors |
|---|---|---|---|---|---|---|
| brexu-cel | CD28 | 1546 | 0.390 | 0.332 | 0.058 | 1 |
| axi-cel | CD28 | 6500 | 0.332 | 0.390 | -0.058 | 1 |
| obe-cel | 4-1BB | 25 | 0.320 | 0.263 | 0.057 | 4 |
| liso-cel | 4-1BB | 531 | 0.318 | 0.264 | 0.055 | 4 |
| cilta-cel | 4-1BB | 1310 | 0.295 | 0.269 | 0.026 | 4 |
| tisa-cel | 4-1BB | 2104 | 0.221 | 0.288 | -0.067 | 4 |
| ide-cel | 4-1BB | 896 | 0.218 | 0.289 | -0.071 | 4 |

Mean absolute error: **0.056** for the class-based predictor, **0.054** for the class-blind predictor (relative change -2.6%). Median absolute error 0.058; largest 0.071; 1 of 7 products predicted within 0.05.

The difference is then tested against all 21 alternative ways of labelling two of the seven products as CD28-costimulated: the observed grouping is not better than chance at predicting held-out values (exact p = 0.24, attainable minimum 0.048). The conclusion is that the class effect is an ordering, not a level predictor.

> the CD28 class contains two products, so its leave-one-out prediction rests on a single donor and its error is not an independent estimate of generalisation within that class.

# Table S9. The partition in EudraVigilance

Case counts returned by the EudraVigilance data analysis system for each substance, restricted to the two phenotype preferred terms, and the resulting R = ICANS/(ICANS+CRS). R(FAERS) is the corresponding value from Table 1. Products with fewer than 20 phenotype reports in EV are listed but not analyzed.

| Product | Modality | Costimulation | EV total ICSRs | ICANS | CRS | R(EV) | 95% CI | R(FAERS) | Δ |
|---|---|---|---|---|---|---|---|---|---|
| brexu-cel | CAR-T | CD28 | 1,371 | 536 | 800 | 0.401 | 0.375–0.428 | 0.390 | +0.011 |
| axi-cel | CAR-T | CD28 | 7,730 | 2,312 | 4,671 | 0.331 | 0.320–0.342 | 0.332 | −0.001 |
| liso-cel | CAR-T | 4-1BB | 562 | 110 | 305 | 0.265 | 0.225–0.310 | 0.318 | −0.053 |
| obe-cel | CAR-T | 4-1BB | 97 | 8 | 23 | 0.258 | 0.137–0.432 | 0.320 | −0.062 |
| cilta-cel | CAR-T | 4-1BB | 2,539 | 166 | 518 | 0.243 | 0.212–0.276 | 0.295 | −0.052 |
| talquetamab | BiTE | — | 1,072 | 88 | 301 | 0.226 | 0.187–0.270 | 0.256 | −0.030 |
| teclistamab | BiTE | — | 3,029 | 179 | 619 | 0.224 | 0.197–0.255 | 0.273 | −0.049 |
| tisa-cel | CAR-T | 4-1BB | 3,344 | 432 | 1,684 | 0.204 | 0.188–0.222 | 0.221 | −0.017 |
| epcoritamab | BiTE | — | 2,719 | 291 | 1,178 | 0.198 | 0.179–0.219 | 0.163 | +0.035 |
| blina | BiTE | — | 6,740 | 305 | 1,521 | 0.167 | 0.151–0.185 | 0.199 | −0.032 |
| elranatamab | BiTE | — | 2,411 | 155 | 836 | 0.156 | 0.135–0.180 | 0.246 | −0.090 |
| ide-cel | CAR-T | 4-1BB | 1,005 | 126 | 681 | 0.156 | 0.133–0.183 | 0.218 | −0.062 |
| glofitamab | BiTE | — | 1,658 | 93 | 687 | 0.119 | 0.098–0.144 | 0.150 | −0.031 |

Spearman ρ between R(FAERS) and R(EV) over the 13 analyzable products: **0.923**; 70 of 78 pairs ordered the same way.

Costimulation test in EV over 7 resolvable CAR-T products (all 21 label assignments enumerated): Δ = +0.141, one-sided p = 0.048, two-sided p = 0.095 (attainable minimum 0.048).

# Table S10. The costimulation contrast inside reporting strata

Same endpoint, same eligibility rule (>= 20 phenotype reports) and same exact permutation test as Table 1 and Figure 1, recomputed on subsets of the FAERS extract defined by reporting country and by reporter qualification. *Separation* means the lowest CD28 product exceeds the highest 4-1BB product; the one-sided p can only reach its floor 1/C(n,2) when separation holds, so the two columns carry the same information and are both shown. rho is the Spearman correlation of product-level R against the all-report value, over the products eligible in that stratum.

| Stratum | Reports | Products | n CD28 | n 4-1BB | Mean R CD28 | Mean R 4-1BB | Δ | One-sided p | Separation | ρ vs all |
|---|---|---|---|---|---|---|---|---|---|---|
| All reports | 16,122 | 14 | 2 | 5 | 0.361 | 0.274 | +0.087 | 0.048 | yes | 1.000 |
| United States | 8,318 | 14 | 2 | 5 | 0.363 | 0.272 | +0.091 | 0.095 | no | 0.802 |
| Europe | 4,302 | 13 | 2 | 4 | 0.380 | 0.216 | +0.164 | 0.067 | yes | 0.448 |
| Japan | 1,972 | 9 | 1 | 3 | 0.305 | 0.228 | not testable | not testable | not testable | not testable |
| Non-US | 7,804 | 13 | 2 | 4 | 0.355 | 0.241 | +0.114 | 0.067 | yes | 0.808 |
| Physician | 7,056 | 13 | 2 | 4 | 0.364 | 0.261 | +0.103 | 0.133 | no | 0.967 |
| Other health professional | 6,838 | 13 | 2 | 4 | 0.361 | 0.276 | +0.085 | 0.067 | yes | 0.912 |
| Consumer | 861 | 12 | 2 | 4 | 0.381 | 0.241 | +0.140 | 0.200 | no | 0.734 |
| US, physician only | 2,136 | 13 | 2 | 4 | 0.334 | 0.261 | +0.073 | 0.200 | no | 0.687 |

Direction is positive in 8 of the 8 testable strata; perfect separation survives in 4. Japan is not testable because only one CD28 product reaches the eligibility threshold there. Strata are nested rather than independent (the United States is a subset of all reports, non-US its complement), so these p values are not a testing family and no multiplicity adjustment is applied to them.

# Table S11. Severity proxy: high-acuity reports and the contrast within them

FAERS records ICANS as one preferred term with no grade, so the primary endpoint cannot separate mild from severe disease. The `serious` flag does not help: 20,466 of 20,732 reports (98.7%) are flagged serious. A term-level proxy was therefore fixed before this contrast was computed. A report is **high-acuity for ICANS** if it carries encephalopathy, depressed level of consciousness, coma, brain edema, cerebral edema, seizure, status epilepticus, hemiparesis, paraparesis, quadriparesis, quadriplegia or raised intracranial pressure; **for CRS** if it carries shock, septic shock, distributive shock, circulatory collapse, respiratory failure, acute respiratory failure, capillary leak syndrome, hemophagocytic lymphohistiocytosis, macrophage activation syndrome or multiple organ dysfunction. Mild terms (*Confusional state*, *Somnolence*, *Pyrexia*, *Hypotension*, *Hypoxia*) are excluded on purpose, so the proxy is conservative: it identifies the grade 3–4 end and does not grade. **R_hi** is R recomputed with both phenotypes restricted to these terms; products with fewer than 20 high-acuity reports are ineligible for it, which is the primary eligibility rule applied to a smaller denominator.

**Panel A. Products.**

| Product | Class | R | ICANS reports | high-acuity ICANS | share (%) | 95% CI of share | R_hi | high-acuity reports |
|---|---|---:|---:|---:|---:|---|---:|---:|
| brexu-cel | CD28 | 0.390 | 603 | 77 | 12.8 | 10.3–15.7 | 0.470 | 164 |
| axi-cel | CD28 | 0.332 | 2,159 | 245 | 11.3 | 10.1–12.8 | 0.485 | 505 |
| obe-cel | 4-1BB | 0.320 | 8 | 0 | 0.0 | 0.0–32.4 | — | 3 |
| liso-cel | 4-1BB | 0.318 | 169 | 19 | 11.2 | 7.3–16.9 | 0.404 | 47 |
| cilta-cel | 4-1BB | 0.295 | 387 | 17 | 4.4 | 2.8–6.9 | 0.150 | 113 |
| teclistamab | bispecific | 0.273 | 342 | 12 | 3.5 | 2.0–6.0 | 0.235 | 51 |
| tarlatamab | bispecific | 0.269 | 377 | 3 | 0.8 | 0.3–2.3 | 0.086 | 35 |
| talquetamab | bispecific | 0.256 | 188 | 8 | 4.3 | 2.2–8.2 | 0.381 | 21 |
| elranatamab | bispecific | 0.246 | 134 | 4 | 3.0 | 1.2–7.4 | 0.174 | 23 |
| tisa-cel | 4-1BB | 0.221 | 465 | 56 | 12.0 | 9.4–15.3 | 0.197 | 284 |
| ide-cel | 4-1BB | 0.218 | 195 | 7 | 3.6 | 1.8–7.2 | 0.171 | 41 |
| blina | bispecific | 0.199 | 239 | 19 | 8.0 | 5.1–12.1 | 0.260 | 73 |
| epcoritamab | bispecific | 0.163 | 210 | 21 | 10.0 | 6.6–14.8 | 0.273 | 77 |
| glofitamab | bispecific | 0.150 | 152 | 3 | 2.0 | 0.7–5.6 | 0.064 | 47 |

**Panel B. The costimulation contrast on each endpoint.**

| Endpoint | Products (CD28 / 4-1BB) | mean CD28 | mean 4-1BB | Δ | assignments | one-sided p | separation |
|---|---|---:|---:|---:|---:|---:|---|
| R (primary) | 2 / 5 | 0.361 | 0.274 | +0.087 | 21 | 0.048 | yes |
| share of ICANS reports that are high-acuity | 2 / 5 | 12.1% | 6.3% | +5.8 pp | 21 | 0.095 | no |
| R_hi | 2 / 4 | 0.477 | 0.231 | +0.247 | 15 | 0.067 | yes |

The primary endpoint is reproduced here as a check that this script counts the same reports as the main pipeline: 0.361, 0.274, Δ = +0.087, p = 0.048. The last row is the informative one. Restricting both phenotypes to their high-acuity forms does not dissolve the ordering; it widens it, and separation holds (0.470 against 0.404). The middle row shows why that is not a contradiction: CD28 ICANS is more often high-acuity in the first place, so the two syndromes are coupled at the severe end rather than independent. Both endpoints are descriptive, not confirmatory (Methods, *Multiplicity*).

# Table S12. Parameters of the mechanistic model, their ranges and their side

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

# Table S13. Positive control: the same null applied to pairs whose relatedness is fixed externally

Every network claim in this paper rests on one null, so the null was run on pairs whose relatedness is curated elsewhere and cannot depend on any choice of ours. The statistic is the one behind the per-module results: random-walk-with-restart mass (α = 0.7) from a uniform seed on the first set, summed over the second, with the second set held fixed and only the first replaced by 1,000 degree-decile-matched random sets. Two folds are given. **fold, null mean** divides by the mean of the null draws and is the definition used in Table S6. **fold, null median** divides by their median. For these targets the null is strongly right-skewed (coefficient of variation 2.5, against 0.4–0.7 for the per-module targets), because a 19-gene seed set that happens to make several direct contacts deposits an order of magnitude more mass than one that makes none. The mean therefore sits above the bulk of the draws, and the mean-based fold of an unrelated pair falls below 1. Against the median an unrelated pair centres on 0.94, which is what a calibration claim needs; against the mean the resolution threshold is nearly the same for every pair, which is what a detection claim needs. **p** is the fraction of the 1,000 draws at or above the observed value.

The code path is the published one. Pointed at three module pairs whose folds appear in Table S6, it reproduces the observed masses exactly (to six decimal places) and the folds to within 1.7% (2.07 against 2.04, 2.61 against 2.56), which is the sampling error of a 2,000-draw null.

**Calibration.** The pairs with no reason to be proximal behave as they should. All 13 give a median fold over the null median of 0.94 (IQR 0.84–1.35) and a median p of 0.59. Of the 10 random pairs, 2 reach p < 0.05, and none of the three curated negative controls does (p = 0.653, 0.909, 0.972). Decile matching leaves an order of magnitude of degree spread inside the top stratum, so a set of near-hub genes can outperform its own null; that is the residual miscalibration, and it runs in the anti-conservative direction.

**Resolution.** Of the 43 distinct related pairs, 12 reach p < 0.05: 11 of the 40 pathway halves and one complex, the ribosomal pair at 25.6-fold. In fold units the threshold is sharp. No related pair below 9.3-fold reached p < 0.05, and every pair at or above 10.5-fold did. The analytic inversion in the main text, which asserted 11.9-fold from the quantiles of the ratio null, is therefore 13–28% above a floor that can be measured directly on pairs whose answer is known.

**Panel A. Pairs known to be related, by fold.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| complex | Ribosome: 40S (RPS) vs 60S (RPL) | 19/19 | 25.62 | 55.80 | < 0.001 |
| pathway half | TNFR2 non-canonical NF-kB pathway (R-HSA-5668541) | 19/19 | 21.80 | 74.80 | < 0.001 |
| pathway half | Visual phototransduction (R-HSA-2187338) | 19/19 | 20.52 | 212.20 | 0.001 |
| pathway half | Semaphorin interactions (R-HSA-373755) | 19/19 | 16.01 | 62.70 | 0.001 |
| pathway half | DDX58/IFIH1-mediated induction of interferon-alpha/beta (R-HSA-168928) | 19/19 | 15.23 | 74.10 | 0.003 |
| pathway half | Degradation of the extracellular matrix (R-HSA-1474228) | 19/19 | 15.09 | 110.50 | 0.004 |
| pathway half | Fcgamma receptor (FCGR) dependent phagocytosis (R-HSA-2029480) | 19/19 | 14.40 | 51.90 | 0.001 |
| pathway half | SUMOylation of DNA damage response and repair proteins (R-HSA-3108214) | 19/19 | 14.24 | 43.60 | 0.003 |
| pathway half | Peptide hormone metabolism (R-HSA-2980736) | 19/19 | 12.16 | 76.20 | 0.018 |
| pathway half | Signaling by NOTCH1 (R-HSA-1980143) | 19/19 | 11.84 | 31.70 | 0.002 |
| pathway half | Regulation of PD-L1(CD274) transcription (R-HSA-9909649) | 19/19 | 10.91 | 38.00 | 0.006 |
| pathway half | SARS-CoV-1-host interactions (R-HSA-9692914) | 19/19 | 10.55 | 79.40 | < 0.001 |
| pathway half | Cytosolic sensors of pathogen-associated DNA (R-HSA-1834949) | 19/19 | 9.33 | 29.40 | 0.050 |
| pathway half | L13a-mediated translational silencing of Ceruloplasmin expression (R-HSA-156827) | 19/19 | 7.38 | 148.30 | 0.107 |
| pathway half | Late Phase of HIV Life Cycle (R-HSA-162599) | 19/19 | 7.29 | 37.70 | 0.057 |
| pathway half | Interferon gamma signaling (R-HSA-877300) | 19/19 | 6.82 | 29.10 | 0.055 |
| pathway half | Respiratory Syncytial Virus Infection Pathway (R-HSA-9820952) | 19/19 | 6.56 | 64.50 | 0.085 |
| pathway half | Ribosome Quality Control (RQC) complex extracts and degrades nascent peptide (R-HSA-9954709) | 19/19 | 5.66 | 161.10 | 0.120 |
| complex | 19S proteasome: ATPase (PSMC) vs base (PSMD) | 6/14 | 5.48 | 55.60 | 0.068 |
| pathway half | Diseases of programmed cell death (R-HSA-9645723) | 19/19 | 5.21 | 17.50 | 0.061 |
| pathway half | Fatty acid metabolism (R-HSA-8978868) | 19/19 | 5.20 | 82.20 | 0.088 |
| complex | 20S proteasome: alpha (PSMA) vs beta (PSMB) | 8/11 | 5.09 | 50.60 | 0.071 |
| pathway half | Ca2+ pathway (R-HSA-4086398) | 19/19 | 5.02 | 10.20 | 0.078 |
| pathway half | Gastrulation (R-HSA-9758941) | 19/19 | 5.01 | 26.70 | 0.075 |
| pathway half | p75 NTR receptor-mediated signalling (R-HSA-193704) | 19/19 | 5.01 | 20.80 | 0.062 |
| pathway half | Glycolysis (R-HSA-70171) | 19/19 | 4.75 | 19.20 | 0.078 |
| pathway half | Opioid Signalling (R-HSA-111885) | 19/19 | 4.35 | 9.80 | 0.079 |
| pathway half | Positive epigenetic regulation of rRNA expression (R-HSA-5250913) | 19/19 | 3.97 | 28.80 | 0.086 |
| pathway half | RAC2 GTPase cycle (R-HSA-9013404) | 19/19 | 3.93 | 19.50 | 0.063 |
| pathway half | Activation of anterior HOX genes in hindbrain development during early embryogenesis (R-HSA-5617472) | 19/19 | 3.88 | 31.90 | 0.091 |
| pathway half | Senescence-Associated Secretory Phenotype (SASP) (R-HSA-2559582) | 19/19 | 3.83 | 6.70 | 0.079 |
| pathway half | Signaling by FGFR in disease (R-HSA-1226099) | 19/19 | 3.74 | 11.40 | 0.118 |
| pathway half | Amyloid fiber formation (R-HSA-977225) | 19/19 | 3.70 | 24.90 | 0.075 |
| pathway half | Interleukin-1 signaling (R-HSA-9020702) | 19/19 | 3.17 | 9.10 | 0.107 |
| pathway half | DNA Double Strand Break Response (R-HSA-5693606) | 19/19 | 2.91 | 10.50 | 0.059 |
| pathway half | Regulation of TP53 Activity through Phosphorylation (R-HSA-6804756) | 19/19 | 2.50 | 10.80 | 0.080 |
| pathway half | Cellular responses to mechanical stimuli (R-HSA-9855142) | 19/19 | 1.97 | 7.10 | 0.111 |
| pathway half | Interleukin-4 and Interleukin-13 signaling (R-HSA-6785807) | 19/19 | 1.53 | 4.60 | 0.128 |
| pathway half | COPI-dependent Golgi-to-ER retrograde traffic (R-HSA-6811434) | 19/19 | 0.73 | 9.00 | 0.112 |
| pathway half | Unfolded Protein Response (UPR) (R-HSA-381119) | 19/19 | 0.40 | 2.90 | 0.107 |
| pathway half | Amplification of signal from the kinetochores (R-HSA-141424) | 19/19 | 0.35 | 2.60 | 0.098 |
| pathway half | Cargo recognition for clathrin-mediated endocytosis (R-HSA-8856825) | 19/19 | 0.22 | 1.20 | 0.350 |
| pathway half | SLC-mediated transmembrane transport (R-HSA-425407) | 19/19 | 0.05 | 2.30 | 0.239 |

**Panel B. Pairs with no reason to be proximal.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| negative control | HEPATOCYTE_NEGCTRL vs half of Opioid Signalling (R-HSA-111885) | 15/19 | 0.64 | 0.90 | 0.653 |
| negative control | HEPATOCYTE_NEGCTRL vs half of Signaling by FGFR in disease (R-HSA-1226099) | 15/19 | 0.41 | 0.80 | 0.909 |
| negative control | HEPATOCYTE_NEGCTRL vs half of Amplification of signal from the kinetochores (R-HSA-141424) | 15/19 | 0.19 | 0.60 | 0.972 |
| random pair | independent random pair | 19/19 | 0.75 | 1.40 | 0.176 |
| random pair | independent random pair | 19/19 | 0.52 | 0.90 | 0.590 |
| random pair | independent random pair | 19/19 | 12.56 | 40.30 | 0.022 |
| random pair | independent random pair | 19/19 | 0.23 | 0.80 | 0.946 |
| random pair | independent random pair | 19/19 | 0.45 | 0.80 | 0.858 |
| random pair | independent random pair | 19/19 | 4.27 | 10.30 | 0.038 |
| random pair | independent random pair | 19/19 | 0.37 | 0.90 | 0.708 |
| random pair | independent random pair | 19/19 | 0.42 | 1.30 | 0.308 |
| random pair | independent random pair | 19/19 | 0.58 | 1.40 | 0.281 |
| random pair | independent random pair | 19/19 | 0.39 | 1.00 | 0.460 |

**Panel C. Second independent split of six pathways.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| pathway half, 2nd split | Opioid Signalling (R-HSA-111885) | 19/19 | 3.63 | 7.70 | 0.091 |
| pathway half, 2nd split | Signaling by FGFR in disease (R-HSA-1226099) | 19/19 | 4.15 | 9.10 | 0.122 |
| pathway half, 2nd split | Amplification of signal from the kinetochores (R-HSA-141424) | 19/19 | 0.43 | 2.60 | 0.074 |
| pathway half, 2nd split | Degradation of the extracellular matrix (R-HSA-1474228) | 19/19 | 15.20 | 113.70 | 0.004 |
| pathway half, 2nd split | L13a-mediated translational silencing of Ceruloplasmin expression (R-HSA-156827) | 19/19 | 6.25 | 146.10 | 0.103 |
| pathway half, 2nd split | Late Phase of HIV Life Cycle (R-HSA-162599) | 19/19 | 5.60 | 35.40 | 0.070 |

The second split in Panel C was drawn independently of the first. The two splits agree to a correlation of 0.999 and a largest relative difference of 2.2%, so the fold is a property of the pathway rather than of where the cut fell.
