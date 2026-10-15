"""
Generator für C3 (Quadratische Funktionen, Polynome), C4.3 (f(x) = a/x) und C5 (Exponentialfunktionen).

    python tools/generatoren/c345.py
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent))
import notation  # noqa: E402
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, nz, schreibe, z  # noqa: E402

X = sympy.Symbol("x")


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 1000 else z(q)


def wert(text, x=None):
    t = notation.ausdruck(text)
    return t.subs(X, sympy.Rational(str(x))) if x is not None else t


def poly2(a, b, c):
    aus = ""
    for k, v in ((F(a), "x²"), (F(b), "x"), (F(c), "")):
        if k == 0:
            continue
        t = v if abs(k) == 1 and v else f"{zt(abs(k))}{v}"
        aus += (("-" if k < 0 else "") + t) if not aus else f" {'-' if k < 0 else '+'} {t}"
    return aus or "0"


def scheitelform(a, m, n):
    """a(x − m)² + n"""
    a, m, n = F(a), F(m), F(n)
    vor = "" if a == 1 else "-" if a == -1 else zt(a)
    kl = "x²" if m == 0 else f"(x {'-' if m > 0 else '+'} {zt(abs(m))})²"
    teil = f"{vor}{kl}"
    return teil if n == 0 else f"{teil} {'+' if n > 0 else '-'} {zt(abs(n))}"


def zahl(frage, loesung, tipps, fehler=(), aus=None, rechnung=None, graph=None, tabelle=None, einheit=None, extra=None):
    """Exakte Lösung oder (bei rechnung mit unendlich vielen Stellen) auf 2 Stellen gerundet."""
    a = {"typ": "zahl", "frage": frage}
    if rechnung is not None and loesung is None:
        v = notation.zahl(rechnung)
        if v.is_rational and endlich(F(str(v))) and (F(str(v)) * 1000).denominator == 1:
            loesung = F(str(v))
        else:
            a["loesung"] = f"{float(v):.2f}".replace(".", ",")
            a["gerundet"] = 2
    if "loesung" not in a:
        a["loesung"] = zt(loesung)
    for k, v in (("aus_term", aus), ("rechnung", rechnung), ("graph", graph), ("tabelle", tabelle), ("einheit", einheit)):
        if v is not None:
            a[k] = v
    if extra:
        a.update(extra)
    a["tipps"] = tipps
    soll = F(a["loesung"].replace(",", ".")) if "gerundet" in a else F(loesung)
    a["fehler"] = [f for f in fehler_zahlen(soll, [(w, h) for w, h in fehler if w is not None]) if abs(F(f["antwort"]) - soll) > F(1, 50)]
    return a


# ── C3.1 Die Parabel ──────────────────────────────────────

def c3_1(r, s):
    if s <= 2:
        a = 1 if s == 1 else r.choice([-1, 2, -2, F(1, 2), -3])
        m, n = nz(r, -4, 4, ()), nz(r, -5, 5, ())
        term = scheitelform(a, m, n)
    else:
        a = 1 if s == 3 else r.choice([-1, 2, -2])
        m, n = nz(r, -3, 3, ()), nz(r, -6, 6, ())
        term = poly2(a, -2 * a * m, a * m * m + n)
    art = r.choice(["x", "y", "oeffnung"] if s >= 2 else ["x", "y"])
    graph = {"x": [m - 5, m + 5], "y": [min(n - 1, -2) if a > 0 else n - 8, n + 8 if a > 0 else max(n + 1, 2)],
             "kurven": [{"term": term, "name": "f"}]} if s in (1, 3) and r.random() < .6 else None
    if graph:
        graph["y"] = [int(v) for v in graph["y"]]
        graph["x"] = [int(v) for v in graph["x"]]
    if art == "oeffnung":
        return {"typ": "auswahl", "frage": f"Ist die Parabel `f(x) = {term}` nach oben oder nach unten geöffnet?",
                "optionen": ["nach oben", "nach unten"], "richtig": [0 if a > 0 else 1], "pruefung": {"art": "oeffnung", "term": term},
                "erklaerung": "Entscheidend ist die Zahl vor x²: positiv → nach oben geöffnet, negativ → nach unten.",
                "tipps": ["Schau auf das Vorzeichen vor x²."]}
    tipps = (["In der Scheitelform `a(x − m)² + n` ist der Scheitel S(m|n).", "Achtung: In der Klammer steht x **minus** m. "
              "`(x + 3)²` heißt also m = −3."] if s <= 2 else
             ["Scheitel: `x = -b/(2a)` – oder zuerst in die Scheitelform umformen.", "Den y-Wert bekommst du durch Einsetzen in f."])
    if graph:
        tipps = ["Der Scheitel ist der tiefste (oder höchste) Punkt der Parabel.", "Lies seine Koordinaten am Graphen ab."]
    wert_ = m if art == "x" else n
    return zahl(f"`f(x) = {term}`. Gib die **{art}-Koordinate** des Scheitelpunkts an." if not graph else
                f"Das ist der Graph von `f(x) = {term}`. Gib die **{art}-Koordinate** des Scheitelpunkts an.",
                wert_, tipps, [(-m if art == "x" else None, "Vorzeichen! In `(x − m)²` steht das Minus schon in der Formel: Bei `(x + 3)²` ist m = −3.")],
                aus={"term": term, "groesse": f"scheitel_{art}"}, graph=graph)


# ── C3.2 Argumentwerte ────────────────────────────────────

def c3_2(r, s):
    x1, x2 = nz(r, -6, 6), nz(r, -6, 6)
    if x1 == x2:
        return None
    b, c = -(x1 + x2), x1 * x2
    k = nz(r, -8, 8)
    term = poly2(1, b, c + k)  # f(x) = k  ⇔  x² + bx + c = 0
    if s == 1:
        n = r.randint(1, 7)
        k = r.randint(-5, 10)
        term = f"x² {'+' if k > 0 else '-'} {abs(k)}" if k else "x²"
        y = n * n + k
        return {"typ": "quadratisch", "frage": f"`f(x) = {term}`. Für welche x gilt `f(x) = {y}`?", "gleichung": f"{term} = {y}",
                "loesung": f"{n}; -{n}", "weg": [f"{term} = {y}", f"x² = {n * n}", f"x = {n} oder x = -{n}"],
                "tipps": [f"Setz `{term} = {y}` und löse nach x.", "Wurzel: plus und minus!"], "fehler": []}
    if s == 4 and r.random() < .3:
        term = poly2(1, 0, r.randint(1, 6))
        return {"typ": "quadratisch", "frage": f"`f(x) = {term}`. Für welche x gilt `f(x) = 0`?", "gleichung": f"{term} = 0",
                "loesung": "keine", "weg": [], "tipps": ["Kann x² + eine positive Zahl jemals 0 sein?"], "fehler": [],
                "erklaerung": "x² ist nie negativ, also ist f(x) immer positiv – keine Lösung."}
    loesung = "; ".join(z(v) for v in sorted({x1, x2}, reverse=True))
    return {"typ": "quadratisch", "frage": f"`f(x) = {term}`. Für welche x gilt `f(x) = {k}`?", "gleichung": f"{term} = {k}",
            "loesung": loesung, "weg": [f"{term} = {k}", f"{poly2(1, b, c)} = 0", " oder ".join(f"x = {z(v)}" for v in sorted({x1, x2}, reverse=True))],
            "tipps": [f"Setz `{term} = {k}`.", "Bring alles auf eine Seite, sodass rechts 0 steht.", "Dann die Lösungsformel."], "fehler": []}


# ── C3.3 Graphen nach Grad erkennen ───────────────────────

GRAD_TERME = {1: ["x - 1", "-2x + 3", "x/2 + 2", "-x - 2"],
              2: ["x² - 3", "-x² + 4", "(x - 1)² - 4", "-(x + 1)²/2 + 3"],
              3: ["x³/2 - 2x", "-x³/3 + 3x", "(x + 2)(x - 1)(x - 3)/3", "x³/4 - 3"],
              4: ["(x² - 1)(x² - 4)/4", "-(x² - 4)(x² - 1)/3", "x⁴/8 - 2x²", "-x⁴/10 + x² + 2"]}
GRAD_ERK = {1: "Eine **Gerade** – Grad 1.", 2: "Eine **Parabel** mit einem Scheitel – Grad 2.",
            3: "Zwei „Buckel“ (Hoch- und Tiefpunkt), die Enden zeigen in entgegengesetzte Richtungen – typisch für Grad 3.",
            4: "Ein „W“ oder „M“ mit bis zu drei Extrempunkten, beide Enden zeigen in dieselbe Richtung – typisch für Grad 4."}


def c3_3(r, s):
    n = r.choice([1, 2, 3, 4] if s > 1 else [1, 2, 3])
    term = r.choice(GRAD_TERME[n])
    graph = {"x": [-4, 4], "y": [-6, 6], "kurven": [{"term": term, "name": "f"}]}
    return {"typ": "auswahl", "frage": "Welchen Grad hat diese Polynomfunktion (wahrscheinlich)?", "optionen": ["1", "2", "3", "4"],
            "richtig": [n - 1], "graph": graph, "pruefung": {"art": "grad", "term": term}, "erklaerung": GRAD_ERK[n],
            "tipps": ["Zähl die „Buckel“ (Hoch- und Tiefpunkte): Grad n hat höchstens n − 1 davon.",
                      "Schau auf die Enden: Zeigen beide in dieselbe Richtung → gerader Grad; entgegengesetzt → ungerader Grad."]}


# ── C3.4 Grad und höchstens wie viele … ───────────────────

def c3_4(r, s):
    n = r.randint(2, 9)
    art = {1: "nullstellen", 2: "extremstellen", 3: "wendestellen"}.get(s) or r.choice(["nullstellen", "extremstellen", "wendestellen"])
    wort = {"nullstellen": "Nullstellen", "extremstellen": "Extremstellen (Hoch- und Tiefpunkte)", "wendestellen": "Wendestellen"}[art]
    loes = {"nullstellen": n, "extremstellen": n - 1, "wendestellen": n - 2}[art]
    return zahl(f"Eine Polynomfunktion hat den Grad {n}. Wie viele **{wort}** kann sie **höchstens** haben?", loes,
                ["Grad n: höchstens n Nullstellen, n − 1 Extremstellen, n − 2 Wendestellen."],
                [(n if art != "nullstellen" else None, "Das gilt für die Nullstellen. Extremstellen: n − 1, Wendestellen: n − 2.")],
                extra={"grad_regel": {"grad": n, "art": art}})


# ── C3.5 Tabelle ↔ Graph (Polynom) ────────────────────────

def c3_5(r, s):
    term = r.choice({1: ["x² - 2", "2x² - 1"], 2: ["x³ - 2x", "-x² + 3x"], 3: ["x³/2 - x", "x⁴ - 2x²"], 4: ["-x³ + 3x - 1", "x⁴/2 - x³"]}[s])
    xs = list(range(-2, 3))
    luecke = r.choice(xs)
    zeilen = [[str(v), "?" if v == luecke else zt(F(str(wert(term, v))))] for v in xs]
    return zahl(f"Die Tabelle gehört zu `f(x) = {term}`. Welcher Wert fehlt?", F(str(wert(term, luecke))),
                [f"Setz x = {luecke} in f ein.", "Negative Zahlen in Klammern – und Hochzahl vor Punkt."],
                [(F(str(wert(term, -luecke))) if luecke else None, "Vorzeichen beim Einsetzen!")],
                aus={"term": term, "groesse": "wert", "x": luecke}, tabelle={"kopf": ["x", "f(x)"], "zeilen": zeilen})


# ── C4.3 Indirekte Proportionalität f(x) = a/x ────────────

def c4_3(r, s):
    a = r.choice([6, 12, 24, 36, 60, 120])
    if s == 1:
        xw = r.choice([v for v in (1, 2, 3, 4, 6, 12) if a % v == 0])
        return zahl(f"`f(x) = {a}/x`. Berechne `f({xw})`.", F(a, xw), ["Setz den Wert für x ein und dividiere."], [(a * xw, "Durch x dividieren, nicht mal.")],
                    aus={"term": f"{a}/x", "groesse": "wert", "x": xw})
    if s == 2:
        xw = r.choice([2, 3, 4, 5, 6])
        yw = F(a, xw)
        return zahl(f"Die Funktion `f(x) = a/x` geht durch den Punkt P({xw}|{zt(yw)}). Wie groß ist a?", a,
                    ["`yw = a/x`, also `a = x · y`.", f"`a = {xw} · {zt(yw)}`"], [(yw / xw, "a = x **mal** y.")], rechnung=f"{xw}·{zt(yw)}")
    if s == 3:
        weg = r.choice([60, 120, 180, 240])
        v = r.choice([40, 60, 80, 90, 120])
        return zahl(f"Für eine Strecke von {weg} km gilt für die Fahrzeit `t(v) = {weg}/v` (v in km/h, t in h). Wie lange dauert die Fahrt "
                    f"mit {v} km/h?", F(weg, v), ["Setz v ein.", f"`t = {weg} : {v}`"], [(F(v, weg), f"t = Strecke **durch** Geschwindigkeit: {weg} : {v}.")],
                    aus={"term": f"{weg}/x", "groesse": "wert", "x": v}, einheit="h",
                    graph={"x": [0, 150], "y": [0, 8], "kurven": [{"term": f"{weg}/x"}], "achsen": {"x": "v in km/h", "y": "t in h"},
                           "schritt": [10, 1]} if weg <= 240 else None)
    k, text = r.choice([(F(2), "verdoppelt"), (F(3), "verdreifacht"), (F(4), "vervierfacht"), (F(10), "verzehnfacht"),
                        (F(1, 2), "halbiert"), (F(1, 3), "gedrittelt"), (F(1, 4), "geviertelt")])
    return zahl(f"`f(x) = a/x`. Mit welchem Faktor ändert sich f(x), wenn x {text} wird?", 1 / k,
                [f"Setz statt x jetzt {zt(k)}·x ein.", "Indirekt proportional: doppelt so viel → halb so viel, halb so viel → doppelt so viel."],
                [(k, "Indirekt proportional: Wird x größer, wird f(x) **kleiner** – und umgekehrt.")],
                extra={"formel_faktor": {"formel": "y = a/x", "ziel": "y", "aenderung": {"x": zt(k)}}})


# ── C5 Exponentialfunktionen ──────────────────────────────

def c5_1(r, s):
    if s == 1:
        a, b, n = r.choice([3, 5, 10, 50, 100]), r.choice([2, 3]), r.randint(1, 4)
        term = f"{a}·{b}^x"
        return zahl(f"`f(x) = {term}`. Berechne `f({n})`.", a * b ** n,
                    [f"Zuerst die Potenz: `{b}^{n}`, dann mal {a}.", "Hochzahl vor Punkt!"], [((a * b) ** n, "Zuerst die Potenz, dann mal a – nicht (a·b)ⁿ."),
                                                                                         (a * b * n, "bⁿ heißt b n-mal mit sich selbst multiplizieren.")],
                    aus={"term": term, "groesse": "wert", "x": n})
    if s == 2:
        a, b, n = r.choice([100, 200, 500, 1000]), r.choice(["1,1", "1,2", "0,5", "0,8", "1,5"]), r.randint(2, 3)
        return zahl(f"`f(x) = {a}·{b}^x`. Berechne `f({n})`.", None, [f"`{a} · {b}^{n}`", "Erst die Potenz, dann mal."],
                    [], rechnung=f"{a}·{b}^{n}")
    if s == 3:
        a, b = r.choice([50, 80, 200, 400]), r.choice([F(6, 5), F(3, 2), F(1, 2), F(4, 5), F(5, 4)])
        return zahl(f"Eine Exponentialfunktion hat `f(0) = {a}` und `f(1) = {zt(a * b)}`. Wie groß ist der Faktor b?", b,
                    ["Bei `f(x) = a·bˣ` ist f(0) = a. Pro Schritt wird mit b multipliziert.", f"`b = f(1) : f(0) = {zt(a * b)} : {a}`"],
                    [(a * b - a, "Das ist die Zunahme (Differenz). Gesucht ist der Faktor: dividieren."), (F(1) / b, "f(1) **durch** f(0).")],
                    rechnung=f"{zt(a * b)}/{a}")
    a, h = r.choice([200, 500, 800, 1000]), r.randint(4, 8)
    return zahl(f"Bakterien verdoppeln sich jede Stunde. Zu Beginn sind es {a}. Wie viele sind es nach {h} Stunden?", a * 2 ** h,
                ["Verdoppeln heißt: mal 2 pro Stunde.", f"`{a} · 2^{h}`"], [(a * 2 * h, "Verdoppeln jede Stunde: hoch h, nicht mal h.")],
                rechnung=f"{a}·2^{h}")


def c5_2(r, s):
    if s == 1:
        a, b = r.choice([100, 250, 500, 1200]), r.choice(["0,8", "1,05", "1,2", "0,9", "1,03"])
        return zahl(f"`f(x) = {a}·{b}^x`. Wie groß ist der Anfangswert f(0)?", a, ["`b^0 = 1` – also bleibt nur a."], [(F(b.replace(",", ".")) * a, "Bei x = 0 ist bˣ = 1.")],
                    aus={"term": f"{a}·{b}^x", "groesse": "wert", "x": 0})
    if s == 2:
        b = r.choice(["0,8", "1,05", "1,2", "0,92", "1,035", "0,75"])
        bw = F(b.replace(",", "."))
        zu = bw > 1
        return zahl(f"`f(x) = 300·{b}^x`. Um wie viel Prozent {'wächst' if zu else 'sinkt'} f pro Schritt?", abs(bw - 1) * 100,
                    ["Der Faktor b sagt es: b = 1,05 heißt +5 %, b = 0,8 heißt −20 %.", f"`({b} - 1) · 100`"],
                    [(bw * 100, "Das ist der neue Wert in Prozent. Die **Änderung** ist das minus 100 %.")],
                    rechnung=f"{'(' + b + ' - 1)' if zu else '(1 - ' + b + ')'}·100", einheit="%")
    if s == 3:
        fx, b = r.choice([81, 64, 125, 200, 48]), r.choice([2, 3, F(1, 2), F(3, 2)])
        return zahl(f"Für eine Exponentialfunktion mit `b = {zt(b)}` gilt `f(4) = {fx}`. Berechne `f(5)`.", fx * b,
                    ["`f(x + 1) = b · f(x)`: Pro Schritt wird mit b multipliziert."], [(fx + b, "Bei Exponentialfunktionen wird **multipliziert**, nicht addiert.")],
                    rechnung=f"{fx}·{zt(b)}")
    p = r.choice([3, 6, 8, 15, 25])
    zu = r.random() < .5
    return zahl(f"Ein Wert {'nimmt pro Jahr um' if zu else 'nimmt pro Jahr um'} {p} % {'zu' if zu else 'ab'}. Mit welchem Faktor b wird jedes Jahr multipliziert?",
                1 + F(p, 100) if zu else 1 - F(p, 100), ["Zunahme um p % → b = 1 + p/100; Abnahme → b = 1 − p/100."],
                [(F(p, 100), "Das ist nur die Änderung, nicht der Faktor."), (1 - F(p, 100) if zu else 1 + F(p, 100), "Zunahme heißt plus, Abnahme minus.")],
                rechnung=f"1 {'+' if zu else '-'} {p}/100")


def c5_3(r, s):
    xs = list(range(0, 5))
    art = r.choice([0, 1, 2])
    if art == 0:
        k, d = F(nz(r, -9, 12), 1 if s < 3 else 2), r.randint(1, 40)
        ys = [k * x + d for x in xs]
    elif art == 1:
        a, b = r.choice([2, 3, 5, 10, 16, 81]), r.choice([2, 3, F(1, 2), F(3, 2)] if s > 1 else [2, 3])
        ys = [a * F(b) ** x for x in xs]
    else:
        ys = [F(x * x + r.randint(0, 5)) for x in xs]
    if any(not endlich(y) or (y * 100).denominator != 1 for y in ys):
        return None
    return {"typ": "auswahl", "frage": "Ist der Zusammenhang in der Tabelle linear, exponentiell oder keins von beiden?",
            "optionen": ["linear", "exponentiell", "weder noch"], "richtig": [art],
            "tabelle": {"kopf": ["x", "y"], "zeilen": [[str(x), zt(y)] for x, y in zip(xs, ys)]}, "pruefung": {"art": "lin_exp"},
            "erklaerung": {0: "Pro Schritt kommt immer **gleich viel dazu** (gleiche Differenz) – linear.",
                           1: "Pro Schritt wird immer mit **demselben Faktor** multipliziert (gleicher Quotient) – exponentiell.",
                           2: "Weder die Differenzen noch die Quotienten sind gleich – weder linear noch exponentiell."}[art],
            "tipps": ["Berechne die Differenzen aufeinanderfolgender y-Werte: alle gleich → linear.",
                      "Berechne die Quotienten (y neu : y alt): alle gleich → exponentiell."]}


def c5_4(r, s):
    a, lam, t = r.choice([50, 100, 200, 1000]), r.choice(["0,03", "0,05", "0,1", "-0,2", "-0,05", "0,2"]), r.choice([5, 10, 20])
    return zahl(f"`f(t) = {a}·e^({lam}·t)`. Berechne `f({t})` (auf zwei Nachkommastellen gerundet).", None,
                ["Rechne zuerst die Hochzahl aus: `" + lam + " · " + str(t) + "`.", "Dann e hoch diese Zahl (Taschenrechner: eˣ), dann mal " + str(a) + "."],
                [], rechnung=f"{a}·e^({lam}·{t})")


def c5_5(r, s):
    if s == 1:
        b, n = r.choice([2, 3, 5, 10]), r.randint(2, 5)
        return zahl(f"Löse `{b}^x = {b ** n}`.", n, [f"Welche Hochzahl macht aus {b} die Zahl {b ** n}? Probier es aus.", "Oder: `x = ln(c)/ln(b)`."],
                    [(F(b ** n, b), "Gesucht ist die Hochzahl, nicht ein Quotient.")], rechnung=f"ln({b ** n})/ln({b})", extra={"gerundet": 2})
    if s == 2:
        b, c = r.choice([2, 3, 5]), r.choice([10, 20, 50, 100])
        return zahl(f"Löse `{b}^x = {c}` (auf zwei Nachkommastellen).", None, ["Logarithmieren: `x = ln({c})/ln({b})`.".format(c=c, b=b)], [],
                    rechnung=f"ln({c})/ln({b})")
    if s == 3:
        a, b, c = r.choice([200, 500, 1000]), r.choice(["1,04", "1,05", "1,08", "0,9", "0,85"]), None
        c = int(a * (2 if float(b.replace(",", ".")) > 1 else 0.5))
        return zahl(f"Löse `{a}·{b}^x = {c}` (auf zwei Nachkommastellen).", None,
                    [f"Zuerst durch {a} dividieren: `{b}^x = {zt(F(c, a))}`.", "Dann `x = ln(…)/ln(" + b + ")`."], [],
                    rechnung=f"ln({c}/{a})/ln({b})")
    k, c = r.choice(["0,2", "0,5", "0,1", "-0,3"]), r.choice([5, 10, 3, F(1, 2)])
    return zahl(f"Löse `e^({k}·x) = {zt(c)}` (auf zwei Nachkommastellen).", None,
                ["Logarithmieren mit ln: `ln(e^(k·x)) = k·x`.", f"`{k}·x = ln({zt(c)})`, dann durch {k}."], [],
                rechnung=f"ln({zt(c)})/({k})")


def c5_6(r, s):
    if s <= 2:
        p = r.choice([2, 3, 4, 5, 6, 7, 8, 10, 12])
        ding = "Ein Kapital" if s == 1 else r.choice(["Die Einwohnerzahl einer Stadt", "Eine Bakterienkultur", "Der Umsatz einer Firma"])
        return zahl(f"{ding} wächst um {p} % pro Jahr. Nach wie vielen Jahren hat sich der Wert **verdoppelt**? (auf zwei Nachkommastellen)", None,
                    [f"Verdoppelt heißt: `{zt(1 + F(p, 100))}^t = 2`.", f"`t = ln(2)/ln({zt(1 + F(p, 100))})`"],
                    [], rechnung=f"ln(2)/ln({zt(1 + F(p, 100))})", einheit="Jahre")
    if s == 3:
        h, t = r.choice([2, 5, 8, 10]), None
        n = r.randint(2, 5)
        t = h * n
        return zahl(f"Ein Stoff hat eine Halbwertszeit von {h} Tagen. Wie viel Prozent sind nach {t} Tagen noch übrig?", F(100, 2 ** n),
                    [f"{t} Tage sind {n} Halbwertszeiten.", f"Jedes Mal halbiert: `100 · 0,5^{n}`."],
                    [(100 - 50 * n if 100 - 50 * n > 0 else None, "Halbieren heißt jedes Mal **die Hälfte vom Rest**, nicht 50 % vom Anfang.")],
                    rechnung=f"100·0,5^({t}/{h})", einheit="%")
    p = r.choice([5, 8, 10, 12, 15, 20, 25, 30, 40])
    return zahl(f"Ein Medikament wird im Körper pro Stunde um {p} % abgebaut. Wie groß ist die Halbwertszeit? (in Stunden, auf zwei Nachkommastellen)", None,
                [f"Pro Stunde bleibt der Faktor `{zt(1 - F(p, 100))}`.", f"Halbwertszeit: `{zt(1 - F(p, 100))}^t = 0,5`, also `t = ln(0,5)/ln({zt(1 - F(p, 100))})`."],
                [], rechnung=f"ln(0,5)/ln({zt(1 - F(p, 100))})", einheit="h")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261026)
    for lid, fn, n in [("C3.1", c3_1, 8), ("C3.2", c3_2, 8), ("C3.3", c3_3, 4), ("C3.4", c3_4, 5), ("C3.5", c3_5, 5),
                       ("C4.3", c4_3, 5), ("C5.1", c5_1, 6), ("C5.2", c5_2, 6), ("C5.3", c5_3, 8), ("C5.4", c5_4, 5),
                       ("C5.5", c5_5, 6), ("C5.6", c5_6, 5)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "c345.py")


if __name__ == "__main__":
    main()
