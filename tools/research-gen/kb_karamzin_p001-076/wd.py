import json, os, sys, time, glob, urllib.request, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
UA = 'ltsgo-kb-bot/0.1 (literary travel guide research)'
API = 'https://www.wikidata.org/w/api.php'
SPARQL = 'https://query.wikidata.org/sparql'
CACHE = os.path.join(BASE, 'wd_scache.json')
cache = json.load(open(CACHE, encoding='utf8')) if os.path.exists(CACHE) else {}

def http(url, data=None, delay=1.0):
    for i in range(8):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            time.sleep(delay); return d
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get('Retry-After') or 0) or (5 * (i + 1))
            print('HTTP', e.code, 'wait', wait, file=sys.stderr, flush=True); time.sleep(min(wait, 90))
        except Exception as e:
            print('ERR', e, file=sys.stderr, flush=True); time.sleep(5)
    raise SystemExit('give up ' + url[:200])

def get(params):
    params = dict(params, format='json')
    url = API + '?' + urllib.parse.urlencode(params)
    if url not in cache:
        cache[url] = http(url)
        json.dump(cache, open(CACHE, 'w', encoding='utf8'))
    return cache[url]

ENT = {}
def E(key, kind, ru, en, then=(), parent=None, q=None, wd=None, forms=(), status=None, **kw):
    if key not in ENT: ENT[key] = dict(kind=kind, ru=ru, en=en, q=q, wd=wd, status=status)
noop = lambda *a, **k: None
g = dict(E=E, S=noop, L=noop, F=noop, Q=noop, M=noop)
for f in sorted(glob.glob(os.path.join(BASE, 'b[0-9]*.py'))):
    exec(open(f, encoding='utf8').read(), g)
for a in ('dane-b', 'becker'): ENT.pop(a, None)

def search(text, lang):
    d = get(dict(action='wbsearchentities', search=text, language=lang, uselang=lang, limit=7, type='item'))
    return [x['id'] for x in d.get('search', [])]

FORCE = {'st-mary-gdansk': None, 'siege-of-ochakov-1788': 'Q2724886', 'royal-library-berlin': 'Q435399', 'new-palace-potsdam': 'Q677383',
 'dresden-neustadt': 'Q8924', 'grosser-garten-dresden': 'Q446470', 'rosenthal-leipzig': 'Q2167253', 'naumburg': 'Q15986',
 'augustinian-monastery-erfurt': 'Q123347667', 'frankfurt-public-library': 'Q2327009', 'st-thomas-strasbourg': 'Q1785858',
 'praise-of-folly': 'Q569869', 'laufen-castle': 'Q678484', 'baden-ag': 'Q63939', 'bern-orphanage': 'Q29651751', 'bern-bear': 'Q666040',
 'grindelwald': 'Q64004', 'brienz': 'Q65268', 'clarens': 'Q178508', 'rhone': 'Q602', 'chateau-de-ferney': 'Q2969210', 'aubonne': 'Q43232',
 'savoy': 'Q426025', 'coxe': 'Q2614067', 'bullinger': 'Q123839', 'rolle': 'Q69570', 'haslital': 'Q689705', 'william-tell': 'Q30908', 'gessler': 'Q679128'}
FORCE = {k: v for k, v in FORCE.items() if v}
NONE = {'st-mary-gdansk', 'stolzenberg-gdansk', 'garrison-church-berlin', 'st-john-church-leipzig', 'st-john-mainz', 'zurich-arsenal', 'bern-arsenal',
 'st-peter-zurich', 'die-alpen-haller', 'atys-piccinni', 'contemplation-de-la-nature', 'haller-sophie', 'tracht-brienz', 'mueller-jg'}
# phase 1: searches via SPARQL mwapi, batched
SQ = '''SELECT ?k ?item ?ord WHERE { VALUES (?k ?s) { %s }
 SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch"; mwapi:search ?s; mwapi:language "%s"; mwapi:limit "7".
 ?item wikibase:apiOutputItem mwapi:item. ?ord wikibase:apiOrdinal true. } }'''
def esc(t): return t.replace(chr(92), ' ').replace('"', ' ')
def bsearch(pairs, lang):
    out = {}
    for i in range(0, len(pairs), 40):
        ch = pairs[i:i+40]
        d = http(SPARQL, data=urllib.parse.urlencode({'query': SQ % (' '.join(f'("{k}" "{esc(t)}")' for k, t in ch), lang), 'format': 'json'}).encode(), delay=2)
        rows = sorted(d['results']['bindings'], key=lambda b: int(b['ord']['value']))
        for b in rows:
            out.setdefault(b['k']['value'], []).append(b['item']['value'].rsplit('/', 1)[1])
        print('search', lang, i, len(pairs), flush=True)
    return out
todo = {k: x for k, x in ENT.items() if x['q'] or x['wd']}
REUSE = '--reuse' in sys.argv and os.path.exists(os.path.join(BASE, 'wd_cands.json'))
if REUSE: OLD = json.load(open(os.path.join(BASE, 'wd_cands.json'), encoding='utf8')); todo = {k: x for k, x in todo.items() if k not in OLD}
en = bsearch([(k, x['q']) for k, x in todo.items() if x['q']], 'en')
miss = [(k, x['ru'].split('(')[0].strip()) for k, x in todo.items() if not en.get(k)]
ru = bsearch(miss, 'ru') if miss else {}
CANDS = {k: list(dict.fromkeys(en.get(k, []) + ru.get(k, []) + ([x['wd']] if x['wd'] else []))) for k, x in todo.items()}
if REUSE: CANDS = {**OLD, **CANDS}
for k, v in FORCE.items(): CANDS[k] = [v] + CANDS.get(k, [])
json.dump(CANDS, open(os.path.join(BASE, 'wd_cands.json'), 'w', encoding='utf8'))

# phase 2: SPARQL details
ids = sorted({i for c in CANDS.values() for i in c})
INFO = {}
Q = '''SELECT ?item ?p31 ?coord ?born ?died ?inc ?dis ?len ?lru ?den ?dru ?ru ?en WHERE {
 VALUES ?item { %s }
 OPTIONAL { ?item wdt:P31 ?p31 } OPTIONAL { ?item wdt:P625 ?coord } OPTIONAL { ?item wdt:P569 ?born }
 OPTIONAL { ?item wdt:P570 ?died } OPTIONAL { ?item wdt:P571 ?inc } OPTIONAL { ?item wdt:P576 ?dis }
 OPTIONAL { ?item rdfs:label ?len FILTER(lang(?len)='en') } OPTIONAL { ?item rdfs:label ?lru FILTER(lang(?lru)='ru') }
 OPTIONAL { ?item schema:description ?den FILTER(lang(?den)='en') } OPTIONAL { ?item schema:description ?dru FILTER(lang(?dru)='ru') }
 OPTIONAL { ?ru schema:about ?item; schema:isPartOf <https://ru.wikipedia.org/> }
 OPTIONAL { ?en schema:about ?item; schema:isPartOf <https://en.wikipedia.org/> } }'''
for i in range(0, len(ids), 120):
    chunk = ids[i:i+120]
    d = http(SPARQL, data=urllib.parse.urlencode({'query': Q % ' '.join('wd:' + x for x in chunk), 'format': 'json'}).encode(), delay=2)
    for b in d['results']['bindings']:
        qid = b['item']['value'].rsplit('/', 1)[1]
        r = INFO.setdefault(qid, dict(p31=set()))
        v = lambda k: b.get(k, {}).get('value')
        if v('p31'): r['p31'].add(v('p31').rsplit('/', 1)[1])
        for k in ('coord', 'born', 'died', 'inc', 'dis', 'len', 'lru', 'den', 'dru', 'ru', 'en'):
            if v(k) and k not in r: r[k] = v(k)
    print('sparql', i, len(ids), flush=True)

def date(s):
    if not s: return None
    if s.startswith('-'): return None
    return s[:10] if not s[5:10] == '01-01' else s[:4]
def year(s):
    try: return int(s[:4])
    except: return None
def ok(kind, r):
    if not r: return False
    if r['p31'] & {'Q4167410', 'Q13406463', 'Q22808320'}: return False
    if kind == 'person':
        return 'Q5' in r['p31'] and (year(r.get('born') or '0') or 0) < 1790
    if kind in ('place', 'building'): return 'coord' in r
    return True

res = {}
for k, c in CANDS.items():
    x = ENT[k]
    good = [i for i in c if ok(x['kind'], INFO.get(i))]
    if k in FORCE: good = [FORCE[k]]
    if k in NONE: good = []
    pick = good[0] if good else None
    out = dict(id=pick, cands=[f"{i}: {INFO.get(i,{}).get('len') or INFO.get(i,{}).get('lru','')} — {INFO.get(i,{}).get('den','')}" for i in c[:5]])
    if pick:
        r = INFO[pick]
        out.update(label=r.get('len') or r.get('lru'), label_ru=r.get('lru'), desc=r.get('den') or r.get('dru'), desc_ru=r.get('dru'),
                   born=date(r.get('born')), died=date(r.get('died')), starts=date(r.get('inc')), ends=date(r.get('dis')),
                   ruwiki=r.get('ru'), enwiki=r.get('en'), wd_guess_mismatch=bool(x['wd'] and x['wd'] != pick))
        if 'coord' in r:
            lon, lat = r['coord'].replace('Point(', '').rstrip(')').split()
            out['lat'], out['lon'] = round(float(lat), 6), round(float(lon), 6)
        if x['kind'] != 'person': out['born'] = out['died'] = None
    res[k] = out
json.dump(res, open(os.path.join(BASE, 'wd_auto.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(len(res), 'queried', sum(1 for r in res.values() if r['id']), 'picked')
