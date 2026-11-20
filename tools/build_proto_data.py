"""Build route data for the map prototype (proto/map/data/<journey>.json) from kb/staging merged files.

Usage: python -I -X utf8 tools/build_proto_data.py [repo_root]
Per stop: place (ru/en, lat/lon), dates (julian), transport class, status, passage, quotes, people mentioned,
images (only with a known licence). Stops without coordinates are skipped and listed in "skipped".
Everything stays a proposal: statuses are copied as they are.

Route: text waypoints (kb/staging/<book>/route/waypoints.jsonl) are placed between stops by their place in
the book; each leg gets real geometry (great circle, or a sea route when that crosses land). Person mentions
are tied to the nearest preceding stop or waypoint → date + place; the links are written to
kb/staging/<book>/route/mention_anchors.jsonl (proposals, status book_only).
Sea legs that would cross land need the searoute package (pip install --user searoute); run without -I so
user site-packages are visible: python -P -X utf8 tools/build_proto_data.py
"""
import json
import os
import re
import sys
import urllib.parse
import bisect
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_legs as rl  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "kb", "staging")
JOURNEYS = {
    "karamzin-1789": {"book": "karamzin-letters", "short": "karamzin", "title_ru": "Письма русского путешественника",
                      "author_ru": "Николай Карамзин", "years": "1789–1790", "borders": "world_1783"},
    "goncharov-1852": {"book": "goncharov-pallada", "short": "goncharov", "title_ru": "Фрегат «Паллада»",
                       "author_ru": "Иван Гончаров", "years": "1852–1855", "borders": "world_1815"},
}


def rd(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def transport(t):
    t = (t or "").lower()
    if not t:
        return None
    for cls, words in (("foot", ("пешком", "foot")), ("horse", ("верхом", "horse")),
                       ("sledge", ("sledge", "сани")), ("rail", ("rail", "поезд")),
                       ("water", ("лодк", "boat", "ship", "packet", "sail", "frigate", "schooner", "корабл"))):
        if any(w in t for w in words):
            return cls
    return "carriage"


def thumb(page_url, file_url):
    m = re.search(r"commons\.wikimedia\.org/wiki/(File:[^?#]+)", page_url or "")
    if m:
        name = urllib.parse.unquote(m.group(1))[5:]
        return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=640"
    return file_url


def person(ents, k):
    return {"key": k, "name": ents[k]["name"].get("ru") or ents[k]["name"].get("en"), "wikidata": ents[k].get("wikidata")}


def route(jkey, j, stops, nb, mentions, ents, land, roads=None, rivers=None):
    """Waypoints between stops, leg geometry, person mentions tied to date + place. Mutates stops."""
    # 1. stops in book order (passage, offset), kept monotonic along the journey
    last = (0, 0)
    for s in stops:
        last = max(last, (s["passage"] or 0, max(s.pop("_off"), 0)))
        s["_k"], s["_wps"] = last, []
    # 2. each waypoint goes after the last stop that precedes it in the text
    wps = []
    for w in rd(os.path.join(ST, j["book"], "route", "waypoints.jsonl")):
        if w.get("journey_key") not in (None, jkey) or w.get("status") in ("obsolete", "disputed"):
            continue
        off = rl.find_offset(nb.get(w["passage_seq"], ""), w["quote"])
        if off < 0:
            print("  waypoint quote not found:", w["passage_seq"], w["quote"][:50])
            continue
        k = (w["passage_seq"], off)
        i = max((n for n, s in enumerate(stops) if s["_k"] <= k), default=0)
        stops[i]["_wps"].append({**w, "_k": k, "after": i})
    chain = []
    for s in stops:
        chain.append(s)
        s["_wps"].sort(key=lambda w: w["_k"])
        wps += s["_wps"]
        chain += s["_wps"]
    rl.fill_coords(chain)
    for w in wps:
        if w.get("interp"):
            rl.to_sea(land, w)
    # 3. legs: stop[i-1] → its waypoints → stop[i]. A ship waits where it was left: after a short land trip
    #    (e.g. Cape Colony, Shuri) the next water leg first goes back to that port by land.
    ship = None
    for i in range(1, len(stops)):
        a, b = stops[i - 1], stops[i]
        water = b["transport"] == "water" or bool(a["_wps"])
        land_back = []
        if water and ship and ship is not a and a["transport"] != "water" \
                and 1 < rl.gc_dist((a["lon"], a["lat"]), (ship["lon"], ship["lat"])) < 150:
            land_back = [(ship["lon"], ship["lat"])]
        pts = [(a["lon"], a["lat"]), *land_back] + \
              [(p["lon"], p["lat"]) for p in [*a["_wps"], b] if p["lat"] is not None and p["lon"] is not None]
        coords, how = [list(pts[0])], set()
        for n, (p, q) in enumerate(zip(pts, pts[1:])):
            if water and not (land_back and n == 0):
                seg, h = rl.sea_leg(land, p, q)
                if h == "gc-land" and rivers:  # inland water: follow the river
                    r = rivers.leg(p, q)
                    seg, h = (r, "river") if r else (seg, h)
            else:  # by land: a sledge in winter goes on river ice; else roads / paths; else a straight line
                seg = rivers.leg(p, q) if rivers and b["transport"] == "sledge" else None
                h = "river"
                if not seg:
                    seg = roads.leg(p, q, "foot" if b["transport"] == "foot" else "car") if roads else None
                    h = "road"
                if not seg:
                    seg, h = rl.gc_line(p, q), "gc"
            coords += seg[1:]
            how.add(h)
        if water:
            ship = b
        b["leg"] = rl.unwrap(coords)
        b["leg_how"] = next((x for x in ("searoute", "river", "road", "gc-land") if x in how), "gc")
        if water:
            b["transport"] = "water"
    # 4. person mentions → nearest preceding anchor (stop or waypoint) → date + place
    anchors = sorted([(s["_k"], 0, n, "stop") for n, s in enumerate(stops)] +
                     [(w["_k"], 1, n, "wp") for n, w in enumerate(wps)])
    keys = [x[0] for x in anchors]
    links, seen = [], set()
    for mt in mentions:
        body, sf = nb.get(mt["passage_seq"], ""), mt.get("surface") or ""
        if len(sf) < 3:
            continue
        for mo in re.finditer(r"(?<!\w)" + re.escape(sf) + r"(?!\w)", body):  # whole words: «адмирал» ≠ «адмиралтейство»
            k = (mt["passage_seq"], mo.start())
            n = bisect.bisect_right(keys, k) - 1
            if n < 0:
                continue  # before the journey starts in the text
            _, _, idx, kind = anchors[n]
            if (mt["entity_key"], kind, idx) in seen:
                continue
            seen.add((mt["entity_key"], kind, idx))
            obj = stops[idx] if kind == "stop" else wps[idx]
            links.append({"journey_key": jkey, "entity_key": mt["entity_key"], "passage_seq": k[0], "offset": k[1],
                          "surface": sf, "anchor": kind, "anchor_index": idx,
                          "place_key": obj["key"] if kind == "stop" else stops[obj["after"]]["key"],
                          "waypoint_quote": obj["quote"] if kind == "wp" else None,
                          "date": obj.get("arrived") if kind == "stop" else obj.get("date"),
                          "calendar": "julian", "status": "book_only",
                          "method": "nearest preceding stop or waypoint in the text"})
    for x in stops + wps:
        x["people"] = []
    for L in sorted(links, key=lambda x: (x["passage_seq"], x["offset"])):
        tgt = (stops if L["anchor"] == "stop" else wps)[L["anchor_index"]]["people"]
        if L["entity_key"] not in [p["key"] for p in tgt]:
            tgt.append(person(ents, L["entity_key"]))
    out = os.path.join(ST, j["book"], "route")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "mention_anchors.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for L in links:
            f.write(json.dumps(L, ensure_ascii=False) + "\n")
    for s in stops:
        s.pop("_k"), s.pop("_wps")
        s["people"] = s["people"][:8]
    return [{"after": w["after"], "lat": w["lat"], "lon": w["lon"], "interp": w.get("interp"), "quote": w["quote"],
             "date": w.get("date"), "date_precision": w.get("date_precision"), "winds": w.get("winds") or [],
             "note": w.get("note"), "status": w.get("status"), "passage": w["passage_seq"],
             "people": w["people"][:6]} for w in wps]


def main():
    ents = {e["key"]: e for e in rd(os.path.join(ST, "_shared", "entities.jsonl"))}
    land = rl.Land(os.path.join(ST, "_shared", "geo", "ne_50m_land.geojson"))
    rivers = rl.Rivers(os.path.join(ST, "_shared", "geo", "ne_10m_rivers.geojson"))
    out_dir = os.path.join(ROOT, "proto", "map", "data")
    os.makedirs(out_dir, exist_ok=True)
    index = []
    for jkey, j in JOURNEYS.items():
        m = os.path.join(ST, j["book"], "merged")
        passages = {p["seq"]: p for p in rd(os.path.join(ROOT, "texts", j["book"], "passages.jsonl"))}
        quotes = defaultdict(list)
        for q in rd(os.path.join(m, "quotes.jsonl")):
            if q.get("quote_ok", True):
                quotes[q["passage_seq"]].append(q)
        mentions = [mt for mt in rd(os.path.join(m, "mentions.jsonl"))
                    if (ents.get(mt["entity_key"]) or {}).get("kind") == "person"]
        nb = {k: rl.norm(p.get("body")) for k, p in passages.items()}
        now = defaultdict(list)  # "what is left today" facts per place
        for f in rd(os.path.join(m, "facts.jsonl")):
            if f.get("layer") == "now" and f.get("fact_class") == "preservation" and f.get("source_url"):
                now[f["entity_key"]].append({"value": f["value"], "status": f.get("status"), "quote": f.get("quote"),
                                             "source_title": f.get("source_title"), "source_url": f["source_url"]})
        media = defaultdict(list)
        for r in rd(os.path.join(ROOT, "research", f"media-{j['short']}.jsonl")):
            lic = (r.get("licence") or "").strip()
            if not lic or lic.lower() == "unknown" or not r.get("place_wikidata"):
                continue
            media[r["place_wikidata"]].append({"src": thumb(r.get("page_url"), r.get("file_url")),
                                               "page": r.get("page_url"), "title": r.get("title"),
                                               "author": r.get("author"), "year": r.get("year"),
                                               "licence": lic, "era": r.get("era")})
        stops, skipped, prev_tr, last_key = [], [], "carriage", None
        for s in rd(os.path.join(m, "stops.jsonl")):
            if s.get("journey_key") not in (None, jkey) or s.get("kind") == "mention_only":
                continue
            e = ents.get(s["place_key"])
            if not e or e.get("lat") is None:
                skipped.append(s["place_key"])
                continue
            if s["place_key"] == last_key:
                continue
            last_key = s["place_key"]
            tr = transport(s.get("transport_in")) or prev_tr
            prev_tr = tr
            pf = s.get("passage_from")
            pq = quotes.get(pf, [])
            own = [q for q in pq if s["place_key"] in (q.get("entity_keys") or [])]
            ps = passages.get(pf, {})
            stops.append({
                "key": s["place_key"], "name": e["name"].get("ru") or e["name"].get("en"),
                "name_then": next((n["name"] for n in e.get("names_then") or [] if n.get("lang") == "ru"), None),  # as the author wrote it
                "name_en": e["name"].get("en"), "lat": s.get("route_lat", e["lat"]), "lon": s.get("route_lon", e["lon"]),  # route point overrides place (river mouth)
                "wikidata": e.get("wikidata"), "kind": s.get("kind"),
                "arrived": s.get("arrived"), "date_in_text": s.get("date_in_text"),
                "transport": tr, "transport_text": s.get("transport_in"),
                "status": s.get("status"), "note": s.get("note"),
                "passage": pf, "heading": ps.get("heading") or ps.get("part"),
                "quotes": [q["text"] for q in (own or pq)[:2]],
                "_off": rl.find_offset(nb.get(pf, ""), s.get("date_in_text")),
                "media": media.get(e.get("wikidata"), [])[:4],
                "preservation": e.get("preservation"), "now": now.get(s["place_key"], [])[:3],
            })
        roads = rl.Roads(os.path.join(ST, j["book"], "route", "road_legs.json"))
        wps = route(jkey, j, stops, nb, mentions, ents, land, roads, rivers)
        roads.save()
        data = {"journey": jkey, **{k: v for k, v in j.items() if k not in ("book", "short")},
                "stops": stops, "waypoints": wps, "skipped": sorted(set(skipped))}
        with open(os.path.join(out_dir, f"{jkey}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        index.append({"journey": jkey, "title_ru": j["title_ru"], "author_ru": j["author_ru"], "years": j["years"]})
        print(jkey, "stops", len(stops), "waypoints", len(wps), "with media", sum(1 for s in stops if s["media"]),
              "skipped", len(set(skipped)), "legs", dict(Counter(s.get("leg_how") for s in stops[1:])))
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
