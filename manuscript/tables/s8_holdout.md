# Supplementary Table S8. Leave-one-product-out prediction of R

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
