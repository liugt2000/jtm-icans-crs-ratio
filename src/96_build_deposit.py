"""96_build_deposit.py -- assemble the reproducibility deposit.

Layout matches the working directory, so every script runs unchanged from the deposit root:

    python src/21_cases.py        # reads data/, writes out/

What goes in is chosen by rule, not by hand:

  * all code and configuration;
  * every derived output, every figure, the manuscript source and the supplementary tables;
  * the registry, so a reader can see what each object was;
  * only those third-party inputs whose terms allow redistribution. The rest are described in
    PROVENANCE.md with endpoint, release and SHA-256 but are not copied here.

The script is idempotent: it rewrites the payload directories, regenerates PROVENANCE.md,
DATA_DICTIONARY.md, requirements.txt and checksums.sha256, then zips the result.

    python src/96_build_deposit.py [--no-zip]
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEP = HERE / "deposit"

VERSION = "1.0.2"

# Third-party inputs we may redistribute. Everything else under data/ stays out.
DATA_INCLUDE = [
    "cases_icans_crs.jsonl",          # openFDA extract, US Government work
    "cases_legacy_nt.jsonl",          # same query on the legacy PT, US Government work
    "GSE195519_raw_counts.csv.gz",    # GEO, public
    "GSE211439_processed_count.txt.gz",
    "reactome_pathways_v98_20261125.gmt",      # pathway membership, redistributed with attribution
    "reactome_pathways_v98_20261125.gmt.zip",
]

# The manuscript parts that the assembled text is built from, plus the assembled text itself.
MS_INCLUDE = [
    "manuscript.md", "intro.md", "methods_full.md", "results_full.md", "discussion.md",
    "failure_and_coarsegraining.md", "abstract.md", "figure_legends.md", "references.md",
    "abbreviations.md", "declarations.md", "additional_file1_tables.md",
    "additional_file2_record_strobe.md",
]

# The four objects we do not redistribute, with the reason. Rendered into PROVENANCE.md.
NOT_REDISTRIBUTED = [
    ("data/omnipath_interactions_20261116.tsv",
     "OmniPath interactions",
     "OmniPath aggregates resources under mixed terms, several of them academic-only; the "
     "combined extract cannot be re-licensed. Re-fetch with src/03_fetch_network.py."),
    ("data/hpa_proteinatlas_20261116.tsv.zip",
     "Human Protein Atlas v24, rna_single_cell_type",
     "HPA distributes its data under its own terms and asks to be cited as the source. "
     "Re-fetch from https://v24.proteinatlas.org/download/tsv/rna_single_cell_type.tsv.zip "
     "(the v24 subdomain pins the release; the unversioned download page moves with it)."),
    ("ChEMBL target assignments",
     "ChEMBL",
     "ChEMBL is CC BY-SA 4.0; a share-alike object inside a CC BY deposit would relicense the "
     "whole record. Retained as queries in src/01_signals.py and src/02_analyse.py."),
    ("DepMap dependency matrix",
     "DepMap Public",
     "DepMap is released for research use under its own terms. Not needed to reproduce any "
     "reported number; retained as a query."),
]

DERIVED_NOTE = {
    "case_products.csv": "Per-product R, Wilson interval and phenotype counts: Table 1.",
    "case_products_anyrole.csv": "The same with any-role exposure instead of primary suspect: Table S2.",
    "case_products_isolated.csv": "Single-phenotype reports only (dual-coded dropped).",
    "case_groups.json": "Arm definitions and counts for the CD28 / 4-1BB / bispecific contrast.",
    "case_by_year.csv": "Annual phenotype volumes and the class-level R: Figure 3A.",
    "case_temporal.csv": "Within-product drift of R across market life.",
    "case_severity.csv": "Term-level acuity proxy, high-acuity subset: Table S11.",
    "case_severity.json": "Parameters of the acuity proxy and the degeneracy of the serious flag.",
    "counts_long.csv": "Product x preferred term x year counts, the base table for everything above.",
    "specification_curve.csv": "The nine analytic specifications: Table 2 and Figure 2.",
    "strata.json": "The nine reporting strata and the contrast inside each: Table S10.",
    "holdout.json": "Leave-one-product-out prediction of R: Table S8.",
    "holdout_products.csv": "Per-product prediction and error.",
    "legacy_pt.json": "The pre-2018 coding sensitivity, with the recoded subset.",
    "legacy_count_reconciliation.json": "Reconciliation of the legacy-term count against the modern one.",
    "network_rwr.json": "Random-walk-with-restart masses per module pair, folds and null quantiles.",
    "network_proximity.csv": "Every module pair with its proximity statistic: Table S6.",
    "network_null_ratio.json": "The 1,000-draw null for the CD28/4-1BB routing ratio: Figure 5A.",
    "power_network.json": "Minimum detectable ratio and the module size it would need: Figure 5B.",
    "positive_control.csv": "The 62 externally curated pairs, one row each: Table S13.",
    "positive_control_summary.json": "Calibration, detection floor and split reproducibility for S13.",
    "null_reproduction.json": "The published module folds recomputed through the same code path.",
    "localisation_hpa.json": "Module localisation across brain cell types: Figure 4.",
    "localisation_per_gene.csv": "Per-gene endothelial-to-myeloid log ratio.",
    "model_beta.json": "Fitted parameters of the three-variable model: Table S12.",
    "model_sobol.json": "Variance decomposition: which parameter can reach R.",
    "model_invariance.json": "Invariance checks for the model.",
    "prediction_rule.json": "The decision rule and its resolution limit: Table 3.",
    "prediction_decidability.json": "Reports needed for a decisive verdict, by product.",
    "ev_replication.json": "The contrast rebuilt in EudraVigilance: Table S9.",
    "ev_counts.json": "EudraVigilance aggregate counts per product and term.",
    "signals.csv": "Disproportionality statistics, the comparison the paper argues against.",
    "n2_test.json": "Built-in positive control for the disproportionality pipeline.",
    "refs_verification.csv": "Each reference re-resolved and checked against the cited record.",
    "pull_meta.json": "openFDA query strings, page counts and timestamps for the extract.",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


def copy_tree(src: Path, dst: Path, pattern: str = "*",
              exclude: tuple[str, ...] = ()) -> int:
    """Copy matching files. `exclude` takes glob patterns: the deposit should carry what
    produced the results, not the bench scripts and publication bookkeeping that sat
    beside them."""
    n = 0
    for p in sorted(src.glob(pattern)):
        if any(p.match(e) for e in exclude):
            continue
        if p.is_file():
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst / p.name)
            n += 1
    return n


def payload() -> None:
    """Refresh the payload directories. Docs at the deposit root are left alone."""
    for sub in ("src", "config", "out", "figs", "data", "data_registry", "manuscript",
                "protocol", "audit"):
        target = DEP / sub
        if target.exists():
            shutil.rmtree(target)

    print("  src/          %3d files" % copy_tree(HERE / "src", DEP / "src", "*.py",
                                                  exclude=("_bench.py",)))
    print("  config/       %3d files" % copy_tree(HERE / "config", DEP / "config"))

    n = 0
    (DEP / "data").mkdir(parents=True, exist_ok=True)
    for name in DATA_INCLUDE:
        src = HERE / "data" / name
        if src.exists():
            shutil.copy2(src, DEP / "data" / name)
            n += 1
        else:
            print("    ! missing input", name)
    print("  data/         %3d files (third-party inputs excluded)" % n)

    print("  out/          %3d files" % copy_tree(HERE / "out", DEP / "out",
                                                  exclude=("zenodo_*.json", "zenodo_*.png")))
    print("  figs/         %3d files" % copy_tree(HERE / "figs", DEP / "figs"))
    print("  data_registry/%3d files" % copy_tree(HERE / "data_registry", DEP / "data_registry"))

    # Only what the manuscript is made of. The working documents -- the review simulation,
    # the audit, the author form, the cover letter and the superseded drafts -- stay out: they
    # describe how the paper was argued, not what it claims.
    ms = DEP / "manuscript"
    ms.mkdir(parents=True, exist_ok=True)
    (ms / "tables").mkdir(exist_ok=True)
    k = 0
    for name in MS_INCLUDE:
        src = HERE / "manuscript" / name
        if src.exists():
            shutil.copy2(src, ms / name)
            k += 1
        else:
            print("    ! missing manuscript part", name)
    k += copy_tree(HERE / "manuscript" / "tables", ms / "tables", "*.md")
    print("  manuscript/   %3d files (source and tables only)" % k)

    # The pre-specified plan, frozen before any record was pulled. It sits at the workspace
    # root rather than in the project tree, so it has to be brought in explicitly.
    proto = HERE.parent / "Phase0_研究方案.md"
    if proto.exists():
        (DEP / "protocol").mkdir(exist_ok=True)
        shutil.copy2(proto, DEP / "protocol" / "Phase0_study_plan_zh.md")
        print("  protocol/       1 file (pre-specified plan, Chinese)")
    else:
        print("    ! pre-specified plan not found next to the project directory")

    # The reference audit table, cited in the Declarations. Its per-DOI cache is not needed.
    audit = HERE / "audit" / "refs_pubmed.csv"
    if audit.exists():
        (DEP / "audit").mkdir(exist_ok=True)
        shutil.copy2(audit, DEP / "audit" / "refs_pubmed.csv")
        print("  audit/          1 file (per-reference verification)")


def requirements() -> None:
    pin = {"numpy": "2.5.4", "pandas": "2.3.3", "scipy": "1.18.1", "matplotlib": "3.11.2",
           "python-docx": "1.2.0"}
    lines = ["# Python 3.13.14; these are the versions that produced out/.",
             "# Install with:  python -m pip install -r requirements.txt", ""]
    lines += [f"{k}=={v}" for k, v in pin.items()]
    # Record what is actually installed, for anything the pin list omits.
    try:
        out = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                             capture_output=True, text=True, timeout=120).stdout
        extra = sorted(l for l in out.splitlines()
                       if l and "==" in l and l.split("==")[0].lower()
                       not in {k.lower() for k in pin})
        lines += ["", "# Transitively required at run time:"]
        lines += extra
    except Exception as exc:                     # noqa: BLE001
        print("  (pip freeze unavailable: %s)" % exc)
    (DEP / "requirements.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  requirements.txt  %d lines" % len(lines))


def provenance() -> None:
    """Rebuild PROVENANCE.md from the registry, so the two can never disagree."""
    manifest = (HERE / "data_registry" / "MANIFEST.md").read_text(encoding="utf-8")
    rows = []
    for line in manifest.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        path = cells[0].strip("`")
        rows.append({"path": path, "bytes": cells[1], "sha": cells[2].strip("`"),
                     "role": cells[3], "source": cells[4], "retrieved": cells[5]})

    included = {f"data/{n}" for n in DATA_INCLUDE}
    lines = [
        "# Provenance of every external object",
        "",
        "This deposit is a snapshot taken on 2026-11-25. The registry in",
        "`data_registry/MANIFEST.md` carries a SHA-256 for every file the analysis reads or",
        "writes; the table below is generated from it and cannot drift from it.",
        "",
        "## Rule for what is redistributed",
        "",
        "A third-party file is copied into `data/` only if its terms let us pass it on without",
        "changing the licence of the deposit as a whole. Everything else is named here with the",
        "endpoint, the release, the retrieval time and the digest of the copy actually used,",
        "together with the script that re-fetches it. The digest is what makes that honest: if a",
        "re-fetch does not match, the provider has moved to a new release, and that is a fact",
        "about the provider rather than a difference in the analysis.",
        "",
        "## Redistributed",
        "",
        "| file | bytes | sha256 (16) | licence |",
        "|---|---:|---|---|",
    ]
    lic = {
        "data/cases_icans_crs.jsonl": "US Government work, no copyright (openFDA / FAERS)",
        "data/cases_legacy_nt.jsonl": "US Government work, no copyright (openFDA / FAERS)",
        "data/GSE195519_raw_counts.csv.gz": "GEO public record, unmodified",
        "data/GSE211439_processed_count.txt.gz": "GEO public record, unmodified",
        "data/reactome_pathways_v98_20261125.gmt": "Reactome v98, redistributed with attribution",
        "data/reactome_pathways_v98_20261125.gmt.zip": "as downloaded from reactome.org",
    }
    for r in rows:
        if r["path"] in included:
            lines.append(f"| `{r['path']}` | {r['bytes']} | `{r['sha']}` | {lic.get(r['path'], '')} |")

    lines += [
        "",
        "## Not redistributed",
        "",
        "| object | why not | how to re-obtain |",
        "|---|---|---|",
    ]
    for path, name, why in NOT_REDISTRIBUTED:
        entry = next((r for r in rows if r["path"] == path), None)
        how = f"`{entry['source']}`" if entry and entry["source"] else "see `src/`"
        if entry:
            how += f"; retrieved {entry['retrieved']}; sha256 `{entry['sha']}`"
        lines.append(f"| {name} | {why} | {how} |")

    lines += [
        "",
        "## Every input, as recorded at the time of the run",
        "",
        "| path | role | bytes | sha256 (16) | source | retrieved (UTC) |",
        "|---|---|---:|---|---|---|",
    ]
    for r in rows:
        if r["role"].startswith("raw_input"):
            src = (r["source"] or "").replace("|", "/")
            lines.append(f"| `{r['path']}` | {r['role']} | {r['bytes']} | "
                         f"`{r['sha']}` | {src[:160]} | {r['retrieved']} |")

    lines += [
        "",
        "## Versions",
        "",
        "- FAERS: openFDA drug/event endpoint, queried 2026-11-16. The database is updated",
        "  quarterly, so the deposited extract, not the query, is the reproducible object.",
        "- OmniPath: interactions export, `datasets=omnipath,pathwayextra,kinaseextra,"
        "ligrecextra`, organism 9606, retrieved 2026-11-16. OmniPath publishes a rolling",
        "  snapshot and no release number, so the deposited SHA-256, not a version string,",
        "  identifies the object.",
        "- Human Protein Atlas: v24, `rna_single_cell_type.tsv.zip`, from",
        "  https://v24.proteinatlas.org/download/tsv/, retrieved 2026-11-16.",
        "- Reactome: v98 release (`ReactomePathways.gmt`), retrieved 2026-11-25.",
        "- EudraVigilance: aggregate line listings, retrieved through the public dashboard;",
        "  no case-level access exists, which is why the replication is at the level of counts.",
        "",
        f"_Generated by `src/96_build_deposit.py` on {dt.date.today().isoformat()}._",
    ]
    (DEP / "PROVENANCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  PROVENANCE.md  %d lines, %d registry rows" % (len(lines), len(rows)))


def dictionary() -> None:
    """Describe out/ by reading it: columns for CSV, top-level keys for JSON. No invention."""
    lines = [
        "# What is in `out/`",
        "",
        "Every file the manuscript cites, in the form the pipeline leaves it. Descriptions are",
        "read from the files themselves -- columns for tables, top-level keys for JSON -- so this",
        "page cannot describe an object that is not there. Each JSON also carries the parameters,",
        "seed and sample counts that produced it.",
        "",
        "| file | rows / keys | content | note |",
        "|---|---|---|---|",
    ]
    for p in sorted((DEP / "out").iterdir()):
        if p.suffix == ".csv":
            with open(p, encoding="utf-8-sig", newline="") as fh:
                rd = csv.reader(fh)
                header = next(rd, [])
                n = sum(1 for _ in rd)
            shape = f"{n:,} rows"
            content = ", ".join(header[:8]) + (" …" if len(header) > 8 else "")
        elif p.suffix == ".json":
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                keys = list(d)[:8] if isinstance(d, dict) else []
                shape = f"{len(d):,} keys" if isinstance(d, dict) else f"{len(d):,} items"
                content = ", ".join(f"`{k}`" for k in keys) + (" …" if isinstance(d, dict) and len(d) > 8 else "")
            except Exception:                    # noqa: BLE001
                shape, content = "—", "(not parseable as JSON)"
        elif p.suffix == ".npz":
            shape, content = "array archive", "the null draws themselves, for re-plotting without a re-run"
        elif p.suffix == ".log":
            shape, content = "log", "console output of the run that produced the neighbouring files"
        else:
            shape, content = "—", ""
        lines.append(f"| `{p.name}` | {shape} | {content} | {DERIVED_NOTE.get(p.name, '')} |")

    lines += [
        "",
        "## Not in `out/`",
        "",
        "The manuscript itself is built by `src/50_assemble.py` from the sections in",
        "`manuscript/`, and the supplementary tables by `src/41_tables_new.py`. Both are already",
        "in this deposit, so the number trace (`src/73_trace_numbers.py`) can be re-run without",
        "regenerating anything.",
    ]
    (DEP / "DATA_DICTIONARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  DATA_DICTIONARY.md  %d files described" % len(list((DEP / 'out').iterdir())))


def checksums() -> None:
    rows = []
    for p in tree(DEP):
        if p.name == "checksums.sha256":
            continue
        rows.append(f"{sha256(p)}  {p.relative_to(DEP).as_posix()}")
    (DEP / "checksums.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")
    total = sum(p.stat().st_size for p in tree(DEP))
    print("  checksums.sha256   %d files, %.1f MB" % (len(rows), total / 1e6))


def zenodo_meta() -> None:
    """Keep the deposit metadata mechanically true.

    The script count and the freeze date are properties of the payload, not of anyone's
    memory: v1.0.0 shipped a description claiming 96 scripts against a payload of 63.
    """
    path = DEP / ".zenodo.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    n = len(list((DEP / "src").glob("*.py")))
    data["description"] = re.sub(r"\d+ scripts", f"{n} scripts",
                                 data.get("description", ""), count=1)
    data["version"] = VERSION
    data["publication_date"] = dt.date.today().isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  .zenodo.json      version %s, %d scripts, %s"
          % (VERSION, n, data["publication_date"]))


def archive(version: str = VERSION) -> Path:
    out = HERE / f"deposit_jtm_icans_v{version}.zip"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in tree(DEP):
            zf.write(p, f"jtm_icans_v{version}/{p.relative_to(DEP).as_posix()}")
    print("  %s  %.1f MB" % (out.name, out.stat().st_size / 1e6))
    return out


def main() -> int:
    DEP.mkdir(exist_ok=True)
    print("payload")
    payload()
    print("metadata")
    requirements()
    provenance()
    dictionary()
    zenodo_meta()
    checksums()
    if "--no-zip" not in sys.argv:
        print("archive")
        archive()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
