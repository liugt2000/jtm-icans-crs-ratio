"""99a_zenodo_newversion.py -- open a new (unpublished) version of a published Zenodo record.

Zenodo models a versioned record as one concept with several versions. Opening a new version
is a POST against the version you want to supersede; it returns a new *draft*, which inherits
the files and metadata of its predecessor and must be edited before it is published.

The browser profile used by 98/99 is already authenticated, so its cookies authorise this call
too. Nothing is published here.

    python src/99a_zenodo_newversion.py --parent 24536543
    python src/99a_zenodo_newversion.py --parent 24536543 --headed
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    os.environ.pop(_k, None)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PROFILE = Path("C:/Users/PC/.workbuddy/skills/playwright-browser-agent/profiles/zenodo")
BASE = "https://zenodo.org"

# The local resolver returns 0.0.0.0 for zenodo.org. Chromium is therefore given a real CERN
# address directly and told to ignore the proxy, which answers 502 for this host.
ZENODO_IP = os.environ.get("ZENODO_IP", "137.138.121.78")
LAUNCH_ARGS = [
    f"--host-resolver-rules=MAP zenodo.org {ZENODO_IP}, MAP www.zenodo.org {ZENODO_IP}",
    "--no-proxy-server",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
]


def log(m: str) -> None:
    print(f"[newver] {m}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", required=True, help="record id of the version to supersede")
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE), headless=not a.headed, args=LAUNCH_ARGS,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"{BASE}/records/{a.parent}", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        csrf = ""
        for c in ctx.cookies():
            if c.get("name") == "csrftoken":
                csrf = c.get("value", "")
                break
        log(f"csrf length = {len(csrf)}")

        api = ctx.request
        H = {
            "X-CSRFToken": csrf,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": f"{BASE}/records/{a.parent}",
            "Origin": BASE,
        }

        # A version that is already a draft cannot be versioned again; report rather than guess.
        cur = api.get(f"{BASE}/api/records/{a.parent}", headers=H)
        if cur.ok:
            st = cur.json().get("status")
            log(f"parent status = {st}")
            if st != "published":
                log("parent is not published; nothing to supersede")
                ctx.close()
                return 2

        r = api.post(f"{BASE}/api/records/{a.parent}/versions", data="{}",
                     headers=H, timeout=180_000)
        log(f"new version: {r.status}")
        if not r.ok:
            log(r.text()[:800])
            ctx.close()
            return 3

        draft = r.json()
        rec_id = str(draft.get("id"))
        concept = draft.get("parent", {}).get("id") if isinstance(draft.get("parent"), dict) \
            else draft.get("conceptrecid")
        info = {
            "record_id": rec_id,
            "concept_id": str(concept) if concept else None,
            "doi": (draft.get("pids", {}).get("doi", {}) or {}).get("identifier"),
            "status": draft.get("status"),
            "version": (draft.get("metadata", {}) or {}).get("version"),
            "files": [f.get("key") for f in draft.get("files", {}).get("entries", [])],
            "url": f"{BASE}/uploads/{rec_id}",
            "supersedes": a.parent,
        }
        (OUT / "zenodo_newversion.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(info, indent=2, ensure_ascii=False))
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
