# Data and code registry

Every file the analysis reads or writes, with its SHA-256 digest. Rows with `role = raw_input` are downloaded verbatim; `raw_input_intermediate_page` are per-page fragments of the same openFDA query kept so that the merge step can be audited; `derived_output` files are reproduced by the numbered scripts in `src/`.

| path | bytes | sha256 (first 16) | role | source | retrieved (UTC) |
|---|---:|---|---|---|---|
| `data/cases_icans_crs.jsonl` | 71,359,107 | `397517cfe16ade95` | raw_input | openFDA drug/event, case-level records; query patient.reaction.reactionmeddrapt:"Immune effector cell-associated neurotoxicity syndrome" + "Cytokine release syndrome"; api.fda.gov, limit=500, paged | 2026-11-16T09:34:09Z |
| `data/cases_legacy_nt.jsonl` | 28,034,659 | `45951bd6c51c0af2` | raw_input |  | 2026-11-20T23:49:34Z |
| `data/cases_part_0_0.jsonl` | 3,951,638 | `3c1dc4f5ce0e5230` | raw_input_intermediate_page |  | 2026-11-16T09:32:09Z |
| `data/cases_part_0_1.jsonl` | 4,013,630 | `08981f337e1c1033` | raw_input_intermediate_page |  | 2026-11-16T09:32:11Z |
| `data/cases_part_0_2.jsonl` | 3,492,030 | `b8d368a676b9f0cc` | raw_input_intermediate_page |  | 2026-11-16T09:32:01Z |
| `data/cases_part_1_0.jsonl` | 22,910,838 | `b7d96c4a0e8038cd` | raw_input_intermediate_page |  | 2026-11-16T09:33:43Z |
| `data/cases_part_1_1.jsonl` | 23,887,131 | `daa1ccf12172fdab` | raw_input_intermediate_page |  | 2026-11-16T09:34:06Z |
| `data/cases_part_1_2.jsonl` | 20,646,889 | `e25f6529eaad1933` | raw_input_intermediate_page |  | 2026-11-16T09:33:53Z |
| `data/GSE195519_raw_counts.csv.gz` | 2,945,720 | `b754d417bd435d5d` | raw_input | GEO GSE195519 (iBMEC/iPSC-EC/HDMEC/iPC) raw counts, NCBI FTP | 2026-11-16T09:07:26Z |
| `data/GSE211439_processed_count.txt.gz` | 692,592 | `0cf607235340fedb` | raw_input | GEO GSE211439 (hBMEC +/- TNF-a) processed counts, NCBI FTP | 2026-11-16T09:07:21Z |
| `data/hpa_proteinatlas_20261116.tsv.zip` | 7,225,618 | `10a737f01ee0bf87` | raw_input | Human Protein Atlas v24 rna_single_cell_type.tsv.zip (https://www.proteinatlas.org/download/tsv/rna_single_cell_type.tsv.zip) | 2026-11-16T08:58:45Z |
| `data/omnipath_interactions_20261116.tsv` | 20,868,481 | `2bb2bbfb88472247` | raw_input | OmniPath interactions (https://omnipathdb.org/interactions), fields=sources,references,curation_effort,is_directed,entity_type, genesymbols=yes, datasets=omnipath,pathwayextra,kinaseextra,ligrecextra, organisms=9606 | 2026-11-16T08:57:40Z |
| `data/omnipath_meta.json` | 697 | `8e8b49349d37cd1b` | raw_input |  | 2026-11-16T08:58:12Z |
| `data/reactome_pathways_v98_20261125.gmt` | 1,039,264 | `a9feaa3ae9bbb746` | raw_input | Reactome v98 pathway gene sets, UniProt-to-HGNC symbols as distributed (https://reactome.org/download/current/ReactomePathways.gmt.zip), positive-control annotation only | 2026-11-25T13:09:16Z |
| `data/reactome_pathways_v98_20261125.gmt.zip` | 300,128 | `6056fcd95dc8f097` | raw_input | same file as downloaded, kept zipped so the unzip step can be re-checked | 2026-11-25T13:09:16Z |
| `out/case_bias_examples.csv` | 752 | `5a948e88e06b8b03` | derived_output |  | 2026-11-25T08:48:14Z |
| `out/case_by_year.csv` | 299 | `1b153ebae2758f21` | derived_output |  | 2026-11-25T08:48:14Z |
| `out/case_groups.json` | 12,725 | `b82d315a04e8ead8` | derived_output |  | 2026-11-25T08:48:14Z |
| `out/case_products.csv` | 1,932 | `5d45f047a368b68c` | derived_output |  | 2026-11-25T08:48:11Z |
| `out/case_products_anyrole.csv` | 1,940 | `078a67ed16bf62a1` | derived_output |  | 2026-11-25T08:48:11Z |
| `out/case_products_isolated.csv` | 1,918 | `d293762ee82368fd` | derived_output |  | 2026-11-25T08:48:11Z |
| `out/case_severity.csv` | 1,671 | `0a88dd00b07374b6` | derived_output |  | 2026-11-25T09:29:38Z |
| `out/case_severity.json` | 2,544 | `7299625807aa6da1` | derived_output |  | 2026-11-25T09:29:38Z |
| `out/case_temporal.csv` | 7,105 | `26ab6d3e3e03071d` | derived_output |  | 2026-11-25T08:48:12Z |
| `out/counts_long.csv` | 36,382 | `ea2b5ea9ed0fc389` | derived_output |  | 2026-11-16T08:47:53Z |
| `out/ebgm_hyperparameters.json` | 185 | `deb5b3492dd8d5cb` | derived_output |  | 2026-11-16T08:51:21Z |
| `out/ebgm_stability.csv` | 515 | `2c47637a3610df80` | derived_output |  | 2026-11-16T08:51:14Z |
| `out/ev_counts.json` | 20,397 | `5b6a83b113f7bd04` | derived_output |  | 2026-11-21T00:38:26Z |
| `out/ev_counts.jsonl` | 16,636 | `294d2f8c144f7dbc` | derived_output |  | 2026-11-21T00:38:26Z |
| `out/ev_index_probe.json` | 22 | `ab4bf214ff8d3e28` | derived_output |  | 2026-11-17T06:21:10Z |
| `out/ev_probe.json` | 2,919 | `04677d3e0936c4ab` | derived_output |  | 2026-11-17T06:19:44Z |
| `out/ev_replication.json` | 6,983 | `4063f925cd44815a` | derived_output |  | 2026-11-21T00:46:31Z |
| `out/ev_substance_index.csv` | 1,198,590 | `c2d3ca321e89ded3` | derived_output |  | 2026-11-17T06:21:10Z |
| `out/holdout.json` | 2,394 | `d4777c3ca38ba297` | derived_output |  | 2026-11-20T23:07:09Z |
| `out/holdout_products.csv` | 420 | `7b26a8198aff101f` | derived_output |  | 2026-11-20T23:07:09Z |
| `out/legacy_count_reconciliation.json` | 109 | `74ba075a121beaf3` | derived_output |  | 2026-11-20T23:18:55Z |
| `out/legacy_pages.log` | 0 | `e3b0c44298fc1c14` | derived_output |  | 2026-11-20T23:21:27Z |
| `out/legacy_products.csv` | 2,807 | `ed2d4f5c37446f39` | derived_output |  | 2026-11-20T23:49:49Z |
| `out/legacy_pt.json` | 2,063 | `b5fa18f18d29b62e` | derived_output |  | 2026-11-20T23:49:53Z |
| `out/legacy_run.log` | 835 | `615c96d90eafc439` | derived_output |  | 2026-11-20T23:17:26Z |
| `out/localisation_hpa.json` | 2,589 | `f17c50e8d3a1415f` | derived_output |  | 2026-11-16T09:13:02Z |
| `out/localisation_per_gene.csv` | 9,116 | `c78579bcc03de3c8` | derived_output |  | 2026-11-16T09:13:02Z |
| `out/model_beta.json` | 459 | `3231982822694a10` | derived_output |  | 2026-11-25T08:44:25Z |
| `out/model_identity.csv` | 193,490 | `af4e61b4f2ea8d29` | derived_output |  | 2026-11-25T08:44:25Z |
| `out/model_invariance.json` | 4,911 | `74616eaa188bd0a0` | derived_output |  | 2026-11-25T08:44:20Z |
| `out/model_sobol.json` | 1,905 | `3e4e14eb00a22adb` | derived_output |  | 2026-11-25T08:44:24Z |
| `out/n2_test.json` | 1,586 | `bff19014ac6a8a41` | derived_output |  | 2026-11-16T08:51:51Z |
| `out/network_null_ratio.json` | 847 | `636304f8177bab45` | derived_output |  | 2026-11-16T09:20:03Z |
| `out/network_null_ratio_samples.npz` | 31,016 | `01f6ed6a45c0b01d` | derived_output |  | 2026-11-16T09:20:03Z |
| `out/network_proximity.csv` | 2,132 | `24ec166eaea5c0b4` | derived_output |  | 2026-11-26T06:03:30Z |
| `out/network_proximity.json` | 10,034 | `2d2fcd96b9b320db` | derived_output |  | 2026-11-26T06:03:30Z |
| `out/network_rwr.json` | 4,479 | `9c9360e130eaa043` | derived_output |  | 2026-11-16T09:15:23Z |
| `out/null_reproduction.json` | 1,664 | `70e1b9a645f0e14c` | derived_output |  | 2026-11-25T14:24:47Z |
| `out/perturbation_validation.json` | 16,816 | `a31a1a23d512bcb6` | derived_output |  | 2026-11-16T09:11:34Z |
| `out/positive_control.csv` | 14,271 | `f23dad056d6ea8e2` | derived_output |  | 2026-11-25T14:20:52Z |
| `out/positive_control.json` | 63,311 | `37e824db948101a5` | derived_output |  | 2026-11-25T14:20:52Z |
| `out/positive_control.log` | 10,616 | `386b3d49ee79b3ad` | derived_output |  | 2026-11-25T14:20:52Z |
| `out/positive_control_samples.npz` | 479,147 | `50c63c3ba8dea73a` | derived_output |  | 2026-11-25T14:20:52Z |
| `out/positive_control_summary.json` | 4,935 | `eb6f75d87568f92c` | derived_output |  | 2026-11-25T14:25:33Z |
| `out/power_network.json` | 958 | `460a5c5ab2511e52` | derived_output |  | 2026-11-16T09:19:04Z |
| `out/prediction_decidability.json` | 1,041 | `fd9f11dac17e5f85` | derived_output |  | 2026-11-20T22:56:37Z |
| `out/prediction_rule.json` | 2,967 | `5d124acba1a45671` | derived_output |  | 2026-11-20T23:07:11Z |
| `out/pull_meta.json` | 582 | `e14ecbdf0bea1405` | derived_output |  | 2026-11-16T08:47:53Z |
| `out/refs_run.log` | 1,845 | `53baef9efd76817d` | derived_output |  | 2026-11-16T10:00:25Z |
| `out/refs_verification.csv` | 3,086 | `6b0a0568cf7e1c44` | derived_output |  | 2026-11-16T10:06:54Z |
| `out/signals.csv` | 83,610 | `8e51cb280e3f83ab` | derived_output |  | 2026-11-16T08:51:21Z |
| `out/specification_curve.csv` | 1,210 | `b95fd8440a645c02` | derived_output |  | 2026-11-25T08:48:26Z |
| `out/strata.json` | 7,327 | `2803de8e67a7d75a` | derived_output |  | 2026-11-25T05:46:47Z |
| `out/table1_products.csv` | 6,920 | `d1f5680c632fb37f` | derived_output |  | 2026-11-16T08:51:51Z |
| `out/table2_icans_share.csv` | 1,421 | `140da967ba2a87f9` | derived_output |  | 2026-11-16T09:19:49Z |

Excluded from the manifest because they are regenerable network responses, not analysis inputs: `out/refs_crossref` (75 files), `out/refs_verify` (24 files). They are deposited alongside so that the reference-resolution steps in `src/71`–`src/72` can be audited without re-querying Crossref.

*70 files. Full 64-character digests in `manifest.csv` and `manifest.json`.*