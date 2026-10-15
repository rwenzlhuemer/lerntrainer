// Mathe-Kern: Schulnotation lesen, schön anzeigen, prüfen.
// Versteht dieselbe Schreibweise wie tools/notation.py:
//   3x + 5 = 20   2,5·x   x²   x^2   (x − 1):2   x/3   √(x)

// ── Lesen ────────────────────────────────────────────────

const HOCH = { "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-" };
const FUNKTIONEN = new Set(["sqrt", "sin", "cos", "tan", "ln", "log"]);
const KONSTANTEN = { pi: Math.PI, "π": Math.PI, e: Math.E };

export function normalisiere(text) {
  return String(text)
    .replace(/[−–—]/g, "-")
    .replace(/[·×*⋅]/g, "*")
    .replace(/[:÷]/g, ":")
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
      // Hochgestellte Ziffern: x¹² → x^12, x⁻² → x^(-2)
      let j = i, s = "";
      while (j < t.length && HOCH[t[j]]) s += HOCH[t[j++]];
      const neg = s.startsWith("-"), ziffern = s.replace(/-/g, "");
      if (!ziffern) throw new Error("Hochzahl");
      tokens.push({ art: "op", wert: "^" });
      if (neg) tokens.push({ art: "op", wert: "-" });
      tokens.push({ art: "zahl", wert: parseFloat(ziffern), text: ziffern });
      i = j; continue;
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
    if ("+-*/:^()=".includes(c)) { tokens.push({ art: c === "=" ? "gleich" : "op", wert: c }); i++; continue; }
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
      } else if (this.istOp(":")) {
        this.nimm();
        a = { t: "bin", op: ":", a, b: this.zahlenbruchOderVorzeichen() };
      } else if (this.beginntFaktor()) {
        a = { t: "bin", op: "*", impl: true, a, b: this.potenz() };
      } else return a;
    }
  }

  // „3/4 : 2/5“ – ein Zahlenbruch nach „:“ gehört zusammen (sonst ((3/4):2)/5)
  zahlenbruchOderVorzeichen() {
    const [k0, k1, k2, k3] = this.t.slice(this.i, this.i + 4);
    if (k0?.art === "zahl" && k1?.art === "op" && k1.wert === "/" && k2?.art === "zahl" && !(k3?.art === "op" && k3.wert === "^")) {
      this.i += 3;
      return { t: "bin", op: "/", a: { t: "zahl", v: k0.wert, s: k0.text }, b: { t: "zahl", v: k2.wert, s: k2.text } };
    }
    return this.vorzeichen();
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
      return { "+": a + c, "-": a - c, "*": a * c, "/": a / c, ":": a / c, "^": Math.pow(a, c) }[b.op];
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
      if (b.op === ":") return `${zeige(b.a)} : ${zeige(b.b)}`;
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

const ggT = (a, b) => (b ? ggT(b, a % b) : Math.abs(a));

// Bruch in der Eingabe: „-3/4“ → {z: -3, n: 4}; ganze Zahl → {z, n: 1}; sonst null
export function bruchForm(text) {
  const t = normalisiere(text).replace(/\s+/g, "");
  let m = t.match(/^\(?([+-]?\d+)\)?$/);
  if (m) return { z: Number(m[1]), n: 1 };
  m = t.match(/^([+-]?)\(?([+-]?\d+)\)?\/\(?([+-]?\d+)\)?$/);
  if (!m) return null;
  let z = Number(m[2]), n = Number(m[3]);
  if (m[1] === "-") z = -z;
  if (n < 0) { z = -z; n = -n; }
  return n ? { z, n } : null;
}

// Verlangte Schreibweise bei Zahl-Aufgaben. null = passt, sonst ein freundlicher Hinweis.
function zahlFormHinweis(t, form, nenner) {
  const b = bruchForm(t);
  if (form === "gekuerzt") {
    if (!b) return "Das stimmt! Schreib das Ergebnis aber als Bruch, zum Beispiel 3/4.";
    if (ggT(b.z, b.n) > 1) return `Das stimmt! Du kannst aber noch kürzen – Zähler und Nenner sind beide durch ${ggT(b.z, b.n)} teilbar.`;
  }
  if (form === "nenner" && (!b || b.n !== Number(nenner))) {
    return `Der Wert stimmt – gefragt ist aber ein Bruch mit dem Nenner ${nenner}.`;
  }
  if (form === "dezimal" && /\//.test(t)) return "Das stimmt! Schreib es aber als Dezimalzahl, zum Beispiel 0,75.";
  if (form === "gleitkomma") {
    const m = normalisiere(t).replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+/g, (h) => "^" + [...h].map((z) => HOCH[z]).join("")).replace(/\s+/g, "").match(/^-?(\d+(?:\.\d+)?)\*10\^\(?-?\d+\)?$/);
    if (!m) return "Das stimmt! Schreib es aber in Gleitkommadarstellung, zum Beispiel 4,5 · 10^-3.";
    if (Number(m[1]) < 1 || Number(m[1]) >= 10) return "Fast: Vor dem Mal muss eine Zahl zwischen 1 und 10 stehen, zum Beispiel 4,5 · 10^-3.";
  }
  return null;
}

// Zahl-Antwort: Einheiten und „x =“ werden toleriert.
// Ergebnis: {art: "richtig"|"gerundet"|"form"|"gemischt"|"falsch"|"unklar", wert?, hinweis?}
export function pruefeZahl(eingabe, loesung, form = null, nenner = null) {
  let t = String(eingabe).trim();
  if (t.includes("=")) t = t.slice(t.lastIndexOf("=") + 1);
  t = t.replace(/[a-zA-ZäöüÄÖÜßµ€%°]+[²³]?(\s*\/\s*[a-zA-Z]+[²³]?)?\.?/g, " ").replace(/\s+/g, " ").trim();
  // Gemischte Zahl „2 1/2“ würde sonst als 2 · 1/2 gelesen
  if (/^[+-−]?\d+ \d+\s*\/\s*\d+$/.test(t)) return { art: "gemischt" };
  // Tausender-Leerzeichen: „3 500“ → 3500
  t = t.replace(/(\d) (?=\d{3}\b)/g, "$1");
  const ist = zahlwert(t);
  const soll = zahlwert(loesung);
  if (ist === null) return { art: "unklar" };
  if (nahe(ist, soll)) {
    const hinweis = form ? zahlFormHinweis(t, form, nenner) : null;
    return hinweis ? { art: "form", wert: ist, hinweis } : { art: "richtig", wert: ist };
  }
  if (form === "gekuerzt" || form === "nenner") return { art: "falsch", wert: ist }; // exakt gefragt, nicht gerundet
  // Gerundet gilt nur, wenn die eingegebenen Nachkommastellen passen: 4,47 für 4,4666…, nicht 4
  const stellen = (normalisiere(t).match(/\.(\d+)/) || [, ""])[1].length;
  if (stellen > 0 && Math.abs(ist - soll) <= 0.5 * 10 ** -stellen + EPS) return { art: "gerundet", wert: ist };
  return { art: "falsch", wert: ist };
}

// ── Terme ────────────────────────────────────────────────
// Zwei Terme sind gleich, wenn sie an mehreren „krummen“ Stellen denselben Wert haben.

const PROBE = [1.37, -2.21, 0.73, 3.11, -0.59, 2.47];

export function termGleich(t1, t2) {
  const vars = [...new Set([...variablen(t1), ...variablen(t2)])].sort();
  let gueltig = 0;
  for (let i = 0; i < PROBE.length; i++) {
    const env = {};
    vars.forEach((v, j) => { env[v] = PROBE[(i + 2 * j) % PROBE.length] + 0.11 * j; });
    let a, b;
    try { a = werte(t1, env); b = werte(t2, env); } catch { return false; }
    if (!Number.isFinite(b)) continue; // Definitionslücke der Lösung
    if (!Number.isFinite(a) || !nahe(a, b, 1e-8)) return false;
    gueltig++;
  }
  return gueltig >= 3;
}

const ohneHuelle = (b) => (b.t === "klammer" || b.t === "neg" ? ohneHuelle(b.a) : b);

function summanden(b) {
  b = b.t === "klammer" ? b.a : b;
  if (b.t === "neg") return summanden(b.a);
  if (b.t === "bin" && (b.op === "+" || b.op === "-")) return summanden(b.a) + summanden(b.b);
  return 1;
}

function vorkommen(b) {
  if (b.t === "var") return 1;
  return (b.a ? vorkommen(b.a) : 0) + (b.b ? vorkommen(b.b) : 0);
}

function zahlAnzahl(b) {
  if (b.t === "zahl") return 1;
  if (b.t === "bin" && b.op === "^") return zahlAnzahl(b.a);
  return (b.a ? zahlAnzahl(b.a) : 0) + (b.b ? zahlAnzahl(b.b) : 0);
}

function enthaelt(b, pruef) {
  return pruef(b) || (b.a ? enthaelt(b.a, pruef) : false) || (b.b ? enthaelt(b.b, pruef) : false);
}

function zahlenSumme(b) {
  if (b.t === "zahl") return Math.abs(b.v);
  if (b.t === "bin" && b.op === "^") return zahlenSumme(b.a); // Hochzahlen zählen nicht
  return (b.a ? zahlenSumme(b.a) : 0) + (b.b ? zahlenSumme(b.b) : 0);
}

// Steht noch eine Klammer mit einer Summe und einer Variablen darin? (Hochzahl-Klammern zählen nicht)
function klammerOffen(b) {
  if (b.t === "klammer" && summanden(b.a) > 1 && variablen(b.a).size) return true;
  if (b.t === "bin" && b.op === "/") return klammerOffen(b.a) || klammerOffen(b.b);
  return (b.a ? klammerOffen(b.a) : false) || (b.b ? klammerOffen(b.b) : false);
}

// Faktoren eines Produkts: 6ab(2a − 3b) → [6, a, b, (2a − 3b)]; (x + 3)² → [(x + 3), (x + 3)]
function faktoren(b) {
  if (b.t === "klammer" && summanden(b.a) === 1) return faktoren(b.a);
  if (b.t === "neg") return faktoren(b.a);
  if (b.t === "bin" && b.op === "*") return [...faktoren(b.a), ...faktoren(b.b)];
  if (b.t === "bin" && b.op === "^" && b.b.t === "zahl" && Number.isInteger(b.b.v) && b.b.v >= 1 && b.b.v <= 4) {
    return Array(b.b.v).fill(0).flatMap(() => faktoren(b.a));
  }
  return [b];
}

const produkt = (liste) => liste.reduce((p, f) => ({ t: "bin", op: "*", a: p, b: f }), { t: "zahl", v: 1, s: "1" });
const plusMinusGleich = (t, soll) => termGleich(t, soll) || termGleich({ t: "neg", a: t }, soll);

// Ist der (schon als gleichwertig erkannte) Term in der verlangten Form? null = ja, sonst Hinweis.
export function termFormHinweis(ist, soll, form, faktor) {
  if (form === "frei") return null;
  if (form === "zusammengefasst" || form === "ausmultipliziert") {
    if (klammerOffen(ist)) return "Stimmt! Jetzt noch die Klammer auflösen.";
    if (summanden(ist) > summanden(soll) || vorkommen(ist) > vorkommen(soll)) return "Stimmt! Jetzt noch gleichartige Glieder zusammenfassen.";
    return null;
  }
  if (form === "gekuerzt") {
    if (summanden(ist) > summanden(soll) || vorkommen(ist) > vorkommen(soll) || zahlenSumme(ist) > zahlenSumme(soll) + 1e-9) {
      return "Stimmt! Das lässt sich aber noch weiter vereinfachen oder kürzen.";
    }
    return null;
  }
  if (form === "potenz") {
    // Jede Variable nur einmal, keine Klammer, keine Bruchstriche mehr als nötig, Zahlen ausgerechnet
    const brueche = (x) => (enthaelt(x, (k) => k.t === "bin" && (k.op === "/" || k.op === ":")) ? 1 : 0);
    const klammer = (x) => enthaelt(x, (k) => k.t === "klammer" && !(k.a.t === "neg" && k.a.a.t === "zahl"));
    const klammerSoll = klammer(soll);
    if ((!klammerSoll && klammer(ist)) || vorkommen(ist) > vorkommen(soll) || brueche(ist) > brueche(soll) ||
        zahlAnzahl(ist) > zahlAnzahl(soll)) {
      return "Stimmt! Wende die Potenzregeln noch weiter an, bis jede Variable nur einmal vorkommt.";
    }
    return null;
  }
  if (form === "faktor") {
    if (summanden(ohneHuelle(ist)) > 1 || ohneHuelle(ist).t !== "bin" && ohneHuelle(ist).t !== "klammer") {
      return "Stimmt – aber das ist noch eine Summe. Gesucht ist ein Produkt, also etwas wie 3(2x + 1).";
    }
    const f = faktoren(ist);
    const ziel = lies(faktor).term;
    const einzeln = f.filter((k) => summanden(k) === 1);
    if (plusMinusGleich(produkt(einzeln), ziel) || f.some((k) => summanden(k) > 1 && plusMinusGleich(k, ziel))) return null;
    return "Stimmt – du kannst aber noch mehr herausheben. Schau, was in allen Gliedern steckt.";
  }
  return null;
}

// Prüft eine Zeile bei einer Term-Aufgabe („Vereinfache …“). Führendes „=“ und „Term =“ werden toleriert.
// Ergebnis: {art: "geloest"|"schritt"|"falsch"|"unklar", hinweis?, fehler?}
export function pruefeTermZeile(eingabe, aufgabe) {
  let t = String(eingabe).trim();
  if (t.includes("=")) t = t.slice(t.lastIndexOf("=") + 1);
  const g = versuche(t);
  if (!t.trim() || !g || g.gleichung) return { art: "unklar" };
  const soll = lies(aufgabe.loesung).term;
  if (!termGleich(g.term, soll)) {
    const f = (aufgabe.fehler || []).find((x) => { const h = versuche(x.antwort); return h && termGleich(g.term, h.term); });
    return { art: "falsch", fehler: f || null };
  }
  const hinweis = termFormHinweis(g.term, soll, aufgabe.form || "frei", aufgabe.faktor);
  return hinweis ? { art: "schritt", hinweis } : { art: "geloest" };
}

// ── Formeln umformen ─────────────────────────────────────
// Eine Zeile ist richtig umgeformt, wenn sie stimmt, sobald man für die gesuchte Variable die Lösung einsetzt.

// Positive Probestellen, gut gestreut – damit auch √(c² − b²) genug gültige Stellen hat
const POSITIV_PROBEN = 24;
const positivProbe = (i, j) => 0.4 + ((i * 7 + j * 11) % 19) * 0.37 + 0.013 * j;

function stimmtMitLoesung(g, nach, soll) {
  const vars = [...new Set([...variablen(g.links), ...variablen(g.rechts), ...variablen(soll)])].filter((v) => v !== nach).sort();
  let gueltig = 0;
  for (let i = 0; i < POSITIV_PROBEN; i++) {
    const env = {};
    vars.forEach((v, j) => { env[v] = positivProbe(i, j); });
    let l, r;
    try { env[nach] = werte(soll, env); l = werte(g.links, env); r = werte(g.rechts, env); } catch { return false; }
    if (!Number.isFinite(env[nach])) continue;
    if (!Number.isFinite(l) || !Number.isFinite(r) || !nahe(l, r, 1e-8)) return false;
    gueltig++;
  }
  return gueltig >= 3;
}

// Ergebnis: {art: "geloest"|"schritt"|"falsch"|"unklar", fehler?}
export function pruefeFormelZeile(eingabe, aufgabe) {
  const nach = aufgabe.nach;
  let t = String(eingabe).trim();
  if (!t.includes("=")) t = `${nach} = ${t}`;
  const g = versuche(t);
  if (!g || !g.gleichung) return { art: "unklar" };
  const soll = lies(aufgabe.loesung).term;
  const allein = (s) => s.t === "var" && s.n === nach;
  const andere = allein(g.links) ? g.rechts : allein(g.rechts) ? g.links : null;
  if (andere && !variablen(andere).has(nach)) {
    if (termGleichPositiv(andere, soll)) return { art: "geloest" };
    const f = (aufgabe.fehler || []).find((x) => { const h = versuche(x.antwort); return h && termGleichPositiv(andere, h.term); });
    return { art: "falsch", fehler: f || null };
  }
  return stimmtMitLoesung(g, nach, soll) ? { art: "schritt" } : { art: "falsch", fehler: null };
}

// Wie termGleich, aber nur an positiven Stellen (Formeln mit Wurzeln: Längen, Flächen sind positiv)
function termGleichPositiv(t1, t2) {
  const vars = [...new Set([...variablen(t1), ...variablen(t2)])].sort();
  let gueltig = 0;
  for (let i = 0; i < POSITIV_PROBEN; i++) {
    const env = {};
    vars.forEach((v, j) => { env[v] = positivProbe(i, j); });
    let a, b;
    try { a = werte(t1, env); b = werte(t2, env); } catch { return false; }
    if (!Number.isFinite(b)) continue;
    if (!Number.isFinite(a) || !nahe(a, b, 1e-8)) return false;
    gueltig++;
  }
  return gueltig >= 3;
}

// ── Ungleichungen ────────────────────────────────────────
// Lösungsmenge als {art: "gt"|"lt"|"alle"|"keine", b?, strikt?}: x > b (gt) bzw. x < b (lt)

const REL = [["<=", "≤"], [">=", "≥"], ["≤", "≤"], ["≥", "≥"], ["<", "<"], [">", ">"]];

function teileUngleichung(text) {
  const t = String(text).replace(/=</g, "<=").replace(/=>/g, ">=");
  for (const [zeichen, rel] of REL) {
    const i = t.indexOf(zeichen);
    if (i > 0) return { links: t.slice(0, i), rel, rechts: t.slice(i + zeichen.length) };
  }
  return null;
}

const UNENDLICH = /^(\+?∞|\+?inf|\+?unendlich)$/i;
const MINUS_UNENDLICH = /^(-|−)(∞|inf|unendlich)$/i;

// Intervall „]−∞; 3[“, „[2; ∞[“, „(−∞; 3)“ → Menge
function intervallMenge(text) {
  const m = String(text).replace(/\s+/g, "").match(/^(\]|\[|\()(.+);(.+)(\[|\]|\))$/);
  if (!m) return null;
  const [, l, a, b, r] = m;
  if (MINUS_UNENDLICH.test(a) && !UNENDLICH.test(b)) {
    const w = zahlwert(b);
    return w === null ? null : { art: "lt", b: w, strikt: r !== "]" };
  }
  if (UNENDLICH.test(b) && !MINUS_UNENDLICH.test(a)) {
    const w = zahlwert(a);
    return w === null ? null : { art: "gt", b: w, strikt: l !== "[" };
  }
  if (MINUS_UNENDLICH.test(a) && UNENDLICH.test(b)) return { art: "alle" };
  return null;
}

export function ungleichungsMenge(text) {
  const iv = intervallMenge(text);
  if (iv) return { menge: iv, intervall: true };
  const u = teileUngleichung(text);
  if (!u) return null;
  const g = versuche(`${u.links} = ${u.rechts}`);
  if (!g || !g.gleichung) return null;
  const vars = new Set([...variablen(g.links), ...variablen(g.rechts)]);
  if (vars.size > 1 || (vars.size === 1 && !vars.has("x"))) return null;
  const f = (x) => werte(g.links, { x }) - werte(g.rechts, { x });
  const gilt = (x) => { const v = f(x); return u.rel === "<" ? v < 0 : u.rel === ">" ? v > 0 : u.rel === "≤" ? v <= 1e-12 : v >= -1e-12; };
  const l = loesungLinear(g);
  if (!l) return null;
  const strikt = u.rel === "<" || u.rel === ">";
  if (l.art !== "eine") return { menge: gilt(0) ? { art: "alle" } : { art: "keine" }, intervall: false, u, g };
  return { menge: { art: gilt(l.x + 1) ? "gt" : "lt", b: l.x, strikt }, intervall: false, u, g };
}

function gleicheUngleichungsMenge(a, b) {
  if (!a || !b || a.art !== b.art) return false;
  if (a.art === "alle" || a.art === "keine") return true;
  return a.strikt === b.strikt && nahe(a.b, b.b, 1e-9);
}

// Ergebnis: {art: "geloest"|"schritt"|"form"|"falsch"|"unklar", fehler?, umgedreht?}
export function pruefeUngleichungsZeile(eingabe, aufgabe) {
  const ist = ungleichungsMenge(eingabe);
  const soll = ungleichungsMenge(aufgabe.loesung).menge;
  if (!ist) return { art: "unklar" };
  if (!gleicheUngleichungsMenge(ist.menge, soll)) {
    const f = (aufgabe.fehler || []).find((x) => gleicheUngleichungsMenge(ungleichungsMenge(x.antwort)?.menge, ist.menge));
    const umgedreht = ist.menge.art !== soll.art && (ist.menge.art === "gt" || ist.menge.art === "lt") && nahe(ist.menge.b, soll.b ?? NaN, 1e-9);
    return { art: "falsch", fehler: f || null, umgedreht };
  }
  if (aufgabe.form === "intervall") return ist.intervall ? { art: "geloest" } : { art: "form" };
  if (ist.intervall) return { art: "geloest" };
  const allein = (s) => s.t === "var" && s.n === "x";
  const fertig = (allein(ist.g.links) && !variablen(ist.g.rechts).size) || (allein(ist.g.rechts) && !variablen(ist.g.links).size);
  return fertig ? { art: "geloest" } : { art: "schritt" };
}

// Anzeige: „−2x + 3 ≤ 7“ mit gesetzten Seiten; Intervalle als Text
export function ungleichungHTML(text) {
  const u = teileUngleichung(text);
  if (!u) return esc(schoeneZeichen(text)).replace(/inf/gi, "∞");
  return `${matheHTML(u.links.trim())} <span class="mathe">${u.rel}</span> ${matheHTML(u.rechts.trim())}`;
}

// Menge als Intervall in österreichischer Schreibweise
export function intervallText(menge) {
  const z = (v) => String(Math.round(v * 1e9) / 1e9).replace(".", ",").replace("-", "−");
  if (menge.art === "gt") return `${menge.strikt ? "]" : "["}${z(menge.b)}; ∞[`;
  if (menge.art === "lt") return `]−∞; ${z(menge.b)}${menge.strikt ? "[" : "]"}`;
  return menge.art === "alle" ? "ℝ" : "{ }";
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
