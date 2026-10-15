"""
Generator für Kapitel B5 (Quadratische Gleichungen). Einmal laufen lassen:

    python tools/generatoren/b5.py

Typ „quadratisch“: gleichung, loesung als „3; -2“, „√7; -√7“ oder „keine“.
"""

import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import erzeuge, nz, schreibe, z  # noqa: E402


def poly(a, b, c):
    """a·x² + b·x + c als Text"""
    aus = ""
    for k, v in ((F(a), "x²"), (F(b), "x"), (F(c), "")):
        if k == 0:
            continue
        betrag = abs(k)
        t = v if betrag == 1 and v else (f"{z(betrag)}{v}" if betrag.denominator == 1 else f"{z(betrag)}·{v}" if v else z(betrag))
        aus += (("-" if k < 0 else "") + t) if not aus else f" {'-' if k < 0 else '+'} {t}"
    return aus or "0"


def wurzel(q):
    """√13 bzw. √(13/4) – Brüche unter der Wurzel in Klammern"""
    q = F(q)
    return f"√{z(q)}" if q.denominator == 1 else f"√({z(q)})"


def kl(q):
    """Negative Zahlen und Brüche in Klammern (vor ² und in Produkten)"""
    q = F(q)
    return f"({z(q)})" if q < 0 or q.denominator != 1 else z(q)


def menge(*werte):
    """Lösungsmenge als Text, absteigend sortiert, ohne Doppelte"""
    ws = sorted({F(w) for w in werte}, reverse=True)
    return "; ".join(z(w) for w in ws)


def oder(*werte):
    ws = sorted({F(w) for w in werte}, reverse=True)
    return " oder ".join(f"x = {z(w)}" for w in ws)


def quadratisch(gleichung, loesung, weg, tipps, fehler=(), frage=None, erklaerung=None):
    a = {"typ": "quadratisch"}
    if frage:
        a["frage"] = frage
    a.update({"gleichung": gleichung, "loesung": loesung, "weg": [gleichung] + list(weg), "tipps": tipps,
              "fehler": [{"antwort": an, "hinweis": h} for an, h in dict(reversed([(an, h) for an, h in fehler if an and an != loesung])).items()][::-1]})
    if erklaerung:
        a["erklaerung"] = erklaerung
    return a


WURZEL_TIPPS = ["Bring x² allein auf eine Seite.", "Dann die Wurzel ziehen – und **beide** Lösungen notieren: plus und minus!",
                "Steht rechts eine negative Zahl, gibt es keine reelle Lösung: Ein Quadrat ist nie negativ."]


# ── B5.1 Reinquadratisch ──────────────────────────────────

def b5_1(r, s):
    if s == 1:
        n = r.randint(2, 12)
        if r.random() < .5:
            return quadratisch(f"x² = {n * n}", menge(n, -n), [f"{oder(n, -n)} | Wurzel: plus und minus"], WURZEL_TIPPS,
                               [(f"x = {z(F(n * n, 2))}", "Die Wurzel ist nicht „durch 2“: Gesucht ist die Zahl, die mal sich selbst " + str(n * n) + " ergibt.")])
        return quadratisch(f"x² - {n * n} = 0", menge(n, -n), [f"x² = {n * n} | +{n * n}", f"{oder(n, -n)} | Wurzel"], WURZEL_TIPPS)
    if s == 2:
        w = r.random()
        if w < .35:
            a, n = r.randint(2, 5), r.randint(2, 8)
            return quadratisch(f"{a}x² = {a * n * n}", menge(n, -n), [f"x² = {n * n} | :{a}", f"{oder(n, -n)} | Wurzel"], WURZEL_TIPPS)
        if w < .7:
            k = r.choice([2, 3, 5, 6, 7, 10, 11, 13])
            return quadratisch(f"x² - {k} = 0", f"√{k}; -√{k}", [f"x² = {k} | +{k}", f"x = ±√{k} | Wurzel"], WURZEL_TIPPS,
                               [(f"x = {z(F(k, 2))}", "Die Wurzel ist nicht „durch 2“.")])
        k = r.randint(1, 20)
        return quadratisch(f"x² + {k} = 0", "keine", [f"x² = -{k} | −{k}"], WURZEL_TIPPS,
                           [(f"√{k}; -√{k}", f"Prüf: `(√{k})² + {k}` ist nicht 0. x² ist nie negativ – hier gibt es keine reelle Lösung.")],
                           erklaerung="Ein Quadrat ist nie negativ. `x² = -" + str(k) + "` hat darum keine reelle Lösung.")
    if s == 3:
        w = r.random()
        if w < .5:
            p, q = r.randint(1, 7), r.choice([2, 3, 4, 5])
            if math.gcd(p, q) != 1:
                return None
            return quadratisch(f"{q * q}x² - {p * p} = 0", menge(F(p, q), F(-p, q)),
                               [f"{q * q}x² = {p * p} | +{p * p}", f"x² = {z(F(p * p, q * q))} | :{q * q}", f"{oder(F(p, q), F(-p, q))} | Wurzel"],
                               WURZEL_TIPPS)
        n = r.randint(2, 7)
        c = r.randint(1, 9)
        return quadratisch(f"2x² - {c + n * n} = x² - {c}", menge(n, -n), [f"x² - {c + n * n} = -{c} | −x²", f"x² = {n * n} | +{c + n * n}",
                                                                      f"{oder(n, -n)} | Wurzel"], WURZEL_TIPPS)
    w = r.random()
    m = nz(r, -5, 5)
    if w < .4:
        n = r.randint(1, 7)
        g = f"(x {'-' if m > 0 else '+'} {abs(m)})² = {n * n}"
        return quadratisch(g, menge(m + n, m - n),
                           [f"x {'-' if m > 0 else '+'} {abs(m)} = {n} oder x {'-' if m > 0 else '+'} {abs(m)} = -{n} | Wurzel: plus und minus",
                            f"{oder(m + n, m - n)}"],
                           ["Du musst nicht ausmultiplizieren! Zieh gleich die Wurzel aus beiden Seiten.",
                            "Dann zwei einfache Gleichungen: Klammer = +Wurzel oder Klammer = −Wurzel."],
                           [(f"x = {z(m + n)}", "Das ist nur eine Lösung – die Klammer kann auch −" + str(n) + " sein.")])
    if w < .7:
        k = r.choice([2, 3, 5, 7])
        g = f"(x {'-' if m > 0 else '+'} {abs(m)})² = {k}"
        return quadratisch(g, f"{m} + √{k}; {m} - √{k}", [f"x {'-' if m > 0 else '+'} {abs(m)} = ±√{k} | Wurzel", f"x = {m} ± √{k}"],
                           ["Zieh gleich die Wurzel aus beiden Seiten: plus und minus.", f"Dann noch {'+' if m > 0 else '−'}{abs(m)} auf beiden Seiten."])
    k = r.randint(1, 9)
    g = f"(x {'-' if m > 0 else '+'} {abs(m)})² + {k} = 0"
    return quadratisch(g, "keine", [f"(x {'-' if m > 0 else '+'} {abs(m)})² = -{k} | −{k}"],
                       ["Bring die Klammer allein auf eine Seite.", "Kann ein Quadrat negativ sein?"],
                       erklaerung="Ein Quadrat ist nie negativ – keine reelle Lösung.")


# ── B5.2 Herausheben und Produkt-Null-Satz ────────────────

PNS = "**Produkt-Null-Satz:** Ein Produkt ist genau dann 0, wenn (mindestens) ein Faktor 0 ist. Jeder Faktor = 0 setzen."


def b5_2(r, s):
    if s == 1:
        a, b = nz(r, -9, 9), nz(r, -9, 9)
        if a == b:
            return None
        if r.random() < .4:
            g = f"x(x {'-' if a > 0 else '+'} {abs(a)}) = 0"
            return quadratisch(g, menge(0, a), [f"x = 0 oder x {'-' if a > 0 else '+'} {abs(a)} = 0 | Produkt-Null-Satz", oder(0, a)],
                               [PNS, "Der erste Faktor ist x – also ist x = 0 eine Lösung!"],
                               [(f"x = {a}", "Der Faktor x selbst kann auch 0 sein: x = 0 ist ebenfalls eine Lösung.")])
        g = f"(x {'-' if a > 0 else '+'} {abs(a)})(x {'-' if b > 0 else '+'} {abs(b)}) = 0"
        return quadratisch(g, menge(a, b), [f"x {'-' if a > 0 else '+'} {abs(a)} = 0 oder x {'-' if b > 0 else '+'} {abs(b)} = 0 | Produkt-Null-Satz",
                                            oder(a, b)],
                           [PNS, "Jede Klammer = 0 setzen und lösen. Achtung Vorzeichen: Aus x − 3 = 0 wird x = 3."],
                           [(menge(-a, -b), "Vorzeichen! Aus `x - 3 = 0` folgt `x = 3`, nicht −3.")])
    if s == 2:
        b, c = nz(r, 1, 6), nz(r, -9, 9)
        if c % b and r.random() < .6:
            return None
        x2 = F(-c, b)
        g = poly(b, c, 0) + " = 0"
        return quadratisch(g, menge(0, x2), [f"x({poly(0, b, c)}) = 0 | x herausheben", oder(0, x2)],
                           ["Heb x heraus – dann hast du ein Produkt.", PNS, "Vergiss die Lösung x = 0 nicht!"],
                           [(f"x = {z(x2)}", "Du hast durch x dividiert – dabei geht die Lösung x = 0 verloren. Heb x lieber heraus.")])
    if s == 3:
        if r.random() < .5:
            p, q, c = nz(r, 1, 3), nz(r, -7, 7), nz(r, -6, 6)
            g = f"({poly(0, p, q)})(x {'-' if c > 0 else '+'} {abs(c)}) = 0"
            return quadratisch(g, menge(F(-q, p), c), [f"{poly(0, p, q)} = 0 oder x {'-' if c > 0 else '+'} {abs(c)} = 0 | Produkt-Null-Satz",
                                                         oder(F(-q, p), c)],
                               [PNS, "Die erste Klammer ist eine kleine lineare Gleichung – löse sie wie gewohnt."])
        k = nz(r, 2, 9)
        g = f"x² = {k}x"
        return quadratisch(g, menge(0, k), [f"x² - {k}x = 0 | −{k}x", f"x(x - {k}) = 0 | herausheben", oder(0, k)],
                           ["Bring alles auf eine Seite, sodass rechts 0 steht.", "Heb x heraus.", "Nicht durch x dividieren – sonst verlierst du x = 0!"],
                           [(f"x = {k}", "Durch x dividieren ist gefährlich: Dabei geht die Lösung x = 0 verloren.")])
    m, k = nz(r, -5, 5), nz(r, 2, 6, ())
    if r.random() < .5:
        g = f"(x {'-' if m > 0 else '+'} {abs(m)})² - {k}(x {'-' if m > 0 else '+'} {abs(m)}) = 0"
        return quadratisch(g, menge(m, m + k), [f"(x {'-' if m > 0 else '+'} {abs(m)})(x {'-' if m > 0 else '+'} {abs(m)} - {k}) = 0 | Klammer herausheben",
                                                oder(m, m + k)],
                           ["Die Klammer kommt zweimal vor – heb sie als Ganzes heraus.", PNS])
    a = nz(r, 2, 5)
    g = f"{a}x({k} - x) = 0"
    return quadratisch(g, menge(0, k), [f"x = 0 oder {k} - x = 0 | Produkt-Null-Satz", oder(0, k)],
                       [PNS, f"Der Faktor {a} kann nie 0 sein – bleiben x und ({k} − x)."])


# ── B5.3 Kleine Lösungsformel ─────────────────────────────

FORMEL_KLEIN = "Kleine Lösungsformel für `x² + px + q = 0`: `x = -p/2 ± √((p/2)² - q)`."


def klein(p, q, faktor=1, umgestellt=None):
    p, q = F(p), F(q)
    h = -p / 2
    D = h * h - q
    if D < 0:
        return None
    wd = F(math.isqrt(D.numerator), math.isqrt(D.denominator)) if math.isqrt(D.numerator) ** 2 == D.numerator and \
        math.isqrt(D.denominator) ** 2 == D.denominator else None
    weg = []
    if umgestellt:
        weg.append(umgestellt)
    if faktor != 1:
        weg.append(f"{poly(1, p, q)} = 0 | :{faktor}")
    weg.append(f"x = {z(h)} ± √({kl(h)}² - {kl(q)}) | Formel mit p = {z(p)}, q = {z(q)}")
    weg.append(f"x = {z(h)} ± {wurzel(D)}")
    if wd is not None:
        if wd != 0:
            weg.append(f"x = {z(h)} ± {z(wd)}")
        weg.append(oder(h + wd, h - wd))
        loesung = menge(h + wd, h - wd)
    else:
        loesung = f"{z(h)} + {wurzel(D)}; {z(h)} - {wurzel(D)}"
    return weg, loesung, h, wd


def b5_3(r, s):
    if s <= 2:
        x1, x2 = (r.randint(1, 9), r.randint(1, 9)) if s == 1 else (nz(r, -9, 9), nz(r, -9, 9))
        p, q = -(x1 + x2), x1 * x2
        weg, loesung, h, wd = klein(p, q)
        g = poly(1, p, q) + " = 0"
        return quadratisch(g, loesung, weg, [FORMEL_KLEIN, f"Hier ist p = {p}, q = {q}. Achtung auf die Vorzeichen!",
                                              "Unter der Wurzel zuerst ausrechnen, dann plus und minus."],
                           [(menge(-x1, -x2), "Vorzeichen von p: In der Formel steht **−p/2**. Bei p = " + str(p) + " ist −p/2 = " + z(h) + ".")])
    if s == 3:
        p, q = nz(r, -10, 10), nz(r, -12, 12)
        if (F(p, 2)) ** 2 - q <= 0:
            return None
        erg = klein(p, q)
        if not erg or erg[3] is not None:
            return None
        weg, loesung, h, wd = erg
        return quadratisch(poly(1, p, q) + " = 0", loesung, weg,
                           [FORMEL_KLEIN, "Geht die Wurzel nicht auf, lässt du sie stehen: z. B. `x = 3 ± √2`."])
    x1, x2 = nz(r, -6, 6), nz(r, -6, 6)
    a = r.choice([2, 3, 4, -1, -2])
    p, q = -(x1 + x2), x1 * x2
    if r.random() < .5:
        g = poly(a, a * p, a * q) + " = 0"
        weg, loesung, h, wd = klein(p, q, faktor=a)
        tipp = f"Die Formel braucht vor x² eine 1. Dividiere zuerst die ganze Gleichung durch {a}."
    else:
        rechts = poly(0, -p, -q)
        g = f"x² = {rechts}"
        weg, loesung, h, wd = klein(p, q, umgestellt=f"{poly(1, p, q)} = 0 | alles nach links")
        tipp = "Bring zuerst alles auf eine Seite, sodass rechts 0 steht."
    return quadratisch(g, loesung, weg, [tipp, FORMEL_KLEIN, "p und q mit Vorzeichen ablesen."],
                       [(menge(-x1, -x2), "Vorzeichen von p: In der Formel steht −p/2.")])


# ── B5.4 Große Lösungsformel ──────────────────────────────

FORMEL_GROSS = "Große Lösungsformel für `ax² + bx + c = 0`: `x = (-b ± √(b² - 4ac))/(2a)`."


def b5_4(r, s):
    if s <= 2:
        a = r.randint(2, 4) if s == 1 else nz(r, -4, 5, (0, 1))
        x1, x2 = nz(r, -6, 6), F(nz(r, -9, 9), a)
    elif s == 3:
        a = nz(r, 2, 6)
        x1, x2 = F(nz(r, -9, 9), a), F(nz(r, -9, 9), r.choice([1, 2, 3]))
    else:
        a = nz(r, -6, 6, (0, 1, -1))
        x1, x2 = F(nz(r, -7, 7), 2), F(nz(r, -7, 7), 3)
    b, c = -a * (x1 + x2), a * x1 * x2
    if F(b).denominator != 1 or F(c).denominator != 1 or x1 == x2:
        return None
    D = b * b - 4 * a * c
    w = math.isqrt(int(D))
    g = poly(a, b, c) + " = 0"
    weg = [f"x = ({z(-b)} ± √({kl(b)}² - 4·{kl(a)}·{kl(c)}))/(2·{kl(a)}) | a = {a}, b = {z(b)}, c = {z(c)}",
           f"x = ({z(-b)} ± √{z(D)})/{kl(2 * a)}", f"x = ({z(-b)} ± {w})/{kl(2 * a)}", oder(x1, x2)]
    return quadratisch(g, menge(x1, x2), weg, [FORMEL_GROSS, f"Hier: a = {a}, b = {z(b)}, c = {z(c)}. Negative Zahlen in Klammern einsetzen!",
                                                  f"Unter der Wurzel: `b² - 4ac = {z(D)}`."],
                       [(menge(-x1, -x2), "Vorzeichen: Vorne steht **−b**."),
                        (menge((-b + w) / 2, (-b - w) / 2) if a != 1 else None, "Der Nenner ist **2a**, nicht nur 2.")]
                       if a != 1 else [(menge(-x1, -x2), "Vorzeichen: Vorne steht **−b**.")])


# ── B5.5 Diskriminante, B5.6 geometrisch ──────────────────

ANZAHL_Q = ["zwei reelle Lösungen", "genau eine reelle Lösung", "keine reelle Lösung"]
PARABEL = ["Sie schneidet die x-Achse in zwei Punkten.", "Sie berührt die x-Achse in genau einem Punkt.",
           "Sie hat keinen Punkt mit der x-Achse gemeinsam."]
ERK_Q = {0: "Die Diskriminante ist **positiv** – unter der Wurzel steht eine positive Zahl, plus und minus geben zwei Lösungen.",
         1: "Die Diskriminante ist **0** – plus und minus 0 ergibt dieselbe Zahl: genau eine Lösung (Doppellösung).",
         2: "Die Diskriminante ist **negativ** – die Wurzel aus einer negativen Zahl gibt es in ℝ nicht: keine reelle Lösung."}


def zufallsquadrat(r, fall, s):
    a = 1 if s <= 2 else nz(r, -3, 3)
    m = nz(r, -6, 6)
    if fall == 0:
        x1, x2 = m, m + nz(r, 1, 6)
        b, c = -a * (x1 + x2), a * x1 * x2
    elif fall == 1:
        b, c = -2 * a * m, a * m * m
    else:
        k = nz(r, 1, 9)
        b, c = -2 * a * m, a * m * m + a * k
    return a, b, c


def b5_5(r, s):
    fall = r.choice([0, 1, 2])
    a, b, c = zufallsquadrat(r, fall, s)
    g = poly(a, b, c) + " = 0"
    if s >= 3 and r.random() < .5:
        if fall == 2:
            return quadratisch(g, "keine", [], ["Berechne zuerst die Diskriminante `D = b² - 4ac` (bzw. `(p/2)² - q`).",
                                                "Ist sie negativ, gibt es keine reelle Lösung – schreib „keine“."],
                               erklaerung=ERK_Q[2])
        return None
    D = b * b - 4 * a * c
    return {"typ": "auswahl", "frage": f"Wie viele reelle Lösungen hat `{g}`?", "optionen": ANZAHL_Q, "richtig": [fall],
            "pruefung": {"art": "q_anzahl", "gleichung": g},
            "erklaerung": f"Die Diskriminante ist `b² - 4ac = {z(D)}`. " + ERK_Q[fall],
            "tipps": ["Berechne nur den Teil unter der Wurzel: die Diskriminante `D = b² - 4ac`.",
                      f"Hier: a = {a}, b = {b}, c = {c}."]}


def b5_6(r, s):
    fall = r.choice([0, 1, 2])
    a, b, c = zufallsquadrat(r, fall, s)
    f = poly(a, b, c)
    if fall == 0 and r.random() < .6:
        g = f + " = 0"
        x_werte = [w for w in [F(x) for x in range(-20, 21)] if a * w * w + b * w + c == 0]
        if len(x_werte) != 2:
            return None
        return quadratisch(g, menge(*x_werte), [oder(*x_werte)],
                           ["Auf der x-Achse ist y = 0. Setz also den Term gleich 0.", "Löse die quadratische Gleichung, z. B. mit der Lösungsformel."],
                           frage=f"Wo schneidet die Parabel `y = {f}` die x-Achse? Gib die x-Werte (Nullstellen) an.")
    return {"typ": "auswahl", "frage": f"Was gilt für die Parabel `y = {f}`?", "optionen": PARABEL, "richtig": [fall],
            "pruefung": {"art": "q_anzahl", "gleichung": f"{f} = 0"},
            "erklaerung": "Die Schnittpunkte mit der x-Achse sind die Lösungen von `" + f + " = 0`. " + ERK_Q[fall],
            "tipps": ["Auf der x-Achse ist y = 0. Wie viele Lösungen hat `" + f + " = 0`?", "Die Diskriminante verrät es."]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261024)
    for lid, fn, n in [("B5.1", b5_1, 8), ("B5.2", b5_2, 8), ("B5.3", b5_3, 8), ("B5.4", b5_4, 8), ("B5.5", b5_5, 8), ("B5.6", b5_6, 6)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "b5.py")


if __name__ == "__main__":
    main()
