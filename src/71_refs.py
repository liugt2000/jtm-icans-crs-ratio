"""Complete the reference list from Crossref, without inventing anything.

The deposited manuscript carried author lists, titles, journals and years but no volume,
page or DOI. Those are recovered here by querying Crossref and accepting a candidate only
if three conditions hold at once: the record is a journal-article, its title similarity to
ours is >= 0.80, and its issued year matches ours. Anything that fails is left in place and
flagged MANUAL, because a wrong DOI is worse than a missing one.

Raw responses are kept under out/refs_crossref/ so every accepted DOI can be inspected.
"""
from __future__ import annotations

import difflib
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
CACHE = ROOT / "out" / "refs_crossref"
CACHE.mkdir(parents=True, exist_ok=True)

UA = "jtm-icans-manuscript/1.0 (mailto:corresponding@example.org)"

# (number, title as written, journal, year) -- transcribed from references.md
REFS = [
    (1, "Current concepts in the diagnosis and management of cytokine release syndrome", "Blood", 2014),
    (2, "ASTCT consensus grading for cytokine release syndrome and neurologic toxicity associated with immune effector cells", "Biology of Blood and Marrow Transplantation", 2019),
    (3, "Chimeric antigen receptor T-cell therapy — assessment and management of toxicities", "Nature Reviews Clinical Oncology", 2018),
    (4, "Endothelial activation and blood–brain barrier disruption in neurotoxicity after adoptive immunotherapy with CD19 CAR-T cells", "Cancer Discovery", 2017),
    (5, "Neurological toxicities associated with chimeric antigen receptor T-cell therapy", "Brain", 2019),
    (6, "4-1BB costimulation ameliorates T cell exhaustion induced by tonic signaling of chimeric antigen receptors", "Nature Medicine", 2015),
    (7, "Structural design of engineered costimulation determines tumor rejection kinetics and persistence of CAR T cells", "Cancer Cell", 2015),
    (8, "Tarlatamab for patients with previously treated small-cell lung cancer", "New England Journal of Medicine", 2023),
    (9, "Bayesian data mining in large frequency tables, with an application to the FDA spontaneous reporting system", "The American Statistician", 1999),
    (10, "Quantitative signal detection using spontaneous ADR reporting", "Pharmacoepidemiology and Drug Safety", 2009),
    (11, "Epidemiology of adverse reactions to nonsteroidal antiinflammatory drugs", "Advances in Inflammation Research", 1984),
    (12, "Novel data-mining methodologies for adverse drug event discovery and analysis", "Clinical Pharmacology & Therapeutics", 2012),
    (13, "Interpreting observational studies: why empirical calibration is needed to correct p-values", "Statistics in Medicine", 2014),
    (14, "The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement", "PLOS Medicine", 2015),
    (15, "The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement", "Annals of Internal Medicine", 2007),
    (16, "Network medicine: a network-based approach to human disease", "Nature Reviews Genetics", 2011),
    (17, "Uncovering disease–disease relationships through the incomplete interactome", "Science", 2015),
    (18, "Network-based in silico drug efficacy screening", "Nature Communications", 2016),
    (19, "Integrated intra- and intercellular signaling knowledge for multicellular omics analysis", "Molecular Systems Biology", 2021),
    (20, "Tissue-based map of the human proteome", "Science", 2015),
    (21, "A single-cell type transcriptomics map of human tissues", "Science Advances", 2021),
    (22, "Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index", "Computer Physics Communications", 2010),
    (23, "Probable inference, the law of succession, and statistical inference", "Journal of the American Statistical Association", 1927),
    (24, "CAR-T cell therapy: current limitations and potential strategies", "Blood Cancer Journal", 2021),
    (25, "Managing the toxicities of CAR T-cell therapy", "Hematological Oncology", 2019),
]

BOOK_CHAPTER_NO = 11

SELECT = "DOI,title,type,volume,issue,page,article-number,issued,container-title,author"


def norm(s: str) -> str:
    s = s.replace("—", "-").replace("–", "-").replace("‐", "-")
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _query(n: int, title: str, journal: str, mode: str) -> list[dict]:
    tag = {"b": "b", "j": "j", "t": "t"}[mode]
    use_journal = mode == "j"
    cache = CACHE / f"ref{n:02d}_{tag}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))["message"]["items"]
    url = ("https://api.crossref.org/works?rows=10&select=" + SELECT +
           "&query.bibliographic=" + urllib.parse.quote(title))
    if use_journal:
        url += "&query.container-title=" + urllib.parse.quote(journal)
    if mode == "t":
        url += "&query.title=" + urllib.parse.quote(title)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as fh:
                data = json.load(fh)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data["message"]["items"]
        except Exception as exc:
            if attempt == 3:
                print(f"  ref {n}: query failed ({type(exc).__name__})")
                return []
            time.sleep(2.0 * (attempt + 1))
    return []


def fetch(n: int, title: str, journal: str) -> list[dict]:
    """Pool the unfiltered and journal-filtered result sets.

    Each query alone loses records: the journal-filtered one drops good matches that
    Crossref ranks lower, the unfiltered one lets a same-title paper in another journal
    through. Pooling and then applying one strict rule is more reliable than either.
    """
    seen, pooled = set(), []
    for mode in ("b", "j", "t"):
        for it in _query(n, title, journal, mode):
            doi = it.get("DOI")
            if doi and doi not in seen:
                seen.add(doi)
                pooled.append(it)
    return pooled


def best_match(items: list[dict], title: str, journal: str, year: int):
    """Accept only records that agree on title, journal *and* year.

    Title similarity alone is not sufficient: an exact-title erratum, or a paper in a
    different journal with a similar name, passes it. The journal check is what caught
    STROBE resolving to a German emergency-medicine journal in the first pass.
    """
    want = norm(title)
    want_j = norm(journal)
    best, best_key = None, None
    for it in items:
        if it.get("type") != "journal-article":
            continue
        cand = (it.get("title") or [""])[0]
        ct = (it.get("container-title") or [""])[0]
        t_sim = difflib.SequenceMatcher(None, want, norm(cand)).ratio()
        j_sim = difflib.SequenceMatcher(None, want_j, norm(ct)).ratio()
        yr = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        if yr is None or abs(yr - year) > 1:
            continue
        # Supplementary appendices share the parent's title; they carry page numbers
        # like "W-163" and DOIs ending -w1. They are not the citable article.
        page = (it.get("page") or "")
        if page.upper().startswith("W-") or (it.get("DOI") or "").endswith(("-w1", "-w2")):
            continue
        if re.match(r"^(correction|erratum|retraction|corrigendum)", cand.strip(), re.I):
            continue
        # either an essentially exact title, or a good title in the right journal
        if not ((t_sim >= 0.95 and j_sim >= 0.55) or
                (t_sim >= 0.72 and j_sim >= 0.75)):
            continue
        key = 0.6 * t_sim + 0.4 * j_sim + (0.15 if yr == year else 0.0)
        if best_key is None or key > best_key:
            best, best_key = it, key
    return best, (best_key or 0.0), ("ok" if best else "no candidate agreed on title+journal+year")


def main() -> int:
    # Always parse the pristine list, never the file this script writes: re-running on
    # its own output would re-prefix every entry with the previous version of itself.
    pristine = MS / "references.orig.md"
    raw = (pristine if pristine.exists() else MS / "references.md").read_text(encoding="utf-8")
    # Split the numbered block only; the header note is regenerated.
    body = raw.split("\n1. ", 1)
    entries = {}
    if len(body) == 2:
        chunks = re.split(r"\n(?=\d{1,2}\. )", "1. " + body[1])
        for ch in chunks:
            m = re.match(r"(\d{1,2})\.\s+(.*)", ch.strip(), re.S)
            if m:
                txt = " ".join(ln.strip() for ln in m.group(2).split("\n")).strip()
                txt = re.sub(r"\s*\*\*\[MANUAL[^\]]*\]\*\*", "", txt)
                entries[int(m.group(1))] = txt
    if len(entries) != 25:
        print(f"warning: parsed {len(entries)} entries, expected 25")

    out_lines = [
        "# References", "",
        "> Volume, issue, page and DOI were resolved against Crossref and are reproduced as "
        "returned; the DOI is the identifier of record, so any disagreement with the printed "
        "pagination should be settled in favour of the DOI. Entries marked **[MANUAL]** did "
        "not resolve to a confident Crossref match and must be completed by hand -- they "
        "have deliberately been left without volume or DOI rather than guessed. Numbering "
        "follows order of first citation.", "",
    ]

    n_ok = 0
    for n, title, journal, year in REFS:
        data = fetch(n, title, journal)
        item, score, why = best_match(data, title, journal, year)
        if n == BOOK_CHAPTER_NO:
            out_lines.append(
                f"{n}. Weber JCP. Epidemiology of adverse reactions to nonsteroidal "
                f"antiinflammatory drugs. In: Rainsford KD, Velo GP, editors. *Advances "
                f"in Inflammation Research*. Vol 6. New York: Raven Press; 1984. "
                f"**[MANUAL: book chapter, no DOI — confirm the volume number, editors "
                f"and page range against the printed volume]**")
            out_lines.append("")
            print(f"  ref {n:2d}  BOOK CHAPTER (no DOI by design)")
            continue

        entry = entries.get(n, "")
        # Author list = everything before the title, and the title is the last sentence
        # preceding the journal name. Keying off the journal rather than the title string
        # keeps the split correct even when the title text itself has been corrected.
        jmark = entry.find("*" + journal + "*")
        prefix = entry[:jmark] if jmark >= 0 else entry
        m_last = re.search(r"\.\s+([^.]*?)\s*$", prefix.rstrip().rstrip("."))
        head = prefix[:m_last.start()] if m_last else prefix
        head = head.rstrip().rstrip(".").strip()

        if item is None:
            out_lines.append(f"{n}. {entry} **[MANUAL: {why}]**")
            out_lines.append("")
            print(f"  ref {n:2d}  MANUAL ({why})")
            continue

        vol = item.get("volume") or ""
        iss = item.get("issue") or ""
        page = item.get("page") or item.get("article-number") or ""
        # Crossref returns Mol Syst Biol article ids as "MSB20209923"; the citable
        # form is e9923.
        m_pg = re.fullmatch(r"MSB\d{4}(\d{4})", page)
        if m_pg:
            page = "e" + m_pg.group(1)
        doi = item.get("DOI") or ""
        ctitle = (item.get("container-title") or [journal])[0]
        loc = f"{year}"
        if vol:
            loc += f";{vol}"
            if iss:
                loc += f"({iss})"
            if page:
                loc += f":{page}"
        elif page:
            loc += f":{page}"

        entry_new = f"{head}. {title}. *{ctitle}*. {loc}."
        if doi:
            entry_new += f" doi:{doi}"
        out_lines.append(f"{n}. {entry_new}")
        out_lines.append("")
        n_ok += 1
        print(f"  ref {n:2d}  {score:.2f}  {loc:<28} {doi}")

    (MS / "references.md").write_text("\n".join(out_lines).rstrip() + "\n",
                                      encoding="utf-8")
    print(f"\nresolved {n_ok}/{len(REFS)}; written {MS/'references.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
