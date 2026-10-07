"""Kontrollib PERG-i Edupage'ist, mis on kõige uuem tunniplaan, ja kirjutab selle faili tunniplaan.json.

Leht ise ei saa Edupage'ist andmeid küsida (Edupage ei luba teistelt lehtedelt päringuid),
seega teeb seda GitHub Actions iga paari tunni tagant (.github/workflows/tunniplaan.yml).
Käsitsi: python tools/tunniplaan.py
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = 'https://perg.edupage.org/timetable/server/'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tunniplaan.json')


def call(func, args):
    req = urllib.request.Request(
        f'{BASE}{func.split(".")[0]}.js?__func={func.split(".")[1]}',
        data=json.dumps({'__args': args, '__gsh': '00000000'}).encode(),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Ajukas tunniplaani kontroll)'})
    # Edupage vastab GitHubi serveritele vahel aeglaselt või veaga: proovi kuni 3 korda
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)['r']
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, KeyError) as e:
            if attempt == 2:
                raise
            print(f'Edupage ei vastanud ({e}), proovin uuesti…')
            time.sleep(15 * (attempt + 1))


def main():
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).date()  # Eesti aeg (piisav täpsus)
    year = today.year if today.month >= 8 else today.year - 1
    viewer = call('ttviewer.getTTViewerData', [None, year])
    reg = viewer['regular']
    tts = [t for t in reg['timetables'] if not t.get('hidden')]
    # uusim nädal, mis on juba alanud või algab 2 päeva jooksul (nädalavahetusel järgmine nädal)
    cands = [t for t in tts if dt.date.fromisoformat(t['datefrom']) <= today + dt.timedelta(days=2)]
    best = max(cands, key=lambda t: t['datefrom']) if cands else None
    num = best['tt_num'] if best else reg.get('default_num')
    text = best['text'] if best else ''
    data = call('regulartt.regularttGetData', [None, num])
    classes = [t for t in data['dbiAccessorRes']['tables'] if t['id'] == 'classes'][0]['data_rows']
    out = {
        'num': num,
        'default_num': reg.get('default_num'),
        'text': text,
        'datefrom': best['datefrom'] if best else None,
        'classes': {c['name']: c['id'] for c in classes},
    }
    old = None
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
        old.pop('checked', None)
    if old == out:
        print('muutusi pole:', num, text)
        return
    out['checked'] = today.isoformat()
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('uuendatud:', num, text, len(out['classes']), 'klassi')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # Edupage maas: jäta vana tunniplaan alles, ära märgi tööd ebaõnnestunuks
        print(f'::warning::Tunniplaani ei õnnestunud kontrollida ({e}). Vana tunniplaan jääb alles.')
        sys.exit(0)
