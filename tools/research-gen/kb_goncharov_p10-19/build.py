import json,re,os,sys
REPO=r'C:\Users\admin\OneDrive\dev\ltsgo'
OUT=os.path.join(REPO,'kb','staging','goncharov-pallada','p10-19')
os.makedirs(OUT,exist_ok=True)
HERE=os.path.dirname(os.path.abspath(__file__))
B={}
for l in open(os.path.join(REPO,'texts','goncharov-pallada','passages.jsonl'),encoding='utf8'):
    d=json.loads(l)
    if 10<=d['seq']<=19: B[d['seq']]=d['body']
ERR=[]
END=re.compile(r'[.!?…]+(?:"|»|\))?(?=\s|$)')
def S_(seq,start,n=1):
    t=B[seq]; i=t.find(start)
    if i<0: ERR.append(f'NOTFOUND {seq}: {start[:60]}'); return None
    j=i
    for _ in range(n):
        k=j+1
        while True:
            m=END.search(t,k)
            if m and m.group(0)=='.' and m.start()>=2 and t[m.start()-1].isupper() and not t[m.start()-2].isalpha(): k=m.end(); continue
            break
        j=m.end() if m else len(t)
    return t[i:j]
JK='goncharov-1852'; CB='p10-19'
WD='https://www.wikidata.org/wiki/'
ents={}
def E(key,kind,wd,ru,en,status=None,**kw):
    st=status or ('verified_wiki' if wd else 'book_only')
    r={'key':key,'kind':kind,'wikidata':wd,'name':{'ru':ru,'en':en},'names_then':kw.pop('names_then',[]),
       'parent_key':kw.pop('parent_key',None),'lat':None,'lon':None,'geo_precision':kw.pop('geo',None),
       'born':kw.pop('born',None),'died':kw.pop('died',None),'starts':kw.pop('starts',None),'ends':kw.pop('ends',None),
       'preservation':kw.pop('pres',None),'status':st,'meta':kw.pop('meta',{}),'created_by':'agent:'+CB}
    assert not kw,kw
    ents[key]=r
exec(open(os.path.join(HERE,'ents_spec.py'),encoding='utf8').read())
exec(open(os.path.join(HERE,'stops_links_spec.py'),encoding='utf8').read())
exec(open(os.path.join(HERE,'facts_spec.py'),encoding='utf8').read())
quotes=[]
def QT(seq,start,tags,ents_=(),n=1):
    q=S_(seq,start,n)
    if q: quotes.append({'passage_seq':seq,'text':q,'stop_ref':None,'entity_keys':list(ents_),'tags':tags})
exec(open(os.path.join(HERE,'quotes_spec.py'),encoding='utf8').read())
exec(open(os.path.join(HERE,'mentions_spec.py'),encoding='utf8').read())
mentions=[];seen=set()
for k,e in ents.items():
    for w in set([e['name']['ru']]+[x['name'] for x in e['names_then']]):
        for seq,t in B.items():
            if len(w)>=4 and w in t and (seq,k) not in seen:
                seen.add((seq,k)); mentions.append({'passage_seq':seq,'entity_key':k,'surface':w})
for k,ws in EXTRA.items():
    if k not in ents: ERR.append('EXTRA dangling '+k); continue
    for w in ws:
        rx=re.compile(w)
        for seq,t in B.items():
            m=rx.search(t)
            if m and (seq,k) not in seen:
                seen.add((seq,k)); mentions.append({'passage_seq':seq,'entity_key':k,'surface':m.group(0).strip()})
mentions.sort(key=lambda m:(m['passage_seq'],m['entity_key']))
sources=[
 {'url':'https://az.lib.ru/g/goncharow_i_a/','title':'И. А. Гончаров. Фрегат «Паллада» (Библиотека Мошкова)','publisher':'az.lib.ru','tier':'primary','lang':'ru','licence':'public domain'},
 {'url':'https://www.wikidata.org/','title':'Wikidata','publisher':'Wikimedia Foundation','tier':'dataset','lang':'en','licence':'CC0'},
 {'url':'https://en.wikipedia.org/wiki/Russian_frigate_Pallada','title':'Russian frigate Pallada','publisher':'Wikipedia','tier':'wiki','lang':'en','licence':'CC BY-SA 4.0'},
 {'url':'https://en.wikipedia.org/wiki/Dejima','title':'Dejima','publisher':'Wikipedia','tier':'wiki','lang':'en','licence':'CC BY-SA 4.0'},
 {'url':'https://en.wikipedia.org/wiki/Shuri_Castle','title':'Shuri Castle','publisher':'Wikipedia','tier':'wiki','lang':'en','licence':'CC BY-SA 4.0'},
]
for l in links:
    for k in (l['from_key'],l['to_key']):
        if k not in ents: ERR.append('dangling link '+k)
for s in stops:
    if s['place_key'] not in ents: ERR.append('dangling stop '+s['place_key'])
    if s['transport_in'] and s['transport_in'] not in ents and s['transport_in'] not in ('foot','horse','boat','sledge','schooner','cart'): ERR.append('transport? '+s['transport_in'])
for f in facts:
    if f['entity_key'] not in ents: ERR.append('dangling fact '+f['entity_key'])
for q in quotes:
    for k in q['entity_keys']:
        if k not in ents: ERR.append('dangling quote '+k)
for e in ents.values():
    if e['parent_key'] and e['parent_key'] not in ents: ERR.append('dangling parent '+e['parent_key'])
# substring check
for r in quotes+links+facts:
    s=r.get('passage_seq'); q=r.get('quote',r.get('text'))
    if s and q not in B[s]: ERR.append('NOT SUBSTR '+q[:40])
def W(name,rows):
    with open(os.path.join(OUT,name+'.jsonl'),'w',encoding='utf8',newline='\n') as fh:
        for r in rows: fh.write(json.dumps(r,ensure_ascii=False)+'\n')
W('entities',list(ents.values()));W('stops',stops);W('entity_links',links);W('mentions',mentions);W('facts',facts);W('quotes',quotes);W('sources',sources)
wd=sum(1 for e in ents.values() if e['wikidata'])
print('entities',len(ents),'wd',wd,f'{100*wd/len(ents):.0f}%','stops',len(stops),'links',len(links),'mentions',len(mentions),'facts',len(facts),'quotes',len(quotes))
from collections import Counter
print(sorted(Counter(q['passage_seq'] for q in quotes).items()))
print(sorted(Counter(e['status'] for e in ents.values()).items()))
print('\n'.join(ERR))
