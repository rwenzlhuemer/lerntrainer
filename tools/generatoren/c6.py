"""
Generator für Kapitel C6 (Eigenschaften von Funktionen). Einmal laufen lassen:

    python tools/generatoren/c6.py
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent))
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, nz, schreibe, z  # noqa: E402

X = sympy.Symbol("x")


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 1000 else z(q)


def schul(expr):
    """sympy-Polynom → Schulnotation mit ^ für Hochzahlen"""
    expr = sympy.expand(expr)
    p = sympy.Poly(expr, X)
    aus = ""
    for (e,), k in sorted(p.terms(), key=lambda t: -t[0][0]):
        k = F(str(k))
        betrag = abs(k)
        var = "" if e == 0 else "x" if e == 1 else f"x^{e}"
        if not var:
            t = zt(betrag)
        elif betrag == 1:
            t = var
        elif betrag.denominator == 1:
            t = f"{z(betrag)}{var}"
        else:
            t = f"{betrag.numerator if betrag.numerator != 1 else ''}{var}/{betrag.denominator}"
        aus += (("-" if k < 0 else "") + t) if not aus else f" {'-' if k < 0 else '+'} {t}"
    return aus or "0"


def kubik(r):
    """k·(((x−m)/h)³ − 3·(x−m)/h) + n: Extrema bei m ± h mit Werten n ± 2k"""
    m, h, k, n = nz(r, -2, 2, ()), r.choice([1, 2]), r.choice([1, 2, -1, -2]), nz(r, -3, 3, ())
    u = (X - m) / h
    return sympy.expand(k * (u ** 3 - 3 * u) + n), m, h, k, n


def graph_fuer(term, m, h, n, k):
    return {"x": [m - h - 3, m + h + 3], "y": [min(n - 2 * abs(k) - 3, -1), max(n + 2 * abs(k) + 3, 1)],
            "kurven": [{"term": term, "name": "f"}]}


def zahl(frage, loesung, tipps, aus=None, graph=None, fehler=()):
    a = {"typ": "zahl", "frage": frage, "loesung": zt(loesung)}
    if aus:
        a["aus_term"] = aus
    if graph:
        a["graph"] = graph
    a["tipps"] = tipps
    a["fehler"] = fehler_zahlen(loesung, [(w, h) for w, h in fehler if w is not None])
    return a


# ── C6.1 Monotonie ────────────────────────────────────────

def c6_1(r, s):
    expr, m, h, k, n = kubik(r)
    term = schul(expr)
    links, rechts = m - h, m + h
    richtung = r.choice(["steigend", "fallend"])
    optionen = [f"[{links - 2}; {links}]", f"[{links}; {rechts}]", f"[{links - 1}; {rechts}]"]
    # k > 0: steigend links und rechts, fallend in der Mitte; k < 0 umgekehrt
    richtig = [0] if (richtung == "steigend") == (k > 0) else [1]
    reihenfolge = list(range(3))
    r.shuffle(reihenfolge)
    optionen = [optionen[i] for i in reihenfolge]
    richtig = [reihenfolge.index(richtig[0])]
    return {"typ": "auswahl", "frage": f"In welchem Intervall ist f **streng monoton {richtung}**?", "optionen": optionen,
            "richtig": richtig, "graph": graph_fuer(term, m, h, n, k),
            "pruefung": {"art": "monoton", "term": term, "richtung": richtung},
            "erklaerung": f"Streng monoton {richtung} heißt: Von links nach rechts geht der Graph im ganzen Intervall "
                          f"{'hinauf' if richtung == 'steigend' else 'hinunter'}. Ein Intervall, das über einen Hoch- oder Tiefpunkt "
                          "hinausgeht, passt nicht.",
            "tipps": ["Lies den Graphen von links nach rechts.", "Wo sind Hoch- und Tiefpunkt? Dort wechselt die Richtung."]}


# ── C6.2 Hochpunkt und Tiefpunkt ──────────────────────────

def c6_2(r, s):
    expr, m, h, k, n = kubik(r)
    term = schul(expr)
    art = r.choice(["hochpunkt", "tiefpunkt"])
    koord = "x" if s <= 2 else r.choice(["x", "y"])
    hx = m - h if k > 0 else m + h
    tx = m + h if k > 0 else m - h
    wert = (hx if art == "hochpunkt" else tx) if koord == "x" else (n + 2 * abs(k) if art == "hochpunkt" else n - 2 * abs(k))
    return zahl(f"Lies am Graphen ab: Wie lautet die **{koord}-Koordinate** des **{'Hochpunkts' if art == 'hochpunkt' else 'Tiefpunkts'}**?",
                wert, ["Der Hochpunkt ist der höchste Punkt in seiner Umgebung (ein „Gipfel“), der Tiefpunkt ein „Tal“.",
                       f"Gesucht ist die {koord}-Koordinate: {'auf der waagrechten Achse' if koord == 'x' else 'auf der senkrechten Achse'} ablesen."],
                aus={"term": term, "groesse": f"{art}_{koord}"}, graph=graph_fuer(term, m, h, n, k),
                fehler=[((tx if art == "hochpunkt" else hx) if koord == "x" else None, "Verwechselt? Hochpunkt = Gipfel, Tiefpunkt = Tal.")])


# ── C6.3 Schnittpunkte mit den Achsen ─────────────────────

def c6_3(r, s):
    if s == 1:
        k, d = nz(r, -4, 4), nz(r, -8, 8)
        term = schul(k * X + d) if r.random() < .5 else schul(X ** 2 + nz(r, -4, 4) * X + d)
        return zahl(f"`f(x) = {term}`. Wo schneidet der Graph die **y-Achse**? Gib den y-Wert an.", d,
                    ["Auf der y-Achse ist x = 0.", "Berechne f(0)."], aus={"term": term, "groesse": "wert", "x": 0})
    if s == 2:
        x1, x2 = nz(r, -6, 6), nz(r, -6, 6)
        if x1 == x2:
            return None
        term = schul((X - x1) * (X - x2))
        loes = "; ".join(z(v) for v in sorted({x1, x2}, reverse=True))
        return {"typ": "quadratisch", "frage": f"Berechne die **Nullstellen** von `f(x) = {term}`.", "gleichung": f"{term} = 0",
                "loesung": loes, "weg": [f"{term} = 0", " oder ".join(f"x = {z(v)}" for v in sorted({x1, x2}, reverse=True))],
                "tipps": ["Nullstellen: Dort ist f(x) = 0 – der Graph schneidet die x-Achse.", "Löse `f(x) = 0` mit der Lösungsformel."], "fehler": []}
    if s == 3:
        a, b, c = sorted(r.sample(range(-4, 5), 3))
        k = r.choice([F(1, 2), F(-1, 2), F(1, 4), F(-1, 3)])
        expr = sympy.Rational(k.numerator, k.denominator) * (X - a) * (X - b) * (X - c)
        term = schul(expr)
        werte = [abs(float(expr.subs(X, sympy.Rational(v, 4)))) for v in range(4 * a, 4 * c + 1)]
        if max(werte) > 7.5 or max(werte) < 1:
            return None
        loes = "; ".join(z(v) for v in sorted({a, b, c}, reverse=True))
        return {"typ": "quadratisch", "frage": "Lies am Graphen alle **Nullstellen** von f ab.", "gleichung": f"{term} = 0", "loesung": loes,
                "graph": {"x": [-6, 6], "y": [-8, 8], "kurven": [{"term": term, "name": "f"}]}, "weg": [],
                "tipps": ["Nullstellen sind die Stellen, an denen der Graph die x-Achse schneidet oder berührt.", "Es können mehr als zwei sein!",
                          "Antwort z. B.: `x = -2 oder x = 0 oder x = 3` oder `-2; 0; 3`."], "fehler": []}
    k, d = F(nz(r, -5, 5), r.choice([1, 2])), F(nz(r, -9, 9))
    term = schul(sympy.Rational(k.numerator, k.denominator) * X + d)
    return zahl(f"`f(x) = {term}`. Berechne die **Nullstelle**.", -d / k, ["Nullstelle: f(x) = 0 setzen und nach x lösen."],
                aus={"term": term, "groesse": "nullstelle"}, fehler=[(d / k, "Vorzeichen! `kx + d = 0` → `x = -d/k`.")])


# ── C6.5 Schnittpunkte zweier Graphen ─────────────────────

def c6_5(r, s):
    x1, x2 = nz(r, -4, 4), nz(r, -4, 4)
    if x1 == x2:
        return None
    if s == 1:
        c, p = r.randint(1, 3), r.randint(-4, 3)
        fexpr, gexpr = X ** 2 + p, sympy.Integer(c * c + p)
        x1, x2 = c, -c
    else:
        a = F(1) if s == 2 else r.choice([F(1), F(-1), F(1, 2)])
        kg, dg = nz(r, -3, 3), nz(r, -4, 4)
        gexpr = kg * X + dg
        fexpr = sympy.Rational(a.numerator, a.denominator) * (X - x1) * (X - x2) + gexpr
        if s == 4 and r.random() < .3:
            # Gerade weit weg verschieben: kein Schnittpunkt
            gexpr = gexpr - 20 if a > 0 else gexpr + 20
            if any(v.is_real for v in sympy.solve(sympy.Eq(fexpr, gexpr), X)):
                return None
            f, g = schul(fexpr), schul(gexpr)
            return {"typ": "quadratisch", "frage": f"Für welche x schneiden sich `f(x) = {f}` und `g(x) = {g}`?", "gleichung": f"{f} = {g}",
                    "loesung": "keine", "weg": [], "fehler": [],
                    "tipps": ["Gleichsetzen: `f(x) = g(x)`.", "Bleibt unter der Wurzel eine negative Zahl, gibt es keinen Schnittpunkt."]}
    f, g = schul(fexpr), schul(gexpr)
    loes = "; ".join(z(v) for v in sorted({x1, x2}, reverse=True))
    y_werte = [float(gexpr.subs(X, v)) for v in (x1, x2)]
    graph = {"x": [min(x1, x2) - 3, max(x1, x2) + 3], "y": [-10, 12], "kurven": [{"term": f, "name": "f"}, {"term": g, "name": "g"}]} \
        if s <= 3 and all(-9 <= y <= 11 for y in y_werte) else None
    a = {"typ": "quadratisch", "frage": f"Für welche x schneiden sich die Graphen von `f(x) = {f}` und `g(x) = {g}`?",
         "gleichung": f"{f} = {g}", "loesung": loes,
         "weg": [f"{f} = {g}", " oder ".join(f"x = {z(v)}" for v in sorted({x1, x2}, reverse=True))],
         "tipps": ["Im Schnittpunkt sind die Funktionswerte gleich: `f(x) = g(x)` setzen.", "Alles auf eine Seite bringen, dann lösen."],
         "fehler": []}
    if graph:
        a["graph"] = graph
    return a

# ── C6.6 Welcher Funktionstyp? ────────────────────────────

TYPEN = ["linear", "quadratisch", "Polynomfunktion vom Grad 3 oder höher", "exponentiell", "Potenzfunktion (z. B. a/x, √x)"]
BEISPIELE = {
    0: ["3x - 2", "-x/2 + 4", "0,5x + 1", "7 - 2x"],
    1: ["x² - 4", "-2x² + 3x", "(x - 1)² + 2", "0,5x² - x + 1"],
    2: ["x³ - 3x", "x^4 - 2x²", "-x³/4 + x", "(x - 1)(x + 2)(x - 3)/4"],
    3: ["2·1,5^x", "100·0,8^x", "3·2^x", "e^(0,5x)"],
    4: ["6/x", "√x", "2/x²", "-3/x"],
}
TYP_ERK = {0: "Höchste Hochzahl 1 – eine Gerade: linear.", 1: "Höchste Hochzahl 2 – eine Parabel: quadratisch.",
           2: "Höchste Hochzahl 3 oder mehr – Polynomfunktion höheren Grades.",
           3: "x steht in der **Hochzahl** – exponentiell.", 4: "x steht im Nenner oder unter der Wurzel – Potenzfunktion."}


def c6_6(r, s):
    typ = r.choice(range(5))
    term = r.choice(BEISPIELE[typ])
    mit_graph = s >= 3
    a = {"typ": "auswahl", "frage": f"Welcher Funktionstyp ist `f(x) = {term}`?" if not mit_graph else "Welcher Funktionstyp passt am besten zu diesem Graphen?",
         "optionen": TYPEN, "richtig": [typ], "pruefung": {"art": "funktionstyp", "term": term}, "erklaerung": TYP_ERK[typ],
         "tipps": ["Wo steht das x? In der Hochzahl → exponentiell; im Nenner oder unter der Wurzel → Potenzfunktion.",
                   "Sonst: Was ist die höchste Hochzahl von x?"]}
    if mit_graph:
        a["graph"] = {"x": [-4, 4] if typ not in (3, 4) else [0 if typ == 4 else -4, 6], "y": [-6, 8], "kurven": [{"term": term, "name": "f"}]}
    return a


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261027)
    for lid, fn, n in [("C6.1", c6_1, 6), ("C6.2", c6_2, 6), ("C6.3", c6_3, 6), ("C6.5", c6_5, 6), ("C6.6", c6_6, 4)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "c6.py")


if __name__ == "__main__":
    main()
