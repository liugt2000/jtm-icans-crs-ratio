"""Probe whether EudraVigilance public access has any machine-readable endpoint.

adrreports.eu is the public face of EudraVigilance. If it is a JSF/PrimeFaces form
app, the only route is a browser; if it exposes a JSON/XHR service, the same R
statistic can be computed from EV without human interaction. This script answers
that question empirically instead of assuming either way.
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HDRS = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}

CANDIDATES = [
    "https://www.adrreports.eu/en/index.html",
    "https://www.adrreports.eu/",
    "https://api.adrreports.eu/",
    "https://www.adrreports.eu/api/",
    "https://www.adrreports.eu/api/v1/substances",
    "https://www.adrreports.eu/en/search_subst.html",
    "https://www.adrreports.eu/en/rest/search",
    # WHO / other second systems, in case EV is closed
    "https://www.pmda.go.jp/safety/info-services/drugs/adr-info/suspected-adr/0003.html",
    "https://vigiaccess.org/",
]


def probe(url: str) -> dict:
    req = urllib.request.Request(url, headers=HDRS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as fh:
            raw = fh.read(200000)
            return {
                "url": url,
                "status": fh.status,
                "ctype": fh.headers.get("Content-Type", ""),
                "bytes": len(raw),
                "head": raw[:300].decode("utf-8", "replace").replace("\n", " "),
            }
    except urllib.error.HTTPError as exc:
        return {"url": url, "status": exc.code, "ctype": "", "bytes": 0,
                "head": f"HTTPError {exc.reason}"}
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "status": 0, "ctype": "", "bytes": 0,
                "head": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    out = []
    for u in CANDIDATES:
        r = probe(u)
        out.append(r)
        print(f'[{r["status"]:>4}] {r["bytes"]:>7}b {r["ctype"][:40]:<40} {u}')
        if r["status"] == 200:
            print(f'        {r["head"][:220]}')
    path = "out/ev_probe.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("written", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
