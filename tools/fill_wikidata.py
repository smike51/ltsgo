"""Fill wikidata id + coordinates for rows of research/places-*.jsonl that cite a Wikipedia article.

Usage: python -I -X utf8 tools/fill_wikidata.py research/places-<book>.jsonl
Status is not raised; a verified_wiki row whose article is not found drops to unverified.
"""
import json, sys, urllib.parse, urllib.request, urllib.error, time
path = sys.argv[1]
UA = {"User-Agent": "kb-research-script/0.1 (https://www.mediawiki.org/wiki/API:Etiquette) python-urllib"}
def get(url):
    for i in range(6):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 5*(i+1))
    raise SystemExit("rate limited: "+url)
rows = [json.loads(l) for l in open(path, encoding="utf-8")]
for r in rows:
    if r.get("wikidata") and r.get("lat"):
        continue
    wiki = next((s["url"] for s in r.get("sources", []) if "wikipedia.org/wiki/" in s.get("url", "")), None)
    if not wiki: continue
    host, title = wiki.split("/wiki/", 1)
    title = urllib.parse.unquote(title)
    q = get(f"{host}/w/api.php?" + urllib.parse.urlencode({"action":"query","prop":"pageprops","ppprop":"wikibase_item","redirects":1,"titles":title,"format":"json"}))
    page = next(iter(q["query"]["pages"].values()))
    wd = page.get("pageprops", {}).get("wikibase_item")
    if not wd:
        if r["status"] == "verified_wiki": r["status"] = "unverified"
        r["notes"] = (r.get("notes") or "") + " | wiki page not found by code"; print("MISS", title); continue
    r["wikidata"] = r.get("wikidata") or wd
    e = get("https://www.wikidata.org/wiki/Special:EntityData/%s.json" % wd)["entities"][wd]
    c = e["claims"].get("P625")
    if c and not r.get("lat"):
        v = c[0]["mainsnak"]["datavalue"]["value"]; r["lat"], r["lon"] = round(v["latitude"],6), round(v["longitude"],6)
    r["notes"] = (r.get("notes") or "") + f" | wikidata+coords filled by code from {wiki}"
    print(wd, r.get("lat"), title)
    time.sleep(1.5)
open(path, "w", encoding="utf-8", newline="\n").write("".join(json.dumps(x, ensure_ascii=False)+"\n" for x in rows))
