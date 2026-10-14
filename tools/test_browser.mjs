// Browser-Test: steuert ein unsichtbares Chrome/Edge (iPad-Größe) über das DevTools-Protokoll.
// Voraussetzung: Build gelaufen, Server läuft:  python -m http.server 8765 -d app
// Aufruf:  node tools/test_browser.mjs <Ordner für Screenshots>
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const URL_BASIS = process.env.LT_URL || "http://127.0.0.1:8765/";  // LT_URL=https://… testet die Live-Seite
const AUSGABE = process.argv[2] || join(tmpdir(), "lerntrainer-screens");
mkdirSync(AUSGABE, { recursive: true });
const BROWSER = ["C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find(existsSync);
const PORT = 9333;

const proz = spawn(BROWSER, [`--headless=new`, `--remote-debugging-port=${PORT}`, "--no-first-run",
  `--user-data-dir=${mkdtempSync(join(tmpdir(), "lt-"))}`, "--window-size=820,1180", "about:blank"], { stdio: "ignore" });
const warte = (ms) => new Promise((r) => setTimeout(r, ms));

let ws, nr = 0;
const offen = new Map();
const probleme = [];
const ergebnisse = [];

async function verbinde() {
  for (let i = 0; i < 50; i++) {
    try {
      const ziele = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const seite = ziele.find((z) => z.type === "page");
      if (seite) return seite.webSocketDebuggerUrl;
    } catch { /* Browser startet noch */ }
    await warte(200);
  }
  throw new Error("Browser nicht erreichbar");
}

function cdp(method, params = {}) {
  const id = ++nr;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((res, rej) => offen.set(id, { res, rej }));
}

async function js(ausdruck) {
  const r = await cdp("Runtime.evaluate", { expression: ausdruck, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || "JS-Fehler");
  return r.result.value;
}

async function bild(name) {
  const r = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(join(AUSGABE, `${name}.png`), Buffer.from(r.data, "base64"));
}

async function geh(hash) {
  await js(`location.hash = ${JSON.stringify(hash)}`);
  await warte(500);
}

function pruefe(bed, was) {
  ergebnisse.push(`${bed ? "✓" : "✗"} ${was}`);
  if (!bed) probleme.push(was);
}

async function tippe(text) {
  await js(`(() => { const f = document.querySelector('#feld'); f.value = ${JSON.stringify(text)};
    f.dispatchEvent(new Event('input')); document.querySelector('#form').requestSubmit(); })()`);
  await warte(250);
}

const rm = () => js(`(() => { const r = document.querySelector('#rm'); return r ? r.className + ' :: ' + r.innerText : ''; })()`);

async function main() {
  ws = new WebSocket(await verbinde());
  await new Promise((r) => ws.addEventListener("open", r));
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && offen.has(m.id)) { offen.get(m.id).res(m.result || {}); offen.delete(m.id); }
    if (m.method === "Runtime.exceptionThrown") probleme.push("JS-Ausnahme: " + m.params.exceptionDetails.exception?.description);
    if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") probleme.push("Konsole: " + JSON.stringify(m.params.args.map((a) => a.value)));
    if (m.method === "Log.entryAdded" && m.params.entry.level === "error") probleme.push("Log: " + m.params.entry.text + " " + (m.params.entry.url || ""));
  });
  await cdp("Runtime.enable");
  await cdp("Log.enable");
  await cdp("Page.enable");
  await cdp("Emulation.setDeviceMetricsOverride", { width: 820, height: 1180, deviceScaleFactor: 1, mobile: false });
  await cdp("Page.navigate", { url: URL_BASIS });
  await warte(1500);

  // Start
  pruefe((await js("document.querySelectorAll('[data-min]').length")) === 4, "Start: 4 Zeitknöpfe");
  await bild("01-start");
  await js("document.querySelector('[data-min=\"20\"]').click()");
  await warte(600);
  pruefe((await js("location.hash")) === "#/ls/B1.1", "Start → empfohlener Lernschritt B1.1");
  await bild("02-lernschritt-B1.1");

  // B1.4: Gleichung Schritt für Schritt, mit einem Fehler zwischendurch
  await geh("#/ueben/B1.4");
  const a = await js("window.__aufgabe");
  pruefe(a && a.typ === "gleichung", `B1.4: Aufgabe ${a?.id} geladen`);
  await bild("03-aufgabe-B1.4");
  if (a.fehler?.length) {
    await tippe(`x = ${a.fehler[0].antwort}`);
    const r = await rm();
    pruefe(r.includes("falsch"), `B1.4: Fehlerantwort orange (${r.slice(0, 80)})`);
    await bild("04-fehlerhinweis");
  }
  await js("document.querySelector('#tipp').click()");
  await warte(200);
  pruefe((await js("document.querySelectorAll('.tipp').length")) === 1, "B1.4: Tipp 1 erscheint");
  for (const zeile of a.weg.slice(1)) await tippe(zeile);
  const r2 = await rm();
  pruefe(r2.startsWith("rueckmeldung gut") && (await js("!!document.querySelector('#next')")), `B1.4: gelöst nach Musterweg (${r2.slice(0, 60)})`);
  pruefe((await js("document.querySelectorAll('.zeile.ok').length")) === a.weg.length - 1, "B1.4: alle Zeilen mit Haken");
  await bild("05-geloest");

  // Schmierzettel mit Maus-Strichen
  await js("document.querySelector('#next').click()");
  await warte(300);
  await js("document.querySelector('#zettel-knopf').click()");
  await warte(400);
  const box = await js("(() => { const r = document.querySelector('.sz-flaeche').getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()");
  await cdp("Runtime.evaluate", { expression: "document.querySelector('.sz-flaeche').scrollIntoView()" });
  await warte(300);
  const b2 = await js("(() => { const r = document.querySelector('.sz-flaeche').getBoundingClientRect(); return {x: r.x, y: r.y}; })()");
  const punkte = Array.from({ length: 30 }, (_, i) => [b2.x + 40 + i * 8, b2.y + 60 + Math.sin(i / 3) * 25]);
  await cdp("Input.dispatchMouseEvent", { type: "mousePressed", x: punkte[0][0], y: punkte[0][1], button: "left", clickCount: 1 });
  for (const [x, y] of punkte) await cdp("Input.dispatchMouseEvent", { type: "mouseMoved", x, y, button: "left", buttons: 1 });
  await cdp("Input.dispatchMouseEvent", { type: "mouseReleased", x: punkte.at(-1)[0], y: punkte.at(-1)[1], button: "left" });
  await warte(200);
  const tinte = await js(`(() => { const c = document.querySelector('.sz-flaeche'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; })()`);
  pruefe(box.h > 200 && tinte > 50, `Schmierzettel: Strich gezeichnet (${tinte} Pixel)`);
  await bild("06-schmierzettel");

  // B1.9: Textaufgabe mit Einheit
  await geh("#/ueben/B1.9");
  const t = await js("window.__aufgabe");
  await tippe(`${t.loesung} ${t.einheit || ""}`.trim());
  pruefe((await rm()).startsWith("rueckmeldung gut"), `B1.9: ${t.id} mit Einheit richtig erkannt`);
  await bild("07-textaufgabe");

  // B1.8: Auswahl, absichtlich falsch
  await geh("#/ueben/B1.8");
  const w = await js("window.__aufgabe");
  const falsch = [0, 1, 2].find((i) => !w.richtig.includes(i));
  await js(`document.querySelector('.option[data-i="${falsch}"]').click()`);
  await warte(200);
  pruefe((await rm()).includes("falsch"), "B1.8: falsche Auswahl orange");
  await js(`document.querySelector('.option[data-i="${w.richtig[0]}"]').click()`);
  await warte(200);
  pruefe((await rm()).startsWith("rueckmeldung gut"), "B1.8: richtige Auswahl danach erkannt");
  await bild("08-auswahl");

  // B1.7: Bruchdarstellung
  await geh("#/ueben/B1.7");
  pruefe(await js("!!document.querySelector('.gleichung-gross .bruch')"), "B1.7: Bruch gesetzt");
  await bild("09-bruch");

  // Lösung zeigen
  await js("document.querySelector('#zeigen').click()");
  await warte(200);
  pruefe((await rm()).startsWith("rueckmeldung neutral"), "Lösung zeigen: neutral, nicht orange");
  await bild("10-loesung-gezeigt");

  // Lernpfad und Lernstand
  await geh("#/pfad");
  pruefe((await js("document.querySelectorAll('.ls a').length")) === 9, "Lernpfad: 9 verfügbare Lernschritte verlinkt");
  await bild("11-lernpfad");
  await geh("#/einstellungen");
  await bild("12-einstellungen");
  pruefe((await js("JSON.parse(localStorage.getItem('lerntrainer.v1')).faecher.mathe.ls['B1.4'].verlauf.length")) >= 1, "Lernstand gespeichert");

  // Schmal (Handy-Breite)
  await cdp("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await geh("#/ueben/B1.6");
  pruefe((await js("document.documentElement.scrollWidth <= window.innerWidth + 1")), "Schmal: kein waagrechtes Scrollen");
  await bild("13-schmal");

  // Offline-Cache aktiv?
  pruefe(await js("navigator.serviceWorker.getRegistration().then(r => !!r)"), "Service Worker registriert");

  console.log(ergebnisse.join("\n"));
  console.log(`\nScreenshots: ${AUSGABE}`);
  if (probleme.length) { console.log("\nPROBLEME:"); for (const p of probleme) console.log("  ✗", p); }
  ws.close();
  proz.kill();
  process.exit(probleme.length ? 1 : 0);
}

main().catch((e) => { console.error("Testlauf abgebrochen:", e); proz.kill(); process.exit(2); });
