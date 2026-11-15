import json,textwrap
out=open('t06.txt','w',encoding='utf8')
for l in open(r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl',encoding='utf8'):
    d=json.loads(l)
    if 63<=d['seq']<=76:
        out.write(f"\n=== SEQ {d['seq']} | {d['heading']} | {d['date_in_text']} | len {len(d['body'])}\n")
        for para in d['body'].split('\n'):
            out.write(textwrap.fill(para,200)+'\n')
