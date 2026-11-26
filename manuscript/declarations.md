# Declarations

**Ethics approval and consent to participate**

Not applicable. All data are public, aggregated and de-identified at source; no
patient-identifiable information was accessed. Under the UK NHS Health Research Authority
guidance and 45 CFR 46, this analysis of de-identified public data does not constitute
human-subjects research, and no ethics committee approval or informed consent was required.

**Consent for publication**

Not applicable. This manuscript contains no individual person's data in any form.

**Availability of data and materials**

No new patient-level data were generated. The sources are public: case-level reports from the
openFDA drug/event interface, the public interface to FAERS, queried once on 2026-11-16 and frozen
at 21,937 records; drug targets, toxicity gene sets and the interactome from the ChEMBL, Open
Targets and OmniPath interfaces; expression from GEO (GSE211439, GSE195519) and the Human Protein
Atlas; pathway membership from Reactome v98. Release, retrieval timestamp and SHA-256 of every
input are recorded in the deposit.

All derived materials are deposited at https://doi.org/10.5281/zenodo.24536542, which resolves to
the most recent version of a timestamped archive with a DOI, so editors and reviewers need no
separate access route. It holds the
frozen extracts, every result table and JSON behind a number here, all figures and supplementary
tables, the prespecified analysis plan, the SHA-256 lock over the 70 deposited objects
(`653a2416…dd4d0f`), and the code with pinned dependencies and every seed written into the JSON it
produced. Re-running the case-level scripts from the deposited extract reproduces every file they
write byte for byte. A second script re-derives every per-product ratio from the deposited extract
alone, and a third re-checks every reported number against the file that produced it. Code is kept
at https://github.com/liugt2000/jtm-icans-crs-ratio. Text,
tables, figures and derived data are released under CC BY 4.0 and code under the MIT license;
third-party files remain subject to their own terms.

Four external objects are not redistributed, because their terms do not permit re-licensing: the
OmniPath interactome, the Human Protein Atlas single-cell table, ChEMBL target assignments and the
DepMap matrix. Each is public, pinned in the deposit by release and SHA-256, and re-fetched by the
script that used it. Every reported number is therefore verifiable from the deposit alone. The
network models are the one layer that additionally needs the raw edges, and the scripts use only
the gene-pair columns of the interactome, which the recorded query re-supplies; OmniPath carries no
release numbers, so a later export is checked against the recorded SHA-256 rather than assumed
identical.

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
number in the manuscript is traced to the deposited output that produced it. It generated no
image — all six figures are drawn by plotting code from the deposited data. The authors take
full responsibility for the content, including the text, the code and the results.
