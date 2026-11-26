"""Verify every DOI in references.md by resolving it back to a Crossref record.

This is the check that makes the reference list trustworthy: a DOI is accepted only if
resolving it returns a record whose title matches the cited title. Reading the list back
from the file means the check applies to what is actually in the manuscript, not to what
the resolver thought it wrote.
"""
from __future__ import annotations

import csv
import difflib
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
OUT = ROOT / "out"
CACHE = OUT / "refs_verify"
CACHE.mkdir(parents=True, exist_ok=True)
UA = "jtm-icans-manuscript/1.0 (mailto:corresponding@example.org)"


def norm(s: str) -> str:
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def resolve(doi: str) -> dict | None:
    safe = doi.replace("/", "_")
    cache = CACHE / f"{safe}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as fh:
                data = json.load(fh)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {"error": "404"}
            time.sleep(1.5)
        except Exception:
            time.sleep(1.5)
    return None


def main() -> int:
    text = (MS / "references.md").read_text(encoding="utf-8")
    entries = re.split(r"\n(?=\d{1,2}\. )", text)
    rows, n_ok, n_bad, n_manual = [], 0, 0, 0
    for ch in entries:
        m = re.match(r"(\d{1,2})\.\s+(.*)", ch.strip(), re.S)
        if not m:
            continue
        num, body = int(m.group(1)), " ".join(
            ln.strip() for ln in m.group(2).split("\n") if ln.strip())
        if "[MANUAL" in body:
            n_manual += 1
            rows.append({"n": num, "doi": "", "title_sim": "", "status": "manual",
                         "note": "no confident Crossref match"})
            continue
        dm = re.search(r"doi:(\S+)", body)
        if not dm:
            rows.append({"n": num, "doi": "", "title_sim": "", "status": "no_doi",
                         "note": ""})
            continue
        doi = dm.group(1).rstrip(".")
        rec = resolve(doi)
        if rec is None:
            rows.append({"n": num, "doi": doi, "title_sim": "", "status": "unreachable",
                         "note": ""})
            n_bad += 1
            continue
        if "error" in rec:
            rows.append({"n": num, "doi": doi, "title_sim": "", "status": "404",
                         "note": ""})
            n_bad += 1
            continue

        got_title = (rec["message"].get("title") or [""])[0]
        got_journal = (rec["message"].get("container-title") or [""])[0]

        # Two independent conditions, because either alone is fooled: a truncated
        # citation title defeats a plain similarity ratio, and an exact title from a
        # different journal defeats title matching alone.
        n_entry, n_got = norm(body), norm(got_title)
        sm = difflib.SequenceMatcher(None, n_got, n_entry, autojunk=False)
        block = sm.find_longest_match(0, len(n_got), 0, len(n_entry))
        cover = block.size / max(1, len(n_got))
        jour_ok = norm(got_journal)[:22] in n_entry if got_journal else False

        # Author and year are checked too: a correct DOI attached to the wrong author
        # list still misattributes the work.
        auths = rec["message"].get("author") or []
        fam = (auths[0].get("family") if auths else "") or ""
        author_ok = (norm(fam) in n_entry) if fam else True
        yr_rec = ((rec["message"].get("issued") or {}).get("date-parts") or [[None]])[0][0]
        yr_entry = re.search(r"\.\s*(19|20)(\d{2})[;.]", body)
        year_ok = True if (yr_rec is None or not yr_entry) else \
            abs(int(yr_entry.group(1) + yr_entry.group(2)) - yr_rec) <= 1

        problems = []
        if cover < 0.65:
            problems.append("title")
        if not jour_ok:
            problems.append("journal")
        if not author_ok:
            problems.append("author")
        if not year_ok:
            problems.append("year")
        ok = not problems
        rows.append({"n": num, "doi": doi, "title_sim": f"{cover:.3f}",
                     "status": "ok" if ok else "MISMATCH:" + "+".join(problems),
                     "note": f"{fam} {yr_rec} | {got_journal[:26]} | {got_title[:52]}"})
        n_ok += ok
        n_bad += (not ok)

    with (OUT / "refs_verification.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "doi", "title_sim", "status", "note"])
        w.writeheader()
        w.writerows(rows)

    for r in rows:
        print(f"  {r['n']:2d}  {r['status']:<14} {str(r['title_sim']):>5}  {r['doi']:<42} {r['note'][:60]}")
    print(f"\nverified {n_ok}, problems {n_bad}, manual {n_manual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
