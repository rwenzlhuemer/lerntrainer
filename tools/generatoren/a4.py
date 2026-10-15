"""
Generator für Kapitel A4 (Terme). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/a4.py

Term-Aufgaben (typ: term) verlangen einen gleichwertigen Term in einer bestimmten Form
(zusammengefasst, ausmultipliziert, faktor, gekuerzt, frei) – siehe app/js/mathe.js.
Stufen: 1 Einstieg · 2 Üben (negative Zahlen) · 3 Vertiefen (zwei Variablen, Hochzahlen) ·
4 Matura-Niveau (Brüche, Dezimalzahlen, verschachtelt).
"""

import random
import re
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent))
import notation  # noqa: E402
from gemeinsam import dez, erzeuge, fehler_zahlen, nz, schreibe, z  # noqa: E402

HOCH = {2: "²", 3: "³", 4: "⁴"}


# ── Terme als Schultext ───────────────────────────────────

def S(text):
    return notation.ausdruck(text)


def monom(k, teile, dezimal=False):
    """k · x²y → '3x²y', 'x/2', '3x/4', '0,5x' (k > 0)"""
    var = "".join(v + (HOCH[e] if e > 1 else "") for v, e in teile if e > 0)
    k = F(k)
    if not var:
        return dez(k) if dezimal and k.denominator != 1 else z(k)
    if k == 1:
        return var
    if k.denominator == 1:
        return f"{k.numerator}{var}"
    if dezimal:
        return f"{dez(k)}{var}"
    return f"{var}/{k.denominator}" if k.numerator == 1 else f"{k.numerator}{var}/{k.denominator}"


def schul(expr, dezimal=False):
    """Polynom → Schulnotation, nach Grad geordnet: 3x² - 5x + 2, a² - 2ab + b²"""
    expr = sympy.expand(sympy.sympify(expr))
    if expr == 0:
        return "0"
    gens = sorted(expr.free_symbols, key=lambda s: s.name)
    if not gens:
        return dez(F(str(expr))) if dezimal else z(F(str(expr)))
    p = sympy.Poly(expr, *gens)
    aus = ""
    for exps, k in p.terms():
        k = F(str(k))
        t = monom(abs(k), list(zip([g.name for g in gens], exps)), dezimal)
        if not aus:
            aus = ("-" if k < 0 else "") + t
        else:
            aus += f" {'-' if k < 0 else '+'} {t}"
    return aus


def glieder(liste, dezimal=False):
    """Unzusammengefasste Summe aus [(k, 'x²')…] in gegebener Reihenfolge: 4x + 3 - 2x"""
    aus = ""
    for k, var in liste:
        k = F(k)
        # 'x²' und 'ab' als ein Variablenteil: monom() bekommt sie wie eine einzelne Variable
        t = monom(abs(k), [(var, 1)] if var else [], dezimal)
        if not aus:
            aus = ("-" if k < 0 else "") + t
        else:
            aus += f" {'-' if k < 0 else '+'} {t}"
    return aus


def term_aufgabe(term, loesung, form, weg, tipps, fehler, faktor=None, anweisung=None, erklaerung=None):
    """Fehler-Antworten, die (zufällig) richtig wären oder doppelt sind, fliegen raus."""
    soll = S(loesung)
    gesehen, fl = [soll], []
    for antwort, hinweis in fehler:
        if antwort is None:
            continue
        w = S(antwort)
        if any(sympy.simplify(w - g) == 0 for g in gesehen):
            continue
        gesehen.append(w)
        fl.append({"antwort": antwort, "hinweis": hinweis})
    a = {"typ": "term", "term": term, "form": form, "loesung": loesung}
    if faktor:
        a["faktor"] = faktor
    if anweisung:
        a["anweisung"] = anweisung
    a.update({"weg": [w for w in dict.fromkeys(weg)], "tipps": tipps, "fehler": fl})
    if erklaerung:
        a["erklaerung"] = erklaerung
    return a


def kette(*teile):
    return " = ".join(dict.fromkeys(teile))


# ── A4.1 Werte einsetzen ──────────────────────────────────

def setze(vorlage, werte=None):
    """'3·{x}² + 5' → Anzeige '3x² + 5' bzw. eingesetzt '3·(-2)² + 5'"""
    if werte is None:
        t = vorlage
        for v in "abxyz":
            t = t.replace("·{" + v + "}", "{" + v + "}")
        return t.replace("{", "").replace("}", "")
    t = vorlage
    for v, w in werte.items():
        w = F(w)
        t = t.replace("{" + v + "}", f"({z(w)})" if w < 0 or w.denominator != 1 else z(w))
    return t


EINSETZ = {
    1: ["3·{x} + 5", "2·{x} - 7", "4·{x} + 1", "5·{x} - 3", "10 - 2·{x}", "{x}² + 1", "6·{x} - 4", "3·({x} + 2)", "2·({x} - 1)",
        "{x}² - 3"],
    2: ["3·{x} + 5", "2·{x} - 7", "{x}² + 1", "2·{x}²", "{x}² - 4·{x}", "5 - 3·{x}", "-2·{x} + 4", "{x}² + {x}", "4 - {x}²",
        "3·({x} - 2)"],
    3: ["2·{a} - 3·{b}", "{a}² - {b}²", "3·{a}·{b}", "{a}·{b} - {a}", "4·{x} + 1", "{x}² - 2·{x}", "2·{a} + {b}²",
        "({a} - {b})²", "{a}² + 2·{a}·{b}", "6·{x} - 3"],
    4: ["-{x}² + 3·{x}", "{a}² - 2·{a}·{b} + {b}²", "3·{x}² - 2·{x} + 1", "-2·{x}² - {x}", "({a} + {b})·({a} - {b})",
        "{x}³ - {x}", "2·{a}² - {a}·{b}", "-{a}² + {b}²", "{x}² - {x}/2", "4·{x}² - 1"],
}


def a4_1(r, s):
    vorlage = r.choice(EINSETZ[s])
    vars_ = sorted({v for v in "abx" if "{" + v + "}" in vorlage})
    werte = {}
    for v in vars_:
        if s == 1:
            werte[v] = r.randint(1, 6)
        elif s == 2:
            werte[v] = nz(r, -5, -1)
        elif s == 3:
            werte[v] = r.choice([nz(r, -4, 4), F(1, 2)]) if v == "x" else nz(r, -5, 5)
        else:
            werte[v] = r.choice([nz(r, -4, -1), F(-1, 2), F(1, 2), F(3, 2)]) if v == "x" else nz(r, -6, 6)
    anzeige = setze(vorlage)
    eingesetzt = setze(vorlage, werte)
    ergebnis = F(str(S(anzeige).subs({sympy.Symbol(k): sympy.Rational(str(v)) for k, v in werte.items()})))
    werte_text = ", ".join(f"{v} = {z(w)}" for v, w in werte.items())
    fehler = []
    if re.search(r"\(-[\d/]+\)²", eingesetzt):
        # (-3)² falsch als -9 gerechnet
        falsch = S(re.sub(r"\((-)([\d/]+)\)²", r"(-(\2)²)", eingesetzt))
        fehler.append((F(str(falsch)), "Achtung beim Quadrieren einer negativen Zahl: `(-3)² = (-3) · (-3) = +9`. Setz die Zahl immer in Klammern!"))
    if vorlage.startswith("-{x}²"):
        x = F(werte["x"])
        fehler.append((ergebnis + 2 * x * x, "`-x²` heißt: zuerst quadrieren, dann das Minus. Für x = -2 ist `-x² = -(-2)² = -4`."))
    if "2·{x}²" in vorlage:
        x = F(werte["x"])
        fehler.append((ergebnis + 2 * x * x, "Hochzahl vor Punkt: zuerst `x²` ausrechnen, dann mal 2 – nicht `(2x)²`."))
    return {"typ": "zahl", "frage": f"Berechne den Wert von `{anzeige}` für {werte_text}.",
            "loesung": z(ergebnis), "term": anzeige, "werte": {k: z(v) for k, v in werte.items()},
            "weg": [kette(eingesetzt, z(ergebnis))],
            "tipps": ["Ersetze jede Variable durch ihre Zahl – negative Zahlen und Brüche **in Klammern**.",
                      f"Eingesetzt: `{eingesetzt}`.",
                      "Dann die Vorrangregeln: Hochzahl vor Punkt vor Strich."],
            "fehler": fehler_zahlen(ergebnis, fehler)}


# ── A4.2 Zusammenfassen ───────────────────────────────────

def a4_2(r, s):
    dezimal = False
    if s == 1:
        vars_ = ["x", ""] if r.random() < .6 else ["x"]
        n = r.randint(3, 4)
        liste = [(nz(r, 1, 9) * (1 if i == 0 or r.random() < .7 else -1), r.choice(vars_)) for i in range(n)]
    elif s == 2:
        vars_ = ["x", ""]
        liste = [(nz(r, -9, 9), v) for v in vars_ for _ in range(2)]
        r.shuffle(liste)
    elif s == 3:
        vars_ = r.choice([["a", "b"], ["x²", "x"], ["a", "b", ""], ["x²", "x", ""], ["ab", "a"]])
        liste = [(nz(r, -9, 9), v) for v in vars_ for _ in range(2)]
        r.shuffle(liste)
    else:
        vars_ = r.choice([["x", ""], ["a", "b"], ["x²", "x"]])
        if r.random() < .5:
            dezimal = True
            liste = [(F(nz(r, -30, 30, (0, 10, -10, 20, -20)), 10), v) for v in vars_ for _ in range(2)]
        else:
            liste = [(F(nz(r, -5, 5), r.choice([2, 3, 4])), v) for v in vars_ for _ in range(2)]
            liste = [(k, v) for k, v in liste if F(k).denominator != 1] or liste
        r.shuffle(liste)
    vorhanden = {v for _, v in liste}
    if len(liste) < 3 or len(vorhanden) == len(liste) or vorhanden <= {""}:
        return None
    term = glieder(liste, dezimal)
    expr = S(term)
    loesung = schul(expr, dezimal)
    if loesung == "0" or len(loesung) > 40:
        return None
    geordnet = glieder(sorted(liste, key=lambda kv: [v for v in vars_].index(kv[1]) if kv[1] in vars_ else 9), dezimal)
    fehler = []
    neg = [i for i, (k, _) in enumerate(liste) if F(k) < 0 and i > 0]
    if neg:
        flip = [(-k if i == neg[0] else k, v) for i, (k, v) in enumerate(liste)]
        fehler.append((schul(S(glieder(flip, dezimal)), dezimal), "Achte auf das Vorzeichen: Das Minus gehört immer zum Glied dahinter."))
    if "" in vorhanden and len(vorhanden) == 2:
        v = next(x for x in vorhanden if x)
        fehler.append((f"{z(sum(F(k) for k, _ in liste))}{v}" if sum(F(k) for k, _ in liste) not in (0,) else None,
                       f"Glieder mit {v} und reine Zahlen sind nicht gleichartig – sie dürfen nicht zusammengezählt werden."))
    if vorhanden == {"x²", "x"}:
        fehler.append((f"{z(sum(F(k) for k, _ in liste))}x²", "`x²` und `x` sind **nicht** gleichartig – die darfst du nicht zusammenfassen."))
    return term_aufgabe(term, loesung, "zusammengefasst",
                        [kette(term, geordnet, loesung)],
                        ["Gleichartig sind Glieder mit genau derselben Variablen (und Hochzahl).",
                         f"Ordne zuerst: `{geordnet}`.",
                         "Rechne dann nur mit den Zahlen davor. Das Vorzeichen gehört zum Glied dahinter."],
                        [(f, h) for f, h in fehler if f])


# ── A4.3 Klammern auflösen ────────────────────────────────

def lin(a, b, v="x"):
    return schul(a * sympy.Symbol(v) + b)


def a4_3(r, s):
    x = sympy.Symbol("x")
    if s == 1:
        k, a, b = r.randint(2, 7), r.randint(1, 5), nz(r, -9, 9)
        term = f"{k}({lin(a, b)})"
        expr = k * (a * x + b)
        fehler = [(schul(k * a * x + b), f"Die {k} wird mit **jedem** Glied in der Klammer multipliziert – auch mit {z(abs(b))}.")]
        tipps = [f"Multipliziere {k} mit jedem Glied in der Klammer.", f"`{k} · {monom(a, [('x', 1)])}` und `{k} · ({b})`."]
    elif s == 2:
        w = r.random()
        a, b = nz(r, -6, 6), nz(r, -9, 9)
        if w < .35:
            term = f"-({lin(a, b)})"
            expr = -(a * x + b)
            fehler = [(schul(-a * x + b), "Minus vor der Klammer dreht **jedes** Vorzeichen in der Klammer um – auch beim letzten Glied.")]
        elif w < .7:
            k = nz(r, -6, -2)
            term = f"{k}({lin(a, b)})"
            expr = k * (a * x + b)
            fehler = [(schul(k * a * x - k * b), "Minus mal Minus ergibt Plus, Minus mal Plus ergibt Minus – prüf jedes Vorzeichen."),
                      (schul(k * a * x + b), f"Die {k} wird mit **jedem** Glied multipliziert.")]
        else:
            c, k = nz(r, 1, 9), r.randint(2, 5)
            term = f"{c} - ({lin(a, b)})" if r.random() < .5 else f"{lin(c, 0)} - {k}({lin(a, b)})"
            expr = S(term)
            if term.startswith(f"{c} -"):
                fehler = [(schul(c - a * x + b), "Minus vor der Klammer dreht **jedes** Vorzeichen um – auch das zweite.")]
            else:
                fehler = [(schul(c * x - k * a * x + k * b), "Minus vor der Klammer dreht **jedes** Vorzeichen um.")]
        tipps = ["Minus vor der Klammer: Jedes Vorzeichen in der Klammer dreht sich um.",
                 "Steht eine Zahl davor, multiplizierst du jedes Glied mit ihr – mit ihrem Vorzeichen.",
                 "Danach gleichartige Glieder zusammenfassen."]
    elif s == 3:
        w = r.random()
        if w < .5:
            k1, k2 = r.randint(2, 5), nz(r, -5, 5, (0, 1, -1))
            a1, b1, a2, b2 = nz(r, 1, 4), nz(r, -6, 6), nz(r, 1, 4), nz(r, -6, 6)
            zwei = f"- {abs(k2)}({lin(a2, b2)})" if k2 < 0 else f"+ {k2}({lin(a2, b2)})"
            term = f"{k1}({lin(a1, b1)}) {zwei}"
            expr = S(term)
            fehler = [(schul(k1 * (a1 * x + b1) + k2 * a2 * x + b2 * (1 if k2 > 0 else -1)),
                       "Auch bei der zweiten Klammer: die Zahl davor mit **jedem** Glied multiplizieren.")]
        else:
            k, a, b = nz(r, -4, 4, (0,)), nz(r, 1, 5), nz(r, -7, 7)
            vor = f"{'-' if k < 0 else ''}{monom(abs(k), [('x', 1)])}"
            term = f"{vor}({lin(a, b)})"
            expr = k * x * (a * x + b)
            fehler = [(schul(k * a * x * x + b), "Das `x` vor der Klammer wird auch mit der Zahl multipliziert."),
                      (schul(k * a * x + k * b * x), "`x · x = x²` – das ergibt nicht einfach x.")]
        tipps = ["Löse jede Klammer einzeln auf: die Zahl (oder das x) davor mal jedes Glied.",
                 "`x · x = x²`.", "Zum Schluss gleichartige Glieder zusammenfassen."]
    else:
        w = r.random()
        if w < .35:
            k, m, a = r.randint(2, 4), r.randint(2, 4), nz(r, 1, 5)
            term = f"{k}(x - {m}(x - {a}))"
            expr = k * (x - m * (x - a))
            fehler = [(schul(k * (x - m * x - m * a)), "Minus vor der inneren Klammer: Aus `- " + f"{m}(x - {a})" + "` wird `" +
                       f"- {m}x + {m * a}" + "`."),
                      (schul(k * x - m * (x - a)), f"Die äußere {k} gilt für die **ganze** große Klammer.")]
        elif w < .7:
            n = r.choice([2, 3, 4])
            a, b = n * nz(r, 1, 4), n * nz(r, -5, 5)
            vor = r.choice([F(1, n), F(-1, n), F(3, n) if n == 4 else F(-1, n)])
            term = f"{'-' if vor < 0 else ''}{z(abs(vor))}·({lin(a, b)})"
            expr = vor * (a * x + b)
            fehler = [(schul(vor * a * x + b), "Der Bruch wird mit **jedem** Glied multipliziert.")]
        else:
            a, b, c = nz(r, -4, 4), nz(r, 1, 5), nz(r, -5, 5)
            term = f"x(x {'-' if a < 0 else '+'} {abs(a)}) - ({monom(b, [('x', 2)])} {'-' if c < 0 else '+'} {monom(abs(c), [('x', 1)])})"
            expr = S(term)
            fehler = [(schul(x * x + a * x - b * x * x + c * x), "Minus vor der zweiten Klammer dreht **jedes** Vorzeichen in ihr um.")]
        tipps = ["Bei verschachtelten Klammern: von innen nach außen auflösen.",
                 "Minus vor einer Klammer dreht jedes Vorzeichen in ihr um.", "Zum Schluss zusammenfassen."]
    loesung = schul(expr)
    if loesung == "0":
        return None
    return term_aufgabe(term, loesung, "ausmultipliziert", [kette(term, loesung)], tipps, fehler)


# ── A4.4 Ausmultiplizieren (a + b)(c + d) ─────────────────

def produkt_glieder(p1, p2):
    """Alle Einzelprodukte als unzusammengefasste Summe (für den Lösungsweg)"""
    teile = [sympy.expand(u * v) for u in sympy.Add.make_args(sympy.expand(p1)) for v in sympy.Add.make_args(sympy.expand(p2))]
    aus = ""
    for t in teile:
        txt = schul(t)
        if not aus:
            aus = txt
        else:
            aus += f" - {txt[1:]}" if txt.startswith("-") else f" + {txt}"
    return aus


def a4_4(r, s):
    x, a_, b_ = sympy.symbols("x a b")
    vor = ""
    if s == 1:
        p, q = nz(r, 1, 8), nz(r, 1, 8)
        f1, f2 = x + p, x + q
    elif s == 2:
        p, q = nz(r, -8, 8), nz(r, -8, 8)
        if p > 0 and q > 0 or p == q:
            return None
        f1, f2 = x + p, x + q
    elif s == 3:
        w = r.random()
        if w < .6:
            f1, f2 = nz(r, 2, 5) * x + nz(r, -7, 7), nz(r, 1, 4) * x + nz(r, -7, 7)
        else:
            f1, f2 = a_ + nz(r, -3, 3) * b_, nz(r, 1, 3) * a_ + nz(r, -4, 4) * b_
    else:
        w = r.random()
        if w < .4:
            k = nz(r, -3, 3, (0, 1))
            f1, f2 = x + nz(r, -6, 6), x + nz(r, -6, 6)
            vor = f"{k}" if k != -1 else "-"
        elif w < .7:
            f1, f2 = nz(r, 2, 4) * x + nz(r, -5, 5), nz(r, -6, 6) - x
        else:
            f1, f2 = x + nz(r, -3, 3), x * x + nz(r, -3, 3) * x + nz(r, -4, 4)
    t1, t2 = schul(f1), schul(f2)
    term = f"{vor}({t1})({t2})"
    k = -1 if vor == "-" else S(vor) if vor else 1
    expr = sympy.expand(k * f1 * f2)
    loesung = schul(expr)
    zwischen = produkt_glieder(f1, f2)
    weg = [kette(term, (f"{vor}({zwischen})" if vor else zwischen), loesung)]
    a1 = sympy.Add.make_args(sympy.expand(f1))
    a2 = sympy.Add.make_args(sympy.expand(f2))
    fehler = []
    if len(a1) == 2 and len(a2) == 2:
        # nur „erstes mal erstes + letztes mal letztes“
        nur_aussen = k * sum(u * v for u, v in zip(sorted(a1, key=sympy.default_sort_key), sorted(a2, key=sympy.default_sort_key)))
        fehler.append((schul(nur_aussen), "Jedes Glied der ersten Klammer wird mit **jedem** Glied der zweiten multipliziert – das sind 4 Produkte."))
    mitte = expr.coeff(x, 1)
    fehler.append((schul(expr - 2 * mitte * x) if mitte else None,
                   "Achte bei jedem Produkt auf das Vorzeichen: Minus mal Minus ist Plus."))
    tipps = ["Jedes Glied der ersten Klammer mal jedes Glied der zweiten Klammer.",
             f"Die Einzelprodukte: `{zwischen}`.", "Zum Schluss gleichartige Glieder zusammenfassen."]
    return term_aufgabe(term, loesung, "ausmultipliziert", weg, tipps, [(f, h) for f, h in fehler if f])


# ── A4.5 Herausheben ──────────────────────────────────────

def a4_5(r, s):
    x, y, a_, b_ = sympy.symbols("x y a b")
    if s == 1:
        k = r.randint(2, 9)
        a, b = r.randint(1, 6), nz(r, -9, 9)
        if sympy.gcd(a, b) != 1:
            return None
        faktor, innen = sympy.Integer(k), a * x + b
    elif s == 2:
        w = r.random()
        if w < .4:
            faktor, innen = x, nz(r, 1, 6) * x + nz(r, -9, 9)
        elif w < .75:
            k = r.randint(2, 6)
            a, b = r.randint(1, 5), nz(r, -7, 7)
            if sympy.gcd(a, b) != 1:
                return None
            faktor, innen = k * x, a * x + b
        else:
            k = r.randint(2, 6)
            faktor, innen = k * x, r.randint(2, 5) * x + r.choice([1, -1])
    elif s == 3:
        w = r.random()
        if w < .5:
            k = r.randint(2, 7)
            p, q = r.randint(1, 4), nz(r, -5, 5)
            if sympy.gcd(p, q) != 1:
                return None
            faktor, innen = k * a_ * b_, p * a_ + q * b_
        else:
            k = r.randint(2, 5)
            p, q, c = r.randint(1, 3), nz(r, -6, 6), nz(r, -7, 7)
            if sympy.gcd(sympy.gcd(p, q), c) != 1:
                return None
            faktor, innen = k * x, p * x * x + q * x + c
    else:
        w = r.random()
        if w < .55:
            u = r.choice([a_ + b_, a_ - b_, x - nz(r, 1, 5), x + nz(r, 1, 5)])
            p, q = nz(r, 1, 5), nz(r, -6, 6)
            v = p * y + q if u.has(x) else p * x + q
            if sympy.gcd(p, q) != 1:
                return None
            us, vs = schul(u), schul(v)
            teile = sympy.Add.make_args(sympy.expand(v))
            glied = lambda t: (f"{schul(t)}({us})" if abs(t) != 1 or t.free_symbols else ("-" if t < 0 else "") + f"({us})")  # noqa: E731
            term = ""
            for t in sorted(teile, key=lambda t: -len(t.free_symbols)):
                g = glied(t)
                term = g if not term else (f"{term} - {g[1:]}" if g.startswith("-") else f"{term} + {g}")
            loesung = f"({us})({vs})"
            return term_aufgabe(term, loesung, "faktor", [kette(term, loesung)],
                                [f"Schau genau: Die Klammer `({us})` steckt in beiden Gliedern.",
                                 f"Heb die ganze Klammer `({us})` heraus – wie eine Zahl.",
                                 f"Was bleibt übrig, wenn du `({us})` wegnimmst? Das kommt in die zweite Klammer."],
                                [(f"({us})({schul(v - q)})", "Vom zweiten Glied bleibt nach dem Herausheben noch etwas übrig – vergiss es nicht.")],
                                faktor=us)
        k = r.randint(2, 6)
        p, q, c = r.randint(1, 4), nz(r, -5, 5), nz(r, -6, 6)
        if sympy.gcd(sympy.gcd(p, q), c) != 1:
            return None
        faktor, innen = k * x * y, p * x + q * y + c
    term = schul(sympy.expand(faktor * innen))
    fs, ins = schul(faktor), schul(innen)
    loesung = f"{fs}({ins})"
    zwischen = " + ".join(f"{fs}·{schul(t)}" if not str(t).startswith("-") else f"{fs}·({schul(t)})"
                          for t in sympy.Add.make_args(sympy.expand(innen)))
    fehler = []
    teile = sympy.Add.make_args(sympy.expand(innen))
    if any(t.is_number and abs(t) == 1 for t in teile):
        ohne_eins = sum(t for t in teile if not (t.is_number and abs(t) == 1))
        fehler.append((f"{fs}({schul(ohne_eins)})", "Hebst du ein ganzes Glied heraus, bleibt in der Klammer **1** stehen – nicht nichts!"))
    if len(teile) >= 2:
        geflippt = sum(-t if i == len(teile) - 1 else t for i, t in enumerate(sorted(teile, key=sympy.default_sort_key)))
        fehler.append((f"{fs}({schul(geflippt)})", "Prüf die Vorzeichen in der Klammer: Multiplizier zur Probe wieder aus."))
    return term_aufgabe(term, loesung, "faktor", [kette(term, zwischen, loesung)],
                        ["Suche, was in **allen** Gliedern steckt: die größte gemeinsame Zahl und gemeinsame Variablen.",
                         f"Gemeinsam ist `{fs}`.",
                         f"Dividiere jedes Glied durch `{fs}` – das kommt in die Klammer. Probe: wieder ausmultiplizieren."],
                        fehler, faktor=fs)


# ── A4.6 Binomische Formeln ───────────────────────────────

def a4_6(r, s):
    x, a_, b_, y = sympy.symbols("x a b y")
    rueck = s >= 2 and r.random() < (.4 if s == 2 else .5)
    art = r.choice(["plus", "minus", "pm"])
    if s == 1:
        u, v = x, nz(r, 1, 9)
    elif s == 2:
        u, v = nz(r, 2, 5) * x, nz(r, 1, 7)
    elif s == 3:
        u, v = nz(r, 2, 5) * a_, nz(r, 1, 5) * b_
    else:
        w = r.random()
        if w < .4 and not rueck:
            u, v = x, sympy.Rational(1, r.choice([2, 3, 4]))
            if r.random() < .5:
                u, v = x / 2, nz(r, 1, 5)
        else:
            u, v = nz(r, 2, 6) * x, nz(r, 1, 5) * y

    if art == "plus":
        faktoren = (u + v) ** 2
        term_f = f"({schul(u + v)})²"
        falsch = [(schul(u ** 2 + v ** 2), "Das Mittelglied fehlt! `(a + b)² = a² + 2ab + b²` – nicht nur a² + b²."),
                  (schul(u ** 2 + u * v + v ** 2), "Das Mittelglied ist **2**·a·b.")]
    elif art == "minus":
        faktoren = (u - v) ** 2
        term_f = f"({schul(u - v)})²"
        falsch = [(schul(u ** 2 - v ** 2), "Das Mittelglied fehlt! `(a - b)² = a² - 2ab + b²`."),
                  (schul(u ** 2 - 2 * u * v - v ** 2), "Das letzte Glied ist immer **plus**: `(-b)² = +b²`.")]
    else:
        faktoren = (u + v) * (u - v)
        term_f = f"({schul(u + v)})({schul(u - v)})"
        falsch = [(schul(u ** 2 + v ** 2), "`(a + b)(a - b) = a² - b²` – in der Mitte steht ein **Minus**."),
                  (schul(u ** 2 - 2 * u * v + v ** 2), "Bei `(a + b)(a - b)` heben sich die Mittelglieder weg: a² - b².")]
    expandiert = schul(sympy.expand(faktoren))
    if u != x and u.is_Mul:
        k = u.as_coeff_Mul()[0]
        falsch.append((schul(sympy.expand(faktoren) - u ** 2 + k * u.as_coeff_Mul()[1] ** 2),
                       f"Auch die Zahl wird quadriert: `({schul(u)})² = {schul(u ** 2)}`."))
    if not rueck:
        zw = {"plus": f"{kl_t(u)}² + 2·{kl_t(u)}·{kl_t(v)} + {kl_t(v)}²", "minus": f"{kl_t(u)}² - 2·{kl_t(u)}·{kl_t(v)} + {kl_t(v)}²",
              "pm": f"{kl_t(u)}² - {kl_t(v)}²"}[art]
        return term_aufgabe(term_f, expandiert, "ausmultipliziert", [kette(term_f, zw, expandiert)],
                            [{"plus": "1. binomische Formel: `(a + b)² = a² + 2ab + b²`.",
                              "minus": "2. binomische Formel: `(a - b)² = a² - 2ab + b²`.",
                              "pm": "3. binomische Formel: `(a + b)(a - b) = a² - b²`."}[art],
                             f"Hier ist a = `{schul(u)}` und b = `{schul(v)}`.",
                             f"Ausgeschrieben: `{zw}`."],
                            falsch)
    faktor = schul(u + v) if art != "minus" else schul(u - v)
    return term_aufgabe(expandiert, term_f, "faktor", [kette(expandiert, term_f)],
                        ["Prüf: Ist der Term `a² + 2ab + b²`, `a² - 2ab + b²` oder `a² - b²`?",
                         f"Was ist `a`, was ist `b`? Hier: a² = `{schul(u ** 2)}` und b² = `{schul(v ** 2)}`.",
                         "Prüf das Mittelglied: Ist es wirklich 2·a·b?"],
                        [(f"({schul(u + v)})({schul(u - v)})" if art != "pm" else f"({schul(u - v)})²",
                          "Prüf mit Ausmultiplizieren, ob wirklich der ursprüngliche Term herauskommt.")],
                        faktor=faktor, anweisung="Schreib den Term mit einer binomischen Formel als Produkt.")


def kl_t(t):
    """Für den Lösungsweg: 2x → (2x), x → x, 3 → 3"""
    t = sympy.sympify(t)
    s = schul(t)
    return f"({s})" if (len(t.free_symbols) and not t.is_Symbol) or s.startswith("-") or "/" in s else s


# ── A4.7 Kürzen bei Bruchtermen ───────────────────────────

KUERZEN = {
    1: [("6x/9", "2x/3"), ("8x²/(4x)", "2x"), ("12ab/(3b)", "4a"), ("10x/(15x²)", "2/(3x)"), ("14a²/(7a)", "2a"),
        ("9xy/(6y)", "3x/2"), ("4x³/(2x)", "2x²"), ("15a/(5ab)", "3/b"), ("18x²/(12x)", "3x/2"), ("20ab²/(4ab)", "5b"),
        ("7x²y/(14xy)", "x/2"), ("6x/(8x²)", "3/(4x)")],
    2: [("(3x + 6)/3", "x + 2"), ("(4x - 8)/4", "x - 2"), ("(x² + 2x)/x", "x + 2"), ("(5x - 10)/(x - 2)", "5"),
        ("(4x - 8)/(2x - 4)", "2"), ("(6x + 9)/3", "2x + 3"), ("(x² - 3x)/x", "x - 3"), ("(2x + 2)/(x + 1)", "2"),
        ("(10x - 15)/5", "2x - 3"), ("(3a + 3b)/(a + b)", "3"), ("(x² + 5x)/(2x)", "(x + 5)/2"), ("(8x + 12)/4", "2x + 3")],
    3: [("(x² - 9)/(x + 3)", "x - 3"), ("(2x + 4)/(x² + 2x)", "2/x"), ("(x² - 4)/(x - 2)", "x + 2"),
        ("(3x - 6)/(x² - 2x)", "3/x"), ("(x² + 2x + 1)/(x + 1)", "x + 1"), ("(a² - b²)/(a - b)", "a + b"),
        ("(x² - 6x + 9)/(x - 3)", "x - 3"), ("(4x² - 1)/(2x + 1)", "2x - 1"), ("(5x² + 10x)/(5x)", "x + 2"),
        ("(x² - 25)/(2x + 10)", "(x - 5)/2")],
    4: [("(x² - 4x + 4)/(x² - 4)", "(x - 2)/(x + 2)"), ("(3x² - 6x)/(x² - 4x + 4)", "3x/(x - 2)"),
        ("(a² - 2ab + b²)/(a² - b²)", "(a - b)/(a + b)"), ("(x² - 1)/(x² + 2x + 1)", "(x - 1)/(x + 1)"),
        ("(2x² - 8)/(x² + 4x + 4)", "(2x - 4)/(x + 2)"), ("(9x² - 4)/(3x² - 2x)", "(3x + 2)/x"),
        ("(x³ - x)/(x² - x)", "x + 1"), ("(4a² + 4ab + b²)/(4a² - b²)", "(2a + b)/(2a - b)"),
        ("(6x - 3)/(4x² - 1)", "3/(2x + 1)"), ("(x² + 6x + 9)/(2x + 6)", "(x + 3)/2")],
}

SUMMANDEN_FALLE = [("(x + 6)/3", ["x/3 + 2", "x + 2", "x/3 + 6"]), ("(2x + 8)/2", ["x + 4", "x + 8", "2x + 4"]),
                   ("(x + 4)/(x + 2)", ["(x + 4)/(x + 2)", "2", "4/2"]), ("(3x + 9)/3", ["x + 3", "x + 9", "3x + 3"]),
                   ("(x² + x)/x", ["x + 1", "x²", "x + x"]), ("(5 + x)/5", ["1 + x/5", "x", "1 + x"]),
                   ("(4x + 2)/2", ["2x + 1", "2x + 2", "4x + 1"]), ("(x + 10)/(x + 5)", ["(x + 10)/(x + 5)", "2", "10/5 + 1"])]


def a4_7(r, s):
    if s in (2, 3) and r.random() < .3:
        term, optionen = r.choice(SUMMANDEN_FALLE)
        optionen = optionen[:]
        r.shuffle(optionen)
        richtig = [i for i, o in enumerate(optionen) if sympy.simplify(S(o) - S(term)) == 0]
        if len(richtig) != 1:
            return None
        return {"typ": "auswahl", "frage": f"Welcher Term ist gleich `{term}`?", "mathe": True,
                "optionen": optionen, "richtig": richtig, "pruefung": {"art": "termgleich", "ziel": term},
                "erklaerung": f"Richtig ist `{optionen[richtig[0]]}`. Kürzen darf man nur **Faktoren**, nie einzelne Summanden. "
                              "Steht oben eine Summe, musst du entweder **jedes** Glied dividieren oder zuerst herausheben.",
                "tipps": ["Setz zur Probe eine Zahl für x ein, z. B. x = 1, und vergleiche."]}
    term, loesung = r.choice(KUERZEN[s])
    fehler = []
    m = re.match(r"^\((\S+) ([+-]) (\d+)\)/(\d+)$", term)
    if m:
        # nur das erste Glied dividiert, das zweite stehen gelassen: (3x + 6)/3 → x + 6
        erstes = sympy.expand(S(m.group(1)) / int(m.group(4)))
        fehler.append((f"{schul(erstes)} {m.group(2)} {m.group(3)}",
                       f"Du musst **jedes** Glied oben durch {m.group(4)} dividieren – oder zuerst herausheben."))
    zerlegt = {
        "(x² - 9)/(x + 3)": "(x + 3)(x - 3)/(x + 3)", "(x² - 4)/(x - 2)": "(x + 2)(x - 2)/(x - 2)",
        "(a² - b²)/(a - b)": "(a + b)(a - b)/(a - b)", "(4x² - 1)/(2x + 1)": "(2x + 1)(2x - 1)/(2x + 1)",
        "(x² - 4x + 4)/(x² - 4)": "(x - 2)^2/((x + 2)(x - 2))", "(3x² - 6x)/(x² - 4x + 4)": "3x(x - 2)/(x - 2)^2",
        "(a² - 2ab + b²)/(a² - b²)": "(a - b)^2/((a + b)(a - b))", "(x² - 1)/(x² + 2x + 1)": "(x + 1)(x - 1)/(x + 1)^2",
        "(9x² - 4)/(3x² - 2x)": "(3x + 2)(3x - 2)/(x(3x - 2))", "(x³ - x)/(x² - x)": "x(x + 1)(x - 1)/(x(x - 1))",
    }
    weg = [kette(term, zerlegt.get(term, term), loesung)]

    return term_aufgabe(term, loesung, "gekuerzt", weg,
                        ["Kürzen darf man nur **Faktoren** – nie einzelne Summanden!",
                         "Steht oben oder unten eine Summe: zuerst herausheben oder eine binomische Formel erkennen."
                         if s >= 2 else "Kürze die Zahlen und die Variablen getrennt: `x² : x = x`.",
                         f"Zerlegt: `{zerlegt[term]}`. Jetzt gleiche Faktoren kürzen." if term in zerlegt else
                         "Zum Schluss: Steht oben und unten noch derselbe Faktor?"],
                        [(f, h) for f, h in fehler if f])


# ── A4.8 Bruchterme addieren und multiplizieren ───────────

BRUCHTERME = {
    1: [("x/2 + x/3", "5x/6"), ("3x/4 - x/4", "x/2"), ("2/x + 5/x", "7/x"), ("x/5 + 2x/5", "3x/5"), ("a/3 + a/6", "a/2"),
        ("5x/6 - x/3", "x/2"), ("3/a - 1/a", "2/a"), ("x/4 + x/2", "3x/4"), ("2x/3 · 3/4", "x/2"), ("x/2 · x/5", "x²/10")],
    2: [("1/x + 1/(2x)", "3/(2x)"), ("x/3 · 6/x²", "2/x"), ("2a/3 · 9/a²", "6/a"), ("3/(2x) - 1/x", "1/(2x)"),
        ("(x/2) : (x/4)", "2"), ("5/(3a) + 1/(6a)", "11/(6a)"), ("(4x/5) : (2/x)", "2x²/5"), ("1/x - 1/x²", "(x - 1)/x²"),
        ("x²/6 · 3/x", "x/2"), ("2/x + 3/x²", "(2x + 3)/x²")],
    3: [("1/x + 1/y", "(x + y)/(xy)"), ("1/(x - 1) - 1/x", "1/(x(x - 1))"), ("2/(x + 1) + 1/(x + 1)", "3/(x + 1)"),
        ("x/(x - 2) - 2/(x - 2)", "1"), ("a/b - b/a", "(a + b)(a - b)/(ab)"), ("(x + 1)/x · x²/(x + 1)", "x"),
        ("3/(x + 2) · (x + 2)/6", "1/2"), ("1/a + 1/(2a) + 1/(3a)", "11/(6a)"), ("x/(x + 3) + 3/(x + 3)", "1"),
        ("2/(a - b) · (a - b)/4", "1/2")],
    4: [("(x² - 1)/x · x/(x + 1)", "x - 1"), ("1/(x - 1) + 1/(x + 1)", "2x/((x + 1)(x - 1))"), ("a/(a - b) - b/(a - b)", "1"),
        ("((x² - 4)/(3x)) : ((x + 2)/(6x))", "2x - 4"), ("1/(x - 2) - 1/(x + 2)", "4/((x + 2)(x - 2))"),
        ("x/(x + 1) - 1/(x - 1)", "(x² - 2x - 1)/((x + 1)(x - 1))"), ("(a + b)/a · a²/(a² - b²)", "a/(a - b)"),
        ("2/x - 3/(2x) + 1/(4x)", "3/(4x)"), ("(x² - 9)/(x + 1) · (x + 1)/(x - 3)", "x + 3"),
        ("1/(x(x + 1)) + 1/(x + 1)", "1/x")],
}


def a4_8(r, s):
    term, loesung = r.choice(BRUCHTERME[s])
    plus = "+" in term or " - " in term
    fehler = []
    if term == "x/2 + x/3":
        fehler.append(("2x/5", "Nenner werden nicht addiert! Gemeinsamer Nenner 6: `3x/6 + 2x/6`."))
    if term == "1/x + 1/y":
        fehler.append(("2/(x + y)", "Nenner werden nicht addiert! Gemeinsamer Nenner ist `xy`."))
    if term == "2/x + 5/x":
        fehler.append(("7/(2x)", "Bei gleichem Nenner bleibt der Nenner stehen – nur die Zähler werden addiert."))
    return term_aufgabe(term, loesung, "gekuerzt", [kette(term, loesung)],
                        (["Wie bei Zahlen-Brüchen: zuerst auf einen gemeinsamen Nenner bringen, dann die Zähler addieren.",
                          "Der gemeinsame Nenner enthält jeden Faktor, der in einem der Nenner vorkommt.",
                          "Zum Schluss kürzen, wenn es geht."] if plus else
                         ["Zähler mal Zähler, Nenner mal Nenner – beim Dividieren mit dem Kehrwert.",
                          "Kürze, bevor du ausmultiplizierst: gleiche Faktoren oben und unten fallen weg.",
                          "Binomische Formeln erkennen hilft beim Kürzen."]),
                        fehler, anweisung="Rechne aus und kürze so weit wie möglich.")


# ── A4.9 Terme aus Text ───────────────────────────────────

def text_aufgabe(frage, loesung, fehler, tipps):
    return {"typ": "term", "frage": frage, "form": "frei", "loesung": loesung,
            "tipps": tipps, "fehler": [{"antwort": a, "hinweis": h} for a, h in fehler]}


def a4_9(r, s):
    n, m = r.randint(2, 9), r.randint(2, 9)
    wort = {2: "Doppelte", 3: "Dreifache", 4: "Vierfache", 5: "Fünffache", 6: "Sechsfache", 7: "Siebenfache",
            8: "Achtfache", 9: "Neunfache"}
    teil = {2: "Hälfte", 3: "dritte Teil", 4: "vierte Teil", 5: "fünfte Teil"}
    if s == 1:
        k = r.randint(2, 5)
        aufgaben = [
            (f"Das {wort[n]} von x, vermehrt um {m}.", f"{n}x + {m}", [(f"{n}(x + {m})", f"Zuerst das {wort[n]}, dann + {m} – keine Klammer nötig.")]),
            (f"x vermindert um {m}.", f"x - {m}", [(f"{m} - x", "„x vermindert um …“: x steht vorne, dann wird abgezogen.")]),
            (f"Die {teil[2]} von x, vermehrt um {m}.", f"x/2 + {m}", [(f"(x + {m})/2", "Nur x wird halbiert, dann kommt + " + str(m) + " dazu.")]),
            (f"Um {m} größer als das {wort[n]} von x.", f"{n}x + {m}", []),
            (f"Das {wort[n]} von x, vermindert um {m}.", f"{n}x - {m}", [(f"{n}(x - {m})", "Zuerst das Vielfache, dann abziehen – ohne Klammer.")]),
            (f"Der {teil[k]} von x." if k > 2 else "Die Hälfte von x.", f"x/{k}", [(f"{k}x", f"Ein Teil heißt dividieren: x : {k}.")]),
        ]
        tipps = [f"„Das {wort[n]}“ heißt: mal {n}.", "„vermehrt um“ = plus, „vermindert um“ = minus."]
    elif s == 2:
        aufgaben = [
            (f"Das {wort[n]} der Summe aus x und {m}.", f"{n}(x + {m})", [(f"{n}x + {m}", "„Das Vielfache der **Summe**“: Die ganze Summe kommt in eine Klammer.")]),
            (f"Die Differenz aus dem {wort[n]}n von x und {m}.", f"{n}x - {m}", []),
            (f"Das Quadrat von x, vermindert um {m}.", f"x² - {m}", [(f"(x - {m})²", "Nur x wird quadriert, danach wird abgezogen.")]),
            (f"Das Quadrat der Summe aus x und {m}.", f"(x + {m})²", [(f"x² + {m}", "Quadrat der **Summe**: Die ganze Summe kommt in Klammer und wird quadriert."),
                                                              (f"x² + {m * m}", "Quadrat der **Summe**: `(x + " + str(m) + ")²` – nicht jedes Glied einzeln quadrieren.")]),
            (f"Der {teil[3]} von x, vermehrt um {m}.", f"x/3 + {m}", [(f"(x + {m})/3", "Nur x wird durch 3 dividiert.")]),
            (f"Das Produkt aus x und der um {m} größeren Zahl.", f"x(x + {m})", [(f"x·x + {m}", "Die um " + str(m) + " größere Zahl ist `(x + " + str(m) + ")` – sie kommt in Klammer.")]),
            (f"Der Quotient aus x und {m}, vermindert um 1.", f"x/{m} - 1", []),
        ]
        tipps = ["„Summe“ = plus, „Differenz“ = minus, „Produkt“ = mal, „Quotient“ = durch.",
                 "Bezieht sich etwas auf eine **Summe** oder **Differenz**, braucht diese eine Klammer."]
    elif s == 3:
        p = r.choice([4, 6, 8, 9, 12])
        q = r.choice([3, 5, 7])
        aufgaben = [
            (f"Ein Rechteck ist um {m} cm länger als breit. Die Breite ist b. Gib einen Term für den **Umfang** an.",
             f"2b + 2(b + {m})", [(f"b + (b + {m})", "Der Umfang hat **zwei** Längen und **zwei** Breiten."),
                                  (f"2b + 2·{m}", "Die Länge ist `b + " + str(m) + "`, nicht nur " + str(m) + ".")]),
            (f"Eine Eintrittskarte kostet {p} € für Erwachsene und {q} € für Kinder. Gib einen Term für den Preis bei a Erwachsenen und k Kindern an.",
             f"{p}a + {q}k", [(f"{p + q}(a + k)", "Erwachsene und Kinder zahlen verschieden viel – jede Gruppe extra.")]),
            (f"Ein Handytarif kostet {n} € Grundgebühr pro Monat und 0,09 € pro Minute. Gib einen Term für die Monatskosten bei t Minuten an.",
             f"{n} + 0,09t", [(f"{n}t + 0,09", "Die Grundgebühr zahlt man einmal, die 0,09 € pro Minute.")]),
            ("Gib einen Term für die Summe dreier aufeinanderfolgender ganzer Zahlen an. Die kleinste ist n.",
             "n + (n + 1) + (n + 2)", [("3n", "Die Zahlen sind n, n + 1 und n + 2 – nicht dreimal dieselbe.")]),
            (f"Anna ist x Jahre alt. Ihr Bruder ist {m} Jahre älter. Gib einen Term für die Summe ihrer Alter an.",
             f"x + (x + {m})", [(f"x + {m}", "Gefragt ist die **Summe** beider Alter.")]),
            (f"Ein Quadrat hat die Seitenlänge s. Jede Seite wird um {m} cm verlängert. Gib einen Term für den neuen Umfang an.",
             f"4(s + {m})", [(f"4s + {m}", "**Jede** der vier Seiten wird länger."), ]),
        ]
        tipps = ["Überleg zuerst: Wofür steht die Variable? Was hängt davon ab?",
                 "Schreib Zwischengrößen mit Klammern, z. B. die Länge `(b + 3)`.",
                 "Du musst den Term nicht vereinfachen – jede richtige Form zählt."]
    else:
        pz = r.choice([10, 20, 25])
        aufgaben = [
            (f"Ein Quadrat hat die Seitenlänge a. Eine Seite wird um {m} cm verlängert, die andere um {m} cm verkürzt. Gib einen Term für den Flächeninhalt des neuen Rechtecks an.",
             f"(a + {m})(a - {m})", [("a²", "Probier es aus: Die Fläche ändert sich!"), (f"a² + {m * m}", "Länge mal Breite: `(a + " + str(m) + ")(a - " + str(m) + ")`.")]),
            (f"Ein Preis p wird um {pz} % erhöht. Gib einen Term für den neuen Preis an.",
             f"{dez(1 + F(pz, 100))}p", [(f"p + {pz}", f"{pz} % von p ist `{dez(F(pz, 100))}p`, nicht {pz}.")]),
            (f"Ein Preis p wird zuerst um {pz} % erhöht und danach um {pz} % gesenkt. Gib einen Term für den Endpreis an.",
             f"{dez(1 + F(pz, 100))}·{dez(1 - F(pz, 100))}p", [("p", f"Die {pz} % beziehen sich das zweite Mal auf einen **größeren** Preis – es bleibt nicht gleich.")]),
            ("Gib einen Term für den Durchschnitt (Mittelwert) der Zahlen a, b und c an.", "(a + b + c)/3",
             [("a + b + c/3", "Die **ganze** Summe wird durch 3 dividiert – sie braucht eine Klammer.")]),
            (f"Ein Zug fährt t Stunden mit 80 km/h und danach {m} Stunden länger mit 100 km/h. Gib einen Term für die gesamte Strecke an.",
             f"80t + 100(t + {m})", [(f"80t + 100·{m}", f"Der zweite Teil dauert `t + {m}` Stunden, nicht {m}.")]),
            ("Ein Rechteck ist doppelt so lang wie breit. Die Breite ist x. Gib einen Term für den Flächeninhalt an.",
             "2x·x", [("2x", "Fläche = Länge mal Breite: `2x · x`.")]),
            (f"Ein Kapital K wird zwei Jahre mit {r.choice([2, 3, 4])} % verzinst (Zinseszins). Gib einen Term für das Endkapital an.",
             None, []),
        ]
        zins = aufgaben[-1][0].split(" mit ")[1].split(" %")[0]
        aufgaben[-1] = (aufgaben[-1][0], f"K·{dez(1 + F(int(zins), 100))}²",
                        [(f"K + 2·{dez(F(int(zins), 100))}K", "Beim Zinseszins werden im zweiten Jahr auch die Zinsen verzinst: zweimal mal " +
                          dez(1 + F(int(zins), 100)) + ".")])
        tipps = ["Überleg zuerst: Wofür steht die Variable? Was hängt davon ab?",
                 "Prozent: „um 20 % erhöhen“ heißt mal 1,2; „um 20 % senken“ heißt mal 0,8.",
                 "Du musst den Term nicht vereinfachen – jede richtige Form zählt."]
    frage, loesung, fehler = r.choice(aufgaben)
    return text_aufgabe(frage if "Term" in frage else f"{frage} Schreib den passenden Term.", loesung, fehler, tipps)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261017)
    for lid, fn, n in [("A4.1", a4_1, 10), ("A4.2", a4_2, 10), ("A4.3", a4_3, 10), ("A4.4", a4_4, 10),
                       ("A4.5", a4_5, 10), ("A4.6", a4_6, 10), ("A4.7", a4_7, 8), ("A4.8", a4_8, 8), ("A4.9", a4_9, 6)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "a4.py")


if __name__ == "__main__":
    main()
