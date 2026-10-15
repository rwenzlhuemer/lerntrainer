"""
Generator für Kapitel A3 (Potenzen und Wurzeln). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/a3.py
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


def wert(text) -> F:
    return F(str(sympy.nsimplify(notation.ausdruck(text))))


def zt(q) -> str:
    q = F(q)
    return dez(q) if endlich(q) and q.denominator != 1 and q.denominator <= 1000 else z(q)


def zahl_aufgabe(frage, ergebnis, weg, tipps, fehler, rechnung=None, form=None, einheit=None, loesung=None):
    a = {"typ": "zahl", "frage": frage, "loesung": loesung or zt(ergebnis)}
    if form:
        a["form"] = form
    if einheit:
        a["einheit"] = einheit
    a.update({"weg": weg, "tipps": tipps, "fehler": [{**f, "antwort": zt(F(f["antwort"]))} for f in fehler_zahlen(ergebnis, fehler)]})
    if rechnung:
        a["rechnung"] = rechnung
    return a


# ── A3.1 Was ist eine Potenz? ─────────────────────────────

def a3_1(r, s):
    if s == 1:
        b, n = r.choice([(2, r.randint(2, 6)), (3, r.randint(2, 4)), (10, r.randint(2, 6)), (r.randint(4, 9), 2), (5, 3), (1, r.randint(5, 9))])
        text = f"{b}^{n}"
    elif s == 2:
        b, n = nz(r, -5, -1), r.randint(2, 5)
        text = r.choice([f"({b})^{n}", f"-{abs(b)}^{n}"]) if abs(b) > 1 else f"({b})^{r.randint(5, 12)}"
    elif s == 3:
        q = r.choice([F(1, 2), F(2, 3), F(3, 4), F(-1, 2), F(-2, 3)])
        if r.random() < .5:
            text = f"({z(q)})^{r.randint(2, 3)}"
        else:
            text = f"{dez(F(r.randint(1, 5), 10))}^{r.randint(2, 3)}"
    else:
        a, b, n, m = r.randint(2, 4), r.randint(2, 4), r.randint(2, 4), r.randint(2, 3)
        text = r.choice([f"{a}^{n} - {b}^{m}", f"(-{a})^{n} - {a}^{n}", f"-{a}^{n} + (-{b})^{m}", f"2 · {a}^{n} - ({b} - {a + b})^{m}"])
    erg = wert(text)
    if text == "":
        return None
    fehler = []
    if s == 1:
        fehler.append((b * n, "Eine Potenz heißt: die Basis so oft **mit sich selbst** multiplizieren, wie die Hochzahl sagt – "
                              "nicht Basis mal Hochzahl."))
    if text.startswith("-") and "(" not in text.split("^")[0]:
        fehler.append((-erg, "`-3²` heißt `-(3²)`: Die Hochzahl gehört nur zur 3, das Minus kommt danach."))
    elif "(-" in text:
        fehler.append((-erg, "Prüf das Vorzeichen: Gerade Hochzahl → positiv, ungerade Hochzahl → negativ."))
    weg = [f"{text} = {zt(erg)}"]
    if s <= 2 and text.count("^") == 1:
        basis, hoch = text.split("^")
        if int(hoch) <= 6:
            if basis.startswith("-"):
                weg = [f"{text} = -({' · '.join([basis[1:]] * int(hoch))}) = {zt(erg)}"]
            else:
                weg = [f"{text} = {' · '.join([basis] * int(hoch))} = {zt(erg)}"]
    return zahl_aufgabe(f"Berechne `{text}`.", erg, weg,
                        ["Die Hochzahl sagt, wie oft die Basis mit sich selbst multipliziert wird: `2³ = 2 · 2 · 2`.",
                         "Achte auf Klammern: `(-2)²` ist die -2 mal sich selbst, `-2²` ist `-(2 · 2)`.",
                         "Bei Brüchen und Dezimalzahlen: Zähler und Nenner einzeln potenzieren bzw. Kommastellen zählen."],
                        fehler, rechnung=text)


# ── A3.2 Potenzregeln ─────────────────────────────────────

def mon(k, potenzen):
    """3, {'a': 2, 'b': 1} → '3a^2b'"""
    k = F(k)
    teile = "".join(v + (f"^{e}" if e != 1 else "") for v, e in potenzen.items() if e != 0)
    if not teile:
        return z(k)
    if k == 1:
        return teile
    if k == -1:
        return "-" + teile
    return f"{z(k)}{teile}" if k.denominator == 1 else f"{k.numerator}{teile}/{k.denominator}"


def a3_2(r, s):
    v = r.choice(["x", "a", "b"])
    falsch_k = None
    if s == 1:
        m, n = r.randint(2, 7), r.randint(2, 6)
        art = r.choice(["mal", "durch", "hoch"])
        if art == "mal":
            term, soll, falsch = f"{v}^{m} · {v}^{n}", {v: m + n}, {v: m * n}
            regel = "Gleiche Basis multiplizieren: Hochzahlen **addieren**."
        elif art == "durch":
            m = n + r.randint(1, 6)
            term, soll, falsch = f"{v}^{m} : {v}^{n}", {v: m - n}, {v: m + n}
            regel = "Gleiche Basis dividieren: Hochzahlen **subtrahieren**."
        else:
            term, soll, falsch = f"({v}^{m})^{n}", {v: m * n}, {v: m + n}
            regel = "Potenz einer Potenz: Hochzahlen **multiplizieren**."
        kf = 1
        fehl_text = "Verwechselt: Beim Multiplizieren addierst du, beim Potenzieren multiplizierst du die Hochzahlen."
    elif s == 2:
        a, b, m, n = r.randint(2, 6), r.randint(2, 6), r.randint(2, 6), r.randint(2, 5)
        art = r.choice(["mal", "durch", "hoch"])
        if art == "mal":
            term, kf, soll, falsch = f"{a}{v}^{m} · {b}{v}^{n}", a * b, {v: m + n}, {v: m * n}
            regel = "Zahlen multiplizieren, Hochzahlen addieren."
            fehl_text = "Die Hochzahlen werden addiert, nicht multipliziert."
        elif art == "durch":
            m = n + r.randint(1, 5)
            term, kf, soll, falsch = f"{a * b}{v}^{m}/({a}{v}^{n})", b, {v: m - n}, {v: m + n}
            regel = "Zahlen dividieren, Hochzahlen subtrahieren."
            fehl_text = "Beim Dividieren werden die Hochzahlen subtrahiert."
        else:
            n = r.randint(2, 3)
            term, kf, soll, falsch = f"({a}{v}^{m})^{n}", a ** n, {v: m * n}, {v: m * n}
            regel = "Jeder Faktor in der Klammer wird potenziert – auch die Zahl."
            fehl_text = f"Auch die Zahl {a} wird hoch {n} genommen: `{a}^{n} = {a ** n}`."
            falsch_k = a
    elif s == 3:
        m1, n1, m2, n2 = (r.randint(1, 5) for _ in range(4))
        art = r.choice(["mal", "durch", "hoch"])
        if art == "mal":
            term, kf, soll = f"{mon(1, {'a': m1, 'b': n1})} · {mon(1, {'a': m2, 'b': n2})}", 1, {"a": m1 + m2, "b": n1 + n2}
            falsch = {"a": m1 * m2, "b": n1 * n2}
            regel = "Jede Basis für sich: Hochzahlen von a addieren, Hochzahlen von b addieren."
            fehl_text = "Die Hochzahlen werden addiert, nicht multipliziert."
        elif art == "durch":
            m2, n2 = r.randint(1, 4), r.randint(1, 3)
            m1, n1 = m2 + r.randint(1, 4), n2 + r.randint(1, 3)
            term, kf, soll = f"{mon(1, {'x': m1, 'y': n1})}/({mon(1, {'x': m2, 'y': n2})})", 1, {"x": m1 - m2, "y": n1 - n2}
            falsch = {"x": m1 + m2, "y": n1 + n2}
            regel = "Jede Basis für sich: Hochzahlen subtrahieren."
            fehl_text = "Beim Dividieren werden die Hochzahlen subtrahiert."
        else:
            n = r.randint(2, 4)
            term, kf, soll = f"({mon(1, {'a': m1, 'b': n1})})^{n}", 1, {"a": m1 * n, "b": n1 * n}
            falsch = {"a": m1 + n, "b": n1 + n}
            regel = "Jeder Faktor in der Klammer wird potenziert: Hochzahlen multiplizieren."
            fehl_text = "Potenz einer Potenz: Hochzahlen multiplizieren, nicht addieren."
    else:
        art = r.choice(["minus", "zahl", "kette"])
        if art == "minus":
            m, n = r.randint(2, 5), r.choice([2, 3, 5])
            term, kf, soll = f"(-{v}^{m})^{n}", (-1) ** n, {v: m * n}
            falsch = {v: m * n}
            regel = "Auch das Minus wird potenziert: gerade Hochzahl → plus, ungerade → minus."
            fehl_text = "Das Vorzeichen: `(-1)` hoch einer geraden Zahl ist +1, hoch einer ungeraden −1."
            falsch_k = -kf
        elif art == "zahl":
            a, m, n = r.randint(2, 3), r.randint(2, 4), r.randint(2, 3)
            term, kf, soll = f"({a}x^{m})^{n} · x", a ** n, {"x": m * n + 1}
            falsch = {"x": m * n}
            regel = "Erst die Klammer potenzieren, dann mit x multiplizieren (x = x¹)."
            fehl_text = "Vergiss das x am Schluss nicht: x = x¹, also Hochzahl + 1."
        else:
            a, m, n = r.randint(2, 4), r.randint(2, 4), r.randint(1, 3)
            term, kf, soll = f"({a}x^{m}y)^2 : ({a}x^{n}y)", a, {"x": 2 * m - n, "y": 1}
            falsch = {"x": 2 * m + n, "y": 2}
            regel = "Zuerst die Klammer quadrieren, dann dividieren: Zahlen dividieren, Hochzahlen subtrahieren."
            fehl_text = "Beim Dividieren werden die Hochzahlen subtrahiert."
    loesung = mon(kf, soll)
    if falsch_k is None:
        falsch_k = kf
    fehler = [(mon(falsch_k, falsch), fehl_text)]
    expr_ok = sympy.simplify(notation.ausdruck(term) - notation.ausdruck(loesung)) == 0
    if not expr_ok:
        raise AssertionError((term, loesung))
    return {"typ": "term", "term": term, "form": "potenz", "loesung": loesung,
            "anweisung": "Vereinfache mit den Potenzregeln.",
            "weg": [f"{term} = {loesung}"],
            "tipps": [regel, "Zahlen vor den Variablen rechnest du ganz normal aus.",
                      f"Ergebnis zur Kontrolle: Die Hochzahl{'en' if len(soll) > 1 else ''} im Ergebnis: "
                      + ", ".join(f"{k}: {e}" for k, e in soll.items()) + "."],
            "fehler": [{"antwort": a, "hinweis": h} for a, h in fehler
                       if sympy.simplify(notation.ausdruck(a) - notation.ausdruck(loesung)) != 0]}


# ── A3.3 Negative Hochzahlen, Zehnerpotenzen, Gleitkomma ──

def gleitkomma_text(q):
    """0,00045 → '4,5·10^-4'"""
    q = F(q)
    e = 0
    m = abs(q)
    while m >= 10:
        m /= 10
        e += 1
    while m < 1:
        m *= 10
        e -= 1
    return f"{'-' if q < 0 else ''}{dez(m)}·10^{e}"


def a3_3(r, s):
    w = r.random()
    if s == 1:
        if w < .5:
            b, n = r.choice([2, 3, 4, 5, 10]), r.randint(1, 3)
            text = f"{b}^-{n}"
            erg = F(1, b ** n)
            return zahl_aufgabe(f"Berechne `{text}`. Gib das Ergebnis als Bruch an.", erg, [f"{text} = 1/{b}^{n} = {z(erg)}"],
                                ["Eine negative Hochzahl heißt: **Kehrwert**. `a^-n = 1/a^n`.", f"`{text} = 1/{b}^{n}`."],
                                [(-F(b ** n), "Eine negative Hochzahl macht die Zahl nicht negativ – sie bedeutet „1 durch …“."),
                                 (F(-b * n), "Eine negative Hochzahl bedeutet „1 durch …“, nicht mal.")],
                                rechnung=text, form="gekuerzt", loesung=z(erg))
        n = r.randint(1, 4)
        text = f"10^-{n}"
        erg = F(1, 10 ** n)
        return zahl_aufgabe(f"Schreib `{text}` als Dezimalzahl.", erg, [f"{text} = 1/10^{n} = {dez(erg)}"],
                            ["`10^-n = 1/10^n`: eine 1 an der n-ten Stelle nach dem Komma.", f"`{text} = 1/{10 ** n}`."],
                            [(-F(10 ** n), "Eine negative Hochzahl macht die Zahl nicht negativ – sie bedeutet „1 durch …“.")],
                            rechnung=text, form="dezimal", loesung=dez(erg))
    if s == 2:
        if w < .5:
            m = F(r.randint(11, 99), 10)
            e = -r.randint(2, 6)
            q = m * F(10) ** e
            lsg = gleitkomma_text(q)
            return zahl_aufgabe(f"Schreib `{dez(q)}` in Gleitkommadarstellung.", q, [f"{dez(q)} = {lsg}"],
                                ["Gleitkommadarstellung: eine Zahl zwischen 1 und 10, mal einer Zehnerpotenz.",
                                 "Zähl, um wie viele Stellen das Komma nach rechts rücken muss – das ist die (negative) Hochzahl."],
                                [], rechnung=lsg, form="gleitkomma", loesung=lsg)
        m = F(r.randint(11, 99), 10)
        e = r.randint(3, 7)
        q = m * 10 ** e
        text = gleitkomma_text(q)
        return zahl_aufgabe(f"Schreib `{text}` als ganze Zahl.", q, [f"{text} = {z(q)}"],
                            ["Mal 10^n heißt: Das Komma rückt n Stellen nach rechts.", "Fehlende Stellen füllst du mit Nullen auf."],
                            [(m * 10 ** (e - 1), "Das Komma rückt genau so viele Stellen, wie die Hochzahl sagt.")],
                            rechnung=text)
    if s == 3:
        if w < .5:
            v = r.choice("xab")
            m, n = r.randint(2, 6), r.randint(2, 8)
            term = f"{v}^-{m} · {v}^{n}"
            if n == m:
                return None
            loesung = v if n - m == 1 else f"{v}^{n - m}" if n > m else f"1/{v}" if m - n == 1 else f"1/{v}^{m - n}"
            return {"typ": "term", "term": term, "form": "potenz", "loesung": loesung,
                    "anweisung": "Vereinfache mit den Potenzregeln.", "weg": [f"{term} = {v}^({n} - {m}) = {loesung}"],
                    "tipps": ["Die Regeln gelten auch für negative Hochzahlen: Beim Multiplizieren addieren.",
                              f"`-{m} + {n} = {n - m}`."],
                    "fehler": [{"antwort": f"{v}^{-m * n}", "hinweis": "Beim Multiplizieren werden die Hochzahlen addiert."}]}
        a, b = F(r.randint(11, 49), 10), F(r.randint(11, 49), 10)
        e1, e2 = r.randint(2, 6), -r.randint(2, 8)
        prod = a * b * F(10) ** (e1 + e2)
        text = f"({dez(a)}·10^{e1}) · ({dez(b)}·10^{e2})"
        lsg = gleitkomma_text(prod)
        return zahl_aufgabe(f"Berechne `{text}` und gib das Ergebnis in Gleitkommadarstellung an.", prod,
                            [" = ".join(dict.fromkeys([text, f"{dez(a * b)}·10^{e1 + e2}", lsg]))],
                            ["Zahlen multiplizieren, Zehnerpotenzen multiplizieren (Hochzahlen addieren).",
                             f"`{dez(a)} · {dez(b)} = {dez(a * b)}` und `10^{e1} · 10^{e2} = 10^{e1 + e2}`.",
                             "Steht vorne eine Zahl ab 10, schiebst du das Komma noch eine Stelle und erhöhst die Hochzahl um 1."],
                            [], rechnung=text, form="gleitkomma", loesung=lsg)
    # Stufe 4
    if w < .4:
        a, b = F(r.randint(2, 9)), F(r.randint(2, 9))
        e1, e2 = r.randint(-9, -2), r.randint(3, 9)
        q = a * F(10) ** e1 / (b * F(10) ** e2)
        text = f"({z(a)}·10^{e1}) : ({z(b)}·10^{e2})"
        if not endlich(a / b):
            return None
        lsg = gleitkomma_text(q)
        return zahl_aufgabe(f"Berechne `{text}` und gib das Ergebnis in Gleitkommadarstellung an.", q,
                            [" = ".join(dict.fromkeys([text, f"{dez(a / b)}·10^{e1 - e2}", lsg]))],
                            ["Zahlen dividieren, Zehnerpotenzen dividieren (Hochzahlen subtrahieren).",
                             f"`10^{e1} : 10^{e2} = 10^({e1} - {e2}) = 10^{e1 - e2}`.",
                             "Steht vorne eine Zahl unter 1, schiebst du das Komma und verringerst die Hochzahl um 1."],
                            [], rechnung=text, form="gleitkomma", loesung=lsg)
    if w < .7:
        q = r.choice([F(2, 3), F(3, 4), F(1, 5), F(2, 5), F(4, 3)])
        n = r.randint(1, 3)
        text = f"({z(q)})^-{n}"
        erg = (1 / q) ** n
        return zahl_aufgabe(f"Berechne `{text}`.", erg, [f"{text} = ({z(1 / q)})^{n} = {z(erg)}"],
                            ["Negative Hochzahl beim Bruch: Bruch umdrehen, dann mit positiver Hochzahl rechnen.",
                             f"`{text} = ({z(1 / q)})^{n}`."],
                            [(q ** n, "Die negative Hochzahl heißt: Kehrwert. Den Bruch erst umdrehen.")],
                            rechnung=text, form="gekuerzt", loesung=z(erg))
    v = r.choice("xa")
    m, n, k = r.randint(2, 5), r.randint(2, 6), r.randint(2, 3)
    term = f"({v}^-{m})^{k} · {v}^{n}"
    e = -m * k + n
    if e in (0, 1):
        return None
    loesung = f"{v}^{e}" if e > 0 else f"1/{v}" if e == -1 else f"1/{v}^{-e}"
    return {"typ": "term", "term": term, "form": "potenz", "loesung": loesung,
            "anweisung": "Vereinfache mit den Potenzregeln.", "weg": [f"{term} = {v}^{-m * k} · {v}^{n} = {loesung}"],
            "tipps": ["Zuerst die Klammer: Hochzahlen multiplizieren.", f"`({v}^-{m})^{k} = {v}^{-m * k}`. Dann Hochzahlen addieren."],
            "fehler": [{"antwort": f"{v}^{-m + k + n}", "hinweis": "Potenz einer Potenz: Hochzahlen multiplizieren, nicht addieren."}]}


# ── A3.4 Wurzeln ──────────────────────────────────────────

WURZEL_POTENZ = [("√x", ["x^(1/2)", "x^2", "x/2"]), ("1/√x", ["x^(-1/2)", "x^(1/2)", "-x^2"]),
                 ("x·√x", ["x^(3/2)", "x^(1/2)", "x^2"]), ("√x·√x", ["x", "2√x", "x^2"]),
                 ("x^(1/2) · x^(1/2)", ["x", "x^(1/4)", "√(2x)"]), ("(√x)^4", ["x^2", "x^4", "4x"])]


def a3_4(r, s):
    w = r.random()
    if s == 1:
        n = r.randint(2, 15)
        if w < .6:
            text, erg = f"√{n * n}", F(n)
        elif w < .8:
            text, erg = f"√{dez(F(n * n, 100))}", F(n, 10)
        else:
            a, b = r.randint(1, 9), r.randint(2, 10)
            if a == b:
                return None
            text, erg = f"√({a * a}/{b * b})", F(a, b)
        return zahl_aufgabe(f"Berechne `{text}`.", erg, [f"{text} = {zt(erg)}"],
                            ["Die Wurzel fragt: Welche positive Zahl mal sich selbst ergibt die Zahl darunter?",
                             "Bei Brüchen: Wurzel aus Zähler und Nenner einzeln. Bei Dezimalzahlen: Kommastellen halbieren."],
                            [(erg * erg / 2 if erg.denominator == 1 else None, "Wurzelziehen heißt nicht „durch 2“: gesucht ist die Zahl, die mit sich selbst multipliziert die Zahl unter der Wurzel ergibt.")],
                            rechnung=text)
    if s == 2:
        if w < .4:
            a = r.choice([2, 3, 5, 6, 7])
            k = r.randint(2, 5)
            text, erg = f"√{a}·√{a * k * k}", F(a * k)
            weg = [f"{text} = √{a * a * k * k} = {a * k}"]
            tipp = "Zwei Wurzeln darfst du multiplizieren: `√a · √b = √(a · b)`."
        elif w < .7:
            a = r.choice([2, 3, 5, 6])
            k = r.randint(2, 6)
            text, erg = f"√{a * k * k} : √{a}", F(k)
            weg = [f"{text} = √{k * k} = {k}"]
            tipp = "Zwei Wurzeln darfst du dividieren: `√a : √b = √(a : b)`."
        else:
            a, b = r.randint(2, 9), r.randint(2, 9)
            text, erg = f"√({a * a}·{b * b})", F(a * b)
            weg = [f"{text} = √{a * a}·√{b * b} = {a}·{b} = {a * b}"]
            tipp = "Wurzel aus einem Produkt: aus jedem Faktor einzeln die Wurzel ziehen."
        return zahl_aufgabe(f"Berechne `{text}`.", erg, weg,
                            [tipp, "Die Zahl unter der Wurzel soll eine Quadratzahl werden."], [], rechnung=text)
    if s == 3:
        b, zz, n = r.choice([(8, 1, 3), (27, 1, 3), (16, 1, 4), (27, 2, 3), (16, 3, 4), (4, 3, 2), (32, 1, 5),
                             (64, 2, 3), (9, 3, 2), (25, 3, 2), (8, 2, 3), (81, 3, 4), (4, -1, 2), (9, -1, 2), (8, -1, 3)])
        text = f"{b}^({zz}/{n})"
        erg = wert(text)
        wurzel = round(b ** (1 / n))
        return zahl_aufgabe(f"Berechne `{text}`.", erg, [f"{text} = {wurzel}^{zz} = {z(erg)}" if zz != 1 else f"{text} = {z(erg)}"],
                            [f"Die Hochzahl 1/{n} heißt: {n}-te Wurzel. `{b}^(1/{n})` ist die Zahl, die {n}-mal mit sich selbst "
                             f"multipliziert {b} ergibt.",
                             f"Hier ist das {wurzel}. Danach noch hoch {zz}." if zz != 1 else f"Hier ist das {wurzel}."],
                            [(F(b * zz, n), "Eine Bruch-Hochzahl heißt Wurzel – nicht Basis mal Bruch.")],
                            rechnung=text, form="gekuerzt" if erg.denominator != 1 else None, loesung=z(erg))
    if w < .4:
        term, optionen = r.choice(WURZEL_POTENZ)
        optionen = optionen[:]
        r.shuffle(optionen)
        richtig = [i for i, o in enumerate(optionen) if sympy.simplify(notation.ausdruck(o) - notation.ausdruck(term)) == 0]
        if len(richtig) != 1:
            return None
        return {"typ": "auswahl", "frage": f"Welcher Term ist gleich `{term}`?", "mathe": True, "optionen": optionen,
                "richtig": richtig, "pruefung": {"art": "termgleich", "ziel": term},
                "erklaerung": f"`√x = x^(1/2)`. Damit gelten die Potenzregeln: Richtig ist `{optionen[richtig[0]]}`.",
                "tipps": ["Schreib jede Wurzel als Potenz mit der Hochzahl 1/2, dann die Potenzregeln anwenden."]}
    text = r.choice(["√12 · √3", "√0,0009", "(√5)^2", "√(2^6)", "27^(-2/3)", "√(3^2 + 4^2)", "√(13^2 - 12^2)", "√50 : √8",
                     "√(6,25)", "16^(-3/4)", "(√7)^4", "√(10^4)"])
    erg = wert(text)
    return zahl_aufgabe(f"Berechne `{text}`.", erg, [f"{text} = {zt(erg)}"],
                        ["Vereinfache Schritt für Schritt: Wurzeln zusammenfassen, Quadratzahlen erkennen.",
                         "`√a · √b = √(a · b)`, `(√a)² = a`, `a^(1/n)` ist die n-te Wurzel.",
                         "Bei `√(a² + b²)` zuerst unter der Wurzel ausrechnen – die Wurzel einer Summe ist **nicht** die Summe der Wurzeln."],
                        [], rechnung=text)


# ── A3.5 Vorsilben und Einheiten ──────────────────────────

EINHEITEN = {
    1: [("km", "m", 1000), ("kg", "g", 1000), ("m", "cm", 100), ("l", "ml", 1000), ("m", "mm", 1000), ("h", "min", 60)],
    2: [("g", "kg", F(1, 1000)), ("mm", "m", F(1, 1000)), ("ml", "l", F(1, 1000)), ("cm", "m", F(1, 100)), ("min", "h", F(1, 60)),
        ("GB", "MB", 1000)],
    3: [("µm", "m", F(1, 10 ** 6)), ("mg", "g", F(1, 1000)), ("MB", "GB", F(1, 1000)), ("nm", "µm", F(1, 1000)),
        ("t", "kg", 1000), ("kW", "W", 1000)],
    4: [("m²", "cm²", 10000), ("dm³", "l", 1), ("cm³", "ml", 1), ("m³", "l", 1000), ("km/h", "m/s", F(1, F(36, 10))),
        ("cm²", "m²", F(1, 10000))],
}
VORSILBEN = "Vorsilben: Kilo = 1000, Mega = 1 000 000, Giga = 10⁹, Milli = 1/1000, Mikro (µ) = 1/1 000 000, Nano = 10⁻⁹."


def a3_5(r, s):
    von, nach, faktor = r.choice(EINHEITEN[s])
    faktor = F(faktor)
    for _ in range(50):
        menge = F(r.randint(1, 99), r.choice([1, 10, 100])) if s >= 2 else F(r.randint(2, 95), r.choice([1, 10]))
        if von == "km/h":
            menge = F(r.choice([18, 36, 54, 72, 90, 108, 126]))
        if von in ("min",) and nach == "h":
            menge = F(r.choice([15, 30, 45, 90, 150, 12, 6]))
        erg = menge * faktor
        if endlich(erg) and erg.denominator <= 10 ** 7:
            break
    else:
        return None
    if von == "km/h":
        rechnung = f"{z(menge)} : 3,6"
    elif faktor.denominator == 1:
        rechnung = f"{dez(menge)} · {z(faktor)}"
    else:
        rechnung = f"{dez(menge)} : {z(1 / faktor)}"
    flaeche = "²" in von or "³" in von
    return zahl_aufgabe(f"Rechne um: {dez(menge)} {von} = ? {nach}", erg, [f"{rechnung} = {dez(erg)}"],
                        [VORSILBEN, f"Von {von} nach {nach}: {'mal' if faktor > 1 else 'durch'} "
                                    f"{z(faktor) if faktor > 1 else z(1 / faktor) if von != 'km/h' else '3,6'}.",
                         "Bei Flächen zählt der Umrechnungsfaktor doppelt (1 m = 100 cm → 1 m² = 10 000 cm²), bei Volumen dreifach."
                         if flaeche else "In die kleinere Einheit: mal (es werden mehr). In die größere Einheit: durch."],
                        [(menge / faktor if faktor != 1 else None, "Umgekehrt! In eine kleinere Einheit wird die Zahl größer, in eine größere Einheit kleiner."),
                         (menge * 100 if von == "m²" else None, "Bei Flächen: 1 m² = 100 cm · 100 cm = 10 000 cm².")],
                        rechnung=rechnung, einheit=nach, loesung=dez(erg))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261019)
    for lid, fn, n in [("A3.1", a3_1, 10), ("A3.2", a3_2, 10), ("A3.3", a3_3, 10), ("A3.4", a3_4, 10), ("A3.5", a3_5, 8)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "a3.py")


if __name__ == "__main__":
    main()
