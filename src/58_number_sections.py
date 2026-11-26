"""58_number_sections.py -- put the manuscript into the section scheme of the group's
previous JTM paper (I020, manuscript R1), so the two read as one series.

What changes:
  * "Background" becomes "1. Introduction" (the abstract keeps its "Background." lead,
    as it does in the I020 paper).
  * Methods and Results carry numbered subsections (2.1..., 3.1...).
  * Discussion is numbered 4.1..., with the failure section folded in as 4.6 and
    Limitations as 4.7; the standalone "Conclusions" heading becomes a run-in
    "Conclusions." paragraph at the end of the Discussion, which is how I020 ends.
  * Display sections are numbered 5. Tables, 6. Figure legends, 7. References.

Idempotent: a heading that already carries a number is left alone.
"""
from __future__ import annotations

import re
from pathlib import Path

MS = Path(__file__).resolve().parents[1] / "manuscript"


def renumber(path: Path, prefix: str, h1_from: str, h1_to: str,
             keep: dict[str, str] | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if h1_from in text:
        text = text.replace(h1_from, h1_to, 1)

    keep = keep or {}
    n = 0
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and not re.match(r"## \d", line):
            title = line[3:].strip()
            if title in keep:
                out.append(keep[title])
            else:
                n += 1
                out.append(f"## {prefix}.{n} {title}")
        else:
            out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{path.name:38} h1 -> {h1_to!r:24} numbered {n} subsections")


def main() -> int:
    renumber(MS / "intro.md", "1", "# Background", "# 1. Introduction")
    renumber(MS / "methods_full.md", "2", "# Methods", "# 2. Methods")
    renumber(MS / "results_full.md", "3", "# Results", "# 3. Results")

    # Discussion: five open subsections, then the failure section (4.6, supplied by
    # failure_and_coarsegraining.md at assembly time), then Limitations as 4.7.
    renumber(MS / "discussion.md", "4", "# Discussion", "# 4. Discussion")
    d = (MS / "discussion.md").read_text(encoding="utf-8")
    d = d.replace("## 4.6 Limitations", "## 4.7 Limitations")

    # Conclusions becomes a run-in closing paragraph, as in the I020 paper.
    if "# Conclusions" in d:
        head, tail = d.split("# Conclusions", 1)
        tail = tail.lstrip()
        tail = re.sub(r"^(?!\*\*)", "**Conclusions.** ", tail, count=1)
        d = head.rstrip() + "\n\n" + tail
    (MS / "discussion.md").write_text(d, encoding="utf-8")
    print("discussion.md: Limitations -> 4.7; Conclusions folded to a run-in paragraph")

    # Failure section: demoted to a Discussion subsection, its own subsection to H3.
    f = (MS / "failure_and_coarsegraining.md").read_text(encoding="utf-8")
    f = f.replace("# How this model fails", "## 4.6 How this model fails", 1)
    f = f.replace("## Coarse-graining statement", "### Coarse-graining statement", 1)
    (MS / "failure_and_coarsegraining.md").write_text(f, encoding="utf-8")
    print("failure_and_coarsegraining.md: H1 -> 4.6, nested H2 -> H3")

    # Display sections.
    for name, old, new in [("references.md", "# References", "# 7. References"),
                           ("figure_legends.md", "# Figure legends", "# 6. Figure legends")]:
        p = MS / name
        t = p.read_text(encoding="utf-8")
        if old in t:
            p.write_text(t.replace(old, new, 1), encoding="utf-8")
            print(f"{name:38} {old!r} -> {new!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
