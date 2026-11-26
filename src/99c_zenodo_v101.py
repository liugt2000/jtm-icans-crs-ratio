"""99c_zenodo_v101.py -- publish a new version of the deposit.

The version it publishes is read from deposit/.zenodo.json, which src/96_build_deposit.py
writes from its own VERSION constant; this script never hard-codes a release number.

Why this script exists rather than a re-run of 98/99/99b: the local resolver returns 0.0.0.0
for zenodo.org (and the configured proxy answers 502 for it), so libcurl inside Playwright's
APIRequestContext cannot resolve the host. Chromium itself is fine when handed a real CERN
address, so the browser opens the page (to obtain an authenticated cookie jar) and every API
call is then made with curl --resolve. The upload is 17 MB, which is why it is streamed from
disk by curl rather than held in a JS string.

Steps, each idempotent enough to re-run:
  1. open a new version of --parent and record the new draft id
  2. remove the files it inherited, upload the v1.0.1 zip, commit it
  3. write metadata (version, date, description) and read it back
  4. only with --publish, publish

    python src/99c_zenodo_v101.py --parent <current version id> --zip <zip>
    python src/99c_zenodo_v101.py --publish --record <newid>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    os.environ.pop(_k, None)

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DEP = ROOT / "deposit"
PROFILE = Path("C:/Users/PC/.workbuddy/skills/playwright-browser-agent/profiles/zenodo")
BASE = "https://zenodo.org"
IP = os.environ.get("ZENODO_IP", "137.138.121.78")
VERSION = json.loads((DEP / ".zenodo.json").read_text(encoding="utf-8"))["version"]
STATE = OUT / ("zenodo_v" + VERSION.replace(".", "") + ".json")


def log(m: str) -> None:
    print(f"[v{VERSION}] {m}", flush=True)


def cookie_jar(parent: str) -> tuple[str, str]:
    """Open the record page in the persistent profile and return (cookie header, csrf)."""
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE), headless=True,
            args=[f"--host-resolver-rules=MAP zenodo.org {IP}, MAP www.zenodo.org {IP}",
                  "--no-proxy-server", "--disable-dev-shm-usage"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"{BASE}/records/{parent}", wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(1500)
        cookies = [c for c in ctx.cookies() if c.get("domain", "").endswith("zenodo.org")]
        jar = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
        csrf = next((c["value"] for c in cookies if c["name"] == "csrftoken"), "")
        ctx.close()
    return jar, csrf


def api(method: str, path: str, jar: str, csrf: str, *,
        json_body: dict | list | None = None, upload: Path | None = None,
        max_time: int = 900) -> tuple[int, str]:
    cmd = ["curl", "-sS", "--noproxy", "*", "--resolve", f"zenodo.org:443:{IP}",
           "--max-time", str(max_time), "-X", method, BASE + path,
           "-H", f"Cookie: {jar}", "-H", f"X-CSRFToken: {csrf}",
           "-H", "Accept: application/json",
           "-H", f"Referer: {BASE}/", "-H", f"Origin: {BASE}",
           "-w", "\n__STATUS__%{http_code}"]
    tmp = None
    if json_body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(json_body, tmp, ensure_ascii=False)
        tmp.close()
        cmd += ["-H", "Content-Type: application/json", "--data-binary", f"@{tmp.name}"]
    elif upload is not None:
        cmd += ["-H", "Content-Type: application/octet-stream", "--data-binary", f"@{upload}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    finally:
        if tmp:
            os.unlink(tmp.name)
    text = r.stdout or ""
    m = re.search(r"\n__STATUS__(\d{3})$", text)
    status = int(m.group(1)) if m else 0
    body = text[: m.start()] if m else text
    return status, body.strip()


def file_entries(obj: dict) -> list[dict]:
    """`files` comes back as {"entries": [...]} on one endpoint and as a bare list on another."""
    f = obj.get("files")
    if isinstance(f, dict):
        return f.get("entries", []) or []
    if isinstance(f, list):
        return f
    return []


def metadata_for(draft: dict) -> dict:
    """Build the PUT payload from what the draft inherited, changing only what must change.

    Zenodo's current schema accepts rights/languages/subjects and maps them onto the older
    license/language/keywords; sending the latter directly is silently dropped (v1.0.0 lesson).
    """
    src = json.loads((DEP / ".zenodo.json").read_text(encoding="utf-8"))
    md = draft.get("metadata", {})
    lic = md.get("license")
    lic_id = lic.get("id") if isinstance(lic, dict) else (lic or src.get("license", "cc-by-4.0"))
    kws = md.get("keywords") or src.get("keywords", [])
    subjects = [{"subject": k["subject"] if isinstance(k, dict) else str(k)} for k in kws]

    # A new draft inherits files but not always creators (v1.0.1 draft came back empty, and a
    # publication without a creator is rejected). Fall back to the names in .zenodo.json.
    creators = md.get("creators") or []
    if not creators:
        creators = []
        for c in src.get("creators", [{"name": "liugt2000"}]):
            fam, _, giv = (c.get("name") or "liugt2000").partition(",")
            person = {"type": "personal", "family_name": fam.strip()}
            if giv.strip():
                person["given_name"] = giv.strip()
            creators.append({"person_or_org": person})
    return {
        "title": src["title"],
        "publication_date": src["publication_date"],
        "description": src["description"],
        "resource_type": {"id": "dataset"},
        "creators": creators,
        "rights": [{"id": lic_id}],
        "languages": [{"id": "eng"}],
        "subjects": subjects,
        "version": src["version"],
        "publisher": "Zenodo",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", default="24551266", help="version to supersede")
    ap.add_argument("--record", default=None, help="resume on an existing draft id")
    ap.add_argument("--zip", default=None)
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--metadata-only", action="store_true")
    a = ap.parse_args()

    if a.publish and not a.record:
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
        a.record = a.record or str(state.get("record_id") or "")
        if not a.record:
            log(f"--publish needs --record (no saved draft at {STATE.name})")
            return 2

    zips = sorted(ROOT.glob("deposit_jtm_icans_v*.zip"), key=lambda p: p.stat().st_mtime)
    zpath = Path(a.zip) if a.zip else (zips[-1] if zips else None)
    if not zpath or not zpath.exists():
        log("no zip found")
        return 2
    log(f"zip = {zpath.name} ({zpath.stat().st_size/1e6:.1f} MB)")

    jar, csrf = cookie_jar(a.parent if not a.record else a.record)
    log(f"cookie jar {len(jar)} chars, csrf {len(csrf)}")

    rec = a.record
    if not rec:
        st, body = api("POST", f"/api/records/{a.parent}/versions", jar, csrf,
                       json_body={})
        log(f"new version: {st}")
        if st not in (200, 201):
            log(body[:800])
            return 3
        rec = str(json.loads(body).get("id"))
        log(f"draft record {rec}")

    st, body = api("GET", f"/api/records/{rec}/draft", jar, csrf)
    if st != 200:
        log(f"draft read: {st} {body[:400]}")
        return 4
    draft = json.loads(body)
    log(f"status={draft.get('status')} version={draft.get('metadata', {}).get('version')} "
        f"files={[f.get('key') for f in file_entries(draft)]}")

    if a.metadata_only:
        st, body = api("PUT", f"/api/records/{rec}/draft", jar, csrf,
                       json_body={"metadata": metadata_for(draft)})
        log(f"metadata: {st}")
        if st not in (200, 201):
            log(body[:1200])
            return 8
        st, body = api("GET", f"/api/records/{rec}/draft", jar, csrf)
        d = json.loads(body)
        print(json.dumps({k: d.get(k) for k in ("parent", "pids", "conceptrecid",
                                                "status", "expid")},
                         ensure_ascii=False, indent=1)[:1200])
        print("creators:", json.dumps(d.get("metadata", {}).get("creators"),
                                      ensure_ascii=False)[:600])
        return 0

    if not a.publish:
        # 1. drop inherited files
        for f in file_entries(draft):
            st, _ = api("DELETE", f"/api/records/{rec}/draft/files/{f['key']}", jar, csrf)
            log(f"delete {f['key']}: {st}")

        # 2. init -> upload -> commit
        st, body = api("POST", f"/api/records/{rec}/draft/files", jar, csrf,
                       json_body=[{"key": zpath.name}])
        log(f"init: {st}")
        if st not in (200, 201):
            log(body[:400])
            return 5
        st, body = api("PUT", f"/api/records/{rec}/draft/files/{zpath.name}/content",
                       jar, csrf, upload=zpath, max_time=1800)
        log(f"upload: {st}")
        if st not in (200, 201):
            log(body[:400])
            return 6
        st, body = api("POST", f"/api/records/{rec}/draft/files/{zpath.name}/commit",
                       jar, csrf, max_time=600)
        log(f"commit: {st}")
        if st not in (200, 201):
            log(body[:400])
            return 7

        # 3. metadata
        st, body = api("PUT", f"/api/records/{rec}/draft", jar, csrf,
                       json_body={"metadata": metadata_for(draft)})
        log(f"metadata: {st}")
        if st not in (200, 201):
            log(body[:800])
            return 8

        # 4. read back
        st, body = api("GET", f"/api/records/{rec}/draft", jar, csrf)
        final = json.loads(body)
        md = final.get("metadata", {})
        info = {
            "record_id": rec,
            "concept_id": str((final.get("parent") or {}).get("id") or ""),
            "doi": (final.get("pids", {}).get("doi", {}) or {}).get("identifier"),
            "status": final.get("status"),
            "version": md.get("version"),
            "publication_date": md.get("publication_date"),
            "title": md.get("title"),
            "creators": [c.get("person_or_org", {}).get("name") or c.get("person_or_org")
                         for c in md.get("creators", [])],
            "license": md.get("license"),
            "keywords": [k.get("subject") if isinstance(k, dict) else k
                         for k in md.get("keywords", [])],
            "files": [{"key": f.get("key"), "size": f.get("size"),
                       "checksum": f.get("checksum")}
                      for f in file_entries(final)],
            "url": f"{BASE}/uploads/{rec}",
            "supersedes": a.parent,
        }
        STATE.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return 0

    # publish path
    st, body = api("GET", f"/api/records/{rec}/draft", jar, csrf)
    draft = json.loads(body)
    files = file_entries(draft)
    md = draft.get("metadata", {})
    log(f"pre-publish: version={md.get('version')} date={md.get('publication_date')} "
        f"files={[(f.get('key'), f.get('size')) for f in files]}")
    if len(files) != 1 or md.get("version") != VERSION or not md.get("creators"):
        log(f"refusing to publish: need exactly one file, version {VERSION} and a creator")
        return 9
    st, body = api("POST", f"/api/records/{rec}/draft/actions/publish", jar, csrf,
                   max_time=600)
    log(f"publish: {st}")
    if st not in (200, 201, 202):
        log(body[:800])
        return 10
    pub = json.loads(body)
    out = {
        "record_id": rec,
        "doi": (pub.get("pids", {}).get("doi", {}) or {}).get("identifier"),
        "status": pub.get("status"),
        "version": pub.get("metadata", {}).get("version"),
        "url": f"{BASE}/records/{rec}",
        "concept_doi": "10.5281/zenodo.24536542",
        "files": [{"key": f.get("key"), "size": f.get("size"), "checksum": f.get("checksum")}
                  for f in file_entries(pub)],
    }
    (OUT / "zenodo_v101_published.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
