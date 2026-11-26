# Supplementary Table S10. The costimulation contrast inside reporting strata

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
