"""
Generator für Kapitel C1 (Funktionsbegriff) und C2 (Lineare Funktionen). Einmal laufen lassen:

    python tools/generatoren/c12.py

Graphen (graph: {x, y, kurven, punkte}) zeichnet die App selbst; Werte, k und d prüft der Build mit sympy (aus_term).
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, nz, schreibe, z  # noqa: E402


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 100 else z(q)


def lin(k, d, var="x"):
    """k·x + d als Text: 2x - 1, -x + 4, x/2 + 3"""
    k, d = F(k), F(d)
    if k == 0:
        return zt(d)
    if k.denominator == 1 or endlich(k):
        kt = var if k == 1 else f"-{var}" if k == -1 else f"{zt(k)}{var}"
    else:
        kt = f"{'-' if k < 0 else ''}{abs(k.numerator) if abs(k.numerator) != 1 else ''}{var}/{k.denominator}"
    if d == 0:
        return kt
    return f"{kt} {'+' if d > 0 else '-'} {zt(abs(d))}"


def zahl(frage, loesung, aus, tipps, fehler=(), graph=None, tabelle=None, erklaerung=None, rechnung=None, einheit=None):
    a = {"typ": "zahl", "frage": frage, "loesung": zt(loesung)}
    if aus:
        a["aus_term"] = aus
    if rechnung:
        a["rechnung"] = rechnung
    if graph:
        a["graph"] = graph
    if tabelle:
        a["tabelle"] = tabelle
    if einheit:
        a["einheit"] = einheit
    a["tipps"] = tipps
    a["fehler"] = [{**f, "antwort": zt(F(f["antwort"]))} for f in fehler_zahlen(loesung, [(w, h) for w, h in fehler if w is not None])]
    if erklaerung:
        a["erklaerung"] = erklaerung
    return a


def bereich(werte, rand=1):
    lo, hi = min(werte), max(werte)
    return [int(min(lo, 0) - rand), int(max(hi, 0) + rand)]


# ── C1.1 Funktion oder nicht? ─────────────────────────────

JA_NEIN = ["Ja, das ist eine Funktion.", "Nein, das ist keine Funktion."]


def c1_1(r, s):
    n = {1: 4, 2: 5, 3: 6, 4: 7}[s]
    xs = r.sample(range(-5, 9), n)
    ys = [nz(r, -6, 9, ()) for _ in xs]
    fall = r.choice(["ja", "nein", "ja_gleiche_y"] if s >= 2 else ["ja", "nein"])
    if fall == "nein":
        i, j = r.sample(range(n), 2)
        xs[j] = xs[i]
        while ys[j] == ys[i]:
            ys[j] = nz(r, -6, 9, ())
    if fall == "ja_gleiche_y":
        i, j = r.sample(range(n), 2)
        ys[j] = ys[i]
    if s <= 2 and fall != "nein":
        xs, ys = zip(*sorted(zip(xs, ys)))
    if s == 4:
        ys = [F(y, 2) for y in ys]
    zeilen = [[zt(x), zt(y)] for x, y in zip(xs, ys)]
    ok = fall != "nein"
    erk = ("Jedem x-Wert ist **genau ein** y-Wert zugeordnet – also eine Funktion. "
           + ("Dass zwei x-Werte denselben y-Wert haben, ist erlaubt!" if fall == "ja_gleiche_y" else "")) if ok else \
        "Ein x-Wert kommt zweimal vor, mit **verschiedenen** y-Werten. Bei einer Funktion gehört zu jedem x genau ein y – also keine Funktion."
    return {"typ": "auswahl", "frage": "Ist diese Zuordnung x → y eine Funktion?", "optionen": JA_NEIN, "richtig": [0 if ok else 1],
            "tabelle": {"kopf": ["x", "y"], "zeilen": zeilen}, "pruefung": {"art": "funktion"}, "erklaerung": erk,
            "tipps": ["Bei einer Funktion gehört zu **jedem** x **genau ein** y.", "Kommt ein x-Wert zweimal vor? Mit demselben oder einem anderen y?"]}


# ── C1.2 Wertetabelle und Graph ───────────────────────────

def zufallsterm(r, s):
    if s == 1:
        return lin(nz(r, -3, 3), nz(r, -4, 4))
    if s == 2:
        return r.choice([f"x² {'-' if (c := nz(r, -5, 5)) < 0 else '+'} {abs(c)}", lin(nz(r, -4, 4), nz(r, -6, 6))])
    if s == 3:
        return r.choice([lin(F(nz(r, -3, 3), 2), nz(r, -4, 4)), f"-x² + {r.randint(1, 6)}", f"2x² - {r.randint(1, 5)}"])
    return r.choice([f"x² - {r.randint(1, 4)}x + {r.randint(0, 3)}", f"-x²/2 + {r.randint(1, 5)}", f"x³ - {r.randint(1, 3)}x"])


def c1_2(r, s):
    term = zufallsterm(r, s)
    import sympy  # noqa: PLC0415
    sys.path.insert(0, str(HIER.parent))
    import notation  # noqa: PLC0415
    t = notation.ausdruck(term)
    xw = nz(r, -3, 3, ()) if s > 1 else r.randint(0, 3)
    y = F(str(t.subs(sympy.Symbol("x"), xw)))
    if r.random() < .5 or s == 4 and abs(y) > 8:
        return zahl(f"Gegeben ist `f(x) = {term}`. Welcher Wert gehört in die Wertetabelle bei x = {xw}?", y,
                    {"term": term, "groesse": "wert", "x": xw},
                    [f"Setz {xw} für x ein: `f({xw})`.", "Negative Zahlen in Klammern einsetzen! `(-2)² = 4`.",
                     "Dann Hochzahl vor Punkt vor Strich."],
                    [(F(str(t.subs(sympy.Symbol("x"), -xw))), "Achte auf das Vorzeichen beim Einsetzen: negative Zahl in Klammern!")])
    # Ablesen am Graphen – nur bei glatten Werten
    xs = [F(v) for v in range(-4, 5)]
    ys = [F(str(t.subs(sympy.Symbol("x"), v))) for v in xs]
    if any(v.denominator not in (1, 2) for v in ys) or abs(y) > 8 or y.denominator != 1:
        return None
    sichtbar = [v for v in ys if abs(v) <= 9]
    graph = {"x": [-5, 5], "y": bereich(sichtbar + [y]), "kurven": [{"term": term, "name": "f"}]}
    return zahl(f"Das ist der Graph von f. Lies ab: Wie groß ist f({xw})?", y, {"term": term, "groesse": "wert", "x": xw},
                [f"Geh auf der x-Achse zu x = {xw}.", "Dann senkrecht hinauf (oder hinunter) bis zum Graphen.",
                 "Waagrecht hinüber zur y-Achse: Dort liest du den Funktionswert ab."],
                [], graph=graph)


# ── C1.3 Funktionswert und Argument ───────────────────────

def c1_3(r, s):
    k, d = nz(r, -5, 5), nz(r, -9, 9)
    term = lin(k, d)
    if r.random() < .5 or s == 1:
        xw = nz(r, -6, 6, ())
        return zahl(f"`f(x) = {term}`. Berechne `f({xw})`.", k * xw + d, {"term": term, "groesse": "wert", "x": xw},
                    [f"`f({xw})` heißt: Setz {xw} für x ein.", "Negative Zahlen in Klammern."],
                    [(k * -xw + d, "Vorzeichen beim Einsetzen!")])
    if s <= 3:
        x0 = F(nz(r, -6, 6, ())) if s == 2 else F(nz(r, -9, 9), r.choice([1, 2]))
        yw = k * x0 + d
        a = {"typ": "zahl", "frage": f"`f(x) = {term}`. Für welches x gilt `f(x) = {zt(yw)}`?", "loesung": zt(x0),
             "gleichung": f"{term} = {zt(yw)}", "weg": [f"{term} = {zt(yw)}", f"x = {zt(x0)}"],
             "tipps": ["Jetzt ist der Funktionswert gegeben, gesucht ist x.", f"Löse die Gleichung `{term} = {zt(yw)}`."],
             "fehler": [{"antwort": zt(k * yw + d), "hinweis": f"Das ist f({zt(yw)}). Gesucht ist das x, für das f(x) = {zt(yw)} herauskommt."}]
             if k * yw + d != x0 else []}
        return a
    n = nz(r, 1, 6)
    c = nz(r, -5, 5)
    term = f"x² {'+' if c > 0 else '-'} {abs(c)}"
    return {"typ": "quadratisch", "frage": f"`f(x) = {term}`. Für welche x gilt `f(x) = {n * n + c}`?",
            "gleichung": f"{term} = {n * n + c}", "loesung": f"{n}; -{n}",
            "weg": [f"{term} = {n * n + c}", f"x² = {n * n}", f"x = {n} oder x = -{n}"],
            "tipps": [f"Löse die Gleichung `{term} = {n * n + c}`.", "x² allein, dann Wurzel – plus und minus!"], "fehler": []}


# ── C1.4 Graphen im Kontext ───────────────────────────────

KONTEXT = [
    # (Term in x, x-Achse, y-Achse, Satz-Vorlage mit {x} und Einheit, x-Bereich, y-Bereich, Schritt)
    ("-x²/2 + 6x - 8", "t in h", "T in °C", "Temperatur T (in °C) im Lauf eines Tages, t = Uhrzeit. Wie warm ist es um {x} Uhr?", [0, 12], [-10, 12], [1, 2], "°C"),
    ("40 - 5x", "t in min", "V in l", "Wasser in einer Badewanne beim Auslaufen, t in Minuten. Wie viel Wasser ist nach {x} Minuten noch drin?", [0, 9], [0, 45], [1, 5], "l"),
    ("3x + 2", "t in Wochen", "h in cm", "Höhe einer Pflanze (in cm) nach t Wochen. Wie hoch ist die Pflanze nach {x} Wochen?", [0, 8], [0, 28], [1, 2], "cm"),
    ("2x² ", "t in s", "s in m", "Weg (in m) eines anrollenden Wagens nach t Sekunden. Wie weit ist er nach {x} Sekunden gekommen?", [0, 5], [0, 50], [1, 5], "m"),
]


def c1_4(r, s):
    term, ax, ay, satz, xb, yb, schritt, einheit = r.choice(KONTEXT)
    import sympy  # noqa: PLC0415
    sys.path.insert(0, str(HIER.parent))
    import notation  # noqa: PLC0415
    t = notation.ausdruck(term)
    xw = r.randint(max(1, xb[0]), xb[1] - 1)
    y = F(str(t.subs(sympy.Symbol("x"), xw)))
    if y.denominator != 1 or not (yb[0] <= y <= yb[1]):
        return None
    graph = {"x": xb, "y": yb, "kurven": [{"term": term}], "achsen": {"x": ax, "y": ay}, "schritt": schritt}
    if s >= 3 and r.random() < .6:
        xw2 = r.randint(xb[0], xb[1])
        if xw2 == xw:
            return None
        y2 = F(str(t.subs(sympy.Symbol("x"), xw2)))
        if y2.denominator != 1:
            return None
        a, b = sorted([xw, xw2])
        diff = F(str(t.subs(sympy.Symbol("x"), b) - t.subs(sympy.Symbol("x"), a)))
        return zahl(satz.split(".")[0] + f". Um wie viel ändert sich der Wert zwischen {a} und {b}? (Abnahme mit Minus.)", diff,
                    {"term": term, "groesse": "differenz", "von": a, "bis": b},
                    [f"Lies beide Werte ab: bei {a} und bei {b}.", "Änderung = späterer Wert − früherer Wert."],
                    [(-diff, "Späterer Wert minus früherer – nicht umgekehrt.")], graph=graph, einheit=einheit)
    return zahl(satz.format(x=xw), y, {"term": term, "groesse": "wert", "x": xw},
                [f"Geh auf der waagrechten Achse zu {xw}.", "Senkrecht zum Graphen, dann waagrecht zur senkrechten Achse – ablesen."],
                [], graph=graph, einheit=einheit)


# ── C1.5 Schreibweise f: x ↦ f(x) ─────────────────────────

def c1_5(r, s):
    term = zufallsterm(r, min(s + 1, 4))
    import sympy  # noqa: PLC0415
    sys.path.insert(0, str(HIER.parent))
    import notation  # noqa: PLC0415
    xw = nz(r, -4, 4, ())
    y = F(str(notation.ausdruck(term).subs(sympy.Symbol("x"), xw)))
    name = r.choice(["f", "g", "h"])
    return zahl(f"Die Funktion `{name}: ℝ → ℝ` ist gegeben durch `x ↦ {term}`. Berechne `{name}({xw})`.", y,
                {"term": term, "groesse": "wert", "x": xw},
                [f"`x ↦ {term}` heißt: Jedem x wird `{term}` zugeordnet. Das ist dasselbe wie `{name}(x) = {term}`.",
                 f"Setz {xw} ein – negative Zahlen in Klammern."], [])


# ── C2.1 k und d ablesen ──────────────────────────────────

KD_ERK = "In `f(x) = k·x + d` ist **k** die Zahl vor dem x (Steigung) und **d** die Zahl ohne x (Schnittpunkt mit der y-Achse)."


def c2_1(r, s):
    welche = r.choice(["k", "d"])
    if s == 1:
        k, d = nz(r, 1, 6), nz(r, 1, 9)
        term = lin(k, d)
    elif s == 2:
        k, d = nz(r, -6, 6), nz(r, -9, 9)
        term = r.choice([lin(k, d), f"{zt(d)} {'+' if k > 0 else '-'} {abs(k) if abs(k) != 1 else ''}x"])
    elif s == 3:
        k, d = r.choice([(F(nz(r, -5, 5), 2), nz(r, -6, 6)), (0, nz(r, -9, 9)), (nz(r, -4, 4), 0)])
        term = lin(k, d)
    else:
        a, b, c = nz(r, 2, 4), nz(r, -6, 6), nz(r, -9, 9)
        if r.random() < .5:
            term = f"({lin(b, c)})/{a}"
            k, d = F(b, a), F(c, a)
        else:
            term = f"{a}(x {'-' if b > 0 else '+'} {abs(b)}) {'+' if c > 0 else '-'} {abs(c)}"
            k, d = F(a), F(-a * b + c)
    wert = k if welche == "k" else d
    fehler = [(d, "Das ist d, die Zahl **ohne** x.")] if welche == "k" else [(k, "Das ist k, die Zahl **vor** dem x.")]
    return zahl(f"`f(x) = {term}`. Wie groß ist **{welche}**?", wert, {"term": term, "groesse": welche},
                [KD_ERK, "Steht die Gleichung nicht in der Form k·x + d, forme sie zuerst um (Klammer auflösen, Bruch aufteilen).",
                 "Das Vorzeichen gehört dazu!"], fehler)


# ── C2.2 Steigungsdreieck: k und d aus dem Graphen ────────

def gerade_graph(r, s):
    q = 1 if s <= 2 else r.choice([1, 2, 3])
    p = nz(r, -3, 3)
    k = F(p, q)
    d = nz(r, -4, 4) if s > 1 else r.randint(0, 4)
    if q == 1 and s >= 3 and r.random() < .5:
        return None
    return k, F(d), q


def c2_2(r, s):
    g = gerade_graph(r, s)
    if not g:
        return None
    k, d, q = g
    term = lin(k, d)
    x1 = 0 if s <= 2 else nz(r, -3, 0, ())
    x2 = x1 + q * (1 if s == 1 else r.choice([1, 2]) if q == 1 else 1)
    p1, p2 = (x1, k * x1 + d), (x2, k * x2 + d)
    if any(v.denominator != 1 for v in (F(p1[1]), F(p2[1]))) or max(abs(F(p1[1])), abs(F(p2[1]))) > 7:
        return None
    graph = {"x": [-5, 5], "y": [-7, 7], "kurven": [{"term": term, "name": "f"}],
             "punkte": [{"x": int(p1[0]), "y": int(p1[1]), "name": "A", "auf": 0}, {"x": int(p2[0]), "y": int(p2[1]), "name": "B", "auf": 0}]}
    if s >= 3 and r.random() < .4:
        return {"typ": "term", "frage": "Gib die Funktionsgleichung der Geraden an: `f(x) = …`", "form": "frei", "loesung": term,
                "graph": graph, "punkte": [[int(p1[0]), int(p1[1])], [int(p2[0]), int(p2[1])]],
                "tipps": ["d ist der Schnittpunkt mit der y-Achse.", "k: Geh von A nach B – wie viel nach oben (oder unten) pro Schritt nach rechts?",
                          "Dann `f(x) = k·x + d` hinschreiben."],
                "fehler": [{"antwort": lin(-k, d), "hinweis": "Steigt die Gerade oder fällt sie? Fällt sie, ist k negativ."}] if k != 0 else []}
    welche = r.choice(["k", "d"]) if s > 1 else "k"
    if welche == "k":
        return zahl("Lies aus dem Graphen die Steigung **k** ab (Steigungsdreieck zwischen A und B).", k, {"term": term, "groesse": "k"},
                    ["Steigungsdreieck: Geh von A aus waagrecht nach rechts bis unter/über B, dann senkrecht zu B.",
                     "`k = (Höhenunterschied) : (waagrechter Weg)`. Geht es nach unten, ist k negativ.",
                     f"Waagrecht sind es {x2 - x1} Einheiten."],
                    [(-k if k != 0 else None, "Achte auf das Vorzeichen: Fällt die Gerade (von links nach rechts), ist k negativ."),
                     (1 / k if k not in (0, 1, -1) else None, "Umgekehrt: Höhe **durch** Breite, nicht Breite durch Höhe.")],
                    graph=graph)
    return zahl("Lies aus dem Graphen **d** ab (wo schneidet die Gerade die y-Achse?).", d, {"term": term, "groesse": "d"},
                ["d ist der y-Wert, wo die Gerade die senkrechte Achse schneidet."], [], graph=graph)


# ── C2.3 Gleichung aus zwei Punkten ───────────────────────

def c2_3(r, s):
    q = 1 if s <= 2 else r.choice([1, 2])
    k = F(nz(r, -4, 4), q) if s > 1 else F(r.randint(1, 4))
    d = F(nz(r, -6, 6)) if s < 4 else F(nz(r, -9, 9), 2)
    x1 = nz(r, -4, 4) if s > 1 else r.randint(0, 3)
    x2 = x1 + q * r.randint(1, 3)
    y1, y2 = k * x1 + d, k * x2 + d
    if y1.denominator != 1 and s < 4 or y2.denominator != 1 and s < 4:
        return None
    term = lin(k, d)
    return {"typ": "term", "frage": f"Eine Gerade geht durch A({zt(x1)}|{zt(y1)}) und B({zt(x2)}|{zt(y2)}). Gib die Funktionsgleichung "
                                    "an: `f(x) = …`", "form": "frei", "loesung": term,
            "punkte": [[zt(x1), zt(y1)], [zt(x2), zt(y2)]],

            "tipps": ["Zuerst k: `k = (y₂ - y₁) : (x₂ - x₁)`.", "Dann d: Setz einen Punkt und k in `y = k·x + d` ein und löse nach d.",
                      f"k = {zt(k)}."],
            "fehler": [{"antwort": lin(1 / k, d) if k != 0 else lin(1, d), "hinweis": "Beim k: y-Differenz **durch** x-Differenz, nicht umgekehrt."}]
            if k not in (1, -1, 0) else []}


def kl(q):
    q = F(q)
    return f"({zt(q)})" if q < 0 else zt(q)


# ── C2.4 Wirkung von k und d ──────────────────────────────

def c2_4(r, s):
    eig = r.choice(["steilste", "fallend", "groesstes_d", "flachste"])
    for _ in range(50):
        ks = [F(nz(r, -5, 5), r.choice([1, 2] if s > 2 else [1])) for _ in range(3)]
        ds = [nz(r, -6, 6) for _ in range(3)]
        absk = [abs(k) for k in ks]
        if eig in ("steilste", "flachste") and len(set(absk)) < 3:
            continue
        if eig == "fallend" and sum(k < 0 for k in ks) != 1:
            continue
        if eig == "groesstes_d" and len(set(ds)) < 3:
            continue
        break
    else:
        return None
    optionen = [lin(k, d) for k, d in zip(ks, ds)]
    frage = {"steilste": "Welche Gerade ist am **steilsten**?", "fallend": "Welche Gerade **fällt** (von links nach rechts)?",
             "groesstes_d": "Welche Gerade schneidet die y-Achse am **höchsten**?", "flachste": "Welche Gerade verläuft am **flachsten**?"}[eig]
    if eig == "steilste":
        richtig = [absk.index(max(absk))]
    elif eig == "flachste":
        richtig = [absk.index(min(absk))]
    elif eig == "fallend":
        richtig = [i for i, k in enumerate(ks) if k < 0]
    else:
        richtig = [ds.index(max(ds))]
    a = {"typ": "auswahl", "frage": frage, "mathe": True, "optionen": optionen, "richtig": richtig,
         "pruefung": {"art": "k_eigenschaft", "eigenschaft": eig},
         "erklaerung": {"steilste": "Steil heißt: großer **Betrag** von k – das Vorzeichen zählt dabei nicht. −4 ist steiler als 3.",
                        "flachste": "Flach heißt: kleiner **Betrag** von k.",
                        "fallend": "Die Gerade fällt, wenn k **negativ** ist.",
                        "groesstes_d": "Wo die Gerade die y-Achse schneidet, sagt **d**. Gesucht ist das größte d."}[eig],
         "tipps": ["k bestimmt die Steigung, d die Höhe beim Schnitt mit der y-Achse."]}
    if s >= 3:
        a["graph"] = {"x": [-5, 5], "y": [-7, 7], "kurven": [{"term": o, "name": n} for o, n in zip(optionen, ["f", "g", "h"])]}

    return a


# ── C2.5 f(x + 1) = f(x) + k, Differenzenquotient ─────────

def c2_5(r, s):
    k, d = nz(r, -5, 6), nz(r, -9, 9)
    if s == 1:
        a, n = nz(r, -3, 3), r.randint(1, 4)
        fa = k * a + d
        return zahl(f"f ist linear mit k = {k}. Es gilt f({a}) = {fa}. Berechne f({a + n}).", fa + n * k, None,
                    [f"Wenn x um 1 größer wird, ändert sich f(x) um k = {k}.", f"x wird um {n} größer – also ändert sich f um {n}·{k}."],
                    [(fa + k, f"x wird um {n} größer, nicht nur um 1."), (fa * n, "Es wird k addiert, nicht multipliziert.")],
                    rechnung=f"{fa} + {n}·{kl(k)}")
    if s == 2:
        a, b = sorted(r.sample(range(-4, 8), 2))
        fa, fb = k * a + d, k * b + d
        return zahl(f"f ist linear, f({a}) = {fa} und f({b}) = {fb}. Wie groß ist k?", k, None,
                    ["k = (Änderung von f) : (Änderung von x).", f"`({fb} - {kl(fa)}) : ({b} - {kl(a)})`"],
                    [(F(b - a, fb - fa) if fb != fa else None, "Umgekehrt: Änderung von f **durch** Änderung von x.")],
                    rechnung=f"({fb} - {kl(fa)})/({b} - {kl(a)})")
    if s == 3:
        term = r.choice([f"x² - {r.randint(1, 4)}", f"0,5x² + {r.randint(0, 3)}", f"-x² + {r.randint(2, 8)}x"])
        a, b = sorted(r.sample(range(-2, 6), 2))
        import sympy  # noqa: PLC0415
        sys.path.insert(0, str(HIER.parent))
        import notation  # noqa: PLC0415
        t = notation.ausdruck(term)
        fa, fb = (F(str(t.subs(sympy.Symbol("x"), v))) for v in (a, b))
        tab = {"kopf": ["x", "f(x)"], "zeilen": [[str(v), zt(F(str(t.subs(sympy.Symbol("x"), v))))] for v in range(a, b + 1)]}
        return zahl(f"Berechne mit der Tabelle die **mittlere Änderungsrate** (Differenzenquotient) von f im Intervall [{a}; {b}].",
                    (fb - fa) / (b - a), {"term": term, "groesse": "steigung_mittel", "von": a, "bis": b},
                    ["Mittlere Änderungsrate = (f(b) − f(a)) : (b − a).", f"`({zt(fb)} - {kl(fa)}) : ({b} - {kl(a)})`"],
                    [(fb - fa, "Das ist nur die Änderung von f. Noch durch die Länge des Intervalls dividieren.")], tabelle=tab)
    kk = F(nz(r, -9, 9), 2)
    n = r.randint(2, 6)
    return zahl(f"`f(x) = {lin(kk, d)}`. Um wie viel ändert sich f(x), wenn x um {n} größer wird?", kk * n, None,
                ["Pro Schritt um 1 ändert sich f um k.", f"Hier also {n} · k."], [(kk, f"x wird um {n} größer, nicht nur um 1.")],
                rechnung=f"{n}·{kl(kk)}")


# ── C2.6 Lineare Modelle im Kontext ───────────────────────

MODELLE = [
    ("Ein Taxi verlangt {a} € Grundgebühr und {b} € pro gefahrenem Kilometer. Gib die Kosten K (in €) für s Kilometer an: `K(s) = …`",
     "s", "{a} + {b}s", "Was kostet eine Fahrt von {x} km?", "€"),
    ("Eine Kerze ist {a} cm hoch und brennt pro Stunde {b} cm ab. Gib die Höhe h (in cm) nach t Stunden an: `h(t) = …`",
     "t", "{a} - {b}t", "Wie hoch ist die Kerze nach {x} Stunden?", "cm"),
    ("Ein Handytarif kostet {a} € im Monat plus {b} € pro Gigabyte. Gib die Monatskosten für g Gigabyte an: `K(g) = …`",
     "g", "{a} + {b}g", "Was kostet ein Monat mit {x} GB?", "€"),
    ("In einem Tank sind {a} Liter Heizöl. Pro Tag werden {b} Liter verbraucht. Gib die Menge nach t Tagen an: `V(t) = …`",
     "t", "{a} - {b}t", "Wie viel ist nach {x} Tagen noch im Tank?", "l"),
]


def c2_6(r, s):
    satz, var, vorlage, frage2, einheit = r.choice(MODELLE)
    a = r.choice([3, 4, 5, 12, 20, 24, 30, 800, 1500]) if "Liter" in satz else r.choice([3, 4, 5, 12, 20, 24, 30])
    b = r.choice([F(1, 2), F(3, 2), F(6, 5), 2, 3, F(5, 2)]) if "Liter" not in satz else r.choice([8, 12, 15, 20, 25])
    term = vorlage.format(a=a, b=zt(b))
    if s <= 2:
        return {"typ": "term", "frage": satz.format(a=a, b=zt(b)), "form": "frei", "loesung": term,
                "punkte": [[0, a], [2, zt(a + (2 * b if "+" in vorlage else -2 * b))]], "variable": var,
                "tipps": ["Was ist der Startwert (bei 0)? Das ist d.", f"Um wie viel ändert sich der Wert pro Einheit von {var}? Das ist k.",
                          "Abnahme heißt: k ist negativ."],
                "fehler": [{"antwort": vorlage.replace("+", "-").format(a=a, b=zt(b)) if "+" in vorlage else vorlage.replace("-", "+").format(a=a, b=zt(b)),
                            "hinweis": "Prüf das Vorzeichen: Wird der Wert mit der Zeit mehr oder weniger?"}]}
    xw = r.randint(2, 9)
    wert = a + xw * b if "+" in vorlage else a - xw * b
    if wert < 0:
        return None
    return zahl(satz.format(a=a, b=zt(b)).split("Gib")[0] + frage2.format(x=xw), wert, None,
                [f"Stell zuerst die Funktion auf: `{term}`.", f"Setz {xw} für {var} ein."],
                [(a + xw * b if "-" in vorlage else a - xw * b, "Prüf das Vorzeichen: wird es mehr oder weniger?")],
                rechnung=term.replace(var, f"·{xw}"), einheit=einheit)


# ── C2.7 Schnittpunkt zweier Geraden ──────────────────────

def c2_7(r, s):
    x0, y0 = nz(r, -4, 4, ()), nz(r, -5, 5, ())
    k1, k2 = nz(r, -3, 3), nz(r, -3, 3)
    if k1 == k2:
        return None
    d1, d2 = y0 - k1 * x0, y0 - k2 * x0
    f1, f2 = lin(k1, d1), lin(k2, d2)
    a = {"typ": "lgs", "frage": f"Berechne den Schnittpunkt S der Geraden `f(x) = {f1}` und `g(x) = {f2}`.",
         "gleichungen": [f"y = {f1}", f"y = {f2}"], "loesung": {"x": zt(x0), "y": zt(y0)},
         "weg": [f"{f1} = {f2} | gleichsetzen", f"x = {x0}", f"y = {y0} | in f einsetzen"],
         "tipps": ["Im Schnittpunkt haben beide Funktionen denselben Wert: `f(x) = g(x)` – gleichsetzen!",
                   "Löse nach x. Dann x in f einsetzen, um y zu bekommen.", "Antwort z. B. als `x = 2, y = 3` oder `(2|3)`."],
         "fehler": []}
    if s >= 2 and abs(y0) <= 6 and abs(x0) <= 4:
        a["graph"] = {"x": [-5, 5], "y": [-7, 7], "kurven": [{"term": f1, "name": "f"}, {"term": f2, "name": "g"}]}
    return a


# ── C2.8 Ist ein lineares Modell angemessen? ──────────────

def c2_8(r, s):
    xs = list(range(0, 5)) if s <= 2 else sorted(r.sample(range(0, 12), 5))
    linear = r.random() < .5
    k, d = F(nz(r, -9, 12), 2 if s >= 3 else 1), r.randint(0, 30)
    if linear:
        ys = [k * x + d for x in xs]
    else:
        q = r.choice([F(3, 2), 2, F(1, 2)])
        ys = [F(d + 2) * q ** x for x in xs] if r.random() < .5 else [F(x * x) + d for x in xs]
    if any(not endlich(y) or (y * 100).denominator != 1 for y in ys):
        return None
    tab = {"kopf": ["x", "y"], "zeilen": [[str(x), zt(y)] for x, y in zip(xs, ys)]}
    return {"typ": "auswahl", "frage": "Passt ein **lineares** Modell `y = k·x + d` genau zu dieser Tabelle?",
            "optionen": ["Ja, linear.", "Nein, nicht linear."], "richtig": [0 if linear else 1], "tabelle": tab,
            "pruefung": {"art": "linear_tabelle"},
            "erklaerung": ("Bei gleichen Schritten in x ändert sich y immer um gleich viel (pro Einheit um k) – linear."
                           if linear else "Die Änderungen von y pro Einheit von x sind **nicht** gleich – kein lineares Modell."),
            "tipps": ["Berechne für jeden Schritt: (Änderung von y) : (Änderung von x).",
                      "Ist das immer dieselbe Zahl, ist es linear." + (" Achtung: Die x-Schritte sind nicht alle gleich groß!" if s >= 3 else "")]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HIER.parent))
    r = random.Random(20261025)
    for lid, fn, n in [("C1.1", c1_1, 8), ("C1.2", c1_2, 8), ("C1.3", c1_3, 8), ("C1.4", c1_4, 6), ("C1.5", c1_5, 6),
                       ("C2.1", c2_1, 8), ("C2.2", c2_2, 8), ("C2.3", c2_3, 8), ("C2.4", c2_4, 8), ("C2.5", c2_5, 8),
                       ("C2.6", c2_6, 6), ("C2.7", c2_7, 8), ("C2.8", c2_8, 8)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "c12.py")


if __name__ == "__main__":
    main()
