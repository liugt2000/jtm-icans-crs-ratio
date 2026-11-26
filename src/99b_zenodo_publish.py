"""99b_zenodo_publish.py -- verify the draft, then (optionally) publish it.

Publishing is irreversible: the DOI becomes active and files can no longer be
changed. Without --publish this script only reads the draft back and prints it.

    python src/99b_zenodo_publish.py --record 24536543
    python src/99b_zenodo_publish.py --record 24536543 --publish
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PROFILE = Path("C:/Users/PC/.workbuddy/skills/playwright-browser-agent/profiles/zenodo")
BASE = "https://zenodo.org"


def entries(files) -> list[dict]:
    if isinstance(files, dict):
        return files.get("entries", [])
    if isinstance(files, list):
        return files
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE), headless=True,
            args=["--disable-dev-shm-usage"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"{BASE}/uploads/{a.record}", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        csrf = ""
        for c in ctx.cookies():
            if c.get("name") == "csrftoken":
                csrf = c.get("value", "")
                break
        H = {
            "X-CSRFToken": csrf,
            "Accept": "application/json",
            "Referer": f"{BASE}/uploads/{a.record}",
            "Origin": BASE,
        }
        api = ctx.request
        draft_url = f"{BASE}/api/records/{a.record}/draft"

        d = api.get(draft_url, headers=H).json()
        md = d.get("metadata", {})
        fs = entries(d.get("files"))
        report = {
            "record_id": a.record,
            "status": d.get("status"),
            "doi": d.get("doi") or d.get("pids", {}).get("doi", {}).get("identifier"),
            "title": md.get("title"),
            "creators": md.get("creators"),
            "license": md.get("license"),
            "version": md.get("version"),
            "publication_date": md.get("publication_date"),
            "resource_type": md.get("resource_type"),
            "keywords": md.get("keywords"),
            "description_chars": len(md.get("description") or ""),
            "files": [
                {"key": f.get("key"), "size": f.get("size"), "status": f.get("status")}
                for f in fs
            ],
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))

        problems = []
        if not report["doi"]:
            problems.append("no DOI reserved")
        if len(fs) != 1:
            problems.append(f"expected 1 file, found {len(fs)}")
        if report["description_chars"] < 1000:
            problems.append("description looks empty")
        if not md.get("creators"):
            problems.append("no creators")

        if problems:
            print("BLOCKED: " + "; ".join(problems))
            ctx.close()
            return 2

        if not a.publish:
            print("dry run -- nothing published")
            ctx.close()
            return 0

        r = api.post(f"{draft_url}/actions/publish", headers=H, timeout=300_000)
        print(f"publish: {r.status}")
        print(r.text()[:500])

        (OUT / "zenodo_published.json").write_text(
            json.dumps({"status": r.status, "body": r.text()[:2000]}, indent=2),
            encoding="utf-8",
        )
        ctx.close()
        return 0 if r.ok else 3


if __name__ == "__main__":
    sys.exit(main())
