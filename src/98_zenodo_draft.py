"""Create (or reuse) a Zenodo draft upload and report the reserved DOI.

The DOI is assigned by Zenodo when the draft record is first saved, not when it is
published. This script therefore only needs to open a new upload, set the resource
type to Dataset, give it the deposit title, and save the draft. Nothing is uploaded
and nothing is published.

Usage:
    python src/98_zenodo_draft.py            # headless
    python src/98_zenodo_draft.py --headed   # watch it happen

Writes out/zenodo_draft.json and prints the DOI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PROFILE = Path(
    "C:/Users/PC/.workbuddy/skills/playwright-browser-agent/profiles/zenodo"
)

TITLE = (
    "The ICANS/CRS ratio tracks costimulation within CD19 and does not hold in "
    "BCMA: code, frozen inputs and derived results"
)
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")


def log(msg: str) -> None:
    print(f"[zenodo] {msg}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--title", default=TITLE)
    ap.add_argument("--record", default=None, help="existing draft id to resume")
    ap.add_argument("--timeout", type=int, default=120_000)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    start_url = (
        f"https://zenodo.org/uploads/{args.record}"
        if args.record
        else "https://zenodo.org/uploads/new"
    )

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=not args.headed,
            args=[
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_timeout(args.timeout)

        log(f"opening {start_url}")
        page.goto(start_url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        for sel in ('button:has-text("Accept all cookies")', "text=Accept all cookies"):
            try:
                if page.locator(sel).count():
                    page.locator(sel).first.click()
                    page.wait_for_timeout(500)
                    break
            except PWTimeout:
                pass

        if "login" in page.url or page.locator('input[name="email"]').count():
            log("NOT LOGGED IN -- aborting")
            ctx.close()
            return 3

        if not args.record:
            # 1. resource type = Dataset (Semantic UI dropdown, not a <select>)
            log("selecting resource type = Dataset")
            page.click('div[name="metadata.resource_type"]')
            page.wait_for_timeout(600)
            page.click(
                'div[name="metadata.resource_type"] .menu .item:has-text("Dataset")'
            )
            page.wait_for_timeout(600)

        # 2. reserve a DOI from Zenodo.  The inputs are visually hidden inside
        # Semantic UI checkboxes, so click the label, then verify the state.
        log("DOI mode -> No, I need one (Zenodo reserves)")
        page.click('div.ui.radio.checkbox:has(input[value="managed"]) label')
        page.wait_for_timeout(600)
        state = page.evaluate(
            "() => [...document.querySelectorAll('input[name=radioGroup]')]"
            ".map(e => [e.value, e.checked])"
        )
        log(f"radio state = {state}")
        if not any(v == "managed" and c for v, c in state):
            log("could not switch DOI mode -- aborting before save")
            page.screenshot(path=str(OUT / "zenodo_doi_mode_failed.png"), full_page=True)
            ctx.close()
            return 6

        # 3. title is the only field required to save a draft
        title_input = page.locator('input[name="metadata.title"]')
        if not (title_input.input_value() or "").strip():
            log("filling title")
            page.fill('input[name="metadata.title"]', args.title)
            page.wait_for_timeout(400)
        else:
            log("title already set")

        # 4. save draft -- this is the moment the DOI is minted
        log("clicking Save draft")
        page.click('button:has-text("Save draft")')
        page.wait_for_timeout(7000)

        url = page.url
        record_id = None
        m = re.search(r"/uploads/(\d+)", url)
        if m:
            record_id = m.group(1)

        if not record_id:
            txt = page.inner_text("body")
            if "error" in txt.lower() and "saved" not in txt.lower():
                log("save appears to have failed")
                page.screenshot(path=str(OUT / "zenodo_save_failed.png"), full_page=True)
                ctx.close()
                return 4
            page.wait_for_timeout(4000)
            m2 = re.search(r"uploads/([0-9a-f-]{8,})", page.url)
            record_id = m2.group(1) if m2 else None

        def read_pids() -> dict:
            return page.evaluate(
                "() => { const el = document.querySelector("
                "'input[name=\"deposits-record\"]');"
                " return el ? JSON.parse(el.value).pids : {}; }"
            )

        def scan_for_doi() -> str | None:
            for probe in (
                "() => document.body.innerText",
                "() => document.documentElement.innerHTML",
            ):
                txt = page.evaluate(probe) or ""
                hit = DOI_RE.search(txt)
                if hit:
                    return hit.group(0)
            return None

        doi = scan_for_doi()
        pids = read_pids()
        log(f"pids after save = {json.dumps(pids)}")

        if not doi and not pids:
            # the DOI mode may only be committed on a second save
            log("no DOI yet -- saving once more")
            try:
                page.click('button:has-text("Save draft")')
                page.wait_for_timeout(6000)
            except PWTimeout:
                log("second save not clickable")
            pids = read_pids()
            log(f"pids after second save = {json.dumps(pids)}")
            doi = scan_for_doi()

        for _ in range(12):
            if doi:
                break
            page.wait_for_timeout(1500)
            doi = scan_for_doi()

        if not doi and pids:
            got = pids.get("doi") or {}
            if isinstance(got, dict):
                doi = got.get("identifier")

        page.screenshot(path=str(OUT / "zenodo_draft.png"), full_page=False)

        info = {
            "doi": doi,
            "record_id": record_id,
            "url": page.url,
            "title": args.title,
            "state": "draft (unpublished)",
        }
        (OUT / "zenodo_draft.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        log(f"url    = {page.url}")
        log(f"record = {record_id}")
        log(f"doi    = {doi}")

        if not doi:
            page.screenshot(path=str(OUT / "zenodo_no_doi.png"), full_page=True)
            ctx.close()
            return 5

        print(json.dumps(info, ensure_ascii=False))
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
