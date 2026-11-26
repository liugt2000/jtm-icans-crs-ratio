## 4.6 How this model fails

These are stated before the limitations, so that the boundary is declared by the authors rather
than discovered by a reader.

1. **It fails if the partition is set by severity rather than by module.** If CD28 products
   simply produce more severe disease on a single axis, any monotone severity marker would order
   the products the same way, and R would be a severity proxy. The dual-coded analysis, in which
   Δ falls from 0.087 to 0.058 when co-reported cases are removed, is consistent with that
   reading. The acuity proxy narrows the question without closing it. High-acuity ICANS is
   nearly twice as common in the CD28 arm, and the ordering survives, indeed widens to 0.247,
   when both phenotypes are restricted to their high-acuity terms. That excludes the version in
   which the ordering is an artifact of how mildly affected cases were coded. It does not
   exclude the version in which CD28 drives more severe disease on both axes at once. Only
   grading would, and FAERS does not carry it.

2. **It fails when the endothelial compartment saturates.** The invariance result is not a
   theorem. Below the ceiling, production-side parameters move R by at most 12%; at the nominal
   ceiling they move it by 68%. Any setting in which endothelial injury approaches its maximum,
   such as a high-dose, high-burden or rapid-expansion regimen, is one in which the partition
   becomes a dose readout. The model predicts where it breaks, and that prediction is its main
   use.

3. **It fails if the two modules are not the operative ones.** The modules were curated from
   prior biology. A partition driven by blood–brain barrier transporter expression or pericyte
   coverage rather than by the endothelial activation program would produce the same
   localization contrast. The curated module contains junctional and basement-membrane genes
   that correlate with both.

4. **It fails if reporting maturity is product-specific rather than generic.** The
   within-product drift (11/13 rising) is read as generic maturation of reporting. If each
   product's trajectory is instead driven by its own label changes, risk management plans and
   publication cycle, the drift is idiosyncratic and the year-stratified robustness (7/8
   positive) is weaker than it appears.

5. **It fails at the network layer for reasons that are arithmetic, not biological.** The
   proximity test had a minimum detectable ratio of 11.9× against an observed 1.34×. Nothing
   here distinguishes "no proximity" from "proximity below the detection floor", and no
   reanalysis of these modules can, because module size is fixed by prior knowledge. Only a
   larger module or a different observable can.

6. **It fails if costimulation is the wrong axis.** The ordering could be produced by any
   construct feature correlated with costimulation in the current market: manufacturing process,
   vector copy number, binder affinity, lymphodepletion intensity, or year of approval. With two
   CD28 products, both CD19 and both in lymphoma, none is separable.

####### Coarse-graining statement

*Scale.* The model is at the tissue scale: three lumped compartments (effector burden, systemic
cytokine exposure, endothelial injury) integrated over weeks, with no spatial or cellular
resolution. It makes no claim about which cytokine, receptor or endothelial cell type carries
the signal.

*What is deliberately ignored.* Antigen density and tumor burden enter only through the initial
condition A₀ and the carrying capacity K. Lymphodepletion, corticosteroid prophylaxis,
tocilizumab and prior therapy are absent. The compartments are well mixed, and endothelial
repair is a single first-order term. Immune infiltration of the brain parenchyma, the mechanism
most often invoked for ICANS, is not represented, because the model tests a vascular account and
would be unfalsifiable if it contained both.

*Why this is acceptable.* The model is used for one purpose: to identify which observable
quantities the partition depends on, and in which direction. A lumped three-variable system is
sufficient for that, and a detailed one would be worse, since its parameters cannot be
identified from the available data. Its predictions are therefore ordinal and structural,
covering which parameters matter and where invariance breaks, rather than quantitative. The one
quantitative statement the paper makes, the threshold rule with its resolution limit, comes from
the empirical distribution and not from the model. The leave-one-product-out test is what shows
that no quantitative forecast of an individual product is currently justified.

*What would require a finer model.* Any claim about dose, schedule, prophylaxis or combination
therapy, all of which act through production-side parameters that this model lumps together.
