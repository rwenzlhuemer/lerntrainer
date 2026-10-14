// Offline-Cache. Erzeugt von tools/build.py aus tools/sw_vorlage.js – app/sw.js nicht bearbeiten.
const VERSION = "__VERSION__";
const CACHE = "lerntrainer-" + VERSION;
const DATEIEN = __DATEIEN__;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(DATEIEN)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((namen) => Promise.all(namen.filter((n) => n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// Zuerst aus dem Cache (offline-fest); was fehlt, aus dem Netz.
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((treffer) => treffer || fetch(e.request))
  );
});
