"""Ajukas tõlketööriist.

Eestikeelne index.html on ainus lähtefail. See skript:
  python tools/i18n.py extract   -> i18n/source.json (kõik tõlgitavad tekstid dokumendi järjekorras)
  python tools/i18n.py build     -> en.html ja ru.html tõlgetest i18n/en.json ja i18n/ru.json
  python tools/i18n.py missing   -> näitab, millised tekstid on tõlkimata (i18n/missing-*.json)
  python tools/i18n.py check     -> kontrollib, et tõlgetes on HTML-sildid, lingid ja {kohatäited} alles

Tõlkefail on sõnastik {eestikeelne tekst: tõlge}. HTML-i sees olevad sildid (<b>, <a href=...> jne)
peavad tõlkes alles jääma. Puuduv tõlge jääb lehel eesti keelde ja ehitus annab sellest teada.
Vajab: pip install beautifulsoup4
"""
import json
import os
import re
import sys

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
I18N = os.path.join(ROOT, 'i18n')
LANGS = {
    'en': {'file': 'en.html', 'locale': 'en_GB'},
    'ru': {'file': 'ru.html', 'locale': 'ru_RU'},
}
SKIP_TAGS = {'script', 'style', 'svg', 'noscript', 'template'}
ATTRS = ['placeholder', 'aria-label', 'title', 'alt', 'data-title', 'data-parent-title']
META = [('name', 'description'), ('property', 'og:title'), ('property', 'og:description'), ('property', 'og:image:alt')]
LETTER = re.compile(r'[A-Za-zÀ-ɏЀ-ӿ]')
JS_T = re.compile(r"\bt\('((?:[^'\\]|\\.)*)'")
JS_FALLBACK = re.compile(r"ERR\[err\.code\] \|\| '((?:[^'\\]|\\.)*)'")
JS_ERR = re.compile(r"'auth/[a-z-]+':\s*'((?:[^'\\]|\\.)*)'")


def norm(x):
    return re.sub(r'\s+', ' ', x).strip()


def inner(el):
    return norm(''.join(str(c) for c in el.contents))


def has_direct_text(el):
    return any(isinstance(c, NavigableString) and not isinstance(c, Comment) and c.strip() for c in el.children)


def text_units(soup):
    out = []

    def walk(el):
        for ch in el.children:
            if getattr(ch, 'name', None) is None or ch.name in SKIP_TAGS:
                continue
            if ch.get('translate') == 'no':
                continue
            if has_direct_text(ch):
                out.append(ch)
            else:
                walk(ch)
    walk(soup.body)
    return [u for u in out if LETTER.search(u.get_text())]


def attr_units(soup):
    for el in soup.body.find_all(True):
        if el.name in SKIP_TAGS or el.find_parent(attrs={'translate': 'no'}) or el.get('translate') == 'no':
            continue
        for a in ATTRS:
            v = el.get(a)
            if isinstance(v, str) and LETTER.search(v):
                yield el, a, v


def meta_units(soup):
    for k, v in META:
        m = soup.find('meta', attrs={k: v})
        if m and m.get('content'):
            yield m
    if soup.title and soup.title.string:
        yield soup.title


def js_keys(soup):
    keys = []
    for sc in soup.find_all('script'):
        if sc.get('type') == 'application/json':
            continue
        code = sc.string or ''
        for rx in (JS_T, JS_FALLBACK, JS_ERR):
            for m in rx.finditer(code):
                keys.append(m.group(1).replace("\\'", "'"))
    return keys


def quiz_data(soup):
    el = soup.find('script', id='quiz-data')
    return el, json.loads(el.string)


def collect(soup):
    keys = []
    keys += [inner(u) for u in text_units(soup)]
    keys += [v for _, _, v in attr_units(soup)]
    keys += [m.get('content') if m.name == 'meta' else m.string for m in meta_units(soup)]
    keys += js_keys(soup)
    _, q = quiz_data(soup)
    for rows in q.values():
        for row in rows:
            keys += row
    seen, ordered = set(), []
    for k in keys:
        k = norm(k)
        if k and k != 'et-EE' and LETTER.search(k) and k not in seen:
            seen.add(k)
            ordered.append(k)
    return ordered


def load_soup():
    with open(SRC, encoding='utf-8') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def load_dict(lang):
    p = os.path.join(I18N, lang + '.json')
    if not os.path.exists(p):
        return {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def extract():
    os.makedirs(I18N, exist_ok=True)
    keys = collect(load_soup())
    with open(os.path.join(I18N, 'source.json'), 'w', encoding='utf-8') as f:
        json.dump(keys, f, ensure_ascii=False, indent=1)
    print(f'{len(keys)} teksti -> i18n/source.json')
    return keys


def missing():
    keys = collect(load_soup())
    total = 0
    for lang in LANGS:
        d = load_dict(lang)
        miss = [k for k in keys if not d.get(k)]
        total += len(miss)
        with open(os.path.join(I18N, f'missing-{lang}.json'), 'w', encoding='utf-8') as f:
            json.dump(miss, f, ensure_ascii=False, indent=1)
        print(f'{lang}: {len(miss)} tõlkimata')
    return total


TAG = re.compile(r'<\s*(/?)\s*([a-zA-Z0-9]+)')
HREF = re.compile(r'\b(?:href|src|for|id|class|data-[a-z-]+)="([^"]*)"')
PH = re.compile(r'\{[a-z]+\}')


def check(langs=None):
    """Kontrollib, et tõlkes on samad HTML-sildid, lingid ja {kohatäited} nagu originaalis."""
    keys = collect(load_soup())
    bad = 0
    for lang in (langs or LANGS):
        d = load_dict(lang)
        for k in keys:
            v = d.get(k)
            if not v:
                continue
            probs = []
            if [m.groups() for m in TAG.finditer(k)] != [m.groups() for m in TAG.finditer(v)]:
                probs.append('HTML-sildid erinevad')
            if sorted(HREF.findall(k)) != sorted(HREF.findall(v)):
                probs.append('atribuudid (href/class/...) erinevad')
            if sorted(PH.findall(k)) != sorted(PH.findall(v)):
                probs.append('{kohatäited} erinevad')
            if probs:
                bad += 1
                print(f'[{lang}] {", ".join(probs)}\n   ET: {k[:160]}\n   {lang.upper()}: {v[:160]}')
        extra = [k for k in d if k not in set(keys)]
        if extra:
            print(f'[{lang}] {len(extra)} tõlget, mille originaali lehel enam pole (võib kustutada)')
    print('OK' if not bad else f'{bad} probleemi')
    return bad


def build():
    keys = collect(load_soup())
    for lang, cfg in LANGS.items():
        d = load_dict(lang)
        tr = lambda k: d.get(norm(k)) or k
        soup = load_soup()
        soup.html['lang'] = lang
        for u in text_units(soup):
            new = d.get(inner(u))
            if new:
                u.clear()
                frag = BeautifulSoup(new, 'html.parser')
                for c in list(frag.contents):
                    u.append(c)
        for el, a, v in list(attr_units(soup)):
            el[a] = tr(v)
        for m in list(meta_units(soup)):
            if m.name == 'meta':
                m['content'] = tr(m['content'])
            else:
                m.string = tr(m.string)
        og_url = soup.find('meta', attrs={'property': 'og:url'})
        if og_url:
            og_url['content'] = og_url['content'].split('#')[0].rstrip('/') + '/' + cfg['file']
        og_loc = soup.find('meta', attrs={'property': 'og:locale'})
        if og_loc:
            og_loc['content'] = cfg['locale']
        el, q = quiz_data(soup)
        for rows in q.values():
            for row in rows:
                row[:] = [tr(x) for x in row]
        el.string = json.dumps(q, ensure_ascii=False).replace('</', '<\\/')
        js = {k: d[k] for k in js_keys(soup) if d.get(k)}
        js['et-EE'] = {'en': 'en-GB', 'ru': 'ru-RU'}[lang]
        for sc in soup.find_all('script'):
            if sc.string and 'window.I18N = {};' in sc.string:
                sc.string = sc.string.replace('window.I18N = {};', 'window.I18N = ' + json.dumps(js, ensure_ascii=False).replace('</', '<\\/') + ';')
        out = str(soup)
        with open(os.path.join(ROOT, cfg['file']), 'w', encoding='utf-8') as f:
            f.write(out)
        miss = [k for k in keys if not d.get(k)]
        print(f"{cfg['file']}: {len(keys) - len(miss)}/{len(keys)} tõlgitud" + (f', {len(miss)} puudu (vt python tools/i18n.py missing)' if miss else ''))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'extract':
        extract()
    elif cmd == 'missing':
        sys.exit(1 if missing() else 0)
    elif cmd == 'build':
        build()
    elif cmd == 'check':
        sys.exit(1 if check(sys.argv[2:] or None) else 0)
    else:
        print(__doc__)
