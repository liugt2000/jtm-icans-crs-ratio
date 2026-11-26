"""Correct the creator list on the published Zenodo record, without cutting a new version.

A metadata-only edit keeps the DOI, the files and the version number; it only rewrites the
DataCite record that a citation of the dataset reads. Two of the four authors have no ORCID,
so `identifiers` is omitted for them rather than left as an empty string.

Two traps in this API, both of which cost a round here:

1. `application/json` is the *legacy* view. It calls keywords `keywords`, returns
   `resource_type` in another shape, and echoes creators without family_name/given_name.
   Writing those keys back silently empties resource_type and the keywords, and the publish
   step then fails with "Missing data for required field: metadata.resource_type".
   Read and write `application/vnd.inveniordm.v1+json` throughout.
2. `affiliations` is a sibling of `person_or_org`. An `affiliation` key inside
   `person_or_org` returns 200 and is dropped.

    python src/99d_zenodo_creators.py            # write metadata, verify, stop before publishing
    python src/99d_zenodo_creators.py --publish  # publish the verified draft
"""

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Reuse the session-cookie + curl machinery that already worked for v1.0.1 and v1.0.2.
_spec = importlib.util.spec_from_file_location("z99c", ROOT / "src" / "99c_zenodo_v101.py")
z99 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(z99)

RECORD = "24552287"

CREATORS = [
    {
        "name": "Zhu, Ying",
        "affiliation": ("Department of Clinical Blood Transfusion, First Affiliated Hospital of "
                        "Zhejiang Chinese Medical University, Hangzhou, China"),
        "orcid": None,
    },
    {
        "name": "Wang, Heyong",
        "affiliation": ("Central Laboratory, Innovation and Incubation Center, Shanghai Pulmonary "
                        "Hospital, School of Medicine, Tongji University, Shanghai, China"),
        "orcid": "0000-0001-5841-2508",
    },
    {
        "name": "Zhang, Chengya",
        "affiliation": ("Department of General Medicine, Beicai Community Health Service of "
                        "Pudong New Area, Shanghai, China"),
        "orcid": None,
    },
    {
        "name": "Liu, Gentao",
        "affiliation": ("Shanghai Pulmonary Hospital, School of Medicine, Tongji University, "
                        "Shanghai, China"),
        "orcid": "0009-0004-3591-7190",
    },
]


def person(c: dict) -> dict:
    family, _, given = c["name"].partition(",")
    po = {"type": "personal", "family_name": family.strip()}
    if given.strip():
        po["given_name"] = given.strip()
    if c.get("orcid"):
        po["identifiers"] = [{"scheme": "orcid", "identifier": c["orcid"]}]
    item = {"person_or_org": po}
    if c.get("affiliation"):
        item["affiliations"] = [{"name": c["affiliation"]}]
    return item


def read_v1(path: str, jar: str, csrf: str) -> dict:
    cmd = ["curl", "-sS", "--noproxy", "*", "--resolve", f"zenodo.org:443:{z99.IP}",
           "--max-time", "120", f"{z99.BASE}{path}",
           "-H", f"Cookie: {jar}", "-H", f"X-CSRFToken: {csrf}",
           "-H", "Accept: application/vnd.inveniordm.v1+json"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"__raw__": (r.stdout or "")[:600]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", default=RECORD)
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()

    jar, csrf = z99.cookie_jar(a.record)
    print(f"session cookies: {len(jar)} chars, csrf {len(csrf)}", flush=True)

    # The published record is the only trustworthy source of resource_type, subjects and
    # rights; a draft opened from it can already be missing them if an earlier PUT used the
    # legacy key names.
    pub = read_v1(f"/api/records/{a.record}", jar, csrf)
    pm = pub.get("metadata", {}) or {}
    if not pm.get("title"):
        print(f"cannot read published metadata: {json.dumps(pub, ensure_ascii=False)[:400]}",
              flush=True)
        return 4
    print(f"source record: v{pm.get('version')} | resource_type="
          f"{(pm.get('resource_type') or {}).get('id')} | subjects={len(pm.get('subjects') or [])} "
          f"| creators={[c.get('person_or_org', {}).get('family_name') for c in pm.get('creators', [])]}",
          flush=True)

    st, body = z99.api("POST", f"/api/records/{a.record}/draft", jar, csrf, json_body={})
    print(f"open draft: {st}", flush=True)

    payload = {
        "title": pm["title"],
        "publication_date": pm["publication_date"],
        "description": pm["description"],
        "resource_type": {"id": (pm.get("resource_type") or {}).get("id", "dataset")},
        "creators": [person(c) for c in CREATORS],
        "rights": [{"id": r.get("id")} for r in (pm.get("rights") or [{"id": "cc-by-4.0"}])],
        "languages": [{"id": lng.get("id")} for lng in (pm.get("languages") or [{"id": "eng"}])],
        "subjects": [{"subject": s.get("subject", s)} for s in (pm.get("subjects") or [])],
        "version": pm.get("version"),
        "publisher": pm.get("publisher") or "Zenodo",
    }

    st, body = z99.api("PUT", f"/api/records/{a.record}/draft", jar, csrf,
                       json_body={"metadata": payload})
    print(f"metadata PUT: {st}", flush=True)
    if st not in (200, 201):
        print(body[:1200], flush=True)
        return 8

    d = read_v1(f"/api/records/{a.record}/draft", jar, csrf)
    dm = d.get("metadata", {}) or {}
    got = dm.get("creators", [])
    print(f"verify: {len(got)} creators, resource_type="
          f"{(dm.get('resource_type') or {}).get('id')}, subjects={len(dm.get('subjects') or [])}",
          flush=True)
    ok = True
    for c in got:
        po = c.get("person_or_org", {}) or {}
        ids = [i.get("identifier") for i in (po.get("identifiers") or [])] or ["none"]
        aff = [x.get("name") for x in (c.get("affiliations") or [])]
        print(f"   {po.get('family_name')}, {po.get('given_name')} | orcid={ids} | "
              f"aff={'yes' if aff else 'NO'}", flush=True)
        if not po.get("family_name") or not po.get("given_name") or not aff:
            ok = False
    names = [(c.get("person_or_org", {}) or {}).get("family_name") for c in got]
    if names != ["Zhu", "Wang", "Zhang", "Liu"]:
        print(f"  !! unexpected order/names: {names}", flush=True)
        ok = False
    if (dm.get("resource_type") or {}).get("id") != "dataset":
        print("  !! resource_type lost", flush=True)
        ok = False
    if len(dm.get("subjects") or []) != len(pm.get("subjects") or []):
        print("  !! subjects changed", flush=True)
        ok = False
    if dm.get("version") != pm.get("version"):
        print("  !! version changed", flush=True)
        ok = False

    if not a.publish:
        print("\ndraft is written and verified; nothing published yet.", flush=True)
        return 0 if ok else 9
    if not ok:
        print("refusing to publish: verification failed", flush=True)
        return 9

    st, body = z99.api("POST", f"/api/records/{a.record}/draft/actions/publish", jar, csrf,
                       json_body={})
    print(f"publish: {st}", flush=True)
    if st not in (200, 202):
        print(body[:900], flush=True)
        return 10
    print("published", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
