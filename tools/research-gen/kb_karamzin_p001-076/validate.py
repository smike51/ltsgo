import json, os
P = r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
OUT = r'C:\Users\admin\OneDrive\dev\ltsgo\kb\staging\karamzin-letters\p001-076'
bodies = {d['seq']: d['body'] for d in map(json.loads, open(P, encoding='utf8'))}
data, errs = {}, []
for n in ['entities', 'stops', 'entity_links', 'mentions', 'facts', 'quotes', 'sources']:
    rows = []
    for i, l in enumerate(open(os.path.join(OUT, n + '.jsonl'), encoding='utf8')):
        try: rows.append(json.loads(l))
        except Exception as e: errs.append(f'{n}:{i+1} parse {e}')
    data[n] = rows
keys = {e['key'] for e in data['entities']}
if len(keys) != len(data['entities']): errs.append('duplicate entity keys')
ST = {'verified_source', 'verified_wiki', 'book_only', 'unverified', 'disputed', 'obsolete'}
for e in data['entities']:
    if e['status'] not in ST: errs.append(f'bad status {e["key"]}')
    if e['status'] == 'verified_source': errs.append(f'verified_source used {e["key"]}')
    if e['parent_key'] and e['parent_key'] not in keys: errs.append(f'parent {e["key"]}')
def sub(seq, q, w):
    if seq is None: return
    if q not in bodies.get(seq, ''): errs.append(f'{w}: quote not substring seq {seq}: {q[:60]}')
for r in data['entity_links']:
    sub(r['passage_seq'], r['quote'], 'link')
    for k in (r['from_key'], r['to_key']):
        if k not in keys: errs.append(f'link key {k}')
for r in data['quotes']:
    sub(r['passage_seq'], r['text'], 'quote')
    for k in r['entity_keys']:
        if k not in keys: errs.append(f'quote key {k}')
for r in data['facts']:
    if r['entity_key'] not in keys: errs.append(f'fact key {r["entity_key"]}')
    if not r['quote']: errs.append(f'fact without quote {r["entity_key"]}')
    if r['passage_seq'] is not None: sub(r['passage_seq'], r['quote'], 'fact')
    elif not r['source_url']: errs.append(f'fact without source {r["entity_key"]}')
    if r['status'] not in ST or r['status'] == 'verified_source': errs.append(f'fact status {r["entity_key"]}')
for r in data['mentions']:
    if r['entity_key'] not in keys: errs.append(f'mention key {r["entity_key"]}')
    if r['surface'] not in bodies[r['passage_seq']]: errs.append(f'mention surface {r}')
for r in data['stops']:
    if r['place_key'] not in keys: errs.append(f'stop key {r["place_key"]}')
print({n: len(v) for n, v in data.items()})
wd = sum(1 for e in data['entities'] if e['wikidata'])
print(f'wikidata {wd}/{len(keys)} = {100*wd/len(keys):.0f}%')
for kind in ('person', 'place', 'building'):
    es = [e for e in data['entities'] if e['kind'] == kind]
    print(kind, sum(1 for e in es if e['wikidata']), '/', len(es))
print('\n'.join(errs[:50]) or 'VALID', len(errs))
