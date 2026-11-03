"""Avalehe nurga teade „Lehte uuendatakse praegu”.

  python tools/teade.py sees [minutid]   # näita teadet, aegub ise (vaikimisi 15 min pärast)
  python tools/teade.py valjas           # peida kohe ja anna kõigile teada, et lehel on uut (ajukas-ver)
  python tools/teade.py versioon         # ainult ajukas-ver edasi: kõigil tuleb „Värskenda”

Väikeste muudatuste peale ajukas-ver ei muutu, seega tavakasutajad teadet ei näe
(arendusrežiimis näeb admin iga muudatust). Teade tuleb kõigile alles siis, kui ajukas-ver muutub.

Leht näitab teadet ainult siis, kui "aktiivne" on true ja "kuni" pole möödas.
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'teade.json')


def versioon():
    import re
    ip = os.path.join(ROOT, 'index.html')
    s = open(ip, encoding='utf-8', newline='').read()
    v = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M')
    s2, n = re.subn(r'<meta name="ajukas-ver" content="[^"]*">', '<meta name="ajukas-ver" content="' + v + '">', s, count=1)
    assert n == 1, 'ajukas-ver puudub'
    open(ip, 'w', encoding='utf-8', newline='').write(s2)
    print('ajukas-ver', v)


if len(sys.argv) > 1 and sys.argv[1] == 'versioon':
    versioon()
    sys.exit(0)
if len(sys.argv) > 1 and sys.argv[1] == 'valjas':
    versioon()
    d = {'aktiivne': False}
else:
    mins = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    kuni = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=mins)
    d = {'aktiivne': True, 'kuni': kuni.strftime('%Y-%m-%dT%H:%M:%SZ')}
with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(d, f, ensure_ascii=False)
    f.write('\n')
print(d)
