# Supplementary Table S7. The partition recomputed under the pre-2018 coding convention

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
