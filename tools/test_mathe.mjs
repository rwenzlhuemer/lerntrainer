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
        erwarte(letzte ? r.art === "geloest" : ["schritt", "ausrechnen", "geloest"].includes(r.art),
          `${a.id}: Zeile "${zeile}" → ${r.art}`);
      });
      erwarte(M.pruefeGleichungsZeile(`x = ${a.loesung}`, a).art === "geloest", `${a.id}: Lösung nicht erkannt`);
      for (const f of a.fehler || []) {
        const r = M.pruefeGleichungsZeile(`x = ${f.antwort}`, a);
        erwarte(r.art === "falsch", `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
        erwarte(M.findeFehler(r.menge?.x, a.fehler) === f, `${a.id}: Fehler-Hinweis ${f.antwort} nicht gefunden`);
      }
    } else if (a.typ === "zahl") {
      const soll = a.gerundet !== undefined && a.rechnung ? a.rechnung : a.loesung;
      const rl = M.pruefeZahl(a.loesung, soll, a.form, a.nenner, a.gerundet ?? null).art;
      erwarte(rl === "richtig" || (a.gerundet !== undefined && rl === "gerundet"), `${a.id}: Lösung nicht erkannt (${rl})`);
      if (a.gerundet !== undefined && a.rechnung) erwarte(M.pruefeZahl(a.rechnung, soll).art === "richtig", `${a.id}: exakte Rechnung nicht erkannt`);
      if (a.einheit) erwarte(M.pruefeZahl(`${a.loesung} ${a.einheit}`, a.loesung).art === "richtig", `${a.id}: mit Einheit`);
      for (const f of a.fehler || []) {
        const r = M.pruefeZahl(f.antwort, soll, a.form, a.nenner);
        erwarte(r.art === "falsch", `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
      }
      // Bei „gekürzt“ darf die ungekürzte Angabe aus der Aufgabe nicht als fertig gelten
      const roh = a.form === "gekuerzt" && /Kürze so weit wie möglich: `(.+)`/.exec(a.frage)?.[1];
      if (roh) erwarte(M.pruefeZahl(roh, a.loesung, a.form).art === "form", `${a.id}: ungekürzt ${roh} nicht bemängelt`);
    } else if (a.typ === "term") {
      const r = M.pruefeTermZeile(a.loesung, a);
      erwarte(r.art === "geloest", `${a.id}: Lösung ${a.loesung} → ${r.art} ${r.hinweis || ""}`);
      if (a.term && a.form !== "frei") {
        const r0 = M.pruefeTermZeile(a.term, a);
        erwarte(r0.art === "schritt", `${a.id}: Ausgangsterm ${a.term} → ${r0.art} (darf nicht schon fertig sein)`);
      }
      for (const zeile of a.weg || []) {
        for (const teil of zeile.split("|")[0].split("=")) {
          const rt = M.pruefeTermZeile(teil, a);
          erwarte(["schritt", "geloest"].includes(rt.art), `${a.id}: Weg-Teil "${teil.trim()}" → ${rt.art}`);
        }
      }
      for (const f of a.fehler || []) {
        const rf = M.pruefeTermZeile(f.antwort, a);
        erwarte(rf.art === "falsch" && rf.fehler === f, `${a.id}: Fehler-Antwort ${f.antwort} → ${rf.art}`);
      }
    } else if (a.typ === "formel") {
      erwarte(M.pruefeFormelZeile(`${a.nach} = ${a.loesung}`, a).art === "geloest", `${a.id}: Lösung nicht erkannt`);
      erwarte(M.pruefeFormelZeile(a.formel, a).art !== "geloest" || M.lies(a.formel).links.n === a.nach, `${a.id}: Ausgangsformel gilt schon als gelöst`);
      for (const zeile of a.weg || []) {
        const r = M.pruefeFormelZeile(zeile.split("|")[0], a);
        erwarte(["schritt", "geloest"].includes(r.art), `${a.id}: Weg-Zeile "${zeile}" → ${r.art}`);
      }
      for (const f of a.fehler || []) {
        const r = M.pruefeFormelZeile(`${a.nach} = ${f.antwort}`, a);
        erwarte(r.art === "falsch" && r.fehler === f, `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
      }
    } else if (a.typ === "quadratisch") {
      const l = String(a.loesung);
      const eingabe = l === "keine" ? "keine" : l.split(";").map((v) => `x = ${v.trim()}`).join(" oder ");
      erwarte(M.pruefeQuadratischZeile(eingabe, a).art === "geloest", `${a.id}: Lösung ${eingabe} nicht erkannt`);
      if (a.gleichung && !/^x\s*=/.test(a.gleichung) && !/[³⁴]|\^[3-9]/.test(a.gleichung)) erwarte(M.pruefeQuadratischZeile(a.gleichung, a).art === "schritt", `${a.id}: Ausgangsgleichung nicht als Schritt`);
      for (const zeile of a.weg || []) {
        const r = M.pruefeQuadratischZeile(zeile.split("|")[0], a);
        erwarte(["schritt", "geloest"].includes(r.art), `${a.id}: Weg-Zeile "${zeile}" → ${r.art}`);
      }
      for (const f of a.fehler || []) {
        const r = M.pruefeQuadratischZeile(f.antwort === "keine" ? "keine" : f.antwort, a);
        erwarte((r.art === "falsch" && r.fehler === f) || r.art === "teil", `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
      }
    } else if (a.typ === "lgs") {
      const l = a.loesung;
      const eingabe = typeof l === "object" ? `x = ${l.x}, y = ${l.y}` : l === "keine" ? "keine" : "unendlich viele";
      erwarte(M.pruefeLgsZeile(eingabe, a).art === "geloest", `${a.id}: Lösung nicht erkannt`);
      if (typeof l === "object") {
        erwarte(M.pruefeLgsZeile(`(${l.x}|${l.y})`, a).art === "geloest", `${a.id}: Paar nicht erkannt`);
        for (const zeile of a.weg || []) {
          const r = M.pruefeLgsZeile(zeile.split("|")[0], a);
          erwarte(["schritt", "teil", "geloest"].includes(r.art), `${a.id}: Weg-Zeile "${zeile}" → ${r.art}`);
        }
        for (const f of a.fehler || []) erwarte(M.pruefeLgsZeile(`x = ${f.x}, y = ${f.y}`, a).art === "falsch", `${a.id}: Fehler ${f.x}|${f.y} nicht falsch`);
      }
    } else if (a.typ === "ungleichung") {
      erwarte(M.pruefeUngleichungsZeile(a.loesung, a).art === (a.form === "intervall" ? "form" : "geloest"), `${a.id}: Lösung nicht erkannt`);
      erwarte(M.pruefeUngleichungsZeile(M.intervallText(M.ungleichungsMenge(a.loesung).menge), a).art === "geloest", `${a.id}: Intervall nicht erkannt`);
      if (a.ungleichung) erwarte(M.pruefeUngleichungsZeile(a.ungleichung, a).art !== "geloest" || /^x\s*[<>≤≥]/.test(a.ungleichung), `${a.id}: Ausgangsungleichung schon gelöst?`);
      for (const zeile of a.weg || []) {
        const r = M.pruefeUngleichungsZeile(zeile.split("|")[0], a);
        erwarte(["schritt", "geloest", "form"].includes(r.art), `${a.id}: Weg-Zeile "${zeile}" → ${r.art}`);
      }
      for (const f of a.fehler || []) {
        const r = M.pruefeUngleichungsZeile(f.antwort, a);
        erwarte(r.art === "falsch" && r.fehler === f, `${a.id}: Fehler-Antwort ${f.antwort} → ${r.art}`);
      }
    } else if (a.typ === "auswahl" && a.mathe) {
      for (const o of a.optionen) erwarte(M.versuche(o), `${a.id}: Option ${o} nicht lesbar`);
    }
    // Alle Texte müssen sich darstellen lassen
    for (const t of [a.frage, a.erklaerung, ...(a.tipps || [])]) if (t) M.textHTML(t);
  }
}

console.log(`${ok} Prüfungen bestanden, ${fehler.length} Fehler`);
for (const f of fehler.slice(0, 40)) console.log("  ✗", f);
process.exit(fehler.length ? 1 : 0);
