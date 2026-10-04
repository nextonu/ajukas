# Ajukas

Kontrolltööde kordamismaterjalid aine ja teema kaupa: https://nextonu.github.io/ajukas/

Kogu leht on üks fail: `index.html`. Koostatud tehisaru abiga, võib sisaldada üksikuid vigu.

## Kontod ja soovitused (Firebase)

Kuni `index.html`-is on `FIREBASE_CONFIG = null`, töötab leht ilma kontodeta ja edusammud jäävad meelde ainult brauseris.

Seadistamine:
1. https://console.firebase.google.com → **Create a project** (nimi nt `ajukas`, Google Analytics võib välja lülitada).
2. **Build → Authentication → Get started → Sign-in method → Email/Password → Enable** (ainult esimene lüliti).
3. **Authentication → Users → Add user**: e-post `nextonu@kasutaja.ajukas.app`, parool enda valitud. See on admin-konto, mis näeb soovitusi. Lehel logid sisse kasutajanimega `nextonu`.
4. **Authentication → Settings → Authorized domains → Add domain**: `nextonu.github.io`.
5. **Build → Firestore Database → Create database** (asukoht `eur3`, *production mode*).
6. **Firestore → Rules**: kopeeri sinna faili `firestore.rules` sisu → **Publish**.
7. **Project settings (hammasratas) → Your apps → `</>` (Web)** → registreeri äpp → kopeeri `firebaseConfig` objekt ja pane see `index.html`-is `FIREBASE_CONFIG` väärtuseks.

Firebase'i veebikonfiguratsioon ei ole saladus, selle võib avalikku reposse panna. Turvalisuse tagavad `firestore.rules` reeglid.
