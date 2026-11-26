26 November 2026

The Editorial Office

Journal of Translational Medicine

Special Issue: Computational Modeling and Network Medicine in Drug Toxicology and Clinical
Pharmacovigilance

Dear Editors,

Please consider the enclosed manuscript, "The ICANS/CRS ratio tracks costimulation within
CD19 and does not hold in BCMA", for publication as a Research article in the special issue
above.

The question it addresses is whether the dissociation between neurotoxicity and cytokine
release belongs to the therapeutic construct or to the patient who receives it. Across
20,732 case-level reports on 14 T-cell-engaging products, the ICANS/CRS ratio orders by
costimulatory architecture within CD19 products, does not hold within BCMA, and is
confounded with antigen in the single contrast that carries the main claim.

We submit it to this special issue because its most transferable result is a bound on a
network method rather than a network finding. The pre-specified proximity test returned
1.34-fold against a minimum detectable effect of 11.9-fold: detecting an effect of that size
at 80% power would require 1,361 genes, and the curated modules hold 19. Reported without
that number, the null is uninformative; reported with it, the result becomes a design
specification that any group can apply before running a proximity analysis. The same
discipline governs the primary endpoint, where exact enumeration fixes the smallest
attainable one-sided p at 1/21 and the resolution limit of 0.309–0.331 is stated rather than
implied.

Every layer is primary data: FDA FAERS case-level records, EudraVigilance counts retrieved
independently, Human Protein Atlas single-nucleus expression, GEO perturbation series, and
curated interaction databases. Seventy files are deposited with full SHA-256 digests
(aggregate `653a2416f76c50f0236f80d2ebdc7a1cbec98b1cfc577ee9b795ed00b2dd4d0f`); the pipeline
runs from retrieval to figure as `src/00`–`src/96`; the derived results, the frozen inputs and
the code are deposited at 10.5281/zenodo.24536542, and a RECORD/STROBE checklist is enclosed.

The manuscript is not under consideration elsewhere and all authors have approved it. In the
interest of disclosure, the competing-interests statement notes two in-house
immuno-oncology programs, neither of which is a CAR-T or bispecific product analyzed here.

In the same interest, the DeepSeek assistant (DeepSeek-V4.1-Flash) was used for language editing,
manuscript formatting and the drafting and debugging of analysis code, and, under our direction, to
compare candidate methodological options; each suggestion was adopted only after it had been
checked against the deposited outputs. The tool is not an author, and we take full responsibility
for the content, as stated in the Declarations.

Yours sincerely,

Gentao Liu

Shanghai Pulmonary Hospital, School of Medicine, Tongji University, 507 Zhengmin Rd,
Yangpu District, Shanghai, China

liugt@cellpeutics.cn
