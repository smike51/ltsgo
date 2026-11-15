import json
P=r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
t=0
for l in open(P,encoding='utf8'):
    d=json.loads(l)
    if d['seq']<=76:
        t+=len(d['body'])
        print(d['seq'],d.get('part'),'|',d['heading'],'|',d['date_in_text'],'|',len(d['body']))
print(t)
