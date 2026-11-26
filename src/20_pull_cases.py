"""
Pull case-level FAERS reports for the two hallmark phenotypes.

Why this exists
---------------
The aggregate `/drug/event.json?limit=1` endpoint returns only margins. It cannot
(a) remove duplicate follow-ups of the same case (`safetyreportid` + `safetyreportversion`),
(b) restrict exposure to primary-suspect drugs (`drugcharacterization == 1`), or
(c) describe co-reporting structure.

All three are mandatory, so the full records of every report carrying either phenotype
PT are downloaded here and reduced to a compact JSONL holding only the fields the
analysis consumes (plus every reaction PT, for co-reporting).

The endpoint accepts at most 500 records per request, so pages are fetched by several
workers over disjoint skip ranges and merged afterwards.

Output: data/cases_icans_crs.jsonl

Usage: python src/20_pull_cases.py [--limit 500] [--workers 3]
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.fda.gov/drug/event.json"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "cases_icans_crs.jsonl")

PHENOTYPES = [
    "Immune effector cell-associated neurotoxicity syndrome",
    "Cytokine release syndrome",
]


def get(url: str, tries: int = 10) -> dict:
    delay = 1.5
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "jtm-icans/0.3"})
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 1.7, 45)
                continue
            if exc.code == 404:
                return {"results": [], "meta": {"results": {"total": 0}}}
            raise RuntimeError(f"HTTP {exc.code} :: {url}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(delay)
            delay = min(delay * 1.7, 45)
    raise RuntimeError(f"giving up on {url}")


def norm(name: str) -> str:
    import re
    return re.sub(r"-[A-Z]{4}$", "", (name or "").strip().upper())


def reduce_record(rec: dict) -> dict:
    pat = rec.get("patient") or {}
    drugs = []
    for d in pat.get("drug") or []:
        names = []
        act = d.get("activesubstance") or {}
        if act.get("activesubstancename"):
            names.append(act["activesubstancename"])
        ofd = d.get("openfda") or {}
        for key in ("substance_name", "generic_name", "brand_name"):
            for v in ofd.get(key) or []:
                names.append(v)
        if d.get("medicinalproduct"):
            names.append(d["medicinalproduct"])
        seen, keep = set(), []
        for n in names:
            k = norm(n)
            if k and k not in seen:
                seen.add(k)
                keep.append(k)
        drugs.append({"names": keep,
                      "char": d.get("drugcharacterization"),
                      "indication": (d.get("drugindication") or "")[:80]})
    reacts = [(r.get("reactionmeddrapt") or "").strip()
              for r in (pat.get("reaction") or [])]
    ps = rec.get("primarysource") or {}
    return {"sid": rec.get("safetyreportid"),
            "ver": rec.get("safetyreportversion"),
            "rdate": rec.get("receivedate"),
            "country": rec.get("occurcountry") or ps.get("reportercountry"),
            "qual": ps.get("qualification"),
            "serious": rec.get("serious"),
            "drugs": drugs,
            "reacts": [r for r in reacts if r]}


def worker(pt: str, limit: int, start_page: int, step: int, path: str,
           progress: dict, key: str) -> None:
    q = urllib.parse.quote(f'patient.reaction.reactionmeddrapt.exact:"{pt}"', safe='+:.')
    total = get(f"{BASE}?search={q}&limit=1")["meta"]["results"]["total"]
    progress[key] = {"total": total, "written": 0}
    with open(path, "w", encoding="utf-8") as fh:
        page = start_page
        while True:
            skip = page * limit
            if skip >= total:
                break
            url = f"{BASE}?search={q}&limit={limit}&skip={skip}"
            payload = get(url)
            batch = payload.get("results", [])
            if not batch:
                break
            for rec in batch:
                fh.write(json.dumps(reduce_record(rec), ensure_ascii=False) + "\n")
            fh.flush()
            progress[key]["written"] += len(batch)
            print(f"  [{pt[:28]}] page {page} skip={skip} "
                  f"written={progress[key]['written']}/{total}", flush=True)
            page += step
            time.sleep(0.4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)

    threads, progress = [], {}
    for i, pt in enumerate(PHENOTYPES):
        for w in range(args.workers):
            path = os.path.join(DATA, f"cases_part_{i}_{w}.jsonl")
            t = threading.Thread(target=worker,
                                 args=(pt, args.limit, w, args.workers, path,
                                       progress, f"{i}_{w}"))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()

    # merge, de-duplicating on (safetyreportid, version)
    seen, n = set(), 0
    with open(OUT, "w", encoding="utf-8") as out:
        for i in range(len(PHENOTYPES)):
            for w in range(args.workers):
                p = os.path.join(DATA, f"cases_part_{i}_{w}.jsonl")
                if not os.path.exists(p):
                    continue
                with open(p, encoding="utf-8") as fh:
                    for line in fh:
                        try:
                            o = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        k = (str(o.get("sid")), str(o.get("ver")))
                        if k in seen:
                            continue
                        seen.add(k)
                        out.write(line if line.endswith("\n") else line + "\n")
                        n += 1
    print(f"\nMERGED unique={n}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
