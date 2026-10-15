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
  pruefe((await js("location.hash")) === "#/ls/A1.1", "Start → empfohlener Lernschritt A1.1 (erster Kernschritt)");
  await bild("02-lernschritt-A1.1");

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

  // Stift/Finger per Touch: muss zeichnen, darf nichts markieren
  await cdp("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
  await js("document.querySelector('[data-sz=\"leeren\"]').click()");
  const tp = (x, y) => [{ x, y, radiusX: 1, radiusY: 1, force: 0.5, id: 1 }];
  const wischen = async () => {
    await cdp("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: tp(b2.x + 50, b2.y + 50) });
    for (let i = 1; i <= 20; i++) await cdp("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: tp(b2.x + 50 + i * 10, b2.y + 50 + i * 4) });
    await cdp("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await warte(200);
    return js(`(() => { const c = document.querySelector('.sz-flaeche'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
      let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; })()`);
  };
  const tinteHand = await wischen();
  pruefe(tinteHand === 0 && (await js("String(getSelection())")) === "", `Schmierzettel: Hand/Finger zeichnet nicht (${tinteHand} Pixel), nichts markiert`);
  await js("document.querySelector('[data-sz=\"finger\"]').click()");
  const tinteFinger = await wischen();
  pruefe(tinteFinger > 50, `Schmierzettel: mit „Finger: an“ wird gezeichnet (${tinteFinger} Pixel)`);
  await js("document.querySelector('[data-sz=\"finger\"]').click()");
  pruefe((await js("getComputedStyle(document.body).userSelect")) === "none" &&
    (await js("getComputedStyle(document.querySelector('#feld')).userSelect")) !== "none", "Text nicht markierbar, Eingabefeld schon");

  // Handballen: Während/kurz nach dem Pencil und bei großer Auflagefläche drückt die Hand keinen Knopf
  const fk = await js(`(() => { const r = document.querySelector('[data-sz="finger"]').getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2}; })()`);
  const fingerText = () => js(`document.querySelector('[data-sz="finger"]').textContent`);
  const antippen = async (radius) => {
    const p = [{ x: fk.x, y: fk.y, radiusX: radius, radiusY: radius, force: 0.5, id: 2 }];
    await cdp("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: p });
    await cdp("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await warte(150);
  };
  await antippen(30);
  pruefe((await fingerText()).includes("aus"), "Handballen (große Fläche) drückt keinen Knopf");
  const stift = (type, x, y) => cdp("Input.dispatchMouseEvent", { type, x, y, button: "left", buttons: type === "mouseReleased" ? 0 : 1, clickCount: 1, pointerType: "pen" });
  await stift("mousePressed", b2.x + 60, b2.y + 120);
  for (let i = 1; i <= 10; i++) await stift("mouseMoved", b2.x + 60 + i * 12, b2.y + 120);
  await stift("mouseReleased", b2.x + 180, b2.y + 120);
  await antippen(5);
  pruefe((await fingerText()).includes("aus"), "Hand kurz nach dem Pencil drückt keinen Knopf");
  await warte(1700);
  await antippen(5);
  pruefe((await fingerText()).includes("an"), "Finger tippt Knopf, wenn der Pencil ruht");
  await js("document.querySelector('[data-sz=\"finger\"]').click()");
  await cdp("Emulation.setTouchEmulationEnabled", { enabled: false });

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

  // A4.3 Term: Zwischenschritt mit Klammer wird angenommen, fertig erst ohne Klammer
  await geh("#/ueben/A4.3");
  const t3 = await js("window.__aufgabe");
  pruefe(t3.typ === "term" && (await js("document.querySelector('.anweisung').innerText")).includes("Klammer"), `A4.3: Term-Aufgabe ${t3.id} ${t3.term}`);
  await tippe(t3.term);
  const r3a = await rm();
  pruefe(r3a.startsWith("rueckmeldung gut") && r3a.includes("Klammer") && (await js("document.querySelectorAll('.zeile.ok').length")) === 1,
    `A4.3: Ausgangsterm als Zwischenschritt (${r3a.slice(0, 60)})`);
  if (t3.fehler?.length) {
    await tippe(t3.fehler[0].antwort);
    pruefe((await rm()).startsWith("rueckmeldung falsch"), `A4.3: typischer Fehler ${t3.fehler[0].antwort} orange mit Hinweis`);
  }
  await tippe(t3.loesung);
  pruefe((await rm()).startsWith("rueckmeldung gut") && (await js("!!document.querySelector('#next')")), `A4.3: Lösung ${t3.loesung} erkannt`);
  await bild("09b-term");

  // A4.5 Herausheben: Summe ist noch nicht fertig, Produkt schon; Symbolleiste hat die Variablen
  await geh("#/ueben/A4.5");
  const t5 = await js("window.__aufgabe");
  pruefe((await js("[...document.querySelectorAll('#symbole .sym')].map(b => b.dataset.s).join(' ')")).includes("x"), "A4.5: Symbolleiste mit x");
  await tippe(t5.loesung);
  pruefe((await rm()).startsWith("rueckmeldung gut"), `A4.5: ${t5.term} = ${t5.loesung} erkannt`);

  // A2.1 Kürzen: ungekürzt → freundlicher Hinweis (neutral), gekürzt → richtig
  const naechsteBis = async (lid, bed) => {
    await geh(`#/ueben/${lid}`);
    for (let i = 0; i < 25; i++) {
      const kand = await js("window.__aufgabe");
      if (bed(kand)) return kand;
      await js("document.querySelector('#zeigen').click()");
      await warte(150);
      await js("document.querySelector('#next').click()");
      await warte(250);
    }
    return null;
  };
  const k = await naechsteBis("A2.1", (x) => x.form === "gekuerzt");
  const roh = /`(.+)`/.exec(k.frage)[1];
  await tippe(roh);
  const rk = await rm();
  pruefe(rk.startsWith("rueckmeldung neutral") && rk.includes("kürzen"), `A2.1: ungekürzt ${roh} → Hinweis (${rk.slice(0, 60)})`);
  await tippe(k.loesung);
  pruefe((await rm()).startsWith("rueckmeldung gut"), `A2.1: ${k.loesung} richtig`);
  await bild("09c-kuerzen");

  // A2.4 Division mit Doppelpunkt wird als „:“ gesetzt, nicht als Bruch
  await js(`(() => { const z = JSON.parse(localStorage.getItem('lerntrainer.v1'));
    z.faecher.mathe.ls['A2.4'] = { stufe: 2, status: 'angefangen', verlauf: [] };
    localStorage.setItem('lerntrainer.v1', JSON.stringify(z)); })()`);
  await cdp("Page.reload");
  await warte(1200);
  const dv = await naechsteBis("A2.4", (x) => x.frage.includes(":"));
  pruefe(dv && (await js("document.querySelector('.frage .mathe').innerText")).includes(":"), `A2.4: Division ${dv?.frage} mit „:“ gesetzt`);
  await bild("09d-division");

  // A3.2 Potenzregeln: Hochzahlen werden gesetzt, Zwischenschritt angenommen
  const p2 = await naechsteBis("A3.2", (x) => x.typ === "term");
  pruefe(await js("!!document.querySelector('.gleichung-gross sup')"), `A3.2: ${p2.term} mit Hochzahlen gesetzt`);
  await tippe(p2.loesung.replace(/\^(\d+)/g, (_, d) => [...d].map((c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[c]).join("")));
  pruefe((await rm()).startsWith("rueckmeldung gut"), `A3.2: Lösung mit hochgestellten Ziffern erkannt`);
  await bild("09e-potenzen");

  // A1.5 Zahlenmengen (Auswahl mit fünf Mengen)
  const zm = await naechsteBis("A1.5", () => true);
  await js(`document.querySelector('.option[data-i="${zm.richtig[0]}"]').click()`);
  await warte(200);
  pruefe((await rm()).startsWith("rueckmeldung gut"), `A1.5: ${zm.frage.slice(0, 50)} richtig`);

  // A5.5 Zinseszins: auf Cent gerundete Antwort wird angenommen
  await js(`(() => { const z = JSON.parse(localStorage.getItem('lerntrainer.v1'));
    z.faecher.mathe.ls['A5.5'] = { stufe: 2, status: 'angefangen', verlauf: [] };
    localStorage.setItem('lerntrainer.v1', JSON.stringify(z)); })()`);
  await cdp("Page.reload");
  await warte(1200);
  const zi = await naechsteBis("A5.5", (x) => x.gerundet !== undefined);
  await tippe(`${zi.loesung} €`);
  pruefe((await rm()).includes("gerundet"), `A5.5: ${zi.loesung} € als sinnvoll gerundet erkannt`);
  await bild("09f-zinseszins");

  // B2.2 Formel umformen: Zwischenzeile, dann Lösung
  const fo = await naechsteBis("B2.2", (x) => x.weg.length >= 3);
  await tippe(fo.weg[1].split("|")[0]);
  const rf = await rm();
  pruefe(rf.startsWith("rueckmeldung gut") && rf.includes("umgeformt"), `B2.2: Zwischenzeile ${fo.weg[1].split("|")[0]} angenommen`);
  await tippe(`${fo.nach} = ${fo.loesung}`);
  pruefe((await rm()).startsWith("rueckmeldung gut") && (await js("!!document.querySelector('#next')")), `B2.2: ${fo.formel} nach ${fo.nach} gelöst`);
  await bild("09g-formel");

  // Lösung zeigen
  await geh("#/ueben/B1.7");
  await js("document.querySelector('#zeigen').click()");
  await warte(200);
  pruefe((await rm()).startsWith("rueckmeldung neutral"), "Lösung zeigen: neutral, nicht orange");
  await bild("10-loesung-gezeigt");

  // „Zu leicht? Schwerer“ hebt die Stufe sofort an
  await geh("#/ueben/B1.5");
  const s0 = (await js("window.__aufgabe")).stufe;
  await js("document.querySelector('#schwerer').click()");
  await warte(300);
  const s1 = await js("window.__aufgabe.stufe");
  const kopf = await js("document.querySelector('.stufe').innerText");
  pruefe(s0 === 1 && s1 === 2 && /Üben/i.test(kopf) && (await js("!!document.querySelector('.aufstieg')")),
    `Schwerer-Knopf: Stufe ${s0} → ${s1} (${kopf})`);
  await bild("10b-schwerer");

  // „Kann ich schon“: drei Prüfaufgaben (Stufe 3, 3, 4), alle richtig → Schritt erledigt
  await geh("#/ls/B1.3");
  pruefe(await js("document.querySelector('#kann').classList.contains('zweit-knopf')"), "Lernschritt: „Kann ich schon“ deutlich sichtbar");
  await js("document.querySelector('#kann').click()");
  await warte(500);
  const stufenTest = [];
  for (let i = 0; i < 3; i++) {
    const p = await js("window.__aufgabe");
    stufenTest.push(p.stufe);
    await tippe(`x = ${p.loesung}`);
    await js("document.querySelector('#next').click()");
    await warte(300);
  }
  pruefe(stufenTest.join() === "3,3,4" && (await js("document.body.innerText.includes('Das kannst du schon')")),
    `Kann ich schon: Prüfaufgaben Stufe ${stufenTest.join("/")}, bestanden`);
  pruefe((await js("JSON.parse(localStorage.getItem('lerntrainer.v1')).faecher.mathe.ls['B1.3'].status")) === "sicher", "Kann ich schon: Schritt als sicher gespeichert");
  await bild("10c-kann-ich-schon");

  // Matura-Niveau: Brüche als Koeffizienten werden gesetzt, Musterlösung lesbar
  await js(`(() => { const z = JSON.parse(localStorage.getItem('lerntrainer.v1'));
    z.faecher.mathe.ls['B1.4'] = { stufe: 4, status: 'angefangen', verlauf: [] };
    localStorage.setItem('lerntrainer.v1', JSON.stringify(z)); })()`);
  await cdp("Page.reload");
  await warte(1200);
  await geh("#/ueben/B1.4");
  const m = await js("window.__aufgabe");
  pruefe(m.stufe === 4 && (await js("!!document.querySelector('.gleichung-gross .bruch')")), `Matura-Niveau: ${m.id} ${m.gleichung} mit Bruch gesetzt`);
  await js("document.querySelector('#zeigen').click()");
  await warte(200);
  await bild("10d-matura-niveau");

  // Lernpfad und Lernstand
  await geh("#/pfad");
  const nLs = await js("document.querySelectorAll('.ls a').length");
  pruefe(nLs >= 33, `Lernpfad: ${nLs} verfügbare Lernschritte verlinkt`);
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
