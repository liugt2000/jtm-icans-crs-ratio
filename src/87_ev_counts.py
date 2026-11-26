"""Pull EudraVigilance PT-level case counts per substance.

Why a browser and not HTTP
--------------------------
The public EV front end (adrreports.eu) does not serve numbers itself: every substance
lands on the Oracle BI portal at dap.ema.europa.eu, which answers with a
`<title>Signing in...</title>` shell whose only content is
`window.onload=function(){onLoggingInPageLoad('saw.dll?PortalPages',{...caj_token...})}`.
Plain HTTP can complete that handshake (POST the token back), but the resulting dashboard
then fills itself in through further XHR round trips, and the reaction-group /
reaction prompts are JS listboxes with no server-side equivalent that we could address
by URL. So the page has to be executed. We drive headless Chromium directly.

How the number is read
----------------------
Selecting a reaction group and then a reaction refreshes three independent charts
(Age Group & Sex, Reporter Group, Outcome) that all describe the *same* filtered case
set. Each chart carries its raw values inline as
`obips.ViewModelBase.getViewInstanceCache(...).BodyDef=new obips.BodyDefinition(...)`.
The three charts refresh asynchronously, so an immediate read can mix a fresh chart with
a stale one. We therefore poll until all three sums agree, and treat agreement as both the
value and the check: a mismatched read is never recorded. Cases with an empty cell
(`"r":""`) are counted as zero.

Output: out/ev_counts.jsonl (one record per substance x phenotype, append-only, resumable)
        out/ev_counts.json  (assembled)
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
JSONL = OUT / "ev_counts.jsonl"
CHROME = r"C:\Users\PC\AppData\Local\ms-playwright\chromium-1254\chrome-win64\chrome.exe"

BASE = ("https://dap.ema.europa.eu/analytics/saw.dll?PortalPages"
        "&PortalPath=%2Fshared%2FPHV%20DAP%2F_portal%2FDAP&Action=Navigate"
        "&P0=1&P1=eq&P2=%22Line%20Listing%20Objects%22.%22Substance%20High%20Level%20Code%22"
        "&P3=1+{code}")
PAGE_PT = BASE + "&Page=Number%20of%20Individual%20Cases%20for%20a%20selected%20Reaction"

# label, EV substance name, EMA high-level code, class assigned in the manuscript
SUBSTANCES = [
    ("tisa",  "TISAGENLECLEUCEL",           "4945331",  "4-1BB"),
    ("liso",  "LISOCABTAGENE MARALEUCEL",   "29137600", "4-1BB"),
    ("obe",   "OBECABTAGENE AUTOLEUCEL",    "36822465", "4-1BB"),
    ("axi",   "AXICABTAGENE CILOLEUCEL",    "23802665", "CD28"),
    ("brexu", "BREXUCABTAGENE AUTOLEUCEL",  "36765481", "CD28"),
    ("cilta", "CILTACABTAGENE AUTOLEUCEL",  "36788089", "4-1BB"),
    ("ide",   "IDECABTAGENE VICLEUCEL",     "35379866", "4-1BB"),
    ("glofi", "GLOFITAMAB",                 "34046514", "CD20xCD3"),
    ("blina", "BLINATUMOMAB",               "132079",   "CD19xCD3"),
    ("tecli", "TECLISTAMAB",                "38817180", "BCMAxCD3"),
    ("talq",  "TALQUETAMAB",                "39540174", "GPRC5DxCD3"),
    ("elran", "ELRANATAMAB",                "40216607", "BCMAxCD3"),
    ("epcor", "EPCORITAMAB",                "39540164", "CD20xCD3"),
    # tarlatamab has no entry in the adrreports.eu substance index (checked 2026-11-21,
    # letter t), so EV cannot be queried for it; it is the one product of the fourteen
    # that the external replication cannot cover.
]

TARGETS = [
    ("icans",     "Nervous system disorders", "Immune effector cell-associated neurotoxicity syndrome"),
    ("crs",       "Immune system disorders",  "Cytokine release syndrome"),
    ("neurotox",  "Nervous system disorders", "Neurotoxicity"),
]

SETTLE = 60          # seconds to wait for the three charts to agree
BODY_RE = re.compile(r"BodyDef=new obips\.BodyDefinition\((.*?)\);", re.S)
ROW_RE = re.compile(r'"r":"([\d,]*)"')


def chart_sums(html: str) -> list[tuple[int, int]]:
    """(number of cells, sum of values) for every chart on the page."""
    out = []
    for blk in BODY_RE.findall(html):
        vals = [int(v.replace(",", "")) if v.replace(",", "").isdigit() else 0
                for v in ROW_RE.findall(blk)]
        out.append((len(vals), sum(vals)))
    return out


def converged(html: str) -> tuple[int | None, list[tuple[int, int]]]:
    s = chart_sums(html)
    totals = {t for n, t in s if n > 1}
    if len(s) >= 3 and len(totals) == 1:
        return totals.pop(), s
    return None, s


def open_group(pg, soc: str) -> None:
    pg.locator("input.promptTextField").first.click()
    pg.wait_for_timeout(1200)
    pg.get_by_text(soc, exact=True).first.click()
    pg.wait_for_timeout(2500)


def wait_pt(pg, pt: str, timeout_s: int = 60) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        if pg.get_by_text(pt, exact=True).count() > 0:
            return True
        pg.wait_for_timeout(500)
    return False


def read_total(pg) -> int | None:
    """'The number of individual cases identified in EudraVigilance for X is 3,344'."""
    txt = pg.inner_text("body")
    m = re.search(r"identified in EudraVigilance for\s+.*?\s+is\s+([\d,]+)", txt, re.S)
    return int(m.group(1).replace(",", "")) if m else None


def selected_option(pg) -> str | None:
    """Text of the highlighted member of the reaction listbox, if the class exposes it."""
    try:
        return pg.evaluate("""() => {
            const opts = [...document.querySelectorAll('div.listBoxPanelOptionBasic')];
            for (const o of opts) {
                const a = (o.className||'') + ' ' + ((o.firstElementChild&&o.firstElementChild.className)||'');
                if (/highlight/i.test(a)) return o.innerText.trim();
            }
            return null;
        }""")
    except Exception:
        return None


def done_keys() -> set[str]:
    keys = set()
    if JSONL.exists():
        for line in JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    if r.get("status") == "ok" and r.get("n") is not None:
                        keys.add(f"{r['substance']}|{r['phenotype']}")
                except Exception:
                    pass
    return keys


def main() -> int:
    OUT.mkdir(exist_ok=True)
    have = done_keys()
    print(f"already done: {len(have)} records", flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, headless=True,
                                     args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1500, "height": 1400})

        for label, name, code, klass in SUBSTANCES:
            todo = [t for t in TARGETS if f"{label}|{t[0]}" not in have]
            if not todo:
                print(f"[{label}] complete, skip", flush=True)
                continue

            # ---- total ICSRs for the substance -------------------------------
            total = None
            try:
                page.goto(BASE.format(code=code), timeout=120000, wait_until="load")
                page.wait_for_selector("text=identified in EudraVigilance", timeout=90000)
                page.wait_for_timeout(1500)
                total = read_total(page)
            except Exception as exc:
                print(f"[{label}] total failed: {type(exc).__name__}", flush=True)
            print(f"[{label}] {name}: total={total}", flush=True)

            # ---- PT page ------------------------------------------------------
            try:
                page.goto(PAGE_PT.format(code=code), timeout=120000, wait_until="load")
                page.wait_for_selector("text=Choose a Reaction Group", timeout=90000)
                page.wait_for_timeout(2500)
            except Exception as exc:
                print(f"[{label}] PT page failed: {type(exc).__name__}", flush=True)
                continue

            current_soc = None
            for tag, soc, pt in todo:
                rec = {"substance": label, "name": name, "code": code, "class": klass,
                       "phenotype": tag, "soc": soc, "pt": pt, "total_icsr": total,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
                try:
                    if current_soc != soc:
                        open_group(page, soc)
                        current_soc = soc
                    if not wait_pt(page, pt):
                        rec.update(n=None, status="pt_missing")
                        print(f"[{label}/{tag}] PT not listed", flush=True)
                    else:
                        page.get_by_text(pt, exact=True).first.click()
                        n, charts, sel = None, [], None
                        end = time.time() + SETTLE
                        while time.time() < end:
                            page.wait_for_timeout(2000)
                            n, charts = converged(page.content())
                            if n is not None:
                                break
                        sel = selected_option(page)
                        if n is None:
                            rec.update(n=None, status="no_convergence", charts=charts)
                            print(f"[{label}/{tag}] no convergence {charts}", flush=True)
                        else:
                            rec.update(n=n, status="ok", charts=charts, selected=sel)
                            print(f"[{label}/{tag}] n={n}  charts={charts}  sel={sel}", flush=True)
                except Exception as exc:
                    rec.update(n=None, status=f"error:{type(exc).__name__}")
                    print(f"[{label}/{tag}] ERROR {type(exc).__name__} {exc}"[:200], flush=True)

                with JSONL.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

        browser.close()

    # assemble
    recs = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    latest, failed = {}, {}
    for r in recs:
        k = f"{r['substance']}|{r['phenotype']}"
        if r.get("status") == "ok" and r.get("n") is not None:
            latest[k] = r
        else:
            failed[k] = r
    for k, v in failed.items():          # keep the failure only where no success exists
        latest.setdefault(k, v)
    rows = list(latest.values())
    (OUT / "ev_counts.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nassembled {len(rows)} records, {ok} ok -> out/ev_counts.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
