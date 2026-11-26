"""
60_docx.py -- render manuscript.md as a submission-format Word document.

Handles the subset of Markdown the manuscript actually uses: ATX headings, bold and
italic inline runs, pipe tables, block quotes, ordered lists and page breaks before
top-level sections. Figures are appended at the end, one per page, so that the document
can be read end to end without opening six files.
"""
from __future__ import annotations

import os
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt, RGBColor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MS = os.path.join(HERE, "manuscript")
FIGS = os.path.join(HERE, "figs")

# Numbered by order of first citation in the body, as the journal requires.
# The content order is: partition -> specification -> drift -> modules -> network power -> model.
FIGURES = [
    ("figs/fig1_partition.png", "Figure 1"),
    ("figs/fig2_specification_falsification.png", "Figure 2"),
    ("figs/fig3_temporal_invariance.png", "Figure 3"),
    ("figs/fig4_module_localisation.png", "Figure 4"),
    ("figs/fig5_network_power.png", "Figure 5"),
    ("figs/fig6_model_constraints.png", "Figure 6"),
]

BODY_FONT = "Times New Roman"

# CJK punctuation and ideographs. Used only to decide whether a line join needs a space.
_CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff01-\uff65]")
# Closing full-width punctuation never takes a preceding space, and an opening bracket
# never takes a following one; a space before "（" is the most visible artefact.
_CJK_CLOSE = "，。、；：？！）】》”’…％"
_CJK_OPEN = "（【《“‘"


def join_wrapped(lines: list[str]) -> str:
    """Join the source lines of one paragraph.

    A space is inserted only when neither side is CJK. Chinese wraps at arbitrary
    characters, so the space that is right for English shows up as a gap inside a
    sentence ("与 免疫"). Joining without it keeps the Chinese text continuous while
    leaving English paragraphs unchanged.
    """
    out = ""
    for x in (x.strip() for x in lines if x.strip()):
        if not out:
            out = x
        elif x[0] in _CJK_CLOSE or x[0] in _CJK_OPEN or out[-1] in _CJK_OPEN:
            out += x
        elif _CJK.match(out[-1]) and _CJK.match(x[0]):
            out += x
        else:
            out += " " + x
    return out


def set_base_style(doc: Document, landscape: bool = False, letter: bool = False) -> None:
    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(11)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    pf = st.paragraph_format
    # The journal asks for double line spacing in the submitted manuscript; 1.5 was a
    # reading copy. Tables set their own single spacing further down. A cover letter is
    # correspondence, not the manuscript, and is set single-spaced without line numbers.
    pf.line_spacing = 1.15 if letter else 2.0
    pf.space_after = Pt(6)
    for p in doc.sections:
        p.top_margin = p.bottom_margin = Cm(2.0)
        p.left_margin = p.right_margin = Cm(2.0)
        if landscape:
            # Wide checklist tables need the long edge; without it the "how addressed"
            # column collapses to four words per line.
            from docx.enum.section import WD_ORIENT
            w, h = p.page_width, p.page_height
            p.orientation = WD_ORIENT.LANDSCAPE
            p.page_width, p.page_height = max(w, h), min(w, h)


SETTINGS_BEFORE_LN = ("w:compat", "w:rsids", "w:mathPr", "w:themeFontLang",
                      "w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
                      "w:doNotAutoCompressPictures", "w:forceUpgrade", "w:captions",
                      "w:readModeInkLockDown", "w:smartTagType", "w:schemaLibrary",
                      "w:shapeDefaults", "w:doNotEmbedSmartTags", "w:decimalSymbol",
                      "w:listSeparator")


def add_line_numbers(doc: Document) -> None:
    """Continuous line numbering, as required for review copies.

    The settings element is ordered, so the node is inserted ahead of the first
    later-positioned sibling rather than appended at the end.
    """
    settings = doc.settings.element
    if settings.find(qn("w:lnNumType")) is not None:
        return
    ln = OxmlElement("w:lnNumType")
    ln.set(qn("w:countBy"), "1")
    ln.set(qn("w:restart"), "continuous")
    ln.set(qn("w:distance"), "360")
    for tag in SETTINGS_BEFORE_LN:
        node = settings.find(qn(tag))
        if node is not None:
            node.addprevious(ln)
            return
    settings.append(ln)


def _field(par, instr: str) -> None:
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), instr)
    run = OxmlElement("w:r")
    txt = OxmlElement("w:t")
    txt.text = "1"
    run.append(txt)
    fld.append(run)
    par._p.append(fld)


def add_page_numbers(doc: Document) -> None:
    """'Page n of m' in the footer of every section."""
    for section in doc.sections:
        footer = section.footer
        par = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.line_spacing = 1.0
        par.paragraph_format.space_after = Pt(0)
        if par.runs:
            for r in list(par.runs):
                r._r.getparent().remove(r._r)
        par.add_run("Page ")
        _field(par, " PAGE ")
        par.add_run(" of ")
        _field(par, " NUMPAGES ")
        for r in par.runs:
            r.font.size = Pt(9)
            r.font.name = BODY_FONT


INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_runs(par, text: str) -> None:
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            r = par.add_run(piece[2:-2]); r.bold = True
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            r = par.add_run(piece[1:-1]); r.italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(9.5)
        else:
            par.add_run(piece)


def is_table_line(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def parse_table(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


def add_table(doc: Document, rows: list[list[str]]) -> None:
    ncol = max(len(r) for r in rows)
    t = doc.add_table(rows=0, cols=ncol)
    t.style = "Table Grid"
    t.autofit = False
    t.allow_autofit = False
    for i, r in enumerate(rows):
        cells = t.add_row().cells
        for j in range(ncol):
            txt = r[j] if j < len(r) else ""
            par = cells[j].paragraphs[0]
            par.paragraph_format.line_spacing = 1.0
            par.paragraph_format.space_after = Pt(1)
            add_runs(par, txt)
            for run in par.runs:
                run.font.size = Pt(8.5)
                if i == 0:
                    run.bold = True

    # Column widths proportional to sqrt(max cell length), with a floor set by the
    # longest unbreakable word in each column. Without the floor a header like
    # "interaction" is split mid-word; without the proportional share the prose column
    # collapses to a few words per line. All arithmetic is in centimetres -- mixing EMU
    # and cm here silently makes the floor zero.
    sec = doc.sections[0]
    avail = (sec.page_width - sec.left_margin - sec.right_margin) / 360000.0
    CHAR_CM = 0.175          # approx advance width at 8.5 pt Times New Roman
    longest = [0] * ncol
    longest_word = [1] * ncol
    for r in rows:
        for j in range(min(ncol, len(r))):
            longest[j] = max(longest[j], len(r[j]))
            for word in re.split(r"[\s/]+", r[j]):
                longest_word[j] = max(longest_word[j], len(word))

    floor = [min(avail / ncol * 1.6, longest_word[j] * CHAR_CM + 0.3)
             for j in range(ncol)]
    weights = [max(3.0, v) ** 0.5 for v in longest]

    # Water-filling: columns that would fall below their floor are pinned at the floor,
    # the remainder of the width is shared among the rest in proportion to weight.
    pinned = [False] * ncol
    widths = [0.0] * ncol
    for _ in range(3):
        free = [j for j in range(ncol) if not pinned[j]]
        used = sum(floor[j] for j in range(ncol) if pinned[j])
        tot_w = sum(weights[j] for j in free) or 1.0
        for j in free:
            widths[j] = (avail - used) * weights[j] / tot_w
            if widths[j] < floor[j]:
                widths[j] = floor[j]
                pinned[j] = True
    if sum(widths) > avail:                     # floors alone overflow: scale the rest
        excess = sum(widths) - avail
        shrinkable = [j for j in range(ncol) if widths[j] > floor[j] + 1e-9]
        if shrinkable:
            tot_s = sum(widths[j] - floor[j] for j in shrinkable)
            for j in shrinkable:
                widths[j] -= excess * (widths[j] - floor[j]) / tot_s

    for j, width in enumerate(widths):
        length = Cm(width)
        # Both the grid column and every cell must carry the width: Word honours the
        # grid when tables are not autofitted, but other renderers read the cell.
        t.columns[j].width = length
        for cell in t.columns[j].cells:
            cell.width = length

    doc.add_paragraph()


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else [])
    src_name = argv[0] if argv else "manuscript.md"
    out_name = argv[1] if len(argv) > 1 else "manuscript.docx"
    with_figures = "--no-figures" not in argv
    landscape = "--landscape" in argv
    letter = "--letter" in argv

    src = open(os.path.join(MS, src_name), encoding="utf-8").read().split("\n")
    doc = Document()
    set_base_style(doc, landscape, letter)
    if not letter:
        add_line_numbers(doc)

    first_h1 = True
    i = 0

    # Markdown wraps a paragraph over several source lines. Rendering one paragraph per
    # line leaves bold spans unclosed (literal ** in the output) and, under justification,
    # stretches each short line across the measure. Lines are therefore buffered and
    # flushed as one paragraph at a blank line or at the next block construct.
    buf: list[str] = []
    buf_style = "plain"
    buf_number = ""

    def flush() -> None:
        nonlocal buf, buf_style, buf_number
        if not buf:
            return
        text = join_wrapped(buf)
        buf.clear()
        if not text:
            return
        if buf_style == "bullet":
            par = doc.add_paragraph(style="List Bullet")
            add_runs(par, text)
        elif buf_style == "number":
            # The literal number is written into the text. Word's List Number counter
            # runs on across the document, which would renumber the 25 references as
            # 7-31 immediately after the six failure modes.
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.75)
            par.paragraph_format.first_line_indent = Cm(-0.75)
            par.paragraph_format.space_after = Pt(3)
            add_runs(par, f"{buf_number}. {text}")
        else:
            par = doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(par, text)
        buf_style = "plain"
        buf_number = ""

    while i < len(src):
        line = src[i]
        s = line.rstrip()

        if not s:
            flush()
            i += 1
            continue

        if s == "---":
            flush()
            i += 1
            continue

        if s.startswith("# "):
            flush()
            if first_h1:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                r = p.add_run(s[2:].strip())
                r.bold = True
                r.font.size = Pt(16)
                r.font.name = BODY_FONT
                first_h1 = False
            else:
                doc.add_page_break()
                doc.add_heading(s[2:].strip(), level=1)
            i += 1
            continue

        if s.startswith("## "):
            flush()
            doc.add_heading(s[3:].strip(), level=2)
            i += 1
            continue

        if s.startswith("### "):
            flush()
            doc.add_heading(s[4:].strip(), level=3)
            i += 1
            continue

        # table block
        if is_table_line(s):
            flush()
            block = []
            while i < len(src) and is_table_line(src[i].rstrip()):
                block.append(src[i].rstrip())
                i += 1
            add_table(doc, parse_table(block))
            continue

        # block quote
        if s.startswith(">"):
            flush()
            qbuf = []
            while i < len(src) and src[i].rstrip().startswith(">"):
                qbuf.append(src[i].rstrip().lstrip(">").strip())
                i += 1
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.8)
            par.paragraph_format.right_indent = Cm(0.8)
            add_runs(par, " ".join(b for b in qbuf if b))
            for r in par.runs:
                r.italic = True
            continue

        # ordered list item
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            flush()
            buf_style = "number"
            buf_number = m.group(1)
            buf.append(m.group(2))
            i += 1
            continue

        # bullet
        if s.startswith("- "):
            flush()
            buf_style = "bullet"
            buf.append(s[2:])
            i += 1
            continue

        buf.append(s)
        i += 1

    flush()

    # ---- figures, one per page
    if with_figures:
        doc.add_page_break()
        doc.add_heading("Figures", level=1)
        for path, label in FIGURES:
            full = os.path.join(HERE, path)
            if not os.path.exists(full):
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(full, width=Cm(16.5))
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = cap.add_run(f"{label}. See figure legends section for the full caption.")
            r.font.size = Pt(9)
            r.italic = True
            doc.add_page_break()

    out = os.path.join(MS, out_name)
    if not letter:
        add_page_numbers(doc)
    doc.save(out)
    print("written", out, os.path.getsize(out) // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
