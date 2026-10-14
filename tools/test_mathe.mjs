// Gegenprobe: Die App-Prüflogik (app/js/mathe.js) muss jede vom Build (sympy) bestätigte Aufgabe
// genauso beurteilen. Aufruf nach dem Build:  node tools/test_mathe.mjs
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as M from "../app/js/mathe.js";

const DATEN = join(dirname(fileURLToPath(import.meta.url)), "..", "app", "daten", "mathe");
let ok = 0;
const fehler = [];
const erwarte = (bed, was) => (bed ? ok++ : fehler.push(was));

// Einzelfälle der Eingabe-Toleranz
const g = { loesung: "5" };
for (const e of ["x = 5", "x=5", "5", "5 = x", "L = {5}", "x = 5,0", "x = 10/2"]) {
  const r = M.pruefeGleichungsZeile(e, g);
  erwarte(e === "x = 10/2" ? r.art === "ausrechnen" : r.art === "geloest", `Eingabe "${e}" → ${r.art}`);
}
erwarte(M.pruefeGleichungsZeile("x = 5/2", { loesung: "5/2" }).art === "geloest", "x = 5/2");
erwarte(M.pruefeGleichungsZeile("x = 2,5", { loesung: "5/2" }).art === "geloest", "x = 2,5");
erwarte(M.pruefeGleichungsZeile("3x = 15", { loesung: "5" }).art === "schritt", "3x = 15 Schritt");
erwarte(M.pruefeGleichungsZeile("3x = 17", { loesung: "5" }).art === "falsch", "3x = 17 falsch");
erwarte(M.pruefeGleichungsZeile("x²+1=2", { loesung: "5" }).art === "unklar", "quadratisch unklar");
erwarte(M.pruefeGleichungsZeile("3·x − 2 = 13", { loesung: "5" }).art === "schritt", "Sonderzeichen");
erwarte(M.pruefeGleichungsZeile("3(x+1) = 18", { loesung: "5" }).art === "schritt", "Klammer");
erwarte(M.pruefeZahl("12 €", "12").art === "richtig", "Einheit €");
erwarte(M.pruefeZahl("x = 55 Minuten", "55").art === "richtig", "x = 55 Minuten");
erwarte(M.pruefeZahl("3 500", "3500").art === "richtig", "Tausender-Leerzeichen");
erwarte(M.pruefeZahl("4,47", "4,4666").art !== "richtig", "gerundet ist nicht exakt");
erwarte(M.matheHTML("x/2 + 1 = 3").includes("bruch"), "Bruch-Darstellung");

for (const datei of readdirSync(DATEN)) {
  if (datei === "lernpfad.json") continue;
  const ls = JSON.parse(readFileSync(join(DATEN, datei), "utf-8"));
  for (const a of ls.aufgaben) {
    if (a.typ === "gleichung") {
      erwarte(M.versuche(a.gleichung)?.gleichung, `${a.id}: Gleichung nicht lesbar`);
      a.weg.forEach((zeile, i) => {
        const gl = zeile.split("|")[0].trim();
        const r = M.pruefeGleichungsZeile(gl, a);
        const letzte = i === a.weg.length - 1;
        erwarte(letzte ? r.art === "geloest" : ["schritt", "geloest"].includes(r.art),
          `${a.id}: Zeile "${zeile}" → ${r.art}`);
      });
      erwarte(M.pruefeGleichungsZeile(`x = ${a.loesung}`, a).art === "geloest", `${a.id}: Lösung nicht erkannt`);
      for (const f of a.fehler || []) {
        const r = M.pruefeGleichungsZeile(`x = ${f.antwort}`, a);
        erwarte(r.art === "falsch", `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
        erwarte(M.findeFehler(r.menge?.x, a.fehler) === f, `${a.id}: Fehler-Hinweis ${f.antwort} nicht gefunden`);
      }
    } else if (a.typ === "zahl") {
      erwarte(M.pruefeZahl(a.loesung, a.loesung).art === "richtig", `${a.id}: Lösung nicht erkannt`);
      if (a.einheit) erwarte(M.pruefeZahl(`${a.loesung} ${a.einheit}`, a.loesung).art === "richtig", `${a.id}: mit Einheit`);
      for (const f of a.fehler || []) {
        const r = M.pruefeZahl(f.antwort, a.loesung);
        erwarte(r.art === "falsch", `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
      }
    }
    // Alle Texte müssen sich darstellen lassen
    for (const t of [a.frage, a.erklaerung, ...(a.tipps || [])]) if (t) M.textHTML(t);
  }
}

console.log(`${ok} Prüfungen bestanden, ${fehler.length} Fehler`);
for (const f of fehler.slice(0, 40)) console.log("  ✗", f);
process.exit(fehler.length ? 1 : 0);
