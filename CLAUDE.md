# Ajukas: juhend Claude'ile

Ajukas on klassi õppeleht (GitHub Pages, https://nextonu.github.io/ajukas/). Kogu leht on üks fail: `index.html` (HTML, CSS, JS ja küsimuste andmed `<script type="application/json" id="quiz-data">`).

**Vasta alati eesti keeles ja lihtsate sõnadega.** Lehe tekst on 17-aastastele: kui õpetaja slaidil on raske sõna, kirjuta põhitekstis lihtne tähendus ja slaidi sõna sulgudesse.

## Iga muudatuse järel

1. `python -X utf8 tools/teade.py sees` (näitab lehel „Lehte uuendatakse praegu”), lisa `teade.json` commit'i.
2. `git pull --rebase` enne push'i: bot teeb main'i ka ise commit'e.
3. Commit'i sõnum eesti keeles, lõpus `Co-Authored-By: Claude <noreply@anthropic.com>`.
4. Kui kasutaja ütleb, et on valmis: `python tools/teade.py valjas`.
5. Kontrolli, et leht töötab: JS-vigu ei ole, vahekaardid avanevad, telefonis (≈360 px) ei keri tabel külgsuunas.

## Turvalisus (avalik repo!)

- Discordi webhook ja boti parool on ainult GitHubi saladustes (`DISCORD_WEBHOOK`, `AJUKAS_BOT_PASSWORD`). Ära kunagi pane neid faili ega küsi neid.
- eKooli parooli ei küsi ega salvesta kunagi.
- Õpetajate slaide, töölehtede ja töövihiku fotosid **ei laadi üles**. Neist kirjutatakse oma sõnadega ja viidatakse nime järgi vahekaardil „Viited”.
- Lehel ei tohi olla hindeid, isikuandmeid ega klassikaaslaste fotosid.
- Pildid ja helid ainult avalikust omandist (nt NASA, Wikimedia Commons PD). Pildid kausta `pildid/<aine>/`.

## Teemalehe reeglid

- Teema = `<div class="view" id="v-<teema>" data-parent="<aine>" ...>`, vahekaardid on `section role="tabpanel"`.
- **Kõik, mida õpilane ise teeb** (küsimused, proovitöö, ülesanded, mängud, treenerid) on vahekaardi **„Testi ennast”** all `.tmode` režiimidena. **Mitte kunagi eraldi vahekaardina.**
- Vahekaart **„Viited”** on alati viimane: õpetaja materjalid nimega, kasutatud lingid ja `#soovita` kast.
- Ülesanded: `article.exq` (`.task` + `details` lahendusega). Küsimused: quiz-data võti, kirje `[teema, küsimus, vastus]` või `[..., 'lisa']`.
- Lehesisesed lingid vahekaardile: `href="#<paneeli-id>"`.
- `data-updated` muuda ainult **uue sisu** korral (uus teema või suur uus osa), mitte paranduste puhul. Uus sisu teeb avalehe ainekaardi „uueks”.
- „Uuendused” nimekirja (avalehel) lisa ainult tähtsad muudatused.
- Klass `.end` on juba kasutusel (sõnalõpu esiletõst). Ära kasuta seda nime muuks.

## Tööde kuupäevad (TOOD)

- Massiiv `var TOOD = [...]` index.html-is: `{"d": "AAAA-KK-PP", "aine", "mis", "note", "link", "topic"}`.
- Ainult klassi ühised kontrolltööd ja hindelised tööd. **Mitte** igapäevased kodutööd (Opiq jms) ega keelerühmade (inglise, vene) tööd.
- Enne kuupäeva lisamist kontrolli tunniplaani: `python -X utf8 tools/tunnid.py 11-J` (nädalad) ja `python -X utf8 tools/tunnid.py 11-J <nr>`. Kui sel päeval selle aine tundi pole, pane järgmine tund ja kirjuta `note`-i põhjus.
- Kui õpetaja hindamisjuhendis on midagi, mida peab ära andma (konspekt, Moodle'i testid jne), pane see aine lehe `.hind` hoiatuskasti.

## Mida kasutaja EI taha (ära lisa tagasi)

Ainete lühendid, konto statistika, „Viita” nupp, kordamisplaan, mälukaardid (spaced repetition), YMusicu nupud, youtube-nocookie, suurendusklaasiga kursor, × sulgemisnupp joonistel, hall lahenduse tekst.

## Stiil

- Tume teema nagu VS Code. Tähtsad sõnad kollase markeriga (`<b>`), mitte värvilise tekstiga.
- Matemaatikas: valemid heledad (`.mx`), jagamine murruna (`.frac`), tulemused eraldi ridadel, selgita „miks”.
- Keemias: klassikaline struktuurivalem täisnurkadega; „graafiline valem” = joonvalem. Arvutis on joonised teksti kõrval, telefonis all.
- Visuaalsed suured muudatused näita enne kasutajale; väikesed nihked võib kohe üles panna.
