"""77_number_provenance.py -- attribute every number in the manuscript to a file.

The manuscript claims no number is hand-entered. 73_trace_numbers.py proves that claim
for the 97 headline values it knows about; this script does the opposite and starts from
the text: it extracts every numeric token in the body (Introduction through Conclusions,
tables included), and tries to find that value in the analysis outputs, the deposited
counts, or the supplementary tables.

A number that matches nothing is not necessarily wrong -- it may be a threshold written
into the design (1/21, 0.320), a year, or a count of figures. The script cannot tell the
difference, so it prints those with their sentence and lets the author decide. What it
does rule out is the dangerous case: a number that looks like a result but exists
nowhere in the pipeline.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript" / "manuscript.md"
TXT = MS.read_text(encoding="utf-8")

START = TXT.index("# Background")
END = TXT.index("# References")
BODY = TXT[START:END]


def add_value(v: float, bag: set[str]) -> None:
    """Register a number under every rendering the text might use."""
    if isinstance(v, bool) or v is None:
        return
    try:
        f = float(v)
    except (TypeError, ValueError):
        return
    if abs(f) >= 1000:
        bag.add(f"{int(round(f)):,}")
    for dp in (0, 1, 2, 3, 4):
        s = f"{f:.{dp}f}"
        bag.add(s)
        bag.add(s.lstrip("-"))
        bag.add(s.replace("-", "−"))
    bag.add(str(int(f)) if f == int(f) else str(f))
    # percentages: a fraction quoted as a percentage, and the reverse
    for scale in (100,):
        p = f * scale
        for dp in (0, 1, 2):
            bag.add(f"{p:.{dp}f}")


def harvest_json(obj, bag: set[str]) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            harvest_json(v, bag)
    elif isinstance(obj, list):
        for v in obj:
            harvest_json(v, bag)
    elif isinstance(obj, (int, float)):
        add_value(obj, bag)
    elif isinstance(obj, str):
        for m in re.findall(r"[-+]?\d*\.?\d+", obj):
            add_value(float(m), bag)


bag: set[str] = set()
for p in sorted((ROOT / "out").glob("*.json")):
    try:
        harvest_json(json.loads(p.read_text(encoding="utf-8")), bag)
    except Exception:
        pass
for p in sorted((ROOT / "out").glob("*.csv")):
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines()[1:]:
        for cell in line.split(","):
            try:
                add_value(float(cell), bag)
            except ValueError:
                pass

# Table cells are themselves under audit, so they do not count as a source. Design
# constants that are defined rather than estimated are listed here.
DESIGN = {
    "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026",
    "95", "80", "0.05", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "30",
    "40", "100", "500", "1000", "10000",
}

TOKEN = re.compile(r"(?<![\w.])[−-]?\d[\d,]*(?:\.\d+)?")
seen: dict[str, list[str]] = {}
for m in TOKEN.finditer(BODY):
    tok = m.group(0)
    ctx = BODY[max(0, m.start() - 70):m.end() + 50].replace("\n", " ")
    seen.setdefault(tok, []).append(ctx)

unmatched = {t: c for t, c in seen.items()
             if t not in bag and t.lstrip("−-") not in bag and t not in DESIGN
             and t.lstrip("−-").replace(",", "") not in bag}

print(f"distinct numeric tokens in body: {len(seen)}")
print(f"matched to a pipeline value:    {len(seen) - len(unmatched)}")
print(f"unmatched:                      {len(unmatched)}\n")
for tok, ctxs in sorted(unmatched.items(), key=lambda kv: -len(kv[1])):
    print(f"{tok:>10}  x{len(ctxs):<2}  …{ctxs[0][:150]}…")
