"""
Generator für Kapitel A2 (Brüche und Dezimalzahlen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/a2.py

Stufen: 1 Einstieg (kleine Nenner) · 2 Üben · 3 Vertiefen (negative Zahlen, mehrere Brüche) ·
4 Matura-Niveau (große Nenner, Klammern, gemischte Aufgaben).
"""

import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gemeinsam import dez, echter_bruch, erzeuge, fehler_zahlen, schreibe, z  # noqa: E402

GEKUERZT = "Am Schluss kürzen, so weit es geht."


def bt(q, erstes=False) -> str:
    """Bruch in einer Rechnung: negative in Klammern (außer ganz vorne)"""
    q = F(q)
    if q < 0 and not erstes:
        return f"({z(q)})"
    return z(q)


def gekuerzt_aufgabe(frage, ergebnis, weg, tipps, fehler, rechnung=None):
    a = {"typ": "zahl", "frage": frage, "loesung": z(ergebnis), "form": "gekuerzt", "weg": weg,
         "tipps": tipps, "fehler": fehler_zahlen(ergebnis, fehler)}
    if rechnung:
        a["rechnung"] = rechnung
    return a


# ── A2.1 Kürzen und Erweitern ─────────────────────────────

def kuerzen(r, nenner, faktoren, negativ=False):
    q = echter_bruch(r, nenner, negativ=negativ)
    k = r.choice(faktoren)
    a, b = q.numerator * k, q.denominator * k
    if b > 400:
        return None
    teiler = [t for t in (2, 3, 5, 7) if a % t == 0 and b % t == 0]
    return gekuerzt_aufgabe(
        f"Kürze so weit wie möglich: `{a}/{b}`", q,
        [f"{a}/{b} = {z(q)} | Zähler und Nenner durch {k}"],
        ["Suche eine Zahl, durch die Zähler **und** Nenner teilbar sind, und dividiere beide durch sie.",
         f"{abs(a)} und {b} sind beide durch {teiler[0]} teilbar. Schau danach, ob es noch weiter geht.",
         f"Der größte gemeinsame Teiler ist {k}."],
        [(F(a // k, b), "Beim Kürzen werden Zähler **und** Nenner durch dieselbe Zahl dividiert – nicht nur der Zähler."),
         (F(a, b // k), "Beim Kürzen werden Zähler **und** Nenner durch dieselbe Zahl dividiert – nicht nur der Nenner.")])


def erweitern(r, nenner, kmax):
    q = echter_bruch(r, nenner)
    k = r.randint(2, kmax)
    n = q.denominator * k
    return {"typ": "zahl", "frage": f"Erweitere `{z(q)}` auf den Nenner {n}.",
            "loesung": f"{q.numerator * k}/{n}", "form": "nenner", "nenner": n,
            "weg": [f"{z(q)} = {q.numerator * k}/{n} | Zähler und Nenner mal {k}"],
            "tipps": [f"Womit musst du {q.denominator} multiplizieren, damit {n} herauskommt?",
                      f"{q.denominator} · {k} = {n}. Jetzt den Zähler auch mal {k}."],
            "fehler": fehler_zahlen(q, [
                (F(q.numerator, n), f"Auch der Zähler muss mit {k} multipliziert werden – sonst ändert sich der Wert."),
                (F(q.numerator + n - q.denominator, n), "Erweitern heißt multiplizieren – nicht dieselbe Zahl dazuzählen.")])}


def luecke(r, nenner, kmax):
    q = echter_bruch(r, nenner)
    k = r.randint(3, kmax)
    n = q.denominator * k
    return {"typ": "zahl", "frage": f"`{z(q)}` soll so erweitert werden, dass im Nenner {n} steht. Welcher Zähler kommt heraus?",
            "loesung": str(q.numerator * k),
            "tipps": [f"Rechne zuerst: {q.denominator} mal wie viel ergibt {n}?",
                      f"{q.denominator} · {k} = {n} – also auch den Zähler mal {k}."],
            "fehler": fehler_zahlen(q.numerator * k, [
                (q.numerator + n - q.denominator, "Erweitern heißt multiplizieren – nicht dieselbe Zahl dazuzählen."),
                (q.numerator, f"Der Zähler muss auch mit {k} multipliziert werden.")])}


def vergleichen(r, nenner, abstand=F(1, 6)):
    p, q = echter_bruch(r, nenner), echter_bruch(r, nenner)
    if p == q or p.denominator == q.denominator or abs(p - q) > abstand or p.numerator == q.numerator == 1:
        return None
    L = math.lcm(p.denominator, q.denominator)
    gross = max(p, q)
    erk = (f"Bring beide auf den Nenner {L}: `{z(p)} = {p.numerator * L // p.denominator}/{L}` und "
           f"`{z(q)} = {q.numerator * L // q.denominator}/{L}`. Jetzt siehst du: `{z(gross)}` ist größer.")
    return {"typ": "auswahl", "frage": f"Welcher Bruch ist größer: `{z(p)}` oder `{z(q)}`?", "mathe": True,
            "optionen": [z(p), z(q)], "richtig": [0 if gross == p else 1], "erklaerung": erk,
            "pruefung": {"art": "wert", "ziel": z(gross)},
            "tipps": ["Bring beide Brüche auf denselben Nenner. Dann vergleichst du nur die Zähler."]}


def gleichwertig(r, nenner):
    q = echter_bruch(r, nenner)
    k = r.randint(2, 6)
    richtig = F(q.numerator * k, q.denominator * k)
    falsch1 = (q.numerator + k, q.denominator + k)        # „dazuzählen“
    falsch2 = (q.numerator * k, q.denominator + k)
    optionen = [f"{q.numerator * k}/{q.denominator * k}", f"{falsch1[0]}/{falsch1[1]}", f"{falsch2[0]}/{falsch2[1]}"]
    if len({F(*map(int, o.split("/"))) for o in optionen}) < 3 or F(*falsch1) == q or F(*falsch2) == q:
        return None
    r.shuffle(optionen)
    idx = optionen.index(f"{q.numerator * k}/{q.denominator * k}")
    return {"typ": "auswahl", "frage": f"Welcher Bruch ist gleich groß wie `{z(q)}`?", "mathe": True,
            "optionen": optionen, "richtig": [idx], "pruefung": {"art": "wert", "ziel": z(richtig)},
            "erklaerung": f"`{optionen[idx]}` ist `{z(q)}`, erweitert mit {k}: Zähler **und** Nenner mal {k}. "
                          "Bei den anderen wurde etwas dazugezählt – das ändert den Wert.",
            "tipps": ["Kürze jeden Bruch so weit wie möglich und vergleiche dann."]}


def a2_1(r, s):
    w = r.random()
    if s == 1:
        return kuerzen(r, [2, 3, 4, 5], [2, 3, 5]) if w < .6 else erweitern(r, [2, 3, 4, 5], 4)
    if s == 2:
        if w < .5:
            return kuerzen(r, [3, 4, 5, 6, 7, 8, 9], [4, 6, 8, 9, 10, 12])
        return luecke(r, [3, 4, 5, 6, 7, 8], 9) if w < .75 else gleichwertig(r, [3, 4, 5, 7])
    if s == 3:
        if w < .5:
            return kuerzen(r, [5, 7, 8, 9, 11, 12], [12, 14, 15, 16, 18, 21, 24], negativ=True)
        return vergleichen(r, [3, 4, 5, 6, 8, 9, 10, 12]) if w < .8 else erweitern(r, [7, 9, 11, 12], 8)
    if w < .6:
        return kuerzen(r, [7, 9, 11, 13, 15, 16], [21, 24, 28, 32, 35, 36, 42, 45], negativ=True)
    return vergleichen(r, [6, 7, 8, 9, 11, 12, 15, 16], abstand=F(1, 12))


# ── A2.2 Bruch ↔ Dezimalzahl ↔ Prozent ────────────────────

def zehner(q):
    """Kleinste Zehnerpotenz, auf die man q erweitern kann: (Zähler, 10^m)"""
    for m in range(1, 5):
        if (10 ** m) % q.denominator == 0:
            return q.numerator * (10 ** m) // q.denominator, 10 ** m
    raise AssertionError(q)


def b2d(r, nenner, ueber1=False):
    q = echter_bruch(r, nenner, hi=(2 * max(nenner)) if ueber1 else None)
    zz, n = zehner(q)
    falsch = F(q.numerator) + F(q.denominator, 10 ** len(str(q.denominator)))
    return {"typ": "zahl", "frage": f"Schreib `{z(q)}` als Dezimalzahl.", "loesung": dez(q), "form": "dezimal",
            "weg": [f"{z(q)} = {zz}/{n} = {dez(q)} | auf den Nenner {n} erweitert"],
            "tipps": ["Erweitere den Bruch auf den Nenner 10, 100 oder 1000.",
                      f"`{z(q)} = {zz}/{n}`. Wie schreibt man das als Dezimalzahl?",
                      f"Oder rechne einfach {q.numerator} : {q.denominator}."],
            "fehler": fehler_zahlen(q, [(falsch, f"Der Bruchstrich ist kein Komma: `{z(q)}` heißt {q.numerator} : {q.denominator}.")])}


def d2b(r, nenner, ueber1=False):
    q = echter_bruch(r, nenner, hi=(2 * max(nenner)) if ueber1 else None)
    zz, n = zehner(q)
    return gekuerzt_aufgabe(
        f"Schreib `{dez(q)}` als gekürzten Bruch.", q,
        [f"{dez(q)} = {zz}/{n} = {z(q)} | {'Zehntel' if n == 10 else 'Hundertstel' if n == 100 else 'Tausendstel'}, dann kürzen"],
        [f"Die letzte Nachkommastelle zeigt dir den Nenner: {'Zehntel → 10' if n == 10 else 'Hundertstel → 100' if n == 100 else 'Tausendstel → 1000'}.",
         f"`{dez(q)} = {zz}/{n}`. Jetzt kürzen!"],
        [])


def d2p(r, nenner, ueber1=False):
    q = echter_bruch(r, nenner, hi=(2 * max(nenner)) if ueber1 else None)
    p = q * 100
    return {"typ": "zahl", "frage": f"Wie viel Prozent sind `{dez(q)}`?", "loesung": dez(p), "einheit": "%",
            "weg": [f"{dez(q)} · 100 = {dez(p)} | Prozent heißt Hundertstel"],
            "tipps": ["„Prozent“ heißt „Hundertstel“. Wie viele Hundertstel sind das?",
                      "Multipliziere mit 100: Das Komma rückt zwei Stellen nach rechts."],
            "fehler": fehler_zahlen(p, [(q, "Das ist noch die Dezimalzahl. In Prozent: mal 100 – das Komma rückt zwei Stellen nach rechts."),
                                        (q * 10, "Fast – für Prozent rückt das Komma **zwei** Stellen nach rechts (mal 100).")])}


def p2d(r, prozente):
    p = F(r.choice(prozente))
    q = p / 100
    return {"typ": "zahl", "frage": f"Schreib {dez(p)} % als Dezimalzahl.", "loesung": dez(q), "form": "dezimal",
            "weg": [f"{dez(p)} : 100 = {dez(q)} | Prozent heißt Hundertstel"],
            "tipps": ["„Prozent“ heißt „Hundertstel“: dividiere durch 100.",
                      "Durch 100 dividieren: Das Komma rückt zwei Stellen nach links."],
            "fehler": fehler_zahlen(q, [(p, "Das ist noch die Prozentzahl. Als Dezimalzahl: durch 100."),
                                        (p / 10, "Fast – das Komma rückt **zwei** Stellen nach links (durch 100).")])}


def b2p(r, nenner):
    q = echter_bruch(r, nenner)
    p = q * 100
    return {"typ": "zahl", "frage": f"Wie viel Prozent sind `{z(q)}`?", "loesung": dez(p), "einheit": "%",
            "weg": [f"{z(q)} · 100 = {dez(p)} | Prozent heißt Hundertstel"],
            "tipps": ["Erweitere auf den Nenner 100 – der Zähler ist dann die Prozentzahl.",
                      f"Oder: zuerst als Dezimalzahl ({dez(q)}), dann mal 100."],
            "fehler": fehler_zahlen(p, [(q, "Das ist die Dezimalzahl. In Prozent: noch mal 100.")])}


def p2b(r, prozente):
    p = F(r.choice(prozente))
    q = p / 100
    if q.denominator == 1:
        return None
    return gekuerzt_aufgabe(
        f"Schreib {dez(p)} % als gekürzten Bruch.", q,
        [f"{dez(p)}/100 = {z(q)} | Prozent heißt Hundertstel, dann kürzen"],
        ["„Prozent“ heißt „Hundertstel“: Schreib die Prozentzahl über 100.",
         "Hat die Prozentzahl ein Komma, erweitere mit 10, damit der Zähler ganz wird. Dann kürzen."],
        [(F(1, 1) / q if q != 0 else None, "Umgekehrt: Die Prozentzahl gehört in den Zähler, 100 in den Nenner.")])


def a2_2(r, s):
    w = r.random()
    if s == 1:
        if w < .35:
            return b2d(r, [2, 4, 5, 10])
        if w < .6:
            return d2p(r, [2, 4, 5, 10])
        return p2d(r, [5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 3, 7, 9])
    if s == 2:
        if w < .3:
            return b2d(r, [8, 20, 25, 50])
        if w < .55:
            return d2b(r, [4, 5, 20, 25, 50])
        if w < .8:
            return b2p(r, [4, 5, 20, 25, 50])
        return d2p(r, [8, 20, 25, 50])
    if s == 3:
        if w < .25:
            return b2d(r, [4, 5, 8, 20], ueber1=True)
        if w < .5:
            return p2b(r, [F(25, 2), F(75, 2), F(5, 2), F(15, 2), 35, 45, 64, 85, 120, 150, 175, 250])
        if w < .75:
            return d2p(r, [4, 5, 8, 20, 40], ueber1=True)
        return p2d(r, [F(1, 2), F(3, 2), F(5, 2), F(25, 2), 120, 150, 105, F(1, 4)])
    if w < .3:
        return b2d(r, [16, 40, 80, 125])
    if w < .55:
        return d2b(r, [16, 40, 80, 125, 200])
    if w < .8:
        return b2p(r, [8, 16, 40, 80])
    return p2b(r, [F(1, 2), F(5, 4), F(1, 4), F(75, 4), F(125, 2), F(5, 8) * 10, 0.5, 2.5])


# ── A2.3 Brüche addieren und subtrahieren ─────────────────

def summe_text(glieder):
    """[(+1, 1/2), (-1, 1/3)] → '1/2 - 1/3'; erstes Glied mit Vorzeichen"""
    aus = ""
    for i, (v, q) in enumerate(glieder):
        t = z(q)
        if i == 0:
            aus = ("-" if v < 0 else "") + t
        else:
            aus += f" {'-' if v < 0 else '+'} {t}"
    return aus


def addition(r, nenner, anzahl=2, gleich=False, ganz=False, minus=0.5, neg_erst=False):
    glieder = []
    n0 = r.choice(nenner)
    for i in range(anzahl):
        n = n0 if gleich else r.choice(nenner)
        q = echter_bruch(r, [n], hi=n - 1) if not (ganz and i == 0) else F(r.randint(2, 4))
        v = -1 if (i > 0 and r.random() < minus) or (i == 0 and neg_erst and r.random() < .5) else 1
        glieder.append((v, q))
    nennerliste = [q.denominator for _, q in glieder]
    if not gleich and len(set(nennerliste)) == 1 or len({q for _, q in glieder}) < anzahl:
        return None
    L = math.lcm(*nennerliste)
    erg = sum(v * q for v, q in glieder)
    if erg == 0:
        return None
    text = summe_text(glieder)
    erweitert = " ".join(
        (("-" if v < 0 else "") if i == 0 else ("- " if v < 0 else "+ ")) + f"{q.numerator * L // q.denominator}/{L}"
        for i, (v, q) in enumerate(glieder))
    zaehler = sum(v * q.numerator * L // q.denominator for v, q in glieder)
    kette = [text]
    if len(set(nennerliste)) > 1 or ganz:
        kette.append(erweitert)
    kette += [f"{zaehler}/{L}", z(erg)]
    weg = [" = ".join(dict.fromkeys(kette))]
    naiv_n = sum(q.denominator for _, q in glieder)
    naiv_z = sum(v * q.numerator for v, q in glieder)
    fehler = [(F(naiv_z, naiv_n) if naiv_n else None,
               "Die Nenner werden nicht addiert! Bei gleichem Nenner bleibt der Nenner einfach stehen, du rechnest nur mit den Zählern."
               if gleich else
               "Die Nenner werden nicht addiert! Bring die Brüche auf einen gemeinsamen Nenner – dann rechnest du nur mit den Zählern."),
              (F(naiv_z, L) if len(set(nennerliste)) > 1 else None,
               "Beim Erweitern musst du auch den **Zähler** mit derselben Zahl multiplizieren wie den Nenner.")]
    if gleich:
        tipps = ["Die Nenner sind gleich: Rechne nur mit den Zählern, der Nenner bleibt.", GEKUERZT]
    else:
        tipps = [f"Such einen gemeinsamen Nenner. Hier passt {L}.",
                 f"Erweitere jeden Bruch auf den Nenner {L} – Zähler und Nenner mit derselben Zahl mal.",
                 "Dann die Zähler addieren bzw. subtrahieren. " + GEKUERZT]
    return gekuerzt_aufgabe(f"Berechne `{text}`.", erg, weg, tipps, fehler, rechnung=text)


def klammer_minus(r, nenner):
    a, b, c = (echter_bruch(r, nenner) for _ in range(3))
    text = f"{z(a)} - ({z(b)} - {z(c)})"
    erg = a - (b - c)
    if erg == 0 or len({a.denominator, b.denominator, c.denominator}) < 2:
        return None
    L = math.lcm(a.denominator, b.denominator, c.denominator)
    e = lambda q: f"{q.numerator * L // q.denominator}/{L}"  # noqa: E731
    weg = [" = ".join(dict.fromkeys([text, f"{z(a)} - {z(b)} + {z(c)}", f"{e(a)} - {e(b)} + {e(c)}",
                                     f"{(erg * L).numerator if (erg * L).denominator == 1 else erg * L}/{L}", z(erg)]))]
    return gekuerzt_aufgabe(
        f"Berechne `{text}`.", erg, weg,
        ["Minus vor der Klammer: Beim Auflösen dreht sich jedes Vorzeichen in der Klammer um.",
         f"`{text} = {z(a)} - {z(b)} + {z(c)}`. Gemeinsamer Nenner: {L}.", GEKUERZT],
        [(a - b - c, "Minus vor der Klammer dreht **jedes** Vorzeichen in der Klammer um: aus − wird +.")],
        rechnung=text)


def a2_3(r, s):
    w = r.random()
    if s == 1:
        return addition(r, [3, 4, 5, 6, 7, 8, 9, 10, 12], gleich=True, minus=.4)
    if s == 2:
        if w < .5:
            n = r.choice([2, 3, 4, 5])
            return addition(r, [n, n * r.choice([2, 3])], minus=.4)
        return addition(r, [2, 3, 4, 5, 6], minus=.4)
    if s == 3:
        if w < .35:
            return addition(r, [2, 3, 4, 6], anzahl=3, minus=.5)
        if w < .65:
            return addition(r, [2, 3, 4, 5, 6, 8], ganz=True, minus=.9)
        return addition(r, [3, 4, 5, 6, 8], neg_erst=True, minus=.4)
    if w < .5:
        return addition(r, [6, 8, 9, 10, 12, 15, 18], minus=.5, neg_erst=True)
    if w < .75:
        return klammer_minus(r, [2, 3, 4, 6, 8, 12])
    return addition(r, [4, 6, 8, 9, 12], anzahl=3, minus=.5, neg_erst=True)


# ── A2.4 Brüche multiplizieren und dividieren ─────────────

def multiplikation(r, nenner, anzahl=2, ganz=False, negativ=False):
    fs = []
    for i in range(anzahl):
        if ganz and i == 0:
            fs.append(F(r.randint(2, 6)))
        else:
            q = echter_bruch(r, nenner, hi=max(nenner) + 3)
            fs.append(-q if negativ and r.random() < .5 else q)
    erg = math.prod(fs)
    text = " · ".join(bt(q, i == 0) for i, q in enumerate(fs))
    zz, nn = math.prod(q.numerator for q in fs), math.prod(q.denominator for q in fs)
    weg = [" = ".join(dict.fromkeys([text, f"{zz}/{nn}" if nn != 1 else str(zz), z(erg)]))]
    fehler = []
    if ganz:
        fehler.append((F(fs[1].numerator, fs[0] * fs[1].denominator),
                       "Eine ganze Zahl multiplizierst du nur mit dem **Zähler** (denk dir 3 = 3/1)."))
    if negativ:
        fehler.append((-erg, "Achte auf das Vorzeichen: Minus mal Minus ergibt Plus, Minus mal Plus ergibt Minus."))
    tipps = ["Zähler mal Zähler, Nenner mal Nenner. Einen gemeinsamen Nenner brauchst du hier **nicht**.",
             "Tipp: Du kannst schon vor dem Ausrechnen über Kreuz kürzen – dann bleiben die Zahlen klein.", GEKUERZT]
    if ganz:
        tipps[0] = f"Schreib {fs[0]} als Bruch: `{fs[0]} = {fs[0]}/1`. Dann Zähler mal Zähler, Nenner mal Nenner."
    return gekuerzt_aufgabe(f"Berechne `{text}`.", erg, weg, tipps, fehler, rechnung=text)


def division(r, nenner, ganz=None, negativ=False):
    p = echter_bruch(r, nenner, hi=max(nenner) + 3)
    q = echter_bruch(r, nenner, hi=max(nenner) + 3)
    if ganz == "links":
        p = F(r.randint(2, 9))
    if ganz == "rechts":
        q = F(r.randint(2, 6))
    if negativ:
        p = -p if r.random() < .5 else p
        q = -q if r.random() < .6 else q
    erg = p / q
    text = f"{bt(p, True)} : {bt(q)}"
    kehr = 1 / q
    weg = [" = ".join(dict.fromkeys([text, f"{bt(p, True)} · {bt(kehr)}", z(erg)]))]
    return gekuerzt_aufgabe(
        f"Berechne `{text}`.", erg, weg,
        ["Durch einen Bruch dividierst du, indem du mit dem **Kehrwert** multiplizierst.",
         f"Der Kehrwert von `{z(q)}` ist `{z(kehr)}`. Also: `{bt(p, True)} · {bt(kehr)}`.", GEKUERZT],
        [(p * q, "Beim Dividieren musst du den zweiten Bruch umdrehen (Kehrwert) und dann multiplizieren."),
         ((1 / p) * q if p != 0 else None, "Nur der **zweite** Bruch wird umgedreht, nicht der erste."),
         (-erg if negativ else None, "Achte auf das Vorzeichen!")],
        rechnung=text)


def gemischt_mult(r, nenner):
    a, b = echter_bruch(r, nenner), echter_bruch(r, nenner)
    c = echter_bruch(r, nenner, hi=max(nenner) + 4)
    if a == b:
        return None
    if r.random() < .5:
        text = f"({z(a)} - {z(b)}) · {z(c)}"
        erg = (a - b) * c
        innen = a - b
        falsch = a - b * c
        hinweis = "Die Klammer kommt zuerst! Erst die Differenz in der Klammer ausrechnen, dann multiplizieren."
    else:
        text = f"{z(c)} : ({z(a)} + {z(b)})"
        erg = c / (a + b)
        innen = a + b
        falsch = c / a + b
        hinweis = "Die Klammer kommt zuerst! Erst die Summe in der Klammer ausrechnen, dann dividieren."
    if erg == 0:
        return None
    weg = [" = ".join(dict.fromkeys([text, text.replace(text[text.index("("):text.index(")") + 1], bt(innen)), z(erg)]))]
    return gekuerzt_aufgabe(f"Berechne `{text}`.", erg, weg,
                            ["Zuerst die Klammer: Dafür brauchst du einen gemeinsamen Nenner.",
                             f"In der Klammer kommt `{z(innen)}` heraus.", GEKUERZT],
                            [(falsch, hinweis)], rechnung=text)


def a2_4(r, s):
    w = r.random()
    if s == 1:
        if w < .6:
            return multiplikation(r, [2, 3, 4, 5, 7])
        return multiplikation(r, [3, 4, 5, 7, 8, 9], ganz=True)
    if s == 2:
        if w < .4:
            return multiplikation(r, [3, 4, 5, 6, 8, 9])
        if w < .8:
            return division(r, [2, 3, 4, 5, 6, 7])
        return division(r, [3, 4, 5, 7], ganz=r.choice(["links", "rechts"]))
    if s == 3:
        if w < .4:
            return multiplikation(r, [3, 4, 5, 6, 8, 9], anzahl=3, negativ=True)
        if w < .8:
            return division(r, [3, 4, 5, 6, 8, 9], negativ=True)
        return division(r, [4, 5, 6, 8], ganz="links", negativ=True)
    if w < .6:
        return gemischt_mult(r, [2, 3, 4, 5, 6])
    return multiplikation(r, [5, 6, 8, 9, 10, 12, 14, 15], anzahl=3, negativ=True)


# ── A2.5 Doppelbrüche und gemischte Aufgaben ──────────────

def doppelbruch(r, nenner, oben_ganz=False, unten_ganz=False):
    p = F(r.randint(2, 6)) if oben_ganz else echter_bruch(r, nenner)
    q = F(r.randint(2, 6)) if unten_ganz else echter_bruch(r, nenner)
    if p == q:
        return None
    pt = str(p) if oben_ganz else f"({z(p)})"
    qt = str(q) if unten_ganz else f"({z(q)})"
    text = f"{pt}/{qt}"
    erg = p / q
    weg = [" = ".join(dict.fromkeys([text, f"{z(p)} : {z(q)}" if not unten_ganz else f"{z(p)} : {q}",
                                     f"{z(p)} · {z(1 / q)}", z(erg)]))]
    return gekuerzt_aufgabe(f"Berechne den Doppelbruch `{text}`.", erg, weg,
                            ["Ein Doppelbruch ist eine Division: oben **durch** unten.",
                             f"`{text} = {z(p)} : {z(q)}`. Dividieren heißt: mit dem Kehrwert multiplizieren.", GEKUERZT],
                            [(q / p, "Oben ist der Zähler, unten der Nenner: Rechne oben **durch** unten, nicht umgekehrt."),
                             (p * q, "Ein Doppelbruch ist eine Division – du musst mit dem Kehrwert multiplizieren.")],
                            rechnung=text)


def vorrang(r, nenner):
    a, b, c = echter_bruch(r, nenner), echter_bruch(r, nenner), echter_bruch(r, nenner, hi=max(nenner) + 3)
    op = r.choice(["+", "-"])
    text = f"{z(a)} {op} {z(b)} · {z(c)}"
    bc = b * c
    erg = a + bc if op == "+" else a - bc
    falsch = (a + b) * c if op == "+" else (a - b) * c
    if erg == 0 or falsch == erg:
        return None
    weg = [" = ".join(dict.fromkeys([text, f"{z(a)} {op} {z(bc)}", z(erg)]))]
    return gekuerzt_aufgabe(f"Berechne `{text}`.", erg, weg,
                            ["Punkt vor Strich: Zuerst wird multipliziert.",
                             f"`{z(b)} · {z(c)} = {z(bc)}`. Jetzt noch {'addieren' if op == '+' else 'subtrahieren'}.",
                             GEKUERZT],
                            [(falsch, "Punkt vor Strich! Zuerst `" + f"{z(b)} · {z(c)}" + "` rechnen, dann erst " +
                              ("addieren." if op == "+" else "subtrahieren."))],
                            rechnung=text)


def doppelbruch_summe(r, nenner, schwer=False):
    a, b, c = echter_bruch(r, nenner), echter_bruch(r, nenner), echter_bruch(r, nenner)
    oben = (a + b) if not schwer else (a - b)
    o_text = f"{z(a)} {'+' if not schwer else '-'} {z(b)}"
    if schwer:
        d = echter_bruch(r, nenner)
        unten, u_text = c + d, f"{z(c)} + {z(d)}"
    else:
        if r.random() < .5:
            unten, u_text = c, z(c)
        else:
            unten, u_text = 1 - c, f"1 - {z(c)}"
    if oben == 0 or unten == 0 or a == b:
        return None
    text = f"({o_text})/({u_text})"
    erg = oben / unten
    weg = [" = ".join(dict.fromkeys([text, f"({z(oben)})/({z(unten)})", f"{bt(oben, True)} : {bt(unten)}", z(erg)]))]
    return gekuerzt_aufgabe(f"Berechne `{text}`.", erg, weg,
                            ["Rechne zuerst oben und unten getrennt aus – jeweils ein einziger Bruch.",
                             f"Oben kommt `{z(oben)}` heraus, unten `{z(unten)}`.",
                             "Dann oben durch unten: mit dem Kehrwert multiplizieren. " + GEKUERZT],
                            [(unten / oben, "Oben durch unten – nicht umgekehrt."),
                             (oben * unten, "Ein Bruchstrich bedeutet Division: mit dem Kehrwert multiplizieren.")],
                            rechnung=text)


def a2_5(r, s):
    w = r.random()
    if s == 1:
        return doppelbruch(r, [2, 3, 4, 5, 6])
    if s == 2:
        if w < .4:
            return doppelbruch(r, [3, 4, 5, 6, 8], oben_ganz=w < .2, unten_ganz=w >= .2)
        if w < .7:
            return doppelbruch(r, [3, 4, 5, 7, 8, 9])
        return vorrang(r, [2, 3, 4, 5])
    if s == 3:
        if w < .6:
            return doppelbruch_summe(r, [2, 3, 4, 6])
        return vorrang(r, [3, 4, 5, 6, 8])
    return doppelbruch_summe(r, [2, 3, 4, 5, 6, 8], schwer=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261016)
    for lid, fn in [("A2.1", a2_1), ("A2.2", a2_2), ("A2.3", a2_3), ("A2.4", a2_4), ("A2.5", a2_5)]:
        schreibe(lid, erzeuge(lid, r, fn), "a2.py")


if __name__ == "__main__":
    main()
