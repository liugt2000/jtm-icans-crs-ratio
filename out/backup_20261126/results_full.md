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
