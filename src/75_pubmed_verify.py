"""
75_pubmed_verify.py -- check every reference in manuscript/references.md against PubMed.

The manuscript's reference list was assembled from Crossref, which confirms that a DOI
exists but not that it resolves to the paper the sentence actually cites. This script
asks the other question: does PubMed hold a record with this title, in this journal, in
this year, at this volume and page? Mismatches are printed rather than silently fixed --
the printed volume is the one a reader will look for.

Records that PubMed does not index (book chapters, statistical methods papers in
non-biomedical journals, web resources) are reported as NOT_INDEXED, with a Crossref
fallback so that "not in PubMed" does not read as "possibly fabricated".
"""
from __future__ import annotations

import csv
import difflib
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "manuscript"
OUT = ROOT / "out"
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)
CACHE = AUDIT / "refs_pubmed_cache"
CACHE.mkdir(parents=True, exist_ok=True)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
UA = {"User-Agent": "jtm-icans-refcheck/1.0 (mailto:corresponding@example.org)"}


def fetch(url: str) -> bytes:
    key = CACHE / (re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:] + ".xml")
    if key.exists():
        return key.read_bytes()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as fh:
        data = fh.read()
    key.write_bytes(data)
    time.sleep(0.4)  # NCBI allows 3 requests per second without an API key
    return data


def esearch(term: str) -> list[str]:
    url = EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmode": "json", "retmax": "5"})
    js = json.loads(fetch(url))
    return js["esearchresult"].get("idlist", [])


def efetch(pmid: str) -> dict:
    url = EUTILS + "efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "xml"})
    root = ET.fromstring(fetch(url))
    art = root.find(".//PubmedArticle")
    if art is None:
        return {}
    cit = art.find("MedlineCitation")
    a = cit.find("Article")
    title = "".join(a.find("ArticleTitle").itertext()) if a.find("ArticleTitle") is not None else ""
    journal = a.findtext("Journal/Title") or ""
    iso = a.findtext("Journal/ISOAbbreviation") or ""
    year = (a.findtext("Journal/JournalIssue/PubDate/Year")
            or (a.findtext("Journal/JournalIssue/PubDate/MedlineDate") or "")[:4])
    vol = a.findtext("Journal/JournalIssue/Volume") or ""
    issue = a.findtext("Journal/JournalIssue/Issue") or ""
    pages = a.findtext("Pagination/MedlinePgn") or ""
    first = ""
    al = a.findall("AuthorList/Author")
    if al:
        first = (al[0].findtext("LastName") or "") + " " + (al[0].findtext("Initials") or "")
    doi = ""
    for aid in art.findall(".//ArticleIdList/ArticleId"):
        if aid.get("IdType") == "doi":
            doi = aid.text or ""
    return {"pmid": pmid, "title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
            "journal": journal, "iso": iso, "year": year, "volume": vol,
            "issue": issue, "pages": pages, "first_author": first.strip(), "doi": doi}


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"&[a-z]+;", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(pubmed_title: str, ref_title: str) -> float:
    """Compare titles, allowing for the section rubric PubMed prepends.

    Science indexes these papers under a heading ("Proteomics.", "Disease networks.")
    that is not part of the article title. Taking the better of the two readings keeps
    a correct reference from being reported as a mismatch.
    """
    a, b = norm(pubmed_title), norm(ref_title)
    best = difflib.SequenceMatcher(None, a, b).ratio()
    m = re.match(r"^([A-Za-z ]{4,22})\.\s+(.*)$", pubmed_title.strip())
    if m:
        best = max(best, difflib.SequenceMatcher(None, norm(m.group(2)), b).ratio())
    return best


STOP = {"a", "an", "the", "of", "in", "for", "and", "with", "to", "on", "by"}


def key_words(s: str) -> list[str]:
    return [w for w in norm(s).split() if w not in STOP and len(w) > 2]


def parse_refs(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    entries = []
    for block in re.split(r"\n(?=\d+\.\s)", text):
        m = re.match(r"^(\d+)\.\s+(.*)$", block.strip(), flags=re.S)
        if not m:
            continue
        n, body = int(m.group(1)), " ".join(m.group(2).split())
        doi = ""
        dm = re.search(r"doi:(10\.\S+?)(?:\s|$)", body)
        if dm:
            doi = dm.group(1).rstrip(".")
        journal = ""
        jm = re.search(r"\*([^*]+)\*", body)
        if jm:
            journal = jm.group(1).strip()
        year = ""
        ym = re.search(r"\b(19|20)\d{2}\b(?!.*\b(19|20)\d{2}\b)", body)
        ym2 = re.search(r"\.\s((?:19|20)\d{2});", body)
        year = (ym2.group(1) if ym2 else (ym.group(0) if ym else ""))
        vol = issue = pages = ""
        vm = re.search(r"(?:19|20)\d{2};([^(:]*)(?:\(([^)]*)\))?:([^.]*)\.", body)
        if vm:
            vol, issue, pages = vm.group(1).strip(), (vm.group(2) or ""), vm.group(3).strip()
        # title: text after the author list, before the italic journal name. "et al."
        # ends the list in most entries and is the only reliable delimiter -- a regex
        # anchored on the first ". " pulls in the author names whenever the list is
        # truncated, which silently lowers every title match.
        title = ""
        if jm:
            head = body[:jm.start()].strip()
            if "et al." in head:
                title = head.split("et al.", 1)[1].strip()
            else:
                tm = re.search(r"\.\s+([A-Z].*?)\.?\s*$", head)
                title = tm.group(1).strip() if tm else head
        entries.append({"n": n, "raw": body, "doi": doi, "journal": journal,
                        "year": year, "volume": vol, "issue": issue, "pages": pages,
                        "title": title})
    return entries


def search_ref(ref: dict) -> tuple[str, list[str], str]:
    """Return (query, pmids, strategy)."""
    if ref["doi"]:
        pmids = esearch(f"{ref['doi']}[doi]")
        if pmids:
            return f"{ref['doi']}[doi]", pmids, "doi"
    words = key_words(ref["title"])[:8] or key_words(ref["raw"])[:8]
    term = " ".join(words)
    return term, esearch(term), "title"


def crossref(doi: str) -> dict:
    """Metadata for the DOIs PubMed does not index (statistics, physics, book chapters)."""
    if not doi:
        return {}
    key = CACHE / ("cr_" + re.sub(r"[^A-Za-z0-9]+", "_", doi) + ".json")
    if key.exists():
        js = json.loads(key.read_text(encoding="utf-8"))
    else:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
        req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
        js = json.loads(urllib.request.urlopen(req, timeout=30).read())["message"]
        key.write_text(json.dumps(js), encoding="utf-8")
        time.sleep(0.3)
    parts = js.get("issued", {}).get("date-parts", [[""]])[0]
    return {"title": (js.get("title") or [""])[0], "journal": (js.get("container-title") or [""])[0],
            "year": str(parts[0]) if parts and parts[0] else "", "volume": js.get("volume", ""),
            "pages": js.get("page", "")}


def url_status(url: str) -> int:
    """HTTP status for a web resource cited as a reference. A dead URL is a citation
    defect even when the resource is real, because the reader cannot reach it."""
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        return urllib.request.urlopen(req, timeout=25).status
    except Exception as e:  # noqa: BLE001 - the point is to report, not to raise
        code = getattr(e, "code", None)
        return int(code) if code else 0


def main() -> int:
    refs = parse_refs(MS / "references.md")
    rows = []
    for ref in refs:
        query, pmids, how = search_ref(ref)
        best, best_sim = None, 0.0
        near = ""
        for pmid in pmids:
            rec = efetch(pmid)
            if not rec:
                continue
            # A title search for a paper PubMed does not index returns the nearest
            # modern paper with a similar name (Wilson 1927 -> a 2025 paper). Without
            # this guard the check reports a mismatch instead of an absence, which are
            # different findings: one is a citation error, the other is a database gap.
            if ref["year"] and rec["year"] and abs(int(ref["year"]) - int(rec["year"])) > 1:
                if not near:
                    near = f"nearest PubMed record is {rec['year']} (PMID {rec['pmid']})"
                continue
            sim = title_sim(rec["title"], ref["title"])
            if sim > best_sim:
                best, best_sim = rec, sim
        if best is None:
            # Not indexed in PubMed. Confirm the DOI elsewhere so that "not in PubMed"
            # is not mistaken for "possibly fabricated".
            if not ref["doi"] and "http" in ref["raw"]:
                url = re.search(r"https?://\S+", ref["raw"]).group(0).rstrip(".")
                code = url_status(url)
                rows.append({**{k: ref[k] for k in ("n", "title", "journal", "year", "volume", "issue", "pages", "doi")},
                             "status": "OK_URL" if code == 200 else "CHECK_URL", "pmid": "",
                             "pm_title": "", "pm_journal": "", "pm_year": "", "pm_volume": "",
                             "pm_pages": "", "similarity": "0", "query": url, "strategy": "url",
                             "note": f"HTTP {code}"})
                print(f"{ref['n']:>2} URL {code}        {url}")
                continue
            cross = crossref(ref["doi"]) if ref["doi"] else {}
            if cross:
                notes = []
                if difflib.SequenceMatcher(None, norm(cross["title"]), norm(ref["title"])).ratio() < 0.90:
                    notes.append("title differs")
                if cross["year"] and ref["year"] and cross["year"] != ref["year"]:
                    notes.append(f"year {ref['year']} vs {cross['year']}")
                if ref["volume"] and cross["volume"] and ref["volume"] != cross["volume"]:
                    notes.append(f"vol {ref['volume']} vs {cross['volume']}")
                status = "OK_CROSSREF" if not notes else "CHECK_CROSSREF"
                rows.append({**{k: ref[k] for k in ("n", "title", "journal", "year", "volume", "issue", "pages", "doi")},
                             "status": status, "pmid": "", "pm_title": cross["title"],
                             "pm_journal": cross["journal"], "pm_year": cross["year"],
                             "pm_volume": cross["volume"], "pm_pages": cross["pages"],
                             "similarity": "0", "query": query, "strategy": "crossref",
                             "note": "; ".join(notes)})
                print(f"{ref['n']:>2} {status:<15} crossref {cross['journal'][:30]} "
                      f"{cross['year']};{cross['volume']}:{cross['pages']} {'; '.join(notes)}")
                continue
            rows.append({**{k: ref[k] for k in ("n", "title", "journal", "year", "volume", "issue", "pages", "doi")},
                         "status": "NOT_INDEXED", "pmid": "", "pm_title": "", "pm_journal": "",
                         "pm_year": "", "pm_volume": "", "pm_pages": "", "similarity": "0",
                         "query": query, "strategy": how, "note": near or "no DOI: verified by hand"})
            print(f"{ref['n']:>2} NOT_INDEXED     {ref['title'][:60]}  {near}")
            continue
        notes = []
        if best_sim < 0.90:
            notes.append(f"title_sim={best_sim:.2f}")
        if str(ref["year"]) != str(best["year"]):
            notes.append(f"year {ref['year']} vs {best['year']}")
        # "37(S1)" and "37 Suppl 1" are the same volume; journals differ only in how
        # they render a supplement, so compare the volume number itself.
        if ref["volume"] and best["volume"]:
            va = re.sub(r"[^0-9]", "", ref["volume"].split("(")[0])
            vb = re.sub(r"[^0-9]", "", best["volume"].split(" ")[0])
            if va and vb and va != vb:
                notes.append(f"vol {ref['volume']} vs {best['volume']}")
        if ref["pages"] and best["pages"]:
            a = re.sub(r"[^0-9]", "", ref["pages"].split("-")[0])
            b = re.sub(r"[^0-9]", "", best["pages"].split("-")[0])
            if a and b and a != b:
                notes.append(f"pages {ref['pages']} vs {best['pages']}")
        status = "OK" if not notes else "CHECK"
        rows.append({**{k: ref[k] for k in ("n", "title", "journal", "year", "volume", "issue", "pages", "doi")},
                     "status": status, "pmid": best["pmid"], "pm_title": best["title"],
                     "pm_journal": best["journal"], "pm_year": best["year"],
                     "pm_volume": best["volume"], "pm_pages": best["pages"],
                     "similarity": f"{best_sim:.3f}", "query": query, "strategy": how,
                     "note": "; ".join(notes)})
        print(f"{ref['n']:>2} {status:<13} pmid={best['pmid']:<9} sim={best_sim:.2f} "
              f"{'; '.join(notes)} | {best['journal'][:34]} {best['year']};{best['volume']}:{best['pages']}")

    with (AUDIT / "refs_pubmed.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n_ok = sum(r["status"] in ("OK", "OK_CROSSREF", "OK_URL") for r in rows)
    n_check = sum(r["status"].startswith("CHECK") for r in rows)
    n_miss = sum(r["status"] in ("NOT_IN_PUBMED", "NOT_INDEXED") for r in rows)
    print(f"\n{len(rows)} refs: verified {n_ok}, CHECK {n_check}, unverified {n_miss}")
    print("written audit/refs_pubmed.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
