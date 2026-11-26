# Additional file 2 — RECORD / STROBE checklist

**Manuscript.** *The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in BCMA.*

**Statement.** This study reports a secondary analysis of a routinely collected
pharmacovigilance database, linked to public omics resources. It is reported against
STROBE (items 1–22) with the RECORD extension for routinely collected health data
(items 1.1, 6.1, 6.2, 7.1, 12.1–12.3, 13.1, 19.1, 22.1). Because the unit of analysis is a
*drug–event report* rather than a person, a number of STROBE items that presume a cohort
of individuals with defined eligibility are answered as *not applicable in that sense*, and
the substitute construct actually used is stated. Blanket "✓ compliant" entries would
misrepresent that substitution.

Section references use the manuscript's own headings. "Methods §FAERS, case level" means
the third-level heading *FAERS, case level* under *Methods*.

---

## Title and abstract

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 1 | 1.1 | Indicate the study's design in the title or abstract; specify the type of routinely collected data | Title; Abstract, *Methods* | The abstract names both the design and the source. Abstract, first sentence of *Methods*: "We analyzed 21,937 case-level reports … from the US Food and Drug Administration Adverse Event Reporting System". RECORD 1.1(a): the data are routinely collected. There is no linkage to a second person-level source, so the RECORD 1.1(b) linkage clause does not apply; where a second source *is* used (Human Protein Atlas, GEO, OmniPath) it is joined at the level of **gene symbol, not person**, and this is stated in Methods §Human brain cell-type expression. |
| 2 | — | Structured summary of what was done and found | Abstract | Structured as Background / Methods / Results / Conclusions. Every number in the abstract (record counts, R values, Δ, both p values, the network null result, the prediction interval) appears identically in Results or Table 1. |

## Introduction

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 3 | — | State the scientific background and rationale | Introduction | Frames the clinical problem (ICANS and CRS co-occur in most patients yet are graded and managed as separate syndromes) and the specific gap (no test of whether their *ratio* carries information beyond their sum). |
| 4 | — | State objectives, and any prespecified hypotheses | Introduction, *The proposition under test* | The objective is stated as a single falsifiable if–then proposition with three clauses (a)(b)(c), written before analysis and deposited as `protocol/Phase0_study_plan_zh.md`. Clause (c) is the refutation condition. This is the study's only primary hypothesis; all other analyses are declared secondary, sensitivity, or descriptive. |
| 5 | — | Describe setting, locations, relevant dates | Introduction; Methods §FAERS, case level | Reporting setting: spontaneous reports to a national regulator, worldwide reporters, 2004 Q1 – 2026 Q3. Analysis window 2019-01-01 onward (justified by the MedDRA introduction of the ICANS PT). |

## Methods

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 6 | 6.1 | Give eligibility criteria, sources and methods of selection of participants; **list in detail the codes/algorithms used to identify subjects**, or explain why not | Methods §FAERS, case level; §Phenotype definitions | The selection algorithm is given as executable specification: the two openFDA `search` strings, the pagination scheme (`limit=500`, three disjoint page ranges per PT, merged and de-duplicated on `(safetyreportid, safetyreportversion)`), the 31-row substance table (`config/substances.csv`) with suffix-variant merging rule, and the eligibility threshold (≥20 phenotype reports). The full substance list is Additional file 1: Table S1. Nothing in the selection is a free-text judgement call except the classification of each product into CD28 / 4-1BB / BiTE, which is enumerated in Table 1 so a reader can disagree. |
| 6 | 6.2 | Reference any validation studies of the codes/algorithms; if validated here, give methods and results | Methods §Phenotype definitions; Results, *Corrections to the aggregate endpoint* | No published validation study exists for the ICANS PT in FAERS, so we did not cite one. Instead we report three internal validity checks that function as calibration: (i) the co-report fraction (68.7 %) against the known clinical co-occurrence; (ii) an isolated-phenotype sensitivity analysis that strips co-reported cases and shows the effect attenuates but does not reverse (Δ 0.087 → 0.058); (iii) a negative-control set of drug–event pairs, with empirical calibration reported in Methods §Disproportionality. We state plainly that (i)–(iii) are consistency checks, not validation against adjudicated charts. |
| 7 | 7.1 | Give a **complete list of codes and algorithms** used to classify exposures, outcomes, confounders and effect modifiers | Methods §Phenotype definitions, §Module definitions; Additional file 1: Tables S1 and S5; `config/` | Exposures: `config/substances.csv` (31 rows, all named). Outcomes: `config/events.csv`, PTs by tier, with the MedDRA version stated for each PT (ICANS 21.0/2018; CRS all versions; legacy *Neurotoxicity* noted as not used in the primary analysis). Effect modifiers: costimulatory class (three levels, enumerated in Table 1). Gene modules: `config/engineered_modules.csv`, five modules with explicit membership, reproduced as Additional file 1: Table S5. **Confounders: none are adjusted for, because no adjustment set is identifiable in this data structure** — there is no denominator, no indication field usable as a proxy, and no consistent baseline covariate across reports. This is stated as a limitation rather than papered over; the design instead removes the market denominator structurally by using a ratio (see Item 9). |
| 8 | — | For each variable, give sources of data and details of methods of assessment | Methods §FAERS, case level; §Human brain cell-type expression; §Primary human brain microvascular endothelium; §Physical interactome | Each variable is traced to one of four raw layers: report fields (`patient.drug.drugcharacterization`, `drug_seq`, `receivedate`, `serious`, `occurcountry`, reaction PTs); HPA `rna_single_cell_type` nCPM; GEO counts matrices (GSE211439, GSE195519); OmniPath curated interactome with evidence codes. No pre-computed score, ranking or "target list" from a secondary database is used as primary evidence; the derived quantities (R, L, proximity z) are defined in Methods and computed from those layers. |
| 9 | — | Describe any efforts to address potential sources of bias | Methods §The partition metric; §Group contrast and its exact null; Results, *Corrections to the aggregate endpoint* | Four biases are addressed structurally rather than statistically. (i) *Reporting volume / market size* — removed by construction: R = ICANS/(ICANS+CRS) has no total-report denominator, so a product that is reported ten times more often has the same R if its phenotype mix is the same. (ii) *Version duplication* — removed by construction once it was verified that the public interface exposes one record per `safetyreportid`; this is reported as a measured fact, together with the residual limitation that `caseid` is not exposed, so cross-`safetyreportid` duplicates cannot be collapsed. (iii) *Exposure-role contamination* — measured, not assumed away: cyclophosphamide still carries `drugcharacterization = 1` in 570 ICANS reports and siltuximab in 33, so role filtering is reported with its own sensitivity table (Additional file 1: Table S2) and its limits are stated in the text. (iv) *Notoriety / time trend* — quantified as within-product drift (11/13 rising, median +0.066) and year-stratified Δ (positive in 7/8 years), so the reader can see how much of the effect is calendar. (v) *Severity confounding* — measured rather than asserted: the `serious` flag is degenerate (98.7%), so a term-level acuity proxy is used, and the contrast is recomputed on high-acuity reports only (Additional file 1: Table S11). |
| 10 | — | Explain how the study size was arrived at | Methods §FAERS, case level; §Network proximity and its power; Results, *The corpus* | The study size was not chosen; it is the complete eligible set (all reports matching the two PTs, 2019 onward). Power is therefore reported *post hoc* as a bound: for the network test, the minimum detectable ratio was inverted from the null distribution (11.9× at 80 % power) and set against the achievable module size (19 genes available vs 1,361 required). This converts an underpowered negative into a quantified one. For the primary partition test, power is bounded by the exact-null grid: with 2-vs-5 product groups the smallest attainable one-sided p is 1/21 = 0.048, and the observed two-sided p is 2/21 = 0.095 — not twice the one-sided value, because at unequal group sizes the mirror of an assignment is not itself a permutation. Both numbers are stated in the Results, not buried. |
| 11 | — | Explain how quantitative variables were handled; if applicable, which groupings and why | Methods §The partition metric; §Localization score and matched null | All continuous quantities are used on their natural scale with a stated transform: R on the proportion scale with Wilson intervals (not normal-approximation, because several products sit near the boundary and n is small); expression as log₂ CPM; localization as a log ratio L = log₂[(endothelial nCPM+1)/(myeloid nCPM+1)]; network proximity as an empirical z against 1,000 matched gene-set pairs. Groupings are three costimulation classes (CD28, 4-1BB, BiTE) — chosen because they are the licensed distinction, not because they maximized separation. No continuous variable was dichotomized at a data-derived cut-point. |
| 12 | 12.1 | Describe the extent to which investigators had access to the database population used to create the study population | Methods §FAERS, case level; Declarations | Full access to the public openFDA `drug/event` endpoint, and to nothing else: no restricted or internal FAERS fields, no `caseid`, no narrative text, no follow-up. The extract was pulled by the authors, not supplied by the regulator. This is stated so that the reader knows the ceiling on what could have been measured. |
| 12 | 12.2 | Describe the extent to which investigators had access to the database used to create the study population | Methods §FAERS, case level; §Software and code | Identical scope to 12.1 (single database). Cleaning steps are enumerated in the order applied — BOM stripping on config files, suffix-variant merging with summed denominators, de-duplication on `(safetyreportid, safetyreportversion)`, the 2019 window, the ≥20-report eligibility threshold — with the record count surviving each step (21,937 → 20,732 → 14 eligible products). The counts are given so that a reader can audit attrition without re-running anything. |
| 12 | 12.3 | State whether the study used a subset of the data or the whole population, and why | Methods §FAERS, case level | The study used the **whole** eligible population meeting the two-PT query, restricted in time (2019 onward, 1,205 records excluded, 5.5 %) and in product eligibility (≥20 phenotype reports). Both restrictions are stated with their counts and their reasons: the time restriction follows the MedDRA PT's introduction, the product threshold prevents unstable proportions from products with a handful of reports. Neither is data-driven in the sense of being tuned to the outcome. |
| 13 | 13.1 | Describe **in detail** the selection of persons included, including filtering on data quality, availability and linkage; text and/or flow diagram | Methods §FAERS, case level; Results, *The corpus*; Figure 1 | Selection is given as a counted sequence in the text rather than a flow diagram, because the exclusions are filters on *reports* not on *persons* and a STROBE-style participant flow would imply a cohort that does not exist. Counts: 5,929 ICANS reports and 20,080 CRS reports in the frozen database, of which 4,072 carry both terms, giving 21,937 distinct reports; the 2019 window removes 1,205, leaving 20,732, of which 5,927 carry ICANS and 4,070 carry both; 15 products appear in the window and 14 meet the ≥20-report threshold. Every count is recomputed from the deposited extract. |
| 14 | — | Give characteristics of study participants and information on exposures and potential confounders | Table 1; Results, *The corpus* | The analogue of a characteristics table is Table 1: per product, the report counts by phenotype, co-report fraction, and R with interval. Report-level characteristics that exist and are used: reporter qualification, serious flag, country, year. Characteristics that would normally be tabled but **do not exist in this data structure** — age, sex, baseline disease stage, prior lines of therapy, tumor type — are named as absent rather than omitted silently; where age and sex are populated in a minority of reports we do not use them, because the missingness is not random across products. |
| 15 | — | Report numbers of individuals at each stage; reasons for non-participation | Results, *The corpus*; Methods §FAERS, case level | Counts at each stage are given (see Item 13). "Non-participation" has no analogue; the corresponding quantity is the number of reports excluded by each filter, which is given. |
| 16 | — | Give unadjusted estimates; consider adjusting | Results, all subsections | All reported estimates are unadjusted, and the paper says so. There is no multivariable model, and no propensity or regression adjustment is presented, because the data structure does not support one: with no denominator and no consistent covariate set, an adjusted estimate would be a false reassurance. The one place a model *is* used — the three-variable ODE — is a mechanistic constraint model, not a confounder-adjustment model, and is labeled as such. |
| 17 | — | Report other analyses done | Results, *Corrections to the aggregate endpoint*; *Network proximity cannot resolve the question*; *The model narrows what can move the partition*; Table 2; Figure 2 | The other analyses are not appended as an afterthought but placed where they bear on the primary claim: nine-specification multiverse (Table 2, Figure 2A), isolated-phenotype sensitivity, any-role and monotherapy sensitivity, within-product drift, year-stratified Δ, temporal rank correlation, EBGM as a negative-control-only statistic, and the ODE variance decomposition. Direction is preserved in 9/9 specifications; one-sided p < 0.05 in 4/9. Both counts are reported, and the paper does not claim robustness it does not have. |

## Results

*(Items 14–17 above are cross-listed here because in this design the "participant
characteristics" and "main results" tables are the same table.)*

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 18 | — | Summarize key results with reference to study objectives | Results; Abstract | The primary result is stated once, in the terms of the proposition: R orders CD28 > 4-1BB > BiTE (0.361 / 0.274 / 0.222), Δ = +0.087, one-sided p = 0.048, two-sided p = 0.095. The ordering of clause (a) is confined to CD19 and **fails within BCMA**, and that failure is a Results subsection, not a Discussion caveat. Clause (b) holds only in part: the modules localize in opposite directions across brain cell types, but both are induced in brain endothelium, which removes inducibility as evidence of specificity. |

## Discussion

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 19 | 19.1 | Discuss limitations, **including the implications of using data not collected to answer the question**: misclassification, unmeasured confounding, missing data, changing eligibility over time | Discussion, *Limitations*; *What the data do not support*; How this model fails | Seven numbered limitations, each with its direction of effect where knowable. RECORD 19.1 is addressed explicitly and at length: (i) *misclassification* — the ICANS PT is applied by reporters, not adjudicators, and the isolated-phenotype analysis quantifies how much of the effect could be coding (Δ falls to 0.058, p 0.200); (ii) *unmeasured confounding* — indication, line of therapy and tumor burden are absent, and costimulation is perfectly confounded with antigen in the CD28 arm, which is stated as the single most important threat; (iii) *missing data* — age and sex are sparsely and non-randomly populated and are therefore unused; (iv) *changing eligibility over time* — the PT did not exist before 2018, reporting practice drifted, and both are measured (within-product drift, year-stratified Δ) rather than assumed absent. |
| 20 | — | Discuss interpretation considering objectives, limitations, multiplicity, similar studies, other relevant evidence | Discussion, *What the data support* / *do not support*; *Implications* | Interpretation is split into five things the data support and five they do not, so the boundary is visible. Multiplicity: the primary test is single and pre-specified and is the only inferential claim; the nine specifications, the nine strata and the severity endpoints are reported as distributions with their own attainable floors, and no secondary p value is presented as confirmatory. No BH-FDR is applied, because no family of confirmatory hypotheses exists to adjust; the choice and its cost are stated in Methods (*Multiplicity*). Comparison with similar work is confined to what is actually comparable (published CRS/ICANS incidence by construct), and the paper declines to compare its R values to trial incidences, because the denominators are not the same object. |
| 21 | — | Discuss the generalizability of the results | Discussion, *Limitations* (item 7); *Implications* | Generalizability is bounded in three directions: to other jurisdictions (spontaneous reporting culture differs; the European replication reproduces the ordering, Δ = 0.141 and ρ = 0.92, at a lower absolute level), to other antigens (the BCMA inversion shows the ordering is not universal), and to other time periods (drift is positive, so R values are not transportable across years). |

## Other information

| Item | RECORD | Requirement | Where | How addressed |
|---|---|---|---|---|
| 22 | 22.1 | Give sources of funding and role of funders; **provide information on how to access supplemental information: protocol, raw data, programming code** | Declarations; Methods §Software and code; `data_registry/` | Funding and funder role: Declarations, *Funding* — three named grants; no funder had any role in design, analysis, interpretation or the decision to submit. Access: the protocol is deposited as `protocol/Phase0_study_plan_zh.md`; raw inputs and every derived output are listed with SHA-256 digests in `data_registry/MANIFEST.md` (70 files, aggregate digest `653a2416…`); the pipeline is sixty-one numbered Python scripts, `src/00` to `src/99`, with pinned dependencies; figure scripts read only the deposited result files. The reproducibility statement is explicit that for a quarterly-updated database the deposited extract, not the retrieval script, is the reproducible object. |

---

## Deviations from the pre-specified protocol

They are recorded here because a reader checking the deposited protocol against the paper
will find them, and none of them should have to be guessed at.

1. **The network-proximity analysis was demoted from a co-primary endpoint to a bounded
   negative.** The protocol pre-specified proximity as a supporting line of evidence. It
   returned 1.34× against a null z of −0.04 (p = 0.26), and the power inversion showed the
   available module (19 genes) is two orders of magnitude short of what the test needs
   (1,361). The absolute claim was withdrawn; the relative ordering across product classes
   is retained with all three statistics quoted. This is a change of interpretation, not of
   data, and it is disclosed in the Results subsection title itself.
2. **The endothelium-specific localization contrast (HDMEC − iPC) was retained after a QC
   failure in one dataset.** GSE195519's iBMEC line does not express *CLDN5* (0.18),
   *PECAM1* (0.13) or *VWF* (0.68), so it was excluded from localization claims. The
   contrast is computed from the lines that pass the gate, and the failing values are
   tabulated (Additional file 1: Table S4) rather than described as "not detectable".
3. **No fitted β is reported from the model.** The inversion of the observed Δ against the
   model gave inconsistent estimates (0.47 / 0.62 / 0.92) depending on which constraint was
   used, so no point estimate is offered. The model is used only for its ordering
   predictions and its variance decomposition.
4. **The exact-null floor was reported as a design property, not a caveat.** With 2-vs-5
   groups the one-sided p cannot go below 0.048, and the observed two-sided p is 0.095.
   The paper states that the design, not the effect size, sets these numbers — and relies
   on the one-sided floor (attained under complete separation), the specification curve,
   and the independent replication in EudraVigilance for support.
5. **A severity proxy was added after the protocol was frozen, and is reported as
   descriptive.** The protocol recorded that FAERS carries no grading and treated severity as
   a limitation of the design. The `serious` flag and term-level acuity signatures turned out to
   be available substitutes, so both were examined; the acuity terms were fixed before the
   contrast was computed, and nothing in the analysis depends on values chosen after seeing it.
   It is reported in Results and Additional file 1: Table S11, with its own attainable p, and is not
   presented as confirmatory.

## Items that are not applicable, and why

| STROBE item | Why not applicable |
|---|---|
| 6 (participant eligibility, in the cohort sense) | The unit is a report, not a person; there is no enrolment and no eligibility in the clinical-trial sense. The substitute — product eligibility by report count — is given in Item 6.1. |
| 10 (study size / sample-size calculation) | The sample is the complete eligible set; there is nothing to size. Replaced by a post-hoc power bound, Item 10. |
| 15 (numbers at each stage, non-participation) | No participants; replaced by report counts surviving each filter. |
| 21 (generalizability, in the trial sense) | Addressed, but not by transportability arguments from a trial population; see Item 21. |

---

*Prepared to accompany the submission. Section references follow the headings of the
manuscript.*
