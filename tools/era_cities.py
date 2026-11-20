"""City labels for the map "as it was then": Natural Earth places (rank <= 6) + Wikidata history.

Usage: python -X utf8 tools/era_cities.py [--fix-only] [repo_root]
Writes proto/map/data/cities.json: [{q, lon, lat, rank, now, founded, names:[{n, lang, from, to}]}]
The map picks, for the journey year, a name valid in that year (official name P1448 with start/end dates)
and hides cities founded later (P571). Nothing is book-specific: one file serves every journey.
Wikidata (CC0) via SPARQL in batches; Natural Earth is public domain.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = ARGS[0] if ARGS else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, "kb", "staging", "_shared", "geo")
URL = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/ne_10m_populated_places.geojson"
SPARQL = "https://query.wikidata.org/sparql"
Q = """SELECT ?c ?inc ?n ?from ?to ?ru WHERE {
  VALUES ?c { %s }
  OPTIONAL { ?c wdt:P571 ?inc }
  OPTIONAL { ?c p:P1448 ?st . ?st ps:P1448 ?n . OPTIONAL { ?st pq:P580 ?from } OPTIONAL { ?st pq:P582 ?to } }
  OPTIONAL { ?c rdfs:label ?ru FILTER(lang(?ru) = "ru") }
}"""


# Wikidata P571 is sometimes an administrative date (city status, merger, statehood), not the settlement's
# founding. Corrections, each from the city's Wikipedia article; founded=None = old settlement, never hidden.
FIX = {
    "Q35765": {"founded": None},   # Osaka: 1889 = municipality; Naniwa/Osaka centuries older
    "Q34664": {"founded": 1589},   # Hiroshima: castle town founded by Mori Terumoto 1589
    "Q1781": {"founded": None},    # Budapest: 1873 = merger of Buda, Pest, Obuda
    "Q11725": {"founded": None},   # Chongqing: 1929 = municipality; ancient city
    "Q3616": {"founded": None},    # Tehran: capital from 1786, town much older
    "Q959": {"founded": 1860},     # Vladivostok: post founded 2 Jul 1860
    "Q181557": {"founded": None},  # Kaohsiung: 2010 = merger with county; Takao port centuries older
    "Q245023": {"founded": None},  # Taichung: 2010 = merger; old Datun settlement
    "Q128849": {"founded": None},  # Nagano: 1966 = merger; Zenko-ji temple town
    "Q271917": {"founded": None},  # Kushiro: 2005 = merger; Kusuri trading post from 18th c.
    "Q9270": {"founded": None},    # Thimphu: 1955 = capital; Tashichho Dzong 1216
    "Q156243": {"founded": 1910},  # Sinuiju: 2002 = special region; town grew with the railway c. 1910
    "Q335548": {"founded": 1927},  # Mbeya: 2005 = city status; founded 1927 (gold rush)
    "Q14501": {"founded": None},   # Tarakan: 1997 = municipality; island settlement older
    "Q1490": {"names_add": [{"n": "Эдо", "lang": "ru", "from": None, "to": 1868}]},  # Tokyo: Edo until 1868
}
ADMIN_AFTER = 1950  # for the largest cities (rank 0-1) later P571 is statehood/reform (Singapore 1965, Hong Kong 1997);
# smaller ones founded after 1950 are real new towns (Erdenet 1974) and stay hidden


def apply_fix(out):
    for c in out:
        f = FIX.get(c["q"], {})
        if "founded" in f:
            c["founded"] = f["founded"]
        elif c["founded"] is not None and c["founded"] > ADMIN_AFTER and c["rank"] <= 1:  # big old city, new status
            c["founded"] = None
        for nm in f.get("names_add", []):
            if nm not in c["names"]:
                c["names"].append(nm)
    return out


def write(out):
    with open(os.path.join(ROOT, "proto", "map", "data", "cities.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))


def year(v):
    if not v or not v.lstrip("-")[:1].isdigit():  # unknown value / blank node
        return None
    s = v.split("T")[0]
    neg = s.startswith("-")
    y = int(s.lstrip("-").split("-")[0])
    return -y if neg else y


def main():
    path = os.path.join(GEO, "ne_10m_places.geojson")
    if not os.path.exists(path):
        os.makedirs(GEO, exist_ok=True)
        urllib.request.urlretrieve(URL, path)
    places = {}
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        p = f["properties"]
        q = p.get("WIKIDATAID")
        if not q or p.get("SCALERANK", 99) > 6:
            continue
        places[q] = {"q": q, "lon": round(p["LONGITUDE"], 3), "lat": round(p["LATITUDE"], 3), "rank": p["SCALERANK"],
                     "now": p.get("NAME_RU") or p.get("NAME"), "founded": None, "names": []}
    ids = list(places)
    for i in range(0, len(ids), 150):
        batch = ids[i:i + 150]
        body = urllib.parse.urlencode({"query": Q % " ".join("wd:" + x for x in batch), "format": "json"}).encode()
        req = urllib.request.Request(SPARQL, data=body, headers={"User-Agent": "ltsgo-kb/0.1",
                                                                 "Accept": "application/sparql-results+json"})
        for attempt in range(3):
            try:
                rows = json.load(urllib.request.urlopen(req, timeout=120))["results"]["bindings"]
                break
            except Exception as e:
                print("retry", i, e)
                time.sleep(10)
        else:
            continue
        for r in rows:
            c = places[r["c"]["value"].rsplit("/", 1)[1]]
            v = lambda k: r.get(k, {}).get("value")
            inc = year(v("inc"))
            if inc is not None and (c["founded"] is None or inc < c["founded"]):
                c["founded"] = inc
            if v("ru"):
                c["now"] = v("ru")
            if v("n"):
                nm = {"n": v("n"), "lang": r["n"].get("xml:lang"), "from": year(v("from")), "to": year(v("to"))}
                if nm not in c["names"]:
                    c["names"].append(nm)
        time.sleep(1)
        print(i + len(batch), "/", len(ids))
    out = apply_fix(sorted(places.values(), key=lambda c: (c["rank"], c["q"])))
    write(out)
    print("cities", len(out), "with dated names", sum(1 for c in out if any(n["to"] for n in c["names"])))


if __name__ == "__main__":
    if "--fix-only" in sys.argv:  # re-apply FIX to the existing file without querying Wikidata
        path = os.path.join(ROOT, "proto", "map", "data", "cities.json")
        write(apply_fix(json.load(open(path, encoding="utf-8"))))
    else:
        main()
