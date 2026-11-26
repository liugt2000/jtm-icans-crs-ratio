"""51_additional.py -- compose Additional file 1 (supplementary tables S1-S13).

The thirteen supplementary tables used to be appended to the main manuscript after the
reference list, which is not how BMC/Springer want them: each additional file is uploaded
separately and cited from the text as "Additional file 1: Table Sn". This script builds that
file from the same `manuscript/tables/s*.md` sources, so the two documents cannot drift.

Headings are normalised to one H1 for the file itself and one H2 per table; the source files
carry their own H1 ("Supplementary Table S1. ..."), which would render each table at the same
level as the file title.
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
TAB = MS / "tables"

TITLE = "The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in BCMA"

CONTENTS = """S1 substance-key normalisation; S2 exposure-role and report-set sensitivity; S3 EBGM
mixture hyperparameters; S4 quality gate on the induced-brain-endothelium dataset; S5 gene
modules and provenance; S6 random-walk-with-restart proximity for all ordered pairs; S7 the
partition under the pre-2018 coding convention; S8 leave-one-product-out prediction of R; S9
the partition in EudraVigilance; S10 the costimulation contrast inside reporting strata; S11 the
severity proxy and the contrast within high-acuity reports; S12 parameters of the mechanistic
model; S13 positive control for the network null."""


def normalise(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    first, _, rest = text.partition("\n")
    m = re.match(r"#+\s*Supplementary [Tt]able (S\d+)\.\s*(.+)$", first.strip())
    if not m:
        raise SystemExit(f"unexpected heading in {path.name}: {first[:70]!r}")
    head = f"# Table {m.group(1)}. {m.group(2).strip()}"
    return head + ("\n" + rest if rest.strip() else "")


def main() -> int:
    files = sorted(TAB.glob("s*.md"), key=lambda p: int(re.search(r"s(\d+)", p.stem).group(1)))
    if len(files) != 13:
        raise SystemExit(f"expected 13 supplementary tables, found {len(files)}")

    parts = [
        f"# Additional file 1: Supplementary tables S1\u2013S{len(files)}",
        "",
        f"**Article title.** {TITLE}",
        "",
        f"**Contents.** {CONTENTS}",
        "",
        "Each table is cited in the main text as *Additional file 1: Table Sn*. The numbering groups "
        "the tables by what they support rather than by order of first mention: data preparation "
        "(S1\u2013S3), the endothelial quality gate (S4), modules and proximity (S5\u2013S6), sensitivity "
        "and replication (S7\u2013S10), severity (S11), the model (S12) and the network null (S13). Tables are provided as "
        "editable text rather than images so that every value can be copied out.",
        "",
    ]
    for p in files:
        parts.append(normalise(p))
        parts.append("")

    text = "\n".join(parts).rstrip() + "\n"

    # The header block is prose and is wrapped to the same 96 columns as the manuscript; the
    # tables below it are not touched, since a wrapped markdown row is a broken table.
    cut = text.index("# Table S1.")
    head = text[:cut]
    paras = [q for q in head.split("\n\n")]
    wrapped = []
    for q in paras:
        flat = " ".join(q.split())
        if not flat:
            continue
        wrapped.append(textwrap.fill(flat, width=96, break_long_words=False,
                                     break_on_hyphens=False))
    text = "\n\n".join(wrapped) + "\n\n" + text[cut:]

    out = MS / "additional_file1_tables.md"
    out.write_text(text, encoding="utf-8")
    n = len(out.read_text(encoding="utf-8").split())
    print(f"written {out}  ({len(files)} tables, ~{n:,} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
