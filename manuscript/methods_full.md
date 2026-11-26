# 2. Methods

## 2.1 Study design and reporting

Retrospective pharmacovigilance analysis of spontaneous reports, combined with public
transcriptomic and interactome data and a deterministic model. The analysis plan covers the
endpoint, phenotype definitions, null models, negative controls and failure criteria. It was
written before any data were retrieved and is deposited with the code, and its timestamp
precedes the timestamp of the retrieval log deposited with the code. Reporting follows RECORD [18,19], with
the checklist as Additional file 2. All records are public and de-identified at source.

## 2.2 Data sources

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

## 2.3 Phenotype definitions

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

## 2.4 The partition metric

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

## 2.5 Severity proxy

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

## 2.6 Group contrast and its exact null

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

## 2.7 Generalization: leave-one-product-out

Each eligible CAR-T product was removed in turn and its R predicted from the mean of the
remaining products **in its class**, with the comparator predicted from all remaining products
regardless of class. The quantity tested is not absolute error but the improvement of the
class-based over the class-blind predictor. It is evaluated against **every** alternative
assignment of two of the seven products to the CD28 label (21 assignments, enumerated exactly).
With two CD28 products, the leave-one-out prediction for a CD28 product rests on a single donor
and its error is not an independent estimate of within-class generalization. Results say so
rather than adjusting for it.

## 2.8 Resolution limit of the prediction

For a candidate true R and sample size *n*, the Wilson interval is formed. The verdict is
*supports* when the lower bound exceeds the highest observed 4-1BB value, *refutes* when the
upper bound falls at or below it, and undecidable otherwise. The smallest *n* admitting a
verdict was found by bisection to integer resolution over candidate values from 0.15 to 0.45 in
steps of 0.0025. The sample size at which the unresolvable band is quoted is the largest
single-product denominator the dataset contains rather than a round number, so the limit is
expressed in units this database has produced.

## 2.9 Disproportionality (secondary, negative control only)

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

## 2.10 Module definitions

Five gene sets were fixed before any expression data were inspected. `CNS_VASCULAR` holds 39
genes of endothelial junction, basement membrane, pericyte and astrocyte endfoot.
`MYELOID_CYTOKINE` holds 35 genes of the systemic cytokine program of monocytes and macrophages.
`COSTIM_CD28` (26 genes) and `COSTIM_41BB` (19) serve as construct-level comparators, and
`HEPATOCYTE_NEGCTRL` (17) as a module with no reason to be enriched in either the brain or the
myeloid compartment. Gene lists and provenance are in Additional file 1: Table S5.

## 2.11 Localization score and matched null

For each gene the localization score is

    L = log2( (endothelial nCPM + 1) / (myeloid nCPM + 1) )

and a module's statistic is the mean of L over its members. The null is a matched random gene
set: 10,000 draws of the same size from the 20,151 assayed genes, stratified on expression
decile so that the null does not merely reproduce the abundance–specificity relationship. The
interaction contrast Δ = mean(L | CNS_VASCULAR) − mean(L | MYELOID) was tested by drawing both
null sets independently in each of 10,000 permutations.

The z values reported for the drawn nulls in this paper express the observed statistic in
standard deviations of its own null. Because these nulls are drawn rather than enumerated, an
independent rerun of the same scripts displaces z by at most 0.15, and no verdict rests on a
difference that small.

## 2.12 Network proximity and its power

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

## 2.13 Mechanistic model

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

## 2.14 Software and code

All computation ran in Python 3.13 with pinned dependencies (`requirements.txt` in the deposit),
and every random seed is written into the JSON that records the parameters of the output it
produced. The DeepSeek assistant (DeepSeek-V4.1-Flash) was used to draft and debug this code and
to compare candidate methodological options; each suggestion was checked against the deposited
outputs before it was adopted, and the authors executed and verified every script. The full
disclosure is in the Declarations.
