"""Inspect the EV front-end markup for a callable route.

Two questions have to be answered from the HTML itself:
  1. Is the report table rendered server-side from query parameters, or does it
     require a stateful form post (JSF ViewState / Liferay portlet)?
  2. Are the aggregate counts addressable by (substance, reaction) in a URL?
"""
from __future__ import annotations

import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HDRS = {"User-Agent": UA, "Accept": "text/html,*/*"}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as fh:
        return fh.read().decode("utf-8", "replace")


for u in ("https://www.adrreports.eu/en/index.html",
          "https://www.adrreports.eu/en/search_subst.html"):
    h = get(u)
    print("=" * 78)
    print(u, len(h))
    for pat, label in (
        (r"<form[^>]*>", "form"),
        (r"javax\.faces[^\"']*", "jsf"),
        (r"ViewState[^\"']{0,40}", "viewstate"),
        (r"p_p_id=[^\"'&]*", "liferay-portlet"),
        (r"action=\"[^\"]*\"", "action"),
        (r"(?:src|href)=\"([^\"]*\.(?:js|json))\"", "asset"),
        (r"https?://[a-z0-9.\-]*adrreports[^\"' <]*", "abs-url"),
    ):
        hits = re.findall(pat, h, re.I)
        uniq = sorted(set(hits))[:14]
        print(f"  {label:<16} {len(hits):>3}  {uniq}")

    # text of visible links, to see whether a substance page is a plain GET
    links = sorted(set(re.findall(r'href="([^"]+\.html[^"]*)"', h)))
    print("  .html links:", links[:16])
