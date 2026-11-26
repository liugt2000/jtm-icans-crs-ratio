"""Reconcile the legacy-term count quoted in the Methods with what the API returns now.

Methods states that the legacy PT *Neurotoxicity* carries 23,247 reports in the same
snapshot, 3.9 times the ICANS PT. The independent pull for the sensitivity analysis
returned 17,539 records. One of the two numbers is wrong, and the Methods cannot keep a
figure that a reader can contradict in one query.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

BASE = "https://api.fda.gov/drug/event.json"
HDRS = {"User-Agent": "jtm-icans/0.3"}

QUERIES = {
    "exact Neurotoxicity": 'patient.reaction.reactionmeddrapt.exact:"Neurotoxicity"',
    "loose Neurotoxicity": 'patient.reaction.reactionmeddrapt:"Neurotoxicity"',
    "exact ICANS": ('patient.reaction.reactionmeddrapt.exact:'
                    '"Immune effector cell-associated neurotoxicity syndrome"'),
    "exact CRS": 'patient.reaction.reactionmeddrapt.exact:"Cytokine release syndrome"',
}


def total(search: str) -> int | None:
    url = f"{BASE}?search={urllib.parse.quote(search, safe='+:.@')}&limit=1"
    try:
        req = urllib.request.Request(url, headers=HDRS)
        with urllib.request.urlopen(req, timeout=120) as fh:
            return json.loads(fh.read().decode())["meta"]["results"]["total"]
    except Exception as exc:  # noqa: BLE001
        print("  failed:", type(exc).__name__, exc)
        return None


if __name__ == "__main__":
    out = {}
    for label, q in QUERIES.items():
        t = total(q)
        out[label] = t
        print(f"  {label:<22} {t}")
    with open("out/legacy_count_reconciliation.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
