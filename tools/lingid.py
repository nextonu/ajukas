"""Kontrollib kõik index.html välislingid ja YouTube'i/Spotify lood.

Kasutus:  python tools/lingid.py        (prindib ainult katkised ja kahtlased)
          python tools/lingid.py -v     (prindib kõik)
"""
import json, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36'
html = open('index.html', encoding='utf-8').read()

urls = set(u.replace('&amp;', '&') for u in re.findall(r'href="(https?://[^"]+)"', html) if "'" not in u)
urls |= set('https://www.youtube.com/watch?v=' + v for v in re.findall(r'\{ v: "([\w-]{11})"', html))
base = re.search(r'data-base="(https://archive\.org/download/[^"]+)" data-files="([^"]+)"', html)
if base:
    urls |= set(base.group(1) + f for f in base.group(2).split())
urls |= set(re.findall(r'"(https://archive\.org/download/[^"]+)"', html))


def get(url, method='GET', rng=True):
    h = {'User-Agent': UA}
    if rng: h['Range'] = 'bytes=0-1023'
    req = urllib.request.Request(url, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status


def check(url):
    host = urllib.parse.urlparse(url).netloc
    try:
        if ('youtube.com' in host or 'youtu.be' in host) and '/results' not in url:
            o = 'https://www.youtube.com/oembed?format=json&url=' + urllib.parse.quote(url, safe='')
            try:
                get(o)
                return url, 'ok', ''
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    return url, 'ok', 'video on olemas, aga lehe sisse panna ei luba'
                return url, 'KATKI', f'YouTube {e.code}: video on kustutatud või privaatne'
        if 'open.spotify.com' in host:
            get('https://open.spotify.com/oembed?url=' + urllib.parse.quote(url, safe=''))
            return url, 'ok', ''
        try:
            get(url, 'HEAD')
        except urllib.error.HTTPError:
            get(url, rng=False)  # osa lehti vastab HEAD-ile või osalisele päringule valesti
        return url, 'ok', ''
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return url, 'kontrolli', f'{e.code}: leht keelab automaatse kontrolli, ava käsitsi'
        return url, 'KATKI', f'HTTP {e.code}'
    except Exception as e:
        return url, 'kontrolli', f'{type(e).__name__}: {str(e)[:80]}'


with ThreadPoolExecutor(12) as ex:
    res = sorted(ex.map(check, sorted(urls)), key=lambda r: (r[1] == 'ok', r[1], r[0]))

verbose = '-v' in sys.argv
bad = 0
for url, st, note in res:
    if st != 'ok' or verbose:
        print(f'{st:9} {url}' + (f'  ({note})' if note else ''))
    bad += st == 'KATKI'
print(f'\nKokku {len(res)} linki: {sum(r[1] == "ok" for r in res)} korras, {bad} katki, {sum(r[1] == "kontrolli" for r in res)} vaja käsitsi vaadata.')
sys.exit(1 if bad else 0)
