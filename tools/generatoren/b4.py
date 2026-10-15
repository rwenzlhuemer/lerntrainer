"""
Generator für Kapitel B4 (Lineare Gleichungssysteme mit 2 Variablen). Einmal laufen lassen:

    python tools/generatoren/b4.py

Typ „lgs“: gleichungen [I, II], loesung {x, y} oder "keine"/"unendlich".
Lösungswege werden automatisch erzeugt; der Build prüft jede Zeile mit der Lösung (sympy).
"""

import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import dez, endlich, erzeuge, nz, schreibe, z  # noqa: E402


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 100 else z(q)


def glied(k, v, erstes):
    k = F(k)
    if k == 0:
        return ""
    betrag = abs(k)
    t = v if betrag == 1 and v else f"{zt(betrag)}{v}"
    if erstes:
        return ("-" if k < 0 else "") + t
    return f" {'-' if k < 0 else '+'} {t}"


def summe(*paare):
    """summe((2, 'x'), (-1, 'y'), (3, '')) → '2x - y + 3'"""
    aus = ""
    for k, v in paare:
        if F(k) != 0:
            aus += glied(k, v, not aus)
    return aus or "0"


def gl(a, b, c):
    """a·x + b·y = c"""
    return f"{summe((a, 'x'), (b, 'y'))} = {zt(c)}"



def fehlerpaare(x0, y0):
    aus = []
    if x0 != y0:
        aus.append({"x": zt(y0), "y": zt(x0), "hinweis": "x und y vertauscht? Prüf, welche Zahl zu welcher Variablen gehört."})
    if y0 != 0:
        aus.append({"x": zt(x0), "y": zt(-y0), "hinweis": "x stimmt, aber bei y ist ein Vorzeichenfehler passiert. Setz x noch einmal sorgfältig ein."})
    return aus


def lgs(gleichungen, x0, y0, weg, tipps, frage=None):
    a = {"typ": "lgs"}
    if frage:
        a["frage"] = frage
    a.update({"gleichungen": gleichungen, "loesung": {"x": zt(x0), "y": zt(y0)}, "weg": weg, "tipps": tipps,
              "fehler": fehlerpaare(x0, y0)})
    return a


# ── Lösungsverfahren mit Lösungsweg ───────────────────────

def einsetzen(r, x0, y0, k, a, b):
    """I: y = k·x + d, II: a·x + b·y = c"""
    d = y0 - k * x0
    c = a * x0 + b * y0
    I = f"y = {summe((k, 'x'), (d, ''))}"
    II = gl(a, b, c)
    kx, cx = a + b * k, c - b * d
    if kx == 0:
        return None
    faktor = zt(abs(b)) if abs(b) != 1 else ""
    weg = [f"{summe((a, 'x'))} {'+' if b > 0 else '-'} {faktor}({summe((k, 'x'), (d, ''))}) = {zt(c)} | I in II einsetzen",
           f"{summe((kx, 'x'), (b * d, ''))} = {zt(c)} | ausmultipliziert, zusammengefasst"]
    if b * d != 0:
        weg.append(f"{summe((kx, 'x'))} = {zt(cx)} | {'−' if b * d > 0 else '+'}{zt(abs(b * d))}")
    if kx != 1:
        weg.append(f"x = {zt(x0)} | :{zt(kx) if kx > 0 else '(' + zt(kx) + ')'}")
    weg.append(f"y = {zt(y0)} | x in I einsetzen")
    return [I, II], weg

def gleichsetzen(r, x0, y0, k1, k2):
    d1, d2 = y0 - k1 * x0, y0 - k2 * x0
    I, II = f"y = {summe((k1, 'x'), (d1, ''))}", f"y = {summe((k2, 'x'), (d2, ''))}"
    kx, cx = k1 - k2, d2 - d1
    weg = [f"{summe((k1, 'x'), (d1, ''))} = {summe((k2, 'x'), (d2, ''))} | gleichsetzen",
           f"{summe((kx, 'x'))} = {zt(cx)} | x-Glieder links, Zahlen rechts"]
    if kx != 1:
        weg.append(f"x = {zt(x0)} | :{zt(kx) if kx > 0 else '(' + zt(kx) + ')'}")
    weg.append(f"y = {zt(y0)} | x in I einsetzen")
    return [I, II], weg


def addition(r, x0, y0, a1, b1, a2, b2):
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0
    I, II = gl(a1, b1, c1), gl(a2, b2, c2)
    g = math.lcm(abs(int(b1)), abs(int(b2))) if F(b1).denominator == F(b2).denominator == 1 else abs(b1 * b2)
    m1, m2 = F(g) / b1, -F(g) / b2
    weg = []
    if m1 != 1:
        weg.append(f"{gl(a1 * m1, b1 * m1, c1 * m1)} | I · {zt(m1) if m1 > 0 else '(' + zt(m1) + ')'}")
    if m2 != 1:
        weg.append(f"{gl(a2 * m2, b2 * m2, c2 * m2)} | II · {zt(m2) if m2 > 0 else '(' + zt(m2) + ')'}")
    kx, cx = a1 * m1 + a2 * m2, c1 * m1 + c2 * m2
    weg.append(f"{summe((kx, 'x'))} = {zt(cx)} | addiert – y fällt weg")
    if kx != 1:
        weg.append(f"x = {zt(x0)} | :{zt(kx) if kx > 0 else '(' + zt(kx) + ')'}")
    weg.append(f"y = {zt(y0)} | x in I einsetzen")
    return [I, II], weg


TIPPS_EINSETZEN = ["Eine Gleichung ist schon nach y aufgelöst. Setz den ganzen Term für y in die andere Gleichung ein – mit Klammer!",
                   "Jetzt hast du eine Gleichung nur mit x. Löse sie.",
                   "Setz x in die erste Gleichung ein, dann hast du y. Antwort z. B.: x = 3, y = 1."]
TIPPS_GLEICH = ["Beide Gleichungen sagen „y = …“. Also müssen die rechten Seiten gleich sein: gleichsetzen!",
                "Löse die neue Gleichung nach x.", "Setz x in eine der Gleichungen ein, dann hast du y."]
TIPPS_ADD = ["Multipliziere die Gleichungen so, dass vor y Zahlen mit gleichem Betrag, aber verschiedenem Vorzeichen stehen.",
             "Addiere dann die beiden Gleichungen: y fällt weg.",
             "Löse nach x und setz x in eine Gleichung ein, um y zu bekommen."]


def b4_1(r, s):
    x0, y0 = nz(r, -6, 6, ()), nz(r, -6, 6, ())
    if s == 1:
        x0, y0 = r.randint(1, 6), r.randint(1, 9)
        k = r.randint(2, 4)
        y0 = k * x0
        erg = einsetzen(r, x0, y0, k, r.randint(1, 3), 1)
        tipps = TIPPS_EINSETZEN
    elif s == 2:
        erg = einsetzen(r, x0, y0, nz(r, -4, 4), nz(r, -4, 5), nz(r, -3, 3))
        tipps = TIPPS_EINSETZEN
    elif s == 3:
        k1, k2 = nz(r, -4, 4), nz(r, -4, 4)
        if k1 == k2:
            return None
        erg = gleichsetzen(r, x0, y0, k1, k2)
        tipps = TIPPS_GLEICH
    else:
        if r.random() < .5:
            x0, y0 = F(nz(r, -9, 9), 2), F(nz(r, -6, 6))
            erg = einsetzen(r, x0, y0, nz(r, -3, 3), nz(r, 2, 5), nz(r, -3, 3))
            tipps = TIPPS_EINSETZEN
        else:
            k1, k2 = F(nz(r, -5, 5), 2), F(nz(r, -4, 4))
            if k1 == k2:
                return None
            erg = gleichsetzen(r, x0, y0, k1, k2)
            tipps = TIPPS_GLEICH
    if not erg:
        return None
    (I, II), weg = erg
    return lgs([I, II], x0, y0, weg, tipps)


def b4_2(r, s):
    x0, y0 = nz(r, -6, 6, ()), nz(r, -6, 6, ())
    if s == 1:
        b = r.randint(1, 3)
        erg = addition(r, x0, y0, r.randint(1, 4), b, r.randint(1, 4), -b)
    elif s == 2:
        b1 = r.randint(1, 3)
        erg = addition(r, x0, y0, nz(r, -4, 4), b1, nz(r, -4, 4), -b1 * r.randint(2, 3))
    elif s == 3:
        erg = addition(r, x0, y0, nz(r, -5, 5), nz(r, 2, 5), nz(r, -5, 5), nz(r, -5, -2))
    else:
        x0, y0 = F(nz(r, -9, 9), 2), F(nz(r, -9, 9), 2)
        erg = addition(r, x0, y0, nz(r, 2, 6), nz(r, -5, 5), nz(r, -6, 6), nz(r, 2, 6))
    if not erg:
        return None
    (I, II), weg = erg
    return lgs([I, II], x0, y0, weg, TIPPS_ADD)


ANZAHL = ["genau eine Lösung", "keine Lösung", "unendlich viele Lösungen"]
GEOMETRIE = ["Die Geraden schneiden sich in einem Punkt.", "Die Geraden sind parallel.", "Die Geraden sind identisch (liegen aufeinander)."]
ANZAHL_ERK = {
    0: "Die Gleichungen sind kein Vielfaches voneinander – die beiden Geraden haben verschiedene Steigungen und schneiden sich "
       "in genau einem Punkt.",
    1: "Die linken Seiten sind Vielfache voneinander, die rechten Seiten aber nicht im selben Verhältnis. Beim Lösen bleibt "
       "z. B. `0 = 5` übrig – ein Widerspruch. Die Geraden sind **parallel**: keine Lösung.",
    2: "Die eine Gleichung ist ein Vielfaches der anderen – beide beschreiben **dieselbe** Gerade. Beim Lösen bleibt `0 = 0` "
       "übrig: unendlich viele Lösungen.",
}


def b4_3(r, s):
    a, b = nz(r, -5, 5), nz(r, -5, 5)
    c = nz(r, -9, 9)
    k = r.choice([2, 3, -2, -1]) if s > 1 else r.choice([2, 3])
    fall = r.choice([0, 1, 2])
    if fall == 0:
        a2, b2 = nz(r, -5, 5), nz(r, -5, 5)
        if a * b2 == a2 * b:
            return None
        c2 = nz(r, -9, 9)
    elif fall == 1:
        a2, b2, c2 = k * a, k * b, k * c + nz(r, -4, 4)
        if c2 == k * c:
            return None
    else:
        a2, b2, c2 = k * a, k * b, k * c
    I, II = gl(a, b, c), gl(a2, b2, c2)
    if s >= 3 and fall != 0 and r.random() < .5:
        return {"typ": "lgs", "gleichungen": [I, II], "loesung": "keine" if fall == 1 else "unendlich",
                "erklaerung": ANZAHL_ERK[fall],
                "tipps": ["Vergleiche die beiden Gleichungen: Ist die eine (links) ein Vielfaches der anderen?",
                          "Versuch, y zu eliminieren. Bleibt `0 = 0` oder ein Widerspruch wie `0 = 5` übrig?",
                          "Schreib „keine“ oder „unendlich viele“, wenn es keine einzelne Lösung gibt."],
                "fehler": []}
    optionen = GEOMETRIE if s in (2, 4) else ANZAHL
    return {"typ": "auswahl", "frage": f"Wie viele Lösungen hat das Gleichungssystem `{I}` und `{II}`?" if optionen is ANZAHL
            else f"Was gilt für die beiden Geraden `{I}` und `{II}`?",
            "optionen": optionen, "richtig": [fall], "pruefung": {"art": "lgs_anzahl", "gleichungen": [I, II]},
            "erklaerung": ANZAHL_ERK[fall],
            "tipps": ["Ist die zweite Gleichung (links) ein Vielfaches der ersten? Prüf auch die rechte Seite."]}


def b4_4(r, s):
    art = r.choice(["kino", "zahlen", "tiere", "muenzen", "alter"][: 3 if s == 1 else 5])
    if art == "kino":
        x0, y0 = r.randint(8, 14), r.randint(4, 8)
        e1, k1, e2, k2 = r.randint(2, 5), r.randint(2, 5), r.randint(2, 5), r.randint(2, 5)
        if e1 * k2 == e2 * k1:
            return None
        frage = (f"Im Kino zahlen {e1} Erwachsene und {k1} Kinder zusammen {e1 * x0 + k1 * y0} €. {e2} Erwachsene und {k2} Kinder "
                 f"zahlen {e2 * x0 + k2 * y0} €. Was kostet eine Karte für Erwachsene (x) und eine für Kinder (y)?")
        a1, b1, a2, b2 = e1, k1, e2, k2
    elif art == "zahlen":
        x0, y0 = r.randint(10, 40), r.randint(1, 9)
        frage = (f"Die Summe zweier Zahlen ist {x0 + y0}, ihre Differenz ist {x0 - y0}. Wie heißen die größere Zahl x und die "
                 "kleinere Zahl y?")
        a1, b1, a2, b2 = 1, 1, 1, -1
    elif art == "tiere":
        x0, y0 = r.randint(3, 15), r.randint(2, 12)
        frage = (f"Auf einem Bauernhof gibt es Hühner (x) und Kaninchen (y). Zusammen haben sie {x0 + y0} Köpfe und "
                 f"{2 * x0 + 4 * y0} Beine. Wie viele Hühner und wie viele Kaninchen sind es?")
        a1, b1, a2, b2 = 1, 1, 2, 4
    elif art == "muenzen":
        x0, y0 = r.randint(3, 12), r.randint(2, 14)
        frage = (f"In einer Kasse liegen {x0 + y0} Münzen, nur 2-€-Münzen (x) und 50-Cent-Münzen (y). Zusammen sind sie "
                 f"{zt(2 * x0 + F(1, 2) * y0)} € wert. Wie viele Münzen jeder Sorte sind es?")
        a1, b1, a2, b2 = 1, 1, 2, F(1, 2)
    else:
        y0 = r.randint(6, 14)
        n = r.randint(3, 4)
        x0 = n * y0
        j = r.randint(4, 12)
        if (x0 + j) % (y0 + j):
            return None
        m = (x0 + j) // (y0 + j)
        if m in (1, n):
            return None
        frage = (f"Eine Mutter ist heute {n}-mal so alt wie ihre Tochter. In {j} Jahren ist sie {m}-mal so alt. "
                 "Wie alt sind Mutter (x) und Tochter (y) heute?")
        gleichungen = [f"x = {n}y", f"x + {j} = {m}(y + {j})"]
        weg = [f"{n}y + {j} = {m}(y + {j}) | I in II einsetzen", f"{n}y + {j} = {m}y + {m * j}",
               f"{n - m}y = {m * j - j}", f"y = {y0}", f"x = {x0} | in I einsetzen"]
        return lgs(gleichungen, x0, y0, weg, ["Übersetze jeden Satz in eine Gleichung. „In j Jahren“: beide sind j Jahre älter.",
                                                f"I: `x = {n}y`. II: `x + {j} = {m}(y + {j})`.", "Setz I in II ein."], frage=frage)
    erg = addition(r, x0, y0, a1, b1, a2, b2)
    if not erg:
        return None
    (I, II), weg = erg
    return lgs([I, II], x0, y0, weg,
               ["Übersetze jeden Satz in eine Gleichung mit x und y.", f"I: `{I}`, II: `{II}`.",
                "Löse mit dem Verfahren, das dir am liebsten ist – z. B. Additionsverfahren."], frage=frage)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261023)
    for lid, fn, n in [("B4.1", b4_1, 8), ("B4.2", b4_2, 8), ("B4.3", b4_3, 8), ("B4.4", b4_4, 6)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "b4.py")


if __name__ == "__main__":
    main()
