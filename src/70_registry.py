"""Build data_registry/: SHA-256 manifest for every raw input and derived output.

Written so that a reader with no access to our filesystem can still verify that a
re-run used the same inputs: each row is (path, bytes, sha256, role, source,
retrieved_utc). Raw downloads are additionally pinned to their upstream endpoint
so that a third party can re-pull and compare hashes.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "out"
REG = ROOT / "data_registry"
REG.mkdir(exist_ok=True)

# What each file *is*, and where it came from. Keys are paths relative to ROOT.
SOURCE = {
    "data/cases_icans_crs.jsonl":
        "openFDA drug/event, case-level records; query "
        "patient.reaction.reactionmeddrapt:\"Immune effector cell-associated neurotoxicity syndrome\" "
        "+ \"Cytokine release syndrome\"; api.fda.gov, limit=500, paged",
    "data/hpa_proteinatlas_20261116.tsv.zip":
        "Human Protein Atlas v24 rna_single_cell_type.tsv.zip "
        "(https://www.proteinatlas.org/download/tsv/rna_single_cell_type.tsv.zip)",
    "data/omnipath_interactions_20261116.tsv":
        "OmniPath interactions (https://omnipathdb.org/interactions), "
        "fields=sources,references,curation_effort,is_directed,entity_type, "
        "genesymbols=yes, datasets=omnipath,pathwayextra,kinaseextra,ligrecextra, "
        "organisms=9606",
    "data/GSE211439_processed_count.txt.gz":
        "GEO GSE211439 (hBMEC +/- TNF-a) processed counts, NCBI FTP",
    "data/GSE195519_raw_counts.csv.gz":
        "GEO GSE195519 (iBMEC/iPSC-EC/HDMEC/iPC) raw counts, NCBI FTP",
    "data/reactome_pathways_v98_20261125.gmt":
        "Reactome v98 pathway gene sets, UniProt-to-HGNC symbols as distributed "
        "(https://reactome.org/download/current/ReactomePathways.gmt.zip), "
        "positive-control annotation only",
    "data/reactome_pathways_v98_20261125.gmt.zip":
        "same file as downloaded, kept zipped so the unzip step can be re-checked",
}
RAW_PREFIXES = ("data/cases_part_",)

ROLE = {
    "data/": "raw_input",
    "out/": "derived_output",
}

# Files that sit beside the results but are not results: text dumps made while checking a
# docx, and the JSON/PNG bookkeeping of the Zenodo upload. Including them made the
# aggregate digest change every time the paper was rebuilt or re-released.
EXCLUDE_GLOBS = ("out/zenodo_*", "out/*_dump.txt")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: pathlib.Path) -> str:
    return p.relative_to(ROOT).as_posix()


def classify(r: str) -> str:
    if r.startswith(RAW_PREFIXES):
        return "raw_input_intermediate_page"
    for pre, role in ROLE.items():
        if r.startswith(pre):
            return role
    return "other"


rows = []
for base in (DATA, OUT):
    if not base.exists():
        continue
    # Only files sitting directly in data/ or out/. The subdirectories are network
    # response caches (openFDA pages, Crossref lookups): keeping them out of the digest
    # makes the aggregate a fingerprint of the analysis itself rather than of how many
    # times a query was retried.
    for p in sorted(base.glob("*")):
        if not p.is_file():
            continue
        r = rel(p)
        if any(pathlib.PurePosixPath(r).match(g) for g in EXCLUDE_GLOBS):
            continue
        st = p.stat()
        rows.append({
            "path": r,
            "bytes": st.st_size,
            "sha256": sha256(p),
            "role": classify(r),
            "source": SOURCE.get(r, ""),
            "mtime_utc": dt.datetime.utcfromtimestamp(st.st_mtime)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

# Manifest as markdown (human-readable, the version shipped with the paper)
md = ["# Data and code registry",
      "",
      "Every file the analysis reads or writes, with its SHA-256 digest. Rows with "
      "`role = raw_input` are downloaded verbatim; `raw_input_intermediate_page` are "
      "per-page fragments of the same openFDA query kept so that the merge step can be "
      "audited; `derived_output` files are reproduced by the numbered scripts in `src/`.",
      "",
      "| path | bytes | sha256 (first 16) | role | source | retrieved (UTC) |",
      "|---|---:|---|---|---|---|"]
for r in rows:
    src = r["source"].replace("|", "/")
    md.append(f"| `{r['path']}` | {r['bytes']:,} | `{r['sha256'][:16]}` | "
              f"{r['role']} | {src} | {r['mtime_utc']} |")
caches = []
for sub in ("out/refs_crossref", "out/refs_verify"):
    d = ROOT / sub
    if d.is_dir():
        caches.append(f"`{sub}` ({len(list(d.glob('*.json')))} files)")
md.append("")
md.append("Excluded from the manifest because they are regenerable network responses, not "
          "analysis inputs: " + ", ".join(caches) + ". They are deposited alongside so that "
          "the reference-resolution steps in `src/71`–`src/72` can be audited without "
          "re-querying Crossref.")
md.append("")
md.append(f"*{len(rows)} files. Full 64-character digests in `manifest.csv` and "
          f"`manifest.json`.*")
(REG / "MANIFEST.md").write_text("\n".join(md), encoding="utf-8")

import csv
with (REG / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

(REG / "manifest.json").write_text(
    json.dumps({"generated_utc": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "n_files": len(rows), "files": rows}, indent=2),
    encoding="utf-8")

# Aggregate digest: one hash over the sorted (path, sha256) pairs. This is the number
# to quote in the paper's data-availability statement, because it changes if any
# single input changes.
agg = hashlib.sha256()
for r in sorted(rows, key=lambda x: x["path"]):
    agg.update(f"{r['path']}\t{r['sha256']}\n".encode())
print(f"files={len(rows)}  aggregate_sha256={agg.hexdigest()}")
print(f"written -> {REG}")
