import json,sys,re
P=r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
a,b=int(sys.argv[1]),int(sys.argv[2])
for l in open(P,encoding='utf8'):
    d=json.loads(l)
    if a<=d['seq']<=b:
        print('=====',d['seq'],d['heading'])
        print(re.sub(r'\s*\n\s*','\n',d['body']))
