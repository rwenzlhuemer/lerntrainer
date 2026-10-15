"""
Generator für Kapitel A1 (Zahlen und Vorzeichen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/a1.py

Stufen: 1 Einstieg (kleine ganze Zahlen) · 2 Üben (doppelte Vorzeichen) · 3 Vertiefen (mehrere Glieder,
Hochzahlen) · 4 Matura-Niveau (Dezimalzahlen, Brüche, lange Ausdrücke).
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent))
import notation  # noqa: E402
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, nz, schreibe, z  # noqa: E402


def wert(text) -> F:
    return F(str(notation.zahl(text)))


def zt(q, dezimal=False) -> str:
    """Zahl als Text, als Dezimalzahl wenn gewünscht und möglich"""
    q = F(q)
    return dez(q) if dezimal and endlich(q) else z(q)


def kz(q, dezimal=False) -> str:
    """negative Zahl in Klammern"""
    return f"({zt(q, dezimal)})" if F(q) < 0 else zt(q, dezimal)


def zahl_aufgabe(frage, ergebnis, weg, tipps, fehler, rechnung=None, einheit=None, dezimal=False):
    a = {"typ": "zahl", "frage": frage, "loesung": zt(ergebnis, dezimal), "weg": weg, "tipps": tipps,
         "fehler": [{**f, "antwort": zt(F(f["antwort"]), dezimal)} for f in fehler_zahlen(ergebnis, fehler)]}
    if rechnung:
        a["rechnung"] = rechnung
    if einheit:
        a["einheit"] = einheit
    return a


# ── A1.1 Negative Zahlen: ordnen, vergleichen ─────────────

ZAHLENGERADE = ("Auf der Zahlengeraden liegt die größere Zahl immer weiter **rechts**. Bei negativen Zahlen heißt das: "
                "Je weiter weg von 0, desto **kleiner** – zum Beispiel ist -7 kleiner als -3.")


def vergleich(r, s):
    if s == 1:
        a, b = nz(r, -12, 12), nz(r, -12, -1)
    elif s == 2:
        a, b = nz(r, -20, -1), nz(r, -20, -1)
    elif s == 3:
        a, b = F(nz(r, -9, -1), 10), F(nz(r, -99, -1), 100)
    else:
        a, b = -F(r.randint(1, 7), 8), F(nz(r, -9, -1), 10)
    if a == b:
        return None
    dezimal = s == 3
    ta, tb = zt(a, dezimal), zt(b, dezimal and True)
    if s == 4:
        tb = zt(b, True)
    gross = max(a, b)
    return {"typ": "auswahl", "frage": f"Welche Zahl ist größer: `{ta}` oder `{tb}`?", "mathe": True,
            "optionen": [ta, tb], "richtig": [0 if gross == a else 1], "pruefung": {"art": "wert", "ziel": z(gross)},
            "erklaerung": ZAHLENGERADE + (" Brüche und Dezimalzahlen vergleichst du am besten, wenn du beide als "
                                          "Dezimalzahl schreibst." if s >= 3 else ""),
            "tipps": ["Stell dir die Zahlengerade vor: Welche Zahl liegt weiter rechts?"]}


def kleinste(r, s):
    if s <= 2:
        werte = list({nz(r, -15, 15) for _ in range(4)})
        dezimal = False
    else:
        werte = list({F(nz(r, -30, 30), 10) for _ in range(4)})
        dezimal = True
    if len(werte) < 4:
        return None
    opt = [zt(w, dezimal) for w in werte]
    k = min(werte)
    return {"typ": "auswahl", "frage": "Welche Zahl ist am **kleinsten**?", "mathe": True,
            "optionen": opt, "richtig": [werte.index(k)], "pruefung": {"art": "wert", "ziel": z(k)},
            "erklaerung": ZAHLENGERADE, "tipps": ["Die kleinste Zahl liegt auf der Zahlengeraden ganz links."]}


def temperatur(r, s):
    start = nz(r, -12, -1)
    aenderung = nz(r, 2, 15)
    waermer = r.random() < .6
    ende = start + aenderung if waermer else start - aenderung
    rechnung = f"{start} {'+' if waermer else '-'} {aenderung}"
    return zahl_aufgabe(
        f"Am Morgen hat es {start} °C. Bis zu Mittag wird es um {aenderung} Grad {'wärmer' if waermer else 'kälter'}. "
        "Wie viel Grad hat es zu Mittag?", ende, [f"{rechnung} = {ende}"],
        ["Wärmer heißt: auf dem Thermometer nach oben, also plus. Kälter heißt minus.",
         f"Rechne `{rechnung}`."],
        [(-ende, "Achte auf das Vorzeichen des Ergebnisses: Liegt es über oder unter 0?"),
         (start - aenderung if waermer else start + aenderung, "Wärmer heißt plus, kälter heißt minus.")],
        rechnung=rechnung, einheit="°C")


def abstand(r, s):
    a, b = nz(r, -15, -1), nz(r, 1, 15)
    if s >= 3:
        a, b = sorted([nz(r, -40, -1), nz(r, -40, 20)])
    if a == b:
        return None
    d = abs(b - a)
    return zahl_aufgabe(
        f"Wie weit liegen die Zahlen {a} und {b} auf der Zahlengeraden auseinander?", d,
        [f"{max(a, b)} - {kz(min(a, b))} = {d}"],
        ["Rechne: größere Zahl minus kleinere Zahl.", f"`{max(a, b)} - {kz(min(a, b))}` – minus minus ergibt plus."],
        [(abs(abs(b) - abs(a)), "Zähle die Schritte bis 0 und dann weiter – der Weg über die 0 gehört dazu.")],
        rechnung=f"{max(a, b)} - {kz(min(a, b))}")


def mitte(r, s):
    a, b = nz(r, -20, -1), nz(r, -10, 16)
    if (a + b) % 2 or a == b:
        return None
    m = F(a + b, 2)
    return zahl_aufgabe(
        f"Welche Zahl liegt auf der Zahlengeraden genau in der Mitte zwischen {a} und {b}?", m,
        [f"({a} + {b})/2 = {z(m)}"],
        ["Die Mitte ist der Durchschnitt: beide Zahlen addieren, dann durch 2.", f"`({a} + {b}) : 2`"],
        [(F(b - a, 2), "Das ist der halbe Abstand. Die Mitte bekommst du mit (a + b) : 2.")],
        rechnung=f"({a} + {b})/2")


def konto(r, s):
    start = -r.randint(5, 40) * 10
    ein, ab = r.randint(10, 60) * 10, r.randint(5, 40) * 10
    ende = start + ein - ab
    rechnung = f"{start} + {ein} - {ab}"
    return zahl_aufgabe(
        f"Ein Konto steht bei {start} €. Es werden {ein} € eingezahlt und danach {ab} € abgebucht. "
        "Wie ist der neue Kontostand?", ende, [f"{rechnung} = {ende}"],
        ["Ein Minus-Kontostand heißt: Schulden. Einzahlen ist plus, abbuchen ist minus.", f"Rechne `{rechnung}`."],
        [(-ende, "Achte auf das Vorzeichen: Ist das Konto am Ende im Plus oder im Minus?"),
         (-start + ein - ab, "Der Anfangsstand ist negativ – er steht mit Minus in der Rechnung.")],
        rechnung=rechnung, einheit="€")


def a1_1(r, s):
    w = r.random()
    if s == 1:
        return vergleich(r, s) if w < .5 else temperatur(r, s)
    if s == 2:
        return kleinste(r, s) if w < .35 else abstand(r, s) if w < .7 else temperatur(r, s)
    if s == 3:
        return vergleich(r, s) if w < .35 else mitte(r, s) if w < .7 else abstand(r, s)
    return vergleich(r, s) if w < .3 else kleinste(r, s) if w < .5 else konto(r, s) if w < .8 else mitte(r, s)


# ── A1.2 Plus und Minus ───────────────────────────────────

def summe(r, glieder, dezimal=False):
    """glieder: [(op, wert)]; erstes op ist '+'"""
    text, einfach, naiv = "", "", F(0)
    for i, (op, w) in enumerate(glieder):
        w = F(w)
        if i == 0:
            text = zt(w, dezimal)
            einfach = zt(w, dezimal)
            naiv = w
            continue
        text += f" {op} {kz(w, dezimal)}"
        plus = (op == "+") == (w >= 0)
        einfach += f" {'+' if plus else '-'} {zt(abs(w), dezimal)}"
        naiv += -abs(w) if op == "-" else w  # typischer Fehler: „minus minus“ bleibt minus
    ergebnis = sum((F(w) if op == "+" else -F(w)) for op, w in glieder)
    doppelt = any(F(w) < 0 for _, w in glieder[1:])
    weg = [" = ".join(dict.fromkeys([text, einfach, zt(ergebnis, dezimal)]))]
    tipps = ["Zwei Zeichen hintereinander: gleiche Zeichen ergeben **plus**, verschiedene ergeben **minus**.",
             f"Vereinfacht: `{einfach}`.",
             "Dann von links nach rechts rechnen. Stell dir die Zahlengerade vor: plus heißt nach rechts, minus nach links."]
    if not doppelt:
        tipps = ["Stell dir die Zahlengerade vor: plus heißt nach rechts, minus nach links.",
                 "Von links nach rechts rechnen."]
    fehler = [(naiv if doppelt else None, "Minus mal Minus ergibt Plus: `- (-4)` ist `+ 4`."),
              (-ergebnis, "Achte auf das Vorzeichen des Ergebnisses.")]
    return zahl_aufgabe(f"Berechne `{text}`.", ergebnis, weg, tipps, fehler, rechnung=text, dezimal=dezimal)


def a1_2(r, s):
    if s == 1:
        a, b = nz(r, -12, 12), nz(r, 1, 12)
        if a > 0 and r.random() < .7:
            a = -a
        op = r.choice("+-")
        if a > 0 and op == "+":
            return None
        return summe(r, [("+", a), (op, b)])
    if s == 2:
        a, b = nz(r, -15, 15), nz(r, -15, -1)
        return summe(r, [("+", a), (r.choice("+-"), b)])
    if s == 3:
        n = r.randint(3, 4)
        g = [("+", nz(r, -25, 25))] + [(r.choice("+-"), nz(r, -25, 25)) for _ in range(n - 1)]
        if not any(w < 0 for _, w in g[1:]):
            return None
        return summe(r, g)
    if r.random() < .5:
        g = [("+", F(nz(r, -60, 60), 4))] + [(r.choice("+-"), F(nz(r, -60, 60), 4)) for _ in range(2)]
        return summe(r, g, dezimal=True)
    g = [("+", F(nz(r, -5, 5), r.choice([2, 3, 4])))] + [(r.choice("+-"), F(nz(r, -5, 5), r.choice([2, 4, 6]))) for _ in range(2)]
    if not any(F(w) < 0 for _, w in g[1:]):
        return None
    return summe(r, g)


# ── A1.3 Mal und Durch ────────────────────────────────────

def a1_3(r, s):
    dezimal = False
    if s == 1:
        a, b = nz(r, -10, 10), nz(r, -10, 10)
        if a > 0 and b > 0:
            return None
        if r.random() < .5:
            text, erg = f"{kz(a)} · {kz(b)}", F(a * b)
        else:
            text, erg = f"{kz(a * b)} : {kz(b)}", F(a)
    elif s == 2:
        f = [nz(r, -6, 6) for _ in range(3)]
        if all(x > 0 for x in f):
            return None
        if r.random() < .5:
            text, erg = " · ".join(kz(x) for x in f), F(f[0] * f[1] * f[2])
        else:
            text, erg = f"{kz(f[0] * f[1])} : {kz(f[1])} · {kz(f[2])}", F(f[0] * f[2])
    elif s == 3:
        f = [nz(r, -9, 9) for _ in range(4)]
        if sum(x < 0 for x in f) < 2:
            return None
        if r.random() < .5:
            text, erg = " · ".join(kz(x) for x in f), F(f[0] * f[1] * f[2] * f[3])
        else:
            text, erg = f"{kz(f[0] * f[1])} : {kz(f[1])} · {kz(f[2])} : {kz(f[3])}", F(f[0] * f[2], f[3])
            if erg.denominator != 1:
                return None
    else:
        if r.random() < .5:
            dezimal = True
            a, b = F(nz(r, -40, 40), 10), F(nz(r, -40, 40), 10)
            if a > 0 and b > 0:
                return None
            text, erg = f"{kz(a, True)} · {kz(b, True)}", a * b
        else:
            a, b = F(nz(r, -7, 7), r.choice([2, 3, 4, 5])), F(nz(r, -7, 7), r.choice([2, 3, 4, 5]))
            if a.denominator == 1 or b.denominator == 1 or (a > 0 and b > 0):
                return None
            text, erg = f"{kz(a)} : {kz(b)}", a / b
    minus = text.count("(-")
    return zahl_aufgabe(
        f"Berechne `{text}`.", erg, [f"{text} = {zt(erg, dezimal)}"],
        ["Zuerst das Vorzeichen: gleiche Vorzeichen ergeben **plus**, verschiedene **minus**.",
         f"Hier stehen {minus} Minus. {'Gerade Anzahl → plus.' if minus % 2 == 0 else 'Ungerade Anzahl → minus.'}",
         "Dann rechnest du mit den Zahlen ohne Vorzeichen."],
        [(-erg, "Das Vorzeichen stimmt nicht: Zähl die Minus – gerade Anzahl ergibt plus, ungerade minus.")],
        rechnung=text, dezimal=dezimal)


# ── A1.4 Vorrangregeln ────────────────────────────────────

# (Vorlage, falsche Rechnung, Hinweis) – {a} … {d} werden mit Zahlen gefüllt
VORRANG = {
    1: [("{a} + {b} · {c}", "({a} + {b}) · {c}", "Punkt vor Strich: Zuerst wird multipliziert."),
        ("{a} - {b} · {c}", "({a} - {b}) · {c}", "Punkt vor Strich: Zuerst wird multipliziert."),
        ("({a} + {b}) · {c}", "{a} + {b} · {c}", "Die Klammer kommt zuerst."),
        ("{a} · {b} + {c} · {d}", "({a} · {b} + {c}) · {d}", "Punkt vor Strich: Beide Produkte zuerst ausrechnen."),
        ("{p} : {b} + {c}", "{p} : ({b} + {c})", "Punkt vor Strich: Zuerst wird dividiert.")],
    2: [("{a} - {b} + {c}", "{a} - ({b} + {c})", "Plus und Minus rechnest du von links nach rechts."),
        ("{p} : {b} · {c}", "{p} : ({b} · {c})", "Mal und Durch rechnest du von links nach rechts."),
        ("{c} · {a}²", "({c} · {a})²", "Hochzahl vor Punkt: Zuerst wird quadriert."),
        ("{a}² + {b} · {c}", "({a}² + {b}) · {c}", "Erst Hochzahl, dann Punkt, dann Strich."),
        ("{d} - ({a} - {b}) · {c}", "({d} - {a} - {b}) · {c}", "Zuerst die Klammer, dann Punkt vor Strich.")],
    3: [("-{a}² + {b}", "(-{a})² + {b}", "`-3²` heißt `-(3²) = -9`. Nur bei `(-3)²` wird die -3 quadriert."),
        ("(-{a})² - {b}", "-{a}² - {b}", "`(-3)² = (-3) · (-3) = +9`."),
        ("{c} · ({a} - {d})² - {b}", "({c} · ({a} - {d}))² - {b}", "Hochzahl vor Punkt: Zuerst die Klammer, dann quadrieren, dann mal."),
        ("({p} - {b} · {c}) : {a}", "({p} - {b}) · {c} : {a}", "Auch in der Klammer gilt Punkt vor Strich."),
        ("{a} - {b} · ({c} - {d})", "({a} - {b}) · ({c} - {d})", "Punkt vor Strich: Zuerst `{b} · (…)`.")],
    4: [("{p} : ({a} + {b}) · {c} - 2³", "{p} : (({a} + {b}) · {c}) - 2³", "Mal und Durch von links nach rechts – und 2³ = 8."),
        ("(-{a})³ + {b} · ({c} - 2 · {d})", "-{a}³ + ({b} · {c} - 2) · {d}", "Erst die Klammer (innen Punkt vor Strich), dann Hochzahl, dann Punkt vor Strich."),
        ("-{a}² - (-{a})²", "(-{a})² - (-{a})²", "`-a²` und `(-a)²` sind verschieden: Das erste ist negativ, das zweite positiv."),
        ("{c} - {b} · ({d} - {a})² : {a}", "({c} - {b}) · ({d} - {a})² : {a}", "Punkt vor Strich – und Hochzahl vor Punkt."),
        ("({a} - {p}) : {b} - {c} · (-{d})", "({a} - {p}) : ({b} - {c}) · (-{d})", "Punkt vor Strich: zuerst teilen und multiplizieren.")],
}


def a1_4(r, s):
    vorlage, falsch, hinweis = r.choice(VORRANG[s])
    werte = dict(zip("abcd", r.sample(range(2, 10), 4)))
    werte["p"] = werte["b"] * r.randint(2, 9)
    text = vorlage.format(**werte)
    try:
        erg = wert(text)
        f = wert(falsch.format(**werte))
    except ZeroDivisionError:
        return None
    if erg.denominator != 1 or abs(erg) > 400:
        return None
    return zahl_aufgabe(
        f"Berechne `{text}`.", erg, [f"{text} = {z(erg)}"],
        ["Die Reihenfolge: **Klammer** vor **Hochzahl** vor **Punkt** (· :) vor **Strich** (+ −).",
         "Gleichrangiges rechnest du von links nach rechts.", hinweis.format(**werte)],
        [(f, hinweis.format(**werte))], rechnung=text)


# ── A1.5 Zahlenmengen ─────────────────────────────────────

MENGEN = ["ℕ", "ℤ", "ℚ", "ℝ", "ℂ"]
MENGEN_ZAHLEN = {
    1: ["5", "0", "-3", "1/2", "-7", "12", "0,25", "-1", "100", "3/4"],
    2: ["-2/3", "0,75", "√2", "π", "-0,5", "√3", "2,5", "-12", "√5", "7/8"],
    3: ["√9", "-√16", "6/3", "-8/4", "√(1/4)", "√8", "√25", "-√2", "10/5", "√0,09"],
    4: ["√(-4)", "√(-1)", "(√2)²", "√2·√8", "1/√4", "π - 3", "√(-9)", "√12 : √3", "-√(1/9)", "√2 + 1"],
}
MENGEN_ERK = {
    0: "Die Zahl ist eine natürliche Zahl (0, 1, 2, 3, …). Damit gehört sie zu ℕ – und automatisch auch zu ℤ, ℚ, ℝ und ℂ.",
    1: "Die Zahl ist eine negative ganze Zahl. Sie gehört nicht zu ℕ, aber zu ℤ (…, -2, -1, 0, 1, 2, …).",
    2: "Die Zahl lässt sich als Bruch zweier ganzer Zahlen schreiben, ist aber nicht ganz. Kleinste Menge: ℚ.",
    3: "Die Zahl lässt sich **nicht** als Bruch schreiben (unendlich viele Nachkommastellen ohne Muster, z. B. √2 oder π). "
       "Kleinste Menge: ℝ.",
    4: "Die Wurzel aus einer negativen Zahl gibt es in ℝ nicht. Solche Zahlen gehören zu den komplexen Zahlen ℂ.",
}


def a1_5(r, s):
    zahl = r.choice(MENGEN_ZAHLEN[s])
    import sympy
    v = sympy.nsimplify(notation.ausdruck(zahl))
    stufe = 0 if v.is_integer and v >= 0 else 1 if v.is_integer else 2 if v.is_rational else 3 if v.is_real else 4
    zusatz = ""
    if s >= 3 and stufe <= 2 and ("√" in zahl or "/" in zahl):
        zusatz = f" Hier hilft Ausrechnen: `{zahl} = {z(F(str(v)))}`."
    return {"typ": "auswahl", "frage": f"Zu welcher **kleinsten** Zahlenmenge gehört `{zahl}`?",
            "optionen": MENGEN, "richtig": [stufe], "pruefung": {"art": "zahlenmenge", "zahl": zahl},
            "erklaerung": MENGEN_ERK[stufe] + zusatz,
            "tipps": ["ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ ⊂ ℂ: Jede Menge enthält die vorige. Gesucht ist die erste, in der die Zahl vorkommt.",
                      "Rechne die Zahl zuerst aus, wenn es geht – manche Wurzeln oder Brüche sind in Wahrheit ganze Zahlen."]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261018)
    for lid, fn, n in [("A1.1", a1_1, 10), ("A1.2", a1_2, 10), ("A1.3", a1_3, 10), ("A1.4", a1_4, 10), ("A1.5", a1_5, 7)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "a1.py")


if __name__ == "__main__":
    main()
