"""
Generator für Teil D (Trigonometrie und Vektoren). Einmal laufen lassen:

    python tools/generatoren/d.py

Dreiecke löst der Build selbst (dreieck_rechnen), Vektoren rechnet er nach (vektor_rechnung, vektor_zahl).
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
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 1000 else z(q)


def gerundet(wert, stellen):
    return f"{wert:.{stellen}f}".replace(".", ",")


def zahl(frage, loesung, tipps, fehler=(), stellen=None, **extra):
    """loesung: Fraction (exakt) oder float (dann auf stellen gerundet)"""
    a = {"typ": "zahl", "frage": frage}
    if isinstance(loesung, float):
        a["loesung"] = gerundet(loesung, stellen)
        a["gerundet"] = stellen
    else:
        a["loesung"] = zt(loesung)
    a.update({k: v for k, v in extra.items() if v is not None})
    a["tipps"] = tipps
    soll = float(loesung)
    a["fehler"] = [{"antwort": gerundet(w, stellen or 2) if isinstance(w, float) else zt(w), "hinweis": h}
                   for w, h in fehler if w is not None and abs(float(w) - soll) > 0.05]
    return a


TRIPEL = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25), (12, 16, 20), (20, 21, 29)]


# ── D1 Rechtwinkeliges Dreieck ────────────────────────────

def d1_1(r, s):
    if s <= 2:
        a, b, c = r.choice(TRIPEL)
        if r.random() < .5:
            a, b = b, a
        if s == 1:
            return zahl("Berechne die Hypotenuse c des rechtwinkeligen Dreiecks.", F(c),
                        ["Pythagoras: `a² + b² = c²` – die Hypotenuse liegt dem rechten Winkel gegenüber.", f"`c = √({a}² + {b}²)`"],
                        [(F(a + b), "Man darf die Seiten nicht einfach addieren – zuerst quadrieren, dann Wurzel ziehen.")],
                        dreieck={"a": a, "b": b}, dreieck_rechnen={"gegeben": {"a": a, "b": b}, "gesucht": "c"})
        return zahl("Berechne die Kathete a des rechtwinkeligen Dreiecks.", F(a),
                    ["`a² + b² = c²`, also `a² = c² − b²`.", f"`a = √({c}² − {b}²)`"],
                    [(math.sqrt(c * c + b * b), "Gesucht ist eine Kathete: c² **minus** b².")],
                    dreieck={"b": b, "c": c}, dreieck_rechnen={"gegeben": {"b": b, "c": c}, "gesucht": "a"})
    if s == 3:
        a, b = r.randint(2, 12), r.randint(2, 12)
        c = math.hypot(a, b)
        return zahl("Berechne die Hypotenuse c (auf zwei Nachkommastellen).", c, [f"`c = √({a}² + {b}²)`"], [(float(a + b), "Zuerst quadrieren.")],
                    stellen=2, dreieck={"a": a, "b": b}, dreieck_rechnen={"gegeben": {"a": a, "b": b}, "gesucht": "c"})
    art = r.choice(["leiter", "bildschirm", "rampe"])
    if art == "leiter":
        lang, abstand = r.choice([(5, 1.5), (4, 1.2), (6, 2), (7, 2.5), (3.5, 1)])
        h = math.sqrt(lang ** 2 - abstand ** 2)
        return zahl(f"Eine {zt(F(str(lang)))} m lange Leiter lehnt an einer Hauswand. Ihr Fuß steht {zt(F(str(abstand)))} m von der Wand entfernt. "
                    "In welcher Höhe berührt sie die Wand? (auf zwei Nachkommastellen)", h,
                    ["Skizze: Die Leiter ist die Hypotenuse.", "Höhe² = Leiter² − Abstand²."], [(math.sqrt(lang ** 2 + abstand ** 2), "Die Leiter ist die längste Seite (Hypotenuse): minus, nicht plus.")],
                    stellen=2, einheit="m", dreieck_rechnen={"gegeben": {"c": zt(F(str(lang))), "b": zt(F(str(abstand)))}, "gesucht": "a"})
    if art == "bildschirm":
        br, ho = r.choice([(16, 9), (4, 3), (16, 10)])
        k = r.choice([3, 4, 5])
        d = math.hypot(br * k, ho * k)
        return zahl(f"Ein Bildschirm ist {br * k} cm breit und {ho * k} cm hoch. Wie lang ist die Diagonale? (auf zwei Nachkommastellen)", d,
                    ["Die Diagonale teilt das Rechteck in zwei rechtwinkelige Dreiecke.", "Diagonale² = Breite² + Höhe²."], [],
                    stellen=2, einheit="cm", dreieck_rechnen={"gegeben": {"a": ho * k, "b": br * k}, "gesucht": "c"})
    laenge, hoehe = r.choice([(5, 0.5), (8, 0.6), (3, 0.25), (12, 1)])
    w = math.sqrt(laenge ** 2 - hoehe ** 2)
    return zahl(f"Eine Rampe ist {laenge} m lang und überwindet {zt(F(str(hoehe)))} m Höhe. Wie lang ist sie waagrecht gemessen? (auf zwei Nachkommastellen)", w,
                ["Die Rampe ist die Hypotenuse, die Höhe eine Kathete."], [], stellen=2, einheit="m",
                dreieck_rechnen={"gegeben": {"c": laenge, "a": zt(F(str(hoehe)))}, "gesucht": "b"})


def d1_2(r, s):
    a, b, c = r.choice(TRIPEL)
    fn = r.choice(["sin", "cos", "tan"])
    wert = {"sin": F(a, c), "cos": F(b, c), "tan": F(a, b)}[fn]
    falsch = {"sin": F(b, c), "cos": F(a, c), "tan": F(b, a)}[fn]
    return zahl(f"Berechne {fn} α im abgebildeten Dreieck (als Bruch oder Dezimalzahl).", wert,
                ["sin α = Gegenkathete : Hypotenuse, cos α = Ankathete : Hypotenuse, tan α = Gegenkathete : Ankathete.",
                 "Gegenkathete von α ist a (liegt gegenüber), Ankathete ist b (liegt an α an), Hypotenuse ist c."],
                [(falsch, "Gegenkathete und Ankathete verwechselt? Die Gegenkathete liegt dem Winkel **gegenüber**.")],
                dreieck={"a": a, "b": b, "c": c}, dreieck_rechnen={"gegeben": {"a": a, "b": b}, "gesucht": f"{fn}_alpha"})


def d1_3(r, s):
    if s <= 2:
        al = r.choice([20, 25, 30, 35, 40, 50, 55, 60])
        bek = r.choice(["c", "b"])
        wert = r.randint(4, 15)
        ges = r.choice(["a", "b"] if bek == "c" else ["a", "c"])
        rad = math.radians(al)
        erg = {("c", "a"): wert * math.sin(rad), ("c", "b"): wert * math.cos(rad), ("b", "a"): wert * math.tan(rad), ("b", "c"): wert / math.cos(rad)}[(bek, ges)]
        dreieck = {"alpha": f"{al}°", bek: wert}
        return zahl(f"Berechne die Seite {ges} (auf zwei Nachkommastellen).", erg,
                    ["Welche Seiten sind beteiligt: Gegenkathete a, Ankathete b, Hypotenuse c?", "Wähle sin, cos oder tan, je nachdem, welche zwei Seiten vorkommen.",
                     "Dann nach der gesuchten Seite umformen."], [], stellen=2, dreieck=dreieck,
                    dreieck_rechnen={"gegeben": {"alpha": al, bek: wert}, "gesucht": ges})
    a, b = r.randint(2, 12), r.randint(2, 12)
    if a == b:
        return None
    gegeben = r.choice([{"a": a, "b": b}, {"a": a, "c": max(a, b) + r.randint(1, 5)}, {"b": b, "c": max(a, b) + r.randint(1, 5)}])
    ges = "alpha" if s == 3 else r.choice(["alpha", "beta"])
    sys.path.insert(0, str(HIER.parent))
    import build  # noqa: PLC0415
    w = float(build.dreieck_loesen(gegeben)[ges])
    return zahl(f"Berechne den Winkel {'α' if ges == 'alpha' else 'β'} in Grad (auf eine Nachkommastelle).", w,
                ["Zuerst sin, cos oder tan des Winkels als Seitenverhältnis aufschreiben.", "Dann mit der Umkehrfunktion (sin⁻¹, cos⁻¹, tan⁻¹) den Winkel berechnen – Taschenrechner auf Grad (DEG)!",
                 "β = 90° − α."], [(90 - w, "Das ist der andere spitze Winkel. α liegt bei A, β bei B.")], stellen=1, einheit="°",
                dreieck={k: v for k, v in gegeben.items()}, dreieck_rechnen={"gegeben": gegeben, "gesucht": ges})


def d1_4(r, s):
    art = r.choice(["steigung", "baum", "seilbahn"] if s > 1 else ["steigung", "baum"])
    if art == "steigung":
        p = r.choice([5, 8, 10, 12, 15, 20, 25])
        w = math.degrees(math.atan(p / 100))
        return zahl(f"Eine Straße hat {p} % Steigung. Wie groß ist der Steigungswinkel? (in Grad, eine Nachkommastelle)", w,
                    [f"{p} % Steigung heißt: auf 100 m waagrecht {p} m Höhe.", f"`tan α = {p}/100`."], [(float(p), "Prozent sind kein Winkel: tan α = p/100.")],
                    stellen=1, einheit="°", dreieck_rechnen={"gegeben": {"a": p, "b": 100}, "gesucht": "alpha"})
    if art == "baum":
        d, al = r.choice([20, 25, 30, 40]), r.choice([25, 30, 35, 40, 45, 50])
        h = d * math.tan(math.radians(al))
        return zahl(f"Aus {d} m Entfernung sieht man die Spitze eines Baumes unter einem Höhenwinkel von {al}°. Wie hoch ist der Baum (Augenhöhe vernachlässigt)? "
                    "(zwei Nachkommastellen)", h, ["Entfernung = Ankathete, Höhe = Gegenkathete.", f"`tan {al}° = h/{d}`."], [], stellen=2, einheit="m",
                    dreieck_rechnen={"gegeben": {"alpha": al, "b": d}, "gesucht": "a"})
    l, al = r.choice([800, 1200, 1500, 2000]), r.choice([15, 20, 25, 30])
    h = l * math.sin(math.radians(al))
    return zahl(f"Eine Seilbahn ist {l} m lang und steigt unter dem Winkel {al}° an. Welchen Höhenunterschied überwindet sie? (zwei Nachkommastellen)", h,
                ["Das Seil ist die Hypotenuse.", f"`sin {al}° = h/{l}`."], [(l * math.cos(math.radians(al)), "Das ist die waagrechte Strecke (cos). Für die Höhe: sin.")],
                stellen=2, einheit="m", dreieck_rechnen={"gegeben": {"alpha": al, "c": l}, "gesucht": "a"})


# ── D2 Einheitskreis, Bogenmaß, Sinusfunktion ─────────────

def d2_1(r, s):
    w = r.choice([120, 135, 150, 210, 225, 240, 300, 315, 330, 180, 270] if s > 1 else [120, 135, 150, 180])
    fn = r.choice(["sin", "cos"])
    v = getattr(math, fn)(math.radians(w))
    return zahl(f"Berechne {fn}({w}°) (auf drei Nachkommastellen).", v,
                ["Am Einheitskreis: cos ist die x-Koordinate, sin die y-Koordinate des Punktes.", "Achte auf das Vorzeichen im jeweiligen Quadranten."],
                [(-v, "Vorzeichen: In welchem Quadranten liegt der Winkel?")], stellen=3, rechnung=f"{fn}({w}·π/180)")


def d2_2(r, s):
    w = r.choice([30, 45, 60, 90, 120, 135, 150, 180, 270, 360, 15, 75, 210])
    if r.random() < .5 or s == 1:
        return zahl(f"Rechne {w}° ins Bogenmaß um (auf drei Nachkommastellen).", math.radians(w),
                    ["180° entsprechen π.", f"`{w} · π/180`"], [(w * 180 / math.pi, "Umgekehrt: Grad mal π/180.")], stellen=3, rechnung=f"{w}·π/180")
    g = F(w, 180)
    text = ("π" if g == 1 else f"{g.numerator}π" if g.denominator == 1 else f"{'' if g.numerator == 1 else g.numerator}π/{g.denominator}")
    return zahl(f"Rechne {text} ins Gradmaß um.", F(w), ["π entspricht 180°.", "Ersetze π durch 180°."], [], rechnung=f"{text}·180/π", einheit="°")


def d2_3(r, s):
    a, b = r.choice([1, 2, 3, F(1, 2)]), r.choice([1, 2, 3, F(1, 2)])
    term = f"{zt(a) if a != 1 else ''}sin({zt(b) if b != 1 else ''}x)"
    art = r.choice(["amplitude", "periode"])
    if art == "amplitude":
        return zahl(f"Wie groß ist die **Amplitude** von `f(x) = {term}`?", a, ["Die Zahl **vor** dem sin streckt in y-Richtung: Das ist die Amplitude."],
                    [(b, "Die Zahl vor dem x ändert die Periode, nicht die Amplitude.")], aus_term={"term": term, "groesse": "amplitude"},
                    graph={"x": [-1, 7], "y": [-4, 4], "kurven": [{"term": term, "name": "f"}]} if s >= 2 else None)
    per = F(2) / b
    text = "2π" if per == 2 else f"{per.numerator}π" if per.denominator == 1 else f"{'' if per.numerator == 1 else per.numerator}π/{per.denominator}"
    return {"typ": "zahl", "frage": f"Wie lang ist die **Periode** von `f(x) = {term}`? (z. B. als Vielfaches von π)", "loesung": text,
            "aus_term": {"term": term, "groesse": "periode"},
            "tipps": ["sin(x) hat die Periode 2π.", "Steht innen b·x, ist die Periode 2π : b."], "fehler": []}


# ── D3 Vektoren ───────────────────────────────────────────

def vek(liste):
    return [zt(v) for v in liste]


def vt(liste):
    return "(" + " | ".join(zt(v) for v in liste) + ")"


def vektor_aufgabe(frage, loesung, rechnung, tipps, fehler=(), form=None):
    a = {"typ": "vektor", "frage": frage, "loesung": vek(loesung), "vektor_rechnung": rechnung, "tipps": tipps,
         "fehler": [{"antwort": vek(w), "hinweis": h} for w, h in fehler if list(w) != list(loesung)]}
    if form:
        a["form"] = form
    return a


def zvek(r, dim, lo=-6, hi=6, s=1):
    return [F(nz(r, lo, hi, ()), 2 if s == 4 and r.random() < .5 else 1) for _ in range(dim)]


def d3_1(r, s):
    n = 3 if s <= 2 else 4
    sorten = ["Äpfel", "Birnen", "Orangen", "Kiwis"][:n]
    stueck = [r.randint(1, 9) for _ in range(n)]
    preise = [F(r.randint(2, 30), 10) for _ in range(n)]
    gesamt = sum(x * y for x, y in zip(stueck, preise))
    return zahl(f"Ein Einkauf: Stückzahlen S = {vt(stueck)} für {', '.join(sorten)}, Preise pro Stück P = {vt(preise)} (in €). "
                "Wie viel kostet der Einkauf (Skalarprodukt S · P)?", gesamt,
                ["Jede Stückzahl mal ihren Preis, dann alles addieren.", "Das ist das Skalarprodukt: S₁·P₁ + S₂·P₂ + …"],
                [(sum(stueck) * sum(preise) / n, "Nicht Summe mal Summe – jede Sorte mit ihrem eigenen Preis.")], einheit="€",
                vektor_zahl={"art": "skalar", "a": vek(stueck), "b": vek(preise)})


def d3_2(r, s):
    dim = 3 if s >= 3 else 2
    A, B = zvek(r, dim, -6, 8, s), zvek(r, dim, -6, 8, s)
    ab = [y - x for x, y in zip(A, B)]
    return vektor_aufgabe(f"Gegeben sind A{vt(A)} und B{vt(B)}. Berechne den Vektor AB.", ab, {"op": "AB", "a": vek(A), "b": vek(B)},
                          ["`AB = B − A`: Spitze minus Schaft.", "Rechne Koordinate für Koordinate."],
                          [([x - y for x, y in zip(A, B)], "Umgekehrt: B minus A (Spitze minus Schaft), nicht A minus B.")])


def d3_3(r, s):
    dim = 3 if s >= 3 else 2
    a, b = zvek(r, dim, s=s), zvek(r, dim, s=s)
    op = r.choice(["plus", "minus", "mal"] if s <= 2 else ["kombi", "minus", "kombi"])
    if op == "plus":
        return vektor_aufgabe(f"Berechne a + b für a = {vt(a)} und b = {vt(b)}.", [x + y for x, y in zip(a, b)], {"op": "plus", "a": vek(a), "b": vek(b)},
                              ["Koordinatenweise addieren."])
    if op == "minus":
        return vektor_aufgabe(f"Berechne a − b für a = {vt(a)} und b = {vt(b)}.", [x - y for x, y in zip(a, b)], {"op": "minus", "a": vek(a), "b": vek(b)},
                              ["Koordinatenweise subtrahieren – Vorsicht bei negativen Zahlen."], [([x + y for x, y in zip(a, b)], "Minus, nicht plus.")])
    if op == "mal":
        k = nz(r, -4, 4, (0, 1))
        return vektor_aufgabe(f"Berechne {k} · a für a = {vt(a)}.", [k * x for x in a], {"op": "mal", "a": vek(a), "k": k}, ["Jede Koordinate mit der Zahl multiplizieren."])
    k, m = nz(r, -3, 3, (0,)), nz(r, -3, 3, (0,))
    return vektor_aufgabe(f"Berechne {k} · a {'+' if m > 0 else '−'} {abs(m)} · b für a = {vt(a)} und b = {vt(b)}.",
                          [k * x + m * y for x, y in zip(a, b)], {"op": "kombi", "a": vek(a), "b": vek(b), "k": k, "m": m},
                          ["Zuerst beide Vektoren mit ihrer Zahl multiplizieren, dann koordinatenweise addieren."])


def d3_4(r, s):
    dim = 3 if s >= 3 else 2
    if s == 1:
        p, q, h = r.choice(TRIPEL)
        v = [p, q]
        w = F(h)
    else:
        v = zvek(r, dim, -7, 7)
        w = math.sqrt(sum(x * x for x in v))
        if float(w).is_integer():
            w = F(int(w))
    return zahl(f"Berechne den Betrag (die Länge) des Vektors v = {vt(v)}" + (" (auf zwei Nachkommastellen)." if isinstance(w, float) else "."), w,
                ["`|v| = √(x² + y²)` (in 3D: `√(x² + y² + z²)`) – Pythagoras!"], [(float(sum(abs(x) for x in v)), "Erst quadrieren, addieren, dann die Wurzel.")],
                stellen=2, vektor_zahl={"art": "betrag", "a": vek(v)})


def d3_5(r, s):
    dim = 3 if s >= 3 else 2
    a, b = zvek(r, dim), zvek(r, dim)
    if r.random() < .5:
        sk = sum(x * y for x, y in zip(a, b))
        return zahl(f"Berechne das Skalarprodukt a · b für a = {vt(a)} und b = {vt(b)}.", sk,
                    ["`a · b = a₁·b₁ + a₂·b₂ (+ a₃·b₃)`.", "Das Ergebnis ist eine **Zahl**, kein Vektor."], [], vektor_zahl={"art": "skalar", "a": vek(a), "b": vek(b)})
    if r.random() < .5 and dim == 2:
        k = r.choice([1, 2, -1])
        b = [-a[1] * k, a[0] * k]
    normal = sum(x * y for x, y in zip(a, b)) == 0
    return {"typ": "auswahl", "frage": f"Stehen a = {vt(a)} und b = {vt(b)} normal (im rechten Winkel) aufeinander?",
            "optionen": ["Ja", "Nein"], "richtig": [0 if normal else 1], "pruefung": {"art": "normal", "a": vek(a), "b": vek(b)},
            "erklaerung": f"Das Skalarprodukt ist {zt(sum(x * y for x, y in zip(a, b)))}. Zwei Vektoren stehen genau dann normal aufeinander, wenn das Skalarprodukt **0** ist.",
            "tipps": ["Berechne das Skalarprodukt.", "Ist es 0, stehen die Vektoren normal aufeinander."]}


def d3_6(r, s):
    v = zvek(r, 2, s=s)
    return vektor_aufgabe(f"Gib einen Normalvektor zu v = {vt(v)} an.", [-v[1], v[0]], {"op": "normal", "a": vek(v)},
                          ["In ℝ²: Koordinaten vertauschen und bei einer das Vorzeichen ändern: (x | y) → (−y | x).",
                           "Probe: Das Skalarprodukt mit v muss 0 sein."], [([v[1], v[0]], "Vertauschen allein reicht nicht – ein Vorzeichen muss sich ändern.")] if v[0] * v[1] != 0 else [],
                          form="parallel")


# ── D4 Geraden ────────────────────────────────────────────

def d4_1(r, s):
    dim = 3 if s >= 3 else 2
    A, d = zvek(r, dim), zvek(r, dim)
    if r.random() < .5:
        B = [x + 2 * y for x, y in zip(A, d)]
        return vektor_aufgabe(f"Gib einen Richtungsvektor der Geraden durch A{vt(A)} und B{vt(B)} an.", [y - x for x, y in zip(A, B)],
                              {"op": "AB", "a": vek(A), "b": vek(B)}, ["Ein Richtungsvektor ist AB = B − A (jedes Vielfache davon geht auch)."], form="parallel")
    t = nz(r, -3, 3, (0,))
    return vektor_aufgabe(f"Die Gerade g: X = {vt(A)} + t · {vt(d)}. Welcher Punkt gehört zu t = {t}?", [x + t * y for x, y in zip(A, d)],
                          {"op": "kombi", "a": vek(A), "b": vek(d), "k": 1, "m": t},
                          [f"Setz t = {t} ein: Stützvektor plus {t}-mal Richtungsvektor."], [([t * x + y for x, y in zip(A, d)], "Nur der Richtungsvektor wird mit t multipliziert.")])


def d4_3(r, s):
    dim = 3 if s >= 3 else 2
    A, d = zvek(r, dim), zvek(r, dim)
    t = nz(r, -3, 3, (0,))
    P = [x + t * y for x, y in zip(A, d)]
    drauf = r.random() < .5
    if not drauf:
        P[r.randrange(dim)] += r.choice([1, -1, 2])
    import sympy  # noqa: PLC0415
    rang = sympy.Matrix.hstack(sympy.Matrix([sympy.nsimplify(str(p - a)) for p, a in zip(P, A)]), sympy.Matrix([sympy.nsimplify(str(x)) for x in d])).rank()
    drauf = rang <= 1
    return {"typ": "auswahl", "frage": f"Liegt der Punkt P{vt(P)} auf der Geraden g: X = {vt(A)} + t · {vt(d)}?", "optionen": ["Ja", "Nein"],
            "richtig": [0 if drauf else 1], "pruefung": {"art": "punkt_auf_gerade", "punkt": vek(P), "stuetz": vek(A), "richtung": vek(d)},
            "erklaerung": "Setz P = A + t · d und löse jede Koordinate nach t. Kommt überall **dasselbe** t heraus, liegt P auf g.",
            "tipps": ["Stell für jede Koordinate eine Gleichung auf: P = A + t · d.", "Löse jede nach t. Gleiches t überall → P liegt auf g."]}


AUFGABEN = [("D1.1", d1_1, 5), ("D1.2", d1_2, 5), ("D1.3", d1_3, 6), ("D1.4", d1_4, 5), ("D2.1", d2_1, 4), ("D2.2", d2_2, 4), ("D2.3", d2_3, 4),
            ("D3.1", d3_1, 5), ("D3.2", d3_2, 6), ("D3.3", d3_3, 6), ("D3.4", d3_4, 5), ("D3.5", d3_5, 6), ("D3.6", d3_6, 5),
            ("D4.1", d4_1, 5), ("D4.3", d4_3, 5)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HIER.parent))
    r = random.Random(20261030)
    for lid, fn, n in AUFGABEN:
        schreibe(lid, erzeuge(lid, r, fn, n), "d.py")


if __name__ == "__main__":
    main()
