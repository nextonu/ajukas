// Ajukase service worker: leht töötab ka ilma internetita.
// Alati proovitakse enne võrku (nii tulevad uuendused kohe), võrgu puudumisel antakse viimane salvestatud versioon.
const CACHE = 'ajukas-v1';
// 'ajukas-audio': audioraamatu allalaaditud peatükid (leht haldab ise), seda ei kustutata
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'og.png', 'qr.svg', 'tunniplaan.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE && k !== 'ajukas-audio').map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // Firebase, Edupage jm käivad otse
  e.respondWith(
    // no-cache: küsi serverilt alati üle, kas fail on muutunud (muidu võib brauser 10 min vana koopiat näidata)
    fetch(req, { cache: 'no-cache' }).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then((hit) => hit || (req.mode === 'navigate' ? caches.match('./') : undefined)))
  );
});

// Audioraamatu taustal allalaadimine (Background Fetch): valmis peatükid vahemällu 'ajukas-audio'
async function keepAudio(e) {
  const c = await caches.open('ajukas-audio');
  let n = 0;
  for (const r of await e.registration.matchAll()) {
    try {
      const res = await r.responseReady;
      if (res && res.status === 200) {
        await c.put(r.request.url, new Response(res.body, { headers: res.headers.get('Content-Length') ? { 'Content-Type': 'audio/mpeg', 'Content-Length': res.headers.get('Content-Length') } : { 'Content-Type': 'audio/mpeg' } }));
        n++;
      }
    } catch (x) {}
  }
  for (const cl of await self.clients.matchAll({ includeUncontrolled: true })) cl.postMessage({ type: 'ajukas-audio' });
  return n;
}
self.addEventListener('backgroundfetchsuccess', (e) => {
  e.waitUntil(keepAudio(e).then(() => e.updateUI({ title: 'Audioraamat on alla laaditud ✓' })));
});
self.addEventListener('backgroundfetchfail', (e) => {
  e.waitUntil(keepAudio(e).then((n) => e.updateUI({ title: n ? 'Osa peatükke laaditi alla (' + n + ')' : 'Allalaadimine ebaõnnestus' })));
});
// peatatud: juba valmis peatükid jäävad alles
self.addEventListener('backgroundfetchabort', (e) => { e.waitUntil(keepAudio(e)); });
self.addEventListener('backgroundfetchclick', (e) => {
  e.waitUntil(self.clients.matchAll({ type: 'window' }).then((l) => (l.length ? l[0].focus() : self.clients.openWindow('./#dorian'))));
});
