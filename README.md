# Ajukas

Kontrolltööde kordamismaterjalid aine ja teema kaupa: https://nextonu.github.io/ajukas/

Kogu leht on üks fail: `index.html`. Koostatud tehisaru abiga, võib sisaldada üksikuid vigu.

## Kontod ja soovitused (Firebase)

Firebase projekt: `ajukas-7be66` (tasuta Spark-pakett). Kontod on kasutajanime ja parooliga (sisemiselt `<nimi>@kasutaja.ajukas.app`), edusammud ja soovitused on Firestore'is.

- Admin-kasutaja `nextonu` näeb avalehel kasti „Saabunud soovitused” ja lehte `#soovitused`; teistele neid ei näidata.
- Turvareeglid on failis `firestore.rules`. Pärast muutmist kopeeri need Firebase konsooli: Firestore → Rules → Publish.
- Manused salvestatakse soovituse sisse (kuni 3, kokku alla ~600 kB), sest Firebase Storage nõuaks Blaze-paketti.

## Keeled (eesti, inglise, vene)

`index.html` on eestikeelne lähtefail. `en.html` ja `ru.html` tehakse sellest tööriistaga, neid käsitsi ei muudeta.

```
pip install beautifulsoup4
python tools/i18n.py extract   # i18n/source.json: kõik tõlgitavad tekstid
python tools/i18n.py missing   # mis on tõlkimata (i18n/missing-*.json)
python tools/i18n.py check     # kas tõlgetes on HTML-sildid, lingid ja {kohatäited} alles
python tools/i18n.py build     # teeb en.html ja ru.html
```

Tõlked on failides `i18n/en.json` ja `i18n/ru.json` (`{eestikeelne tekst: tõlge}`). JavaScripti tekstid käivad läbi funktsiooni `t('…')`, testiküsimused on plokis `<script id="quiz-data">`. Keel ja teema (hele/tume) on hammasrattamenüüs paremal üleval ning jäävad brauserisse meelde.
