import json,re,textwrap
P=r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
out=open('text.txt','w',encoding='utf8')
for l in open(P,encoding='utf8'):
    d=json.loads(l)
    if d['seq']<=76:
        out.write('===== %d %s\n'%(d['seq'],d['heading']))
        for para in re.split(r'\s*\n\s*',d['body']):
            out.write('\n'.join(textwrap.wrap(para,220))+'\n')
