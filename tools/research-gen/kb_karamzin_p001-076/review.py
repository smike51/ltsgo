import json, os, glob
BASE = os.path.dirname(os.path.abspath(__file__))
ENT = {}
def E(key, kind, ru, en, q=None, wd=None, **kw):
    if key not in ENT: ENT[key] = (kind, ru, q)
noop = lambda *a, **k: None
g = dict(E=E, S=noop, L=noop, F=noop, Q=noop, M=noop)
for f in sorted(glob.glob(os.path.join(BASE, 'b[0-9]*.py'))): exec(open(f, encoding='utf8').read(), g)
res = json.load(open(os.path.join(BASE, 'wd_auto.json'), encoding='utf8'))
with open(os.path.join(BASE, 'review.txt'), 'w', encoding='utf8') as fh:
    for k, r in res.items():
        kind, ru, q = ENT[k]
        if r['id']:
            fh.write(f"{k}|{kind[:2]}|{ru[:40]}|{r['id']}|{(r.get('label') or '')[:35]}|{(r.get('desc') or '')[:50]}{' !GUESS' if r.get('wd_guess_mismatch') else ''}\n")
        else:
            fh.write(f"{k}|{kind[:2]}|{ru[:40]}|NONE|{'; '.join(c[:40] for c in r['cands'][:3])}\n")
print(len(res))
