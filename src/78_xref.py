"""78_xref.py -- one-to-one check of every display item and reference cited in the text.

Three questions, all mechanical:
  * is every figure (1-6), table (1-3) and supplementary table (S1-S12) cited at least once?
  * is every cited item actually present in the package?
  * are citations numbered in order of first appearance, and is every reference [1-26] used?

The last one matters because the list was renumbered when the sections moved: a reference
that is never cited is a sign the renumbering left a gap, and a first citation out of order
is a sign a paragraph was moved without renumbering.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
TXT = (MS / "manuscript.md").read_text(encoding="utf-8")

BODY = TXT[TXT.index("# 1. Introduction"):TXT.index("# 5. Tables")]

figs = {int(m) for m in re.findall(r"\bFig(?:ure)?\.?\s*(\d+)", BODY)}
figs_d = {int(m) for m in re.findall(r"\bFigure\s+(\d+)\b", BODY)}
tabs = {int(m) for m in re.findall(r"\bTable\s+(\d+)\b", BODY)}
sup = {int(m) for m in re.findall(r"\bTable S(\d+)", BODY)}

legend_figs = {int(m) for m in re.findall(r"^\*\*Figure (\d+)\.", (MS / "figure_legends.md")
                                              .read_text(encoding="utf-8"), re.M)}
table_files = sorted((MS / "tables").glob("*.md"))
table_ids = []
for p in table_files:
    m = re.search(r"table_?(\d+)", p.stem)
    s = re.search(r"s(\d+)", p.stem)
    if s:
        table_ids.append(f"S{s.group(1)}")
    elif m:
        table_ids.append(m.group(1))
sup_files = {int(t[1:]) for t in table_ids if t.startswith("S")}
main_files = {int(t) for t in table_ids if not t.startswith("S")}

print("figures cited in text:      ", sorted(figs))
print("figure legends present:     ", sorted(legend_figs))
print("figures never cited:        ", sorted(legend_figs - figs) or "none")
print("figures cited but missing:  ", sorted(figs - legend_figs) or "none")
print()
print("tables cited in text:       ", sorted(tabs))
print("table files present:        ", sorted(main_files))
print("tables never cited:         ", sorted(main_files - tabs) or "none")
print("tables cited but missing:   ", sorted(tabs - main_files) or "none")
print()
print("supplementary cited:        ", sorted(sup))
print("supplementary files:        ", sorted(sup_files))
print("S-tables never cited:       ", sorted(sup_files - sup) or "none")
print("S-tables cited but missing: ", sorted(sup - sup_files) or "none")
print()

# order of first citation
def first_order(pattern: str, keys) -> list[int]:
    pos = {}
    for k in keys:
        m = re.search(pattern.format(k), BODY)
        if m:
            pos[k] = m.start()
    return [k for k, _ in sorted(pos.items(), key=lambda kv: kv[1])]

fig_order = first_order(r"\bFig(?:ure)?\.?\s*{}", sorted(figs))
tab_order = first_order(r"\bTable\s*{}", sorted(tabs))
sup_order = first_order(r"\bTable S{}", sorted(sup))
print("figure first-citation order:", fig_order, "->", "sequential" if fig_order == sorted(figs) else "NOT sequential")
print("table  first-citation order:", tab_order, "->", "sequential" if tab_order == sorted(tabs) else "NOT sequential")
print("S-table first-citation order:", sup_order, "->", "sequential" if sup_order == sorted(sup) else "not sequential (allowed)")
print()

def expand(group: str) -> list[int]:
    """Vancouver ranges ("[12–14]") and lists ("[8,9]") both occur; a parser that only
    splits on commas reports six live references as uncited."""
    out: list[int] = []
    for part in group.replace("–", "-").split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            if a.strip().isdigit() and b.strip().isdigit():
                out.extend(range(int(a), int(b) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out


cited: list[int] = []
for group in re.findall(r"\[([\d,\s–-]+)\]", BODY):
    cited.extend(expand(group))
uniq = sorted(set(cited))
print("references cited:", len(uniq), "range", (min(uniq), max(uniq)) if uniq else None)
missing = [i for i in range(1, 27) if i not in uniq]
print("reference numbers never cited:", missing or "none")
extra = [i for i in uniq if i > 26]
print("citations beyond the list:", extra or "none")

# first citation order must be 1,2,3,... by construction of the renumbering
first_pos = {}
for m in re.finditer(r"\[([\d,\s–-]+)\]", BODY):
    for n in expand(m.group(1)):
        first_pos.setdefault(n, m.start())
order = [k for k, _ in sorted(first_pos.items(), key=lambda kv: kv[1])]
print("first-citation order:", order[:12], "...")
print("numbered in order of first appearance:",
      "yes" if order == list(range(1, len(order) + 1)) else "NO -> " + str(order))
