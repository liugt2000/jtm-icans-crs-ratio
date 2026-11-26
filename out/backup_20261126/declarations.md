# Declarations

**Ethics approval and consent to participate**

Not applicable. All data are public, aggregated and de-identified at source; no
patient-identifiable information was accessed. Under the UK NHS Health Research Authority
guidance and 45 CFR 46, this analysis of de-identified public data does not constitute
human-subjects research, and no ethics committee approval or informed consent was required.

**Consent for publication**

Not applicable. This manuscript contains no individual person's data in any form.

**Availability of data and materials**

No new patient-level data were generated. The source data are public: case-level reports came
from the openFDA drug/event application programming interface, the public interface to FAERS,
queried once on 2026-11-16 for the two preferred terms and frozen at 21,937 records; drug
targets, toxicity gene sets and the signalling interactome from the ChEMBL, Open Targets and
OmniPath interfaces; expression from GEO (GSE211439, GSE195519) and the Human Protein Atlas;
pathway membership from Reactome v98. The endpoint, release, retrieval timestamp and SHA-256 of
every input are recorded in the deposit.

All derived materials are deposited at https://doi.org/10.5281/zenodo.24536543 — a timestamped,
immutable archive that has been assigned a digital object identifier. The deposit contains the
frozen extracts, every result table and JSON behind a number in this paper, the six figures, the
thirteen supplementary tables, the prespecified analysis plan, the SHA-256 version-lock record
over all 70 objects (`653a2416f76c50f0…dd4d0f`), and the complete analysis code with pinned
dependencies; the pipeline runs from retrieval to figure as `src/00`–`src/96`, with every
network call cached and hashed, every random seed written into the JSON it produced, and
figure-generating scripts reading only from `out/` and never from the network. Re-running the
case-level scripts from the deposited extract reproduces every file they write byte for byte;
`src/76_recount.py` recomputes every per-product ratio independently of the pipeline that wrote
it, and `src/73_trace_numbers.py` matches all 108 numbers in the text to the file that produced
each. The current code version is maintained at https://github.com/liugt2000/jtm-icans-crs-ratio,
and the archived release cited here is linked from the deposit record. The deposit is openly
available, so editors and reviewers need no separate access route; the same DOI resolves to the
archived release. Deposited code is released under the MIT license, and deposited text, tables,
figures and derived data under a Creative Commons Attribution 4.0 International license
(CC BY 4.0), which permits reuse, including commercial reuse, with attribution; redistributed
third-party files and the public source databases remain subject to their own terms of use.

Four external objects are not redistributed, because their terms do not permit us to re-license
them: the OmniPath interactome, the Human Protein Atlas single-cell table, ChEMBL target
assignments and the DepMap matrix. Each is public, each is pinned in the deposit by release and
SHA-256, and each is re-fetched by the script that used it. Every reported number can therefore
be verified from the deposit alone; re-deriving the network statistics from raw edges
additionally requires re-fetching OmniPath at the pinned release.

Reference metadata were resolved against Crossref; all 26 references were checked against
PubMed, Crossref or the publisher record, and each of the 24 DOI-bearing entries was re-resolved
against the cited title, journal, first author and year (`audit/refs_pubmed.csv`).

**Competing interests**

The authors declare that they have no competing interests. In the interest of full disclosure,
the authors are developing two immuno-oncology assets — an oncolytic virus candidate and a TCR-T
program. Neither is a chimeric antigen receptor T-cell or a bispecific T-cell engager, neither
is manufactured or licensed by any company whose product appears in Table 1, and the authors
hold no equity, consultancy, patent or advisory relationship with any of those manufacturers.

**Funding**

The study was partly supported by Natural Science Foundation of Zhejiang Province, Exploration
Project (LY22H290002), China Postdoctoral Science Foundation (2023M733565) and National Natural
Science Foundation of China (81871861, 82004129).

**Authors' contributions**

Y.Z. conceived and designed the study, performed the data extraction and statistical analysis,
and drafted the manuscript. H.W. contributed to the prespecified definitions and the clinical
interpretation of the results. C.Z. conducted project administration, resources and software
validation. G.L. supervised the project and critically revised the manuscript. All authors read
and approved the final manuscript.

**Acknowledgements**

We thank the US Food and Drug Administration for maintaining FAERS and providing openFDA, and
the EMBL-EBI, Open Targets, Reactome, OmniPath and Human Protein Atlas teams for the public
resources used here. We thank the investigators who deposited GSE211439 and GSE195519, and we
are grateful to the reporters whose voluntary submissions make pharmacovigilance possible.

**Use of generative artificial intelligence**

DeepSeek (model DeepSeek-V4.1-Flash) was used to assist with language editing, manuscript
formatting, and the drafting and debugging of analysis code. It was also used, under the
authors' direction, to compare candidate methodological options and to explain statistical
output in plain language. No suggestion was adopted on trust: each was retained only after it
had been checked against the deposited outputs and the prespecified decision rules, and every
number in the manuscript is traced to the file in `out/` that produced it. It generated no
image — all six figures are drawn by plotting code from the deposited data. The authors take
full responsibility for the content, including the text, the code and the results.
