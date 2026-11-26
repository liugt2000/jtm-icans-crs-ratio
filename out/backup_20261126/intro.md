# Background

Chimeric antigen receptor T cells and bispecific engagers have produced durable remissions in
B-cell and plasma-cell malignancies [1,2]. They also share a toxicity signature that has
resisted explanation. Cytokine release syndrome (CRS) is a systemic inflammatory response driven
by myeloid cytokine release, graded by hypotension, hypoxia and organ dysfunction [3–5]. Immune
effector cell-associated neurotoxicity syndrome (ICANS) is a neurological syndrome, graded by
aphasia, altered mentation, seizures and cerebral edema, and is only weakly predicted by the
severity of the CRS that usually precedes it [4,5]. The two co-occur often enough to be mistaken
for one process, and dissociate often enough to be modeled as two.

Clinical writing has treated the dissociation as a property of the patient. Pharmacovigilance
has treated it as a property of the report. Neither asks the question a mechanistic model can
answer: if the same construct triggers both syndromes, what sets the split between them?

There is a candidate answer, and it is testable. The neurovascular unit comprises brain
microvascular endothelium, its tight junctions, the basement membrane, the pericyte coat and the
astrocyte endfoot, and it is where a systemic cytokine wave becomes a neurological event [6,7].
If ICANS is the failure mode of that unit under cytokine exposure, and CRS the failure mode of
the systemic myeloid compartment, then the two are separate modules rather than two severities
of one process. What separates them should then track whichever construct-level feature changes
the gain of the endothelial arm.

Costimulation is such a feature. CD28- and 4-1BB-costimulated products differ in the kinetics
and magnitude of cytokine release [8,9], and the impression that CD28 products cause more
neurotoxicity is old and reasonably well established [5]. Bispecific engagers carry no
costimulatory domain and supply a third point on the same axis [10]. A construct-level
determinant should therefore order CD28 > 4-1BB > bispecific. An ordering by antigen, lineage,
tumor burden or market exposure would count against the account.

The question is about a ratio rather than a signal, which changes the measurement problem.
Almost all pharmacovigilance work in this space reports disproportionality, in the form of
reporting odds ratios, empirical Bayes geometric means or report counts, and then ranks products
by it [11,12]. Those quantities are dominated by terms with nothing to do with mechanism. They
include how many patients received the drug, when it launched, which indications it holds, how
closely it is monitored, and how novel it feels to the reporting physician (the Weber effect
[12–14]). A ranking of EBGM values is mostly a ranking of exposure and attention. A partition of
one class's own phenotype space is not, because exposure and attention enter numerator and
denominator alike. Among reports of the two hallmark toxicities, what fraction is the
neurological one?

Network medicine supplies the natural formalism for a two-module account [15–17], and also its
most common failure. The standard recipe maps targets and disease genes onto an interactome,
computes a proximity statistic, and reports a small p against degree-preserving rewiring. It has
produced a literature in which proximity is almost always significant and almost never
replicated prospectively. The null model is usually specified correctly. The difficulty is that
significance is reported without the power to detect the claimed effect. A nineteen-gene module
tested against a null whose dispersion is of the same order as the effect cannot resolve
anything, and its p value describes the null rather than the biology. We compute that power
explicitly and report it as a bound.

## The proposition under test

The hypothesis is stated as a falsifiable if–then proposition, and the rest of the paper is held
to it.

> If ICANS is carried by a neurovascular-unit module and CRS by a systemic myeloid module, then
> three things should hold in data that played no part in constructing the modules:
>
> (a) the partition R = ICANS/(ICANS + CRS) should order by costimulatory strength
> (CD28 > 4-1BB > bispecific) rather than by antigen, lineage or indication;
>
> (b) the two modules should localize in opposite directions across human brain cell types, and
> the neurovascular module should be inducible in primary human brain endothelium;
>
> (c) R should be invariant to production-side quantities (dose, expansion kinetics, tumor
> burden, cytokine clearance) and therefore stable across calendar time even while absolute
> report volumes change.
>
> If instead R orders by antigen or lineage, or the two modules co-localize, or R drifts with
> market exposure, the two-module account is false and the model is withdrawn.

Clause (c) carries the risk, because it predicts an absence and a single counterexample can
break it. We report it on those terms.

## What this paper does not claim

It does not claim a validated predictive model, a new biomarker or a molecular mechanism. It claims that a partition of a drug class's toxicity space behaves as a construct-level property,
and that two gene modules localize oppositely in human brain at a magnitude chance does not
produce. It claims further that the network route linking them cannot be resolved at currently
available module sizes, and that the resulting model makes one prediction a future launch can
settle. That prediction is
a threshold rule, stated with the number of reports at which it becomes decidable and silent
where no sample size decides it. For a computational venue, the negative result about network
proximity is arguably the more useful half.
