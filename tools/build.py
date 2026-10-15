"""
Build: Inhalte prüfen und App-Daten erzeugen.

  inhalte/<fach>/lernpfad.yaml                 Struktur (einzige Quelle)
  inhalte/<fach>/<Kapitel>/<ID>.yaml           Erklärung, Beispiel, handgeschriebene Aufgaben
  inhalte/<fach>/<Kapitel>/<ID>.aufgaben.yaml  erzeugte Aufgaben (tools/generatoren/)

Erzeugt:
  app/daten/<fach>/lernpfad.json, app/daten/<fach>/<ID>.json
  app/sw.js (Offline-Cache mit Dateiliste und Versionsstempel)
  docs/LERNPFAD.md

Jede Mathe-Lösung wird mit sympy nachgerechnet. Bei einem einzigen Fehler bricht der Build ab
und schreibt nichts.
"""

import hashlib
import json
import math
import re
import shutil
import sys
from pathlib import Path

import sympy
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notation  # noqa: E402

BASIS = Path(__file__).resolve().parent.parent
INHALTE = BASIS / "inhalte"
APP = BASIS / "app"
DATEN = APP / "daten"

FAECHER = ["mathe"]
STUFEN = {1, 2, 3, 4}
TYPEN = {"gleichung", "zahl", "auswahl", "term", "formel", "ungleichung", "lgs", "quadratisch"}


class Fehlerliste(list):
    def melde(self, wo: str, was: str):
        self.append(f"{wo}: {was}")


# ── Prüfungen ─────────────────────────────────────────────

def soll_menge(loesung) -> sympy.Set:
    text = str(loesung).strip()
    if text == "keine":
        return sympy.S.EmptySet
    if text == "alle":
        return sympy.S.Reals
    return sympy.FiniteSet(*[notation.zahl(t) for t in text.split(";")])


def gleichungsteil(zeile: str) -> str:
    """'3x = 15 | −5' → '3x = 15'"""
    return zeile.split("|")[0].strip()


def pruefe_gleichung(a: dict, wo: str, fehler: Fehlerliste):
    try:
        ist = notation.loesungsmenge(a["gleichung"])
        soll = soll_menge(a["loesung"])
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"nicht lesbar ({e})")
        return
    if ist != soll:
        fehler.melde(wo, f"Lösung {a['loesung']!r} stimmt nicht – sympy: {ist}")
        return
    for zeile in a.get("weg", []):
        teil = gleichungsteil(zeile)
        if "=" not in teil:
            continue
        try:
            if notation.loesungsmenge(teil) != ist:
                fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} ist keine Äquivalenzumformung")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} nicht lesbar ({e})")
    for f in a.get("fehler", []):
        try:
            if notation.zahl(str(f["antwort"])) in ist:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Fehler-Antwort {f.get('antwort')!r} nicht lesbar ({e})")


def pruefe_zahl(a: dict, wo: str, fehler: Fehlerliste):
    try:
        soll = notation.zahl(str(a["loesung"]))
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Lösung nicht lesbar ({e})")
        return
    pruefe_zahlform(a, wo, fehler)
    if "aus_term" in a:
        try:
            if sympy.simplify(aus_term(a["aus_term"]) - soll) != 0:
                fehler.melde(wo, f"{a['aus_term']} ergibt nicht {a['loesung']!r}")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"aus_term nicht prüfbar ({e})")
    if "formel_faktor" in a:
        pruefe_faktor(a, wo, fehler, soll)
    if "grad_regel" in a:
        # Polynom vom Grad n: höchstens n Nullstellen, n − 1 Extremstellen, n − 2 Wendestellen
        n, art = a["grad_regel"]["grad"], a["grad_regel"]["art"]
        erwartet = {"nullstellen": n, "extremstellen": n - 1, "wendestellen": n - 2}[art]
        if erwartet != soll:
            fehler.melde(wo, f"Grad {n}, {art}: höchstens {erwartet}, nicht {a['loesung']}")
    if "term" in a:
        # Einsetzen: term mit werte {x: -2} muss die Lösung ergeben
        try:
            werte = {sympy.Symbol(k): notation.zahl(str(v)) for k, v in a["werte"].items()}
            if sympy.simplify(notation.ausdruck(a["term"]).subs(werte) - soll) != 0:
                fehler.melde(wo, f"{a['term']!r} mit {a['werte']} ergibt nicht {a['loesung']!r}")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Einsetzen nicht prüfbar ({e})")
    if "rechnung" in a:
        try:
            diff = abs(notation.zahl(a["rechnung"]) - soll)
            # gerundet: n → die Lösung ist die auf n Nachkommastellen gerundete Rechnung
            erlaubt = sympy.Rational(1, 2 * 10 ** a["gerundet"]) if "gerundet" in a else 0
            if diff > erlaubt or (not erlaubt and sympy.simplify(diff) != 0):
                fehler.melde(wo, f"Rechnung {a['rechnung']!r} ergibt nicht {a['loesung']!r}")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Rechnung nicht lesbar ({e})")
    if "gleichung" in a:
        try:
            menge = notation.loesungsmenge(a["gleichung"])
            if soll not in menge:
                fehler.melde(wo, f"{a['loesung']!r} löst die Gleichung {a['gleichung']!r} nicht")
            for zeile in a.get("weg", []):
                teil = gleichungsteil(zeile)
                if "=" in teil and notation.loesungsmenge(teil) != menge:
                    fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} ist keine Äquivalenzumformung")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Gleichung nicht lesbar ({e})")
    if "gleichung" not in a:
        exakt = notation.zahl(a["rechnung"]) if "gerundet" in a else soll
        # Rechenweg als Kette: „1/2 + 1/3 = 3/6 + 2/6 = 5/6“ – jedes Glied muss den Wert der Lösung haben
        for zeile in a.get("weg", []):
            for teil in zeile.split("|")[0].split("="):
                try:
                    if teil.strip() and sympy.simplify(notation.zahl(teil) - exakt) != 0:
                        fehler.melde(wo, f"Rechenweg {zeile!r}: {teil.strip()!r} hat einen anderen Wert")
                except Exception as e:  # noqa: BLE001
                    fehler.melde(wo, f"Rechenweg {zeile!r} nicht lesbar ({e})")
    for f in a.get("fehler", []):
        try:
            if sympy.simplify(notation.zahl(str(f["antwort"])) - soll) == 0:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Fehler-Antwort nicht lesbar ({e})")


def gleicher_term(t1: str, t2: str) -> bool:
    return sympy.simplify(notation.ausdruck(t1) - notation.ausdruck(t2)) == 0


TERM_FORMEN = {"zusammengefasst", "ausmultipliziert", "faktor", "gekuerzt", "potenz", "frei"}


def pruefe_term(a: dict, wo: str, fehler: Fehlerliste):
    """Term-Aufgabe: Ausgangsterm (oder Text) → gleichwertiger Term in einer verlangten Form."""
    if a.get("form") not in TERM_FORMEN:
        fehler.melde(wo, f"Form fehlt oder unbekannt: {a.get('form')!r}")
    if not (a.get("term") or a.get("frage")):
        fehler.melde(wo, "Term oder Frage fehlt")
    try:
        for px_, py_ in a.get("punkte", []):
            wert = notation.ausdruck(a["loesung"]).subs(sympy.Symbol(a.get("variable", "x")), notation.zahl(str(px_)))
            if sympy.simplify(wert - notation.zahl(str(py_))) != 0:
                fehler.melde(wo, f"Lösung {a['loesung']!r} geht nicht durch ({px_}|{py_})")
        if a.get("term") and not gleicher_term(a["term"], a["loesung"]):
            fehler.melde(wo, f"Lösung {a['loesung']!r} ist nicht gleich {a['term']!r}")
        if a.get("form") == "faktor":
            q = sympy.cancel(notation.ausdruck(a["loesung"]) / notation.ausdruck(a["faktor"]))
            if sympy.fraction(q)[1].free_symbols:
                fehler.melde(wo, f"Faktor {a['faktor']!r} steckt nicht in {a['loesung']!r}")
        for zeile in a.get("weg", []):
            for teil in zeile.split("|")[0].split("="):
                if teil.strip() and not gleicher_term(teil, a["loesung"]):
                    fehler.melde(wo, f"Lösungsweg {zeile!r}: {teil.strip()!r} ist nicht gleich")
        for f in a.get("fehler", []):
            if gleicher_term(str(f["antwort"]), a["loesung"]):
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Term nicht lesbar ({e})")


def positiv(expr):
    """Formelgrößen (Längen, Flächen, Zeiten …) sind positiv – sonst wäre √(d²) nicht d."""
    return expr.subs({s: sympy.Symbol(s.name, positive=True) for s in expr.free_symbols})


def formel_seiten(text: str):
    links, rechts = text.split("=")
    return positiv(notation.ausdruck(links)), positiv(notation.ausdruck(rechts))


def pruefe_formel(a: dict, wo: str, fehler: Fehlerliste):
    """Formel nach einer Variablen umformen: loesung ist die rechte Seite von „nach = …“."""
    try:
        nach = sympy.Symbol(a["nach"], positive=True)
        links, rechts = formel_seiten(a["formel"])
        soll = positiv(notation.ausdruck(a["loesung"]))
        if nach in soll.free_symbols:
            fehler.melde(wo, f"Lösung enthält noch {a['nach']}")
        kandidaten = sympy.solve(sympy.Eq(links, rechts), nach)
        if not any(sympy.simplify(k - soll) == 0 for k in kandidaten):
            fehler.melde(wo, f"Lösung {a['loesung']!r} stimmt nicht – sympy: {kandidaten}")
        for zeile in a.get("weg", []):
            l, r = formel_seiten(zeile.split("|")[0])
            if sympy.simplify((l - r).subs(nach, soll)) != 0:
                fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} folgt nicht aus der Formel")
        for f in a.get("fehler", []):
            if sympy.simplify(positiv(notation.ausdruck(f["antwort"])) - soll) == 0:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Formel nicht lesbar ({e})")


def pruefe_faktor(a: dict, wo: str, fehler: Fehlerliste, soll):
    """„r wird verdoppelt – mit welchem Faktor ändert sich A?“: Verhältnis neu/alt der rechten Seite."""
    try:
        p = a["formel_faktor"]
        _, rechts = formel_seiten(p["formel"])
        neu = rechts.subs({sympy.Symbol(k, positive=True): sympy.Symbol(k, positive=True) * notation.zahl(str(v)) for k, v in p["aenderung"].items()},
                          simultaneous=True)
        if sympy.simplify(neu / rechts - soll) != 0:
            fehler.melde(wo, f"Faktor stimmt nicht: sympy {sympy.simplify(neu / rechts)}")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Faktor nicht prüfbar ({e})")


def q_menge(text: str):
    """Lösungsmenge aus „x = 3 oder x = -2“, „3; -2“, „x = 3 ± √2“, „keine“ – oder aus einer Gleichung in x."""
    t = text.strip()
    if t in ("keine", "{ }", "{}"):
        return sympy.S.EmptySet
    teile = [s for s in re.split(r"\s*(?:;|\boder\b|,(?!\d))\s*", re.sub(r"x\s*[₁₂12]", "x", t)) if s]
    aufzaehlung = len(teile) > 1 or "±" in t or re.fullmatch(r"x\s*=\s*[^x]+", t) or "x" not in t
    if aufzaehlung:
        werte = []
        for teil in teile:
            if "=" in teil:
                links, rechts = teil.split("=")
                if links.strip() != "x":
                    # lineare Teilgleichung wie „x + 4 = ±3“
                    for g in ([teil.replace("±", "+", 1), teil.replace("±", "-", 1)] if "±" in teil else [teil]):
                        werte += list(notation.loesungsmenge(g))
                    continue
                teil = rechts
            if "±" in teil:
                werte += [notation.zahl(teil.replace("±", "+", 1)), notation.zahl(teil.replace("±", "-", 1))]
            else:
                werte.append(notation.zahl(teil))
        return sympy.FiniteSet(*[sympy.nsimplify(sympy.simplify(w)) for w in werte])
    return notation.loesungsmenge(t)


def pruefe_quadratisch(a: dict, wo: str, fehler: Fehlerliste):
    try:
        soll = q_menge(str(a["loesung"]))
        if a.get("gleichung"):
            ist = notation.loesungsmenge(a["gleichung"])
            if ist != soll:
                fehler.melde(wo, f"Lösung {a['loesung']!r} stimmt nicht – sympy: {ist}")
        for zeile in a.get("weg", []):
            if q_menge(zeile.split("|")[0]) != soll:
                fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} hat eine andere Lösungsmenge")
        for f in a.get("fehler", []):
            if q_menge(str(f["antwort"])) == soll:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Quadratische Gleichung nicht lesbar ({e})")


def lgs_loesung(gleichungen):
    x, y = sympy.symbols("x y")
    system = [notation.gleichung(g) for g in gleichungen]
    menge = sympy.linsolve(system, x, y)
    if menge == sympy.S.EmptySet:
        return "keine"
    (px, py), = menge
    if px.free_symbols or py.free_symbols:
        return "unendlich"
    return (px, py)


def pruefe_lgs(a: dict, wo: str, fehler: Fehlerliste):
    try:
        ist = lgs_loesung(a["gleichungen"])
        soll = a["loesung"]
        if isinstance(soll, dict):
            soll_paar = (notation.zahl(str(soll["x"])), notation.zahl(str(soll["y"])))
            if ist != soll_paar:
                fehler.melde(wo, f"Lösung {soll} stimmt nicht – sympy: {ist}")
                return
            x, y = sympy.symbols("x y")
            for zeile in a.get("weg", []):
                for teil in re.split(r"\s*(?:;|,(?!\d))\s*", zeile.split("|")[0]):
                    if "=" in teil and sympy.simplify(notation.gleichung(teil).subs({x: soll_paar[0], y: soll_paar[1]})) != 0:
                        fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} stimmt nicht für die Lösung")
            for f in a.get("fehler", []):
                if (notation.zahl(str(f["x"])), notation.zahl(str(f["y"]))) == soll_paar:
                    fehler.melde(wo, f"Fehler-Antwort {f} ist in Wahrheit richtig")
        elif ist != soll:
            fehler.melde(wo, f"Lösung {soll!r} stimmt nicht – sympy: {ist}")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Gleichungssystem nicht lesbar ({e})")


REL = [("<=", "≤"), (">=", "≥"), ("≤", "≤"), ("≥", "≥"), ("<", "<"), (">", ">")]


def ungleichung_menge(text: str):
    """„3 - 2x ≤ 7“ oder „]-∞; 3[“ → sympy-Menge in ℝ"""
    t = text.replace(" ", "")
    m = re.fullmatch(r"([\]\[(])(.+);(.+)([\[\])])", t)
    if m:
        l, a, b, r = m.groups()
        unten = -sympy.oo if a in ("-∞", "−∞") else notation.zahl(a)
        oben = sympy.oo if b in ("∞", "+∞") else notation.zahl(b)
        return sympy.Interval(unten, oben, left_open=l != "[", right_open=r != "]")
    for zeichen, rel in REL:
        if zeichen in text:
            links, rechts = text.split(zeichen)
            x = sympy.Symbol("x")
            L, R = notation.ausdruck(links), notation.ausdruck(rechts)
            ausdruck = {"≤": L <= R, "≥": L >= R, "<": L < R, ">": L > R}[rel]
            return sympy.solveset(ausdruck, x, domain=sympy.S.Reals)
    raise ValueError(f"keine Ungleichung: {text!r}")


def pruefe_ungleichung(a: dict, wo: str, fehler: Fehlerliste):
    try:
        soll = ungleichung_menge(a["loesung"])
        if a.get("ungleichung") and ungleichung_menge(a["ungleichung"]) != soll:
            fehler.melde(wo, f"Lösung {a['loesung']!r} stimmt nicht – sympy: {ungleichung_menge(a['ungleichung'])}")
        for zeile in a.get("weg", []):
            if ungleichung_menge(zeile.split("|")[0]) != soll:
                fehler.melde(wo, f"Lösungsweg-Zeile {zeile!r} ist keine Äquivalenzumformung")
        for f in a.get("fehler", []):
            if ungleichung_menge(f["antwort"]) == soll:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Ungleichung nicht lesbar ({e})")


def aus_term(p: dict):
    """k, d, Funktionswert oder Nullstelle eines Funktionsterms in x"""
    x = sympy.Symbol("x")
    t = notation.ausdruck(p["term"])
    g = p["groesse"]
    if g == "k":
        return sympy.diff(t, x) if sympy.degree(t, x) <= 1 else None
    if g == "d":
        return t.subs(x, 0)
    if g == "wert":
        return t.subs(x, notation.zahl(str(p["x"])))
    if g == "nullstelle":
        (n,) = sympy.solve(t, x)
        return n
    if g in ("scheitel_x", "scheitel_y"):
        xs = sympy.solve(sympy.diff(t, x), x)[0]
        return xs if g == "scheitel_x" else t.subs(x, xs)
    if g == "grad":
        return sympy.degree(t, x)
    if g in ("hochpunkt_x", "hochpunkt_y", "tiefpunkt_x", "tiefpunkt_y"):
        d1, d2 = sympy.diff(t, x), sympy.diff(t, x, 2)
        stellen = [s for s in sympy.solve(d1, x) if s.is_real and (d2.subs(x, s) < 0) == g.startswith("hoch") and d2.subs(x, s) != 0]
        if len(stellen) != 1:
            raise ValueError(f"{g}: nicht eindeutig ({stellen})")
        return stellen[0] if g.endswith("_x") else t.subs(x, stellen[0])
    if g == "differenz":
        a, b = notation.zahl(str(p["von"])), notation.zahl(str(p["bis"]))
        return t.subs(x, b) - t.subs(x, a)
    if g == "steigung_mittel":
        a, b = notation.zahl(str(p["von"])), notation.zahl(str(p["bis"]))
        return (t.subs(x, b) - t.subs(x, a)) / (b - a)
    raise ValueError(f"unbekannte Größe {g!r}")


def pruefe_graph(a: dict, wo: str, fehler: Fehlerliste):
    """Graphen und Tabellen müssen lesbar sein; Punkte im Bild müssen auf der Kurve liegen, wenn markiert."""
    g = a.get("graph")
    if g:
        try:
            for k in g.get("kurven", []):
                notation.ausdruck(k["term"])
            if not (g["x"][0] < g["x"][1] and g["y"][0] < g["y"][1]):
                fehler.melde(wo, "Graph-Bereich ungültig")
            for p in g.get("punkte", []):
                if "auf" in p:
                    k = g["kurven"][p["auf"]]
                    wert = notation.ausdruck(k["term"]).subs(sympy.Symbol("x"), notation.zahl(str(p["x"])))
                    if sympy.simplify(wert - notation.zahl(str(p["y"]))) != 0:
                        fehler.melde(wo, f"Punkt {p} liegt nicht auf {k['term']!r}")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Graph nicht lesbar ({e})")
    t = a.get("tabelle")
    if t and any(len(z) != len(t["kopf"]) for z in t["zeilen"]):
        fehler.melde(wo, "Tabelle: Zeilen passen nicht zum Kopf")


def pruefe_zahlform(a: dict, wo: str, fehler: Fehlerliste):
    """form: gekuerzt | nenner | dezimal – die Lösung selbst muss die verlangte Form haben."""
    form, l = a.get("form"), str(a["loesung"]).replace(" ", "")
    teile = l.lstrip("-").split("/")
    if form == "gekuerzt":
        if not all(t.isdigit() for t in teile) or (len(teile) == 2 and math.gcd(int(teile[0]), int(teile[1])) != 1):
            fehler.melde(wo, f"Lösung {l!r} ist kein gekürzter Bruch")
    elif form == "nenner":
        if len(teile) != 2 or teile[1] != str(a.get("nenner")):
            fehler.melde(wo, f"Lösung {l!r} hat nicht den Nenner {a.get('nenner')!r}")
    elif form == "dezimal":
        if "/" in l:
            fehler.melde(wo, f"Lösung {l!r} ist keine Dezimalzahl")
    elif form == "gleitkomma":
        m = re.fullmatch(r"-?(\d+(?:[.,]\d+)?)·10\^\(?-?\d+\)?", l)
        if not m or not (1 <= float(m.group(1).replace(",", ".")) < 10):
            fehler.melde(wo, f"Lösung {l!r} ist keine Gleitkommadarstellung")
    elif form is not None:
        fehler.melde(wo, f"unbekannte Form {form!r}")


def pruefe_auswahl(a: dict, wo: str, fehler: Fehlerliste):
    optionen, richtig = a.get("optionen", []), a.get("richtig", [])
    if len(optionen) < 2:
        fehler.melde(wo, "Auswahl braucht mindestens 2 Optionen")
    if not richtig or any(not (0 <= i < len(optionen)) for i in richtig):
        fehler.melde(wo, f"'richtig' ungültig: {richtig}")
        return
    p = a.get("pruefung")
    if not p:
        return
    try:
        if p["art"] in ("wert", "termgleich"):
            # Optionen sind Zahlen bzw. Terme; richtig sind genau die, die gleich dem Ziel sind
            if p["art"] == "wert":
                ziel = notation.zahl(str(p["ziel"]))
                erwartet = [i for i, o in enumerate(optionen) if sympy.simplify(notation.zahl(o) - ziel) == 0]
            else:
                erwartet = [i for i, o in enumerate(optionen) if gleicher_term(o, p["ziel"])]
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "monoton":
            # Optionen sind Intervalle „[a; b]“; richtig: f ist dort durchgehend steigend bzw. fallend (Stichproben von f′)
            x = sympy.Symbol("x")
            d1 = sympy.diff(notation.ausdruck(p["term"]), x)
            erwartet = []
            for i, o in enumerate(optionen):
                lo, hi = [notation.zahl(v) for v in o.strip("[]").split(";")]
                werte_ = [d1.subs(x, lo + (hi - lo) * sympy.Rational(k, 40)) for k in range(1, 40)]
                if all(w > 0 for w in werte_) if p["richtung"] == "steigend" else all(w < 0 for w in werte_):
                    erwartet.append(i)
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "funktionstyp":
            x = sympy.Symbol("x")
            t = notation.ausdruck(p["term"])
            if t.is_polynomial(x):
                n = sympy.degree(t, x)
                typ = "linear" if n == 1 else "quadratisch" if n == 2 else "Polynomfunktion vom Grad 3 oder höher"
            elif any(x in pw.exp.free_symbols for pw in t.atoms(sympy.Pow)) or t.has(sympy.exp):
                typ = "exponentiell"
            else:
                typ = "Potenzfunktion (z. B. a/x, √x)"
            if [optionen[i] for i in richtig] != [typ]:
                fehler.melde(wo, f"'richtig' = {[optionen[i] for i in richtig]}, sympy sagt {typ!r}")
            return
        if p["art"] == "oeffnung":
            # Optionen 0 = nach oben, 1 = nach unten
            a2 = sympy.Poly(notation.ausdruck(p["term"]), sympy.Symbol("x")).coeff_monomial(sympy.Symbol("x") ** 2)
            if sorted(richtig) != [0 if a2 > 0 else 1]:
                fehler.melde(wo, f"'richtig' = {richtig}, a = {a2}")
            return
        if p["art"] == "grad":
            # Optionen sind Gradzahlen als Text
            n = sympy.degree(notation.ausdruck(p["term"]), sympy.Symbol("x"))
            if [optionen[i] for i in richtig] != [str(n)]:
                fehler.melde(wo, f"'richtig' = {richtig}, Grad ist {n}")
            return
        if p["art"] == "lin_exp":
            # Optionen 0 = linear, 1 = exponentiell, 2 = weder noch (gleiche x-Schritte vorausgesetzt)
            zeilen = a["tabelle"]["zeilen"]
            xs = [notation.zahl(str(z[0])) for z in zeilen]
            ys = [notation.zahl(str(z[1])) for z in zeilen]
            if len({xs[i + 1] - xs[i] for i in range(len(xs) - 1)}) != 1:
                fehler.melde(wo, "lin_exp braucht gleiche x-Schritte")
                return
            diffs = {sympy.simplify(ys[i + 1] - ys[i]) for i in range(len(ys) - 1)}
            quot = {sympy.simplify(ys[i + 1] / ys[i]) for i in range(len(ys) - 1)} if all(y != 0 for y in ys) else {None, 0}
            erwartet = [0] if len(diffs) == 1 else [1] if len(quot) == 1 else [2]
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "funktion":
            # Optionen 0 = Ja (ist eine Funktion), 1 = Nein; Tabelle aus der Aufgabe
            zuordnung = {}
            for xw, yw in a["tabelle"]["zeilen"]:
                if zuordnung.setdefault(str(xw), str(yw)) != str(yw):
                    ok = False
                    break
            else:
                ok = True
            if sorted(richtig) != [0 if ok else 1]:
                fehler.melde(wo, f"'richtig' = {richtig}, aber Funktion = {ok}")
            return
        if p["art"] == "linear_tabelle":
            # Optionen 0 = Ja (linear), 1 = Nein: gleiche x-Schritte → gleiche y-Schritte?
            xs = [notation.zahl(str(z[0])) for z in a["tabelle"]["zeilen"]]
            ys = [notation.zahl(str(z[1])) for z in a["tabelle"]["zeilen"]]
            steig = {sympy.simplify((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])) for i in range(len(xs) - 1)}
            if sorted(richtig) != [0 if len(steig) == 1 else 1]:
                fehler.melde(wo, f"'richtig' = {richtig}, Steigungen {steig}")
            return
        if p["art"] == "k_eigenschaft":
            # Optionen sind lineare Terme; richtig ist, was die Eigenschaft erfüllt
            x = sympy.Symbol("x")
            ks = [sympy.Poly(notation.ausdruck(o), x).coeff_monomial(x) for o in optionen]
            ds = [notation.ausdruck(o).subs(x, 0) for o in optionen]
            e = p["eigenschaft"]
            if e == "steilste":
                erwartet = [i for i, k in enumerate(ks) if abs(k) == max(abs(v) for v in ks)]
            elif e == "fallend":
                erwartet = [i for i, k in enumerate(ks) if k < 0]
            elif e == "groesstes_d":
                erwartet = [i for i, d in enumerate(ds) if d == max(ds)]
            elif e == "flachste":
                erwartet = [i for i, k in enumerate(ks) if abs(k) == min(abs(v) for v in ks)]
            else:
                raise ValueError(e)
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "q_anzahl":
            # Optionen: 0 = zwei reelle Lösungen, 1 = eine, 2 = keine
            n = len(notation.loesungsmenge(p["gleichung"]))
            erwartet = [{2: 0, 1: 1, 0: 2}[n]]
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "lgs_anzahl":
            # Optionen: 0 = genau eine Lösung, 1 = keine, 2 = unendlich viele
            ist = lgs_loesung(p["gleichungen"])
            erwartet = [1] if ist == "keine" else [2] if ist == "unendlich" else [0]
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "intervall":
            # Optionen sind Intervalle/Ungleichungen; richtig sind die mit derselben Lösungsmenge wie das Ziel
            ziel = ungleichung_menge(p["ziel"])
            erwartet = [i for i, o in enumerate(optionen) if ungleichung_menge(o) == ziel]
            if sorted(richtig) != erwartet:
                fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
            return
        if p["art"] == "zahlenmenge":
            # Optionen ℕ, ℤ, ℚ, ℝ, ℂ – richtig ist die kleinste Menge, zu der die Zahl gehört (ℕ mit 0)
            v = sympy.nsimplify(notation.ausdruck(str(p["zahl"])))
            stufe = (0 if v.is_integer and v >= 0 else 1 if v.is_integer else 2 if v.is_rational
                     else 3 if v.is_real else 4)
            if optionen != ["ℕ", "ℤ", "ℚ", "ℝ", "ℂ"] or richtig != [stufe]:
                fehler.melde(wo, f"Zahlenmenge von {p['zahl']!r}: richtig wäre {stufe}, angegeben {richtig}")
            return
        menge = notation.loesungsmenge(p["gleichung"])
        if p["art"] == "einsetzen":
            # Optionen: 0 = Ja, 1 = Nein
            erwartet = [0] if notation.zahl(str(p["wert"])) in menge else [1]
        elif p["art"] == "anzahl":
            # Optionen: 0 = genau eine, 1 = keine, 2 = unendlich viele
            if menge == sympy.S.EmptySet:
                erwartet = [1]
            elif menge == sympy.S.Reals:
                erwartet = [2]
            else:
                erwartet = [0]
        else:
            fehler.melde(wo, f"unbekannte Prüfart {p['art']!r}")
            return
        if sorted(richtig) != erwartet:
            fehler.melde(wo, f"'richtig' = {richtig}, sympy sagt {erwartet}")
    except Exception as e:  # noqa: BLE001
        fehler.melde(wo, f"Prüfung nicht lesbar ({e})")


PRUEFER = {"gleichung": pruefe_gleichung, "zahl": pruefe_zahl, "auswahl": pruefe_auswahl, "term": pruefe_term,
           "formel": pruefe_formel, "ungleichung": pruefe_ungleichung, "lgs": pruefe_lgs,
           "quadratisch": pruefe_quadratisch}


def pruefe_aufgabe(a: dict, wo: str, fehler: Fehlerliste):
    if a.get("typ") not in TYPEN:
        fehler.melde(wo, f"unbekannter Typ {a.get('typ')!r}")
        return
    if a.get("stufe") not in STUFEN:
        fehler.melde(wo, f"Stufe fehlt oder ungültig: {a.get('stufe')!r}")
    tipps = a.get("tipps", [])
    if a["typ"] != "auswahl" and not (1 <= len(tipps) <= 3):
        fehler.melde(wo, f"1–3 Tipps erwartet, gefunden {len(tipps)}")
    PRUEFER[a["typ"]](a, wo, fehler)
    pruefe_graph(a, wo, fehler)


# ── Laden ─────────────────────────────────────────────────

def lade_yaml(pfad: Path):
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def baue_fach(fach: str, fehler: Fehlerliste):
    ordner = INHALTE / fach
    pfad = lade_yaml(ordner / "lernpfad.yaml")
    ausgaben: dict[str, dict] = {}
    gesehen_ls: set[str] = set()
    gesehen_aufg: set[str] = set()

    for teil in pfad["teile"]:
        for kap in teil["kapitel"]:
            for ls in kap["lernschritte"]:
                lid = ls["id"]
                if lid in gesehen_ls:
                    fehler.melde(lid, "Lernschritt-ID doppelt")
                gesehen_ls.add(lid)
                datei = ordner / kap["id"] / f"{lid}.yaml"
                if not datei.exists():
                    ls["verfuegbar"] = False
                    continue
                inhalt = lade_yaml(datei)
                if inhalt.get("id") != lid:
                    fehler.melde(str(datei), f"id {inhalt.get('id')!r} passt nicht zu {lid!r}")
                aufgaben = list(inhalt.get("aufgaben") or [])
                erzeugt = ordner / kap["id"] / f"{lid}.aufgaben.yaml"
                if erzeugt.exists():
                    aufgaben += lade_yaml(erzeugt) or []
                texte: set[str] = set()
                for a in aufgaben:
                    aid = a.get("id", "?")
                    text = (a.get("frage") or a.get("gleichung") if a.get("typ") in ("gleichung", "quadratisch") else a.get("frage") or a.get("ungleichung") if a.get("typ") == "ungleichung" else
                            a.get("frage") or " | ".join(a.get("gleichungen", [])) if a.get("typ") == "lgs" else
                            f"{a.get('formel')} nach {a.get('nach')}" if a.get("typ") == "formel" else a.get("frage") or a.get("term"))
                    text = f"{text} {json.dumps(a.get('graph'), sort_keys=True)} {json.dumps(a.get('tabelle'))} {a.get('optionen')}"
                    if text in texte:
                        fehler.melde(aid, f"Aufgabe doppelt im Lernschritt: {text!r}")
                    texte.add(text)
                    if aid in gesehen_aufg:
                        fehler.melde(aid, "Aufgaben-ID doppelt")
                    gesehen_aufg.add(aid)
                    pruefe_aufgabe(a, f"{lid}/{aid}", fehler)
                for zeile in (inhalt.get("beispiel") or {}).get("weg", []):
                    teil_gl = gleichungsteil(zeile)
                    g = (inhalt.get("beispiel") or {}).get("gleichung")
                    if g and "=" in teil_gl and "loesung" not in (inhalt.get("beispiel") or {}):
                        try:
                            if notation.loesungsmenge(teil_gl) != notation.loesungsmenge(g):
                                fehler.melde(lid, f"Beispiel-Zeile {zeile!r} ist keine Äquivalenzumformung")
                        except Exception as e:  # noqa: BLE001
                            fehler.melde(lid, f"Beispiel-Zeile {zeile!r} nicht lesbar ({e})")
                bsp = inhalt.get("beispiel") or {}
                pruefe_graph(bsp, f"{lid}/Beispiel", fehler)
                if bsp.get("gleichung") and bsp.get("loesung") is not None:
                    pruefe_quadratisch({**bsp, "fehler": []}, f"{lid}/Beispiel", fehler)
                if bsp.get("gleichungen"):
                    pruefe_lgs(bsp, f"{lid}/Beispiel", fehler)
                if bsp.get("ungleichung"):
                    try:
                        soll_u = ungleichung_menge(bsp["ungleichung"])
                        for zeile in bsp.get("weg", []):
                            if ungleichung_menge(zeile.split("|")[0]) != soll_u:
                                fehler.melde(lid, f"Beispiel-Zeile {zeile!r} ist keine Äquivalenzumformung")
                    except Exception as e:  # noqa: BLE001
                        fehler.melde(lid, f"Beispiel nicht lesbar ({e})")
                if bsp.get("formel"):
                    pruefe_formel({**bsp, "fehler": []}, f"{lid}/Beispiel", fehler)
                if bsp.get("term") or bsp.get("wert"):
                    # Beispiel als Kette: jedes Glied gleich dem Term bzw. Wert
                    for zeile in bsp.get("weg", []):
                        for teil in zeile.split("|")[0].split("="):
                            if not teil.strip():
                                continue
                            try:
                                gleich = (gleicher_term(teil, bsp["term"]) if bsp.get("term")
                                          else sympy.simplify(notation.zahl(teil) - notation.zahl(str(bsp["wert"]))) == 0)
                                if not gleich:
                                    fehler.melde(lid, f"Beispiel {zeile!r}: {teil.strip()!r} stimmt nicht")
                            except Exception as e:  # noqa: BLE001
                                fehler.melde(lid, f"Beispiel {zeile!r} nicht lesbar ({e})")
                stufen = {s: sum(1 for a in aufgaben if a.get("stufe") == s) for s in STUFEN}
                ls["titel"] = inhalt.get("titel", ls["titel"])  # Inhaltsdatei hat den kurzen Titel
                ls["verfuegbar"] = bool(aufgaben)
                ls["anzahl"] = len(aufgaben)
                ausgaben[lid] = {**inhalt, "titel": inhalt.get("titel", ls["titel"]), "aufgaben": aufgaben,
                                 "kapitel": kap["id"]}
                print(f"  {lid:6} {len(aufgaben):4} Aufgaben  (Stufe 1/2/3/4: {stufen[1]}/{stufen[2]}/{stufen[3]}/{stufen[4]})")
    return pfad, ausgaben


# ── Ausgabe ───────────────────────────────────────────────

def schreibe_lernpfad_md(pfad: dict):
    zeilen = ["# Lernpfad Mathematik", "",
              "> Erzeugt von `tools/build.py` aus `inhalte/mathe/lernpfad.yaml` – hier nicht bearbeiten.", "",
              pfad["einleitung"].rstrip(), ""]
    gesamt = kern = fertig = 0
    for teil in pfad["teile"]:
        zeilen += ["---", "", f"## Teil {teil['id']} – {teil['titel']}", ""]
        for kap in teil["kapitel"]:
            if teil["id"] != "G":
                zeilen += [f"### {kap['id']} {kap['titel']}", ""]
            zeilen += ["| ID | Lernschritt | GK | in der App |", "|----|-------------|----|-----|"]
            for ls in kap["lernschritte"]:
                gesamt += 1
                kern += bool(ls.get("kern"))
                fertig += bool(ls.get("verfuegbar"))
                stern = " ★" if ls.get("kern") else ""
                da = f"✓ {ls['anzahl']}" if ls.get("verfuegbar") else ""
                zeilen.append(f"| {ls['id']}{stern} | {ls['titel']} | {ls.get('gk', '')} | {da} |")
            zeilen.append("")
    zeilen += ["---", "", f"**Umfang:** {gesamt} Lernschritte, davon {kern} im Kernpfad (★). "
               f"In der App verfügbar: {fertig}.", ""]
    (BASIS / "docs" / "LERNPFAD.md").write_text("\n".join(zeilen), encoding="utf-8")


ERZEUGT = {"sw.js", "js/version.js"}


def schreibe_sw():
    """Versionsstempel = Hash über alle App-Dateien. Ändert sich etwas, lädt das iPad neu."""
    dateien = sorted(p.relative_to(APP).as_posix() for p in APP.rglob("*")
                     if p.is_file() and p.relative_to(APP).as_posix() not in ERZEUGT)
    h = hashlib.sha256()
    for d in dateien:
        h.update(d.encode())
        h.update((APP / d).read_bytes())
    version = h.hexdigest()[:12]
    (APP / "js" / "version.js").write_text(
        f'// Erzeugt von tools/build.py\nwindow.APP_VERSION = "{version}";\n', encoding="utf-8")
    vorlage = (BASIS / "tools" / "sw_vorlage.js").read_text(encoding="utf-8")
    sw = (vorlage.replace("__VERSION__", version)
                 .replace("__DATEIEN__", json.dumps(["./"] + dateien + ["js/version.js"], indent=2)))
    (APP / "sw.js").write_text(sw, encoding="utf-8")
    return version, len(dateien) + 1


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows-Konsole ist sonst cp1252
    fehler = Fehlerliste()
    ergebnisse = {}
    for fach in FAECHER:
        print(f"Fach {fach}:")
        ergebnisse[fach] = baue_fach(fach, fehler)

    if fehler:
        print(f"\nBUILD ABGEBROCHEN – {len(fehler)} Fehler:")
        for f in fehler:
            print("  ✗", f)
        sys.exit(1)

    if DATEN.exists():
        shutil.rmtree(DATEN)
    for fach, (pfad, ausgaben) in ergebnisse.items():
        ziel = DATEN / fach
        ziel.mkdir(parents=True)
        (ziel / "lernpfad.json").write_text(json.dumps(pfad, ensure_ascii=False), encoding="utf-8")
        for lid, inhalt in ausgaben.items():
            (ziel / f"{lid}.json").write_text(json.dumps(inhalt, ensure_ascii=False), encoding="utf-8")
        if fach == "mathe":
            schreibe_lernpfad_md(pfad)
    version, n = schreibe_sw()
    gesamt = sum(len(i["aufgaben"]) for _, a in ergebnisse.values() for i in a.values())
    print(f"\nOK – {gesamt} Aufgaben geprüft, {n} Dateien im Offline-Cache, Version {version}")


if __name__ == "__main__":
    main()
