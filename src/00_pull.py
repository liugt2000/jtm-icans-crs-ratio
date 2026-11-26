"""
Pull FAERS report counts from the openFDA aggregate API and persist a local cache.

Produces the complete set of margins needed for a report-level 2x2 table:
    n_ij  reports containing substance i AND event j
    n_i   reports containing substance i (any event)
    n_j   reports containing event j (any substance)
    N     all reports in the database

Everything is cached in cache/openfda_cache.json keyed by the canonical query string,
so re-runs are free and the frozen snapshot can be hashed for the Zenodo deposit.

Usage:  python src/00_pull.py [--tiers primary,severe,neg] [--sleep 0.15]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.fda.gov/drug/event.json"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "cache", "openfda_cache.json")
OUT = os.path.join(HERE, "out")

DRUG_FIELD = "patient.drug.activesubstance.activesubstancename"
REAC_FIELD = "patient.reaction.reactionmeddrapt"


def load_cache() -> dict:
    if os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"_meta": {"created": time.strftime("%Y-%m-%dT%H:%M:%S"), "endpoints": BASE}}


def save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE)


def build_query(drug: str | None, pt: str | None) -> str:
    parts = []
    if drug:
        parts.append(f'{DRUG_FIELD}.exact:"{drug}"')
    if pt:
        parts.append(f'{REAC_FIELD}.exact:"{pt}"')
    return "+AND+".join(parts)


def fetch_total(query: str, sleep: float = 0.15, tries: int = 6) -> int:
    """Return meta.results.total for a search expression, with backoff on 429/5xx."""
    url = f"{BASE}?limit=1"
    if query:
        url += "&search=" + urllib.parse.quote(query, safe="+:.\"")
    delay = 0.6
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "jtm-icans/0.1"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            time.sleep(sleep)
            return int(payload["meta"]["results"]["total"])
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:300]
            if exc.code == 429 or exc.code >= 500:
                time.sleep(delay)
                delay = min(delay * 2, 20)
                continue
            if exc.code == 404:
                # openFDA returns 404 when a search legitimately matches nothing
                time.sleep(sleep)
                return 0
            if exc.code == 400 and ".exact" in url:
                # exact keyword field unavailable for this field -> fall back
                url = url.replace(".exact", "")
                continue
            raise RuntimeError(f"HTTP {exc.code} for {url}\n{body}") from None
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay = min(delay * 2, 20)
    raise RuntimeError(f"giving up after {tries} tries: {url}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiers", default="primary,severe,neg",
                    help="comma separated event tiers to pull from config/events.csv")
    ap.add_argument("--sleep", type=float, default=0.15)
    ap.add_argument("--skip-comparators", action="store_true")
    args = ap.parse_args()

    tiers = {t.strip() for t in args.tiers.split(",") if t.strip()}

    with open(os.path.join(HERE, "config", "substances.csv"), encoding="utf-8-sig") as fh:
        substances = list(csv.DictReader(fh))
    with open(os.path.join(HERE, "config", "events.csv"), encoding="utf-8-sig") as fh:
        events = [r for r in csv.DictReader(fh) if r["tier"] in tiers]

    if args.skip_comparators:
        substances = [s for s in substances if s["group"] != "COMPARATOR"]

    cache = load_cache()
    todo: list[str] = [""] + [build_query(None, e["pt"]) for e in events] + \
                      [build_query(s["substance"], None) for s in substances] + \
                      [build_query(s["substance"], e["pt"]) for s in substances for e in events]

    pending = [q for q in todo if q not in cache]
    print(f"queries total={len(todo)} cached={len(todo) - len(pending)} pending={len(pending)}", flush=True)

    for i, q in enumerate(pending, 1):
        cache[q] = fetch_total(q, sleep=args.sleep)
        if i % 25 == 0 or i == len(pending):
            save_cache(cache)
            print(f"  [{i}/{len(pending)}] last={q[:70]} -> {cache[q]}", flush=True)
    save_cache(cache)

    os.makedirs(OUT, exist_ok=True)
    n_total = cache[""]
    with open(os.path.join(OUT, "counts_long.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["substance", "pt", "event_label", "tier", "n_ij", "n_i", "n_j", "N"])
        for s in substances:
            n_i = cache[build_query(s["substance"], None)]
            for e in events:
                w.writerow([s["substance"], e["pt"], e["event_label"], e["tier"],
                            cache[build_query(s["substance"], e["pt"])], n_i,
                            cache[build_query(None, e["pt"])], n_total])

    meta = {
        "N_total": n_total,
        "n_substances": len(substances),
        "n_events": len(events),
        "tiers": sorted(tiers),
        "cache_sha256": hashlib.sha256(open(CACHE, "rb").read()).hexdigest(),
        "pulled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "endpoint": BASE,
        "deduplicated": False,
        "role_filtered": False,
        "note": "Report-level counts from the openFDA aggregate API. NOT deduplicated by "
                "case version and NOT restricted to drugcharacterization=1; both are applied "
                "only in the raw-ASCII pipeline (src/10_parse_faers.py).",
    }
    with open(os.path.join(OUT, "pull_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
