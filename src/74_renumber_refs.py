"""Renumber citations to order of first appearance, and reorder the reference list to match.

Vancouver numbering is positional: a reference list that is numbered by any other rule is a
technical defect regardless of how good the science is. This script reads the parts in
assembly order, assigns numbers as numbers are first met, rewrites every citation group
(compressing runs back to ranges), and rewrites references.md in the new order.

Run it after adding or removing a citation; it is idempotent when the order is already right.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"

# assembly order, so that "first appearance" means the same thing here as in the PDF
PARTS = ["abstract.md", "intro.md", "methods_full.md", "results_full.md",
         "failure_and_coarsegraining.md", "discussion.md", "abbreviations.md",
         "declarations.md", "figure_legends.md"]

CITE = re.compile(r"\[(\d{1,2}(?:\s*[,\u2013-]\s*\d{1,2})*)\]")


def expand(group: str) -> list[int]:
    out = []
    for tok in group.split(","):
        tok = tok.strip()
        m = re.fullmatch(r"(\d{1,2})\s*[\u2013-]\s*(\d{1,2})", tok)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif tok.isdigit():
            out.append(int(tok))
    return out


def compress(nums: list[int]) -> str:
    nums = sorted(set(nums))
    runs, cur = [], [nums[0]]
    for v in nums[1:]:
        if v == cur[-1] + 1:
            cur.append(v)
        else:
            runs.append(cur)
            cur = [v]
    runs.append(cur)
    bits = []
    for r in runs:
        if len(r) >= 3:
            bits.append(f"{r[0]}\u2013{r[-1]}")
        else:
            bits.extend(str(x) for x in r)
    return "[" + ",".join(bits) + "]"


def main() -> int:
    texts = {p: (MS / p).read_text(encoding="utf-8") for p in PARTS}

    # pass 1: assign new numbers in order of first appearance
    mapping: dict[int, int] = {}
    for p in PARTS:
        for grp in CITE.findall(texts[p]):
            for old in expand(grp):
                if old not in mapping:
                    mapping[old] = len(mapping) + 1

    refs_raw = (MS / "references.md").read_text(encoding="utf-8")
    entries: dict[int, str] = {}
    for ch in re.split(r"\n(?=\d{1,2}\. )", refs_raw):
        m = re.match(r"(\d{1,2})\.\s+(.*)", ch.strip(), re.S)
        if m:
            entries[int(m.group(1))] = " ".join(
                ln.strip() for ln in m.group(2).split("\n") if ln.strip())

    missing = [o for o in mapping if o not in entries]
    unused = [o for o in entries if o not in mapping]
    if missing:
        print(f"citations to non-existent references: {missing}")
        return 1
    if unused:
        print(f"references never cited: {unused} -- remove them or cite them")
        return 1

    # pass 2: rewrite the text
    changed = 0
    for p in PARTS:
        def repl(m: re.Match) -> str:
            nonlocal changed
            new = compress([mapping[o] for o in expand(m.group(1))])
            if new != m.group(0):
                changed += 1
            return new
        texts[p] = CITE.sub(repl, texts[p])
        (MS / p).write_text(texts[p], encoding="utf-8")

    # pass 3: rewrite the reference list in the new order
    header = refs_raw.split("\n1. ", 1)[0].rstrip()
    lines = [header, ""]
    inv = {v: k for k, v in mapping.items()}
    for new in range(1, len(mapping) + 1):
        lines.append(f"{new}. {entries[inv[new]]}")
        lines.append("")
    (MS / "references.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(f"{len(mapping)} references; {changed} citation groups rewritten")
    renames = {o: n for o, n in mapping.items() if o != n}
    print("moved: " + ", ".join(f"{o}->{n}" for o, n in sorted(renames.items())) if renames
          else "moved: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
