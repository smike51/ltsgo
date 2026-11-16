"""Build route data for the map prototype (proto/map/data/<journey>.json) from kb/staging merged files.

Usage: python -I -X utf8 tools/build_proto_data.py [repo_root]
Per stop: place (ru/en, lat/lon), dates (julian), transport class, status, passage, quotes, people mentioned,
images (only with a known licence). Stops without coordinates are skipped and listed in "skipped".
Everything stays a proposal: statuses are copied as they are.
"""
import json
import os
import re
import sys
import urllib.parse
from collections import defaultdict

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


def main():
    ents = {e["key"]: e for e in rd(os.path.join(ST, "_shared", "entities.jsonl"))}
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
        people = defaultdict(list)
        for mt in rd(os.path.join(m, "mentions.jsonl")):
            e = ents.get(mt["entity_key"])
            if e and e.get("kind") == "person" and mt["entity_key"] not in people[mt["passage_seq"]]:
                people[mt["passage_seq"]].append(mt["entity_key"])
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
                "name_en": e["name"].get("en"), "lat": e["lat"], "lon": e["lon"],
                "wikidata": e.get("wikidata"), "kind": s.get("kind"),
                "arrived": s.get("arrived"), "date_in_text": s.get("date_in_text"),
                "transport": tr, "transport_text": s.get("transport_in"),
                "status": s.get("status"), "note": s.get("note"),
                "passage": pf, "heading": ps.get("heading") or ps.get("part"),
                "quotes": [q["text"] for q in (own or pq)[:2]],
                "people": [{"key": k, "name": ents[k]["name"].get("ru") or ents[k]["name"].get("en"),
                            "wikidata": ents[k].get("wikidata")} for k in people.get(pf, [])[:6]],
                "media": media.get(e.get("wikidata"), [])[:4],
                "preservation": e.get("preservation"), "now": now.get(s["place_key"], [])[:3],
            })
        data = {"journey": jkey, **{k: v for k, v in j.items() if k not in ("book", "short")},
                "stops": stops, "skipped": sorted(set(skipped))}
        with open(os.path.join(out_dir, f"{jkey}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        index.append({"journey": jkey, "title_ru": j["title_ru"], "author_ru": j["author_ru"], "years": j["years"]})
        print(jkey, "stops", len(stops), "with media", sum(1 for s in stops if s["media"]),
              "skipped", len(set(skipped)))
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
