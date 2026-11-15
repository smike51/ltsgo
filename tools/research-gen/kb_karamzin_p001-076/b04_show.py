import json,re,textwrap
P=r'C:\Users\admin\OneDrive\dev\ltsgo\texts\karamzin-letters\passages.jsonl'
out=open('b04_text.txt','w',encoding='utf8')
for l in open(P,encoding='utf8'):
    d=json.loads(l)
    if 35<=d['seq']<=44:
        out.write('===== %d %s | %s\n'%(d['seq'],d['heading'],d.get('date_in_text')))
        for para in re.split(r'\s*\n\s*',d['body']):
            out.write('\n'.join(textwrap.wrap(para,200))+'\n')
