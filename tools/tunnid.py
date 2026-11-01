"""Prindib klassi tunniplaani päevade kaupa (Edupage), et kontrollida tööde kuupäevi. Kasutus: python -X utf8 tools/tunnid.py 11-J  (nädalate nimekiri), python -X utf8 tools/tunnid.py 11-J 137  (selle nädala tunnid)"""
import json, sys, urllib.request

BASE = 'https://perg.edupage.org/timetable/server/'
def call(func, args):
    req = urllib.request.Request(f'{BASE}{func.split(".")[0]}.js?__func={func.split(".")[1]}',
        data=json.dumps({'__args': args, '__gsh': '00000000'}).encode(),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['r']

cls = sys.argv[1]
if len(sys.argv) > 2:
    num = sys.argv[2]
else:
    v = call('ttviewer.getTTViewerData', [None, 2026])['regular']
    for t in v['timetables']:
        print(t['tt_num'], t['text'], t.get('datefrom'))
    sys.exit()
d = call('regulartt.regularttGetData', [None, num])
T = {t['id']: {r['id']: r for r in t.get('data_rows', [])} for t in d['dbiAccessorRes']['tables']}
cid = [k for k, c in T['classes'].items() if c['name'] == cls][0]
out = {}
for card in T['cards'].values():
    les = T['lessons'].get(card['lessonid'])
    if not les or cid not in les['classids'] or not card.get('days'):
        continue
    subj = T['subjects'][les['subjectid']]['name']
    grp = ', '.join(T['groups'][g]['name'] for g in les['groupids'] if g in T['groups'])
    for i, ch in enumerate(card['days']):
        if ch == '1':
            out.setdefault(i, []).append((int(card['period'] or 0), subj, grp))
for i in sorted(out):
    print(['E', 'T', 'K', 'N', 'R', 'L', 'P'][i], '; '.join(f'{p}. {s} [{g}]' for p, s, g in sorted(set(out[i]))))
