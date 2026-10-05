"""Avalehe nurga teade „Lehte uuendatakse praegu”.

  python tools/teade.py sees [minutid]   # näita teadet, aegub ise (vaikimisi 15 min pärast)
  python tools/teade.py valjas           # peida kohe

Leht näitab teadet ainult siis, kui "aktiivne" on true ja "kuni" pole möödas.
"""
import datetime as dt
import json
import os
import sys

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'teade.json')

if len(sys.argv) > 1 and sys.argv[1] == 'valjas':
    d = {'aktiivne': False}
else:
    mins = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    kuni = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=mins)
    d = {'aktiivne': True, 'kuni': kuni.strftime('%Y-%m-%dT%H:%M:%SZ')}
with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False)
    f.write('\n')
print(d)
