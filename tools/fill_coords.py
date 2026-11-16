"""Fill lat/lon of place/building entities from Wikidata P625 (coordinate location).

Usage: python -I -X utf8 tools/fill_coords.py [repo_root]
Edits kb/staging/<book>/<chunk>/entities.jsonl in place: only rows of kind place/building with a wikidata id
and no lat. Sets meta.coord_source. Does not change statuses. Run tools/merge_staging.py afterwards.
"""
import glob
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "geo-research-script/1.0"
API = "https://www.wikidata.org/w/api.php"


def get(ids):
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids), "props": "claims",
                                "format": "json"})
    for attempt in range(5):
        try:
            req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(req, timeout=60))["entities"]
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 5 * (attempt + 1)))
    raise RuntimeError("wikidata: too many 429")


def main():
    files = glob.glob(os.path.join(ROOT, "kb", "staging", "*", "*", "entities.jsonl"))
    files = [f for f in files if os.sep + "merged" + os.sep not in f]
    need = set()
    data = {}
    for f in files:
        rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
        data[f] = rows
        for r in rows:
            if r.get("kind") in ("place", "building") and r.get("wikidata") and r.get("lat") is None:
                need.add(r["wikidata"].strip())
    need = sorted(w for w in need if w.startswith("Q"))
    coords = {}
    for i in range(0, len(need), 50):
        for qid, ent in get(need[i:i + 50]).items():
            for c in (ent.get("claims") or {}).get("P625", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if v and v.get("globe", "").endswith("Q2"):
                    coords[qid] = (round(v["latitude"], 6), round(v["longitude"], 6))
                    break
        time.sleep(1)
    n = 0
    for f, rows in data.items():
        changed = False
        for r in rows:
            c = coords.get((r.get("wikidata") or "").strip())
            if c and r.get("kind") in ("place", "building") and r.get("lat") is None:
                r["lat"], r["lon"] = c
                r.setdefault("meta", {})["coord_source"] = "wikidata P625"
                changed, n = True, n + 1
        if changed:
            with open(f, "w", encoding="utf-8", newline="\n") as out:
                for r in rows:
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"asked {len(need)} ids, got coords for {len(coords)}, filled {n} rows")


if __name__ == "__main__":
    main()
