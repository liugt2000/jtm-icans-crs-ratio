# 6. Figure legends

**Figure 1. The ICANS/CRS partition orders by costimulatory architecture.**
(**A**) R = ICANS/(ICANS + CRS) for all fourteen products with at least twenty phenotype
reports as primary suspect, 2019 onward, with Wilson score intervals. Tick color
indicates costimulatory class; the number to the right is the number of phenotype
reports. (**B**) Fraction of each product's ICANS reports that also carry the CRS term,
on the same vertical order. The dashed line is the class-level value, 0.687. (**C**) R
recomputed after discarding every report that carries both terms (open symbols), against
the all-report value (filled symbols). The contrast survives in direction and loses
roughly one third of its magnitude; the one-sided exact permutation p rises from 0.048 to
0.200. (**D**) The same partition recomputed in EudraVigilance. Each point is one product,
plotted at its FAERS value against its European value; the dashed line is identity and
color follows the costimulatory class. Products on the line are reproduced exactly,
products below it sit lower in Europe. Spearman's ρ over the thirteen analyzable products
is 0.92 and 70 of 78 pairs are ordered identically; tarlatamab has no European substance
entry and is absent.

**Figure 2. Is the conclusion a property of the data, and what can one product settle?**
(**A**) The CD28-minus-4-1BB difference under nine analytic specifications. Filled
symbols are specifications in which the pre-specified one-sided exact p is below 0.05;
open symbols are those in which it is not. The direction never reverses. (**B**)
Leave-one-product-out prediction. Each product's partition is predicted from the other
products of its costimulatory class; the dashed line is identity. Points far from the
diagonal are products whose class does not forecast them. The class-based predictor
(mean absolute error 0.056) is no better than one blind to class (0.055), and the
observed grouping is not better than an arbitrary two-versus-five split of the same
products (exact p = 0.24). (**C**) The resolution limit of the prediction. The curve is
the number of reports a new CD28-costimulated product needs before its Wilson interval
clears the highest observed 4-1BB value (0.320) on one side or the other, as a function
of the product's true partition. The dashed horizontal line is the largest single-product
sample in the database (6,500); above it, no verdict is available. The shaded band
(0.309–0.331) is the set of true values that no sample size of that order can resolve,
and it contains the boundary on which the account rests.

**Figure 3. The level drifts; the ordering does not.**
(**A**) Annual phenotype volumes (bars, left axis) and the class-level partition (line,
right axis). Volume triples across the window. The 2019 value sits on the floor set by
the term's introduction into MedDRA in 2018. (**B**) Each product's R recomputed in the
first and second half of its own observation window; 11 of 13 rise, median +0.066. Tick
color indicates costimulatory class. (**C**) The CD28-minus-4-1BB difference recomputed
within each calendar year. It is positive in 7 of 8 years; the exception is 2019, when
each stratum contains a single product (annotated as the number of products per stratum).

**Figure 4. Two modules, opposite localizations.**
(**A**) Localization score L = log₂[(endothelial nCPM + 1)/(myeloid nCPM + 1)] for every
gene of the neurovascular and myeloid cytokine modules, and for the hepatocyte negative
control, from Human Protein Atlas single-nucleus brain data. Each point is one gene; the
black bar is the module mean and the dashed line the annotation- and expression-matched
null mean. The interaction contrast is annotated. (**B**) The same modules scored in an independent, non-cerebral endothelial-versus-
progenitor contrast (GSE195519, human dermal microvascular endothelium versus
induced endothelial progenitors), with the matched-null z for each. The neurovascular
module's endothelial character is not specific to the brain. (**C**) Induction of each module in
primary human brain microvascular endothelium challenged with TNF-α (GSE211439). The
myeloid module is induced more strongly than the neurovascular one, which is the finding
that rules out inducibility as evidence of specificity.

**Figure 5. The network test could not have detected the effect it was asked to find.**
(**A**) Null distribution of the CD28/4-1BB routing ratio over 1,000 matched gene-set
pairs, on a log scale. The observed ratio (1.34) is marked, together with the smallest
ratio this design could detect at 80% power and α = 0.05 (11.9). The shaded region is
where a difference would have been visible. (**B**) Module size available (19 genes)
against the size that would be required to resolve the observed ratio at the same power
(1,361 and 641 genes for the two targets).

**Figure 6. What the model constrains, and where it breaks.**
(**A**) Relative change in R when each parameter is swept over its stated range, in an
unsaturated regime (E_max = 10⁴, light bars) and at a nominal ceiling (E_max = 8, solid
bars). Production-side parameters are gray, amplification-side parameters blue. The
dashed line separates the two groups. (**B**) Saltelli–Sobol total-order indices for the
same parameters in the same two regimes; E_max is fixed within each run because it is the
quantity being contrasted. (**C**) Simulated R against the analytic limit k_E/λ_E over
2,000 random parameter draws, colored by how close the endothelial compartment comes to
its ceiling. Deviation from the identity line is the only route by which a production-side
parameter can reach the partition.
