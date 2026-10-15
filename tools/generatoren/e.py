"""
Generator für Teil E (Analysis): Änderungsmaße, Ableiten, Kurvendiskussion, Anwendungen, Integral.

    python tools/generatoren/e.py

Alles wird beim Build mit sympy geprüft (Ableitung, Stammfunktion, Integral, Fläche, Extrem- und Wendestellen).
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
R = sympy.Rational


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 1000 else z(q)


def schul(expr, var="x"):
    """Polynom → Schulnotation mit ^ für Hochzahlen (auch in t)"""
    expr = sympy.expand(expr)
    if expr == 0:
        return "0"
    p = sympy.Poly(expr, X)
    aus = ""
    for (e,), k in sorted(p.terms(), key=lambda t: -t[0][0]):
        k = F(str(k))
        betrag = abs(k)
        v = "" if e == 0 else var if e == 1 else f"{var}^{e}"
        if not v:
            t = zt(betrag)
        elif betrag == 1:
            t = v
        elif betrag.denominator == 1 or endlich(betrag):
            t = f"{zt(betrag)}{v}"
        else:
            t = f"{betrag.numerator if betrag.numerator != 1 else ''}{v}/{betrag.denominator}"
        aus += (("-" if k < 0 else "") + t) if not aus else f" {'-' if k < 0 else '+'} {t}"
    return aus


def Fz(v):
    return F(str(sympy.nsimplify(v)))


def zahl(frage, loesung, tipps, fehler=(), **extra):
    a = {"typ": "zahl", "frage": frage, "loesung": zt(loesung)}
    a.update({k: v for k, v in extra.items() if v is not None})
    a["tipps"] = tipps
    a["fehler"] = fehler_zahlen(loesung, [(w, h) for w, h in fehler if w is not None])
    return a


def zpoly(r, grad, lo=-4, hi=4, nenner=(1,)):
    """Zufallspolynom vom Grad grad mit kleinen Koeffizienten"""
    while True:
        koeff = [R(nz(r, lo, hi, ()), r.choice(nenner)) for _ in range(grad + 1)]
        if koeff[-1] != 0 and sum(k != 0 for k in koeff) >= 2:
            return sum(k * X ** i for i, k in enumerate(koeff))


# ── E1 Änderungsmaße ──────────────────────────────────────

def e1_1(r, s):
    f = zpoly(r, 2 if s < 3 else 3, -3, 3)
    a, b = sorted(r.sample(range(-2, 5), 2))
    fa, fb = Fz(f.subs(X, a)), Fz(f.subs(X, b))
    term = schul(f)
    if s <= 2 or fa == 0:
        return zahl(f"`f(x) = {term}`. Berechne die **absolute Änderung** von f im Intervall [{a}; {b}].", fb - fa,
                    ["Absolute Änderung = f(b) − f(a).", f"`f({b}) - f({a})`"], [(fa - fb, "Neuer minus alter Wert: f(b) − f(a).")],
                    aus_term={"term": term, "groesse": "differenz", "von": a, "bis": b})
    return zahl(f"`f(x) = {term}`. Berechne die **relative Änderung** von f im Intervall [{a}; {b}] (als Dezimalzahl).", (fb - fa) / fa,
                ["Relative Änderung = (f(b) − f(a)) : f(a).", f"f({a}) = {zt(fa)}, f({b}) = {zt(fb)}."],
                [((fb - fa) / fb if fb else None, "Geteilt wird durch den **Anfangswert** f(a).")],
                rechnung=f"({zt(fb)} - ({zt(fa)}))/({zt(fa)})")


def e1_2(r, s):
    f = zpoly(r, 2 if s <= 2 else 3, -3, 3, (1, 2) if s == 4 else (1,))
    a, b = sorted(r.sample(range(-3, 5), 2))
    term = schul(f)
    m = (Fz(f.subs(X, b)) - Fz(f.subs(X, a))) / (b - a)
    graph = {"x": [a - 2, b + 2], "y": [-8, 8], "kurven": [{"term": term, "name": "f"}]} if s == 1 and abs(Fz(f.subs(X, a))) < 7 and abs(Fz(f.subs(X, b))) < 7 else None
    return zahl(f"`f(x) = {term}`. Berechne den **Differenzenquotienten** (mittlere Änderungsrate) im Intervall [{a}; {b}].", m,
                ["Differenzenquotient = (f(b) − f(a)) : (b − a).", f"f({a}) = {zt(Fz(f.subs(X, a)))}, f({b}) = {zt(Fz(f.subs(X, b)))}."],
                [(Fz(f.subs(X, b)) - Fz(f.subs(X, a)) if b - a != 1 else None, "Noch durch die Intervalllänge (b − a) dividieren.")],
                aus_term={"term": term, "groesse": "steigung_mittel", "von": a, "bis": b}, graph=graph)


def e1_3(r, s):
    a = r.choice([R(1, 2), R(-1, 2), 1, -1, R(1, 4)])
    f = a * X ** 2 + nz(r, -2, 2) * X + nz(r, -3, 3)
    x0 = nz(r, -3, 3)
    m = Fz(sympy.diff(f, X).subs(X, x0))
    y0 = Fz(f.subs(X, x0))
    if abs(y0) > 6 or m.denominator != 1 or y0.denominator != 1:
        return None
    tang = schul(m * (X - x0) + y0)
    term = schul(f)
    return zahl("Im Bild siehst du den Graphen von f und die **Tangente** im markierten Punkt. Lies die Steigung der Tangente ab – "
                "das ist die momentane Änderungsrate f′ an dieser Stelle.", m,
                ["Steigungsdreieck an der Tangente (nicht am Graphen!): eine Einheit nach rechts – wie viel nach oben oder unten?",
                 "Fällt die Tangente, ist die Steigung negativ."],
                [(-m if m else None, "Vorzeichen: Fällt die Tangente von links nach rechts, ist die Steigung negativ.")],
                aus_term={"term": term, "groesse": "ableitung", "x": x0},
                graph={"x": [x0 - 4, x0 + 4], "y": [int(y0) - 6, int(y0) + 6],
                       "kurven": [{"term": term, "name": "f"}, {"term": tang, "name": "t"}], "punkte": [{"x": x0, "y": int(y0), "auf": 0}]})


def e1_4(r, s):
    c = r.choice([2, 3, 4, 5])
    term = schul(c * X ** 2)
    a, b = sorted(r.sample(range(0, 6), 2))
    if s <= 2:
        return zahl(f"Ein Körper bewegt sich nach `s(t) = {schul(c * X ** 2, 't')}` (s in Metern, t in Sekunden). Wie groß ist die "
                    f"**mittlere Geschwindigkeit** zwischen t = {a} und t = {b}?", c * (b + a),
                    ["Mittlere Geschwindigkeit = zurückgelegter Weg : Zeit = (s(b) − s(a)) : (b − a)."],
                    [(c * (b * b - a * a), "Noch durch die Zeitdauer (b − a) dividieren.")],
                    aus_term={"term": term, "groesse": "steigung_mittel", "von": a, "bis": b}, einheit="m/s")
    t0 = r.randint(1, 6)
    return zahl(f"Ein Körper bewegt sich nach `s(t) = {schul(c * X ** 2, 't')}` (s in m, t in s). Wie groß ist die **momentane "
                f"Geschwindigkeit** zum Zeitpunkt t = {t0}?", 2 * c * t0,
                ["Momentangeschwindigkeit = Ableitung s′(t).", f"`s′(t) = {2 * c}t`. Setz t = {t0} ein."],
                [(c * t0, "Das ist die mittlere Geschwindigkeit seit dem Start, nicht die momentane.")],
                aus_term={"term": term, "groesse": "ableitung", "x": t0}, einheit="m/s")


# ── E2 Ableiten ───────────────────────────────────────────

def ableiten(funktion, abl, tipps, fehler=(), ordnung=1, name="f"):
    strich = "′" * ordnung
    a = {"typ": "term", "frage": f"Leite ab: `{name}(x) = {funktion}`. Gib `{name}{strich}(x)` an." if ordnung == 1 else
         f"Berechne die **zweite** Ableitung von `{name}(x) = {funktion}`.",
         "form": "frei", "loesung": abl, "ableitung_von": funktion, "tipps": tipps,
         "fehler": [{"antwort": an, "hinweis": h} for an, h in fehler]}
    if ordnung != 1:
        a["ordnung"] = ordnung
    return a


POTENZREGEL = "Potenzregel: `(xⁿ)′ = n · xⁿ⁻¹` – die Hochzahl kommt nach vorne, die neue Hochzahl ist um 1 kleiner."


def e2_1(r, s):
    if s == 1:
        n = r.randint(2, 9)
        return ableiten(f"x^{n}", f"{n}x^{n - 1}" if n > 2 else "2x", [POTENZREGEL],
                        [(f"x^{n - 1}", "Die alte Hochzahl kommt als Faktor nach vorne."), (f"{n}x^{n}", "Die Hochzahl wird um 1 kleiner.")])
    if s == 2:
        a, n = nz(r, -6, 6, (0, 1)), r.randint(2, 6)
        return ableiten(f"{a}x^{n}", schul(a * n * X ** (n - 1)), ["Faktorregel: Die Zahl davor bleibt stehen.", POTENZREGEL],
                        [(schul(a * X ** (n - 1)), "Die Hochzahl kommt auch nach vorne: mal n.")])
    if s == 3:
        n, a = r.randint(1, 4), r.choice([1, 2, 3, 4, -1, -2])
        abl = -a * n
        ft = f"{a}/x^{n}" if n > 1 else f"{a}/x"
        lt = f"{abl}/x^{n + 1}"
        return ableiten(ft, lt, ["Schreib zuerst als Potenz: `a/xⁿ = a · x⁻ⁿ`.", POTENZREGEL, "Die neue Hochzahl ist −n − 1."],
                        [(f"{a}/x^{n - 1}" if n > 1 else str(a), "Schreib als Potenz mit negativer Hochzahl, dann Potenzregel.")])
    ft, lt, falsch = r.choice([("√x", "1/(2√x)", "√x/2"), ("2√x", "1/√x", "√x"), ("x^(1/3)", "1/(3x^(2/3))", "x^(1/3)/3"),
                               ("x^(3/2)", "3√x/2", "x^(1/2)"), ("4√x", "2/√x", "2√x"), ("x^(5/2)", "5x^(3/2)/2", "x^(3/2)"),
                               ("6√x", "3/√x", "3√x")])
    return ableiten(ft, lt, ["Wurzel als Potenz: `√x = x^(1/2)`.", POTENZREGEL, "`1/2 − 1 = −1/2`, und `x^(-1/2) = 1/√x`."],
                    [(falsch, "Potenzregel: Hochzahl nach vorne, neue Hochzahl um 1 kleiner (bei √x wird sie negativ).")])

def e2_2(r, s):
    if s <= 3:
        f = zpoly(r, s + 1, -6, 6, (1,) if s < 3 else (1, 2))
        term, abl = schul(f), schul(sympy.diff(f, X))
        konst = Fz(f.subs(X, 0))
        return ableiten(term, abl, ["Summenregel: Jedes Glied einzeln ableiten.", POTENZREGEL, "Eine Zahl ohne x fällt weg (Ableitung 0)."],
                        [(schul(sympy.diff(f, X) + konst), "Eine Zahl ohne x fällt beim Ableiten weg.")] if konst else [])
    p, q = zpoly(r, 1, -3, 3), zpoly(r, 1, -3, 3)
    f = sympy.expand(p * q)
    return ableiten(f"({schul(p)})({schul(q)})", schul(sympy.diff(f, X)),
                    ["Multipliziere zuerst aus, dann leite jedes Glied ab.", f"Ausmultipliziert: `{schul(f)}`."],
                    [(schul(sympy.diff(p, X) * sympy.diff(q, X)), "Man darf nicht einfach die Faktoren einzeln ableiten – zuerst ausmultiplizieren.")])


def e2_3(r, s):
    f = zpoly(r, min(s + 1, 4), -5, 5, (1,) if s < 4 else (1, 2))
    return ableiten(schul(f), schul(sympy.diff(f, X, 2)), ["Zweimal hintereinander ableiten: zuerst f′, dann davon die Ableitung.",
                                                          f"`f′(x) = {schul(sympy.diff(f, X))}`."],
                    [(schul(sympy.diff(f, X)), "Das ist erst f′. Jetzt noch einmal ableiten.")], ordnung=2)


TRANSZ = [("sin(x)", "cos(x)", "-cos(x)"), ("cos(x)", "-sin(x)", "sin(x)"), ("e^x", "e^x", "x·e^(x-1)"),
          ("3e^x", "3e^x", "3"), ("sin(2x)", "2cos(2x)", "cos(2x)"), ("cos(3x)", "-3sin(3x)", "-sin(3x)"),
          ("e^(2x)", "2e^(2x)", "e^(2x)"), ("5e^(-x)", "-5e^(-x)", "5e^(-x)"), ("2sin(x) + x^2", "2cos(x) + 2x", "2cos(x) + x"),
          ("e^(0,5x)", "0,5e^(0,5x)", "e^(0,5x)"), ("4cos(x) - 3x", "-4sin(x) - 3", "4sin(x) - 3"), ("sin(4x)", "4cos(4x)", "cos(4x)")]


def e2_4(r, s):
    f, abl, falsch = r.choice(TRANSZ[3 * (s - 1): 3 * s])
    return ableiten(f, abl, ["`(sin x)′ = cos x`, `(cos x)′ = −sin x`, `(eˣ)′ = eˣ`.",
                             "Steht innen k·x, kommt der Faktor k nach vorne: `[f(kx)]′ = k · f′(kx)`."],
                    [(falsch, "Prüf die Regel: Vorzeichen bei cos, und der innere Faktor k kommt nach vorne.")])


# ── E3 Was die Ableitung verrät ───────────────────────────

def e3_1(r, s):
    f = zpoly(r, 2 if s <= 2 else 3, -4, 4)
    x0 = nz(r, -3, 3)
    term = schul(f)
    m = Fz(sympy.diff(f, X).subs(X, x0))
    return zahl(f"`f(x) = {term}`. Wie groß ist die Steigung des Graphen an der Stelle x = {x0}?", m,
                ["Die Steigung an einer Stelle ist f′ an dieser Stelle.", f"`f′(x) = {schul(sympy.diff(f, X))}`. Setz x = {x0} ein."],
                [(Fz(f.subs(X, x0)), "Das ist der Funktionswert f(x₀). Gesucht ist f′(x₀).")],
                aus_term={"term": term, "groesse": "ableitung", "x": x0})


def e3_2(r, s):
    f = zpoly(r, 2 if s <= 2 else 3, -4, 4)
    x0 = nz(r, -3, 3)
    d = Fz(sympy.diff(f, X).subs(X, x0))
    term = schul(f)
    return {"typ": "auswahl", "frage": f"`f(x) = {term}`. Wie verhält sich f an der Stelle x = {x0}?",
            "optionen": ["streng monoton steigend (f′ > 0)", "streng monoton fallend (f′ < 0)", "waagrechte Tangente (f′ = 0)"],
            "richtig": [0 if d > 0 else 1 if d < 0 else 2], "pruefung": {"art": "ableitung_vorzeichen", "term": term, "x": x0},
            "erklaerung": f"`f′({x0}) = {zt(d)}`. " + ("Positiv – f steigt dort." if d > 0 else "Negativ – f fällt dort." if d < 0 else
                                                       "Null – waagrechte Tangente (möglicher Hoch- oder Tiefpunkt)."),
            "tipps": ["Berechne f′ und setz x ein.", "f′ > 0: steigend, f′ < 0: fallend."]}


def e3_3(r, s):
    m, h, k, n = nz(r, -2, 2, ()), r.choice([1, 2]), r.choice([1, -1, 2]), nz(r, -3, 3, ())
    u = (X - m) / h
    f = sympy.expand(k * (u ** 3 - 3 * u) + n)
    term = schul(f)
    if s <= 2:
        loes = f"{m + h}; {m - h}"
        return {"typ": "quadratisch", "frage": f"Berechne die **Extremstellen** von `f(x) = {term}` (die x-Werte mit f′(x) = 0).",
                "gleichung": f"{schul(sympy.diff(f, X))} = 0", "loesung": loes, "ableitung_von": term,
                "weg": [f"{schul(sympy.diff(f, X))} = 0", f"x = {m + h} oder x = {m - h}"],
                "tipps": ["Extremstellen: f′(x) = 0 setzen.", f"`f′(x) = {schul(sympy.diff(f, X))}`.", "Löse die quadratische Gleichung."],
                "fehler": []}
    art = r.choice(["hochpunkt", "tiefpunkt"])
    koord = r.choice(["x", "y"])
    hx = m - h if k > 0 else m + h
    tx = m + h if k > 0 else m - h
    xw = hx if art == "hochpunkt" else tx
    wert_ = xw if koord == "x" else Fz(f.subs(X, xw))
    return zahl(f"`f(x) = {term}`. Berechne die **{koord}-Koordinate des {'Hochpunkts' if art == 'hochpunkt' else 'Tiefpunkts'}**.", wert_,
                ["f′(x) = 0 liefert die Extremstellen.", "f″ entscheidet: f″ < 0 → Hochpunkt, f″ > 0 → Tiefpunkt.",
                 "Für die y-Koordinate x in f (nicht in f′!) einsetzen."],
                [((tx if art == "hochpunkt" else hx) if koord == "x" else None, "Prüf mit f″: negativ → Hochpunkt, positiv → Tiefpunkt.")],
                aus_term={"term": term, "groesse": f"{art}_{koord}"})


def e3_4(r, s):
    f = zpoly(r, 3, -3, 3)
    x0 = nz(r, -3, 3)
    d2 = Fz(sympy.diff(f, X, 2).subs(X, x0))
    if d2 == 0:
        return None
    term = schul(f)
    return {"typ": "auswahl", "frage": f"`f(x) = {term}`. Ist der Graph an der Stelle x = {x0} links- oder rechtsgekrümmt?",
            "optionen": ["linksgekrümmt (f″ > 0)", "rechtsgekrümmt (f″ < 0)"], "richtig": [0 if d2 > 0 else 1],
            "pruefung": {"art": "kruemmung", "term": term, "x": x0},
            "erklaerung": f"`f″(x) = {schul(sympy.diff(f, X, 2))}`, also `f″({x0}) = {zt(d2)}`. "
                          + ("Positiv: linksgekrümmt (wie ein lächelnder Mund)." if d2 > 0 else "Negativ: rechtsgekrümmt."),
            "tipps": ["Zweimal ableiten, dann x einsetzen.", "f″ > 0: linksgekrümmt, f″ < 0: rechtsgekrümmt."]}


def e3_5(r, s):
    a = r.choice([1, -1, R(1, 3), 2])
    w = nz(r, -3, 3)
    b, c = nz(r, -6, 6), nz(r, -5, 5)
    # Wendestelle bei w: f″(w) = 0 → 6a·w + 2B = 0 → B = −3a·w
    f = a * X ** 3 - 3 * a * w * X ** 2 + b * X + c
    term = schul(f)
    koord = "x" if s <= 2 else r.choice(["x", "y"])
    return zahl(f"`f(x) = {term}`. Berechne die **{koord}-Koordinate des Wendepunkts**.", w if koord == "x" else Fz(f.subs(X, w)),
                ["Wendestelle: f″(x) = 0 setzen.", f"`f″(x) = {schul(sympy.diff(f, X, 2))}`.", "Für die y-Koordinate x in f einsetzen."],
                [], aus_term={"term": term, "groesse": "wendestelle_x" if koord == "x" else "wendepunkt_y"})


# ── E4 Graphisches Ableiten ───────────────────────────────

def e4_1(r, s):
    f = zpoly(r, 2 if s <= 2 else 3, -3, 3, (1, 2) if s >= 3 else (1,))
    abl = schul(sympy.diff(f, X))
    falsch1 = schul(-sympy.diff(f, X))
    falsch2 = schul(sympy.diff(f, X) + r.choice([2, -2, 3]))
    falsch3 = schul(f)
    optionen = list(dict.fromkeys([abl, falsch1, falsch2 if s > 1 else falsch3]))
    if len(optionen) < 3:
        return None
    r.shuffle(optionen)
    werte = [abs(float(f.subs(X, v))) for v in range(-3, 4)]
    if max(werte) > 9:
        return None
    return {"typ": "auswahl", "frage": "Abgebildet ist der Graph von f. Welcher Term gehört zur **Ableitung f′**?", "mathe": True,
            "optionen": optionen, "richtig": [optionen.index(abl)], "pruefung": {"art": "termgleich", "ziel": abl},
            "graph": {"x": [-4, 4], "y": [-9, 9], "kurven": [{"term": schul(f), "name": "f"}]},
            "erklaerung": "Wo f steigt, ist f′ positiv; wo f fällt, negativ; an Hoch- und Tiefpunkten ist f′ = 0. "
                          f"Hier passt `{abl}`.",
            "tipps": ["Wo hat f einen Hoch- oder Tiefpunkt? Dort muss f′ null sein.", "Steigt f ganz links? Dann muss f′ dort positiv sein."]}


def e4_2(r, s):
    a, b = sorted(r.sample(range(-3, 4), 2))
    k = r.choice([1, -1, R(1, 2), R(-1, 2)])
    fs = k * (X - a) * (X - b)
    art = r.choice(["Hochpunkt", "Tiefpunkt"])
    groesse = "vzw_plus_minus" if art == "Hochpunkt" else "vzw_minus_plus"
    # k > 0: f′ ist links von a positiv, zwischen a und b negativ → Hochpunkt bei a, Tiefpunkt bei b
    loes = (a if k > 0 else b) if art == "Hochpunkt" else (b if k > 0 else a)
    return zahl(f"Abgebildet ist der Graph der **Ableitung f′**. An welcher Stelle hat f einen **{art}**?", loes,
                ["f hat eine Extremstelle, wo f′ die x-Achse schneidet (f′ = 0).",
                 "Hochpunkt: f′ wechselt von + nach − (der Graph von f′ geht von oben nach unten durch die x-Achse). Tiefpunkt: von − nach +."],
                [((b if loes == a else a), "Prüf den Vorzeichenwechsel: Hochpunkt von f heißt f′ wechselt von plus nach minus.")],
                aus_term={"term": schul(fs), "groesse": groesse},
                graph={"x": [-5, 5], "y": [-6, 6], "kurven": [{"term": schul(fs), "name": "f′"}]})


# ── E5 Kurvendiskussion ───────────────────────────────────

def e5_1(r, s):
    if s == 1:
        a = r.randint(1, 5)
        f = X ** 3 - a * a * X
    elif s == 2:
        a, b = nz(r, -5, 5), nz(r, -5, 5)
        if a == b:
            return None
        f = X * (X - a) * (X - b)
    elif s == 3:
        a, b = r.randint(1, 4), r.randint(1, 4)
        if a == b:
            return None
        f = (X ** 2 - a * a) * (X ** 2 - b * b)
    else:
        a, c = nz(r, -4, 4), r.choice([2, 3, R(1, 2)])
        f = c * X ** 2 * (X - a)
    term = schul(f)
    nst = sorted(sympy.solveset(f, X, sympy.S.Reals), reverse=True)
    loes = "; ".join(zt(Fz(v)) for v in nst)
    return {"typ": "quadratisch", "frage": f"Berechne alle **Nullstellen** von `f(x) = {term}`.", "gleichung": f"{term} = 0", "loesung": loes,
            "weg": [f"{term} = 0", " oder ".join(f"x = {zt(Fz(v))}" for v in nst)],
            "tipps": ["Fehlt die Zahl ohne x, kannst du x (oder x²) herausheben.", "Dann Produkt-Null-Satz: jeder Faktor = 0.",
                      "Bei x⁴ und x²: Ersetze x² durch u – dann ist es eine quadratische Gleichung."],
            "fehler": []}


def e5_2(r, s):
    return e3_3(r, 3 if s <= 2 else 4)


def e5_3(r, s):
    return e3_5(r, s)


# ── E6 Anwendungen ────────────────────────────────────────

def e6_1(r, s):
    a, b = r.choice([1, 2, 3, R(1, 2)]), nz(r, 0, 8)
    sexpr = a * X ** 3 / 3 + b * X if s >= 3 else r.choice([2, 3, 5]) * X ** 2 + b * X
    t0 = r.randint(1, 5)
    vexpr = sympy.diff(sexpr, X)
    if s <= 2 or r.random() < .5:
        return zahl(f"Für eine Bewegung gilt `s(t) = {schul(sexpr, 't')}` (s in m, t in s). Wie groß ist die **Geschwindigkeit** zum "
                    f"Zeitpunkt t = {t0}?", Fz(vexpr.subs(X, t0)), ["Geschwindigkeit `v(t) = s′(t)`.", f"`v(t) = {schul(vexpr, 't')}`."],
                    [(Fz(sexpr.subs(X, t0)), "Das ist der Weg s(t). Gesucht ist die Geschwindigkeit v(t) = s′(t).")],
                    aus_term={"term": schul(sexpr), "groesse": "ableitung", "x": t0}, einheit="m/s")
    return zahl(f"Für eine Bewegung gilt `s(t) = {schul(sexpr, 't')}` (s in m, t in s). Wie groß ist die **Beschleunigung** zum "
                f"Zeitpunkt t = {t0}?", Fz(sympy.diff(vexpr, X).subs(X, t0)),
                ["Beschleunigung `a(t) = v′(t) = s″(t)`.", f"`v(t) = {schul(vexpr, 't')}`, also `a(t) = {schul(sympy.diff(vexpr, X), 't')}`."],
                [(Fz(vexpr.subs(X, t0)), "Das ist die Geschwindigkeit. Noch einmal ableiten.")],
                aus_term={"term": schul(vexpr), "groesse": "ableitung", "x": t0}, einheit="m/s²")


def e6_2(r, s):
    fix, var, quad = r.choice([200, 300, 500, 1000]), r.choice([10, 15, 20, 25]), r.choice([R(1, 2), R(1, 10), R(1, 5), 1])
    K = quad * X ** 2 + var * X + fix
    preis = r.choice([40, 50, 60, 80])
    E = preis * X
    x0 = r.choice([10, 20, 30, 40])
    if s == 1:
        return zahl(f"Kostenfunktion `K(x) = {schul(K)}` (x in Stück, K in €). Wie hoch sind die **Fixkosten**?", fix,
                    ["Fixkosten fallen auch an, wenn nichts produziert wird: K(0)."], [], aus_term={"term": schul(K), "groesse": "wert", "x": 0}, einheit="€")
    if s == 2:
        return zahl(f"`K(x) = {schul(K)}`. Berechne die **Grenzkosten** bei x = {x0} (also K′({x0})).", Fz(sympy.diff(K, X).subs(X, x0)),
                    ["Grenzkosten = K′(x): ungefähr die Kosten für ein zusätzliches Stück.", f"`K′(x) = {schul(sympy.diff(K, X))}`."],
                    [(Fz(K.subs(X, x0)), "Das sind die Gesamtkosten K(x₀). Gesucht ist K′(x₀).")],
                    aus_term={"term": schul(K), "groesse": "ableitung", "x": x0}, einheit="€/Stück")
    G = E - K
    if s == 3:
        return zahl(f"Kosten `K(x) = {schul(K)}`, Erlös `E(x) = {preis}x`. Wie groß ist der **Gewinn** bei x = {x0} Stück?", Fz(G.subs(X, x0)),
                    ["Gewinn = Erlös − Kosten: `G(x) = E(x) − K(x)`.", f"`G({x0}) = {preis}·{x0} − K({x0})`."],
                    [(Fz((K - E).subs(X, x0)), "Erlös minus Kosten – nicht umgekehrt.")],
                    aus_term={"term": schul(G), "groesse": "wert", "x": x0}, einheit="€")
    # Break-even direkt aus den Nullstellen bauen: G(x) = −q(x − x1)(x − x2), K = E − G
    x1, x2 = sorted(r.sample([10, 20, 30, 40, 50, 60, 80], 2))
    q = r.choice([R(1, 10), R(1, 5), R(1, 2)])
    K = sympy.expand(E + q * (X - x1) * (X - x2))
    if sympy.Poly(K, X).coeff_monomial(X) <= 0:
        return None
    G = E - K
    loes = f"{x2}; {x1}"
    return {"typ": "quadratisch", "frage": f"Kosten `K(x) = {schul(K)}`, Erlös `E(x) = {preis}x`. Bei welchen Stückzahlen ist der Gewinn "
                                           "genau 0 (Gewinngrenzen, Break-even)?",
            "gleichung": f"{preis}x = {schul(K)}", "loesung": loes, "weg": [f"{schul(G)} = 0", f"x = {x2} oder x = {x1}"],
            "tipps": ["Gewinn 0 heißt Erlös = Kosten.", "Alles auf eine Seite und mit der Lösungsformel lösen."], "fehler": []}

# ── E7 Integralrechnung ───────────────────────────────────

def e7_1(r, s):
    if s <= 2:
        n = r.randint(1, 5)
        a = 1 if s == 1 else nz(r, 2, 8)
        f = a * X ** n
    elif s == 3:
        f = zpoly(r, 2, -4, 4)
    else:
        f = r.choice([X ** -2, 2 * X ** -3, sympy.cos(X), sympy.exp(X), 3 * sympy.sin(X)])
    stamm = sympy.integrate(f, X)
    ft = schul(f) if f.is_polynomial(X) else {X ** -2: "1/x^2", 2 * X ** -3: "2/x^3", sympy.cos(X): "cos(x)", sympy.exp(X): "e^x",
                                                3 * sympy.sin(X): "3sin(x)"}[f]
    st = schul(stamm) if stamm.is_polynomial(X) else {X ** -2: "-1/x", 2 * X ** -3: "-1/x^2", sympy.cos(X): "sin(x)", sympy.exp(X): "e^x",
                                                       3 * sympy.sin(X): "-3cos(x)"}[f]
    falsch = schul(sympy.diff(f, X)) if f.is_polynomial(X) else None
    return {"typ": "term", "frage": f"Gib eine **Stammfunktion** F von `f(x) = {ft}` an.", "form": "stammfunktion", "loesung": st,
            "stammfunktion_von": ft,
            "tipps": ["Stammfunktion: Ableiten rückwärts. Probe: F′ muss f ergeben.", "`xⁿ` → `xⁿ⁺¹/(n + 1)`: Hochzahl um 1 erhöhen, durch die neue Hochzahl dividieren.",
                      "Eine Konstante + C darfst du dazuschreiben, musst aber nicht."],
            "fehler": [{"antwort": falsch, "hinweis": "Das ist die Ableitung. Gesucht ist umgekehrt eine Funktion, deren Ableitung f ist."}] if falsch else []}


def e7_2(r, s):
    f = zpoly(r, min(s + 1, 4), -6, 6, (1,) if s < 3 else (1, 2))
    return {"typ": "term", "frage": f"Gib eine **Stammfunktion** von `f(x) = {schul(f)}` an.", "form": "stammfunktion",
            "loesung": schul(sympy.integrate(f, X)), "stammfunktion_von": schul(f),
            "tipps": ["Summenregel: Jedes Glied einzeln integrieren.", "Faktorregel: Die Zahl davor bleibt stehen.", "Eine Zahl k wird zu k·x."],
            "fehler": [{"antwort": schul(sympy.diff(f, X)), "hinweis": "Das ist die Ableitung – gesucht ist das Gegenteil."}]}


def e7_3(r, s):
    f = zpoly(r, 1 if s == 1 else 2 if s <= 3 else 3, -4, 4)
    a, b = sorted(r.sample(range(-2, 5), 2))
    wert_ = Fz(sympy.integrate(f, (X, a, b)))
    Fst = sympy.integrate(f, X)
    return zahl(f"Berechne `∫ ({schul(f)}) dx` von {a} bis {b}.", wert_,
                ["Stammfunktion F bestimmen.", f"`F(x) = {schul(Fst)}`.", f"Ergebnis = F({b}) − F({a})."],
                [(Fz(Fst.subs(X, a) - Fst.subs(X, b)), "Obere Grenze minus untere: F(b) − F(a)."),
                 (Fz(f.subs(X, b) - f.subs(X, a)), "Du brauchst F (die Stammfunktion), nicht f.")],
                integral={"term": schul(f), "von": a, "bis": b})


def e7_4(r, s):
    if s <= 2:
        a, k = r.randint(1, 4), r.choice([1, 2, R(1, 2)])
        f = k * (a * a - X ** 2) if s == 1 else k * (X ** 2 - a * a)
        von, bis = -a, a
    else:
        a, b = sorted(r.sample(range(-3, 4), 2))
        f = (X - a) * (X - b)
        von, bis = a - r.randint(0, 2), b + r.randint(1, 2)

    stellen = sorted({von, bis, *[n for n in sympy.solve(f, X) if n.is_real and von < n < bis]})
    flaeche = Fz(sum(abs(sympy.integrate(f, (X, u, v))) for u, v in zip(stellen, stellen[1:])))
    integral = Fz(sympy.integrate(f, (X, von, bis)))
    return zahl(f"Wie groß ist die **Fläche** zwischen dem Graphen von `f(x) = {schul(f)}` und der x-Achse im Intervall [{von}; {bis}]?", flaeche,
                ["Zuerst die Nullstellen im Intervall suchen.", "Flächen unter der x-Achse ergeben ein negatives Integral – davon den **Betrag** nehmen.",
                 "Teilflächen einzeln berechnen und addieren."],
                [(integral if integral != flaeche else None, "Teile unter der x-Achse zählen negativ – für die Fläche Beträge der Teilintegrale addieren.")],
                flaeche={"term": schul(f), "von": von, "bis": bis},
                graph={"x": [von - 1, bis + 1], "y": [-8, 8], "kurven": [{"term": schul(f), "name": "f"}]})


def e7_5(r, s):
    a, b = sorted(r.sample(range(-3, 4), 2))
    g = nz(r, -2, 2) * X + nz(r, -3, 3)
    f = g - (X - a) * (X - b)  # f liegt zwischen a und b über g
    diff = f - g
    flaeche = Fz(sympy.integrate(diff, (X, a, b)))
    return zahl(f"Berechne die Fläche zwischen den Graphen von `f(x) = {schul(f)}` und `g(x) = {schul(g)}`.", flaeche,
                ["Schnittstellen: f(x) = g(x).", f"Sie schneiden sich bei x = {a} und x = {b}.", "Fläche = ∫ (oberer − unterer Graph) dx."],
                [(-flaeche, "Fläche ist immer positiv: oberer minus unterer Graph.")],
                flaeche={"term": schul(diff), "von": a, "bis": b},
                graph={"x": [a - 2, b + 2], "y": [-9, 9], "kurven": [{"term": schul(f), "name": "f"}, {"term": schul(g), "name": "g"}]})


def e7_6(r, s):
    n = r.choice([2, 4]) if s <= 2 else r.choice([4, 5])
    bis = r.choice([2, 4]) if s <= 2 else r.choice([2, 3, 5])
    h = R(bis, n)
    art = r.choice(["Untersumme", "Obersumme"])
    # f(x) = x² ist auf [0; b] steigend: Untersumme nimmt linke, Obersumme rechte Ränder
    knoten = [h * i for i in (range(n) if art == "Untersumme" else range(1, n + 1))]
    wert_ = Fz(sum(h * k ** 2 for k in knoten))
    rechnung = f"{zt(Fz(h))}·(" + " + ".join(f"{zt(Fz(k))}^2" for k in knoten) + ")"
    return zahl(f"Berechne die **{art}** von `f(x) = x²` im Intervall [0; {bis}] mit {n} gleich breiten Streifen.", wert_,
                [f"Streifenbreite: {bis} : {n} = {zt(Fz(h))}.",
                 "f ist hier steigend: Für die Untersumme nimmst du jeweils den linken Rand, für die Obersumme den rechten.",
                 "Summe aus Breite mal Höhe aller Streifen."],
                [], rechnung=rechnung)


def e7_7(r, s):
    if s <= 2:
        v0, a = r.choice([0, 2, 5, 10]), r.choice([1, 2, 3])
        v = v0 + a * X
        t1 = r.randint(2, 8)
        return zahl(f"Ein Fahrzeug hat die Geschwindigkeit `v(t) = {schul(v, 't')}` (v in m/s, t in s). Welchen Weg legt es in den ersten "
                    f"{t1} Sekunden zurück?", Fz(sympy.integrate(v, (X, 0, t1))),
                    ["Weg = Integral der Geschwindigkeit: `∫ v(t) dt` von 0 bis t₁.", "Stammfunktion bilden, Grenzen einsetzen."],
                    [(Fz(v.subs(X, t1)) * t1, "Die Geschwindigkeit ist nicht konstant – du brauchst das Integral.")],
                    integral={"term": schul(v), "von": 0, "bis": t1}, einheit="m")
    rate = r.choice([R(1, 2), 1, 2]) * X ** 2 + r.choice([0, 5, 10])
    t1 = r.choice([3, 6, 9])
    return zahl(f"In ein Becken fließt Wasser mit der Rate `r(t) = {schul(rate, 't')}` (Liter pro Minute). Wie viele Liter fließen in den "
                f"ersten {t1} Minuten hinein?", Fz(sympy.integrate(rate, (X, 0, t1))),
                ["Gesamtmenge = Integral der Rate.", f"`∫ r(t) dt` von 0 bis {t1}."], [],
                integral={"term": schul(rate), "von": 0, "bis": t1}, einheit="l")


AUFGABEN = [("E1.1", e1_1, 6), ("E1.2", e1_2, 6), ("E1.3", e1_3, 5), ("E1.4", e1_4, 5),
            ("E2.1", e2_1, 6), ("E2.2", e2_2, 6), ("E2.3", e2_3, 6), ("E2.4", e2_4, 3),
            ("E3.1", e3_1, 6), ("E3.2", e3_2, 6), ("E3.3", e3_3, 6), ("E3.4", e3_4, 6), ("E3.5", e3_5, 6),
            ("E4.1", e4_1, 5), ("E4.2", e4_2, 5), ("E5.1", e5_1, 5), ("E5.2", e5_2, 5), ("E5.3", e5_3, 5),
            ("E6.1", e6_1, 5), ("E6.2", e6_2, 5),
            ("E7.1", e7_1, 4), ("E7.2", e7_2, 6), ("E7.3", e7_3, 6), ("E7.4", e7_4, 5), ("E7.5", e7_5, 5), ("E7.6", e7_6, 3), ("E7.7", e7_7, 5)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261028)
    for lid, fn, n in AUFGABEN:
        schreibe(lid, erzeuge(lid, r, fn, n), "e.py")


if __name__ == "__main__":
    main()
