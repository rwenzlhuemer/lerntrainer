"""
Generator für Kapitel B1 (Lineare Gleichungen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/b1.py

Schreibt inhalte/mathe/B1/B1.x.aufgaben.yaml. Fester Zufalls-Startwert → reproduzierbar.
Die Richtigkeit prüft unabhängig davon tools/build.py mit sympy.
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

import yaml

ZIEL = Path(__file__).resolve().parents[2] / "inhalte" / "mathe" / "B1"


# ── Formatierung ──────────────────────────────────────────

def z(q) -> str:
    """Zahl in Schulnotation: 5, -3, 5/2 (Brüche), 2,5 nur wenn als Dezimalzahl gegeben."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def dez(q) -> str:
    """Dezimalzahl mit Komma, nur für endliche Dezimalbrüche."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    s = f"{float(q):.4f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def anzeige(q) -> str:
    """Lösung lesbar: 5/2 = 2,5 – Dezimalform nur, wenn sie endet."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    d = q.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return f"{z(q)} = {dez(q)}" if d == 1 else z(q)


def term(a, b=0, var="x") -> str:
    """a·x + b als Text: 3x - 5, -x + 2, x, 7"""
    a, b = F(a), F(b)
    teile = []
    if a != 0:
        if a == 1:
            teile.append(var)
        elif a == -1:
            teile.append(f"-{var}")
        else:
            teile.append(f"{z(a)}{var}" if a.denominator == 1 else f"{z(a)}·{var}")
    if b != 0 or not teile:
        if teile:
            teile.append(f"+ {z(b)}" if b > 0 else f"- {z(-b)}")
        else:
            teile.append(z(b))
    return " ".join(teile)


def op(zeichen: str, q) -> str:
    """Kommentar zur Umformung: | −5, | +3, | :3, | ·2"""
    q = F(q)
    if zeichen in "+-":
        if q < 0:
            zeichen, q = ("-" if zeichen == "+" else "+"), -q
        return f"| {'−' if zeichen == '-' else '+'}{z(q)}"
    if zeichen == ":":
        return f"| :{z(q)}" if q > 0 else f"| :({z(q).replace('-', '−')})"
    if zeichen == "·":
        return f"| ·{z(q)}" if q > 0 else f"| ·({z(q).replace('-', '−')})"
    raise ValueError(zeichen)


def opx(q) -> str:
    """| −3x bzw. | +3x"""
    q = F(q)
    t = "x" if abs(q) == 1 else f"{z(abs(q))}x"
    return f"| −{t}" if q > 0 else f"| +{t}"


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


def nz(r, lo, hi, ohne=(0,)):
    while True:
        v = r.randint(lo, hi)
        if v not in ohne:
            return v


def aufgabe(lid, nr, stufe, gleichung, loesung, weg, tipps, fehler=(), **extra):
    a = {"id": f"{lid}-{nr:03d}", "typ": "gleichung", "stufe": stufe, "gleichung": gleichung,
         "loesung": z(loesung), "anzeige": anzeige(loesung), "weg": weg, "tipps": tipps}
    f = fehlerliste(loesung, fehler)
    if f:
        a["fehler"] = f
    a.update(extra)
    return a


# ── B1.1 Probe: Ist das eine Lösung? ──────────────────────

def b1_1(r):
    lid, aus, nr = "B1.1", [], 0
    for stufe, n in ((1, 8), (2, 8), (3, 6)):
        for i in range(n):
            nr += 1
            x0 = nz(r, -6 if stufe > 1 else 1, 9)
            if stufe == 1:
                b = nz(r, 1, 9)
                gl, links = f"x + {b} = {x0 + b}", lambda v: v + b
                probe = lambda v: f"{z(v)} + {b}"
                rechts = x0 + b
            elif stufe == 2:
                a, b = nz(r, 2, 6), nz(r, -9, 9)
                rechts = a * x0 + b
                gl = f"{term(a, b)} = {rechts}"
                links = lambda v, a=a, b=b: a * v + b
                probe = lambda v, a=a, b=b: f"{a} · {klammer(v)} {'+' if b > 0 else '−'} {abs(b)}"
            else:
                a, b, c = nz(r, 2, 6), nz(r, -9, 9), nz(r, 1, 4)
                if a == c:
                    a += 1
                d = a * x0 + b - c * x0
                gl = f"{term(a, b)} = {term(c, d)}"
                links = lambda v, a=a, b=b: a * v + b
                rechts_f = lambda v, c=c, d=d: c * v + d
                probe = None
            ja = r.random() < 0.5
            wert = x0 if ja else x0 + r.choice([-2, -1, 1, 2])
            if stufe < 3:
                lw, rw = links(wert), rechts
                erk = f"Probe: `{probe(wert)} = {lw}`. " + (
                    f"Das ist genau {rw} ✓ – also ja, x = {wert} ist eine Lösung."
                    if lw == rw else f"Das ist nicht {rw} – also ist x = {wert} keine Lösung.")
            else:
                lw, rw = links(wert), rechts_f(wert)
                erk = (f"Setze x = {wert} links und rechts ein. Links kommt {lw} heraus, rechts {rw}. "
                       + ("Beide Seiten sind gleich ✓ – also ja." if lw == rw
                          else "Die Seiten sind verschieden – also keine Lösung."))
            aus.append({
                "id": f"{lid}-{nr:03d}", "typ": "auswahl", "stufe": stufe,
                "frage": f"Ist x = {wert} eine Lösung der Gleichung `{gl}`?",
                "optionen": ["Ja", "Nein"], "richtig": [0 if links(wert) == (rechts if stufe < 3 else rechts_f(wert)) else 1],
                "erklaerung": erk,
                "pruefung": {"art": "einsetzen", "gleichung": gl, "wert": str(wert)},
                "tipps": ["Setze die Zahl statt x ein und rechne beide Seiten aus.",
                          "Wenn links und rechts dasselbe herauskommt, ist es eine Lösung."],
            })
    return aus


def klammer(v):
    return f"({v})" if v < 0 else str(v)


# ── B1.2 Plus und Minus ───────────────────────────────────

def b1_2(r):
    lid, aus = "B1.2", []
    for nr in range(1, 29):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        if stufe == 1:
            x0, b = nz(r, 1, 15), nz(r, 1, 12)
        elif stufe == 2:
            x0, b = nz(r, -12, 15), nz(r, -12, 12)
        else:
            x0, b = F(nz(r, -40, 40), 2), F(nz(r, -30, 30), 2)
        c = x0 + b
        form = r.choice(["xb", "bx", "cxb"]) if stufe > 1 else "xb"
        links = {"xb": term(1, b), "bx": f"{z(b)} + x" if b > 0 else f"{z(b)} + x",
                 "cxb": term(1, b)}[form]
        if stufe == 3:
            links = links.replace(z(abs(b)), dez(abs(b)))
            c_txt = dez(c)
        else:
            c_txt = z(c)
        gl = f"{c_txt} = {links}" if form == "cxb" else f"{links} = {c_txt}"
        b_txt = dez(abs(b)) if stufe == 3 else z(abs(b))
        weg_x = f"x = {dez(x0) if stufe == 3 else z(x0)}"
        weg = [gl, f"{weg_x} {op('-', b)}"]
        vz = "+" if b > 0 else "−"
        gegen = "−" if b > 0 else "+"
        tipps = [
            "Ziel: x soll ganz allein auf einer Seite stehen. Was steht noch bei x?",
            f"Bei x steht {vz} {b_txt}. Das Gegenteil davon ist {gegen} {b_txt}.",
            f"Rechne auf beiden Seiten {gegen} {b_txt}. Dann steht x allein da.",
        ]
        fehler = [(c + b, f"Da wurde vermutlich {vz} {b_txt} gerechnet statt {gegen} {b_txt}. "
                          f"Um {vz} {b_txt} wegzubringen, brauchst du das Gegenteil: {gegen} {b_txt}."),
                  (-x0, "Fast – schau noch einmal auf das Vorzeichen.")]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.3 Mal und Durch ────────────────────────────────────

def b1_3(r):
    lid, aus = "B1.3", []
    for nr in range(1, 29):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        art = r.choice(["ax", "ax", "x/a"] if stufe < 3 else ["ax", "x/a", "-x", "ax_bruch"])
        if art == "ax":
            a = nz(r, 2, 9) if stufe == 1 else nz(r, -9, 9, (0, 1, -1))
            x0 = nz(r, 1, 10) if stufe == 1 else nz(r, -10, 10)
            c = a * x0
            gl = f"{term(a)} = {c}"
            weg = [gl, f"x = {z(x0)} {op(':', a)}"]
            tipps = [f"{term(a)} bedeutet {a} · x.",
                     f"Das Gegenteil von · {klammer(a)} ist : {klammer(a)}.",
                     f"Rechne auf beiden Seiten : {klammer(a)}: x = {c} : {klammer(a)}."]
            fehler = [(F(c) * a, f"Da wurde mal {klammer(a)} gerechnet. Um · {klammer(a)} wegzubringen, "
                                 f"rechnest du : {klammer(a)}."),
                      (c - a, f"{term(a)} heißt {a} · x – also Mal, nicht Plus. Darum dividierst du durch {klammer(a)}."),
                      (-x0, "Fast! Schau noch einmal auf das Vorzeichen: Minus durch Minus ergibt Plus.")]
        elif art == "x/a":
            a = nz(r, 2, 9) if stufe < 3 else nz(r, -9, 9, (0, 1, -1))
            x0 = a * (nz(r, 1, 9) if stufe == 1 else nz(r, -9, 9))
            c = F(x0, a)
            gl = f"x/{a} = {z(c)}" if a > 0 else f"x/({a}) = {z(c)}"
            weg = [gl, f"x = {z(x0)} {op('·', a)}"]
            tipps = [f"x/{klammer(a)} bedeutet x : {klammer(a)}.",
                     f"Das Gegenteil von : {klammer(a)} ist · {klammer(a)}.",
                     f"Rechne auf beiden Seiten · {klammer(a)}."]
            fehler = [(c / a, f"Da wurde durch {klammer(a)} dividiert. Um : {klammer(a)} wegzubringen, "
                              f"multiplizierst du mit {klammer(a)}.")]
        elif art == "-x":
            x0 = nz(r, -12, 12)
            gl = f"-x = {z(-x0)}"
            weg = [gl, f"x = {z(x0)} {op('·', -1)}"]
            tipps = ["−x bedeutet (−1) · x.", "Multipliziere beide Seiten mit (−1).",
                     "Dabei dreht sich auf beiden Seiten das Vorzeichen um."]
            fehler = [(-x0, "Fast! −x ist noch nicht x. Multipliziere beide Seiten mit (−1).")]
        else:  # ax_bruch: Lösung ist ein Bruch
            a = nz(r, 2, 8)
            c = nz(r, 1, 30)
            while c % a == 0:
                c += 1
            x0 = F(c, a)
            gl = f"{a}x = {c}"
            weg = [gl, f"x = {z(x0)} {op(':', a)}"]
            tipps = [f"Rechne auf beiden Seiten : {a}.",
                     f"{c} : {a} geht nicht glatt auf – das macht nichts!",
                     f"Du darfst das Ergebnis als Bruch schreiben: x = {c}/{a}."]
            fehler = [(F(c * a), f"Um · {a} wegzubringen, rechnest du : {a}, nicht · {a}."),
                      (F(a, c), f"Achtung, umgekehrt: Es ist {c} : {a}, also {c}/{a}.")]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.4 Zwei Schritte: ax + b = c ────────────────────────

def b1_4(r):
    lid, aus = "B1.4", []
    for nr in range(1, 31):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        a = nz(r, 2, 6) if stufe == 1 else nz(r, -7, 7, (0, 1, -1))
        x0 = nz(r, 1, 9) if stufe == 1 else nz(r, -9, 9)
        b = nz(r, 1, 15) if stufe == 1 else nz(r, -15, 15)
        if stufe == 3 and r.random() < 0.4:
            x0 = F(nz(r, -19, 19, (0,)), a)  # Bruch-Lösung möglich
        c = a * x0 + b
        form = "std" if stufe < 3 else r.choice(["std", "rechts", "b_vorne"])
        if form == "std":
            gl = f"{term(a, b)} = {z(c)}"
        elif form == "rechts":
            gl = f"{z(c)} = {term(a, b)}"
        else:
            gl = f"{z(b)} {'+' if a > 0 else '-'} {z(abs(a))}x = {z(c)}"
        weg = [gl, f"{term(a)} = {z(c - b)} {op('-', b)}", f"x = {z(x0)} {op(':', a)}"]
        if form == "rechts":
            weg[1] = f"{z(c - b)} = {term(a)} {op('-', b)}"
            weg.append(f"x = {z(x0)} | Seiten tauschen")
            weg[2] = f"{z(x0)} = x {op(':', a)}"
        vz, gegen = ("+", "−") if b > 0 else ("−", "+")
        tipps = [
            f"Zwei Schritte: zuerst die {vz} {abs(b)} wegbringen, dann das · {klammer(a)}.",
            f"Rechne auf beiden Seiten {gegen} {abs(b)}. Dann steht da {term(a)} = {z(c - b)}.",
            f"Jetzt noch auf beiden Seiten : {klammer(a)}.",
        ]
        fehler = [
            (F(c + b, a), f"Achtung beim ersten Schritt: Um {vz} {abs(b)} wegzubringen, rechnest du {gegen} {abs(b)}."),
            (c - b, f"Fast! {term(a)} = {z(c - b)} stimmt schon. Jetzt fehlt nur noch : {klammer(a)}."),
            (F(c, a) - b, "Die Reihenfolge ist wichtig: zuerst Plus/Minus wegbringen, erst dann dividieren."),
        ]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.5 x auf beiden Seiten ──────────────────────────────

def b1_5(r):
    lid, aus = "B1.5", []
    for nr in range(1, 29):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        if stufe == 1:
            c = nz(r, 1, 4)
            a = c + nz(r, 1, 4)        # a > c: x-Glied bleibt links positiv
            x0 = nz(r, 1, 8)
        else:
            a, c = nz(r, -6, 7), nz(r, -6, 7)
            while a == c:
                c = nz(r, -6, 7)
            x0 = nz(r, -8, 8)
            if stufe == 3 and r.random() < 0.3:
                x0 = F(nz(r, -15, 15), a - c)
        b = nz(r, -12, 12)
        d = a * x0 + b - c * x0
        if F(d).denominator != 1:
            d = F(d)
        gl = f"{term(a, b)} = {term(c, d)}"
        k = a - c
        weg = [gl,
               f"{term(k, b)} = {z(d)} {opx(c)}",
               f"{term(k)} = {z(d - b)} {op('-', b)}",
               f"x = {z(x0)} {op(':', k)}"]
        xs = "x" if abs(c) == 1 else f"{abs(c)}x"
        tipps = [
            "Bring zuerst alle x auf eine Seite und alle Zahlen auf die andere.",
            f"Rechne auf beiden Seiten {'−' if c > 0 else '+'}{xs}. Dann ist rechts kein x mehr.",
            f"Danach steht da {term(k, b)} = {z(d)}. Das löst du wie vorher in zwei Schritten.",
        ]
        fehler = [
            (F(d - b, a + c) if a + c else None, f"Beim Hinüberbringen von {term(c)}: Auf der anderen Seite wird daraus "
                              f"{'−' if c > 0 else '+'}{xs}, nicht {'+' if c > 0 else '−'}{xs}."),
            (F(d + b, k), "Achtung beim Wegbringen der Zahl links – das Vorzeichen dreht sich um."),
        ]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.6 Klammern ─────────────────────────────────────────

def b1_6(r):
    lid, aus = "B1.6", []
    for nr in range(1, 29):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        if stufe == 1:  # a(x + b) = c
            a, b, x0 = nz(r, 2, 5), nz(r, -6, 6), nz(r, 1, 8)
            c = a * (x0 + b)
            gl = f"{a}({term(1, b)}) = {c}"
            weg = [gl, f"{term(a, a * b)} = {c} | ausmultiplizieren",
                   f"{term(a)} = {c - a * b} {op('-', a * b)}", f"x = {x0} {op(':', a)}"]
            tipps = [f"Löse zuerst die Klammer auf: {a} mal x und {a} mal {klammer(b)}.",
                     f"{a}({term(1, b)}) = {term(a, a * b)}.",
                     f"Jetzt hast du {term(a, a * b)} = {c} – das kennst du schon."]
            fehler = [(F(c - b, a), f"Beim Ausmultiplizieren muss die {a} mit beiden Gliedern in der Klammer "
                                    f"multipliziert werden – auch mit {klammer(b)}."),
                      (F(c, a) + b, "Fast – schau noch einmal auf das Vorzeichen der Zahl in der Klammer.")]
        elif stufe == 2:  # a(x + b) = cx + d
            a, b = nz(r, -5, 5, (0, 1)), nz(r, -6, 6)
            c = nz(r, -4, 4)
            while c == a:
                c = nz(r, -4, 4)
            x0 = nz(r, -7, 7)
            d = a * (x0 + b) - c * x0
            gl = f"{a}({term(1, b)}) = {term(c, d)}"
            k = a - c
            weg = [gl, f"{term(a, a * b)} = {term(c, d)} | ausmultiplizieren",
                   f"{term(k, a * b)} = {z(d)} {opx(c)}" if c else f"{term(k, a * b)} = {z(d)}",
                   f"{term(k)} = {z(d - a * b)} {op('-', a * b)}", f"x = {z(x0)} {op(':', k)}"]
            if not c:
                weg.pop(2)
            tipps = ["Zuerst die Klammer auflösen (ausmultiplizieren).",
                     f"{gl.split('=')[0].strip()} = {term(a, a * b)}. Achte auf die Vorzeichen!",
                     "Dann alle x auf eine Seite, alle Zahlen auf die andere."]
            fehler = [(F(d - b, k) if k else None, "Beim Ausmultiplizieren: Die Zahl vor der Klammer gehört "
                                                    "mit jedem Glied in der Klammer multipliziert.")]
        else:  # Minus vor der Klammer: a·x + b − (c·x + e) = f
            a, b = nz(r, 2, 7), nz(r, -9, 9)
            c, e = nz(r, 1, 5), nz(r, -9, 9)
            while c == a:
                c = nz(r, 1, 5)
            x0 = nz(r, -6, 8)
            f = a * x0 + b - (c * x0 + e)
            gl = f"{term(a, b)} - ({term(c, e)}) = {f}"
            k = a - c
            aufgeloest = f"{term(a, b)} - {term(c).lstrip('-')} {'-' if e > 0 else '+'} {abs(e)}"
            weg = [gl, f"{aufgeloest} = {f} | Minus vor der Klammer",
                   f"{term(k, b - e)} = {f} | zusammenfassen",
                   f"{term(k)} = {f - (b - e)} {op('-', b - e)}", f"x = {z(x0)} {op(':', k)}"]
            tipps = ["Ein Minus vor der Klammer dreht beim Auflösen jedes Vorzeichen in der Klammer um.",
                     f"−({term(c, e)}) wird zu {('−' + term(c).lstrip('-'))} {'−' if e > 0 else '+'} {abs(e)}.",
                     "Dann fasst du die x-Glieder und die Zahlen zusammen."]
            fehler = [(F(f - b - e, k), f"Beim Minus vor der Klammer muss auch das Vorzeichen von {klammer(e)} "
                                        f"umgedreht werden."),
                      (F(f - b + e, a + c), "Beim Minus vor der Klammer dreht sich auch das Vorzeichen vor dem x um.")]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.7 Brüche ───────────────────────────────────────────

def b1_7(r):
    lid, aus = "B1.7", []
    for nr in range(1, 29):
        stufe = 1 if nr <= 10 else 2 if nr <= 20 else 3
        if stufe == 1:  # x/a + b = c
            a = nz(r, 2, 6)
            x0 = a * nz(r, 1, 8)
            b = nz(r, 1, 9)
            c = F(x0, a) + b
            gl = f"x/{a} + {b} = {z(c)}"
            weg = [gl, f"x/{a} = {z(c - b)} {op('-', b)}", f"x = {x0} {op('·', a)}"]
            tipps = ["Zuerst die Zahl wegbringen, dann den Bruch.",
                     f"Rechne auf beiden Seiten −{b}. Dann steht x/{a} = {z(c - b)} da.",
                     f"x/{a} heißt x : {a}. Das Gegenteil ist · {a}."]
            fehler = [(F(c - b, a), f"x/{a} heißt x : {a}. Um das wegzubringen, rechnest du mal {a}, nicht durch {a}."),
                      ((c + b) * a, f"Um + {b} wegzubringen, rechnest du − {b}.")]
        elif stufe == 2:  # x/a + x/b = c  oder (x + b)/a = c
            if r.random() < 0.5:
                a, b = r.choice([(2, 3), (2, 5), (3, 4), (3, 6), (2, 4), (4, 6)])
                hn = a * b // __import__("math").gcd(a, b)
                x0 = hn * nz(r, 1, 4)
                c = F(x0, a) + F(x0, b)
                gl = f"x/{a} + x/{b} = {z(c)}"
                weg = [gl, f"{hn // a}x + {hn // b}x = {z(c * hn)} {op('·', hn)}",
                       f"{hn // a + hn // b}x = {z(c * hn)} | zusammenfassen",
                       f"x = {x0} {op(':', hn // a + hn // b)}"]
                tipps = [f"Suche den Hauptnenner von {a} und {b}: die kleinste Zahl, die durch beide teilbar ist.",
                         f"Der Hauptnenner ist {hn}. Multipliziere JEDES Glied mit {hn} – auch die rechte Seite!",
                         f"x/{a} · {hn} = {hn // a}x und x/{b} · {hn} = {hn // b}x."]
                fehler = [(F(c, hn // a + hn // b), f"Beim Multiplizieren mit {hn} muss auch die rechte Seite "
                                                    f"mal {hn} gerechnet werden.")]
            else:
                a, b = nz(r, 2, 6), nz(r, -8, 8)
                x0 = nz(r, -10, 12)
                while (x0 + b) % a:
                    x0 += 1
                c = F(x0 + b, a)
                gl = f"({term(1, b)})/{a} = {z(c)}"
                weg = [gl, f"{term(1, b)} = {z(c * a)} {op('·', a)}", f"x = {x0} {op('-', b)}"]
                tipps = [f"Der Bruchstrich wirkt wie eine Klammer um ({term(1, b)}).",
                         f"Multipliziere beide Seiten mit {a}. Dann ist der Bruch weg.",
                         f"Jetzt steht da {term(1, b)} = {z(c * a)}."]
                fehler = [(c - b, f"Zuerst den Bruch wegbringen: beide Seiten mal {a}."),
                          (c * a + b, f"Um {'+' if b > 0 else '−'} {abs(b)} wegzubringen, rechnest du das Gegenteil.")]
        else:  # (x + a)/b = (x + c)/d
            b, d = r.choice([(2, 3), (3, 4), (2, 5), (4, 3), (3, 2), (5, 2)])
            x0 = nz(r, -10, 10)
            a = nz(r, -6, 6)
            # (x0 + a)/b = (x0 + c)/d → c = d·(x0 + a)/b − x0, ganzzahlig machen
            while (d * (x0 + a)) % b:
                a += 1
            c = d * (x0 + a) // b - x0
            hn = b * d // __import__("math").gcd(b, d)
            gl = f"({term(1, a)})/{b} = ({term(1, c)})/{d}"
            pb, pd = hn // b, hn // d
            weg = [gl, f"{pb}({term(1, a)}) = {pd}({term(1, c)}) {op('·', hn)}",
                   f"{term(pb, pb * a)} = {term(pd, pd * c)} | ausmultiplizieren",
                   f"{term(pb - pd, pb * a)} = {z(pd * c)} {opx(pd)}",
                   f"{term(pb - pd)} = {z(pd * c - pb * a)} {op('-', pb * a)}",
                   f"x = {z(x0)} {op(':', pb - pd)}"]
            tipps = [f"Multipliziere beide Seiten mit dem Hauptnenner {hn}.",
                     f"Links bleibt {pb}({term(1, a)}), rechts {pd}({term(1, c)}). Die Bruchstriche sind weg!",
                     "Jetzt Klammern auflösen und wie gewohnt weiterrechnen."]
            fehler = [(F(d * c - b * a, b - d), f"Achtung, über Kreuz: Beim Multiplizieren mit {hn} bleibt links "
                                                f"{pb}({term(1, a)}) und rechts {pd}({term(1, c)}) – nicht umgekehrt.")]
        aus.append(aufgabe(lid, nr, stufe, gl, x0, weg, tipps, fehler))
    return aus


# ── B1.8 Sonderfälle ──────────────────────────────────────

def b1_8(r):
    lid, aus = "B1.8", []
    optionen = ["genau eine Lösung", "keine Lösung", "unendlich viele Lösungen"]
    for nr in range(1, 22):
        stufe = 1 if nr <= 8 else 2 if nr <= 15 else 3
        fall = [0, 1, 2][nr % 3]
        a = nz(r, 2, 6)
        b, d = nz(r, -9, 9), nz(r, -9, 9)
        if stufe < 3:
            if fall == 0:
                c = a + nz(r, 1, 3)
                gl = f"{term(a, b)} = {term(c, d)}"
                erk = (f"Bringst du {term(c)} nach links, bleibt {term(a - c)} übrig – das x verschwindet nicht. "
                       "Also gibt es genau eine Lösung.")
            elif fall == 1:
                while d == b:
                    d = nz(r, -9, 9)
                gl = f"{term(a, b)} = {term(a, d)}"
                erk = (f"Rechnest du auf beiden Seiten −{a}x, bleibt `{b} = {d}` übrig. Das stimmt nie – "
                       "egal, was x ist. Also keine Lösung: L = { }.")
            else:
                k = nz(r, 2, 4)
                gl = f"{k}({term(a, b)}) = {term(k * a, k * b)}"
                erk = (f"Löst du die Klammer auf, steht links genau dasselbe wie rechts: {term(k * a, k * b)}. "
                       "Das stimmt für jede Zahl. Also unendlich viele Lösungen: L = ℝ.")
        else:
            if fall == 0:
                gl = f"{a}(x + {abs(b)}) = {term(a + 1, d)}"
                erk = "Nach dem Ausmultiplizieren hast du links und rechts verschieden viele x – also genau eine Lösung."
            elif fall == 1:
                e = nz(r, 1, 5)
                gl = f"{a}(x - {e}) = {term(a, -a * e + nz(r, 1, 5))}"
                erk = f"Ausmultipliziert: {term(a, -a * e)} links. Rechts steht gleich viel x, aber eine andere Zahl. Das stimmt nie – keine Lösung."
            else:
                e = nz(r, 1, 5)
                gl = f"{term(a + 2, 2 * e)} - 2(x - {e}) = {term(a, 4 * e)}"
                erk = "Minus vor der Klammer beachten: Links bleibt nach dem Zusammenfassen genau dasselbe wie rechts – unendlich viele Lösungen."
        aus.append({"id": f"{lid}-{nr:03d}", "typ": "auswahl", "stufe": stufe,
                    "frage": f"Wie viele Lösungen hat die Gleichung `{gl}`?",
                    "optionen": optionen, "richtig": [fall], "erklaerung": erk,
                    "pruefung": {"art": "anzahl", "gleichung": gl},
                    "tipps": ["Vereinfache die Gleichung so weit wie möglich.",
                              "Bring alle x auf eine Seite. Bleibt ein x übrig – oder verschwindet es?"]})
    return aus


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ZIEL.mkdir(parents=True, exist_ok=True)
    r = random.Random(20261014)
    for lid, fn in [("B1.1", b1_1), ("B1.2", b1_2), ("B1.3", b1_3), ("B1.4", b1_4),
                    ("B1.5", b1_5), ("B1.6", b1_6), ("B1.7", b1_7), ("B1.8", b1_8)]:
        aufgaben = fn(r)
        kopf = (f"# ERZEUGT von tools/generatoren/b1.py – nicht von Hand bearbeiten.\n"
                f"# Geprüft wird beim Build (tools/build.py) mit sympy.\n")
        text = yaml.safe_dump(aufgaben, allow_unicode=True, sort_keys=False, width=200)
        (ZIEL / f"{lid}.aufgaben.yaml").write_text(kopf + text, encoding="utf-8")
        print(f"{lid}: {len(aufgaben)} Aufgaben")


if __name__ == "__main__":
    main()
