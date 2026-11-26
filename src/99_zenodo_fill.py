"""99_zenodo_fill.py -- put the deposit zip and the metadata into the Zenodo draft.

The browser session is already authenticated, so this reuses it: the same cookies
authorise the JSON API, and the csrftoken cookie authorises the unsafe methods.
Nothing here publishes; the record stays a draft.

    python src/99_zenodo_fill.py --record 24536543
    python src/99_zenodo_fill.py --record 24536543 --creator "Family, Given"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DEP = ROOT / "deposit"
PROFILE = Path("C:/Users/PC/.workbuddy/skills/playwright-browser-agent/profiles/zenodo")
BASE = "https://zenodo.org"


def log(m: str) -> None:
    print(f"[fill] {m}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--zip", default=None, help="defaults to the newest deposit zip")
    ap.add_argument("--creator", action="append", default=None,
                    help='repeatable, "Family, Given"')
    ap.add_argument("--affiliation", default=None)
    ap.add_argument("--metadata-only", action="store_true",
                    help="skip file handling, just write metadata")
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()

    zips = sorted(ROOT.glob("deposit_*.zip"), key=lambda p: p.stat().st_mtime)
    zpath = Path(a.zip) if a.zip else (zips[-1] if zips else None)
    if not zpath or not zpath.exists():
        log("no zip found")
        return 2
    log(f"zip = {zpath.name} ({zpath.stat().st_size/1e6:.1f} MB)")

    meta_src = json.loads((DEP / ".zenodo.json").read_text(encoding="utf-8"))
    creators = []
    for c in a.creator or ["liugt2000"]:
        if "," in c:
            family, given = (x.strip() for x in c.split(",", 1))
        else:
            family, given = c.strip(), ""
        person = {"type": "personal", "family_name": family}
        if given:
            person["given_name"] = given
        item = {"person_or_org": person}
        if a.affiliation:
            item["affiliations"] = [{"name": a.affiliation}]
        creators.append(item)

    metadata = {
        "title": meta_src["title"],
        "publication_date": meta_src["publication_date"],
        "description": meta_src["description"],
        "resource_type": {"id": "dataset"},
        "creators": creators,
        # This Zenodo build accepts rights/languages/subjects and maps them onto
        # license/language/keywords; sending the latter directly is silently dropped.
        "rights": [{"id": meta_src.get("license", "cc-by-4.0")}],
        "languages": [{"id": "eng"}],
        "subjects": [{"subject": k} for k in meta_src.get("keywords", [])],
        "version": meta_src.get("version", "1.0.0"),
        "publisher": "Zenodo",
    }

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE), headless=not a.headed,
            args=["--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"{BASE}/uploads/{a.record}", wait_until="domcontentloaded")
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
            "Referer": f"{BASE}/uploads/{a.record}",
            "Origin": BASE,
        }

        draft = f"{BASE}/api/records/{a.record}/draft"

        if a.metadata_only:
            r = api.put(draft, data=json.dumps({"metadata": metadata}),
                        headers={**H, "Content-Type": "application/json"},
                        timeout=120_000)
            print(f"[fill] metadata: {r.status}")
            md = (r.json() or {}).get("metadata", {}) if r.ok else {}
            print(json.dumps({k: md.get(k) for k in
                              ("license", "language", "keywords", "creators", "version")},
                             ensure_ascii=False))
            if not r.ok:
                print(r.text()[:600])
            ctx.close()
            return 0 if r.ok else 6

        # 0. clear any previous file so a re-run does not stack duplicates
        cur = api.get(f"{draft}/files", headers=H)
        if cur.ok:
            for e in cur.json().get("entries", []):
                key = e.get("key")
                if key:
                    api.delete(f"{draft}/files/{key}", headers=H)
                    log(f"removed old file {key}")

        # 1. init -> upload -> commit
        r = api.post(f"{draft}/files", data=json.dumps([{"key": zpath.name}]), timeout=120_000,
                     headers={**H, "Content-Type": "application/json"})
        log(f"init file: {r.status}")
        if not r.ok:
            log(r.text()[:400])
            ctx.close()
            return 3

        payload = zpath.read_bytes()
        r = api.put(f"{draft}/files/{zpath.name}/content", data=payload, timeout=900_000,
                    headers={**H, "Content-Type": "application/octet-stream"})
        log(f"upload content: {r.status} ({len(payload)/1e6:.1f} MB)")
        if not r.ok:
            log(r.text()[:400])
            ctx.close()
            return 4

        r = api.post(f"{draft}/files/{zpath.name}/commit", headers=H, timeout=300_000)
        log(f"commit: {r.status}")
        if not r.ok:
            log(r.text()[:400])
            ctx.close()
            return 5

        # 2. metadata
        r = api.put(draft, data=json.dumps({"metadata": metadata}),
                    headers={**H, "Content-Type": "application/json"})
        log(f"metadata: {r.status}")
        if not r.ok:
            log(r.text()[:600])
            ctx.close()
            return 6

        # 3. read back what the server now holds
        final = api.get(draft, headers=H).json()
        info = {
            "record_id": a.record,
            "doi": final.get("pids", {}).get("doi", {}).get("identifier")
                   or final.get("doi"),
            "title": final.get("metadata", {}).get("title"),
            "creators": final.get("metadata", {}).get("creators"),
            "license": final.get("metadata", {}).get("license"),
            "files": [f.get("key") for f in final.get("files", {}).get("entries", [])],
            "file_bytes": [f.get("size") for f in final.get("files", {}).get("entries", [])],
            "status": final.get("status"),
            "url": f"{BASE}/uploads/{a.record}",
        }
        (OUT / "zenodo_filled.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(info, indent=2, ensure_ascii=False))
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
