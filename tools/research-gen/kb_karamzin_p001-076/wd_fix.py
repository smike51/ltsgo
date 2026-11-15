import json, urllib.request, urllib.parse, time, sys
UA = 'ltsgo-kb-bot/0.1 (literary travel guide research)'
S = dict(l.split('=', 1) for l in open(sys.argv[1], encoding='utf8').read().strip().splitlines())
vals = ' '.join(f'("{k}" "{v}")' for k, v in S.items())
Q = '''SELECT ?k ?item ?ord ?l ?d WHERE { VALUES (?k ?s) { %s }
 SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch"; mwapi:search ?s; mwapi:language "%s"; mwapi:limit "5".
 ?item wikibase:apiOutputItem mwapi:item. ?ord wikibase:apiOrdinal true. }
 OPTIONAL { ?item rdfs:label ?l FILTER(lang(?l)='en') } OPTIONAL { ?item schema:description ?d FILTER(lang(?d)='en') } }''' % (vals, sys.argv[2])
req = urllib.request.Request('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query': Q, 'format': 'json'}).encode(),
                             headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
d = json.load(urllib.request.urlopen(req, timeout=90))
rows = sorted(d['results']['bindings'], key=lambda b: (b['k']['value'], int(b['ord']['value'])))
for b in rows:
    print(b['k']['value'], b['item']['value'].rsplit('/', 1)[1], '|', b.get('l', {}).get('value', ''), '|', b.get('d', {}).get('value', '')[:70])
