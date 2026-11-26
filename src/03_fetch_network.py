"""
Freeze the signalling interactome used for the network-proximity models.

Source: OmniPath (omnipathdb.org), which harmonises IntAct, BioGRID, SIGNOR,
Reactome, SignaLink and others and — critically for this project — keeps the
per-record provenance (`sources`, `references`, `curation_effort`). That is what
allows edges to be filtered by evidence type instead of being collapsed into a
single STRING-like confidence score.

The raw response is written verbatim to data/omnipath_interactions_<date>.tsv.gz and
hashed, so the edge set used in the paper is identified by a fingerprint that can be
checked against PROVENANCE.md. OmniPath is a rolling resource with no release numbers,
and the file cannot be redistributed under its mixed terms, so a re-run today re-derives
the network from a later export; the fingerprint tells you whether it is the same one.

Usage: python src/03_fetch_network.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
BASE = "https://omnipathdb.org/interactions"

FIELDS = ["sources", "references", "curation_effort", "is_directed", "entity_type"]
DATASETS = ["omnipath", "pathwayextra", "kinaseextra", "ligrecextra"]


def probe_fields(fields: list[str]) -> tuple[list[str], list[str]]:
    """Drop any requested field that OmniPath no longer accepts.

    The API rejects the whole request if a single name in `fields` is unknown, and
    it promotes names to default columns over time: `is_directed`, accepted when
    this export was made on 2026-11-16, is now returned for every record and is
    rejected as an explicit field. Without this probe a re-run dies on the server's
    error string instead of fetching anything. What was dropped is written into the
    meta JSON, so the adjustment is on the record rather than silent.
    """
    dropped: list[str] = []
    while fields:
        q = urllib.parse.urlencode({
            "fields": ",".join(fields),
            "datasets": DATASETS[0],
            "organisms": "9606",
            "format": "tsv",
            "genesymbols": "yes",
        })
        with urllib.request.urlopen(f"{BASE}?{q}", timeout=120) as resp:
            head = resp.read(400).decode("utf-8", "replace")
        if not head.startswith("Something is not entirely good"):
            return fields, dropped
        m = re.search(r"Unknown values for argument `fields`: `([^`]+)`", head)
        if not m:
            raise RuntimeError("OmniPath rejected the request: " + head.strip())
        bad = [x.strip() for x in m.group(1).split(",")]
        keep = [f for f in fields if f not in bad]
        if keep == fields:
            raise RuntimeError("OmniPath rejected the request: " + head.strip())
        dropped += [f for f in bad if f in fields]
        fields = keep
    raise RuntimeError("OmniPath rejected every requested field; check FIELDS")


def main() -> int:
    os.makedirs(DATA, exist_ok=True)
    stamp = time.strftime("%Y%m%d")
    out = os.path.join(DATA, f"omnipath_interactions_{stamp}.tsv.gz")

    fields, dropped = probe_fields(list(FIELDS))
    if dropped:
        print(f"note: dropped now-unknown field(s) {dropped}; "
              f"the API returns them as default columns", flush=True)

    q = urllib.parse.urlencode({
        "fields": ",".join(fields),
        "datasets": ",".join(DATASETS),
        "organisms": "9606",
        "format": "tsv",
        "genesymbols": "yes",
    })
    url = f"{BASE}?{q}"
    print("GET", url, flush=True)

    partial = out + ".part"
    n_bytes = 0 if not os.path.exists(partial) else os.path.getsize(partial)
    t0 = time.time()
    for attempt in range(8):
        headers = {"User-Agent": "jtm-icans/0.1"}
        if n_bytes:
            headers["Range"] = f"bytes={n_bytes}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                        timeout=180) as resp:
                if n_bytes and getattr(resp, "status", 200) == 200:
                    # server ignored the Range header -> restart from zero
                    print("  server ignored Range, restarting", flush=True)
                    n_bytes = 0
                    open(partial, "wb").close()
                fh = open(partial, "ab")
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    fh.write(chunk)
                    n_bytes += len(chunk)
                    if n_bytes % (10 << 20) < (1 << 20):
                        print(f"  {n_bytes/1e6:.0f} MB  {time.time()-t0:.0f}s", flush=True)
                fh.close()
            break
        except Exception as exc:
            print(f"  attempt {attempt+1} interrupted at {n_bytes/1e6:.1f} MB: "
                  f"{type(exc).__name__}", flush=True)
            time.sleep(2)
    else:
        raise RuntimeError(f"download incomplete at {n_bytes} bytes")
    with open(partial, "rb") as fh:
        blob = fh.read()
    sha = hashlib.sha256(blob).hexdigest()
    # The endpoint returns plain TSV; keep the .gz name only for a real gzip body,
    # otherwise the file lands as .tsv, which is the name the pipeline reads.
    is_gzip = blob[:2] == b"\x1f\x8b"
    if not is_gzip and out.endswith(".gz"):
        out = out[:-3]
    os.replace(partial, out)

    with open(os.path.join(DATA, "omnipath_meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"url": url, "file": os.path.basename(out),
                   "bytes": n_bytes,
                   "gzip": is_gzip,
                   "sha256_of_response": sha,
                   "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "fields_requested": FIELDS, "fields_dropped": dropped,
                   "fields_used": fields,
                   "datasets": DATASETS, "organism": "9606"},
                  fh, indent=2)

    opener = gzip.open if is_gzip else open
    with opener(out, "rt", encoding="utf-8", errors="replace") as fh:
        header = fh.readline().rstrip("\n")
        if header.startswith("Something is not entirely good"):
            raise RuntimeError("OmniPath rejected the request: " + header)
        n = sum(1 for _ in fh)
    print(f"rows={n}\nheader={header}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
