"""
Page-wise, verifiable pull of the legacy *Neurotoxicity* preferred term.

The first attempt used three worker threads over disjoint page ranges and died when the
API began returning 500s: two threads were stuck in exponential backoff and the merge
step would have written a file that looked complete but was not. A truncated denominator
is the worst possible failure in a prevalence analysis, because nothing downstream can
notice it.

This version makes each page a file. A page that already exists and parses is never
re-fetched, so the pull is resumable; at the end every expected page index must be
present, and the merged record count must equal the API's own reported total. If either
check fails the script exits non-zero and says which pages are missing.

Outputs: data/legacy_pages/page_NNN.jsonl, data/cases_legacy_nt.jsonl
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
PAGES = os.path.join(DATA, "legacy_pages")
MERGED = os.path.join(DATA, "cases_legacy_nt.jsonl")

BASE = "https://api.fda.gov/drug/event.json"
PT = "Neurotoxicity"
LIMIT = 500
UA = {"User-Agent": "jtm-icans/0.3"}


def get(url: str, tries: int = 3, base_delay: float = 15.0) -> dict:
    delay = base_delay
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            if exc.code == 404:
                return {"results": [], "meta": {"results": {"total": 0}}}
            # 429 and 5xx are both transient here; back off hard because the endpoint
            # starts rejecting bursts once a few hundred pages have been requested.
            time.sleep(delay)
            delay = min(delay * 2.0, 90)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = type(exc).__name__
            time.sleep(delay)
            delay = min(delay * 2.0, 90)
    raise RuntimeError(f"giving up after {tries} tries ({last}) :: {url}")


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
        drugs.append({"names": keep, "char": d.get("drugcharacterization"),
                      "indication": (d.get("drugindication") or "")[:80]})
    reacts = [(r.get("reactionmeddrapt") or "").strip()
              for r in (pat.get("reaction") or [])]
    ps = rec.get("primarysource") or {}
    return {"sid": rec.get("safetyreportid"), "ver": rec.get("safetyreportversion"),
            "rdate": rec.get("receivedate"),
            "country": rec.get("occurcountry") or ps.get("reportercountry"),
            "qual": ps.get("qualification"), "serious": rec.get("serious"),
            "drugs": drugs, "reacts": [r for r in reacts if r]}


def main() -> int:
    os.makedirs(PAGES, exist_ok=True)
    q = urllib.parse.quote(f'patient.reaction.reactionmeddrapt.exact:"{PT}"',
                           safe="+:.@")
    total = get(f"{BASE}?search={q}&limit=1")["meta"]["results"]["total"]
    n_pages = (total + LIMIT - 1) // LIMIT
    print(f"total={total} pages={n_pages}", flush=True)

    missing = []
    for page in range(n_pages):
        path = os.path.join(PAGES, f"page_{page:03d}.jsonl")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        skip = page * LIMIT
        try:
            payload = get(f"{BASE}?search={q}&limit={LIMIT}&skip={skip}")
        except RuntimeError as exc:
            print(f"  page {page:>3} FAILED :: {exc}")
            missing.append(page)
            continue
        batch = payload.get("results", [])
        with open(path, "w", encoding="utf-8") as fh:
            for rec in batch:
                fh.write(json.dumps(reduce_record(rec), ensure_ascii=False) + "\n")
        print(f"  page {page:>3}/{n_pages - 1} skip={skip} n={len(batch)}", flush=True)
        time.sleep(2.5)

    if missing:
        print(f"\nINCOMPLETE: {len(missing)} pages missing -> {missing[:20]}")
        print("re-run this script; completed pages are skipped")
        return 2

    seen, n, n_dup = set(), 0, 0
    with open(MERGED, "w", encoding="utf-8") as out:
        for page in range(n_pages):
            path = os.path.join(PAGES, f"page_{page:03d}.jsonl")
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    k = (str(o.get("sid")), str(o.get("ver")))
                    if k in seen:
                        n_dup += 1
                        continue
                    seen.add(k)
                    out.write(line if line.endswith("\n") else line + "\n")
                    n += 1
    print(f"\nmerged unique={n}  exact-duplicate records={n_dup}  api total={total}")
    # The API returns one record per report *version*; a case that was followed up can
    # appear twice under the same safetyreportid with different versions. Those are the
    # only legitimate reason for merged < total, so the counts must close exactly.
    if n + n_dup != total:
        print("MISMATCH: merged + duplicates != API total -- do not analyse")
        return 3
    if n_dup > 0.01 * total:
        print(f"WARNING: {n_dup} duplicate records is more than 1% of the pull")
    print("OK ->", MERGED)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
