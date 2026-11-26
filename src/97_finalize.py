"""97_finalize.py -- put the real DOI and repository URL into the deposit and the manuscript.

The deposit cannot contain its own DOI before it exists, and the manuscript cannot cite a DOI
before it is assigned. Zenodo resolves this by reserving the DOI as soon as a draft upload is
created: the number is fixed at that moment and does not change on publication. So the order is

  1. create the draft in Zenodo, copy the reserved DOI;
  2. run this script with that DOI and the repository URL;
  3. upload the zip it produces, then publish.

Everything that carries a placeholder is rewritten in one pass, then the deposit is rebuilt,
the manuscript is re-assembled, and the two checks that matter are re-run.

    python src/97_finalize.py --doi 10.5281/zenodo.12345678 \
        --repo https://github.com/liugt2000/jtm-icans-crs-ratio
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MS = HERE / "manuscript"
DEP = HERE / "deposit"

TARGETS = [
    DEP / "README.md",
    DEP / "CITATION.cff",
    DEP / ".zenodo.json",
    MS / "declarations.md",
    MS / "cover_letter.md",
]


def replace(path: Path, pairs: list[tuple[str, str]]) -> None:
    raw = path.read_text(encoding="utf-8", newline="")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    before = text
    for a, b in pairs:
        text = text.replace(a, b)
    if text == before:
        print(f"  {path.name}: nothing replaced")
        return
    path.write_text(text.replace("\n", nl), encoding="utf-8", newline="")
    print(f"  {path.name}: updated")


def run(script: str, *args: str, expect_ok: bool = True) -> bool:
    print(f"\n>>> {script} {' '.join(args)}".rstrip())
    r = subprocess.run([sys.executable, str(HERE / "src" / script), *args], cwd=HERE)
    if expect_ok and r.returncode != 0:
        print(f"!! {script} exited {r.returncode}")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi", required=True,
                    help="reserved or published Zenodo DOI, e.g. 10.5281/zenodo.12345678")
    ap.add_argument("--repo", required=True,
                    help="https://github.com/<user>/<repo>")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--skip-docx", action="store_true",
                    help="leave the Word file alone (use when it is open in Word)")
    a = ap.parse_args()

    doi = a.doi.strip().replace("https://doi.org/", "").strip()
    if not re.fullmatch(r"10\.\d{4,9}/zenodo\.\d{4,}", doi):
        print(f"DOI does not look like a Zenodo DOI: {doi!r}")
        return 2
    repo = a.repo.strip().rstrip("/")
    if not repo.startswith("https://github.com/"):
        print(f"repository URL should start with https://github.com/: {repo!r}")
        return 2
    name = repo.rsplit("/", 1)[-1]

    print("tokens")
    pairs = [
        ("{{ZENODO_DOI}}", doi),
        ("https://doi.org/{{ZENODO_DOI}}", f"https://doi.org/{doi}"),
        ("{{REPO_URL}}", repo),
        ("https://github.com/liugt2000/{{REPO_NAME}}", repo),
        ("{{REPO_NAME}}", name),
        ("{{VERSION}}", a.version),
    ]
    for p in TARGETS:
        replace(p, pairs)

    # The .zenodo.json one-liner about placeholders is metadata, not prose; drop it.
    # The related identifier block is dropped too: it exists only to point at the
    # manuscript, and once the DOI template is filled it would point at this deposit.
    z = DEP / ".zenodo.json"
    if z.exists():
        t = z.read_text(encoding="utf-8")
        changed = False
        if "PLACEHOLDER: replace the creator block" in t:
            t = re.sub(r',?\s*"notes":\s*"PLACEHOLDER:[^"]*"', "", t)
            changed = True
        if '"related_identifiers"' in t:
            t = re.sub(r',?\s*"related_identifiers":\s*\[[^\]]*\]', "", t)
            changed = True
        if changed:
            t = re.sub(r",(\s*)\}", r"\1}", t)
            json.loads(t)  # refuse to write a file that is not valid JSON
            z.write_text(t, encoding="utf-8")
            print("  .zenodo.json: notes and self-reference removed")

    print("\nrebuild")
    if not run("50_assemble.py"):
        return 1
    if not run("73_trace_numbers.py"):
        print("\nThe number trace or the placeholder guard failed. The manuscript is not "
              "consistent yet; fix it before uploading.")
        return 1
    run("78_xref.py")
    if not run("96_build_deposit.py"):
        return 1
    if not a.skip_docx:
        run("60_docx.py", expect_ok=False)

    print("\nleft to do by hand")
    print(f"  1. upload deposit_jtm_icans_v{a.version}.zip to Zenodo, check the creator list,")
    print(f"     then publish — this activates {doi}")
    print(f"  2. push this directory to {repo} (see DEPOSIT_INSTRUCTIONS.md)")
    print("  3. the manuscript now cites the DOI; rebundle the submission files if the zip")
    print("     you uploaded was built before publication (it was not: build order handles it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
