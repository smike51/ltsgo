import json, re, glob, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
P = r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
OUT = r'C:\Users\admin\OneDrive\dev\ltsgo\kb\staging\karamzin-letters\p001-076'
AGENT = 'agent:karamzin-p001-076'
JOURNEY = 'karamzin-1789'
bodies = {}
for l in open(P, encoding='utf8'):
    d = json.loads(l)
    if d['seq'] <= 76:
        bodies[d['seq']] = d['body']

ENT, STOPS, LINKS, FACTS, QUOTES, EXTRA_MENTIONS = {}, [], [], [], [], []
errors = []

def E(key, kind, ru, en, then=(), parent=None, q=None, wd=None, forms=(), status=None, born=None, died=None, starts=None, ends=None, preservation=None, note=None, cands=None):
    if key in ENT:
        # merge forms
        ENT[key]['forms'] = list(dict.fromkeys(ENT[key]['forms'] + list(forms)))
        return
    ENT[key] = dict(key=key, kind=kind, ru=ru, en=en, then=list(then), parent=parent, q=q, wd=wd, forms=list(forms),
                    status=status, born=born, died=died, starts=starts, ends=ends, preservation=preservation, note=note, cands=cands)

def S(seq, place, arr, dep, cal, prec, dit, tr, pf, pt, kind, note):
    STOPS.append(dict(journey_key=JOURNEY, seq_hint=seq, place_key=place, arrived=arr, departed=dep, calendar=cal,
                      date_precision=prec, date_in_text=dit or None, transport_in=tr or None, passage_from=pf, passage_to=pt,
                      kind=kind, status='book_only', note=note or None))

def fix_quote(seq, q, where):
    b = bodies.get(seq)
    if b is None:
        errors.append(f'{where}: no passage {seq}'); return q
    if q in b: return q
    pat = r'\s+'.join(re.escape(w) for w in q.split())
    m = re.search(pat, b)
    if m: return m.group(0)
    errors.append(f'{where}: quote not in body seq {seq}: {q[:70]}')
    return q

def L(fr, to, kind, seq, quote, note=None, during=None):
    LINKS.append(dict(from_key=fr, to_key=to, kind=kind, passage_seq=seq, during=during, status='book_only',
                      quote=fix_quote(seq, quote, f'link {fr}->{to}'), note=note))

def F(ek, layer, value, seq, quote, fclass='history', status=None, source_url=None, source_title=None, note=None):
    if seq is not None:
        quote = fix_quote(seq, quote, f'fact {ek}')
    FACTS.append(dict(entity_key=ek, key=None, layer=layer, lang='ru', value=value, fact_class=fclass,
                      status=status or ('book_only' if seq is not None else 'verified_wiki'),
                      source_url=source_url, source_title=source_title, passage_seq=seq, quote=quote, note=note, created_by=AGENT))

def Q(seq, text, eks, tags):
    QUOTES.append(dict(passage_seq=seq, text=fix_quote(seq, text, 'quote'), stop_ref=None, entity_keys=eks, tags=tags))

def M(seq, ek, surface):
    EXTRA_MENTIONS.append((seq, ek, surface))

g = dict(E=E, S=S, L=L, F=F, Q=Q, M=M)
for f in sorted(glob.glob(os.path.join(BASE, 'b[0-9]*.py'))):
    exec(open(f, encoding='utf8').read(), g)

ALIAS = {'dane-b': 'becker-dane', 'becker': 'becker-dane'}
for a, t in ALIAS.items():
    if a in ENT:
        ENT[t]['forms'] = list(dict.fromkeys(ENT[t]['forms'] + ENT.pop(a)['forms']))
for l in LINKS:
    l['from_key'] = ALIAS.get(l['from_key'], l['from_key']); l['to_key'] = ALIAS.get(l['to_key'], l['to_key'])
for s_ in STOPS: s_['place_key'] = ALIAS.get(s_['place_key'], s_['place_key'])
for f_ in FACTS: f_['entity_key'] = ALIAS.get(f_['entity_key'], f_['entity_key'])
for q_ in QUOTES: q_['entity_keys'] = [ALIAS.get(k, k) for k in q_['entity_keys']]
EXTRA_MENTIONS[:] = [(s_, ALIAS.get(k, k), u) for s_, k, u in EXTRA_MENTIONS]
for e_ in ENT.values():
    if e_['parent']: e_['parent'] = ALIAS.get(e_['parent'], e_['parent'])

# wikidata enrichment results (from wd.py)
WD = {}
wdf = os.path.join(BASE, 'wd_result.json')
if os.path.exists(wdf):
    WD = json.load(open(wdf, encoding='utf8'))
WDFACTS = []
wff = os.path.join(BASE, 'wd_facts.py')

# referential checks
for l in LINKS:
    for k in (l['from_key'], l['to_key']):
        if k not in ENT: errors.append(f'link refers unknown entity {k}')
for s in STOPS:
    if s['place_key'] not in ENT: errors.append(f'stop unknown place {s["place_key"]}')
for f in FACTS:
    if f['entity_key'] not in ENT: errors.append(f'fact unknown entity {f["entity_key"]}')
for q in QUOTES:
    for k in q['entity_keys']:
        if k not in ENT: errors.append(f'quote unknown entity {k}')
for k, e in ENT.items():
    if e['parent'] and e['parent'] not in ENT: errors.append(f'parent unknown {k}->{e["parent"]}')

# mentions
WORD = 'А-Яа-яЁёA-Za-zÀ-ÿ'
mentions = []
seen = set()
for k, e in ENT.items():
    for form in e['forms']:
        if form.endswith('*') or not form[-1].isalpha():
            pat = r'(?<![%s])%s' % (WORD, re.escape(form))
        else:
            pat = r'(?<![%s])%s[%s]*' % (WORD, re.escape(form), WORD)
        for seq, b in bodies.items():
            for m in re.finditer(pat, b):
                surf = m.group(0)
                key = (seq, k, surf)
                if key not in seen:
                    seen.add(key); mentions.append(dict(passage_seq=seq, entity_key=k, surface=surf))
for seq, k, surf in EXTRA_MENTIONS:
    if surf not in bodies[seq]: errors.append(f'mention surface not in body {seq} {surf}')
    key = (seq, k, surf)
    if key not in seen:
        seen.add(key); mentions.append(dict(passage_seq=seq, entity_key=k, surface=surf))
mentions.sort(key=lambda m: (m['passage_seq'], m['entity_key']))

if '--check' in sys.argv:
    print('\n'.join(errors) or 'no errors')
    print(len(ENT), 'entities', len(STOPS), 'stops', len(LINKS), 'links', len(FACTS), 'facts', len(QUOTES), 'quotes', len(mentions), 'mentions')
    sys.exit()

# entities output
ents_out = []
for k, e in ENT.items():
    w = WD.get(k, {})
    wd = w.get('id')
    meta = {}
    if e['note']: meta['note'] = e['note']
    if w.get('desc'): meta['wikidata_desc'] = w['desc']
    if w.get('ruwiki'): meta['ruwiki'] = w['ruwiki']
    if w.get('enwiki'): meta['enwiki'] = w['enwiki']
    if e['cands'] or w.get('cands'): meta['candidates'] = e['cands'] or w.get('cands')
    if e['q'] and not wd and not e['status']: meta.setdefault('note', 'Wikidata не найдена однозначно')
    status = 'verified_wiki' if wd else (e['status'] or 'unverified')
    name = {'ru': e['ru'], 'en': e['en']}
    ents_out.append(dict(key=k, kind=e['kind'], wikidata=wd, name=name,
                         names_then=[dict(name=n, lang=lg, until=u) for n, lg, u in e['then']],
                         parent_key=e['parent'], lat=w.get('lat'), lon=w.get('lon'),
                         geo_precision=('city' if e['kind'] == 'place' else 'exact') if w.get('lat') is not None else None,
                         born=e['born'] or w.get('born'), died=e['died'] or w.get('died'),
                         starts=e['starts'] or w.get('starts'), ends=e['ends'] or w.get('ends'),
                         preservation=e['preservation'], status=status, meta=meta, created_by=AGENT))

# wikidata-derived facts
sources = {}
def src(url, title, publisher, tier, lang, licence):
    sources[url] = dict(url=url, title=title, publisher=publisher, tier=tier, lang=lang, licence=licence)
src('http://az.lib.ru/k/karamzin_n_m/text_0320.shtml', 'Карамзин Н. М. Письма русского путешественника', 'az.lib.ru', 'primary', 'ru', 'PD')
for k, w in WD.items():
    if not w.get('id'): continue
    url = 'https://www.wikidata.org/wiki/' + w['id']
    src(url, f'Wikidata {w["id"]}: {w.get("label","")}', 'Wikidata', 'dataset', 'mul', 'CC0')
    FACTS.append(dict(entity_key=k, key='wikidata', layer='then', lang='en', value=f'Wikidata {w["id"]}: {w.get("label","")} — {w.get("desc","")}',
                      fact_class='identity', status='verified_wiki', source_url=url, source_title='Wikidata',
                      passage_seq=None, quote=w.get('desc') or w.get('label'), note=None, created_by=AGENT))
if os.path.exists(wff):
    exec(open(wff, encoding='utf8').read(), g)
    for f in FACTS:
        if f['source_url'] and f['source_url'] not in sources:
            pub = 'ru.wikipedia' if 'ru.wikipedia' in f['source_url'] else ('en.wikipedia' if 'en.wikipedia' in f['source_url'] else 'web')
            src(f['source_url'], f['source_title'], pub, 'wiki', 'ru' if 'ru.' in f['source_url'] else 'en', 'CC BY-SA 4.0')

os.makedirs(OUT, exist_ok=True)
def dump(name, rows):
    with open(os.path.join(OUT, name), 'w', encoding='utf8', newline='\n') as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(name, len(rows))
dump('entities.jsonl', ents_out)
dump('stops.jsonl', STOPS)
dump('entity_links.jsonl', LINKS)
dump('mentions.jsonl', mentions)
dump('facts.jsonl', FACTS)
dump('quotes.jsonl', QUOTES)
dump('sources.jsonl', list(sources.values()))
print('\n'.join(errors) or 'no errors')
