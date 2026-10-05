"""Saadab uued Ajukase soovitused Discordi.

Käivitab GitHub Actions (.github/workflows/teavita.yml) iga 5 minuti tagant.
Vajab GitHubi salajasi väärtusi (Settings → Secrets and variables → Actions):
  DISCORD_WEBHOOK       – Discordi webhooki aadress
  AJUKAS_BOT_PASSWORD   – Firebase'i kasutaja teavitaja@kasutaja.ajukas.app parool
Teavitaja konto saab firestore.rules järgi ainult soovitusi lugeda ja märkida need teavitatuks.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API_KEY = 'AIzaSyD4tAFZAiOhCyqvJ9XYNTlRZurorvdLfVw'  # avalik veebivõti, sama mis lehel
PROJECT = 'ajukas-7be66'
BOT_EMAIL = 'teavitaja@kasutaja.ajukas.app'
DOCS = f'https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents'
SITE = 'https://nextonu.github.io/ajukas/#soovitused'
MAX_MESSAGES = 5          # rohkem korraga ei saadeta (rämpsu korral tuleb üks kokkuvõte)
FRESH = dt.timedelta(hours=6)  # vanemaid soovitusi ei teavitata, ainult märgitakse teavitatuks


def req(url, data=None, method=None, token=None):
    h = {'Content-Type': 'application/json'}
    if token:
        h['Authorization'] = 'Bearer ' + token
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        body = resp.read()
        return json.loads(body) if body else {}


def discord(hook, payload):
    payload['allowed_mentions'] = {'parse': []}  # @everyone jms ei tööta
    r = urllib.request.Request(hook, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'Ajukas-teavitaja'})
    urllib.request.urlopen(r, timeout=30).read()


def val(f, key, default=''):
    v = f.get(key)
    if not v:
        return default
    for k in ('stringValue', 'timestampValue', 'booleanValue', 'integerValue'):
        if k in v:
            return v[k]
    if 'arrayValue' in v:
        return v['arrayValue'].get('values', [])
    return default


def main():
    hook = os.environ.get('DISCORD_WEBHOOK', '').strip()
    pw = os.environ.get('AJUKAS_BOT_PASSWORD', '').strip()
    if not hook or not pw:
        print('DISCORD_WEBHOOK või AJUKAS_BOT_PASSWORD puudub, jätan vahele.')
        return
    token = req(f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}',
                {'email': BOT_EMAIL, 'password': pw, 'returnSecureToken': True})['idToken']
    rows = req(f'{DOCS}:runQuery', {'structuredQuery': {
        'from': [{'collectionId': 'soovitused'}],
        'orderBy': [{'field': {'fieldPath': 'aeg'}, 'direction': 'DESCENDING'}],
        'limit': 30}}, token=token)
    new = []
    for row in rows:
        d = row.get('document')
        if not d:
            continue
        f = d.get('fields', {})
        if val(f, 'teavitatud', False) is True:
            continue
        new.append((d['name'], f))
    new.reverse()  # vanemad enne
    now = dt.datetime.now(dt.timezone.utc)
    fresh = []
    for name, f in new:
        t = val(f, 'aeg')
        try:
            when = dt.datetime.fromisoformat(t.replace('Z', '+00:00'))
        except Exception:
            when = now
        if now - when <= FRESH and not f.get('kustutatud', {}).get('timestampValue'):
            fresh.append((name, f, when))
    for name, f, when in fresh[:MAX_MESSAGES]:
        tekst = val(f, 'tekst')[:1800]
        nimi = val(f, 'nimi') or 'Anonüümne'
        failid = len(val(f, 'failid', []))
        embed = {'title': 'Uus soovitus Ajukases', 'url': SITE, 'description': tekst, 'color': 0xEAB308,
                 'fields': [{'name': 'Saatja', 'value': nimi[:100], 'inline': True}],
                 'timestamp': when.isoformat()}
        if failid:
            embed['fields'].append({'name': 'Failid', 'value': f'{failid} (vaata lehelt)', 'inline': True})
        discord(hook, {'username': 'Ajukas', 'embeds': [embed]})
    if len(fresh) > MAX_MESSAGES:
        discord(hook, {'username': 'Ajukas', 'content': f'… ja veel {len(fresh) - MAX_MESSAGES} soovitust. Vaata kõiki: {SITE}'})
    for name, f in new:
        req(f'https://firestore.googleapis.com/v1/{name}?updateMask.fieldPaths=teavitatud',
            {'fields': {'teavitatud': {'booleanValue': True}}}, method='PATCH', token=token)
    print(f'teavitatud: {min(len(fresh), MAX_MESSAGES)}, märgitud: {len(new)}')


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as e:
        print('HTTP viga', e.code, e.read()[:300])
        sys.exit(1)
