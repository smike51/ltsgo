import sys,json,os,time,urllib.request,urllib.parse,urllib.error,importlib
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import lib
for i in range(1,14): importlib.import_module('d%d'%i)
C=os.path.join(HERE,'wdk'); os.makedirs(C,exist_ok=True)
UA={'User-Agent':'LtsgoKB/0.1 (research script; python-urllib)','Accept':'application/sparql-results+json'}
def sparql(q):
    for k in range(8):
        try:
            time.sleep(1)
            req=urllib.request.Request('https://query.wikidata.org/sparql',data=urllib.parse.urlencode({'query':q}).encode(),headers={**UA,'Content-Type':'application/x-www-form-urlencoded'})
            return json.load(urllib.request.urlopen(req,timeout=90))['results']['bindings']
        except urllib.error.HTTPError as e:
            ra=e.headers.get('Retry-After'); w=int(ra) if ra and ra.isdigit() else 15*(k+1)
            print('http',e.code,w,flush=True); time.sleep(min(w,120))
        except Exception as ex:
            print('err',ex,flush=True); time.sleep(10)
    return None
def lit(s): return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"@en'
strings=set()
for e in lib.ENT.values():
    if e['search']:
        strings.add(e['search']); strings.add(e['en'])
strings=sorted(strings)
P1=os.path.join(C,'sp_match.json')
MATCH=json.load(open(P1,encoding='utf8')) if os.path.exists(P1) else {}
todo=[s for s in strings if s not in MATCH]
for j in range(0,len(todo),8):
    b=todo[j:j+8]
    vals=' '.join(lit(s_) for s_ in b)
    ok=True; rows=[]
    for how,pat in (('label','?item rdfs:label ?s .'),('enwiki','?art schema:name ?s ; schema:isPartOf <https://en.wikipedia.org/> ; schema:about ?item .')):
        r=sparql('SELECT ?s ?item ?sl WHERE { VALUES ?s { %s } %s ?item wikibase:sitelinks ?sl . }'%(vals,pat))
        if r is None: ok=False; break
        for x in r: x['how']={'value':how}
        rows+=r
    if not ok: print('FAIL batch',j,flush=True); continue
    for s_ in b: MATCH[s_]=[]
    for x in rows:
        MATCH[x['s']['value']].append({'id':x['item']['value'].rsplit('/',1)[1],'how':x['how']['value'],'sl':int(x['sl']['value'])})
    json.dump(MATCH,open(P1,'w',encoding='utf8'),ensure_ascii=False)
    print('match',j+len(b),'/',len(todo),flush=True)
# details: only items with >0 sitelinks, cap per string top 6 by sitelinks
ids=set()
SSP=os.path.join(C,'sp_search.json')
SSD=json.load(open(SSP,encoding='utf8')) if os.path.exists(SSP) else {}
for v in list(MATCH.values())+[x[:4] for x in SSD.values()]:
    for x in sorted(v,key=lambda t:-t['sl'])[:6]: ids.add(x['id'])
P2=os.path.join(C,'ents.json')
EN=json.load(open(P2,encoding='utf8')) if os.path.exists(P2) else {}
need=sorted(i for i in ids if i not in EN)
for j in range(0,len(need),60):
    b=need[j:j+60]
    q='''SELECT ?item (GROUP_CONCAT(DISTINCT ?p31;separator="|") AS ?p31s) (SAMPLE(?coord) AS ?c) (SAMPLE(?bt) AS ?born) (SAMPLE(?bp) AS ?bprec)
 (SAMPLE(?dt) AS ?died) (SAMPLE(?dp) AS ?dprec) (SAMPLE(?inc) AS ?inception) (SAMPLE(?dis) AS ?dissolved) (SAMPLE(?st) AS ?start) (SAMPLE(?en) AS ?end)
 (SAMPLE(?le) AS ?labEn) (SAMPLE(?lr) AS ?labRu) (SAMPLE(?de) AS ?descEn) (SAMPLE(?dr) AS ?descRu) (SAMPLE(?t) AS ?enwiki) (SAMPLE(?tr) AS ?ruwiki) WHERE {
 VALUES ?item { %s }
 OPTIONAL{?item wdt:P31 ?p31} OPTIONAL{?item wdt:P625 ?coord}
 OPTIONAL{?item p:P569/psv:P569 [wikibase:timeValue ?bt; wikibase:timePrecision ?bp]}
 OPTIONAL{?item p:P570/psv:P570 [wikibase:timeValue ?dt; wikibase:timePrecision ?dp]}
 OPTIONAL{?item wdt:P571 ?inc} OPTIONAL{?item wdt:P576 ?dis} OPTIONAL{?item wdt:P580 ?st} OPTIONAL{?item wdt:P582 ?en}
 OPTIONAL{?item rdfs:label ?le FILTER(lang(?le)="en")} OPTIONAL{?item rdfs:label ?lr FILTER(lang(?lr)="ru")}
 OPTIONAL{?item schema:description ?de FILTER(lang(?de)="en")} OPTIONAL{?item schema:description ?dr FILTER(lang(?dr)="ru")}
 OPTIONAL{?a schema:about ?item; schema:isPartOf <https://en.wikipedia.org/>; schema:name ?t}
 OPTIONAL{?ar schema:about ?item; schema:isPartOf <https://ru.wikipedia.org/>; schema:name ?tr}
} GROUP BY ?item'''%(' '.join('wd:'+i for i in b))
    r=sparql(q)
    if r is None: print('FAIL det',j,flush=True); continue
    for x in r:
        g=lambda k:x[k]['value'] if k in x else None
        i=g('item').rsplit('/',1)[1]
        EN[i]={'p31':[p.rsplit('/',1)[1] for p in (g('p31s') or '').split('|') if p],'coord':g('c'),'born':g('born'),'bprec':g('bprec'),
               'died':g('died'),'dprec':g('dprec'),'inception':g('inception'),'dissolved':g('dissolved'),'start':g('start'),'end':g('end'),
               'labels':{k:v for k,v in (('en',g('labEn')),('ru',g('labRu'))) if v},'desc':{k:v for k,v in (('en',g('descEn')),('ru',g('descRu'))) if v},
               'enwiki':g('enwiki'),'ruwiki':g('ruwiki')}
    json.dump(EN,open(P2,'w',encoding='utf8'),ensure_ascii=False)
    print('det',j+len(b),'/',len(need),flush=True)
print('done',len(MATCH),len(EN),flush=True)
