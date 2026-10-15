// Oberfläche: Start, Lernpfad, Lernschritt, Üben, Einstellungen. Navigation über #/…
import * as M from "./mathe.js";
import * as S from "./speicher.js";
import { schmierzettel } from "./schmierzettel.js";
import "./handablage.js";

const FACH = "mathe";
const STUFE_NAME = { 1: "Einstieg", 2: "Üben", 3: "Vertiefen", 4: "Matura-Niveau" };
const TEST_STUFEN = [3, 3, 4]; // „Kann ich schon“: zwei Aufgaben Vertiefen, eine auf Matura-Niveau
const LOB = ["Gut gemacht!", "Genau so!", "Sauber gelöst.", "Richtig!", "Stark!", "Passt!", "Super, stimmt!"];
const MUT = [
  "Du bist auf einem guten Weg.", "Schritt für Schritt wird das sicherer.", "Das sitzt immer besser.",
  "Weiter so – in deinem Tempo.", "Jede Aufgabe macht dich ein Stück sicherer.",
];
const TROST = [
  "Fehler gehören zum Lernen dazu – du schaffst das.", "Kein Problem, genau dafür üben wir.",
  "Das passiert jedem. Probier es gleich noch einmal.", "Du bist nah dran!",
];
const TERM_ANWEISUNG = {
  zusammengefasst: "Fasse zusammen.", ausmultipliziert: "Löse die Klammern auf und fasse zusammen.",
  faktor: "Heb heraus – schreib den Term als Produkt.", gekuerzt: "Kürze so weit wie möglich.", frei: "Schreib den Term auf.",
};
const SYMBOLE = ["x", "²", "(", ")", "·", ":", "/", "+", "−", "=", ","];
const zufall = (liste) => liste[Math.floor(Math.random() * liste.length)];
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const haupt = document.getElementById("haupt");
let lernpfad = null;
const cache = {};
const einheit = { ende: null, gemacht: 0, zeitHinweis: false };

// ── Daten ────────────────────────────────────────────────

async function ladeLernpfad() {
  if (!lernpfad) lernpfad = await (await fetch(`daten/${FACH}/lernpfad.json`)).json();
  return lernpfad;
}

async function ladeLernschritt(lid) {
  if (!cache[lid]) cache[lid] = await (await fetch(`daten/${FACH}/${lid}.json`)).json();
  return cache[lid];
}

function alleLernschritte() {
  const aus = [];
  for (const t of lernpfad.teile) for (const k of t.kapitel) for (const l of k.lernschritte) aus.push({ ...l, kapitel: k, teil: t });
  return aus;
}

function empfehlung() {
  const alle = alleLernschritte().filter((l) => l.verfuegbar);
  const l = S.letzter();
  if (l && l.fach === FACH) {
    const letzter = alle.find((x) => x.id === l.lid);
    if (letzter && S.lernschritt(FACH, letzter.id).status !== "sicher") return letzter;
  }
  return alle.find((x) => x.kern && S.lernschritt(FACH, x.id).status !== "sicher")
      || alle.find((x) => S.lernschritt(FACH, x.id).status !== "sicher")
      || null;
}

function nachfolger(lid) {
  const alle = alleLernschritte().filter((l) => l.verfuegbar);
  const i = alle.findIndex((l) => l.id === lid);
  return i >= 0 ? alle[i + 1] || null : null;
}

// ── Navigation ───────────────────────────────────────────

async function zeige() {
  await ladeLernpfad();
  const [, seite, arg] = location.hash.replace(/^#/, "").split("/");
  window.scrollTo(0, 0);
  if (seite === "pfad") return seitePfad();
  if (seite === "ls" && arg) return seiteLernschritt(arg);
  if (seite === "ueben" && arg) return seiteUeben(arg, false);
  if (seite === "test" && arg) return seiteUeben(arg, true);
  if (seite === "einstellungen") return seiteEinstellungen();
  return seiteStart();
}

function geh(ziel) { location.hash = ziel; }

// ── Start ────────────────────────────────────────────────

function seiteStart() {
  const emp = empfehlung();
  const pause = S.letzteAktivitaet() ? (Date.now() - S.letzteAktivitaet()) / 864e5 : null;
  const gruss = pause === null ? "Willkommen!" : pause > 7 ? "Schön, dass du wieder da bist!" : "Hallo!";
  const istIOS = /iPad|iPhone|Macintosh/.test(navigator.userAgent) && "ontouchend" in document;
  const standalone = window.navigator.standalone || matchMedia("(display-mode: standalone)").matches;
  const installHinweis = istIOS && !standalone && !S.hinweisGesehen("install");

  haupt.innerHTML = `
    <section class="start">
      <h1>${gruss}</h1>
      <p class="leise">Wie viel Zeit hast du heute?</p>
      <div class="zeitwahl">
        ${[10, 20, 30].map((m) => `<button class="knopf zeit" data-min="${m}">${m} Minuten</button>`).join("")}
        <button class="knopf zeit leise-knopf" data-min="0">ohne Zeit</button>
      </div>
      ${emp ? `<p class="weiter-info">Als Nächstes: <strong>${esc(emp.id)} ${esc(emp.titel)}</strong></p>`
            : `<p class="weiter-info">Du hast alle verfügbaren Lernschritte geschafft. Großartig!</p>`}
      <nav class="unten-links">
        <a href="#/pfad">Lernpfad ansehen</a>
        <a href="#/einstellungen">Lernstand sichern</a>
      </nav>
      ${installHinweis ? `<div class="hinweis-karte" id="install">
        <p><strong>Tipp:</strong> Tippe in Safari auf das Teilen-Symbol <span aria-hidden="true">⬆︎</span> und dann auf
        „Zum Home-Bildschirm“. Dann hast du die App wie eine normale App – und sie funktioniert auch ohne Internet.</p>
        <button class="knopf klein" id="install-ok">Verstanden</button></div>` : ""}
    </section>`;

  haupt.querySelectorAll("[data-min]").forEach((b) => b.addEventListener("click", () => {
    const min = Number(b.dataset.min);
    einheit.ende = min ? Date.now() + min * 60e3 : null;
    einheit.gemacht = 0;
    einheit.zeitHinweis = false;
    if (!emp) return geh("#/pfad");
    const st = S.lernschritt(FACH, emp.id);
    geh(st.status === "neu" ? `#/ls/${emp.id}` : `#/ueben/${emp.id}`);
  }));
  haupt.querySelector("#install-ok")?.addEventListener("click", () => {
    S.hinweisMerken("install");
    haupt.querySelector("#install").remove();
  });
}

// ── Lernpfad ─────────────────────────────────────────────

const STATUS_ZEICHEN = { neu: "○", angefangen: "◐", sicher: "●" };

function seitePfad() {
  const teile = lernpfad.teile.map((t) => {
    const kapitel = t.kapitel.map((k) => {
      const da = k.lernschritte.some((l) => l.verfuegbar);
      const zeilen = k.lernschritte.map((l) => {
        const st = S.lernschritt(FACH, l.id).status;
        if (!l.verfuegbar) return `<li class="ls aus"><span class="st">·</span><span class="ls-id">${esc(l.id)}</span> ${esc(l.titel)}</li>`;
        return `<li class="ls"><a href="#/ls/${esc(l.id)}"><span class="st st-${st}" title="${st}">${STATUS_ZEICHEN[st]}</span>` +
               `<span class="ls-id">${esc(l.id)}</span> ${esc(l.titel)}</a></li>`;
      }).join("");
      const titel = t.id === "G" ? k.titel : `${k.id} ${k.titel}`;
      return `<details class="kapitel"${da ? " open" : ""}><summary>${esc(titel)}${da ? "" : ' <span class="bald">kommt bald</span>'}</summary><ul>${zeilen}</ul></details>`;
    }).join("");
    return `<section class="teil"><h2>Teil ${esc(t.id)} · ${esc(t.titel)}</h2>${kapitel}</section>`;
  }).join("");
  haupt.innerHTML = `
    <div class="leiste"><a href="#/" class="zurueck">← Start</a></div>
    <h1>Lernpfad</h1>
    <p class="leise legende">○ noch nicht begonnen · ◐ angefangen · ● kann ich</p>
    ${teile}`;
}

// ── Lernschritt: Erklärung und Beispiel ──────────────────

async function seiteLernschritt(lid) {
  const ls = await ladeLernschritt(lid);
  S.merkeBesuch(FACH, lid);
  const b = ls.beispiel || {};
  const weg = (b.weg || []).map((z) => `<li>${M.wegZeileHTML(z)}</li>`).join("");
  haupt.innerHTML = `
    <div class="leiste"><a href="#/pfad" class="zurueck">← Lernpfad</a></div>
    <p class="ls-nummer">${esc(ls.id)}</p>
    <h1>${esc(ls.titel)}</h1>
    <p class="ziel">${esc(ls.ziel || "")}</p>
    <section class="karte erklaerung">${M.textHTML(ls.erklaerung)}</section>
    ${b.text || weg ? `<section class="karte beispiel"><h2>Beispiel</h2>${M.textHTML(b.text || "")}
      ${weg ? `<ol class="weg">${weg}</ol>` : ""}</section>` : ""}
    <div class="knopfreihe">
      <button class="knopf haupt-knopf" id="los">Los geht's</button>
      <button class="knopf zweit-knopf" id="kann">Kann ich schon ✓</button>
    </div>
    <p class="leise klein-text">Kennst du das schon? Mit „Kann ich schon“ bekommst du drei schwierigere Prüfaufgaben.
      Passen alle drei, ist der Schritt erledigt und du gehst gleich weiter.</p>`;
  haupt.querySelector("#los").addEventListener("click", () => geh(`#/ueben/${lid}`));
  haupt.querySelector("#kann").addEventListener("click", () => geh(`#/test/${lid}`));
}

// ── Üben ─────────────────────────────────────────────────

function waehleAufgabe(ls, stufe, ausser) {
  const verlauf = S.lernschritt(FACH, ls.id).verlauf;
  let kandidaten = ls.aufgaben.filter((a) => a.stufe === stufe);
  for (let d = 1; !kandidaten.length && d < S.HOECHSTE_STUFE; d++) kandidaten = ls.aufgaben.filter((a) => Math.abs(a.stufe - stufe) === d);
  const zuletzt = new Map();
  verlauf.forEach((v, i) => zuletzt.set(v.a, i));
  let pool = kandidaten.filter((a) => !zuletzt.has(a.id) && a.id !== ausser);
  if (!pool.length) {
    pool = [...kandidaten].filter((a) => a.id !== ausser).sort((x, y) => zuletzt.get(x.id) - zuletzt.get(y.id));
    pool = pool.slice(0, Math.max(1, Math.ceil(pool.length / 2)));
  }
  if (!pool.length) pool = kandidaten;
  return zufall(pool);
}

async function seiteUeben(lid, testModus) {
  const ls = await ladeLernschritt(lid);
  S.merkeBesuch(FACH, lid);
  const test = testModus ? { nr: 0, richtig: 0, gesehen: new Set() } : null;
  let aufgabe = null;
  let zettel = null;
  let hinweisOben = "";

  haupt.innerHTML = `
    <div class="leiste">
      <a href="#/ls/${esc(lid)}" class="zurueck">← ${esc(ls.id)}</a>
      <span class="leiste-titel">${esc(ls.titel)}</span>
      <a href="#/" class="leiste-rechts">Pause</a>
    </div>
    <div id="aufgabe"></div>
    <section class="schmierzettel karte" id="zettel" hidden></section>
    <div class="symbole" id="symbole" hidden></div>`;
  const ort = haupt.querySelector("#aufgabe");
  const zettelOrt = haupt.querySelector("#zettel");

  // Symbolleiste: fügt in das zuletzt benutzte Eingabefeld ein, ohne die Tastatur zu schließen
  let aktivesFeld = null;
  haupt.querySelector("#symbole").addEventListener("pointerdown", (e) => {
    const s = e.target.closest("[data-s]")?.dataset.s;
    if (!s || !aktivesFeld) return;
    e.preventDefault();
    const f = aktivesFeld, a = f.selectionStart ?? f.value.length, b = f.selectionEnd ?? a;
    if (s === "⌫") {
      const von = a === b ? Math.max(0, a - 1) : a;
      f.value = f.value.slice(0, von) + f.value.slice(b);
      f.setSelectionRange(von, von);
    } else {
      f.value = f.value.slice(0, a) + s + f.value.slice(b);
      f.setSelectionRange(a + s.length, a + s.length);
    }
    f.dispatchEvent(new Event("input"));
    f.focus();
  });

  function naechste() {
    if (test && test.nr >= 3) return testErgebnis();
    const st = S.lernschritt(FACH, lid);
    const stufe = test ? TEST_STUFEN[test.nr] : st.stufe;
    aufgabe = waehleAufgabe(ls, stufe, aufgabe?.id);
    if (test) { test.nr++; }
    zettel?.leeren();
    zeigeAufgabe(aufgabe, stufe);
  }

  function schwerer() {
    const neu = S.stufeHoch(FACH, lid);
    hinweisOben = `<p class="aufstieg">Alles klar – ab jetzt: <strong>${STUFE_NAME[neu]}</strong>.</p>`;
    naechste();
  }

  // Knöpfe unter der Aufgabe, die nur beim Üben Sinn haben
  function uebenKnoepfe() {
    if (test) return "";
    const st = S.lernschritt(FACH, lid);
    return (st.stufe < S.HOECHSTE_STUFE ? `<button class="knopf leise-knopf" id="schwerer">Zu leicht? Schwerer ⬆</button>` : "") +
      (st.status !== "sicher" && st.stufe < 3 ? `<a href="#/test/${esc(lid)}" class="knopf leise-knopf">Kann ich schon ✓</a>` : "");
  }

  function testErgebnis() {
    if (test.richtig === 3) {
      S.setzeSicher(FACH, lid);
      const n = nachfolger(lid);
      ort.innerHTML = `<section class="karte erfolg"><h2>Das kannst du schon!</h2>
        <p>Alle drei Prüfaufgaben richtig. Dieser Schritt ist erledigt.</p>
        ${n ? `<button class="knopf haupt-knopf" id="weiter">Weiter: ${esc(n.id)} ${esc(n.titel)}</button>` : ""}
        <a href="#/pfad" class="knopf leise-knopf">Zum Lernpfad</a></section>`;
      ort.querySelector("#weiter")?.addEventListener("click", () => geh(`#/ls/${n.id}`));
    } else {
      ort.innerHTML = `<section class="karte"><h2>Gut, dass wir nachgesehen haben</h2>
        <p>${test.richtig} von 3 haben gepasst. Wir üben diesen Schritt noch ein bisschen – das geht schnell.</p>
        <button class="knopf haupt-knopf" id="ueben">Üben</button></section>`;
      ort.querySelector("#ueben").addEventListener("click", () => geh(`#/ueben/${lid}`));
    }
    haupt.querySelector("#symbole").hidden = true;
  }

  function zeigeAufgabe(a, stufe) {
    const zustand = { tipps: 0, fehlversuche: 0, gezeigt: false, fertig: false, zeilen: [] };
    window.__aufgabe = a; // für tools/test_browser.mjs
    const istGl = a.typ === "gleichung";
    const istTerm = a.typ === "term";
    const kopf = test ? `Prüfaufgabe ${test.nr} von 3` : `${STUFE_NAME[stufe]} · Stufe ${stufe} von ${S.HOECHSTE_STUFE}`;
    let koerper;
    if (istGl) {
      koerper = `<p class="anweisung">Löse die Gleichung.</p>
        <div class="gleichung-gross">${M.matheHTML(a.gleichung)}</div>
        <ol class="zeilen" id="zeilen"></ol>`;
    } else if (istTerm) {
      koerper = `${a.frage ? `<div class="frage">${M.textHTML(a.frage)}</div>` : `<p class="anweisung">${esc(a.anweisung || TERM_ANWEISUNG[a.form] || "Vereinfache.")}</p>`}
        ${a.term ? `<div class="gleichung-gross">${M.matheHTML(a.term)}</div>` : ""}
        <ol class="zeilen" id="zeilen"></ol>`;
    } else {
      koerper = `<div class="frage">${M.textHTML(a.frage)}</div>`;
    }
    const platzhalter = istGl ? "nächste Zeile, z. B. 3x = 15" : istTerm ? "z. B. 3x + 6" : a.form ? "z. B. 3/4" : "Antwort";
    const eingabe = a.typ === "auswahl"
      ? `<div class="optionen">${a.optionen.map((o, i) => `<button class="knopf option" data-i="${i}">${a.mathe ? M.matheHTML(o) : esc(o)}</button>`).join("")}</div>`
      : `<form class="eingabe" id="form" autocomplete="off">
           <input id="feld" type="text" inputmode="text" autocapitalize="off" autocorrect="off" spellcheck="false"
             placeholder="${platzhalter}" aria-label="Deine Antwort">
           <button class="knopf haupt-knopf" type="submit">Prüfen</button>
         </form>
         <div class="vorschau" id="vorschau" aria-hidden="true"></div>
         ${istGl ? `<p class="leise klein-text eingabe-hinweis">Schreib Zeile für Zeile – oder gleich das Ergebnis, z. B. x = 4.</p>` : ""}
         ${istTerm ? `<p class="leise klein-text eingabe-hinweis">Du kannst Zwischenschritte schreiben – jede Zeile wird geprüft.</p>` : ""}
         ${a.form === "gekuerzt" && !istTerm ? `<p class="leise klein-text eingabe-hinweis">Ergebnis als gekürzter Bruch (oder ganze Zahl), z. B. 3/4.</p>` : ""}
         ${a.einheit ? `<p class="leise klein-text eingabe-hinweis">Antwort in ${esc(a.einheit)}</p>` : ""}`;

    ort.innerHTML = `
      <section class="karte aufgabe">
        ${hinweisOben}
        <p class="stufe">${esc(kopf)}</p>
        ${koerper}
        ${eingabe}
        <div class="tipps" id="tipps"></div>
        <div class="rueckmeldung" id="rm" aria-live="polite"></div>
        <div class="hilfen" id="hilfen">
          ${(a.tipps || []).length ? `<button class="knopf leise-knopf" id="tipp">💡 Tipp</button>` : ""}
          <button class="knopf leise-knopf" id="zettel-knopf">✏️ Schmierzettel</button>
          ${test ? "" : `<button class="knopf leise-knopf" id="zeigen">Lösung zeigen</button>`}
          ${uebenKnoepfe()}
        </div>
      </section>`;
    hinweisOben = "";
    ort.querySelector("#schwerer")?.addEventListener("click", schwerer);

    const rm = ort.querySelector("#rm");
    const feld = ort.querySelector("#feld");
    const symbole = haupt.querySelector("#symbole");
    symbole.hidden = !feld;
    const zeichen = istTerm ? [...[...M.variablen(M.lies(a.loesung).term)].sort(), "²", "(", ")", "·", "/", "+", "−", ","]
      : a.typ === "zahl" && a.form ? ["/", "−", ",", "(", ")"] : SYMBOLE;
    symbole.innerHTML = zeichen.map((s) => `<button type="button" class="sym" data-s="${s}">${s}</button>`).join("") +
      `<button type="button" class="sym" data-s="⌫" aria-label="Zeichen löschen">⌫</button>`;
    if (feld) {
      aktivesFeld = feld;
      feld.addEventListener("focus", () => { aktivesFeld = feld; });
      const vorschau = ort.querySelector("#vorschau");
      feld.addEventListener("input", () => {
        const t = feld.value.split("|")[0];
        vorschau.innerHTML = t.trim() && M.versuche(t) ? M.matheHTML(t) : "";
      });
      // Auf dem iPad nicht automatisch fokussieren (Tastatur würde den Bildschirm verdecken)
      if (!("ontouchend" in document)) feld.focus();
    }

    function melde(art, html) {
      rm.className = `rueckmeldung ${art}`;
      rm.innerHTML = html;
    }

    function abschliessen(ergebnis, html) {
      zustand.fertig = true;
      einheit.gemacht++;
      let meldung = null;
      if (test) {
        if (ergebnis === "richtig") test.richtig++;
      } else {
        meldung = S.merkeErgebnis(FACH, lid, a.id, a.stufe, ergebnis);
      }
      const zusatz = {
        aufstieg: `<p class="aufstieg">Du bist jetzt bei <strong>${STUFE_NAME[S.lernschritt(FACH, lid).stufe]}</strong>. Die Aufgaben werden ein bisschen anspruchsvoller.</p>`,
        sicher: `<p class="aufstieg">🎉 <strong>Diesen Schritt kannst du!</strong> Du kannst zum nächsten Schritt gehen – oder dich an Aufgaben auf Matura-Niveau wagen.</p>`,
        leichter: `<p class="aufstieg">Wir machen kurz mit etwas leichteren Aufgaben weiter.</p>`,
      }[meldung] || "";
      const n = meldung === "sicher" ? nachfolger(lid) : null;
      const zeitUm = einheit.ende && Date.now() > einheit.ende && !einheit.zeitHinweis;
      if (zeitUm) einheit.zeitHinweis = true;
      melde(ergebnis === "gezeigt" ? "neutral" : "gut", html + zusatz + (zeitUm
        ? `<p class="zeit-um">Deine geplante Zeit ist um. Toll, dass du heute geübt hast!</p>` : ""));
      ort.querySelector("#form")?.remove();
      ort.querySelector("#vorschau")?.remove();
      ort.querySelectorAll(".eingabe-hinweis").forEach((p) => p.remove());
      ort.querySelectorAll(".option").forEach((b) => { b.disabled = true; });
      haupt.querySelector("#symbole").hidden = true;
      const hilfen = ort.querySelector("#hilfen");
      hilfen.innerHTML = zeitUm
        ? `<a href="#/" class="knopf haupt-knopf">Fertig für heute</a><button class="knopf leise-knopf" id="next">Noch eine Aufgabe</button>`
        : `<button class="knopf haupt-knopf" id="next">${test && test.nr >= 3 ? "Auswerten" : "Nächste Aufgabe"}</button>` +
          (n ? `<button class="knopf leise-knopf" id="zum-naechsten">Weiter: ${esc(n.id)}</button>` : "") +
          (zeitUm ? "" : uebenKnoepfe());
      hilfen.querySelector("#next")?.addEventListener("click", naechste);
      hilfen.querySelector("#schwerer")?.addEventListener("click", schwerer);
      hilfen.querySelector("#zum-naechsten")?.addEventListener("click", () => geh(`#/ls/${n.id}`));
      hilfen.querySelector("#next")?.focus();
    }

    function ergebnisArt() {
      if (zustand.gezeigt) return "gezeigt";
      return zustand.tipps === 0 && zustand.fehlversuche <= 1 ? "richtig" : "hilfe";
    }

    function wegHTML() {
      if (!a.weg?.length) return "";
      return `<ol class="weg">${a.weg.map((z) => `<li>${M.wegZeileHTML(z)}</li>`).join("")}</ol>`;
    }

    // Tipps nacheinander
    ort.querySelector("#tipp")?.addEventListener("click", (e) => {
      if (zustand.tipps >= a.tipps.length) return;
      zustand.tipps++;
      ort.querySelector("#tipps").insertAdjacentHTML("beforeend",
        `<div class="tipp"><span class="tipp-nr">Tipp ${zustand.tipps}</span> ${M.textHTML(a.tipps[zustand.tipps - 1])}</div>`);
      if (zustand.tipps >= a.tipps.length) e.target.disabled = true;
    });

    ort.querySelector("#zettel-knopf").addEventListener("click", () => {
      zettelOrt.hidden = !zettelOrt.hidden;
      if (!zettel) zettel = schmierzettel(zettelOrt);
      if (!zettelOrt.hidden) zettelOrt.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });

    ort.querySelector("#zeigen")?.addEventListener("click", () => {
      if (zustand.fertig) return;
      zustand.gezeigt = true;
      const loesung = a.typ === "auswahl" ? esc(a.optionen[a.richtig[0]]) :
        a.typ === "gleichung" ? M.matheHTML(`x = ${a.loesung}`) : M.matheHTML(a.loesung) + (a.einheit ? " " + esc(a.einheit) : "");
      abschliessen("gezeigt", `<p><strong>Lösung:</strong> ${loesung}</p>${wegHTML()}
        ${a.erklaerung ? M.textHTML(a.erklaerung) : ""}
        <p class="mut">Anschauen ist auch lernen. Geh die Schritte in Ruhe durch – bei der nächsten Aufgabe probierst du es selbst.</p>`);
    });

    // Auswahl
    ort.querySelectorAll(".option").forEach((b) => b.addEventListener("click", () => {
      if (zustand.fertig) return;
      const i = Number(b.dataset.i);
      const richtig = a.richtig.includes(i);
      b.classList.add(richtig ? "gewaehlt-gut" : "gewaehlt-falsch");
      if (richtig) {
        abschliessen(ergebnisArt(), `<p><strong>${zufall(LOB)}</strong></p>${M.textHTML(a.erklaerung)}<p class="mut">${zufall(MUT)}</p>`);
      } else {
        zustand.fehlversuche++;
        if (a.optionen.length === 2) {
          // Ja/Nein: beim ersten Fehlgriff gleich erklären – raten hilft hier nicht weiter
          ort.querySelector(`.option[data-i="${a.richtig[0]}"]`).classList.add("gewaehlt-gut");
          zustand.fehlversuche = 2;
          abschliessen("hilfe", `<p><strong>Nicht ganz.</strong></p>${M.textHTML(a.erklaerung)}<p class="mut">${zufall(TROST)}</p>`);
        } else {
          b.disabled = true;
          melde("falsch", `<p>Das stimmt leider nicht. Schau dir die Aufgabe noch einmal an – vielleicht hilft ein Tipp.</p><p class="mut">${zufall(TROST)}</p>`);
        }
      }
    }));

    // Freie Eingabe
    ort.querySelector("#form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      if (zustand.fertig) return;
      const roh = feld.value.trim();
      if (!roh) return;
      if (istGl) pruefeZeile(roh);
      else if (istTerm) pruefeTerm(roh);
      else pruefeAntwort(roh);
    });

    function pruefeTerm(roh) {
      const r = M.pruefeTermZeile(roh, a);
      const neueZeile = () => {
        const t = roh.includes("=") ? roh.slice(roh.lastIndexOf("=") + 1).trim() : roh;
        ort.querySelector("#zeilen").insertAdjacentHTML("beforeend",
          `<li class="zeile ok"><span class="weg-op">=</span> ${M.matheHTML(t)}<span class="haken" aria-label="richtig">✓</span></li>`);
        feld.value = "";
        ort.querySelector("#vorschau").innerHTML = "";
      };
      if (r.art === "geloest") {
        neueZeile();
        abschliessen(ergebnisArt(), `<p><strong>${zufall(LOB)}</strong> ${a.term ? `${M.matheHTML(a.term)} = ` : ""}${M.matheHTML(a.loesung)}</p>
          ${a.erklaerung ? M.textHTML(a.erklaerung) : ""}
          ${a.weg?.length ? `<details class="weg-details"><summary>Musterlösung ansehen</summary>${wegHTML()}</details>` : ""}
          <p class="mut">${zufall(MUT)}</p>`);
      } else if (r.art === "schritt") {
        neueZeile();
        melde("gut", `<p>✓ ${esc(r.hinweis)}</p>`);
        feld.focus();
      } else if (r.art === "falsch") {
        zustand.fehlversuche++;
        const text = r.fehler ? M.textHTML(r.fehler.hinweis)
          : `<p>Das ist leider nicht derselbe Term. Setz zur Probe eine Zahl ein, z. B. x = 2 – dann muss bei beiden dasselbe herauskommen.</p>`;
        melde("falsch", `${text}<p class="mut">${zufall(TROST)}</p>`);
      } else {
        melde("neutral", `<p>Das kann ich leider nicht lesen. Schreib zum Beispiel <span class="mathe">3<i>x</i> + 6</span> oder <span class="mathe">2(<i>x</i> − 1)</span>.</p>`);
      }
    }

    function pruefeZeile(roh) {
      const [glText, ...kommentar] = roh.split("|");
      const r = M.pruefeGleichungsZeile(glText, a);
      const liste = ort.querySelector("#zeilen");
      const neueZeile = () => {
        const html = M.wegZeileHTML(glText.trim() + (kommentar.length ? " | " + kommentar.join("|") : ""));
        liste.insertAdjacentHTML("beforeend", `<li class="zeile ok">${html}<span class="haken" aria-label="richtig">✓</span></li>`);
        feld.value = "";
        ort.querySelector("#vorschau").innerHTML = "";
      };
      if (r.art === "geloest") {
        neueZeile();
        abschliessen(ergebnisArt(), `<p><strong>${zufall(LOB)}</strong> Die Lösung ist ${M.matheHTML(`x = ${a.loesung}`)}${
          a.anzeige && a.anzeige.includes("=") ? ` (${esc(a.anzeige.split("=")[1].trim())})` : ""}.</p>
          <details class="weg-details"><summary>Musterlösung ansehen</summary>${wegHTML()}</details>
          <p class="mut">${zufall(MUT)}</p>`);
      } else if (r.art === "schritt") {
        neueZeile();
        melde("gut", `<p>✓ Richtig umgeformt. ${zustand.zeilen.push(1) === 1 ? "Schreib die nächste Zeile." : "Weiter so!"}</p>`);
        feld.focus();
      } else if (r.art === "ausrechnen") {
        neueZeile();
        melde("gut", `<p>✓ Stimmt! Rechne das noch aus, dann bist du fertig.</p>`);
        feld.focus();
      } else if (r.art === "falsch") {
        zustand.fehlversuche++;
        const f = r.menge?.art === "eine" ? M.findeFehler(r.menge.x, a.fehler) : null;
        const fertigForm = /^\s*x\s*=\s*[^x]*$/.test(glText) || !/x/.test(glText);
        const text = f ? M.textHTML(f.hinweis)
          : fertigForm ? `<p>Das ist noch nicht die Lösung. Mach die Probe: Setz deine Zahl für x in die Gleichung ein.</p>`
          : `<p>Diese Zeile hat eine andere Lösung als die Zeile davor – beim letzten Schritt ist ein kleiner Fehler passiert. Schau ihn dir noch einmal an.</p>`;
        melde("falsch", `${text}<p class="mut">${zufall(TROST)}</p>`);
      } else {
        melde("neutral", `<p>Das kann ich leider nicht lesen. Schreib zum Beispiel <span class="mathe">3<i>x</i> = 15</span> oder <span class="mathe"><i>x</i> = 5</span>.</p>`);
      }
    }

    function pruefeAntwort(roh) {
      const r = M.pruefeZahl(roh, a.loesung, a.form, a.nenner);
      const einheitText = a.einheit ? " " + esc(a.einheit) : "";
      if (r.art === "form") return melde("neutral", `<p>${esc(r.hinweis)}</p>`);
      if (r.art === "gemischt") return melde("neutral", `<p>Schreib gemischte Zahlen bitte als Bruch: statt 2 1/2 schreibst du 5/2.</p>`);
      if (r.art === "richtig" || r.art === "gerundet") {
        abschliessen(ergebnisArt(), `<p><strong>${zufall(LOB)}</strong> ${M.matheHTML(a.loesung)}${einheitText} stimmt${
          r.art === "gerundet" ? " (du hast sinnvoll gerundet)" : ""}.</p>
          ${a.gleichung ? `<p>Die Gleichung dazu: ${M.matheHTML(a.gleichung)}</p>` : ""}
          ${a.weg?.length ? `<details class="weg-details"><summary>Musterlösung ansehen</summary>${wegHTML()}</details>` : ""}
          ${a.erklaerung ? M.textHTML(a.erklaerung) : ""}
          <p class="mut">${zufall(MUT)}</p>`);
      } else if (r.art === "falsch") {
        zustand.fehlversuche++;
        const f = M.findeFehler(r.wert, a.fehler);
        melde("falsch", `${f ? M.textHTML(f.hinweis) : "<p>Das stimmt noch nicht. Ein Tipp kann helfen!</p>"}<p class="mut">${zufall(TROST)}</p>`);
      } else {
        melde("neutral", `<p>Bitte gib eine Zahl ein, zum Beispiel <span class="mathe">12</span> oder <span class="mathe">6,5</span>.</p>`);
      }
    }
  }

  naechste();
}

// ── Einstellungen / Sichern ──────────────────────────────

function seiteEinstellungen() {
  haupt.innerHTML = `
    <div class="leiste"><a href="#/" class="zurueck">← Start</a></div>
    <h1>Lernstand</h1>
    <section class="karte">
      <h2>Sichern</h2>
      <p>Dein Lernstand ist nur auf diesem Gerät gespeichert. Mit einer Sicherung kannst du ihn aufheben
      oder auf ein anderes Gerät mitnehmen.</p>
      <button class="knopf haupt-knopf" id="export">Sicherung speichern</button>
    </section>
    <section class="karte">
      <h2>Sicherung laden</h2>
      <p>Lädt einen gesicherten Lernstand. Der jetzige wird dabei ersetzt.</p>
      <input type="file" id="import" accept="application/json,.json">
      <div class="rueckmeldung" id="rm-import"></div>
    </section>
    <section class="karte">
      <h2>Von vorne beginnen</h2>
      <button class="knopf leise-knopf" id="reset">Lernstand löschen …</button>
    </section>
    <p class="leise klein-text">Version ${esc(window.APP_VERSION || "")}</p>`;
  haupt.querySelector("#export").addEventListener("click", () => {
    const blob = new Blob([S.exportieren()], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `lernstand-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  });
  haupt.querySelector("#import").addEventListener("change", async (e) => {
    const rm = haupt.querySelector("#rm-import");
    try {
      S.importieren(await e.target.files[0].text());
      rm.className = "rueckmeldung gut";
      rm.textContent = "Lernstand geladen.";
    } catch {
      rm.className = "rueckmeldung falsch";
      rm.textContent = "Diese Datei ist leider keine gültige Sicherung.";
    }
  });
  haupt.querySelector("#reset").addEventListener("click", () => {
    if (confirm("Wirklich den ganzen Lernstand löschen? Das kann man nicht rückgängig machen.")) {
      S.zuruecksetzen();
      geh("#/");
    }
  });
}

// ── Start der App ────────────────────────────────────────

S.dauerhaftAnfragen();
window.addEventListener("hashchange", zeige);
zeige().catch((e) => {
  haupt.innerHTML = `<section class="karte"><h1>Hoppla</h1><p>Die Inhalte konnten nicht geladen werden.</p><p class="leise">${esc(e.message)}</p></section>`;
});
if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("sw.js").catch(() => { /* offline-Cache optional */ });
}
