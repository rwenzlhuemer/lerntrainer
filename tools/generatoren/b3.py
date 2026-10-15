"""
Generator für Kapitel B3 (Lineare Ungleichungen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/b3.py
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import dez, endlich, erzeuge, nz, schreibe, z  # noqa: E402

UMDREHEN = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}


def zt(q):
    q = F(q)
    return dez(q) if endlich(q) and q.denominator <= 1000 else z(q)


def lin(a, b):
    """a·x + b als Text"""
    a, b = F(a), F(b)
    if a == 0:
        return zt(b)
    k = "x" if a == 1 else "-x" if a == -1 else f"{zt(a)}x"
    if b == 0:
        return k
    return f"{k} {'+' if b > 0 else '-'} {zt(abs(b))}"


def intervall(rel, b):
    bt = zt(b)
    return {"<": f"]-∞; {bt}[", "≤": f"]-∞; {bt}]", ">": f"]{bt}; ∞[", "≥": f"[{bt}; ∞["}[rel]


def loese(A, B, rel, C, D):
    """A·x + B rel C·x + D → (Weg-Zeilen, Endrelation, Grenze, umgedreht?)"""
    A, B, C, D = map(F, (A, B, C, D))
    weg = []
    k = A - C
    if C != 0:
        weg.append(f"{lin(k, B)} {rel} {zt(D)} | {'−' if C > 0 else '+'}{lin(abs(C), 0)}")
    if B != 0:
        weg.append(f"{lin(k, 0)} {rel} {zt(D - B)} | {'−' if B > 0 else '+'}{zt(abs(B))}")
    grenze = (D - B) / k
    end = rel if k > 0 else UMDREHEN[rel]
    if k != 1:
        weg.append(f"x {end} {zt(grenze)} | :{zt(k) if k > 0 else '(' + zt(k) + ')'}" + (" – Zeichen umdrehen!" if k < 0 else ""))
    return weg, end, grenze, k < 0


def aufgabe(ungl, weg, end, grenze, umgedreht, form=None, frage=None):
    loesung = f"x {end} {zt(grenze)}"
    fehler = []
    if umgedreht:
        fehler.append({"antwort": f"x {UMDREHEN[end]} {zt(grenze)}",
                       "hinweis": "Beim Multiplizieren oder Dividieren mit einer **negativen** Zahl dreht sich das Ungleichheitszeichen um!"})
    a = {"typ": "ungleichung"}
    if frage:
        a["frage"] = frage
    a["ungleichung"] = ungl
    if form:
        a["form"] = form
    a.update({"loesung": loesung, "weg": [ungl] + weg,
              "tipps": ["Du formst wie bei einer Gleichung um: x-Glieder auf eine Seite, Zahlen auf die andere.",
                        "**Einzige Ausnahme:** Multiplizierst oder dividierst du mit einer **negativen** Zahl, dreht sich das Zeichen um "
                        "(aus < wird >).", f"Zum Schluss steht da: `x {end} …`" if not umgedreht else
                        "Hier musst du durch eine negative Zahl dividieren – Zeichen umdrehen!"],
              "fehler": fehler})
    if form == "intervall":
        a["tipps"][2] = ("Als Intervall: `x < 3` ist `]-∞; 3[`, `x ≥ 2` ist `[2; ∞[`. Die eckige Klammer zeigt nach außen, wenn die Zahl **nicht** dazugehört.")
    return a


def zufallsungleichung(r, s):
    rel = r.choice(["<", ">", "≤", "≥"])
    if s == 1:
        A, B, C = nz(r, 1, 6), nz(r, -9, 9), 0
        D = B + A * nz(r, -6, 6)
    elif s == 2:
        A, B, C = nz(r, -6, -1), nz(r, -9, 9), 0
        D = B + A * nz(r, -6, 6)
    elif s == 3:
        A, C = nz(r, -6, 6), nz(r, -6, 6)
        if A == C:
            return None
        B = nz(r, -9, 9)
        D = B + (A - C) * nz(r, -7, 7)
    else:
        A, C = F(nz(r, -5, 5), r.choice([2, 3, 4])), F(nz(r, -5, 5), r.choice([2, 3, 4]))
        if A == C:
            return None
        B, D = F(nz(r, -9, 9), r.choice([1, 2])), F(nz(r, -9, 9), r.choice([1, 2]))
    links = lin(A, B)
    rechts = lin(C, D) if C != 0 else zt(D)
    return f"{links} {rel} {rechts}", (A, B, rel, C, D)


def b3_1(r, s, form=None):
    u = zufallsungleichung(r, s)
    if not u:
        return None
    text, (A, B, rel, C, D) = u
    if s == 4 and r.random() < .5:
        # mit Klammern
        k, m = nz(r, -4, -2), nz(r, 2, 4)
        p, q = nz(r, -5, 5), nz(r, -5, 5)
        text = f"{k}(x {'+' if p > 0 else '-'} {abs(p)}) {rel} {m}(x {'+' if q > 0 else '-'} {abs(q)})"
        A, B, C, D = F(k), F(k * p), F(m), F(m * q)
        weg0 = [f"{lin(A, B)} {rel} {lin(C, D)} | Klammern aufgelöst"]
    else:
        weg0 = []
    weg, end, grenze, umgedreht = loese(A, B, rel, C, D)
    return aufgabe(text, weg0 + weg, end, grenze, umgedreht, form=form)


def b3_2(r, s):
    if s >= 2 and r.random() < .35:
        rel = r.choice(["<", ">", "≤", "≥"])
        b = F(nz(r, -9, 9), r.choice([1, 1, 2]))
        ziel = f"x {rel} {zt(b)}"
        optionen = [intervall(rel, b), intervall({"<": "≤", "≤": "<", ">": "≥", "≥": ">"}[rel], b), intervall(UMDREHEN[rel], b)]
        r.shuffle(optionen)
        return {"typ": "auswahl", "frage": f"Welches Intervall beschreibt alle Zahlen mit `{ziel}`?",
                "optionen": optionen, "richtig": [optionen.index(intervall(rel, b))],
                "pruefung": {"art": "intervall", "ziel": ziel},
                "erklaerung": "Die Klammer zeigt, ob die Grenze dazugehört: `[` bzw. `]` nach innen = gehört dazu (≤, ≥); "
                              "nach außen gedreht = gehört nicht dazu (<, >). Bei ∞ ist die Klammer immer offen.",
                "tipps": ["Zeichne dir die Zahlengerade: Liegen die Lösungen links oder rechts der Grenze?",
                          "Gehört die Grenze selbst dazu (≤, ≥) oder nicht (<, >)?"]}
    return b3_1(r, max(1, s - 1) if s < 4 else 3, form="intervall")


TEXTE = {
    1: [("Ein Handytarif kostet 10 € Grundgebühr und 0,05 € pro Minute. Wie viele Minuten x darf man höchstens telefonieren, "
         "damit die Rechnung höchstens 25 € beträgt? Gib die Lösung als Ungleichung an.", "10 + 0,05x ≤ 25"),
        ("Lisa hat 30 € und kauft Hefte um je 2,5 €. Wie viele Hefte x kann sie höchstens kaufen? (Ungleichung)", "2,5x ≤ 30"),
        ("Das Dreifache einer Zahl x, vermehrt um 4, ist größer als 19. Welche Zahlen x erfüllen das?", "3x + 4 > 19"),
        ("Ein Aufzug trägt höchstens 600 kg. Ein Mann mit 90 kg fährt mit Kisten zu je 30 kg. Wie viele Kisten x darf er mitnehmen?",
         "90 + 30x ≤ 600")],
    2: [("Tarif A: 15 € Grundgebühr + 0,10 € pro Minute. Tarif B: 25 € Grundgebühr + 0,05 € pro Minute. Für welche Minutenzahlen x "
         "ist Tarif B billiger?", "25 + 0,05x < 15 + 0,1x"),
        ("Ein Rechteck ist 5 cm lang. Für welche Breiten x ist der Umfang mindestens 24 cm?", "2·5 + 2x ≥ 24"),
        ("Eine Zahl x wird um 7 verkleinert und das Ergebnis verdoppelt. Das ist kleiner als 10. Welche Zahlen x erfüllen das?", "2(x - 7) < 10"),
        ("Ein Wasserbecken enthält 800 Liter und verliert 25 Liter pro Stunde. Nach wie vielen Stunden x sind weniger als 300 Liter drin?",
         "800 - 25x < 300")],
    3: [("Ein Kopierladen verlangt 0,08 € pro Kopie, ein anderer 0,05 € pro Kopie plus 6 € Grundgebühr. Ab wie vielen Kopien x ist der "
         "zweite billiger?", "6 + 0,05x < 0,08x"),
        ("Die Temperatur fällt ab 20 °C jede Stunde um 1,5 Grad. Nach wie vielen Stunden x ist es kälter als 5 °C?", "20 - 1,5x < 5"),
        ("Für welche x ist der Term 4 - 3x positiv?", "4 - 3x > 0"),
        ("Ein Taxi kostet 3,5 € plus 1,2 € pro km. Wie viele km x kann man mit 20 € höchstens fahren?", "3,5 + 1,2x ≤ 20")],
    4: [("Ein Fitnessstudio A kostet 40 € Aufnahme und 25 € pro Monat, Studio B keine Aufnahme und 30 € pro Monat. Ab wie vielen "
         "Monaten x ist A günstiger?", "40 + 25x < 30x"),
        ("Für welche x ist der Mittelwert von x, 8 und 11 mindestens 10?", "(x + 8 + 11)/3 ≥ 10"),
        ("Ein Sparschwein enthält 40 €. Jede Woche kommen 7,5 € dazu, Paul nimmt aber jede Woche 2 € heraus. Ab wie vielen Wochen x "
         "sind mehr als 100 € drin?", "40 + 7,5x - 2x > 100"),
        ("Für welche x ist 3(x - 2) kleiner als 5x + 4?", "3(x - 2) < 5x + 4")],
}


def b3_3(r, s):

    frage, ungl = r.choice(TEXTE[s])
    import notation  # noqa: E402
    for zeichen in ["≤", "≥", "<", ">"]:
        if zeichen in ungl:
            rel = zeichen
            links, rechts = ungl.split(zeichen)
            break
    x = notation.ausdruck("x")
    L, R = notation.ausdruck(links) - notation.ausdruck(rechts), 0
    A = F(str(L.coeff(x, 1)))
    B = F(str(L.subs(x, 0)))
    weg, end, grenze, umgedreht = loese(A, B, rel, 0, R)
    weg = [f"{lin(A, B)} {rel} 0 | alles auf eine Seite"] + weg
    return aufgabe(ungl, weg, end, grenze, umgedreht, frage=frage + " Stell eine Ungleichung auf und löse sie nach x.")


def main():
    sys.path.insert(0, str(HIER.parent))
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261022)
    for lid, fn, n in [("B3.1", b3_1, 10), ("B3.2", b3_2, 8), ("B3.3", b3_3, 4)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "b3.py")


if __name__ == "__main__":
    main()
