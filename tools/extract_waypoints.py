"""Find route hints in a book text: positions (latitude/longitude), winds, speed. Output = CANDIDATES for review.

Usage: python -I -X utf8 tools/extract_waypoints.py <book> [repo_root]
Reads texts/<book>/passages.jsonl, writes kb/staging/<book>/route/candidates.jsonl:
  {passage_seq, heading, date_in_text, kind (position|wind|speed), quote, lat, lon, lat_only, lon_only, winds, knots}
Coordinates are parsed only when the hemisphere is written next to the number; everything else stays null
for the reviewer. Nothing here is a fact yet (rule 2): a person or model turns candidates into waypoints.jsonl.
"""
import json
import os
import re
import sys

BOOK = sys.argv[1]
ROOT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUM = r"(\d{1,3}(?:\s?\d/\d|[½¼¾])?)"
DEG = NUM + r"\s?(?:°|R(?=\s)|-?(?:х|ти|ми|го)?\s?градус\w*)"
LAT = re.compile(DEG + r"\s*(?:(?P<h>северн\w*|южн\w*|с\.|ю\.|сев\.)\s*)?(?:широт\w*|ш\.)", re.I)
LON = re.compile(DEG + r"\s*(?:(?P<h>восточн\w*|западн\w*|в\.|з\.)\s*)?(?:долгот\w*|д\.)", re.I)
GEO = re.compile(r"широт|долгот|\bш\.|\bд\.|экватор|тропик", re.I)
WIND = re.compile(r"(?<![A-Za-z])(N{1,2}O|N{1,2}W|S{1,2}O|S{1,2}W|[NS][NS]?[OW]|O[NS]O|W[NS]W|N|S|O|W)(?![A-Za-z])")
WIND_RU = re.compile(r"пассат\w*|муссон\w*|штил\w*|шквал\w*|бейдевинд\w*|фордевинд\w*|галфвинд\w*", re.I)
KNOTS = re.compile(NUM + r"\s?(?:1/2\s)?узл", re.I)


def num(s):
    s = s.replace("½", " 1/2").replace("¼", " 1/4").replace("¾", " 3/4")
    m = re.match(r"(\d+)(?:\s?(\d)/(\d))?", s.strip())
    return int(m.group(1)) + (int(m.group(2)) / int(m.group(3)) if m.group(2) else 0)


def coord(rx, s, neg):
    m = rx.search(s)
    if not m:
        return None, None
    v, h = num(m.group(1)), (m.group("h") or "").lower()
    if not h:
        return None, v  # number without hemisphere: reviewer decides
    return (-v if h.startswith(neg) else v), v


def main():
    src = os.path.join(ROOT, "texts", BOOK, "passages.jsonl")
    out_dir = os.path.join(ROOT, "kb", "staging", BOOK, "route")
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for line in open(src, encoding="utf-8"):
        p = json.loads(line)
        for s in re.split(r"(?<=[.!?;])\s+", p["body"]):
            s1 = " ".join(s.split())
            if len(s1) < 8:
                continue
            row = {"passage_seq": p["seq"], "heading": p.get("heading"), "date_in_text": p.get("date_in_text"),
                   "quote": s1}
            if GEO.search(s1) and re.search(r"\d", s1) and not re.search(r"Реомюр|термометр|в тени", s1):
                lat, lat_raw = coord(LAT, s1, ("ю", "south"))
                lon, lon_raw = coord(LON, s1, ("з", "west"))
                if lat_raw is not None or lon_raw is not None or re.search(r"экватор|тропик", s1, re.I):
                    rows.append({**row, "kind": "position", "lat": lat, "lon": lon,
                                 "lat_raw": lat_raw, "lon_raw": lon_raw})
                    continue
            w = [x for x in WIND.findall(s1) if x not in ("S", "O", "W", "N") or re.search(r"ветер|дул|задул|ветр", s1)]
            r = WIND_RU.findall(s1)
            if w or r:
                rows.append({**row, "kind": "wind", "winds": w, "wind_words": [x.lower() for x in r]})
                continue
            k = KNOTS.search(s1)
            if k:
                rows.append({**row, "kind": "speed", "knots": num(k.group(1))})
    with open(os.path.join(out_dir, "candidates.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    print(BOOK, len(rows), dict(Counter(r["kind"] for r in rows)))


if __name__ == "__main__":
    main()
