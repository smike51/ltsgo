import json, os, re, time, urllib.request, urllib.parse, glob
BASE = os.path.dirname(os.path.abspath(__file__))
UA = 'ltsgo-kb-bot/0.1 (literary travel guide research)'
WD = json.load(open(os.path.join(BASE, 'wd_result.json'), encoding='utf8'))
KIND = {}
def E(key, kind, *a, **kw): KIND.setdefault(key, kind)
noop = lambda *a, **k: None
g = dict(E=E, S=noop, L=noop, F=noop, Q=noop, M=noop)
for f in sorted(glob.glob(os.path.join(BASE, 'b[0-9]*.py'))): exec(open(f, encoding='utf8').read(), g)
KW = re.compile(r'\b(destroyed|demolished|rebuilt|reconstructed|reconstruction|razed|burn(?:ed|t)|ruin(?:s|ed)?|survive[sd]?|restored|bombing|bombed|now (?:houses|a|the)|today|museum)\b', re.I)
out = []
for k, w in WD.items():
    if KIND.get(k) not in ('building', 'artwork') or not w.get('enwiki'): continue
    title = w['enwiki'].rsplit('/wiki/', 1)[1]
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(dict(action='query', prop='extracts', exintro=1, explaintext=1, redirects=1, titles=urllib.parse.unquote(title), format='json'))
    for i in range(5):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30)); break
        except Exception as e:
            print('ERR', k, e); time.sleep(10 * (i + 1))
    else: continue
    ext = next(iter(d['query']['pages'].values())).get('extract', '')
    sents = re.split(r'(?<=[.!?])\s+', ext)
    hits = [s for s in sents if KW.search(s) and len(s.split()) <= 40]
    if hits: out.append(dict(key=k, url=w['enwiki'], sents=hits[:2]))
    time.sleep(0.5)
json.dump(out, open(os.path.join(BASE, 'wp_now.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(out))
