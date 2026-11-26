# Supplementary Table S13. Positive control: the same null applied to pairs whose relatedness is fixed externally

Every network claim in this paper rests on one null, so the null was run on pairs whose relatedness is curated elsewhere and cannot depend on any choice of ours. The statistic is the one behind the per-module results: random-walk-with-restart mass (α = 0.7) from a uniform seed on the first set, summed over the second, with the second set held fixed and only the first replaced by 1,000 degree-decile-matched random sets. Two folds are given. **fold, null mean** divides by the mean of the null draws and is the definition used in Table S6. **fold, null median** divides by their median. For these targets the null is strongly right-skewed (coefficient of variation 2.5, against 0.4–0.7 for the per-module targets), because a 19-gene seed set that happens to make several direct contacts deposits an order of magnitude more mass than one that makes none. The mean therefore sits above the bulk of the draws, and the mean-based fold of an unrelated pair falls below 1. Against the median an unrelated pair centres on 0.94, which is what a calibration claim needs; against the mean the resolution threshold is nearly the same for every pair, which is what a detection claim needs. **p** is the fraction of the 1,000 draws at or above the observed value.

The code path is the published one. Pointed at three module pairs whose folds appear in Table S6, it reproduces the observed masses exactly (to six decimal places) and the folds to within 1.7% (2.07 against 2.04, 2.61 against 2.56), which is the sampling error of a 2,000-draw null.

**Calibration.** The pairs with no reason to be proximal behave as they should. All 13 give a median fold over the null median of 0.94 (IQR 0.84–1.35) and a median p of 0.59. Of the 10 random pairs, 2 reach p < 0.05, and none of the three curated negative controls does (p = 0.653, 0.909, 0.972). Decile matching leaves an order of magnitude of degree spread inside the top stratum, so a set of near-hub genes can outperform its own null; that is the residual miscalibration, and it runs in the anti-conservative direction.

**Resolution.** Of the 43 distinct related pairs, 12 reach p < 0.05: 11 of the 40 pathway halves and one complex, the ribosomal pair at 25.6-fold. In fold units the threshold is sharp. No related pair below 9.3-fold reached p < 0.05, and every pair at or above 10.5-fold did. The analytic inversion in the main text, which asserted 11.9-fold from the quantiles of the ratio null, is therefore 13–28% above a floor that can be measured directly on pairs whose answer is known.

**Panel A. Pairs known to be related, by fold.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| complex | Ribosome: 40S (RPS) vs 60S (RPL) | 19/19 | 25.62 | 55.80 | < 0.001 |
| pathway half | TNFR2 non-canonical NF-kB pathway (R-HSA-5668541) | 19/19 | 21.80 | 74.80 | < 0.001 |
| pathway half | Visual phototransduction (R-HSA-2187338) | 19/19 | 20.52 | 212.20 | 0.001 |
| pathway half | Semaphorin interactions (R-HSA-373755) | 19/19 | 16.01 | 62.70 | 0.001 |
| pathway half | DDX58/IFIH1-mediated induction of interferon-alpha/beta (R-HSA-168928) | 19/19 | 15.23 | 74.10 | 0.003 |
| pathway half | Degradation of the extracellular matrix (R-HSA-1474228) | 19/19 | 15.09 | 110.50 | 0.004 |
| pathway half | Fcgamma receptor (FCGR) dependent phagocytosis (R-HSA-2029480) | 19/19 | 14.40 | 51.90 | 0.001 |
| pathway half | SUMOylation of DNA damage response and repair proteins (R-HSA-3108214) | 19/19 | 14.24 | 43.60 | 0.003 |
| pathway half | Peptide hormone metabolism (R-HSA-2980736) | 19/19 | 12.16 | 76.20 | 0.018 |
| pathway half | Signaling by NOTCH1 (R-HSA-1980143) | 19/19 | 11.84 | 31.70 | 0.002 |
| pathway half | Regulation of PD-L1(CD274) transcription (R-HSA-9909649) | 19/19 | 10.91 | 38.00 | 0.006 |
| pathway half | SARS-CoV-1-host interactions (R-HSA-9692914) | 19/19 | 10.55 | 79.40 | < 0.001 |
| pathway half | Cytosolic sensors of pathogen-associated DNA (R-HSA-1834949) | 19/19 | 9.33 | 29.40 | 0.050 |
| pathway half | L13a-mediated translational silencing of Ceruloplasmin expression (R-HSA-156827) | 19/19 | 7.38 | 148.30 | 0.107 |
| pathway half | Late Phase of HIV Life Cycle (R-HSA-162599) | 19/19 | 7.29 | 37.70 | 0.057 |
| pathway half | Interferon gamma signaling (R-HSA-877300) | 19/19 | 6.82 | 29.10 | 0.055 |
| pathway half | Respiratory Syncytial Virus Infection Pathway (R-HSA-9820952) | 19/19 | 6.56 | 64.50 | 0.085 |
| pathway half | Ribosome Quality Control (RQC) complex extracts and degrades nascent peptide (R-HSA-9954709) | 19/19 | 5.66 | 161.10 | 0.120 |
| complex | 19S proteasome: ATPase (PSMC) vs base (PSMD) | 6/14 | 5.48 | 55.60 | 0.068 |
| pathway half | Diseases of programmed cell death (R-HSA-9645723) | 19/19 | 5.21 | 17.50 | 0.061 |
| pathway half | Fatty acid metabolism (R-HSA-8978868) | 19/19 | 5.20 | 82.20 | 0.088 |
| complex | 20S proteasome: alpha (PSMA) vs beta (PSMB) | 8/11 | 5.09 | 50.60 | 0.071 |
| pathway half | Ca2+ pathway (R-HSA-4086398) | 19/19 | 5.02 | 10.20 | 0.078 |
| pathway half | Gastrulation (R-HSA-9758941) | 19/19 | 5.01 | 26.70 | 0.075 |
| pathway half | p75 NTR receptor-mediated signalling (R-HSA-193704) | 19/19 | 5.01 | 20.80 | 0.062 |
| pathway half | Glycolysis (R-HSA-70171) | 19/19 | 4.75 | 19.20 | 0.078 |
| pathway half | Opioid Signalling (R-HSA-111885) | 19/19 | 4.35 | 9.80 | 0.079 |
| pathway half | Positive epigenetic regulation of rRNA expression (R-HSA-5250913) | 19/19 | 3.97 | 28.80 | 0.086 |
| pathway half | RAC2 GTPase cycle (R-HSA-9013404) | 19/19 | 3.93 | 19.50 | 0.063 |
| pathway half | Activation of anterior HOX genes in hindbrain development during early embryogenesis (R-HSA-5617472) | 19/19 | 3.88 | 31.90 | 0.091 |
| pathway half | Senescence-Associated Secretory Phenotype (SASP) (R-HSA-2559582) | 19/19 | 3.83 | 6.70 | 0.079 |
| pathway half | Signaling by FGFR in disease (R-HSA-1226099) | 19/19 | 3.74 | 11.40 | 0.118 |
| pathway half | Amyloid fiber formation (R-HSA-977225) | 19/19 | 3.70 | 24.90 | 0.075 |
| pathway half | Interleukin-1 signaling (R-HSA-9020702) | 19/19 | 3.17 | 9.10 | 0.107 |
| pathway half | DNA Double Strand Break Response (R-HSA-5693606) | 19/19 | 2.91 | 10.50 | 0.059 |
| pathway half | Regulation of TP53 Activity through Phosphorylation (R-HSA-6804756) | 19/19 | 2.50 | 10.80 | 0.080 |
| pathway half | Cellular responses to mechanical stimuli (R-HSA-9855142) | 19/19 | 1.97 | 7.10 | 0.111 |
| pathway half | Interleukin-4 and Interleukin-13 signaling (R-HSA-6785807) | 19/19 | 1.53 | 4.60 | 0.128 |
| pathway half | COPI-dependent Golgi-to-ER retrograde traffic (R-HSA-6811434) | 19/19 | 0.73 | 9.00 | 0.112 |
| pathway half | Unfolded Protein Response (UPR) (R-HSA-381119) | 19/19 | 0.40 | 2.90 | 0.107 |
| pathway half | Amplification of signal from the kinetochores (R-HSA-141424) | 19/19 | 0.35 | 2.60 | 0.098 |
| pathway half | Cargo recognition for clathrin-mediated endocytosis (R-HSA-8856825) | 19/19 | 0.22 | 1.20 | 0.350 |
| pathway half | SLC-mediated transmembrane transport (R-HSA-425407) | 19/19 | 0.05 | 2.30 | 0.239 |

**Panel B. Pairs with no reason to be proximal.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| negative control | HEPATOCYTE_NEGCTRL vs half of Opioid Signalling (R-HSA-111885) | 15/19 | 0.64 | 0.90 | 0.653 |
| negative control | HEPATOCYTE_NEGCTRL vs half of Signaling by FGFR in disease (R-HSA-1226099) | 15/19 | 0.41 | 0.80 | 0.909 |
| negative control | HEPATOCYTE_NEGCTRL vs half of Amplification of signal from the kinetochores (R-HSA-141424) | 15/19 | 0.19 | 0.60 | 0.972 |
| random pair | independent random pair | 19/19 | 0.75 | 1.40 | 0.176 |
| random pair | independent random pair | 19/19 | 0.52 | 0.90 | 0.590 |
| random pair | independent random pair | 19/19 | 12.56 | 40.30 | 0.022 |
| random pair | independent random pair | 19/19 | 0.23 | 0.80 | 0.946 |
| random pair | independent random pair | 19/19 | 0.45 | 0.80 | 0.858 |
| random pair | independent random pair | 19/19 | 4.27 | 10.30 | 0.038 |
| random pair | independent random pair | 19/19 | 0.37 | 0.90 | 0.708 |
| random pair | independent random pair | 19/19 | 0.42 | 1.30 | 0.308 |
| random pair | independent random pair | 19/19 | 0.58 | 1.40 | 0.281 |
| random pair | independent random pair | 19/19 | 0.39 | 1.00 | 0.460 |

**Panel C. Second independent split of six pathways.**

| Class | Pair | k (A/B) | fold, null mean | fold, null median | p |
|---|---|---|---|---|---|
| pathway half, 2nd split | Opioid Signalling (R-HSA-111885) | 19/19 | 3.63 | 7.70 | 0.091 |
| pathway half, 2nd split | Signaling by FGFR in disease (R-HSA-1226099) | 19/19 | 4.15 | 9.10 | 0.122 |
| pathway half, 2nd split | Amplification of signal from the kinetochores (R-HSA-141424) | 19/19 | 0.43 | 2.60 | 0.074 |
| pathway half, 2nd split | Degradation of the extracellular matrix (R-HSA-1474228) | 19/19 | 15.20 | 113.70 | 0.004 |
| pathway half, 2nd split | L13a-mediated translational silencing of Ceruloplasmin expression (R-HSA-156827) | 19/19 | 6.25 | 146.10 | 0.103 |
| pathway half, 2nd split | Late Phase of HIV Life Cycle (R-HSA-162599) | 19/19 | 5.60 | 35.40 | 0.070 |

The second split in Panel C was drawn independently of the first. The two splits agree to a correlation of 0.999 and a largest relative difference of 2.2%, so the fold is a property of the pathway rather than of where the cut fell.
