"""Build a full index of the EudraVigilance public substance tables.

adrreports.eu serves the substance index as static HTML at /tables/substance/<a-z|0-9>.html;
each row carries the EMA "Substance High Level Code" inside a dap.ema.europa.eu URL.
That code is the join key for every downstream EV query, so it is worth harvesting
once and caching.
"""
from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HDRS = {"User-Agent": UA, "Accept": "text/html,*/*"}
BASE = "https://www.adrreports.eu/tables/substance/{}.html"
LETTERS = list("abcdefghijklmnopqrstuvwxyz") + ["0-9"]

ROW = re.compile(
    r'<a href="(?P<url>[^"]+)"[^>]*>(?P<name>.*?)</a>(?P<tail>[^<]*)', re.S)
CODE = re.compile(r"P3=1\+(\d+)")


def fetch(url: str, tries: int = 3) -> str | None:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=30) as fh:
                return fh.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            time.sleep(1.5 * (i + 1))
        except Exception:  # noqa: BLE001
            time.sleep(1.5 * (i + 1))
    return None


def main() -> int:
    rows: list[dict] = []
    for letter in LETTERS:
        page = fetch(BASE.format(letter))
        if not page:
            print(f"  {letter:<4} -- none")
            continue
        n0 = len(rows)
        for m in ROW.finditer(page):
            name = html.unescape(re.sub(r"<[^>]+>", "", m.group("name"))).strip()
            code = CODE.search(m.group("url"))
            if not name or not code:
                continue
            # an asterisk marks a substance with a caveat on the EV page
            caveat = "*" in m.group("tail")
            rows.append({"substance": name, "code": code.group(1),
                         "letter": letter, "caveat": caveat,
                         "dap_url": m.group("url")})
        print(f"  {letter:<4} {len(rows) - n0:>4} rows")

    # de-duplicate on (substance, code); the index repeats some entries across letters
    seen, uniq = set(), []
    for r in rows:
        key = (r["substance"].upper(), r["code"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    with open("out/ev_substance_index.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(uniq[0].keys()))
        w.writeheader()
        w.writerows(uniq)
    print(f"\nindexed {len(uniq)} distinct substances -> out/ev_substance_index.csv")

    # Sanity: are our target substances in there?
    want = ["TISAGENLECLEUCEL", "AXICABTAGENE", "LISOCABTAGENE", "CILTACABTAGENE",
            "BREXUCABTAGENE", "IDECABTAGENE", "BLINATUMOMAB", "TECLISTAMAB",
            "TALQUETAMAB", "ELRANATAMAB", "EPCORITAMAB", "GLDFITAMAB",
            "MOSUNETUZUMAB", "TOCILIZUMAB"]
    found = {r["substance"].upper(): r["code"] for r in uniq}
    print()
    for w_ in want:
        hit = [k for k in found if k.startswith(w_)]
        print(f"  {w_:<18} -> {[(h, found[h]) for h in hit] or 'MISSING'}")

    with open("out/ev_index_probe.json", "w", encoding="utf-8") as fh:
        json.dump({"n_substances": len(uniq)}, fh)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
