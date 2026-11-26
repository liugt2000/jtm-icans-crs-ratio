# Discussion

## What the data support

The partition of a T-cell engager's two hallmark toxicities is not a property of the patient
population alone. Across fourteen products it spans 2.6-fold, and the spread does not follow
market size. The two CD28 products, with 6,500 and 1,546 phenotype reports, sit at the top,
while the largest-volume bispecific (tarlatamab, 1,399 reports) sits in the middle. Within CD19,
the only stratum where antigen, disease and era are all held roughly constant, the ordering by
costimulation is clean and monotone.

The two modules are anatomically distinct in the human brain by a margin that random gene sets
do not reproduce. They sit on opposite sides of the endothelial–myeloid axis, with an
interaction contrast of 6.0 log₂ units (z = 8.6 over 10,000 stratified permutations). The
neurovascular module's endothelial character also replicates in a non-cerebral endothelium. This
is the strongest result in the paper and the least dependent on modeling choices.

The network-proximity route cannot answer the question at currently available module sizes, and
the arithmetic is general. A nineteen-gene module tested against a degree-matched null has a
minimum detectable ratio of about twelve-fold at 80% power. Proximity effects of the size
usually reported, a few fold at most, would be invisible to a design of this kind. The p values
are real, but they answer a different question.

## What the data do not support

**R is not the share of patients who develop ICANS.** It is the ratio of two report margins
inside one product's phenotype reports, and a report coded to both terms counts once in the
numerator and twice in the denominator.

**(i) A fixed construct property.** R matures upward inside eleven of thirteen products, by a
median of 0.066, and the class-level series takes two years to leave the floor set by the term's
introduction. R is a relative marker: valid between products observed at a similar stage of
market life, invalid across eras. Used as a fixed attribute, whether a product label or a
regulatory benchmark, it measures the calendar.

**(ii) That costimulation explains the partition.** In the BCMA stratum the ordering does not
hold: the two 4-1BB products fall on opposite sides of the bispecifics. With two CD28 products,
both CD19, costimulation and antigen are perfectly confounded in the contrast that carries the
main claim. CD28 costimulation is associated with a neurologically weighted partition in CD19
products in lymphoma. Generalization to other antigens is untested, and already contradicted
once.

**(iii) That a third of the effect is mechanism.** Discarding the 4,070 dual-coded reports
attenuates the CD28 excess from 0.087 to 0.058 and removes the separation (p = 0.20). The
coupling is either a severity effect or a coding habit attached to certain products. The severity proxy leans toward the first, since the ordering survives and widens on high-acuity
reports alone. Either reading weakens a claim of a clean module switch: on the available evidence,
CD28 products drive more severe disease overall rather than a different mixture of two equally
severe syndromes.

**(iv) That inducibility is specificity.** The myeloid module is induced more strongly than the
neurovascular one in TNF-α-stimulated endothelium (+2.02 versus +0.48). "Module X responds in
cell type Y" is therefore not evidence of anything, and papers making that inference, including
the obvious version of this one, are measuring the ubiquity of NF-κB signaling.

**(v) That a mechanism has been identified.** No experiment here manipulates a variable. The
account is a description with a falsifiable consequence, and that consequence will be settled by
a product launch rather than by another analysis of these data.

## Why the negative network result is worth publishing

A computational modeling venue is the right place to report that a standard route is
underpowered, because the failure is not specific to this question. Small curated module,
degree-matched null, significant proximity, no power calculation: that pattern is the default
in network pharmacology. Our own test produced a 1.34-fold effect at p = 0.26, and when the
same null was applied to 43 externally curated pairs it resolved them only above about tenfold.
The 1.34× is therefore untestable at this size, not absent. The
temptation to report the distance statistic (z = −1.91, nominally significant) while omitting
the random-walk statistic (z = −0.48, opposite sign) was considerable. Reporting both, then
inverting the null, converts a null result into a design specification: testing a 1.34-fold
difference needs modules of roughly 1,400 genes, or a different observable. Proximity studies
should publish their minimum detectable effect alongside their p value. It costs one paragraph.

## What the model is for

The model was not built to fit the data and does not fit them: inverting the group ratios
against its single gain returns 0.47, 0.62 and 0.92, which is not one number. Its value is
diagnostic. It shows three things. The partition is governed by the ratio of endothelial
amplification to recovery. Production-side quantities cancel only when the endothelial
compartment runs well below its ceiling. And the ceiling term is the route by which dose, tumor
burden and cytokine kinetics re-enter. That turns a vague worry, that the model ignores
severity, into a quantitative statement: production-side parameters contribute 18% of the
variance below the ceiling and 69% at it. It also tells the next study what to measure, which is
endothelial injury saturation rather than cytokine peak.

## Implications

*For clinicians.* The contribution here is subtractive. Nothing in this paper changes how a
patient is managed, and R is not a risk score: it has no denominator, no grading and no
individual-level prediction. What the paper removes is three habits of reading. Cross-product
comparison of neurotoxicity rates is not interpretable, because R matures upward within eleven
of thirteen products, so a comparison across launch eras measures the calendar rather than the
construct. The costimulatory domain does not stratify individual risk, because within-class
prediction error (0.056) is five times the between-class gap (0.012). Suppressing peripheral
cytokines is not expected to close the gap between the syndromes, because both modules are
induced in endothelium and the myeloid one more strongly (+2.02 versus +0.48). A single
circulating mediator does not separate two programs that both land on the same endothelium.

*The tocilizumab asymmetry, which we do not explain.* Tocilizumab controls CRS better than ICANS
[5,6], and our data do not account for that selectivity. If anything they cut against its
simplest reading. Because the myeloid module is induced in endothelium at all, a
myeloid-to-endothelial relay is a plausible route by which an IL-6-directed antibody could reach
the neurovascular compartment. That would predict the opposite of what is observed. The clinical
asymmetry therefore requires either that the endothelial amplification driving ICANS is largely
IL-6-independent, or that the two compartments are exposed to the drug differently. These data
distinguish neither. The preceding paragraph claims consistency with the clinical record, not an
explanation of it.

*For development.* The costimulatory domain, its geometry and the binder's affinity are fixed
years before the first patient is dosed. At that moment, a partition estimate from a class with
a decade of post-marketing reports costs one download. It cannot substitute for a phase 1 trial,
but it can inform the toxicity monitoring a program budgets for.

*For therapeutics.* Agents that reduce endothelial amplification address a different node from
tocilizumab, which drains the cytokine pool. They might interfere with IFN-γ signaling at the
endothelium, stabilize the blood–brain barrier, or block endothelial activation rather than
cytokine production. That is where a trial of ICANS prevention should aim.

*For pharmacovigilance methods.* Ratios of co-reported phenotypes are cheap, robust to market
size, and sensitive to construct-level features that disproportionality ranking cannot see. They
belong beside ROR and EBGM, with the caveat that they inherit every coding artifact of the terms
they are built from.

## Limitations

*Confounding of costimulation with antigen and disease.* The central limitation. Resolution
requires a CD28-costimulated product in a non-CD19 indication, which does not exist.

*Residual duplicate cases.* The extract holds 21,937 records over 21,937 distinct
`safetyreportid` values. The query returns one version per case, so there is no follow-up
version to prefer and no choice that could bias the phenotype counts upward. What cannot be
detected is the same patient under two identifiers, because FDA deduplicates on `caseid`, which
is not exposed. Counts are therefore an upper bound on unique patients by an unknown margin, and
the effect on R runs in whichever direction the more frequently re-reported phenotype lies.

*No exposure, dose or grade.* FAERS carries no denominator and no grading. R is a ratio over
reports, not over patients. Nothing here estimates incidence. The `serious` flag cannot stand in for severity,
because 98.7% of reports carry it. The term-level acuity proxy in Results approximates ASTCT
grade 3–4 without substituting for it. That endpoint rests on 491 ICANS reports, so it
constrains direction more firmly than magnitude.

*MedDRA version and the choice of preferred term.* Terms were matched by exact string on stored
values mapped to the current version [4]. Reports coded before 2018 cannot carry the ICANS term
prospectively; 1,205 were excluded, and the small number recoded retrospectively is covered by a
sensitivity analysis (Δ = 0.081, p = 0.143). The legacy-term analysis
(Table S7) bounds the problem directly: the direction survives all three
definitions, the statistical support does not. Whether that reflects dilution by non-specific
events or class-linked coding practice cannot be separated, and dilution is treated as the
parsimonious reading rather than a demonstrated one.

*Reporter type and country.* Both are modeled (Table S10) with a mixed
outcome. The direction is preserved in all eight testable strata, so neither a national
coding habit nor consumer reporting accounts for the sign, but separation survives in
only four. In the tightest homogeneous slice we can build, United States and
physician-reported, the contrast falls to +0.073 at p = 0.20. What survives is the
ordering of class means.

*The external replication is aggregate.* EudraVigilance publishes counts per term but not per
case, so the phenotype-isolation correction, the one that costs a third of the FAERS contrast,
cannot be reproduced there. The replication supports the ordering, not the magnitude. It is also
not like-for-like: the European counts are cumulative rather than window-restricted and include
all suspect roles, and eleven of thirteen products sit lower, with the fall concentrated in the
4-1BB arm. That shift is unexplained and is not claimed to be explained. tarlatamab has no
European entry and is absent altogether.

*Gene modules and one stimulus.* The five modules were curated before analysis but are not
exhaustive: the interaction contrast is robust to annotation availability (37/39 and 23/35 genes
annotated) but not to a wholesale redefinition of the neurovascular unit. GSE211439 is a single
dataset, one donor set, one cytokine. It establishes inducibility and nothing about
dose–response.

# Conclusions

The partition of ICANS and CRS across T-cell-engaging therapies behaves like a construct-level
property within the one antigen stratum where it can be tested. It is anatomically consistent
with a neurovascular-unit module that localizes in the human brain by a margin chance does not
produce. It matures with reporting experience in a way that forbids cross-era comparison. And it
is connected to its candidate mechanism by a network route that this design cannot resolve, and
that most published designs cannot resolve either. The prediction is a threshold, the refutation
is a report count, and only a large enough launch will decide between them.
