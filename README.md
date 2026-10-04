# Ajukas

Kontrolltööde kordamismaterjalid aine ja teema kaupa: https://nextonu.github.io/ajukas/

Kogu leht on üks fail: `index.html`. Koostatud tehisaru abiga, võib sisaldada üksikuid vigu.

## Kontod ja soovitused (Firebase)

Firebase projekt: `ajukas-7be66` (tasuta Spark-pakett). Kontod on kasutajanime ja parooliga (sisemiselt `<nimi>@kasutaja.ajukas.app`), edusammud ja soovitused on Firestore'is.

- Admin-kasutaja `nextonu` näeb avalehel kasti „Saabunud soovitused” ja lehte `#soovitused`; teistele neid ei näidata.
- Turvareeglid on failis `firestore.rules`. Pärast muutmist kopeeri need Firebase konsooli: Firestore → Rules → Publish.
- Manused salvestatakse soovituse sisse (kuni 3, kokku alla ~600 kB), sest Firebase Storage nõuaks Blaze-paketti.
