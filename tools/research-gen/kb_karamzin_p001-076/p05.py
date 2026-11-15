import json,re,textwrap
P=r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
out=open('t05.txt','w',encoding='utf8')
for l in open(P,encoding='utf8'):
    d=json.loads(l)
    if 45<=d['seq']<=62:
        out.write('===== %d %s\n'%(d['seq'],d['heading']))
        for para in re.split(r'\s*\n\s*',d['body']):
            out.write('\n'.join(textwrap.wrap(para,200))+'\n')
