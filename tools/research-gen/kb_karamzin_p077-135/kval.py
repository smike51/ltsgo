import json,os,collections
R=r'C:\Users\admin\OneDrive\dev\ltsgo'; D=os.path.join(R,r'kb\staging\karamzin-letters\p077-135')
B={json.loads(l)['seq']:json.loads(l)['body'] for l in open(os.path.join(R,r'texts\karamzin-letters\passages.jsonl'),encoding='utf8')}
T={}
for f in sorted(os.listdir(D)):
    T[f]=[json.loads(l) for l in open(os.path.join(D,f),encoding='utf8')]
    print(f,len(T[f]))
keys={e['key'] for e in T['entities.jsonl']}
assert len(keys)==len(T['entities.jsonl'])
wds=collections.Counter(e['wikidata'] for e in T['entities.jsonl'] if e['wikidata'])
bad=0
def sub(seq,q,w):
    global bad
    if not q or q not in B[seq]: bad+=1; print('BAD',w,seq,(q or '')[:60])
for x in T['quotes.jsonl']: sub(x['passage_seq'],x['text'],'Q')
for x in T['entity_links.jsonl']: sub(x['passage_seq'],x['quote'],'L'); assert x['from_key'] in keys and x['to_key'] in keys
for x in T['mentions.jsonl']: sub(x['passage_seq'],x['surface'],'M'); assert x['entity_key'] in keys
for x in T['facts.jsonl']:
    if not x.get('quote'): bad+=1; print('NOQUOTE',x)
    if x['layer']=='then': sub(x['passage_seq'],x['quote'],'F')
    if x.get('entity_key'): assert x['entity_key'] in keys
for x in T['stops.jsonl']: assert x['place_key'] in keys
print('bad',bad,'dup wikidata',[k for k,v in wds.items() if v>1])
c=collections.Counter((f['layer'],f['status']) for f in T['facts.jsonl']); print(c)
print(collections.Counter(e['status'] for e in T['entities.jsonl']))
