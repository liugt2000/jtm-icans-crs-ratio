# Supplementary Table S11. Severity proxy: high-acuity reports and the contrast within them

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
