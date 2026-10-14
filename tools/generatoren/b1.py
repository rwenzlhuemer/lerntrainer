"""
Generator für Kapitel B1 (Lineare Gleichungen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/b1.py

Schreibt inhalte/mathe/B1/B1.x.aufgaben.yaml. Fester Zufalls-Startwert → reproduzierbar.
Die Richtigkeit prüft unabhängig davon tools/build.py mit sympy.

Stufen (je Lernschritt):
  1 Einstieg   – ganze Zahlen, auch negative
  2 Üben       – alle Formen, Brüche als Lösung
  3 Vertiefen  – Dezimalzahlen, mehrere Klammern, Minus vor Bruch/Klammer
  4 Matura     – Brüche als Koeffizienten, gemischte Darstellungen, Klammern auf beiden Seiten
"""

import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

import yaml

ZIEL = Path(__file__).resolve().parents[2] / "inhalte" / "mathe" / "B1"
PRO_STUFE = 10


# ── Formatierung ──────────────────────────────────────────

def z(q) -> str:
    """Zahl in Schulnotation: 5, -3, 5/2 (Brüche)."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def endlich(q) -> bool:
    d = F(q).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def dez(q) -> str:
    """Dezimalzahl mit Komma, nur für endliche Dezimalbrüche."""
    q = F(q)
    assert endlich(q), q
    if q.denominator == 1:
        return str(q.numerator)
    s = f"{float(q):.6f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def anzeige(q) -> str:
    """Lösung lesbar: 5/2 = 2,5 – Dezimalform nur, wenn sie endet."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    return f"{z(q)} = {dez(q)}" if endlich(q) else z(q)


def koeff(a, var="x", f=z) -> str:
    """a·x als Text: x, -x, 3x, 0,5x, 2/3·x"""
    a = F(a)
    if a == 1:
        return var
    if a == -1:
        return f"-{var}"
    if f is z and a.denominator != 1:
        return f"{z(a)}·{var}"
    return f"{f(a)}{var}"


def term(a, b=0, var="x", f=z) -> str:
    """a·x + b als Text: 3x - 5, -x + 2, x, 7"""
    return glieder([(a, var), (b, "")], f)


def glieder(liste, f=z) -> str:
    """Summe aus (Koeffizient, Variable) – auch unzusammengefasst: 6x + 4 - 2x - 6"""
    aus = ""
    for k, v in liste:
        k = F(k)
        if k == 0:
            continue
        if not aus:
            aus = koeff(k, v, f) if v else f(k)
        else:
            betrag = koeff(abs(k), v, f) if v else f(abs(k))
            aus += f" + {betrag}" if k > 0 else f" - {betrag}"
    return aus or "0"


def kl(q, f=z) -> str:
    """Zahl, negative in Klammern: 3, (-3)"""
    return f"({f(q)})" if F(q) < 0 else f(q)


def op(zeichen: str, q, f=z) -> str:
    """Kommentar zur Umformung: | −5, | +3, | :3, | ·2"""
    q = F(q)
    if zeichen in "+-":
        if q < 0:
            zeichen, q = ("-" if zeichen == "+" else "+"), -q
        return f"| {'−' if zeichen == '-' else '+'}{f(q)}"
    t = f(q).replace("-", "−")
    return f"| {zeichen}{t}" if q > 0 else f"| {zeichen}({t})"


def opx(q, f=z) -> str:
    """| −3x bzw. | +3x"""
    q = F(q)
    t = koeff(abs(q), "x", f)
    return f"| −{t}" if q > 0 else f"| +{t}"


def loese(A, B, C, D, f=z) -> list[str]:
    """Restlicher Lösungsweg für A·x + B = C·x + D (schon zusammengefasst)."""
    A, B, C, D = map(F, (A, B, C, D))
    k = A - C
    x0 = (D - B) / k
    aus = []
    if C != 0:
        aus.append(f"{term(k, B, f=f)} = {f(D)} {opx(C, f)}")
    if B != 0:
        aus.append(f"{term(k, f=f)} = {f(D - B)} {op('-', B, f)}")
    if k != 1:
        aus.append(f"x = {(f if endlich(x0) else z)(x0)} {op(':', k, f)}")
    return aus


def lin_fehler(A, B, C, D):
    """Typische falsche Ergebnisse für A·x + B = C·x + D."""
    A, B, C, D = map(F, (A, B, C, D))
    k = A - C
    aus = []
    if B != 0 and k != 0:
        aus.append(((D + B) / k, "Achtung beim Hinüberbringen der Zahl: Aus + wird −, aus − wird +."))
    if C != 0 and A + C != 0:
        aus.append(((D - B) / (A + C), "Beim Hinüberbringen des x-Glieds dreht sich das Vorzeichen um."))
    if k not in (0, 1, -1):
        aus.append(((D - B) * k, "Am Schluss wird dividiert, nicht multipliziert."))
    return aus


def fehlerliste(loesung, kandidaten):
    """Nur echte, voneinander verschiedene Fehler-Antworten behalten."""
    gesehen, aus = {F(loesung)}, []
    for wert, hinweis in kandidaten:
        if wert is None:
            continue
        w = F(wert)
        if w in gesehen:
            continue
        gesehen.add(w)
        aus.append({"antwort": z(w), "hinweis": hinweis})
    return aus


# ── Zufall ────────────────────────────────────────────────

def nz(r, lo, hi, ohne=(0,)):
    while True:
        v = r.randint(lo, hi)
        if v not in ohne:
            return v


def bruch(r, nenner=(2, 3, 4, 5, 6), lo=-11, hi=11):
    """Echter Bruch (nicht ganz), z. B. -5/6"""
    while True:
        q = F(nz(r, lo, hi), r.choice(nenner))
        if q.denominator != 1:
            return q


def dezi(r, lo, hi, teiler=10):
    """Dezimalzahl ≠ 0 mit höchstens zwei Stellen, z. B. 2,4 oder -0,25"""
    return F(nz(r, lo, hi), teiler)


def kgv(*zahlen):
    return math.lcm(*zahlen)


def vz(q) -> str:
    """+ 3 bzw. - 3 (Zahl mit Rechenzeichen davor)"""
    return f"+ {z(q)}" if F(q) >= 0 else f"- {z(-q)}"


def mal(k, innen, erstes=True) -> str:
    """k(innen) für den Lösungsweg; bei k = 1 ohne Faktor"""
    if erstes:
        return innen if k == 1 else f"{k}({innen})"
    return f"- ({innen})" if k == 1 else f"- {k}({innen})"


# ── Gerüst ────────────────────────────────────────────────

def gleichung(gl, loesung, weg, tipps, fehler=()):
    a = {"typ": "gleichung", "gleichung": gl, "loesung": z(loesung), "anzeige": anzeige(loesung),
         "weg": weg, "tipps": tipps}
    f = fehlerliste(loesung, fehler)
    if f:
        a["fehler"] = f
    return a


def erzeuge(lid, r, macher, pro_stufe=PRO_STUFE):
    """Ruft macher(r, stufe) so oft auf, bis jede Stufe genug verschiedene Aufgaben hat."""
    aus, gesehen, nr = [], set(), 0
    for stufe in (1, 2, 3, 4):
        n = 0
        for _ in range(5000):
            if n == pro_stufe:
                break
            try:
                a = macher(r, stufe)
            except (ZeroDivisionError, AssertionError):
                a = None
            if not a:
                continue
            schluessel = a.get("gleichung") or a.get("frage")
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            nr += 1
            n += 1
            aus.append({"id": f"{lid}-{nr:03d}", "typ": a.pop("typ"), "stufe": stufe, **a})
        else:
            raise RuntimeError(f"{lid} Stufe {stufe}: nicht genug Aufgaben")
    return aus


# ── B1.1 Probe: Ist das eine Lösung? ──────────────────────

def b1_1(r, stufe):
    if stufe == 1:
        a, b, x0 = nz(r, -6, 6, (0, 1, -1)), nz(r, -12, 12), nz(r, -6, 9)
        gl = f"{term(a, b)} = {a * x0 + b}"
        L, R = (lambda v: a * v + b), (lambda v: F(a * x0 + b))
        werte = [x0, x0 + r.choice([-2, -1, 1, 2]), -x0]
    elif stufe == 2:
        a, c = nz(r, -6, 6), nz(r, -5, 5)
        if a == c:
            return None
        b, x0 = nz(r, -9, 9), nz(r, -6, 8)
        d = (a - c) * x0 + b
        gl = f"{term(a, b)} = {term(c, d)}"
        L, R = (lambda v: a * v + b), (lambda v: c * v + d)
        werte = [x0, x0 + r.choice([-2, -1, 1, 2])]
    elif stufe == 3:
        a, b = nz(r, -5, 5, (0, 1, -1)), nz(r, -7, 7)
        c, x0 = nz(r, -4, 4), nz(r, -6, 6)
        if a == c:
            return None
        d = a * (x0 + b) - c * x0
        gl = f"{a}({term(1, b)}) = {term(c, d)}"
        L, R = (lambda v: a * (v + b)), (lambda v: c * v + d)
        werte = [x0, x0 + r.choice([-1, 1]), -x0]
    else:
        q = r.choice([2, 3, 4])
        x0 = F(nz(r, -9, 9), q)
        if x0.denominator == 1:
            return None
        a, b = nz(r, -6, 6, (0, 1, -1)), nz(r, -5, 5)
        c = a - q * nz(r, -2, 2)
        d = a * (x0 + b) - c * x0
        gl = f"{a}({term(1, b)}) = {term(c, d)}"
        L, R = (lambda v: a * (v + b)), (lambda v: c * v + d)
        werte = [x0, -x0, x0 + F(r.choice([-1, 1]), q)]
    wert = F(r.choice(werte)) if r.random() < 0.55 else F(x0)
    lw, rw = L(wert), R(wert)
    ja = lw == rw
    erk = (f"Setze `x = {z(wert)}` links und rechts ein. Links kommt `{z(lw)}` heraus, rechts `{z(rw)}`. "
           + ("Beide Seiten sind gleich ✓ – also ja." if ja else "Die Seiten sind verschieden – also keine Lösung."))
    return {"typ": "auswahl", "frage": f"Ist `x = {z(wert)}` eine Lösung der Gleichung `{gl}`?",
            "optionen": ["Ja", "Nein"], "richtig": [0 if ja else 1], "erklaerung": erk,
            "pruefung": {"art": "einsetzen", "gleichung": gl, "wert": z(wert)},
            "tipps": ["Setze die Zahl statt x ein und rechne beide Seiten aus.",
                      "Wenn links und rechts dasselbe herauskommt, ist es eine Lösung."]}


# ── B1.2 Plus und Minus ───────────────────────────────────

def b1_2(r, stufe):
    if stufe == 1:
        f, x0, b = z, F(nz(r, -15, 15)), F(nz(r, -15, 15))
    elif stufe == 2:
        f, x0, b = dez, dezi(r, -99, 99), dezi(r, -99, 99)
    elif stufe == 3:
        f, x0, b = z, bruch(r, (2, 3, 4, 6)), bruch(r, (2, 3, 4, 6))
    else:
        return b1_2_gemischt(r)
    c = x0 + b
    form = r.choice(["xb", "bx", "cxb"])
    links = term(1, b, f=f) if form != "bx" else f"{f(b)} + x"
    gl = f"{f(c)} = {links}" if form == "cxb" else f"{links} = {f(c)}"
    vz, gegen = ("+", "−") if b > 0 else ("−", "+")
    bt = f(abs(b))
    if stufe == 3:
        rest = f"{z(c)} - {z(b)}" if b > 0 else f"{z(c)} + {z(-b)}"
        weg = [gl, f"x = {rest} {op('-', b)}", f"x = {z(x0)} | auf gleichen Nenner bringen"]
    else:
        weg = [gl, f"x = {f(x0)} {op('-', b, f)}"]
    tipps = ["Ziel: x soll ganz allein auf einer Seite stehen. Was steht noch bei x?",
             f"Bei x steht {vz} `{bt}`. Das Gegenteil davon ist {gegen} `{bt}`.",
             f"Rechne auf beiden Seiten {gegen} `{bt}`."
             + (" Bring die Brüche dann auf einen gemeinsamen Nenner." if stufe == 3 else "")]
    fehler = [(c + b, f"Da wurde {vz} {bt} gerechnet statt {gegen} {bt}. "
                      f"Um {vz} {bt} wegzubringen, brauchst du das Gegenteil: {gegen} {bt}."),
              (-x0, "Fast – schau noch einmal auf das Vorzeichen.")]
    return gleichung(gl, x0, weg, tipps, fehler)


def b1_2_gemischt(r):
    """Bruch und Dezimalzahl gemischt, zwei Zahlen bei x: 3/2 + x - 0,75 = 1/4"""
    k, m = bruch(r, (2, 4)), dezi(r, 1, 40, 4)
    if k == m or m.denominator == 1:
        return None
    x0 = bruch(r, (2, 4)) if r.random() < 0.6 else F(nz(r, -9, 9))
    c = k + x0 - m
    links = f"{z(k)} + x - {dez(m)}"
    gl = f"{links} = {z(c)}" if r.random() < 0.6 else f"{z(c)} = {links}"
    s = k - m
    weg = [gl, f"{term(1, s)} = {z(c)} | zusammenfassen" if gl.startswith(links) else f"{z(c)} = {term(1, s)} | zusammenfassen",
           f"x = {z(x0)} {op('-', s)}"]
    tipps = [f"Fasse zuerst die Zahlen bei x zusammen: `{z(k)} - {dez(m)}`. Tipp: `{dez(m)} = {z(m)}`.",
             f"`{z(k)} - {z(m)} = {z(s)}`. Jetzt steht da `{term(1, s)} = {z(c)}`.",
             f"Rechne auf beiden Seiten {'−' if s > 0 else '+'} `{z(abs(s))}`."]
    fehler = [(c + s, "Um eine Zahl wegzubringen, rechnest du das Gegenteil – das Vorzeichen dreht sich um."),
              (c - k - m, f"Achtung: Vor {dez(m)} steht ein Minus. Zusammengefasst ergibt das {z(k)} − {z(m)}.")]
    return gleichung(gl, x0, weg, tipps, fehler)


# ── B1.3 Mal und Durch ────────────────────────────────────

def b1_3(r, stufe):
    if stufe == 1:
        art = r.choice(["ax", "ax", "x/a"])
        if art == "ax":
            a, x0 = nz(r, -9, 9, (0, 1, -1)), nz(r, -10, 10)
            return mal_aufgabe(a * x0, a, x0, z)
        a = nz(r, 2, 9)
        return durch_aufgabe(a, a * nz(r, -9, 9))
    if stufe == 2:
        art = r.choice(["x/a", "-x", "ax_bruch", "ax_bruch"])
        if art == "x/a":
            a = nz(r, -9, 9, (0, 1, -1))
            return durch_aufgabe(a, a * nz(r, -9, 9))
        if art == "-x":
            x0 = F(r.choice([nz(r, -15, 15), bruch(r)]))
            gl = f"-x = {z(-x0)}"
            return gleichung(gl, x0, [gl, f"x = {z(x0)} {op('·', -1)}"],
                             ["−x bedeutet (−1) · x.", "Multipliziere beide Seiten mit (−1).",
                              "Dabei dreht sich auf beiden Seiten das Vorzeichen um."],
                             [(-x0, "Fast! −x ist noch nicht x. Multipliziere beide Seiten mit (−1).")])
        a, c = nz(r, -8, 8, (0, 1, -1)), nz(r, -30, 30)
        if c % a == 0:
            return None
        return mal_aufgabe(c, a, F(c, a), z)
    if stufe == 3:
        a = r.choice([F(2, 10), F(4, 10), F(5, 10), F(8, 10), F(15, 10), F(25, 10), F(1, 4), F(12, 10), F(3, 4)])
        a *= r.choice([1, 1, -1])
        x0 = F(nz(r, -40, 40), r.choice([1, 2]))
        return mal_aufgabe(a * x0, a, x0, dez)
    # Stufe 4: Bruch als Koeffizient
    a = bruch(r, (2, 3, 4, 5), -7, 7)
    if abs(a.numerator) == 1:
        a = F(r.choice([2, 3, -2, -3, 5]), a.denominator)
        if a.denominator == 1:
            return None
    x0 = F(nz(r, -12, 12), r.choice([1, 1, 2, 3]))
    c = a * x0
    form = r.choice(["bruch_x", "zaehler"])
    gl = (f"{koeff(a)} = {z(c)}" if form == "bruch_x" else
          f"{'-' if a < 0 else ''}{abs(a.numerator)}x/{a.denominator} = {z(c)}")
    kehr = 1 / a
    weg = [gl, f"x = {z(c)} · {kl(kehr)} {op('·', kehr)}", f"x = {z(x0)} | ausrechnen"]
    tipps = [f"`{gl.split('=')[0].strip()}` heißt: x wird mit `{z(a)}` multipliziert.",
             f"Durch einen Bruch dividieren heißt: mit dem Kehrwert multiplizieren. Der Kehrwert von `{z(a)}` ist `{z(kehr)}`.",
             f"Rechne auf beiden Seiten · `{z(kehr)}`."]
    fehler = [(c * a, f"Da wurde mit {z(a)} multipliziert. Du brauchst aber den Kehrwert {z(kehr)}."),
              (-x0, "Fast! Schau noch einmal auf das Vorzeichen.")]
    return gleichung(gl, x0, weg, tipps, fehler)


def mal_aufgabe(c, a, x0, f):
    c, a, x0 = F(c), F(a), F(x0)
    if not (f is z or (endlich(c) and endlich(x0))):
        return None
    gl = f"{koeff(a, f=f)} = {f(c)}"
    weg = [gl, f"x = {(f if endlich(x0) else z)(x0)} {op(':', a, f)}"]
    tipps = [f"`{koeff(a, f=f)}` bedeutet `{f(a)} · x`.",
             f"Das Gegenteil von · {kl(a, f)} ist : {kl(a, f)}.",
             f"Rechne auf beiden Seiten : {kl(a, f)}."
             + (" Das Ergebnis darf ein Bruch sein." if x0.denominator != 1 and not endlich(x0) else "")]
    fehler = [(c * a, f"Da wurde mal {kl(a, f)} gerechnet. Um · {kl(a, f)} wegzubringen, rechnest du : {kl(a, f)}."),
              (c - a, f"`{koeff(a, f=f)}` heißt {f(a)} · x – also Mal, nicht Plus. Darum dividierst du."),
              (-x0, "Fast! Schau noch einmal auf das Vorzeichen: Minus durch Minus ergibt Plus.")]
    return gleichung(gl, x0, weg, tipps, fehler)


def durch_aufgabe(a, x0):
    c = F(x0, a)
    gl = f"x/{a} = {z(c)}" if a > 0 else f"x/({a}) = {z(c)}"
    weg = [gl, f"x = {z(x0)} {op('·', a)}"]
    tipps = [f"x/{kl(a)} bedeutet x : {kl(a)}.", f"Das Gegenteil von : {kl(a)} ist · {kl(a)}.",
             f"Rechne auf beiden Seiten · {kl(a)}."]
    fehler = [(c / a, f"Da wurde durch {kl(a)} dividiert. Um : {kl(a)} wegzubringen, multiplizierst du mit {kl(a)}.")]
    return gleichung(gl, x0, weg, tipps, fehler)


# ── B1.4 Zwei Schritte: ax + b = c ────────────────────────

def b1_4(r, stufe):
    if stufe == 1:
        f, a, b, x0 = z, F(nz(r, -7, 7, (0, 1, -1))), F(nz(r, -15, 15)), F(nz(r, -9, 9))
    elif stufe == 2:
        f, a, b = z, F(nz(r, -9, 9, (0, 1, -1))), F(nz(r, -20, 20))
        x0 = F(nz(r, -19, 19), a) if r.random() < 0.6 else F(nz(r, -12, 12))
    elif stufe == 3:
        f, a, b = dez, dezi(r, -30, 30), dezi(r, -99, 99)
        if a in (1, -1):
            return None
        x0 = F(nz(r, -30, 30), r.choice([1, 2]))
    else:
        f, a, b = z, bruch(r, (2, 3, 4, 5, 6), -9, 9), bruch(r, (2, 3, 4, 6))
        x0 = F(nz(r, -9, 9), r.choice([1, 2, 3]))
    c = a * x0 + b
    if f is dez and not (endlich(c) and endlich(x0)):
        return None
    form = "std" if stufe == 1 else r.choice(["std", "rechts", "b_vorne"])
    if form == "std":
        gl = f"{term(a, b, f=f)} = {f(c)}"
    elif form == "rechts":
        gl = f"{f(c)} = {term(a, b, f=f)}"
    else:
        gl = f"{f(b)} {'+' if a > 0 else '-'} {koeff(abs(a), f=f)} = {f(c)}"
    xt = (f if endlich(x0) else z)(x0)
    weg = [gl, f"{koeff(a, f=f)} = {f(c - b)} {op('-', b, f)}", f"x = {xt} {op(':', a, f)}"]
    if form == "rechts":
        weg = [gl, f"{f(c - b)} = {koeff(a, f=f)} {op('-', b, f)}", f"{xt} = x {op(':', a, f)}",
               f"x = {xt} | Seiten tauschen"]
    vz, gegen = ("+", "−") if b > 0 else ("−", "+")
    bt = f(abs(b))
    tipps = [f"Zwei Schritte: zuerst die {vz} `{bt}` wegbringen, dann das · {kl(a, f)}.",
             f"Rechne auf beiden Seiten {gegen} `{bt}`. Dann steht da `{koeff(a, f=f)} = {f(c - b)}`.",
             f"Jetzt noch auf beiden Seiten : {kl(a, f)}."
             + (" Durch einen Bruch dividieren = mit dem Kehrwert multiplizieren." if stufe == 4 else "")]
    fehler = [((c + b) / a, f"Achtung beim ersten Schritt: Um {vz} {bt} wegzubringen, rechnest du {gegen} {bt}."),
              (c - b, f"Fast! `{koeff(a, f=f)} = {f(c - b)}` stimmt schon. Jetzt fehlt nur noch : {kl(a, f)}."),
              (c / a - b, "Die Reihenfolge ist wichtig: zuerst Plus/Minus wegbringen, erst dann dividieren."),
              ((c - b) * a, "Am Schluss wird dividiert, nicht multipliziert.")]
    return gleichung(gl, x0, weg, tipps, fehler)


# ── B1.5 x auf beiden Seiten ──────────────────────────────

def b1_5(r, stufe):
    if stufe in (1, 2):
        f = z
        a, c = F(nz(r, -7, 7)), F(nz(r, -7, 7))
        b = F(nz(r, -15, 15))
        x0 = F(nz(r, -9, 9)) if stufe == 1 or a == c else F(nz(r, -20, 20), a - c)
    elif stufe == 3:
        f = dez
        a, c, b = dezi(r, -30, 30), dezi(r, -30, 30), dezi(r, -99, 99)
        x0 = F(nz(r, -20, 20), r.choice([1, 2]))
    else:
        f = z
        a, c = bruch(r, (2, 3, 4, 6), -9, 9), r.choice([bruch(r, (2, 3, 4, 6), -9, 9), F(nz(r, -3, 3))])
        b = bruch(r, (2, 3, 4, 6))
        x0 = F(nz(r, -12, 12), r.choice([1, 2, 3]))
    if a == c or a == 0 or c == 0:
        return None
    d = (a - c) * x0 + b
    if f is dez and not endlich(d):
        return None
    gl = f"{term(a, b, f=f)} = {term(c, d, f=f)}"
    weg = [gl] + loese(a, b, c, d, f)
    xs = koeff(abs(c), f=f)
    tipps = ["Bring zuerst alle x auf eine Seite und alle Zahlen auf die andere.",
             f"Rechne auf beiden Seiten {'−' if c > 0 else '+'}`{xs}`. Dann ist rechts kein x mehr.",
             f"Danach steht da `{term(a - c, b, f=f)} = {f(d)}`. Das löst du wie vorher in zwei Schritten."]
    return gleichung(gl, x0, weg, tipps, lin_fehler(a, b, c, d))


# ── B1.6 Klammern ─────────────────────────────────────────

def b1_6(r, stufe):
    if stufe == 1:  # a(x + b) = cx + d
        a, b, c = nz(r, -6, 6, (0, 1, -1)), nz(r, -8, 8), nz(r, -5, 5)
        x0 = nz(r, -8, 8)
        if c == a:
            return None
        d = a * (x0 + b) - c * x0
        gl = f"{a}({term(1, b)}) = {term(c, d)}"
        weg = [gl, f"{term(a, a * b)} = {term(c, d)} | ausmultiplizieren"] + loese(a, a * b, c, d)
        tipps = [f"Löse zuerst die Klammer auf: {kl(a)} · x und {kl(a)} · {kl(b)}.",
                 f"`{a}({term(1, b)}) = {term(a, a * b)}`. Achte auf die Vorzeichen!",
                 "Dann alle x auf eine Seite, alle Zahlen auf die andere."]
        fehler = [(F(d - b, a - c), "Beim Ausmultiplizieren muss die Zahl vor der Klammer mit jedem Glied "
                                    "in der Klammer multipliziert werden.")] + lin_fehler(a, a * b, c, d)
        return gleichung(gl, x0, weg, tipps, fehler)

    if stufe == 2:  # Minus vor der Klammer: ax + b − (cx + e) = g
        a, b, c, e = nz(r, -7, 7), nz(r, -9, 9), nz(r, -5, 5), nz(r, -9, 9)
        x0 = nz(r, -9, 9)
        if a == c:
            return None
        g = (a - c) * x0 + b - e
        gl = f"{term(a, b)} - ({term(c, e)}) = {g}"
        weg = [gl, f"{glieder([(a, 'x'), (b, ''), (-c, 'x'), (-e, '')])} = {g} | Minus vor der Klammer",
               f"{term(a - c, b - e)} = {g} | zusammenfassen"] + loese(a - c, b - e, 0, g)
        tipps = ["Ein Minus vor der Klammer dreht beim Auflösen jedes Vorzeichen in der Klammer um.",
                 f"`-({term(c, e)})` wird zu `{glieder([(-c, 'x'), (-e, '')])}`.",
                 "Dann fasst du die x-Glieder und die Zahlen zusammen."]
        fehler = [(F(g - b - e, a - c), "Beim Minus vor der Klammer muss auch das Vorzeichen der Zahl in der Klammer "
                                        "umgedreht werden."),
                  (F(g - b + e, a + c) if a + c else None, "Beim Minus vor der Klammer dreht sich auch das Vorzeichen vor dem x um.")]
        return gleichung(gl, x0, weg, tipps, fehler)

    if stufe == 3:  # a(px + b) − c(qx + e) = g
        a, p, b = nz(r, 2, 5), nz(r, 1, 3), nz(r, -9, 9)
        c, q, e = nz(r, 2, 4), nz(r, 1, 3), nz(r, -9, 9)
        A, B = a * p - c * q, a * b - c * e
        if A == 0:
            return None
        x0 = nz(r, -8, 8)
        g = A * x0 + B
        gl = f"{a}({term(p, b)}) - {c}({term(q, e)}) = {g}"
        weg = [gl, f"{glieder([(a * p, 'x'), (a * b, ''), (-c * q, 'x'), (-c * e, '')])} = {g} | ausmultiplizieren",
               f"{term(A, B)} = {g} | zusammenfassen"] + loese(A, B, 0, g)
        tipps = ["Löse beide Klammern auf. Bei der zweiten gehört das Minus zur Zahl davor: Du multiplizierst mit (−"
                 f"{c}).",
                 f"`-{c}({term(q, e)}) = {glieder([(-c * q, 'x'), (-c * e, '')])}`.",
                 f"Zusammengefasst steht da `{term(A, B)} = {g}`."]
        fehler = [(F(g - (a * b + c * e), A), f"Beim Auflösen von −{c}(…) dreht sich das Vorzeichen jedes Glieds um – "
                                              "auch das der Zahl.")] + lin_fehler(A, B, 0, g)
        return gleichung(gl, x0, weg, tipps, fehler)

    # Stufe 4: a(px + b) − (qx + e) = d(x + h)
    a, p, b = nz(r, -4, 5, (0, 1, -1)), nz(r, 1, 4), nz(r, -6, 6)
    q, e = nz(r, -5, 5), nz(r, -9, 9)
    d, h = nz(r, -4, 4, (0, 1)), nz(r, -6, 6)
    A, B, C, D = a * p - q, a * b - e, d, d * h
    if A == C:
        return None
    x0 = F(D - B, A - C)
    if x0.denominator > 4 or abs(x0) > 15:
        return None
    gl = f"{a}({term(p, b)}) - ({term(q, e)}) = {d}({term(1, h)})"
    weg = [gl, f"{glieder([(a * p, 'x'), (a * b, ''), (-q, 'x'), (-e, '')])} = {term(d, d * h)} | ausmultiplizieren",
           f"{term(A, B)} = {term(C, D)} | zusammenfassen"] + loese(A, B, C, D)
    tipps = ["Zuerst alle Klammern auflösen – links und rechts. Achtung beim Minus vor der Klammer!",
             f"Links: `{glieder([(a * p, 'x'), (a * b, ''), (-q, 'x'), (-e, '')])}`, rechts: `{term(d, d * h)}`.",
             f"Zusammengefasst: `{term(A, B)} = {term(C, D)}`. Das Ergebnis darf ein Bruch sein."]
    fehler = [(F(D - (a * b + e), A - C), "Beim Minus vor der Klammer dreht sich auch das Vorzeichen der Zahl um."),
              (F(d * h - B, A - d) if h and A != d else None, "Rechts muss die Zahl vor der Klammer mit beiden Gliedern "
                                                              "multipliziert werden.")] + lin_fehler(A, B, C, D)
    return gleichung(gl, x0, weg, tipps, fehler)


# ── B1.7 Brüche ───────────────────────────────────────────

def b1_7(r, stufe):
    if stufe == 1:
        if r.random() < 0.5:  # x/a + x/b = c
            a, b = r.choice([(2, 3), (2, 5), (3, 4), (3, 6), (2, 4), (4, 6), (5, 10), (3, 5)])
            hn = kgv(a, b)
            x0 = hn * nz(r, -5, 5)
            c = F(x0, a) + F(x0, b)
            gl = f"x/{a} + x/{b} = {z(c)}"
            weg = [gl, f"{hn // a}x + {hn // b}x = {z(c * hn)} {op('·', hn)}",
                   f"{hn // a + hn // b}x = {z(c * hn)} | zusammenfassen", f"x = {x0} {op(':', hn // a + hn // b)}"]
            tipps = [f"Suche den Hauptnenner von {a} und {b}: die kleinste Zahl, die durch beide teilbar ist.",
                     f"Der Hauptnenner ist {hn}. Multipliziere JEDES Glied mit {hn} – auch die rechte Seite!",
                     f"`x/{a} · {hn} = {hn // a}x` und `x/{b} · {hn} = {hn // b}x`."]
            fehler = [(F(c, hn // a + hn // b), f"Beim Multiplizieren mit {hn} muss auch die rechte Seite mal {hn} gerechnet werden.")]
            return gleichung(gl, x0, weg, tipps, fehler)
        a, b = nz(r, 2, 7), nz(r, -9, 9)  # (x + b)/a = c
        c = nz(r, -8, 8)
        x0 = c * a - b
        gl = f"({term(1, b)})/{a} = {c}"
        weg = [gl, f"{term(1, b)} = {c * a} {op('·', a)}", f"x = {x0} {op('-', b)}"]
        tipps = [f"Der Bruchstrich wirkt wie eine Klammer um `{term(1, b)}`.",
                 f"Multipliziere beide Seiten mit {a}. Dann ist der Bruch weg.", f"Jetzt steht da `{term(1, b)} = {c * a}`."]
        fehler = [(c - b, f"Zuerst den Bruch wegbringen: beide Seiten mal {a}."),
                  (c * a + b, f"Um {'+' if b > 0 else '−'} {abs(b)} wegzubringen, rechnest du das Gegenteil.")]
        return gleichung(gl, x0, weg, tipps, fehler)

    if stufe == 2:  # (x + a)/b = (x + c)/d
        b, d = r.choice([(2, 3), (3, 4), (2, 5), (4, 3), (3, 2), (5, 2), (4, 6), (6, 4)])
        a, c = nz(r, -8, 8), nz(r, -8, 8)
        hn = kgv(b, d)
        pb, pd = hn // b, hn // d
        x0 = F(pd * c - pb * a, pb - pd)
        if x0.denominator != 1 or x0 == 0 or abs(x0) > 30:
            return None
        gl = f"({term(1, a)})/{b} = ({term(1, c)})/{d}"
        weg = [gl, f"{pb}({term(1, a)}) = {pd}({term(1, c)}) {op('·', hn)}",
               f"{term(pb, pb * a)} = {term(pd, pd * c)} | ausmultiplizieren"] + loese(pb, pb * a, pd, pd * c)
        tipps = [f"Multipliziere beide Seiten mit dem Hauptnenner {hn}.",
                 f"Links bleibt `{pb}({term(1, a)})`, rechts `{pd}({term(1, c)})`. Die Bruchstriche sind weg!",
                 "Jetzt Klammern auflösen und wie gewohnt weiterrechnen."]
        fehler = [(F(d * c - b * a, b - d), f"Achtung, über Kreuz: Beim Multiplizieren mit {hn} bleibt links "
                                            f"{pb}({term(1, a)}) und rechts {pd}({term(1, c)}) – nicht umgekehrt.")]
        return gleichung(gl, x0, weg, tipps, fehler)

    if stufe == 3:  # (x + a)/b − (x + c)/d = e   – Minus vor dem Bruch
        b, d = r.choice([(2, 3), (3, 4), (2, 5), (4, 3), (3, 2), (6, 4), (4, 6), (3, 6), (6, 3)])
        a, c, e = nz(r, -8, 8), nz(r, -8, 8), nz(r, -5, 5)
        hn = kgv(b, d)
        pb, pd = hn // b, hn // d
        A, B = pb - pd, pb * a - pd * c
        if A == 0:
            return None
        x0 = F(hn * e - B, A)
        if x0.denominator != 1 or x0 == 0 or abs(x0) > 30:
            return None
        gl = f"({term(1, a)})/{b} - ({term(1, c)})/{d} = {e}"
        weg = [gl, f"{mal(pb, term(1, a))} {mal(pd, term(1, c), False)} = {hn * e} {op('·', hn)}",
               f"{glieder([(pb, 'x'), (pb * a, ''), (-pd, 'x'), (-pd * c, '')])} = {hn * e} | ausmultiplizieren",
               f"{term(A, B)} = {hn * e} | zusammenfassen"] + loese(A, B, 0, hn * e)
        tipps = [f"Multipliziere JEDES Glied mit dem Hauptnenner {hn} – auch die {e} rechts.",
                 f"Das Minus vor dem zweiten Bruch gilt für den ganzen Zähler: `{mal(pd, term(1, c), False)}`.",
                 f"Aufgelöst: `{glieder([(pb, 'x'), (pb * a, ''), (-pd, 'x'), (-pd * c, '')])} = {hn * e}`."]
        fehler = [(F(hn * e - (pb * a + pd * c), A), "Das Minus vor dem Bruch gilt für den ganzen Zähler – "
                                                     "auch das Vorzeichen der Zahl dreht sich um."),
                  (F(e - B, A), f"Auch die rechte Seite muss mit {hn} multipliziert werden.")]
        return gleichung(gl, x0, weg, tipps, fehler)

    # Stufe 4: (px + a)/b − (qx + c)/d = (x + h)/g
    b, d, g = r.sample([2, 3, 4, 6], 3)
    p, q = nz(r, 1, 3), nz(r, 1, 3)
    a, c, h = nz(r, -7, 7), nz(r, -7, 7), nz(r, -7, 7)
    hn = kgv(b, d, g)
    pb, pd, pg = hn // b, hn // d, hn // g
    A, B, C, D = pb * p - pd * q, pb * a - pd * c, pg, pg * h
    if A == C:
        return None
    x0 = F(D - B, A - C)
    if x0.denominator > 3 or x0 == 0 or abs(x0) > 20:
        return None
    gl = f"({term(p, a)})/{b} - ({term(q, c)})/{d} = ({term(1, h)})/{g}"
    weg = [gl, f"{mal(pb, term(p, a))} {mal(pd, term(q, c), False)} = {mal(pg, term(1, h))} {op('·', hn)}",
           f"{glieder([(pb * p, 'x'), (pb * a, ''), (-pd * q, 'x'), (-pd * c, '')])} = {term(pg, pg * h)} | ausmultiplizieren",
           f"{term(A, B)} = {term(C, D)} | zusammenfassen"] + loese(A, B, C, D)
    tipps = [f"Der Hauptnenner von {b}, {d} und {g} ist {hn}. Multipliziere jedes Glied damit.",
             f"Es bleibt `{mal(pb, term(p, a))} {mal(pd, term(q, c), False)} = {mal(pg, term(1, h))}`.",
             f"Klammern auflösen, zusammenfassen: `{term(A, B)} = {term(C, D)}`."]
    fehler = [(F(D - (pb * a + pd * c), A - C), "Das Minus vor dem Bruch gilt für den ganzen Zähler – "
                                                "auch das Vorzeichen der Zahl dreht sich um.")] + lin_fehler(A, B, C, D)
    return gleichung(gl, x0, weg, tipps, fehler)


# ── B1.8 Sonderfälle ──────────────────────────────────────

OPTIONEN = ["genau eine Lösung", "keine Lösung", "unendlich viele Lösungen"]
ERK = {
    0: "Nach dem Vereinfachen bleibt ein x übrig – also gibt es genau eine Lösung.",
    1: "Nach dem Vereinfachen fällt das x weg, und übrig bleibt eine falsche Aussage (z. B. 3 = 5). "
       "Das stimmt nie – also keine Lösung: L = { }.",
    2: "Nach dem Vereinfachen steht links genau dasselbe wie rechts. Das stimmt für jede Zahl – "
       "also unendlich viele Lösungen: L = ℝ.",
}


def b1_8(r, stufe):
    fall = r.choice([0, 1, 2])
    a, b, d = nz(r, -6, 6, (0,)), nz(r, -9, 9), nz(r, -9, 9)
    if stufe == 1:
        if fall == 0:
            gl = f"{term(a, b)} = {term(a + nz(r, -3, 3), d)}"
        elif fall == 1:
            if d == b:
                return None
            gl = f"{term(a, b)} = {term(a, d)}"
        else:
            k = nz(r, 2, 4)
            gl = f"{k}({term(a, b)}) = {term(k * a, k * b)}"
    elif stufe == 2:
        e = nz(r, 1, 5)
        if fall == 0:
            gl = f"{a}({term(1, b)}) = {term(a + nz(r, -2, 2), d)}"
        elif fall == 1:
            gl = f"{a}({term(1, -e)}) = {term(a, -a * e + nz(r, -5, 5))}"
        else:
            gl = f"{term(a + 2, 2 * e)} - 2({term(1, -e)}) = {term(a, 4 * e)}"
    elif stufe == 3:
        k = nz(r, 2, 5)
        if fall == 0:
            gl = f"x/{k} {vz(b)} = x/{k + nz(r, 1, 3)} {vz(d)}"
        elif fall == 1:
            if b == k * d:
                return None
            gl = f"({term(k, b)})/{k} = {term(1, d)}"
        else:
            gl = r.choice([f"({term(k, k * d)})/{k} = {term(1, d)}", f"x/{k} {vz(d)} = ({term(1, k * d)})/{k}"])
    else:
        if fall == 2:
            a1, c1 = nz(r, 2, 5), nz(r, 1, 4)
            e = a1 - c1
            if e == 0:
                return None
            b1, f1 = nz(r, -5, 5), nz(r, -5, 5)
            d1 = a1 * b1 - e * f1
            if d1 == 0:
                return None
            gl = f"{a1}({term(1, -b1)}) - ({term(c1, -d1)}) = {mal(e, term(1, -f1)) if e != -1 else '-(' + term(1, -f1) + ')'}"
        else:
            p, q = 2 * nz(r, 1, 4), 2 * nz(r, -5, 5)
            m = r.choice([F(1, 2), F(3, 2)])
            links = f"{dez(m)}({term(p, q)})"
            if fall == 0:
                gl = f"{links} = {term(m * p + nz(r, -2, 2), nz(r, -9, 9))}"
            else:
                gl = f"{links} = {term(m * p, m * q + nz(r, -3, 3))}"
    return {"typ": "auswahl", "frage": f"Wie viele Lösungen hat die Gleichung `{gl}`?",
            "optionen": OPTIONEN, "richtig": [fall], "erklaerung": ERK[fall],
            "pruefung": {"art": "anzahl", "gleichung": gl},
            "tipps": ["Vereinfache die Gleichung so weit wie möglich: Klammern auflösen, Brüche wegbringen.",
                      "Bring alle x auf eine Seite. Bleibt ein x übrig – oder verschwindet es?"]}



def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ZIEL.mkdir(parents=True, exist_ok=True)
    r = random.Random(20261015)
    for lid, fn in [("B1.1", b1_1), ("B1.2", b1_2), ("B1.3", b1_3), ("B1.4", b1_4),
                    ("B1.5", b1_5), ("B1.6", b1_6), ("B1.7", b1_7), ("B1.8", b1_8)]:
        aufgaben = erzeuge(lid, r, fn, 9 if lid == "B1.8" else PRO_STUFE)
        kopf = (f"# ERZEUGT von tools/generatoren/b1.py – nicht von Hand bearbeiten.\n"
                f"# Geprüft wird beim Build (tools/build.py) mit sympy.\n")
        text = yaml.safe_dump(aufgaben, allow_unicode=True, sort_keys=False, width=200)
        (ZIEL / f"{lid}.aufgaben.yaml").write_text(kopf + text, encoding="utf-8")
        print(f"{lid}: {len(aufgaben)} Aufgaben")


if __name__ == "__main__":
    main()
