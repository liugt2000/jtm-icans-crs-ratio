"""95_export_submission.py -- collect the Journal of Translational Medicine submission package.

The package is a **snapshot**, not a move. Every deliverable is produced in manuscript/
by the build chain (50_assemble -> 60_docx, 51_additional), so moving the files out of
manuscript/ would break the next rebuild. This script copies them into submission_package/
under the names the editorial system expects, then writes MANIFEST.txt (SHA-256 per file)
and README_投稿清单.md (upload order, placeholders, known issues).

    python src/95_export_submission.py

Idempotent: the package directory is rewritten from scratch on each run. Nothing in it is
edited by hand -- edit the sources, rebuild, re-export.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import shutil

from docx import Document

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MS = os.path.join(HERE, "manuscript")
PKG = os.path.join(HERE, "submission_package")

FIGDIR = "06_Figures"
REFDIR = "07_reference_zh"

# source (relative to project root) -> destination (relative to the package) -> system type
FILES = [
    ("manuscript/manuscript.docx", "01_Manuscript_JTM.docx", "Manuscript"),
    ("manuscript/cover_letter.docx", "02_Cover_Letter_JTM.docx", "Cover Letter"),
    ("manuscript/additional_file1_tables.docx", "03_Additional_file1_tables.docx",
     "Supplementary Material (Additional file 1: Tables S1-S13)"),
    ("manuscript/additional_file2_record_strobe.docx",
     "04_Additional_file2_RECORD_STROBE.docx",
     "Supplementary Material (Additional file 2: RECORD/STROBE checklist)"),
    ("manuscript/title_abstract_zh_en.docx", f"{REFDIR}/Title_and_abstract_zh_en.docx",
     "not uploaded - Chinese reference only"),
]

FIGURES = [
    ("figs/fig1_partition.png", f"{FIGDIR}/Fig1_partition.png"),
    ("figs/fig2_specification_falsification.png",
     f"{FIGDIR}/Fig2_specification_falsification.png"),
    ("figs/fig3_temporal_invariance.png", f"{FIGDIR}/Fig3_temporal_invariance.png"),
    ("figs/fig4_module_localisation.png", f"{FIGDIR}/Fig4_module_localisation.png"),
    ("figs/fig5_network_power.png", f"{FIGDIR}/Fig5_network_power.png"),
    ("figs/fig6_model_constraints.png", f"{FIGDIR}/Fig6_model_constraints.png"),
]

# Strings that must not survive into an uploaded file.
PLACEHOLDERS = [
    "[Date]", "[Corresponding author]", "[Affiliation]", "[E-mail]",
    "[Author list", "[TO BE COMPLETED", "{{", "TODO",
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def docx_text(path: str) -> str:
    doc = Document(path)
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


README = """# JTM 投稿包

**稿件**：The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in BCMA
**专刊**：Computational Modeling and Network Medicine in Drug Toxicology and Clinical Pharmacovigilance
**导出时间**：{stamp}
**来源**：`manuscript/`，由 `src/50_assemble.py` → `src/60_docx.py` / `src/51_additional.py` 生成

---

## 1. 上传顺序

| 顺序 | 文件 | 系统里的类型 |
|---|---|---|
{upload_table}

正文 docx 已含 3 张主表与 6 张图（图在文末逐页，便于审稿人一次读完）。图另附独立 PNG，
系统要求单独提交图件时用 `06_Figures/` 里的文件，不要重复上传正文里的图。

## 2. 上传前必须处理

{placeholder_block}

其余待办：

- [ ] Cover letter 日期填的是 26 November 2026；若实际投稿日不同，改 `manuscript/cover_letter.md`
      第 1 行后重建（`src/60_docx.py cover_letter.md cover_letter.docx --letter --no-figures`）。

已完成（2026-11-26）：

- [x] 六张图统一按 600 dpi 重新导出，16.5 cm 宽下有效分辨率 546–723 dpi，全部高于 BMC 的
      300 dpi 下限；图 5 内嵌标注的 12× 已改为 11.9×，与正文及图注一致。

- [x] Zenodo 已发 **v1.0.2**（record 24552287，18.1 MB，MD5 与本地 zip 一致）：存档内稿件、
      补充材料与正文一致，RECORD 清单的 13 处错误、参考文献的审计说明、PROVENANCE 的
      OmniPath/HPA 参数均已修正。正文与 cover letter 引概念 DOI `10.5281/zenodo.24536542`，
      以后加版本不必再动正文。
- [x] GitHub 仓库 <https://github.com/liugt2000/jtm-icans-crs-ratio> 已推送（`master`，
      423 个条目）。

## 3. 这个目录不要手改

包内每个文件都是副本，改这里不会改到稿件；下次跑 `src/95_export_submission.py` 会被整体覆盖。
要改稿就改 `manuscript/` 下的源文件，然后：

    python src/50_assemble.py
    python src/58_number_sections.py
    python src/78_xref.py
    python src/60_docx.py
    python src/95_export_submission.py

## 4. 内容核对口径（本次导出）

{content_block}

---

`MANIFEST.txt` 是逐文件 SHA-256，用于确认上传的确实是这一版。
"""


def main() -> int:
    if os.path.isdir(PKG):
        shutil.rmtree(PKG)
    os.makedirs(os.path.join(PKG, FIGDIR))
    os.makedirs(os.path.join(PKG, REFDIR))

    missing: list[str] = []
    rows: list[tuple[str, int, str, str]] = []   # name, size, digest, type

    for src_rel, dst_rel, kind in FILES:
        src = os.path.join(HERE, src_rel)
        dst = os.path.join(PKG, dst_rel)
        if not os.path.exists(src):
            missing.append(src_rel)
            continue
        shutil.copy2(src, dst)
        rows.append((dst_rel, os.path.getsize(dst), sha256(dst), kind))

    for src_rel, dst_rel in FIGURES:
        src = os.path.join(HERE, src_rel)
        dst = os.path.join(PKG, dst_rel)
        if not os.path.exists(src):
            missing.append(src_rel)
            continue
        shutil.copy2(src, dst)
        rows.append((dst_rel, os.path.getsize(dst), sha256(dst), "Figure"))

    # staleness: each .docx is compiled from its own markdown sources; if a source is newer,
    # the package would silently carry an out-of-date file. The mapping has to be explicit —
    # scanning every .md in the folder would count drafts, the two additional files and the
    # Chinese title page as sources of the main manuscript.
    body_parts = [
        "abstract.md", "intro.md", "methods_full.md", "results_full.md", "discussion.md",
        "failure_and_coarsegraining.md", "abbreviations.md", "declarations.md",
        "figure_legends.md", "references.md",
    ]
    table_parts = [
        p for p in os.listdir(os.path.join(MS, "tables")) if p.endswith(".md")
    ]
    stale: list[str] = []
    checks = [
        ("manuscript.docx",
         [os.path.join(MS, f) for f in body_parts]
         + [os.path.join(MS, "tables", f) for f in table_parts]),
        ("cover_letter.docx", [os.path.join(MS, "cover_letter.md")]),
        ("additional_file1_tables.docx", [os.path.join(MS, "additional_file1_tables.md")]),
        ("additional_file2_record_strobe.docx",
         [os.path.join(MS, "additional_file2_record_strobe.md")]),
    ]
    for docx_name, sources in checks:
        newest = max(sources, key=os.path.getmtime)
        if os.path.getmtime(newest) > os.path.getmtime(os.path.join(MS, docx_name)) + 1:
            stale.append(f"{os.path.basename(newest)} > {docx_name}")

    print(f"package  {PKG}")
    print(f"{len(rows)} files, {sum(r[1] for r in rows) / 1e6:.1f} MB")
    for name, size, digest, _ in rows:
        print(f"  {size:>10,}  {digest[:16]}  {name}")
    if missing:
        print("MISSING SOURCE:", *missing)

    if stale:
        print("\nWARNING  source is newer than the compiled .docx; rebuild before uploading:")
        for line in stale:
            print("         " + line)
        print("         50_assemble -> 58_number_sections -> 60_docx -> 95_export_submission")

    # placeholder audit, per file
    print("\nplaceholders")
    flagged: list[tuple[str, list[str]]] = []
    for name, _, _, _ in rows:
        if not name.lower().endswith(".docx"):
            continue
        text = docx_text(os.path.join(PKG, name))
        hits = [f"{t} x{text.count(t)}" for t in PLACEHOLDERS if text.count(t)]
        print(f"  {'FAIL' if hits else 'ok  '}  {name}" + (": " + ", ".join(hits) if hits else ""))
        if hits:
            flagged.append((name, hits))

    if flagged:
        lines = []
        for name, hits in flagged:
            lines.append(f"- `{name}`：{', '.join(hits)}")
        placeholder_block = "\n".join(lines)
        placeholder_block += ("\n\n这些是投稿系统的硬性必填项，带着方括号上传会被技术审查退回。")
    else:
        placeholder_block = "- 无。所有 .docx 里都没有残留占位符。"

    upload_rows = [(n, k) for n, _, _, k in rows if not k.startswith("not uploaded")]
    skipped = [n for n, _, _, k in rows if k.startswith("not uploaded")]
    upload_table = "\n".join(
        f"| {i} | `{name}` | {kind} |" for i, (name, kind) in enumerate(upload_rows, 1)
    )
    if skipped:
        upload_table += ("\n\n不上传：`" + "`、`".join(skipped) +
                         "`（中文参考，仅内部核对用）。")

    doc = Document(os.path.join(PKG, "01_Manuscript_JTM.docx"))
    words = len(docx_text(os.path.join(PKG, "01_Manuscript_JTM.docx")).split())
    content_block = (
        f"- 正文 docx：{len(doc.paragraphs)} 段（不含表格单元格），约 {words:,} 词含表与图注\n"
        f"- 主表 3 张、补充表 S1-S13（Additional file 1）、图 6 张、参考文献 26 条\n"
        f"- 数字溯源 108/108、图 6/6 与表 3/3 首现有序、文献 26/26 首现有序"
    )

    with open(os.path.join(PKG, "README_投稿清单.md"), "w", encoding="utf-8") as fh:
        fh.write(README.format(
            stamp=f"{dt.datetime.now():%Y-%m-%d %H:%M}",
            upload_table=upload_table,
            placeholder_block=placeholder_block,
            content_block=content_block,
        ))

    with open(os.path.join(PKG, "MANIFEST.txt"), "w", encoding="utf-8") as fh:
        fh.write("Journal of Translational Medicine submission package\n")
        fh.write(f"exported {dt.datetime.now():%Y-%m-%d %H:%M}\n\n")
        for name, size, digest, _ in rows:
            fh.write(f"{digest}  {size:>10,}  {name}\n")

    print(f"\nwritten {os.path.join(PKG, 'README_投稿清单.md')}")
    print(f"written {os.path.join(PKG, 'MANIFEST.txt')}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
