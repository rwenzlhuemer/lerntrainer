// Mathe-Kern: Schulnotation lesen, schön anzeigen, prüfen.
// Versteht dieselbe Schreibweise wie tools/notation.py:
//   3x + 5 = 20   2,5·x   x²   x^2   (x − 1):2   x/3   √(x)

// ── Lesen ────────────────────────────────────────────────

const HOCH = { "²": "2", "³": "3", "⁴": "4" };
const FUNKTIONEN = new Set(["sqrt", "sin", "cos", "tan", "ln", "log"]);
const KONSTANTEN = { pi: Math.PI, "π": Math.PI, e: Math.E };

export function normalisiere(text) {
  return String(text)
    .replace(/[−–—]/g, "-")
    .replace(/[·×*⋅]/g, "*")
    .replace(/[:÷]/g, "/")
    .replace(/(\d),(?=\d)/g, "$1.")
    .replace(/√/g, " √ ")
    .trim();
}

function tokenisiere(text) {
  const t = normalisiere(text);
  const tokens = [];
  let i = 0;
  while (i < t.length) {
    const c = t[i];
    if (/\s/.test(c)) { i++; continue; }
    if (/[\d.]/.test(c)) {
      let j = i;
      while (j < t.length && /[\d.]/.test(t[j])) j++;
      const s = t.slice(i, j);
      if ((s.match(/\./g) || []).length > 1 || s === ".") throw new Error("Zahl");
      tokens.push({ art: "zahl", wert: parseFloat(s), text: s });
      i = j; continue;
    }
    if (HOCH[c]) {
      tokens.push({ art: "op", wert: "^" }, { art: "zahl", wert: parseFloat(HOCH[c]), text: HOCH[c] });
      i++; continue;
    }
    if (/[a-zA-Zπ]/.test(c)) {
      let j = i;
      while (j < t.length && /[a-zA-Zπ]/.test(t[j])) j++;
      const wort = t.slice(i, j);
      if (FUNKTIONEN.has(wort) || wort in KONSTANTEN) {
        tokens.push({ art: FUNKTIONEN.has(wort) ? "fn" : "konst", wert: wort });
      } else {
        // „xy“ = x · y; jede Variable ist ein Buchstabe
        for (const b of wort) tokens.push({ art: "var", wert: b });
      }
      i = j; continue;
    }
    if (c === "√") { tokens.push({ art: "fn", wert: "sqrt" }); i++; continue; }
    if ("+-*/^()=".includes(c)) { tokens.push({ art: c === "=" ? "gleich" : "op", wert: c }); i++; continue; }
    if (c === "[" || c === "{") { tokens.push({ art: "op", wert: "(" }); i++; continue; }
    if (c === "]" || c === "}") { tokens.push({ art: "op", wert: ")" }); i++; continue; }
    throw new Error("Zeichen " + c);
  }
  return tokens;
}

class Leser {
  constructor(tokens) { this.t = tokens; this.i = 0; }
  sieh() { return this.t[this.i]; }
  nimm() { return this.t[this.i++]; }
  istOp(w) { const k = this.sieh(); return k && k.art === "op" && k.wert === w; }

  ausdruck() {
    let a = this.produkt();
    while (this.istOp("+") || this.istOp("-")) {
      const op = this.nimm().wert;
      a = { t: "bin", op, a, b: this.produkt() };
    }
    return a;
  }

  produkt() {
    let a = this.vorzeichen();
    for (;;) {
      if (this.istOp("*") || this.istOp("/")) {
        const op = this.nimm().wert;
        a = { t: "bin", op, a, b: this.vorzeichen() };
      } else if (this.beginntFaktor()) {
        a = { t: "bin", op: "*", impl: true, a, b: this.potenz() };
      } else return a;
    }
  }

  beginntFaktor() {
    const k = this.sieh();
    return k && (k.art === "zahl" || k.art === "var" || k.art === "fn" || k.art === "konst" ||
      (k.art === "op" && k.wert === "("));
  }

  vorzeichen() {
    if (this.istOp("-")) { this.nimm(); return { t: "neg", a: this.vorzeichen() }; }
    if (this.istOp("+")) { this.nimm(); return this.vorzeichen(); }
    return this.potenz();
  }

  potenz() {
    const basis = this.atom();
    if (this.istOp("^")) { this.nimm(); return { t: "bin", op: "^", a: basis, b: this.vorzeichen() }; }
    return basis;
  }

  atom() {
    const k = this.nimm();
    if (!k) throw new Error("Ende");
    if (k.art === "zahl") return { t: "zahl", v: k.wert, s: k.text };
    if (k.art === "var") return { t: "var", n: k.wert };
    if (k.art === "konst") return { t: "konst", n: k.wert };
    if (k.art === "fn") {
      if (this.istOp("(")) return { t: "fn", n: k.wert, a: this.atom() };
      return { t: "fn", n: k.wert, a: this.potenz() };
    }
    if (k.art === "op" && k.wert === "(") {
      const a = this.ausdruck();
      if (!this.istOp(")")) throw new Error("Klammer");
      this.nimm();
      return { t: "klammer", a };
    }
    throw new Error("Unerwartet");
  }
}

export function lies(text) {
  const tokens = tokenisiere(text);
  const seiten = [[]];
  for (const k of tokens) {
    if (k.art === "gleich") seiten.push([]);
    else seiten[seiten.length - 1].push(k);
  }
  if (seiten.length > 2) throw new Error("zu viele =");
  const baeume = seiten.map((s) => {
    if (!s.length) throw new Error("leer");
    const l = new Leser(s);
    const b = l.ausdruck();
    if (l.i < s.length) throw new Error("Rest");
    return b;
  });
  return baeume.length === 2 ? { gleichung: true, links: baeume[0], rechts: baeume[1] }
                             : { gleichung: false, term: baeume[0] };
}

export function versuche(text) {
  try { return lies(text); } catch { return null; }
}

// ── Rechnen ──────────────────────────────────────────────

export function werte(b, env = {}) {
  switch (b.t) {
    case "zahl": return b.v;
    case "var": if (!(b.n in env)) throw new Error("Variable " + b.n); return env[b.n];
    case "konst": return KONSTANTEN[b.n];
    case "klammer": return werte(b.a, env);
    case "neg": return -werte(b.a, env);
    case "fn": {
      const a = werte(b.a, env);
      return { sqrt: Math.sqrt, sin: Math.sin, cos: Math.cos, tan: Math.tan, ln: Math.log, log: Math.log10 }[b.n](a);
    }
    case "bin": {
      const a = werte(b.a, env), c = werte(b.b, env);
      return { "+": a + c, "-": a - c, "*": a * c, "/": a / c, "^": Math.pow(a, c) }[b.op];
    }
  }
  throw new Error("Knoten");
}

export function variablen(b, menge = new Set()) {
  if (!b) return menge;
  if (b.t === "var") menge.add(b.n);
  for (const k of ["a", "b"]) if (b[k]) variablen(b[k], menge);
  return menge;
}

export function zahlwert(text) {
  const g = versuche(text);
  if (!g || g.gleichung) return null;
  try { const v = werte(g.term); return Number.isFinite(v) ? v : null; } catch { return null; }
}

// ── Anzeigen ─────────────────────────────────────────────

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function zahlText(b) {
  return esc(b.s.replace(".", ","));
}

function ohneKlammer(b) { return b.t === "klammer" ? b.a : b; }

function zeige(b) {
  switch (b.t) {
    case "zahl": return zahlText(b);
    case "var": return `<i>${esc(b.n)}</i>`;
    case "konst": return b.n === "pi" ? "π" : `<i>${esc(b.n)}</i>`;
    case "klammer": return `(${zeige(b.a)})`;
    case "neg": return `−${zeige(b.a)}`;
    case "fn":
      if (b.n === "sqrt") return `√<span class="wurzel">${zeige(ohneKlammer(b.a))}</span>`;
      return `${b.n}(${zeige(ohneKlammer(b.a))})`;
    case "bin":
      if (b.op === "+") return `${zeige(b.a)} + ${zeige(b.b)}`;
      if (b.op === "-") return `${zeige(b.a)} − ${zeige(b.b)}`;
      if (b.op === "*") return b.impl ? `${zeige(b.a)}${zeige(b.b)}` : `${zeige(b.a)} · ${zeige(b.b)}`;
      if (b.op === "/") {
        return `<span class="bruch"><span class="zaehler">${zeige(ohneKlammer(b.a))}</span>` +
               `<span class="nenner">${zeige(ohneKlammer(b.b))}</span></span>`;
      }
      if (b.op === "^") return `${zeige(b.a)}<sup>${zeige(ohneKlammer(b.b))}</sup>`;
  }
  return "";
}

// Mathe-Text als HTML; wenn nicht lesbar, als Text mit schönen Zeichen.
export function matheHTML(text) {
  // Auch Ketten wie „2 · 4 + 3 = 8 + 3 = 11“ setzen
  const teile = String(text).split("=").map((t) => versuche(t));
  if (teile.some((g) => !g || g.gleichung)) return esc(schoeneZeichen(text));
  return `<span class="mathe">${teile.map((g) => zeige(g.term)).join(" = ")}</span>`;
}

export function schoeneZeichen(text) {
  return String(text)
    .replace(/(^|[\s(=])-(?=[\dx(])/g, "$1−")
    .replace(/ - /g, " − ")
    .replace(/\*/g, "·");
}

// Lösungsweg-Zeile „3x = 15 | −5“ → Gleichung + Kommentar
export function wegZeileHTML(zeile) {
  const [gl, ...rest] = String(zeile).split("|");
  const kommentar = rest.join("|").trim();
  return `<span class="weg-gl">${matheHTML(gl.trim())}</span>` +
    (kommentar ? `<span class="weg-op">| ${esc(schoeneZeichen(kommentar))}</span>` : "");
}

// Fließtext mit **fett**, *kursiv*, `Mathe` und Absätzen.
// Umbrüche im Quelltext sind nur Zeilenumbruch im Editor – außer vor Aufzählungen („1. “, „- “, „→ “).
export function textHTML(text) {
  if (!text) return "";
  const absaetze = String(text).trim().split(/\n\s*\n/);
  return absaetze.map((a) => {
    const html = a.split("\n").map((z) => z.trim())
      .reduce((acc, z) => acc + (acc && /^(\d+\.|[-•→])\s/.test(z) ? "<br>" : acc ? " " : "") + inline(z), "");
    return `<p>${html}</p>`;
  }).join("");
}

function inline(s) {
  const teile = s.split("`");
  return teile.map((t, i) => {
    if (i % 2 === 1) return matheHTML(t);
    const h = esc(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|\s)\*(\S.*?)\*/g, "$1<em>$2</em>");
    return schoeneZeichen(h);
  }).join("");
}

// ── Prüfen ───────────────────────────────────────────────

const EPS = 1e-9;

function nahe(a, b, rel = EPS) {
  return Math.abs(a - b) <= rel * Math.max(1, Math.abs(a), Math.abs(b));
}

// Lösungsmenge einer linearen Gleichung in x: {art: "eine", x} | {art: "keine"} | {art: "alle"} | null
export function loesungLinear(g, variable = "x") {
  const f = (x) => werte(g.links, { [variable]: x }) - werte(g.rechts, { [variable]: x });
  let w0, w1, w2, w3;
  try { w0 = f(0); w1 = f(1); w2 = f(2); w3 = f(-3); } catch { return null; }
  if (![w0, w1, w2, w3].every(Number.isFinite)) return null;
  const k = w1 - w0;
  const linear = nahe(w2, w0 + 2 * k, 1e-7) && nahe(w3, w0 - 3 * k, 1e-7);
  if (!linear) return null;
  if (nahe(k, 0, 1e-10)) return nahe(w0, 0, 1e-10) ? { art: "alle" } : { art: "keine" };
  return { art: "eine", x: -w0 / k };
}

export function sollMenge(loesung) {
  const s = String(loesung).trim();
  if (s === "keine") return { art: "keine" };
  if (s === "alle") return { art: "alle" };
  return { art: "eine", x: zahlwert(s) };
}

function gleicheMenge(a, b) {
  if (!a || !b || a.art !== b.art) return false;
  return a.art !== "eine" || nahe(a.x, b.x, 1e-9);
}

const WORT_KEINE = /^(l\s*=\s*)?(\{\s*\}|∅|keine( lösung)?|leer)$/i;
const WORT_ALLE = /^(l\s*=\s*)?(ℝ|r|alle( zahlen)?|unendlich( viele)?( lösungen)?)$/i;

// Prüft eine eingegebene Zeile bei einer Gleichungsaufgabe.
// Ergebnis: {art: "geloest"|"schritt"|"falsch"|"ausrechnen"|"unklar", menge?}
export function pruefeGleichungsZeile(eingabe, aufgabe) {
  const soll = sollMenge(aufgabe.loesung);
  const roh = eingabe.trim();
  if (WORT_KEINE.test(roh)) return { art: soll.art === "keine" ? "geloest" : "falsch", menge: { art: "keine" } };
  if (WORT_ALLE.test(roh)) return { art: soll.art === "alle" ? "geloest" : "falsch", menge: { art: "alle" } };

  // „L = {5}“ oder „5“ allein → x = 5
  const lMenge = roh.match(/^l\s*=\s*\{(.+)\}$/i);
  let text = lMenge ? `x = ${lMenge[1]}` : roh;
  const g0 = versuche(text);
  if (!g0) return { art: "unklar" };
  if (!g0.gleichung) {
    if (variablen(g0.term).size) return { art: "unklar" };
    text = `x = ${text}`;
  }
  const g = lies(text);
  const menge = loesungLinear(g);
  if (!menge) return { art: "unklar" };
  if (!gleicheMenge(menge, soll)) return { art: "falsch", menge };

  // äquivalent – ist x schon isoliert?
  const [seiteX, seiteZahl] = istVar(g.links) ? [g.links, g.rechts] : istVar(g.rechts) ? [g.rechts, g.links] : [null, null];
  if (seiteX && variablen(seiteZahl).size === 0) {
    // „x = 5“ und „x = 5/2“ sind fertig; „x = 15 : 3“ oder „x = 12 − 7“ noch ausrechnen
    const ganz = Number.isInteger(Math.round(werte(seiteZahl) * 1e9) / 1e9);
    if (istZahl(seiteZahl) || (istBruch(seiteZahl) && !ganz)) return { art: "geloest", menge };
    return { art: "ausrechnen", menge };
  }
  return { art: "schritt", menge };
}

function istVar(b) { return b.t === "var" && b.n === "x"; }

function istZahl(b) {
  if (b.t === "zahl") return true;
  return (b.t === "neg" || b.t === "klammer") && istZahl(b.a);
}

function istBruch(b) {
  if (b.t === "neg" || b.t === "klammer") return istBruch(b.a);
  return b.t === "bin" && b.op === "/" && istZahl(b.a) && istZahl(b.b);
}

// Zahl-Antwort: Einheiten und „x =“ werden toleriert.
// Ergebnis: {art: "richtig"|"gerundet"|"falsch"|"unklar", wert?}
export function pruefeZahl(eingabe, loesung) {
  let t = String(eingabe).trim();
  if (t.includes("=")) t = t.slice(t.lastIndexOf("=") + 1);
  t = t.replace(/[a-zA-ZäöüÄÖÜß€%]+\.?/g, " ").replace(/\s+/g, " ").trim();
  // Tausender-Leerzeichen: „3 500“ → 3500
  t = t.replace(/(\d) (?=\d{3}\b)/g, "$1");
  const ist = zahlwert(t);
  const soll = zahlwert(loesung);
  if (ist === null) return { art: "unklar" };
  if (nahe(ist, soll)) return { art: "richtig", wert: ist };
  // Gerundet gilt nur, wenn die eingegebenen Nachkommastellen passen: 4,47 für 4,4666…, nicht 4
  const stellen = (normalisiere(t).match(/\.(\d+)/) || [, ""])[1].length;
  if (stellen > 0 && Math.abs(ist - soll) <= 0.5 * 10 ** -stellen + EPS) return { art: "gerundet", wert: ist };
  return { art: "falsch", wert: ist };
}

// Passt ein Wert zu einer vorbereiteten Fehler-Antwort?
export function findeFehler(wert, fehlerListe) {
  if (wert === null || wert === undefined || !fehlerListe) return null;
  for (const f of fehlerListe) {
    const v = zahlwert(f.antwort);
    if (v !== null && Math.abs(v - wert) <= 0.002 * Math.max(1, Math.abs(v))) return f;
  }
  return null;
}
