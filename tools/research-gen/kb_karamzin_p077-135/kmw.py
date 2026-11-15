import sys,json,os,time,urllib.request,urllib.parse,urllib.error
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from ksparql_lib import sparql
C=os.path.join(HERE,'wdk')
P=os.path.join(C,'sp_search.json'); SS=json.load(open(P,encoding='utf8')) if os.path.exists(P) else {}
todo=[l.strip() for l in open(sys.argv[1],encoding='utf8') if l.strip()]
for s in todo:
    if s in SS: continue
    lit=s.replace('\\','\\\\').replace('"','\\"')
    q='''SELECT ?item ?num ?sl WHERE { SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch";
 mwapi:search "%s"; mwapi:language "en"; mwapi:limit "5". ?item wikibase:apiOutputItem mwapi:item. ?num wikibase:apiOrdinal true. }
 OPTIONAL{?item wikibase:sitelinks ?sl} } ORDER BY ?num'''%lit
    r=sparql(q)
    if r is None: print('FAIL',s,flush=True); continue
    SS[s]=[{'id':x['item']['value'].rsplit('/',1)[1],'how':'search','sl':int(x['sl']['value']) if 'sl' in x else 0} for x in r]
    json.dump(SS,open(P,'w',encoding='utf8'),ensure_ascii=False)
print('done',len(SS))
