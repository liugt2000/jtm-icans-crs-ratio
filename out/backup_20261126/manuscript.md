# The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in BCMA

**Running title.** Costimulation and the ICANS/CRS ratio

**Authors.** [Author list to be completed]

**Affiliations.** [To be completed]

**Corresponding author.** [Name, address, e-mail]

**Manuscript type.** Original research

**Word count (main text, excluding abstract, references, tables and figure legends).**
10,640

**Figures.** 6. **Tables.** 3 in the main text; the 13 supplementary tables are in
Additional file 1.

---


# Abstract

**Background.** T-cell-engaging therapies cause cytokine release syndrome (CRS), a systemic
myeloid response, and immune effector cell-associated neurotoxicity syndrome (ICANS). The two
co-occur in most patients and dissociate in many, but whether their ratio is a construct or a
patient property has not been tested.

**Methods.** We analyzed 21,937 case-level reports carrying either phenotype term in the US FDA
Adverse Event Reporting System; 20,732 came from 2019 onward, when the ICANS term existed,
covering 14 products with ≥20 primary-suspect reports. The pre-specified
endpoint was R = ICANS/(ICANS + CRS), a ratio of report margins that cancels the market denominator.
CD28- and 4-1BB-costimulated products were compared over all 21 label permutations, under
nine analytic specifications and nine reporting strata, and the ratio was rebuilt in
EudraVigilance. Two gene modules were localized in human brain single-nucleus data against
10,000 expression-stratified nulls and tested for inducibility in TNF-α-stimulated brain
endothelium; a network-proximity test followed.

**Results.** R was 0.361 for CD28, 0.274 for 4-1BB and 0.222 for bispecific products (Δ = 0.087).
Both CD28 products ranked above all five 4-1BB products, the most extreme ordering a
two-versus-five design can score, and the ordering reproduced in EudraVigilance (Δ = 0.141,
ρ = 0.92). The direction held in all eight testable strata and seven of eight years, but
separation failed in the tightest homogeneous slice (United States, physician-reported:
Δ = +0.073, p = 0.20). Restricting to single-phenotype reports attenuated Δ to 0.058;
restricting to high-acuity reports widened it to 0.247; the ordering failed within BCMA. The
modules localized in opposite directions across brain cell types (Δ = +6.03, z = +8.57) yet
were both induced in brain endothelium. Network proximity gave 1.34-fold against a minimum
detectable 11.9-fold; the same null resolved 43 externally curated pairs only above tenfold.

**Conclusions.** Within CD19 the ratio is ordered by costimulatory architecture, but its support
is confined to the modern phenotype, fails within BCMA, and matures with reporting experience. At 6,500 reports, ratios between 0.309 and 0.331 cannot be resolved at all.

**Keywords.** ICANS; cytokine release syndrome; chimeric antigen receptor T cells; bispecific
T-cell engagers; pharmacovigilance; network medicine; neurovascular unit.

---

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

---

# Methods

## Study design and reporting

Retrospective pharmacovigilance analysis of spontaneous reports, combined with public
transcriptomic and interactome data and a deterministic model. The analysis plan covers the
endpoint, phenotype definitions, null models, negative controls and failure criteria. It was
written before any data were retrieved and is deposited with the code, and its timestamp
precedes the retrieval timestamp in `out/pull_meta.json`. Reporting follows RECORD [18,19], with
the checklist as Additional file 2. All records are public and de-identified at source.

## Data sources

### FAERS, case level

Reports were retrieved through the public openFDA `drug/event` interface, frozen on 2026-11-16
(`meta.last_updated` 2026-10-28). Because the record-level interface returns whole reports
rather than marginal totals, the analysis operates on reports. Every report carrying either
phenotype preferred term was downloaded in full, reduced to the fields used below and stored as
JSONL. Retrieval was exhaustive, not sampled.

*Duplicate follow-ups.* FAERS resubmits a case as it is followed up, but the public interface
exposes one record per case, the latest version. This was verified rather than assumed: the
21,937 records carry 21,937 distinct `safetyreportid` values, with versions 1 to 6. No records
were removed at this step. The residual risk cannot be eliminated through this interface,
because the same patient under two identifiers is undetectable. The deduplication key `caseid`
is not exposed, so counts are an upper bound on unique patients by an unknown margin.

*Primary-suspect restriction.* Exposure was `drugcharacterization == 1` for that drug entry,
matched within the report rather than across it. The filter removes concomitant-only entries,
497 of the 1,067 ICANS reports listing cyclophosphamide and 459 of 863 for fludarabine. FAERS
permits several primary suspects, however, so conditioning chemotherapy survives:
cyclophosphamide is a primary suspect in 570 ICANS reports, and siltuximab, used to *treat* CRS,
in 33. Role restriction guarantees that the cell product is a suspect, not that the suspect set
is causally coherent. The any-role analysis is reported alongside (Additional file 1: Table S2).

*Substance normalization.* Names were upper-cased, suffix-stripped and collapsed to a single
substance key before any counting (`TECLISTAMAB` and `TECLISTAMAB-CQYV`); the merge table is
Additional file 1: Table S1.

*Analysis window.* The ICANS preferred term entered MedDRA 21.0 (2018), so reports received
before 2019-01-01 were excluded. Because openFDA maps stored terms to the current dictionary, a
few pre-2019 cases carry the term retrospectively, and the window removes them.

### EudraVigilance, aggregate level

The replication used the public European interface [20] (`adrreports.eu`, queried 2026-11-21),
which publishes, per substance, the number of reports carrying each preferred term, cumulative
to 15 November 2026. Each substance resolves to an Oracle BI dashboard addressed by its European
Medicines Agency high-level code, and the phenotype is selected as a reaction group and then a
reaction from two dependent list boxes. Because the dashboard assembles its content client-side,
pages were rendered in headless Chromium and counts read from the three charts the filter
refreshes: age and sex, reporter group, and outcome. A value was accepted only when all three
agreed, and disagreement was treated as a failed read and retried. The source is aggregate, so
the co-reporting and phenotype-isolation analyses (4,070 dual-coded FAERS reports) have no
counterpart here. The counts are neither window-restricted nor primary-suspect-restricted,
because the interface exposes neither filter.

### Human brain cell-type expression

Human Protein Atlas `proteinatlas.tsv` (release 2026-11-16) [21,22], field `RNA single nuclei
brain specific nCPM`: 20,151 genes, of which 6,084 carry at least one brain cell-type
annotation. Genes without annotation were scored zero rather than excluded, so that module
scores are not conditioned on annotation availability; a sensitivity analysis restricted to
annotated genes is reported.

### Primary human brain microvascular endothelium under inflammatory challenge

GSE211439 (primary human brain microvascular endothelial cells, TNF-α versus medium, three
replicates per arm) supplied the induced-response data, and GSE195519 supplied the orthogonal
endothelial-versus-non-endothelial contrast. Counts were used at the deposited level, log
CPM-transformed and filtered to mean log CPM > 1. A quality gate preceded use. In GSE195519 the
iBMEC arm expresses *SLC2A1* and *OCLN* but not *CLDN5*, *PECAM1* or *VWF*, and scored z = +0.67
for the neurovascular module, which is indistinguishable from a random gene set. It was
therefore excluded from all localization claims (Additional file 1: Table S4).

### Physical interactome

OmniPath `interactions` (2026-11-16; layers `omnipath`, `pathwayextra`, `kinaseextra`,
`ligrecextra`; human, protein–protein entities only) returned 139,851 records [23] (SHA-256
`2bb2bbfb…`). The largest connected component has 10,156 nodes and 79,553 edges, with mean
degree 15.7. Evidence codes are retained but not used to weight edges, because weighting by
supporting publications would reintroduce the study-attention bias the design avoids.

### Pathway annotation (positive control only)

Reactome release 98 was downloaded on 2026-11-25 (`ReactomePathways.gmt.zip`, SHA-256
`6056fcd9…`; 2,874 pathways). It is used only to build the positive control described under
*Network proximity and its power*: 261 pathways have 60–120 genes in the interactome, 152 remain
after removing pairs whose gene sets overlap by more than a Jaccard index of 0.5 — the near
duplicate cascade families, such as nine Toll-like-receptor variants — and 40 were taken at even
intervals in Reactome-ID order. No pathway annotation enters any other analysis, and the choice was
fixed before any statistic was computed on it.

## Phenotype definitions

Two phenotypes were fixed before retrieval. *Neurotoxicity* is the single PT *Immune effector
cell-associated neurotoxicity syndrome*, deliberately narrower than a composite: the legacy PT
*Neurotoxicity* carries 17,539 reports, 2.96 times as many, and pools chemotherapy, transplant
and infection-related events. A non-exact search returned 23,246 on the freeze date because it
also matches longer terms; the exact count is used. The legacy term is a sensitivity analysis,
not a secondary phenotype.

Two alternative numerators were built against the shared CRS denominator, R(union) using either
term and R(legacy) using *Neurotoxicity* alone. Both were retrieved independently and
completely, with 17,539 records over 36 pages, the merged count reconciled against the API
total, and the two records lost to version de-duplication accounted for. They were merged on
`safetyreportid`, and on the 1,909 reports present in both pulls every phenotype flag agrees.
Neither is primary: the legacy term pools chemotherapy- and infection-related neuropathy and
would import the mechanism under test. *Cytokine release syndrome* is the single PT *Cytokine
release syndrome*, with a severe-CRS composite (hemophagocytic lymphohistiocytosis, macrophage
activation, capillary leak) as a sensitivity analysis.

## The partition metric

For each product *p*, reports carrying either phenotype in which *p* is the primary suspect
define

    R_p = n_ICANS(p) / (n_ICANS(p) + n_CRS(p))

**What R is arithmetically.** R = a/(a + b), with a the ICANS and b the CRS report count, is the
ratio of two marginal counts, and the two counts are not disjoint. In the analyzed set 1,703
reports carry ICANS alone, 10,623 CRS alone and 3,794 both, so each dual-coded report enters the
numerator once and the denominator twice. Pooled over the set this gives R = 0.276, whereas the
share of ICANS among phenotype-positive reports is 0.341. The gap is the dual coding, not an
error in either quantity, and it fixes the interpretation: R compares the two terms' report
margins within one class. It is **not** the fraction of patients with ICANS, it is **not** a
partition of patients into two groups, and nothing in this paper uses it as either.

R is therefore named for what it is: a **ratio of report margins**. That name is used wherever
the quantity itself is meant. *Partition* names the construct — the split of a class's phenotype
reports between its two hallmark toxicities — so that "the partition orders by costimulation"
claims something about the phenomenon, while every number attached to it is R. The two names are
not interchangeable, and no sentence here treats R as an estimate of the share of patients who
develop ICANS.

R normalizes within one class's own phenotype reports, so it omits the market denominator that
dominates ROR and EBGM. Products with fewer than 20 phenotype reports were ineligible, since R
is unstable at small denominators. Intervals are Wilson score intervals [24]; the normal
approximation was rejected because several products sit near a boundary and the smallest
eligible denominator is 25, where the Wald interval is anti-conservative.

## Severity proxy

FAERS records ICANS as one preferred term and carries no grade, so the primary endpoint cannot
distinguish grade 1 confusion from grade 4 coma. Two proxies were built, and the first is
reported as a failure. The `serious` flag has almost no variance in this extract: 20,466 of
20,732 reports (98.7%) are flagged serious and 266 are not, so it cannot stratify anything.
`seriousnesslifethreatening` and the hospitalization flags were not retained in the frozen
extract, and adding them would change the dataset and every digest in the paper.

A term-level proxy was therefore fixed before the contrast was computed. A report is
*high-acuity* for ICANS if it carries encephalopathy, depressed level of consciousness, coma,
brain edema, seizure, status epilepticus or paresis. It is *high-acuity* for CRS if it carries
shock, respiratory failure, capillary leak, hemophagocytic lymphohistiocytosis or macrophage
activation, or multiple organ dysfunction. Mild presentations, namely *Confusional state*,
*Somnolence*, *Pyrexia*, *Hypotension* and *Hypoxia*, are deliberately excluded, so the proxy is
conservative. Two endpoints follow: the share of a product's ICANS reports that are high-acuity,
and R recomputed with both phenotypes restricted to their high-acuity forms (R_hi). Products
with fewer than 20 high-acuity reports are ineligible for R_hi, which is the same rule applied
to a smaller denominator. Both endpoints are descriptive (see *Multiplicity*, below) and both
are given in Additional file 1: Table S11.

## Group contrast and its exact null

The pre-specified contrast is the difference in mean R between CD28- and 4-1BB-costimulated
products. With seven such products no asymptotic test is credible, so the null was obtained by
**enumerating all C(7,2) = 21 label permutations exactly**, not sampled. The smallest attainable
one-sided p is 1/21 = 0.048, reached only under perfect separation. The two-sided p counts
assignments at least as extreme in absolute value. Because the two groups are unequal in size
(two and five), the mirror of an assignment is not itself a permutation, so the two-sided value
is not twice the one-sided one. Here it is 2/21 = 0.095, and 1/21 is attainable in principle.
The contrast is therefore a separation check, and any claim resting on it is worded accordingly.

Two further stratifications use fields recorded per case but not used in the primary contrast.
The first is reporting country: the United States, Europe (the EU aggregate code plus European
country codes), Japan, and the remainder. The second is the primary source's
qualification:/nphysician, other health professional, or consumer. Each stratum is analyzed with
the same eligibility rule, the same endpoint and the same exhaustive permutation over its own
product set. Each is reported with the number of label assignments it admits, so that a thinner
stratum reads as less resolvable rather than as silently significant.

**Multiplicity.** The strata are nested, the United States being a subset of all reports and
non-US its complement, so their p values are not independent and are not corrected as if they
were. The same holds for the nine analytic specifications, the calendar windows, the three
phenotype definitions and the severity endpoints: **only the pre-specified primary contrast
carries an inferential claim**. Everything else is reported descriptively, each with the number
of label assignments its design admits and, where relevant, the smallest p that design can
produce. No BH-FDR adjustment is applied, because no family of confirmatory hypotheses is being
tested; attaching q values to contrasts never stated as hypotheses would imply a testing program
that does not exist. The choice is declared rather than left implicit, and its cost is accepted:
no secondary contrast in this paper can be read as a discovery.

## Generalization: leave-one-product-out

Each eligible CAR-T product was removed in turn and its R predicted from the mean of the
remaining products **in its class**, with the comparator predicted from all remaining products
regardless of class. The quantity tested is not absolute error but the improvement of the
class-based over the class-blind predictor. It is evaluated against **every** alternative
assignment of two of the seven products to the CD28 label (21 assignments, enumerated exactly).
With two CD28 products, the leave-one-out prediction for a CD28 product rests on a single donor
and its error is not an independent estimate of within-class generalization. Results say so
rather than adjusting for it.

## Resolution limit of the prediction

For a candidate true R and sample size *n*, the Wilson interval is formed. The verdict is
*supports* when the lower bound exceeds the highest observed 4-1BB value, *refutes* when the
upper bound falls at or below it, and undecidable otherwise. The smallest *n* admitting a
verdict was found by bisection to integer resolution over candidate values from 0.15 to 0.45 in
steps of 0.0025. The sample size at which the unresolvable band is quoted is the largest
single-product denominator the dataset contains rather than a round number, so the limit is
expressed in units this database has produced.

## Disproportionality (secondary, negative control only)

A disproportionality statistic is computed for one purpose: to check that the phenotype of
interest is not simply the strongest signal in the class. ROR (Haldane correction only for zero
cells) and EBGM with its lower 5% bound were computed from aggregate margins using DuMouchel's
two-component gamma-Poisson shrinker [11], fitted by expectation-maximization from four
initializations (Additional file 1: Table S3). The margins are neither role-restricted nor
case-level, so they are an upper bound. Eight PTs with no plausible mechanistic link to either
module were pre-specified as negative controls (alopecia, rash, pruritus, neutropenia,
thrombocytopenia, diarrhea, constipation, peripheral edema); the check is whether any attains an
EB05 above that of ICANS. The set calibrates rather than filters. A p value against the full
database answers a question nobody asked and is anti-conservative when the outcome is
class-private [25], whereas unrelated outcomes supply an empirical null for this design.

## Module definitions

Five gene sets were fixed before any expression data were inspected. `CNS_VASCULAR` holds 39
genes of endothelial junction, basement membrane, pericyte and astrocyte endfoot.
`MYELOID_CYTOKINE` holds 35 genes of the systemic cytokine program of monocytes and macrophages.
`COSTIM_CD28` (26 genes) and `COSTIM_41BB` (19) serve as construct-level comparators, and
`HEPATOCYTE_NEGCTRL` (17) as a module with no reason to be enriched in either the brain or the
myeloid compartment. Gene lists and provenance are in Additional file 1: Table S5.

## Localization score and matched null

For each gene the localization score is

    L = log2( (endothelial nCPM + 1) / (myeloid nCPM + 1) )

and a module's statistic is the mean of L over its members. The null is a matched random gene
set: 10,000 draws of the same size from the 20,151 assayed genes, stratified on expression
decile so that the null does not merely reproduce the abundance–specificity relationship. The
interaction contrast Δ = mean(L | CNS_VASCULAR) − mean(L | MYELOID) was tested by drawing both
null sets independently in each of 10,000 permutations.

## Network proximity and its power

Three statistics were computed. The first is the minimum shortest-path distance between modules.
The second is random-walk-with-restart mass deposited on the target module (α = 0.7, sparse LU
with batched right-hand sides). The third is the ratio of RWR mass from the CD28 to the 4-1BB
module, with CD28 subsampled to the size of the 4-1BB module (19 genes) over 1,000 subsets. All
pairwise values are given in Additional file 1: Table S6.

Every null substitutes gene sets rather than rewiring the graph. Each gene in a set is replaced by
a gene drawn from the same degree decile, with the graph itself left intact; the per-module
statistics use 2,000 such draws, and the CD28/4-1BB ratio uses 1,000 independently matched pairs.
Substitution is the deliberate choice. Edge rewiring randomizes the adjacency that the statistic
measures, so any curated module looks enriched against its own randomized graph; substitution
keeps the real topology and asks instead whether a set with the same degree profile, placed
elsewhere in that graph, would land as much mass on the target. Degree is therefore preserved in
strata rather than exactly. Within the top stratum it still spans an order of magnitude, so a set
of near-hub genes can out-deposit its own null; the direction of that error is anti-conservative,
and its size is measured in Additional file 1: Table S13.

The null was then applied, unchanged, to pairs whose relatedness is fixed externally (Additional
file 1: Table S13). Forty Reactome v98 pathways of 60–120 genes were each cut into two disjoint
halves of 19 genes, drawn from the pathway's members in alternating order within each degree
decile so that the split cannot itself create a degree difference; three pairs of subunits of one
physical complex fix the ceiling (40S against 60S ribosomal proteins, 20S proteasome alpha against
beta subunits, 19S ATPase against base subunits); and thirteen pairs with no reason to be proximal
fix the floor (the hepatocyte negative-control module against three pathway halves, and ten
independent random pairs). Each pair is scored with the statistic and the 1,000-draw null used in
the per-module results. The fold is the quantity reported, because it does not depend on how many
draws the null contains.

Where the observed effect lies inside the null, the analysis does not stop at "not significant".
The null quantiles are inverted to give the minimum ratio detectable at 80% power with α = 0.05,
and the module size needed to resolve the observed ratio. The σ ∝ 1/√k scaling used for that
extrapolation is an assumption, and its consequence is an order of magnitude rather than a precise
requirement.

## Mechanistic model

**This is a plausibility model, not a fitted one.** No parameter is estimated from the FAERS
data, nothing is calibrated to the observed values of R, and no goodness of fit is claimed.
Parameters are stated ranges of the right order of magnitude for CAR-T expansion and cytokine
kinetics, swept in full over those ranges (Additional file 1: Table S12). The model is asked only
which quantities can move the endpoint, and in which direction. With that stated, a
three-variable deterministic model gives the account one prediction beyond the ordering it was
built to explain:

    dA/dt = r·A·(1 − A/K) − d_A·A
    dC/dt = k_C·A − λ_C·C
    dE/dt = k_E·C·(1 − E/E_max) − λ_E·E,     k_E = k_E0·(1 + β·s)

where A is effector burden, C systemic cytokine exposure, E neurovascular endothelial injury and
s costimulation strength (CD28 = 1, 4-1BB = 0.5, bispecific = 0), and the observable is R = max
E / max C. Integration used fixed-step RK4 (Δt = 0.05 d, 60 d), vectorized over parameter draws.
A one-at-a-time sweep was repeated in an unsaturated regime (E_max = 10⁴, ceiling never binding)
and at a nominal saturating value (E_max = 8). It tested the claim that R → k_E/λ_E, and
therefore independent of every production-side parameter. A Saltelli–Sobol decomposition [26]
(base sample 512, nine parameters with E_max held fixed, 10,240 model evaluations per regime)
then gave first- and total-order indices, implemented directly rather than through a library.
The model is small enough to be checked by hand, and its role is to identify which quantities
the conclusion depends on.

## Software and code

All computation ran in Python 3.13 with pinned dependencies (`requirements.txt` in the deposit),
and every random seed is written into the JSON that records the parameters of the output it
produced. The DeepSeek assistant (DeepSeek-V4.1-Flash) was used to draft and debug this code and
to compare candidate methodological options; each suggestion was checked against the deposited
outputs before it was adopted, and the authors executed and verified every script. The full
disclosure is in the Declarations.

---

# Results

## The corpus

The openFDA record interface returned 5,929 reports carrying the ICANS preferred term and 20,080
carrying the CRS term (database frozen 2026-10-28). Removing the 4,072 reports carrying both
(4,070 of them inside the analysis window) left 21,937 distinct reports, one per
`safetyreportid`. The interface exposes a single version per case, so no duplicate follow-up
survived retrieval. Restricting to reports received on or after 2019-01-01 removed 1,205 records
and left **20,732**. Fifteen products appear in the window. Of those, 14 products met the
eligibility rule of at least twenty phenotype reports as primary suspect; the fifteenth,
afamitresgene autoleucel, had two, and is reported but not analyzed (Table 1).

The two phenotypes are strongly but incompletely coupled. Of the 5,927 in-window ICANS reports,
4,070 (**68.7%**) also carry the CRS term, ranging from 46.3% (elranatamab) to 79.5%
(idecabtagene vicleucel) (Figure 1B). That leaves 1,857 reports with ICANS alone and 14,805
with CRS alone. Treating the two as independent outcomes models a correlation structure that
does not exist. Dividing the ICANS count by their sum divides two margins, as Methods sets out.

## The partition orders by costimulation

Figure 1A shows R = ICANS/(ICANS + CRS) for all fourteen eligible products. R spans 0.150 to
0.390, a 2.6-fold range within one drug class.

| stratum | products | mean R | range |
|---|---|---|---|
| CD28 costimulation | 2 | **0.361** | 0.332–0.390 |
| 4-1BB costimulation | 5 | **0.274** | 0.218–0.320 |
| no costimulatory domain (bispecific) | 7 | **0.222** | 0.150–0.273 |

The ordering is the one the two-module account predicts, and it is monotone across all three
strata. The point estimates separate completely: the lower CD28 product (axicabtagene
ciloleucel, 0.332, 95% CI 0.321–0.344) exceeds the higher 4-1BB product (lisocabtagene
maraleucel, 0.318, CI 0.280–0.359). It exceeds it only just, and the widest 4-1BB interval
belongs to obecabtagene autoleucel on twenty-five reports (0.320, CI 0.172–0.516). Separation is
therefore nominal at the level of individual products, even where it is clean at the level of
group means.

The pre-specified contrast, mean R(CD28) − mean R(4-1BB), is **+0.087**. With two and five
products the exact permutation distribution has 21 points, and the observed grouping is its
maximum in the pre-specified direction: **one-sided exact p = 1/21 = 0.048**. That is the
smallest value the design can produce. The two-sided p is 2/21 = 0.095, which is not twice the
one-sided value. With a two-and-five split the mirror of an assignment is not itself a
permutation, so the two tails are asymmetric and 1/21 is attainable in principle. One of the
calendar-window specifications does reach it (Table 2). A conventional two-sided claim is
therefore out of reach at this design size. We report the contrast as a directional separation
test, and the inference rests on the robustness analyses below rather than on the p value.

## The ordering holds within CD19 and fails within BCMA

Stratifying by antigen is the sharpest test of whether the partition tracks the construct or the
disease, because CD19 and BCMA products treat different diseases with different baseline
neurological risk.

*CD19.* Six products, three strata, clean ordering: CD28 (0.390, 0.332) > 4-1BB (0.320, 0.318,
0.221) > bispecific (0.199). Antigen is held constant and disease roughly so, and the partition
still separates by costimulation.

*BCMA.* Four products, and the ordering does not hold. Ciltacabtagene autoleucel (4-1BB) at
0.295 exceeds both bispecifics (teclistamab 0.273, elranatamab 0.246), while idecabtagene
vicleucel (4-1BB) at 0.218 falls below them.

*Bispecifics across five antigens.* R ranges from 0.150 (glofitamab, CD20) to 0.273
(teclistamab, BCMA). The CD20 agents sit at the bottom and the plasma-cell and neuroendocrine
agents at the top. That pattern reads as an indication effect rather than an antigen effect:
heavily pretreated myeloma and small-cell lung cancer patients carry a different baseline burden
of neurological comorbidity than lymphoma patients.

Two conclusions follow, and they pull in opposite directions. The CD19 stratum supports the
construct-level account under the tightest available control; the BCMA stratum refutes its
universality. The CD28 arm also contains only CD19 products, so costimulation and antigen are
perfectly confounded for the one contrast this paper turns on. No CD28-costimulated BCMA or CD20
product exists.

## The ordering depends on the ICANS term

The primary term entered MedDRA in 2018, so for the first years of the class there was no such
code to report. Recomputing the partition under the convention it replaced tests construct
validity rather than a technicality (Additional file 1: Table S7).

| Definition of the numerator | CD28 | 4-1BB | Δ | one-sided p |
|---|---|---|---|---|
| ICANS only (primary) | 0.361 | 0.274 | +0.087 | 0.048 |
| ICANS or *Neurotoxicity* (union) | 0.440 | 0.353 | +0.087 | 0.095 |
| *Neurotoxicity* only (legacy) | 0.196 | 0.163 | +0.033 | 0.333 |

The direction survives all three definitions. The strength of the evidence does not. Under the
union definition Δ is unchanged at 0.087, yet the exact p rises to 0.095 because complete
separation is lost: liso-cel's union value (0.433) exceeds axi-cel's (0.427). Under the legacy
term alone the contrast attenuates by 62% to 0.033, and p rises to 0.333.

The attenuation is not random. Legacy-to-ICANS ratios differ by product, at 0.83 for tisa-cel
and 0.64 for liso-cel against 0.54 for axi-cel and 0.34 for brexu-cel, so pooling the legacy
term adds events unevenly to the two classes. Two readings are available and the design cannot
separate them. Either the legacy term is dominated by non-specific neurological events that
dilute a real signal, which attenuates without reversing, or coding practice differs by product
in a way that tracks class. Both forbid the stronger claim.

The conclusion is therefore narrower than the hypothesis: the ordering is a property of the
ICANS phenotype specifically, and does not extend to neurotoxicity at large. Broadening the
numerator raises every partition, with the class means moving from 0.361 and 0.274 to 0.440 and
0.353, while leaving the gap at 0.087.

## The ordering reproduces in a second reporting system

A partition that orders by costimulation in FAERS may still reflect American reporting practice
rather than pharmacology. We therefore rebuilt it in EudraVigilance [20], which draws on a
different reporter population, a different coding convention and a case base that overlaps only
partly with the American one. That interface publishes counts per substance, reaction group and
preferred term, but not case-level records, so the phenotype-isolation correction cannot be
applied there. What can be tested is whether the ordering and the grouping survive.

Thirteen of the fourteen products have a substance entry; tarlatamab has none. Across the
thirteen, EudraVigilance holds **34,277** reports, of which **18,625** carry either phenotype
term (4,801 ICANS, 13,824 CRS), and every product clears the threshold.

The ordering is reproduced (Figure 1D; Additional file 1: Table S9). Spearman's ρ between the
two systems over the thirteen products is **0.92**, and 70 of the 78 product pairs are ordered
the same way in both. The two CD28 products sit at the top in both systems and agree almost
exactly: R = 0.331 in EudraVigilance against 0.332 in FAERS for axi-cel, and 0.401 against 0.390
for brexu-cel. The contrast is **+0.141** (CD28 0.366, 4-1BB 0.225) against 0.087 in FAERS. With
all 21 label assignments enumerated it attains the same values as in FAERS: one-sided
p = 0.048, two-sided 0.095. Same grouping, same inferential resolution, different data.

That p depends on how many products the design admits, and one product sits on the threshold.
obe-cel clears twenty phenotype reports on 31 European reports. Including it makes the design
seven-versus-two rather than six-versus-two, and lowers the attainable one-sided minimum from
1/15 to 1/21. Excluding it gives Δ = 0.149 at one-sided p = 0.067, again the minimum
attainable for that design. The inclusion does not manufacture the result. The honest summary is
that the replication reproduces the grouping at the smallest p each design permits, not at a
conventionally small one.

The agreement is not uniform in level. Eleven of the thirteen products sit lower in
EudraVigilance, and the median absolute difference is 0.035. The two CD28 products are
essentially unchanged (mean +0.005), whereas the five 4-1BB products fall by a mean of 0.049:
liso-cel by 0.053, cilta-cel by 0.052, and ide-cel and obe-cel by 0.062 each. The class gap is
therefore wider in Europe, and the shift is concentrated in one arm. We offer no explanation. A
difference in how the two systems grade CRS would produce it, but so would a real difference in
European product performance. Two further differences cannot be removed through the public
interface: the counts are cumulative to 15 November 2026 rather than window-restricted, and they
include every report naming the substance. The European figures are therefore not a
like-for-like re-estimate of Table 1.

One further asymmetry constrains the paper's own sensitivity analysis. In FAERS the legacy
*Neurotoxicity* term is used 2.96 times more often than ICANS. In EudraVigilance the reverse
holds for most products, with axi-cel carrying 970 legacy events against 2,312 ICANS events. Use
of the legacy term is therefore a property of the reporting system rather than of the drug,
which is the strongest justification for resting the claim on the ICANS term alone.

## Direction survives every stratum, separation does not

Both fields are recorded per case. Splitting the extract nine ways
(Additional file 1: Table S10), the direction is positive in all eight testable strata,
from +0.073 among American physician-reported cases to +0.164 in Europe. Perfect product-level
separation, the condition the exact test actually scores, survives in only four. In the United
States alone Δ = +0.091 and the one-sided p rises to 0.095; among physician-reported cases it is
+0.103 at p = 0.133. Japan cannot be tested, because
only one CD28 product reaches twenty phenotype reports there. What replicates across
systems and strata is the order of the class means, not the clean separation that the all-report
p value reflects.

## Corrections to the aggregate endpoint

Table 2 and Figure 2A recompute the contrast under nine specifications.

*Exposure role.* Restricting to primary-suspect entries changes Δ from 0.087 to 0.089, which is
negligible. The restriction removes concomitant-only entries but does not purge the
lymphodepletion regimen, because FAERS permits several primary suspects per report.
Cyclophosphamide survives as a primary suspect in 570 ICANS reports, fludarabine in 404, and
siltuximab, given to *treat* CRS, in 33. Role filtering is necessary but not sufficient for
causal coherence.

*Combination reports.* Restricting to reports in which the product is the only engager leaves Δ
at 0.091 (p = 0.048). Product-level ranking is not produced by combination regimens.

*Phenotype isolation.* This is the correction that matters. Recomputed on reports carrying
exactly one of the two terms, which discards all 4,070 dual-coded reports, Δ falls from 0.087 to
**0.058** and the one-sided p rises to 0.200 (Figure 1C). The direction survives; roughly one
third of the magnitude does not, and neither does the separation. A material part of the CD28
excess is carried by reports recording both syndromes. That is what one expects if the two
modules are coupled at the severe end, and if CD28 products drive more severe cases overall. The
shift is then partly a severity effect rather than a pure module switch.

## The ordering is not an artifact of mild reports

The isolation correction raises the severity question directly. If a third of the CD28 excess is
carried by reports recording both syndromes, does the ordering survive when only severe reports
are counted? The `serious` flag cannot answer it, because 98.7% of these reports carry it. A
term-level acuity proxy was therefore fixed before this contrast was computed (Methods;
Table S11).

High-acuity ICANS (encephalopathy, depressed consciousness, coma, brain edema, seizure or
paresis) is recorded in **8.7%** of the 5,628 ICANS reports belonging to the fourteen products.
It is nearly twice as common in the CD28 arm as in the 4-1BB arm, at **12.1%** against **6.3%**
of ICANS reports (Δ = +5.8 percentage points, one-sided exact p = 0.095). Complete
separation is absent, because tisa-cel's 12.0% exceeds axi-cel's 11.3%. CD28 neurotoxicity is
therefore not only more frequent relative to CRS but more often severe. That is the coupling the
isolation correction exposed, seen from the other side.

Restricting both phenotypes to their high-acuity forms sharpens the ordering rather than
dissolving it. R_hi is **0.477** for CD28 against **0.231** for 4-1BB, Δ = **+0.247** at
one-sided exact p = 0.067, again the smallest value its design admits, now over fifteen
label assignments. Separation is intact: the lower CD28 product (0.470) exceeds the highest
4-1BB product (0.404). obe-cel drops out of this endpoint, having three high-acuity reports in
total, so the 4-1BB arm is four products rather than five. The costimulation ordering is
therefore not produced by the coding of mild events; at the severe end it widens.

## The level drifts, the ordering does not

R is not stable in absolute terms, and the drift is systematic. Recomputing each product's R in
the first and second half of its own observation window, **11 of 13 products rise**, with
a median increase of **+0.066** (Figure 3B). The class-level series shows the same pattern. R
sits at 0.025 in 2019, the first year the term existed, reaches 0.267 by 2021, then holds
between 0.267 and 0.310 for six consecutive years while annual report volume triples
(Figure 3A). The 2019 value is a coding artifact. The later rise inside every product is the
signature of reporting maturation, not of changing disease. Clause (c) of the model is therefore
**refuted in absolute form**: R is a relative marker, comparable between products observed at a
similar stage of market life and not across eras.

What survives is invariance of the ordering. Recomputing the CD28-minus-4-1BB difference within
each calendar year gives a positive value in **seven of eight years**, the exception being
2019, when each stratum contains one product (Figure 3C). Restricting to 2021–2023 and
2024–2026, product-level rankings correlate at Spearman ρ = **0.78** (p = 0.0026, n = 12).
The ordering is not an artifact of era, launch order or market composition in any given year.

## The two modules localize in opposite directions in the human brain

The localization score L = log₂[(endothelial nCPM + 1)/(myeloid nCPM + 1)] was computed from the
Human Protein Atlas single-nucleus brain atlas for 20,151 genes, 6,084 of which carry at least
one brain cell-type annotation.

| module | genes | annotated | mean L | matched null | z | p |
|---|---|---|---|---|---|---|
| CNS_VASCULAR | 39 | 37 | **+3.770** | −0.351 ± 0.601 | **+6.86** | <10⁻⁴ |
| MYELOID_CYTOKINE | 35 | 23 | **−2.259** | −0.184 ± 0.409 | **−5.08** | <10⁻⁴ |
| HEPATOCYTE_NEGCTRL | 17 | 3 | 0.000 | −0.042 ± 0.266 | +0.16 | 0.67 |

The interaction contrast, Δ = mean L(CNS_VASCULAR) − mean L(MYELOID_CYTOKINE), is **+6.029**
against a null of −0.166 ± 0.723 (10,000 stratified permutations), **z = +8.57, p < 10⁻⁴**
(Figure 4A). The modules are not merely both present in the brain; they sit on opposite sides
of the endothelial–myeloid axis. No random gene set of the same size and expression decile
reproduces that margin. The hepatocyte negative control sits at zero, as it should, although
with three annotated genes it constrains direction rather than precision.

Two orthogonal checks behave as required and one does not. GSE195519 compares human dermal
microvascular endothelium with induced endothelial progenitors. In that dataset the CNS_VASCULAR
module is again the more endothelial (z = +6.43, against +3.55 for MYELOID_CYTOKINE and −0.72
for the hepatocyte control; Figure 4B). The localization is endothelial, not merely cerebral.
Primary human brain microvascular endothelium challenged with TNF-α (GSE211439) induces the
CNS_VASCULAR module (+0.475 log₂FC, z = +5.36, p < 10⁻⁴). It also induces MYELOID_CYTOKINE, and
more strongly (**+2.015**, z = +15.5) (Figure 4C). Inducibility is not specificity. The
cytokine program is a generic inflammatory response that endothelium can mount, and only the
spatial direction distinguishes the modules. This constrains the model rather than supporting
it, and it is carried into the failure analysis.

A quality gate changed a conclusion. The induced-brain-endothelial arm of GSE195519 expresses
barrier genes *SLC2A1* and *OCLN* but not *CLDN5*, *PECAM1* or *VWF*, and scored z = +0.67 for
the neurovascular module, which is uninterpretable. Had these samples carried the contrast, the
module would have appeared absent from brain endothelium. They were excluded, and the claim
rests on the HPA data and the dermal-endothelial contrast instead (Table S4).

## Network proximity cannot resolve the question

The interactome (OmniPath curated layers, 139,851 records, 10,156 nodes in the largest
component, mean degree 15.7) was used to ask whether the CD28 module lies closer to the
neurovascular module than the 4-1BB module does.

| statistic | CD28 | 4-1BB | reading |
|---|---|---|---|
| shortest-path distance to CNS_VASCULAR | 1.462 (z = −1.91) | 1.632 (z = −0.23) | both closer than random |
| RWR mass on CNS_VASCULAR | 7.55×10⁻³ (z = −0.48) | 5.61×10⁻³ (z = −0.64) | **both below random** |
| size-matched mass ratio, CD28/4-1BB | **1.34×** | — | 1,000/1,000 subsets > 1 |
| same ratio against 1,000 matched gene-set pairs | null median 0.99, SD 1.34 | **z = −0.04, p = 0.26** | **indistinguishable** |

The two standard statistics disagree in sign at the absolute level. The distance statistic
places CD28 closer to the neurovascular module than chance, while the random-walk mass places it
further, so we withdraw all absolute-proximity claims. What is left is the relative ordering,
which is identical under all three statistics. CD28 sits nearer the neurovascular module and
further from the myeloid module than 4-1BB does: distance 1.462 versus 1.632, RWR mass on
neurovascular 7.55×10⁻³ versus 5.61×10⁻³, and on myeloid 4.77×10⁻² versus 5.92×10⁻². A
consistent sign across statistics with different failure modes is worth recording even when none
is individually interpretable.

The size-matched ratio of 1.34× is stable but uninformative. It lies inside the distribution
produced by 1,000 matched random gene-set pairs (z = −0.04, p = 0.26).

The reason is arithmetic rather than biological. Inverting the null quantiles gives σ(log ratio)
= 0.88, and hence a **minimum detectable ratio of 11.9× at 80% power and α = 0.05**. The
observed 1.34× is an order of magnitude below what this design could have detected. Resolving it
would need approximately **1,361 genes**; nineteen were available (Figure 5). The test
did not refute the hypothesis. It was incapable of testing it, and the number that says so is
the most transferable result here. Proximity claims built on modules of tens of genes, evaluated
against degree-matched nulls, report the dispersion of the null rather than a property of the
biology.

Both numbers come from inverting a null, and an inverted null is only as good as the null. The
same statistic and the same 1,000-draw null were therefore applied to 43 pairs whose relatedness
does not depend on any choice of ours, and to 13 with no reason to be proximal (Additional file 1:
Table S13). Twelve of the 43 reached p < 0.05, and in fold units the boundary was sharp: no related
pair below 9.3-fold over the null mean reached significance, and every pair at or above 10.5-fold
did. The 40S and 60S ribosomal proteins, adjacent subunits of one machine, reached 25.6-fold. The
unrelated pairs mostly did not fire: two of the ten random pairs reached p < 0.05, one of them at
12.6-fold, while all three curated negative controls sat at p = 0.65 or above. The mechanism behind
those two is decile matching, which leaves an order of magnitude of degree spread inside the top
stratum, so a set of near-hub genes can beat its own null. The null is approximately calibrated,
and mildly anti-conservative at high degree.

A design of this size therefore begins to resolve genuine relatedness at about tenfold, which lands
the 11.9× just above a floor that can now be measured rather than asserted. The tenfold is a fold
in a single enrichment and the 11.9× is a ratio between two, so they are not the same quantity;
they agree in magnitude, and both place the working range of this design some sevenfold above the
1.34× contrast it was asked to test.

## The model narrows what can move the partition

The model makes one prediction that is not built into its structure. Because the endothelial
compartment tracks cytokine exposure through k_E/λ_E, the partition R = max E / max C should be
approximately k_E/λ_E. It should therefore be independent of every production-side parameter:
expansion rate, carrying capacity, cytokine production, clearance and initial dose.

That prediction holds only partially, and the way it fails is informative. Sweeping each
parameter over its stated range in an unsaturated regime (E_max = 10⁴), production-side
parameters move R by at most **12%**, while amplification-side parameters move it by **599%**
(Figure 6A). Letting endothelial injury approach its ceiling (E_max = 8) raises the
production-side figure to **68%**. Saturation is the only route by which a production-side
quantity can reach the partition.

The variance decomposition says the same thing with different arithmetic (Figure 6B). With
E_max at 10⁴, the total-order Sobol indices summed over production-side parameters are
**0.176**, against **1.453** for the amplification side; k_E0 and λ_E alone account for 0.667
and 0.605. Fixing E_max at 8 raises the production-side sum to **0.685** and lowers the
amplification sum to 1.182. The partition is dominated by the endothelial gain and its recovery
rate. Production-side quantities contaminate it in proportion to how close the endothelial
compartment runs to its ceiling.

A single multiplicative gain is not identifiable here: inverting the three group means returns
mutually inconsistent values (Discussion). The model is used for what it can support, which is
which quantities matter and in which direction, not as a calibrated predictor.

## What a future launch can and cannot settle

An interval for the next CD28 product would be the obvious way to close the paper, and it would
be dishonest. The interval would come from the two products already in the table and could not
be checked against a third. The widest defensible gap between the classes is 0.012, from the
highest 4-1BB estimate (obe-cel, 0.320) to the lowest CD28 estimate (axi-cel, 0.332). That is
about the half-width of the narrowest interval in Table 1 (±0.012). A forecast at that
precision restates the data rather than testing them.

Removing each product in turn and predicting it from the others of its class shows how much the
class label carries. The class-based predictor has a mean absolute error of **0.056**; a
class-blind predictor has **0.054**. We enumerated all 21 ways of assigning two of the
seven CAR-T products to the CD28 label. The observed grouping is no better than an arbitrary
grouping of the same shape (one-sided exact p = 0.24; Additional file 1: Table S8,
Figure 2B). The reason is within-class spread: tisa-cel (0.221) and obe-cel (0.320) share a
class, as do axi-cel (0.332) and brexu-cel (0.390). The costimulation effect is therefore a rank
effect, not a level predictor, and a single-product forecast inherits an error of roughly 0.06,
five times the between-class gap it is meant to resolve.

The prediction is therefore a rule about a threshold, with its resolution limit computed rather
than assumed. Take the highest observed 4-1BB value (0.320) as the boundary. A new CD28 product
**supports** the account when the Wilson lower bound of its partition exceeds 0.320, and
**refutes** it when the Wilson upper bound falls at or below 0.320. Otherwise the question is
undecidable. The number of reports at which a verdict becomes available depends on where the
product sits:

> A CD28 product at R = 0.250 is settled by 171 reports and one at 0.300 by 2,090. A product at
> 0.325 needs 33,437, more than any single product in this database has ever generated. Expressed
> at 6,500 reports, the largest sample any product here has reached, values between 0.309 and
> 0.331 cannot be resolved at all.

That band contains both the 4-1BB ceiling (0.320) and the lower CD28 estimate (0.332), so the
boundary on which the whole account turns is exactly where the data stop speaking (Table 3,
Figure 2C). What survives is asymmetric. Refutation is cheap: a CD28 product with at least
2,090 reports and R at or below 0.300, or any CD28 product landing in the bispecific range
(≤0.280 with ≥523 reports), would end the account. Confirmation is expensive, and needs either a
large series or a product well clear of the boundary.

This is a weaker claim than the interval first drafted, and it is the claim these data support.
It also tells the reader what to do next: state the rule in advance, count reports, and compare
intervals rather than point estimates.

---

# How this model fails

These are stated before the Discussion, so that the boundary is the authors' rather than a
reviewer's.

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

## Coarse-graining statement

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

---

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

---

# List of abbreviations

| Abbreviation | Expansion |
|---|---|
| BCMA | B-cell maturation antigen |
| BiTE | bispecific T-cell engager |
| CAR-T | chimeric antigen receptor T cell |
| CD | cluster of differentiation (CD19, CD20, CD28 as used in the text) |
| CI | confidence interval |
| CRS | cytokine release syndrome |
| EBGM | empirical Bayes geometric mean |
| EV | EudraVigilance |
| FAERS | FDA Adverse Event Reporting System |
| FDA | United States Food and Drug Administration |
| HPA | Human Protein Atlas |
| ICANS | immune effector cell-associated neurotoxicity syndrome |
| MedDRA | Medical Dictionary for Regulatory Activities |
| PT | preferred term (MedDRA) |
| ROR | reporting odds ratio |
| RWR | random walk with restart |
| TNF | tumor necrosis factor |

---

# Declarations

**Ethics approval and consent to participate.** Not applicable. All data are public,
aggregated and de-identified at source; no patient-identifiable information was accessed.
Under the UK NHS Health Research Authority guidance and the equivalent US provisions for
research on de-identified public data, this analysis does not constitute human-subjects
research.

**Consent for publication.** Not applicable.

**Availability of data and materials.** No new patient-level data were generated. The
source data are public: case-level reports came from the openFDA drug/event application
programming interface, the public interface to FAERS, queried once on 2026-11-16 for the two
preferred terms and frozen at 21,937 records; drug targets, the toxicity gene sets and the
signalling interactome from the ChEMBL, Open Targets and OmniPath interfaces; expression from
GEO (GSE211439, GSE195519) and the Human Protein Atlas; pathway membership from Reactome v98.
The endpoint, release, retrieval timestamp and SHA-256 of every input are recorded in the
deposit.

All derived materials are deposited at 10.5281/zenodo.24536543, a timestamped, immutable archive that
has been assigned a digital object identifier. The deposit contains the frozen extracts, every
result table and JSON behind a number in this paper, the six figures, the thirteen
supplementary tables, the pre-specified analysis plan, the complete analysis code with pinned
dependencies, and the SHA-256 version-lock record over all 70 objects
(`653a2416f76c50f0…dd4d0f`), so a reader can confirm that a re-run used the same inputs.
Re-running the case-level scripts from the deposited extract reproduces every file they write
byte for byte, and two scripts in the deposit recheck the result: `src/76_recount.py`
recomputes every per-product ratio independently of the pipeline that wrote it, and
`src/73_trace_numbers.py` matches all 108 numbers in the text to the file that produced each.

Four external objects are not redistributed, because their terms do not permit us to
re-license them: the OmniPath interactome, the Human Protein Atlas single-cell table, ChEMBL
target assignments and the DepMap matrix. Each is public, each is pinned in the deposit by
release and SHA-256, and each is re-fetched by the script that used it. Every reported number
can therefore be verified from the deposit alone; re-deriving the network statistics from raw
edges additionally requires re-fetching OmniPath at the pinned release.

The current code version is maintained at https://github.com/liugt2000/jtm-icans-crs-ratio, and the archived release cited here is
linked from the deposit record. The deposit is openly available, so editors and reviewers need
no separate access route; the same DOI resolves to the archived release. Deposited code is
released under the MIT licence, and deposited text, tables, figures and derived data under a
Creative Commons Attribution 4.0 International licence (CC BY 4.0), which permits reuse,
including commercial reuse, with attribution; redistributed third-party files and the public
source databases remain subject to their own terms of use.

Reference metadata were resolved against Crossref; all 26 references were checked against
PubMed, Crossref or the publisher record, and each of the 24 DOI-bearing entries was
re-resolved and checked back against the cited title, journal, first author and year
(`out/refs_verification.csv`), the full audit being tabulated in `audit/refs_pubmed.csv`.

**Code availability.** The pipeline runs from retrieval to figure as `src/00`–`src/96`;
`src/96_build_deposit.py` assembles the deposit described above. Every network call is cached and
hashed, every random seed is fixed and recorded in the JSON it produced, and figure-generating
scripts read only from `out/` and never from the network.

**Competing interests.** The authors declare that they have no competing interests. In the
interest of full disclosure, the authors are developing two immuno-oncology assets — an
oncolytic virus candidate and a TCR-T program. Neither is a chimeric antigen receptor T-cell
or a bispecific T-cell engager, neither is manufactured or licensed by any company whose
product appears in Table 1, and the authors hold no equity, consultancy, patent or advisory
relationship with any of those manufacturers.

**Funding.** [TO BE COMPLETED BY THE AUTHORS: funder name(s) and grant number(s), or "This
research received no specific grant from any funding agency in the public, commercial, or
not-for-profit sectors."] No funder had any role in design, analysis, interpretation, or
the decision to submit.

**Authors' contributions.** [TO BE COMPLETED BY THE AUTHORS using the CRediT taxonomy:
conceptualization; data curation; formal analysis; funding acquisition; investigation;
methodology; project administration; resources; software; supervision; validation;
visualization; writing — original draft; writing — review and editing. Every author must
appear against at least one role, and all authors must approve the submitted version.]

**Acknowledgements.** We thank the US Food and Drug Administration for maintaining FAERS and
providing openFDA, and the EMBL-EBI, Open Targets, Reactome, OmniPath and Human Protein Atlas
teams for the public resources used here. We thank the investigators who deposited GSE211439 and
GSE195519, and we are grateful to the reporters whose voluntary submissions make pharmacovigilance
possible.

**Use of generative artificial intelligence.** DeepSeek (model DeepSeek-V4.1-Flash) was used to
assist with language editing, manuscript formatting, and the drafting and debugging of analysis
code. It was also used, under the authors' direction, to compare candidate methodological options
and to explain statistical output in plain language. No suggestion was adopted on trust: each was
retained only after it had been checked against the deposited outputs and the pre-specified
decision rules, and every number in the manuscript is traced to the file in `out/` that produced
it. The tool generated no image — all six figures are drawn by plotting code from the deposited
data — and it is not an author. The authors take full responsibility for the content, including the
text, the code and the results.

---

# Additional files


**Additional file 1. Supplementary tables S1–S13.** Thirteen tables carrying the
substance-key normalisation, the exposure-role sensitivity, the EBGM hyperparameters, the
endothelial quality gate, the gene modules, the all-pairs proximity statistics, the
pre-2018 coding sensitivity, the leave-one-product-out prediction, the EudraVigilance
replication, the reporting strata, the severity proxy, the model parameters and the
positive control for the network null. (DOCX 54 KB)

**Additional file 2. RECORD/STROBE checklist.** The completed checklist for this
case-level pharmacovigilance analysis, item by item against the section of the manuscript
where each item is addressed. (DOCX 48 KB)

---

# References

> Every entry was resolved against Crossref (volume, issue, page, DOI) and then checked
> record-by-record against PubMed; where the two differ only in house style — "37(S1)" versus
> "37 Suppl 1", a section rubric such as "Proteomics." that PubMed prepends to a Science title
> — the printed form follows Crossref, because the DOI is the identifier of record. The five
> entries PubMed does not index (two statistics papers, one physics paper, one book chapter,
> one web resource) were verified against Crossref or, for the book chapter, against three
> independent printed citations of it. The audit is reproduced by `src/75_pubmed_verify.py`
> and written to `out/refs_pubmed.csv`. Numbering follows order of first citation.

1. Sterner RC, Sterner RM. CAR-T cell therapy: current limitations and potential strategies. *Blood Cancer Journal*. 2021;11(4):69. doi:10.1038/s41408-021-00459-7

2. Neelapu SS. Managing the toxicities of CAR T-cell therapy. *Hematological Oncology*. 2019;37(S1):48-52. doi:10.1002/hon.2595

3. Lee DW, Gardner R, Porter DL, Louis CU, Ahmed N, Jensen M, Grupp SA, Mackall CL. Current concepts in the diagnosis and management of cytokine release syndrome. *Blood*. 2014;124(2):188-195. doi:10.1182/blood-2014-05-552729

4. Lee DW, Santomasso BD, Locke FL, Ghobadi A, Turtle CJ, Brudno JN, et al. ASTCT consensus grading for cytokine release syndrome and neurologic toxicity associated with immune effector cells. *Biology of Blood and Marrow Transplantation*. 2019;25(4):625-638. doi:10.1016/j.bbmt.2018.12.758

5. Neelapu SS, Tummala S, Kebriaei P, Wierda W, Gutierrez C, Locke FL, et al. Chimeric antigen receptor T-cell therapy — assessment and management of toxicities. *Nature Reviews Clinical Oncology*. 2018;15(1):47-62. doi:10.1038/nrclinonc.2017.148

6. Gust J, Hay KA, Hanafi LA, Li D, Myerson D, Gonzalez-Cuyar LF, et al. Endothelial activation and blood–brain barrier disruption in neurotoxicity after adoptive immunotherapy with CD19 CAR-T cells. *Cancer Discovery*. 2017;7(12):1404-1419. doi:10.1158/2159-8290.cd-17-0698

7. Rubin DB, Danish HH, Ali AB, Li K, LaRose S, Monk AD, et al. Neurological toxicities associated with chimeric antigen receptor T-cell therapy. *Brain*. 2019;142(5):1334-1348. doi:10.1093/brain/awz053

8. Long AH, Haso WM, Shern JF, Wanhainen KM, Murgai M, Ingaramo M, et al. 4-1BB costimulation ameliorates T cell exhaustion induced by tonic signaling of chimeric antigen receptors. *Nature Medicine*. 2015;21(6):581-590. doi:10.1038/nm.3838

9. Zhao Z, Condomines M, van der Stegen SJC, Perna F, Kloss CC, Gunset G, et al. Structural design of engineered costimulation determines tumor rejection kinetics and persistence of CAR T cells. *Cancer Cell*. 2015;28(4):415-428. doi:10.1016/j.ccell.2015.09.004

10. Ahn MJ, Cho BC, Felip E, Korantzis I, Ohashi K, Majem M, et al. Tarlatamab for patients with previously treated small-cell lung cancer. *New England Journal of Medicine*. 2023;389(22):2063-2075. doi:10.1056/nejmoa2307980

11. DuMouchel W. Bayesian data mining in large frequency tables, with an application to the FDA spontaneous reporting system. *The American Statistician*. 1999;53(3):177-190. doi:10.1080/00031305.1999.10474456

12. Bate A, Evans SJW. Quantitative signal detection using spontaneous ADR reporting. *Pharmacoepidemiology and Drug Safety*. 2009;18(6):427-436. doi:10.1002/pds.1742

13. Weber JCP. Epidemiology of adverse reactions to nonsteroidal antiinflammatory drugs. In: Rainsford KD, Velo GP, editors. *Side-effects of anti-inflammatory drugs* (Advances in Inflammation Research, vol 6). New York: Raven Press; 1984. p. 1-7.

14. Harpaz R, DuMouchel W, Shah NH, Madigan D, Ryan P, Friedman C. Novel data-mining methodologies for adverse drug event discovery and analysis. *Clinical Pharmacology &amp; Therapeutics*. 2012;91(6):1010-1021. doi:10.1038/clpt.2012.50

15. Barabási AL, Gulbahce N, Loscalzo J. Network medicine: a network-based approach to human disease. *Nature Reviews Genetics*. 2011;12(1):56-68. doi:10.1038/nrg2918

16. Menche J, Sharma A, Kitsak M, Ghiassian SD, Vidal M, Loscalzo J, Barabási AL. Uncovering disease–disease relationships through the incomplete interactome. *Science*. 2015;347(6224):1257601. doi:10.1126/science.1257601

17. Guney E, Menche J, Vidal M, Barábási AL. Network-based in silico drug efficacy screening. *Nature Communications*. 2016;7(1):10331. doi:10.1038/ncomms10331

18. Benchimol EI, Smeeth L, Guttmann A, Harron K, Moher D, Petersen I, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. *PLOS Medicine*. 2015;12(10):e1001885. doi:10.1371/journal.pmed.1001885

19. von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC, Vandenbroucke JP. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *Annals of Internal Medicine*. 2007;147(8):573-577. doi:10.7326/0003-4819-147-8-200710160-00010

20. European Medicines Agency. EudraVigilance: European database of suspected adverse drug reaction reports [Internet]. Amsterdam: EMA; 2026 [cited 2026 Nov 21]. Available from: https://www.adrreports.eu

21. Uhlén M, Fagerberg L, Hallström BM, Lindskog C, Oksvold P, Mardinoglu A, et al. Tissue-based map of the human proteome. *Science*. 2015;347(6220):1260419. doi:10.1126/science.1260419

22. Karlsson M, Zhang C, Méar L, Zhong W, Digre A, Katona B, et al. A single-cell type transcriptomics map of human tissues. *Science Advances*. 2021;7(31):eabh2169. doi:10.1126/sciadv.abh2169

23. Türei D, Valdeolivas A, Gul L, Palú N, Montavi A, Ivanova O, et al. Integrated intra- and intercellular signaling knowledge for multicellular omics analysis. *Molecular Systems Biology*. 2021;17(3):e9923. doi:10.15252/msb.20209923

24. Wilson EB. Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*. 1927;22(158):209-212. doi:10.1080/01621459.1927.10502953

25. Schuemie MJ, Ryan PB, DuMouchel W, Suchard MA, Madigan D. Interpreting observational studies: why empirical calibration is needed to correct p-values. *Statistics in Medicine*. 2014;33(2):209-218. doi:10.1002/sim.5925

26. Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S. Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index. *Computer Physics Communications*. 2010;181(2):259-270. doi:10.1016/j.cpc.2009.09.018

---

# Figure legends

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

---

# Tables


# Table 1. Partition of the two hallmark phenotypes by product

Reports in which the product is the primary suspect, received 2019-01-01 or later, carrying either phenotype preferred term. R = ICANS/(ICANS + CRS); intervals are Wilson score intervals. "Also CRS" is the fraction of the product's ICANS reports that carry the CRS term as well. Products with fewer than 20 phenotype reports are shown but are not analyzed.

| Product | Modality | Costimulation | Target | Phenotype reports | ICANS | CRS | R | 95% CI | Also CRS |
|---|---|---|---|---|---|---|---|---|---|
| brexu-cel | CAR-T | CD28 | CD19 | 1546 | 603 | 943 | 0.390 | 0.366–0.415 | 0.766 |
| axi-cel | CAR-T | CD28 | CD19 | 6500 | 2159 | 4341 | 0.332 | 0.321–0.344 | 0.787 |
| obe-cel | CAR-T | 4-1BB | CD19 | 25 | 8 | 17 | 0.320 | 0.172–0.516 | 0.625 |
| liso-cel | CAR-T | 4-1BB | CD19 | 531 | 169 | 362 | 0.318 | 0.280–0.359 | 0.610 |
| cilta-cel | CAR-T | 4-1BB | BCMA | 1310 | 387 | 923 | 0.295 | 0.271–0.321 | 0.690 |
| teclistamab | BiTE | — | BCMA | 1254 | 342 | 912 | 0.273 | 0.249–0.298 | 0.591 |
| tarlatamab | BiTE | — | DLL3 | 1399 | 377 | 1022 | 0.269 | 0.247–0.293 | 0.504 |
| talquetamab | BiTE | — | GPRC5D | 733 | 188 | 545 | 0.256 | 0.226–0.289 | 0.569 |
| elranatamab | BiTE | — | BCMA | 545 | 134 | 411 | 0.246 | 0.212–0.284 | 0.463 |
| tisa-cel | CAR-T | 4-1BB | CD19 | 2104 | 465 | 1639 | 0.221 | 0.204–0.239 | 0.723 |
| ide-cel | CAR-T | 4-1BB | BCMA | 896 | 195 | 701 | 0.218 | 0.192–0.246 | 0.795 |
| blina | BiTE | — | CD19 | 1201 | 239 | 962 | 0.199 | 0.177–0.223 | 0.494 |
| epcoritamab | BiTE | — | CD20 | 1286 | 210 | 1076 | 0.163 | 0.144–0.184 | 0.514 |
| glofitamab | BiTE | — | CD20 | 1013 | 152 | 861 | 0.150 | 0.129–0.173 | 0.632 |
| afa-cel | CAR-T | — | MAGEA4 | 2 | 0 | 2 | 0.000 | 0.000–0.658 | — |



# Table 2. The CD28-versus-4-1BB contrast under nine analytic specifications

Δ is the difference in mean R. Both p values are exact, obtained by enumerating every label permutation. The one-sided value is 1/21 in a two-versus-five design, reached only under complete separation. The two-sided value counts assignments at least as extreme in absolute value; because the two groups are unequal in size, the mirror of an assignment is not itself a permutation, so it is not twice the one-sided value and can fall to 1/permutations — as it does in the two calendar-window rows.

| Specification | Δ | one-sided p | two-sided p | products | permutations | mean R, CD28 | mean R, 4-1BB |
|---|---|---|---|---|---|---|---|
| primary (pre-specified) | 0.087 | 0.048 | 0.095 | 7 | 21 | 0.361 | 0.274 |
| any-role exposure | 0.089 | 0.048 | 0.095 | 7 | 21 | 0.361 | 0.273 |
| monotherapy only | 0.091 | 0.048 | 0.095 | 7 | 21 | 0.364 | 0.273 |
| single-phenotype reports | 0.058 | 0.200 | 0.333 | 6 | 15 | 0.187 | 0.129 |
| exclude obe-cel (n=25) | 0.098 | 0.067 | 0.133 | 6 | 15 | 0.361 | 0.263 |
| threshold 50 reports | 0.098 | 0.067 | 0.133 | 6 | 15 | 0.361 | 0.263 |
| 2019-2022 only | 0.101 | 0.067 | 0.067 | 6 | 15 | 0.298 | 0.197 |
| 2023-2026 only | 0.095 | 0.048 | 0.048 | 7 | 21 | 0.399 | 0.304 |
| including pre-2019 reports | 0.081 | 0.143 | 0.190 | 7 | 21 | 0.353 | 0.272 |



# Table 3. The partition a future product would need, and how many reports to settle it

The rule is one-sided against the highest observed 4-1BB value (0.320): a new CD28-costimulated product supports the account when the Wilson lower bound of its partition exceeds 0.320, refutes it when the upper bound falls at or below 0.320, and is undecidable otherwise. A dash means no sample size decides the question. The reference column is the largest single-product sample in this database (axi-cel, n = 6,500); at that size the unresolvable band is 0.309–0.331.

| True R of the new product | Verdict at 6,500 reports | Reports needed for a verdict |
|---|---|---|
| 0.200 | refutes | 59 |
| 0.250 | refutes | 171 |
| 0.280 | refutes | 523 |
| 0.300 | refutes | 2,090 |
| 0.310 | undecidable | 8,360 |
| 0.320 | undecidable | — |
| 0.325 | undecidable | 33,437 |
| 0.330 | undecidable | 8,360 |
| 0.340 | supports | 2,090 |
| 0.360 | supports | 523 |
| 0.390 | supports | 171 |

---


