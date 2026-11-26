"""Test whether the EMA DAP portal will actually serve a report body over plain GET.

The dap.ema.europa.eu links are Oracle BI (saw.dll) portal navigations. Oracle BI can
answer either with the rendered dashboard or with a shell that then fetches its content
through a second call, and it usually wants a session cookie. This script finds out
which one it is before any parsing code is written around it.
"""
from __future__ import annotations

import http.cookiejar
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

CODE = "4945331"  # tisagenlecleucel
URL = ("https://dap.ema.europa.eu/analyticsSOAP/saw.dll?PortalPages"
       "&PortalPath=%2Fshared%2FPHV%20DAP%2F_portal%2FDAP"
       "&Action=Navigate&P0=1&P1=eq&P2=%22Line%20Listing%20Objects%22."
       "%22Substance%20High%20Level%20Code%22&P3=1+" + CODE)

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [("User-Agent", UA), ("Accept", "text/html,*/*"),
                     ("Accept-Language", "en-US,en;q=0.9")]

print("GET", URL[:110], "...")
try:
    with opener.open(URL, timeout=60) as fh:
        body = fh.read().decode("utf-8", "replace")
        print("status", fh.status, "bytes", len(body))
        print("final url", fh.geturl()[:140])
except Exception as exc:  # noqa: BLE001
    print("FAILED", type(exc).__name__, exc)
    raise SystemExit(1)

open("out/ev_dap_probe.html", "w", encoding="utf-8").write(body)

print("\ncookies:", [(c.name, c.domain) for c in jar])
print("title:", re.findall(r"<title>(.*?)</title>", body, re.S)[:1])

text = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", "\n", text)
lines = [l.strip() for l in text.split("\n") if l.strip()]
print("\nvisible lines:", len(lines))
for l in lines[:45]:
    print("  |", l[:100])

print("\n--- markers ---")
for pat in ("Cytokine", "neurotox", "Immune effector", "Reaction", "SOC",
            "saw.dll", "csv", "Export", "session", "Login", "password",
            "No Results", "error"):
    print(f"  {pat:<18} {len(re.findall(pat, body, re.I)):>4}")
