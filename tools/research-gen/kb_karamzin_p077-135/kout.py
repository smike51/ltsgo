import sys,json,os,re,time,urllib.request,urllib.parse,urllib.error,importlib
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import lib
for i in range(1,14): importlib.import_module('d%d'%i)
REPO=r'C:\Users\admin\OneDrive\dev\ltsgo'
OUT=os.path.join(REPO,'kb','staging','karamzin-letters','p077-135'); os.makedirs(OUT,exist_ok=True)
C=os.path.join(HERE,'wdk')
MATCH=json.load(open(os.path.join(C,'sp_match.json'),encoding='utf8'))
EN=json.load(open(os.path.join(C,'ents.json'),encoding='utf8'))
OLD=json.load(open(os.path.join(C,'search.json'),encoding='utf8')) if os.path.exists(os.path.join(C,'search.json')) else {}
CB='agent:karamzin-p077-135'; JK='karamzin-1789'; BK='karamzin-letters'
B={}
for l in open(os.path.join(REPO,'texts','karamzin-letters','passages.jsonl'),encoding='utf8'):
    p=json.loads(l); B[p['seq']]=p['body']
HUMAN={'Q5','Q15632617','Q4271324','Q95074','Q15773347','Q178885','Q22988604','Q20643955','Q3658341','Q21070568','Q16979650'}
BADT={'Q4167410','Q13406463','Q4167836','Q11266439','Q17633526','Q15184295'}
def okType(e,i):
    d=EN.get(i)
    if not d: return False
    if BADT & set(d['p31']): return False
    k=e['kind']
    if k=='person': return bool(HUMAN & set(d['p31']))
    if k in ('place','building'): return bool(d['coord']) or bool(d['enwiki'])
    return True
def wlab(i): return EN[i]['labels'].get('en') or EN[i]['labels'].get('ru') or i
SSP=os.path.join(C,'sp_search.json'); SS=json.load(open(SSP,encoding='utf8')) if os.path.exists(SSP) else {}
OVR={'james-thomson':'Q555029','russia':'Q159','rue-d-enfer':'Q48748327'}
NOWD={'oedipe-voltaire','pierre-le-grand-opera','voyage-du-jeune-anacharsis','rosiere-festival','chateau-de-bellevue','repentant-magdalene-le-brun','monument-heart-henri-ii','la-pucelle-voltaire','adelphi-buildings','windsor-forest-poem','kings-theatre','john-barber-mayor','carew-beddington','clarissa','apotheosis-of-hercules'}
PSKIP={'louvre','chateau-de-chantilly','old-bailey','st-james-palace','chiswick-house','syon-house'}  # keyword hit is about another building  # picked from API candidate lists (see audit)
def choose(e):
    if e['key'] in OVR: return OVR[e['key']],[],'ok'
    if e['key'] in NOWD:
        i,raw,how=choose0(e); return None,(SS.get(re.sub(r'\s*\(.*?\)','',e['en']).strip()) or raw),'amb'
    i,raw,how=choose0(e)
    if how=='ok': return i,raw,how
    ss=SS.get(re.sub(r'\s*\(.*?\)','',e['en']).strip()) or []
    f=[x for x in ss[:3] if okType(e,x['id'])]
    if f and f[0]['id']==ss[0]['id']: return f[0]['id'],ss,'ok'
    return None,(f or ss or raw),('amb' if (f or how=='amb') else 'no')
def choose0(e):
    raw={}
    for s_ in (e['search'],e['en']):
        for x in MATCH.get(s_,[]):
            if x['id'] not in raw or x['how']=='enwiki': raw[x['id']]=x
    raw=sorted(raw.values(),key=lambda t:(t['how']!='enwiki',-t['sl']))
    f=[x for x in raw if okType(e,x['id'])]
    if not f: return None,raw,'no'
    ew=[x for x in f if x['how']=='enwiki']
    if len({x['id'] for x in ew})==1: return ew[0]['id'],raw,'ok'
    fl=sorted(f,key=lambda t:-t['sl'])
    if len(fl)==1 or (fl[0]['sl']>=10 and fl[0]['sl']>=3*fl[1]['sl']): return fl[0]['id'],raw,'ok'
    return None,fl,'amb'
def tdate(t,p=11):
    if not t: return None
    p=int(p or 11); sign='-' if t.startswith('-') else ''
    m=re.match(r'-?(\d+)-(\d\d)-(\d\d)',t)
    if not m: return None
    y=m.group(1).lstrip('0').zfill(4)
    if p>=11: return f'{sign}{y}-{m.group(2)}-{m.group(3)}'
    if p==10: return f'{sign}{y}-{m.group(2)}'
    return f'{sign}{y}'
def coord(c):
    m=re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)',c or '')
    return (float(m.group(2)),float(m.group(1))) if m else None
UA={'User-Agent':'LtsgoKB/0.1 (research script; python-urllib)'}
def get(base,params):
    u=base+'?'+urllib.parse.urlencode({**params,'format':'json'})
    for k in range(5):
        try:
            time.sleep(0.4); return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
        except Exception: time.sleep(4*(k+1))
    return {}
ents=[];facts=[];WDURL='https://www.wikidata.org/wiki/'
stat={'ok':0,'amb':0,'no':0,'skip':0}
amb=[]
for e in lib.ENT.values():
    wd=None;note=e['note'];status=e['status']
    if e['search']:
        wd,raw,how=choose(e); stat[how]+=1
        cl='; '.join(f"{x['id']} {wlab(x['id']) if x['id'] in EN else ''} ({(EN.get(x['id'],{}).get('desc',{}).get('en') or '')[:50]})" for x in raw[:3])
        if how=='amb':
            status='unverified'; note=((note+'; ') if note else '')+'Wikidata ambiguous, candidates: '+cl; amb.append(e['key'])
        elif how=='no':
            status=status or ('unverified' if raw else 'book_only')
            if raw: note=((note+'; ') if note else '')+'no Wikidata item of matching type; search gave: '+cl
            else: note=((note+'; ') if note else '')+'no Wikidata match found'
        else:
            status=status or 'verified_wiki'
    else:
        stat['skip']+=1; status=status or 'book_only'
    d=EN.get(wd) if wd else None
    r={'key':e['key'],'kind':e['kind'],'wikidata':wd,'name':{'ru':e['ru'],'en':e['en']},'names_then':e['names_then'],
       'parent_key':e['parent'],'lat':None,'lon':None,'geo_precision':None,'born':None,'died':None,
       'starts':e['kw'].get('starts'),'ends':e['kw'].get('ends'),'preservation':None,'status':status,
       'meta':({'note':note} if note else {}),'created_by':CB}
    if d:
        c=coord(d['coord'])
        if c and e['kind'] in ('place','building','event'):
            r['lat']=round(c[0],5); r['lon']=round(c[1],5)
            r['geo_precision']='exact' if e['kind']=='building' else 'centroid'
        if e['kind']=='person': r['born']=tdate(d['born'],d['bprec']); r['died']=tdate(d['died'],d['dprec'])
        if e['kind'] in ('building','event','organisation','artwork'):
            r['starts']=r['starts'] or tdate(d['start'],9) or tdate(d['inception'],9); r['ends']=r['ends'] or tdate(d['end'],9) or tdate(d['dissolved'],9)
        lab=d['labels'].get('ru') or d['labels'].get('en')
        for lg in ('ru','en'):
            ds=d['desc'].get(lg)
            if ds:
                facts.append({'entity_key':e['key'],'key':'identity.wikidata','layer':'now','lang':lg,'value':ds,'fact_class':'identity',
                    'status':'verified_wiki' if status=='verified_wiki' else 'unverified','source_url':WDURL+wd,'source_title':'Wikidata: '+(lab or wd),
                    'passage_seq':None,'quote':ds,'note':None,'created_by':CB}); break
        if e['kind']=='person' and (r['born'] or r['died']):
            q=f"{r['born'] or '?'} – {r['died'] or '?'}"
            facts.append({'entity_key':e['key'],'key':'identity.life','layer':'now','lang':'en','value':q,'fact_class':'identity',
                'status':'verified_wiki' if status=='verified_wiki' else 'unverified','source_url':WDURL+wd,'source_title':'Wikidata: '+(lab or wd),
                'passage_seq':None,'quote':'P569/P570: '+q,'note':'date of birth / death from Wikidata claims','created_by':CB})
    r['_d']=d
    ents.append(r)
# Wikipedia preservation for buildings
WPC=os.path.join(C,'wp.json'); WP=json.load(open(WPC,encoding='utf8')) if os.path.exists(WPC) else {}
blds=[r for r in ents if r['kind']=='building' and r['_d'] and r['_d']['enwiki']]
titles=[r['_d']['enwiki'] for r in blds if r['_d']['enwiki'] not in WP]
for j in range(0,len(titles),20):
    res=get('https://en.wikipedia.org/w/api.php',{'action':'query','prop':'extracts','exintro':1,'explaintext':1,'exlimit':20,'titles':'|'.join(titles[j:j+20]),'redirects':1})
    q=res.get('query',{}); rd={x['to']:x['from'] for x in q.get('redirects',[])}
    nm={x['to']:x['from'] for x in q.get('normalized',[])}
    for pg in q.get('pages',{}).values():
        t=pg.get('title'); t0=rd.get(t,t); t0=nm.get(t0,t0)
        WP[t0]=pg.get('extract','')
    for t in titles[j:j+20]: WP.setdefault(t,'')
json.dump(WP,open(WPC,'w',encoding='utf8'),ensure_ascii=False)
RULES=[('lost',r'\b(demolished|was destroyed|were destroyed|burned down|burnt down|no longer exists|no longer survives|pulled down|razed)\b'),
       ('ruin',r'\b(ruin|ruins|ruined)\b'),('rebuilt',r'\b(rebuilt|reconstructed|replaced by)\b')]
pres={}
for r in blds:
    t=r['_d']['enwiki']; tx=WP.get(t,'')
    if not tx: continue
    sents=re.split(r'(?<=[.!?])\s+',tx.replace('\n',' '))
    val=None;qs=None;st='verified_wiki'
    for v,rx in ([] if r['key'] in PSKIP else RULES):
        for s in sents:
            if re.search(rx,s,re.I): val=v;qs=s;break
        if val: break
    if not val:
        val='intact';qs=sents[0];st='unverified'
    w=qs.split()
    if len(w)>30: qs=' '.join(w[:30])
    url='https://en.wikipedia.org/wiki/'+urllib.parse.quote(t.replace(' ','_'))
    r['preservation']=val; pres[val]=pres.get(val,0)+1
    facts.append({'entity_key':r['key'],'key':'preservation','layer':'now','lang':'en','value':val,'fact_class':'preservation',
        'status':st if r['status']=='verified_wiki' else 'unverified','source_url':url,'source_title':'Wikipedia: '+t,'passage_seq':None,'quote':qs,
        'note':('keyword match' if st=='verified_wiki' else 'no demolition/ruin/rebuild wording in the lead; intact inferred, needs check'),'created_by':CB})
for r in ents: r.pop('_d')
# book facts
for f in lib.FACTS:
    x={'key':f['key'],'layer':'then','lang':'ru','value':f['value'],'fact_class':f['fc'],'status':'book_only',
       'source_url':None,'source_title':'Н. М. Карамзин. Письма русского путешественника','passage_seq':f['seq'],'quote':f['quote'],'note':f['note'],'created_by':CB}
    if f['entity_key']: x={'entity_key':f['entity_key'],**x}
    else: x={'book_key':BK,**x}
    facts.append(x)
# stops
st=sorted(enumerate(lib.STOPS),key=lambda t:(t[1]['passage_from'],t[0]))
stops=[];sref={}
for n,(i,s) in enumerate(st):
    hint=770+n
    stops.append({'journey_key':JK,'seq_hint':hint,'place_key':s['place_key'],'arrived':s['arrived'],'departed':s['departed'],'calendar':'julian',
        'date_precision':s['date_precision'],'date_in_text':s['date_in_text'],'transport_in':s['transport_in'],'passage_from':s['passage_from'],
        'passage_to':s['passage_to'],'kind':s['kind'],'status':'book_only','note':s['note']})
def stopref(seq):
    best=None
    for s in stops:
        if s['passage_from']<=seq<=s['passage_to'] and s['kind']!='mention_only':
            if best is None or (s['passage_to']-s['passage_from'])<(best['passage_to']-best['passage_from']): best=s
    return f"{JK}:{best['seq_hint']}:{best['place_key']}" if best else None
links=[{'from_key':l['from_key'],'to_key':l['to_key'],'kind':l['kind'],'passage_seq':l['passage_seq'],'during':l['during'] or stopref(l['passage_seq']),
        'status':'book_only','quote':l['quote'],'note':l['note']} for l in lib.LINKS]
seen=set();mentions=[]
for m in lib.MENT:
    k=(m['passage_seq'],m['entity_key'],m['surface'])
    if k in seen: continue
    seen.add(k); mentions.append(m)
quotes=[{'passage_seq':q['passage_seq'],'text':q['text'],'stop_ref':stopref(q['passage_seq']),'entity_keys':q['entity_keys'],'tags':q['tags']} for q in lib.QUOTES]
sources=[{'url':'http://az.lib.ru/k/karamzin_n_m/text_0320.shtml','title':'Н. М. Карамзин. Письма русского путешественника (Библиотека Мошкова)','publisher':'az.lib.ru','tier':'primary','lang':'ru','licence':'public domain'},
         {'url':'https://www.wikidata.org/','title':'Wikidata','publisher':'Wikimedia Foundation','tier':'dataset','lang':'en','licence':'CC0'}]
for u in sorted({f['source_url'] for f in facts if f.get('source_url','') and 'wikipedia' in f['source_url']}):
    sources.append({'url':u,'title':urllib.parse.unquote(u.rsplit('/',1)[1]).replace('_',' '),'publisher':'Wikipedia','tier':'wiki','lang':'en','licence':'CC BY-SA 4.0'})
def W(n,rows):
    with open(os.path.join(OUT,n+'.jsonl'),'w',encoding='utf8',newline='\n') as fh:
        for r in rows: fh.write(json.dumps(r,ensure_ascii=False)+'\n')
W('entities',ents);W('stops',stops);W('entity_links',links);W('mentions',mentions);W('facts',facts);W('quotes',quotes);W('sources',sources)
withwd=sum(1 for r in ents if r['wikidata'])
print('stat',stat,'pres',pres)
print('ent',len(ents),'wd',withwd,'%.0f%%'%(100*withwd/len(ents)),'searchable',sum(1 for e in lib.ENT.values() if e['search']))
print('stops',len(stops),'links',len(links),'mentions',len(mentions),'facts',len(facts),'quotes',len(quotes),'sources',len(sources))
print('amb',amb)
