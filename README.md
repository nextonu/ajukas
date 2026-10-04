# Ajukas

Kontrolltööde kordamismaterjalid aine ja teema kaupa: https://nextonu.github.io/ajukas/

Kogu leht on üks fail: `index.html`. Koostatud tehisaru abiga, võib sisaldada üksikuid vigu.

## Kontod ja soovitused (Firebase)

Firebase projekt: `ajukas-7be66` (tasuta Spark-pakett). Kontod on kasutajanime ja parooliga (sisemiselt `<nimi>@kasutaja.ajukas.app`), edusammud ja soovitused on Firestore'is.

- Admin-kasutaja `nextonu` näeb avalehel kasti „Saabunud soovitused” ja lehte `#soovitused`; teistele neid ei näidata.
- Turvareeglid on failis `firestore.rules`. Pärast muutmist kopeeri need Firebase konsooli: Firestore → Rules → Publish.
- Manused (kuni 3, igaüks kuni ~700 kB) on alamkogus `soovitused/{id}/manused` ja laaditakse alles siis, kui admin vajutab „Näita”. Firebase Storage nõuaks Blaze-paketti.

## Keeled

Leht on ainult eesti keeles. Inglise ja vene keele versioon (tõlketööriist `tools/i18n.py`, tõlked `i18n/*.json`) on eemaldatud, aga alles git-märgise `keeled-arhiiv` all:

```
git checkout keeled-arhiiv -- tools i18n
```

`en.html` ja `ru.html` suunavad vanad lingid eestikeelsele lehele.
