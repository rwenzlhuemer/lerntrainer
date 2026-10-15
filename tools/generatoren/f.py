"""
Generator für Teil F (Statistik und Wahrscheinlichkeit). Einmal laufen lassen:

    python tools/generatoren/f.py

Jede Lösung wird beim Build unabhängig berechnet (statistik, laplace, urne, binom, erwartungswert, normal_p …).
"""

import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, schreibe, z  # noqa: E402


def zt(q):
    q = F(q)
    return dez(q) if q.denominator != 1 and endlich(q) and q.denominator <= 1000 else z(q)


def liste(werte):
    return "; ".join(zt(v) for v in werte)


def median(d):
    d = sorted(d)
    m = len(d)
    return d[m // 2] if m % 2 else (d[m // 2 - 1] + d[m // 2]) / 2


def zahl(frage, loesung, tipps, fehler=(), gerundet=None, **extra):
    a = {"typ": "zahl", "frage": frage}
    if gerundet is not None:
        exakt = endlich(F(loesung)) and (F(loesung) * 10 ** gerundet).denominator == 1
        a["loesung"] = zt(loesung) if exakt else f"{float(loesung):.{gerundet}f}".replace(".", ",")
        a["gerundet"] = gerundet
    else:
        a["loesung"] = zt(loesung)
    a.update({k: v for k, v in extra.items() if v is not None})
    a["tipps"] = tipps
    a["fehler"] = [f for f in fehler_zahlen(F(loesung), [(w, h) for w, h in fehler if w is not None])
                   if abs(F(f["antwort"]) - F(loesung)) > F(1, 100)]
    return a


# ── F1 Beschreibende Statistik ────────────────────────────

MONATE = ["Jän", "Feb", "Mär", "Apr", "Mai", "Jun"]
TAGE = ["Mo", "Di", "Mi", "Do", "Fr"]


def f1_1(r, s):
    kat = r.choice([MONATE, TAGE])
    n = len(kat)
    faktor = {1: 1, 2: 5, 3: 10, 4: 25}[s]
    werte = [r.randint(1, 9) * faktor for _ in kat]
    diagramm = {"kategorien": kat, "werte": werte, "achse": "Besucher"}
    art = r.choice(["wert", "differenz", "summe"] if s < 3 else ["differenz", "summe", "anteil_prozent"])
    i, j = r.sample(range(n), 2)
    if art == "wert":
        return zahl(f"Wie viele Besucher waren es laut Diagramm am {kat[i]}?" if kat is TAGE else f"Wie viele Besucher waren es im {kat[i]}?",
                    werte[i], ["Geh zur Säule und lies an der senkrechten Achse ab."], diagramm=diagramm,
                    aus_daten={"werte": werte, "art": "wert", "i": i})
    if art == "differenz":
        return zahl(f"Um wie viele Besucher waren es am {kat[i]} mehr als am {kat[j]}? (weniger: mit Minus)" if kat is TAGE else
                    f"Um wie viele Besucher waren es im {kat[i]} mehr als im {kat[j]}? (weniger: mit Minus)", werte[i] - werte[j],
                    ["Beide Werte ablesen, dann subtrahieren."], [(werte[j] - werte[i], "Reihenfolge: erster Wert minus zweiter.")],
                    diagramm=diagramm, aus_daten={"werte": werte, "art": "differenz", "i": i, "j": j})
    if art == "summe":
        return zahl("Wie viele Besucher waren es insgesamt?", sum(werte), ["Alle Säulen ablesen und addieren."], diagramm=diagramm,
                    aus_daten={"werte": werte, "art": "summe"})
    anteil = F(werte[i] * 100, sum(werte))
    return zahl(f"Wie viel Prozent aller Besucher kamen {'am' if kat is TAGE else 'im'} {kat[i]}? (auf eine Nachkommastelle)", anteil,
                ["Anteil = Teil : Ganzes.", f"Teil: {werte[i]}, Ganzes: Summe aller Säulen. Dann mal 100."],
                [(F(werte[i], sum(werte)), "Noch mal 100 für Prozent.")], gerundet=1, diagramm=diagramm,
                aus_daten={"werte": werte, "art": "anteil_prozent", "i": i}, einheit="%")


def daten(r, s, n=None):
    n = n or {1: 5, 2: 6, 3: 7, 4: 8}[s]
    if s <= 2:
        return [r.randint(1, 20) for _ in range(n)]
    if s == 3:
        return [r.randint(10, 60) for _ in range(n)]
    return [F(r.randint(10, 99), 10) for _ in range(n)]


def f1_2(r, s):
    d = daten(r, s)
    art = r.choice(["mittelwert", "median"] + (["modus"] if s <= 2 else []))
    if art == "modus":
        d[1] = d[3]
        if sum(1 for v in set(d) if d.count(v) == max(d.count(w) for w in d)) != 1:
            return None
    text = liste(d)
    if art == "mittelwert":
        mw = F(sum(d), len(d))
        return zahl(f"Berechne den **Mittelwert** (arithmetisches Mittel) der Daten: {text}", mw,
                    ["Alle Werte addieren, dann durch die Anzahl dividieren.", f"Es sind {len(d)} Werte."],
                    [(median(d), "Das ist der Median. Der Mittelwert ist Summe : Anzahl.")], gerundet=2,
                    statistik={"daten": [zt(v) for v in d], "groesse": "mittelwert"})
    if art == "median":
        return zahl(f"Bestimme den **Median** der Daten: {text}", median(d),
                    ["Zuerst der Größe nach **ordnen**!", "Der Median steht in der Mitte. Bei gerader Anzahl: Mittelwert der beiden mittleren Werte."],
                    [(d[len(d) // 2], "Zuerst ordnen – der Median ist der mittlere Wert der **geordneten** Liste.")],
                    statistik={"daten": [zt(v) for v in d], "groesse": "median"})
    modus = max(set(d), key=d.count)
    return zahl(f"Bestimme den **Modus** (häufigsten Wert) der Daten: {text}", modus, ["Welcher Wert kommt am öftesten vor?"],
                statistik={"daten": [zt(v) for v in d], "groesse": "modus"})


def f1_3(r, s):
    if r.random() < .5 or s == 1:
        noten = [1, 2, 3, 4, 5]
        anz = [r.randint(0, 8) for _ in noten]
        if sum(anz) == 0:
            return None
        mw = F(sum(n * a for n, a in zip(noten, anz)), sum(anz))
        tab = {"kopf": ["Note", "Anzahl"], "zeilen": [[str(n), str(a)] for n, a in zip(noten, anz)]}
        return zahl("Berechne den **Notendurchschnitt** der Klasse (gewogenes Mittel).", mw,
                    ["Jede Note mal ihre Anzahl, alles addieren.", "Dann durch die Gesamtzahl der Schülerinnen und Schüler dividieren."],
                    [(F(sum(noten), 5), "Die Noten kommen verschieden oft vor – jede mit ihrer Anzahl gewichten.")], gerundet=2,
                    tabelle=tab, gewogen={"werte": noten, "gewichte": anz})
    d = daten(r, 2, 6)
    ausreisser = r.choice([80, 95, 120])
    d2 = d + [ausreisser]
    art = r.choice(["mittelwert", "median"])
    wert_ = F(sum(d2), len(d2)) if art == "mittelwert" else median(d2)
    return zahl(f"Daten: {liste(d2)}. Berechne den **{'Mittelwert' if art == 'mittelwert' else 'Median'}**. "
                f"(Beachte den Ausreißer {ausreisser}.)", wert_,
                ["Mittelwert: Summe : Anzahl. Median: ordnen, mittlerer Wert.",
                 "Der Mittelwert wird von Ausreißern stark beeinflusst, der Median kaum."], gerundet=2,
                statistik={"daten": [zt(v) for v in d2], "groesse": art})


def f1_4(r, s):
    d = daten(r, s, {1: 7, 2: 8, 3: 9, 4: 11}[s])
    art = r.choice(["q1", "q3", "iqr"] if s >= 2 else ["q1", "q3"])
    ds = sorted(d)
    n = len(ds)
    unten, oben = ds[: n // 2], ds[(n + 1) // 2:]
    wert_ = {"q1": median(unten), "q3": median(oben), "iqr": median(oben) - median(unten)}[art]
    name = {"q1": "das **untere Quartil** q₁", "q3": "das **obere Quartil** q₃", "iqr": "den **Interquartilsabstand** q₃ − q₁"}[art]
    return zahl(f"Daten: {liste(d)}. Bestimme {name}.", wert_,
                ["Ordne die Daten und bestimme den Median.", "q₁ ist der Median der unteren Hälfte, q₃ der Median der oberen Hälfte "
                 "(bei ungerader Anzahl ohne den mittleren Wert).", "Interquartilsabstand = q₃ − q₁."],
                [], statistik={"daten": [zt(v) for v in d], "groesse": art})


def f1_5(r, s):
    d = daten(r, min(s, 3), 5)
    art = "spannweite" if s <= 2 else "varianz"
    if art == "spannweite":
        return zahl(f"Daten: {liste(d)}. Wie groß ist die **Spannweite**?", max(d) - min(d), ["Spannweite = größter Wert − kleinster Wert."], [],
                    statistik={"daten": [zt(v) for v in d], "groesse": "spannweite"})
    mw = F(sum(d), len(d))
    var = sum((v - mw) ** 2 for v in d) / len(d)
    return zahl(f"Daten: {liste(d)}. Berechne die **Varianz** (mittlere quadratische Abweichung vom Mittelwert; durch n dividieren).", var,
                [f"Mittelwert: {zt(mw) if endlich(mw) else z(mw)}.", "Von jedem Wert den Mittelwert abziehen, quadrieren, alles addieren, durch n."],
                [], gerundet=2, statistik={"daten": [zt(v) for v in d], "groesse": "varianz"})


# ── F2 Wahrscheinlichkeit ─────────────────────────────────

W6 = list(range(1, 7))
LAPLACE = {
    1: [("Ein Würfel wird geworfen. Wie groß ist die Wahrscheinlichkeit für eine **Sechs**?", [W6], "a == 6"),
        ("Ein Würfel wird geworfen. Wie groß ist die Wahrscheinlichkeit für eine **gerade** Zahl?", [W6], "a % 2 == 0"),
        ("Ein Würfel wird geworfen. Wie groß ist die Wahrscheinlichkeit für eine Zahl **größer als 4**?", [W6], "a > 4"),
        ("Ein Würfel wird geworfen. Wie groß ist die Wahrscheinlichkeit für **keine** Sechs?", [W6], "a != 6"),
        ("Ein Würfel wird geworfen. Wie groß ist die Wahrscheinlichkeit für eine Zahl **höchstens 2**?", [W6], "a <= 2")],
    2: [("Zwei Münzen werden geworfen (K = Kopf, Z = Zahl). Wie groß ist die Wahrscheinlichkeit für **zweimal Kopf**?", [["K", "Z"]] * 2, "a == 'K' and b == 'K'"),
        ("Zwei Münzen werden geworfen. Wie groß ist die Wahrscheinlichkeit für **genau einmal Kopf**?", [["K", "Z"]] * 2, "(a == 'K') + (b == 'K') == 1"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für einen **Pasch** (zwei gleiche Zahlen)?", [W6, W6], "a == b"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für die **Augensumme 7**?", [W6, W6], "a + b == 7"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für **zwei Sechsen**?", [W6, W6], "a == 6 and b == 6")],
    3: [("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für eine **Augensumme von mindestens 10**?", [W6, W6], "a + b >= 10"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für **mindestens eine Sechs**?", [W6, W6], "a == 6 or b == 6"),
        ("Drei Münzen werden geworfen. Wie groß ist die Wahrscheinlichkeit für **genau zweimal Kopf**?", [["K", "Z"]] * 3, "(a == 'K') + (b == 'K') + (c == 'K') == 2"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit, dass das **Produkt** der Augenzahlen **12** ist?", [W6, W6], "a * b == 12"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für eine **Augensumme kleiner als 5**?", [W6, W6], "a + b < 5")],
    4: [("Drei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für **drei gleiche** Zahlen?", [W6] * 3, "a == b == c"),
        ("Drei Münzen werden geworfen. Wie groß ist die Wahrscheinlichkeit für **mindestens einmal Zahl**?", [["K", "Z"]] * 3, "'Z' in (a, b, c)"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit, dass die **Differenz** der Augenzahlen **2** beträgt?", [W6, W6], "abs(a - b) == 2"),
        ("Drei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit für die **Augensumme 4**?", [W6] * 3, "a + b + c == 4"),
        ("Zwei Würfel werden geworfen. Wie groß ist die Wahrscheinlichkeit, dass **beide Zahlen gerade** sind?", [W6, W6], "a % 2 == 0 and b % 2 == 0")],
}


def f2_3(r, s):
    frage, raum, bed = r.choice(LAPLACE[s])
    from itertools import product
    namen = "abc"[: len(raum)]
    alle = list(product(*raum))
    gunst = sum(1 for e in alle if eval(bed, {"__builtins__": {"abs": abs}}, dict(zip(namen, e))))  # noqa: S307
    p = F(gunst, len(alle))
    return zahl(frage + " (als Bruch oder Dezimalzahl)", p,
                ["Laplace: P = günstige Fälle : mögliche Fälle.", f"Mögliche Fälle: {len(alle)}." + (" Schreib sie als Paare (1|1), (1|2), … auf." if len(raum) > 1 else ""),
                 "Zähle die günstigen Fälle sorgfältig."],
                [(F(gunst, 6 * len(raum)) if len(raum) > 1 else None, f"Bei {len(raum)} Würfen/Würfeln gibt es mehr mögliche Fälle: alle Kombinationen.")],
                laplace={"raum": raum, "bedingung": bed})


def f2_1(r, s):
    if s == 2:
        w, m = r.randint(1, 3), r.randint(1, 3)
        return zahl(f"Es werden {w} Würfel und {m} Münzen gleichzeitig geworfen. Wie viele Ergebnisse hat der Grundraum?", 6 ** w * 2 ** m,
                    ["Jeder Würfel hat 6, jede Münze 2 Möglichkeiten.", "Alle Anzahlen werden miteinander multipliziert."],
                    [(6 * w + 2 * m, "Multiplizieren, nicht addieren: Jede Möglichkeit kombiniert sich mit jeder anderen.")],
                    rechnung=f"6^{w}·2^{m}")
    if s == 1:
        k = r.randint(1, 3)
        art = r.choice(["wuerfel", "muenze"])
        n = 6 ** k if art == "wuerfel" else 2 ** k
        return zahl(f"Wie viele Ergebnisse hat der Grundraum, wenn {'ein Würfel' if art == 'wuerfel' else 'eine Münze'} {k}-mal geworfen wird?",
                    n, ["Jeder Wurf hat gleich viele Möglichkeiten. Die Anzahlen werden multipliziert.",
                        f"{6 if art == 'wuerfel' else 2} hoch {k}."], [(6 * k if art == "wuerfel" else 2 * k, "Multiplizieren, nicht addieren: jede Möglichkeit des ersten Wurfs mit jeder des zweiten.")],
                    rechnung=f"{6 if art == 'wuerfel' else 2}^{k}")
    p = r.choice([F(1, 6), F(1, 4), F(2, 5), F(3, 10), F(7, 20), F(1, 8), F(5, 6), F(3, 8), F(9, 20), F(1, 20), F(2, 3), F(7, 10), F(13, 25)])
    return zahl(f"Die Wahrscheinlichkeit für ein Ereignis E ist P(E) = {zt(p)}. Wie groß ist die Wahrscheinlichkeit des **Gegenereignisses** ¬E?",
                1 - p, ["Ereignis und Gegenereignis ergeben zusammen 1.", "P(¬E) = 1 − P(E)."], [(p, "Das ist P(E). Gesucht ist 1 − P(E).")],
                rechnung=f"1 - {zt(p)}")


def f2_2(r, s):
    n = r.choice([50, 80, 120, 200, 250, 400, 500])
    k = r.randint(1, n // 2)
    p = F(k, n)
    if s >= 3:
        m = r.choice([1000, 2000, 5000])
        return zahl(f"Bei {n} Versuchen trat ein Ereignis {k}-mal auf. Wie oft ist es bei {m} Versuchen ungefähr zu erwarten?", p * m,
                    ["Relative Häufigkeit als Schätzwert für die Wahrscheinlichkeit: k : n.", f"Dann mal {m}."], [], gerundet=0,
                    rechnung=f"{k}/{n}·{m}")
    return zahl(f"Bei {n} Würfen mit einem Reißnagel landete er {k}-mal auf der Spitze. Wie groß ist die **relative Häufigkeit** (als Dezimalzahl)?",
                p, ["Relative Häufigkeit = Anzahl : Gesamtzahl."], [(F(n, k), "Umgekehrt: Anzahl **durch** Gesamtzahl.")], gerundet=3,
                rechnung=f"{k}/{n}")


def f2_4(r, s):
    rot, blau = r.randint(2, 6), r.randint(2, 6)
    zurueck = s <= 2 and r.random() < .6 or s == 1
    zuege = 2 if s < 4 else 3
    ziel = r.choice(["zwei rote", "genau eine rote", "zwei gleiche Farben"] if zuege == 2 else ["drei rote", "genau zwei rote"])
    bed = {"zwei rote": "zug == 'rr'", "genau eine rote": "zug.count('r') == 1", "zwei gleiche Farben": "zug in ('rr', 'bb')",
           "drei rote": "zug == 'rrr'", "genau zwei rote": "zug.count('r') == 2"}[ziel]
    from itertools import product
    gesamt = F(0)
    for folge in product("rb", repeat=zuege):
        rest = {"r": rot, "b": blau}
        p = F(1)
        for k in folge:
            p *= F(rest[k], sum(rest.values())) if rest[k] else 0
            if not zurueck:
                rest[k] -= 1
        if eval(bed, {"__builtins__": {}}, {"zug": "".join(folge)}):  # noqa: S307
            gesamt += p
    naiv = F(rot, rot + blau) ** zuege if ziel in ("zwei rote", "drei rote") and not zurueck else None
    return zahl(f"In einer Urne sind {rot} rote und {blau} blaue Kugeln. Es werden {zuege} Kugeln {'mit' if zurueck else 'ohne'} Zurücklegen "
                f"gezogen. Wie groß ist die Wahrscheinlichkeit für **{ziel}**? (Bruch oder Dezimalzahl)", gesamt,
                ["Zeichne ein Baumdiagramm.", "Entlang eines Pfades wird **multipliziert** (Pfadregel), passende Pfade werden **addiert**.",
                 "Ohne Zurücklegen: Beim zweiten Zug ist eine Kugel weniger in der Urne." if not zurueck else "Mit Zurücklegen bleiben die Wahrscheinlichkeiten gleich."],
                [(naiv, "Ohne Zurücklegen ändert sich die Wahrscheinlichkeit beim zweiten Zug: eine Kugel weniger!")], gerundet=4,
                urne={"kugeln": {"r": rot, "b": blau}, "zuege": zuege, "zuruecklegen": zurueck, "bedingung": bed})


def f2_5(r, s):
    n = r.randint(2, 4) if s <= 2 else r.randint(4, 10)
    p = r.choice([F(1, 6), F(1, 2), F(1, 10), F(1, 4)] if s <= 3 else [F(3, 100), F(5, 100), F(2, 10)])
    ereignis = {F(1, 6): "eine Sechs", F(1, 2): "Kopf", F(1, 10): "einen Treffer", F(1, 4): "einen Gewinn"}.get(p, "einen Defekt")
    wert_ = 1 - (1 - p) ** n
    return zahl(f"Ein Versuch mit der Erfolgswahrscheinlichkeit {zt(p)} wird {n}-mal unabhängig wiederholt. Wie groß ist die Wahrscheinlichkeit für "
                f"**mindestens** {ereignis}? (auf vier Nachkommastellen)", wert_,
                ["„Mindestens einmal“ rechnet man am besten über das Gegenereignis „kein einziges Mal“.",
                 f"P(nie) = {zt(1 - p)}^{n}.", "P(mindestens einmal) = 1 − P(nie)."],
                [(n * p if n * p < 1 else None, "Wahrscheinlichkeiten darf man hier nicht einfach addieren – über das Gegenereignis rechnen."),
                 ((1 - p) ** n, "Das ist P(nie). Gesucht ist 1 − P(nie).")], gerundet=4,
                binom={"n": n, "p": zt(p), "k": 1, "art": "mindestens"})


# ── F3 Zufallsvariable, Binomialverteilung ────────────────

def f3_1(r, s):
    k = 4 if s <= 2 else 5
    nenner = r.choice([10, 20, 100])
    teile = sorted(r.sample(range(1, nenner), k - 1))
    ps = [F(b - a, nenner) for a, b in zip([0] + teile, teile + [nenner])]
    if any(p == 0 for p in ps):
        return None
    luecke = r.randrange(k)
    tab = {"kopf": ["x", "P(X = x)"], "zeilen": [[str(i), "?" if i == luecke else zt(p)] for i, p in enumerate(ps)]}
    return zahl("Die Tabelle zeigt die Wahrscheinlichkeitsverteilung einer Zufallsvariablen X. Welche Wahrscheinlichkeit fehlt?", ps[luecke],
                ["Alle Wahrscheinlichkeiten zusammen ergeben 1.", "Fehlender Wert = 1 − Summe der anderen."], [],
                tabelle=tab, rechnung="1 - (" + " + ".join(zt(p) for i, p in enumerate(ps) if i != luecke) + ")")


def f3_2(r, s):
    k = 3 if s <= 2 else 4
    werte = sorted(r.sample(range(-5 if s >= 3 else 0, 11), k))
    nenner = r.choice([4, 5, 10, 20])
    teile = sorted(r.sample(range(1, nenner), k - 1))
    ps = [F(b - a, nenner) for a, b in zip([0] + teile, teile + [nenner])]
    ew = sum(w * p for w, p in zip(werte, ps))
    tab = {"kopf": ["x", "P(X = x)"], "zeilen": [[str(w), zt(p)] for w, p in zip(werte, ps)]}
    ctx = "Gewinn in Euro bei einem Glücksspiel" if s >= 3 else "Zufallsvariable X"
    return zahl(f"Die Tabelle zeigt die Verteilung ({ctx}). Berechne den **Erwartungswert** E(X).", ew,
                ["E(X) = Summe aus Wert mal Wahrscheinlichkeit.", " + ".join(f"{w}·{zt(p)}" for w, p in zip(werte, ps))],
                [(F(sum(werte), k), "Nicht einfach der Mittelwert der Werte – jeder Wert wird mit seiner Wahrscheinlichkeit gewichtet.")],
                tabelle=tab, erwartungswert={"werte": werte, "wahrscheinlichkeiten": [zt(p) for p in ps]})


def f3_5(r, s):
    n = {1: r.randint(3, 5), 2: r.randint(5, 10), 3: r.randint(8, 15), 4: r.randint(10, 20)}[s]
    p = r.choice([F(1, 2), F(1, 6), F(1, 5), F(3, 10), F(2, 5), F(1, 4)])
    art = r.choice(["gleich", "mu"] if s == 1 else ["gleich", "hoechstens", "mu", "sigma"] if s >= 3 else ["gleich", "mu"])
    k = r.randint(0, n)
    q = 1 - p
    if art == "gleich":
        wert_ = math.comb(n, k) * p ** k * q ** (n - k)
        return zahl(f"X ist binomialverteilt mit n = {n} und p = {zt(p)}. Berechne P(X = {k}) (auf vier Nachkommastellen).", wert_,
                    ["`P(X = k) = (n über k) · pᵏ · (1 − p)ⁿ⁻ᵏ`.", f"Hier: ({n} über {k}) · {zt(p)}^{k} · {zt(q)}^{n - k}."],
                    [(p ** k * q ** (n - k) if math.comb(n, k) > 1 else None, f"Der Binomialkoeffizient ({n} über {k}) = {math.comb(n, k)} fehlt.")],
                    gerundet=4, binom={"n": n, "p": zt(p), "k": k, "art": "gleich"})
    if art == "hoechstens":
        k = r.randint(1, max(1, n // 3))
        wert_ = sum(math.comb(n, i) * p ** i * q ** (n - i) for i in range(k + 1))
        return zahl(f"X ist binomialverteilt mit n = {n} und p = {zt(p)}. Berechne P(X ≤ {k}) (auf vier Nachkommastellen).", wert_,
                    [f"`P(X ≤ {k}) = P(X = 0) + … + P(X = {k})`.", "Jede einzelne Wahrscheinlichkeit mit der Formel berechnen (oder Technologie)."],
                    [], gerundet=4, binom={"n": n, "p": zt(p), "k": k, "art": "hoechstens"})
    if art == "mu":
        return zahl(f"X ist binomialverteilt mit n = {n} und p = {zt(p)}. Berechne den Erwartungswert μ.", n * p, ["`μ = n · p`."],
                    [(n * q, "μ = n · p, nicht n · (1 − p).")], binom={"n": n, "p": zt(p), "art": "mu"})
    wert_ = (n * p * q) ** 0.5
    return zahl(f"X ist binomialverteilt mit n = {n} und p = {zt(p)}. Berechne die Standardabweichung σ (auf zwei Nachkommastellen).",
                F(wert_).limit_denominator(10 ** 9), ["`σ = √(n · p · (1 − p))`."], [(n * p * q, "Das ist die Varianz. σ ist die Wurzel daraus.")],
                gerundet=2, binom={"n": n, "p": zt(p), "art": "sigma"})


# ── F4 Normalverteilung ───────────────────────────────────

SIGMA = {1: ("μ − σ", "μ + σ", 1), 2: ("μ − 2σ", "μ + 2σ", 2), 3: ("μ − 3σ", "μ + 3σ", 3)}


def f4_1(r, s):
    mu, sigma = r.randint(-2, 4), r.choice([1, 2])
    term = f"e^(-(x - ({mu}))^2/(2·{sigma}^2))/({sigma}·√(2π))"

    return zahl("Abgebildet ist die Dichtefunktion (Glockenkurve) einer Normalverteilung. Lies den Erwartungswert μ ab.", mu,
                ["μ liegt dort, wo die Glockenkurve am höchsten ist (Symmetrieachse)."], [],
                aus_term={"term": term, "groesse": "hochpunkt_x"},
                graph={"x": [mu - 4 * sigma, mu + 4 * sigma], "y": [0, 1], "kurven": [{"term": term}], "schritt": [1, 0.1]})


def f4_2(r, s):
    mu, sigma = r.choice([(100, 15), (170, 8), (50, 5), (20, 2), (500, 20), (60, 4), (250, 10), (80, 6), (1000, 50), (35, 3)])
    if s == 1:
        return zahl(f"X ist normalverteilt mit μ = {mu} und σ = {sigma}. Wie groß ist P(X ≤ {mu})?", F(1, 2),
                    ["Die Glockenkurve ist symmetrisch um μ.", "Die Fläche links von μ ist genau die Hälfte."], [],
                    normal_p={"mu": mu, "sigma": sigma, "von": None, "bis": mu})
    k = r.choice([1, 2])
    innen = {1: F(683, 1000), 2: F(954, 1000)}[k]
    wert_ = (1 - innen) / 2
    return zahl(f"X ist normalverteilt mit μ = {mu} und σ = {sigma}. Ungefähr {zt(innen * 100)} % der Werte liegen zwischen {mu - k * sigma} und "
                f"{mu + k * sigma}. Wie groß ist (ungefähr) P(X > {mu + k * sigma})? (auf drei Nachkommastellen)", wert_,
                ["Außerhalb liegen 1 − " + zt(innen) + ".", "Die Kurve ist symmetrisch: Die Hälfte davon liegt rechts."],
                [(1 - innen, "Das ist links **und** rechts zusammen. Rechts allein ist die Hälfte.")], gerundet=3,
                normal_p={"mu": mu, "sigma": sigma, "von": mu + k * sigma, "bis": None})


def f4_3(r, s):
    k = r.choice([1, 2, 3])
    mu, sigma = r.choice([(100, 15), (170, 8), (50, 5), (80, 4), (12, 2), (60, 4), (250, 10), (1000, 50), (35, 3), (500, 20)])
    unten, oben = mu - k * sigma, mu + k * sigma
    import sympy  # noqa: PLC0415
    wert_ = float(sympy.erf(k / sympy.sqrt(2))) * 100
    return zahl(f"X ist normalverteilt mit μ = {mu} und σ = {sigma}. Wie viel Prozent der Werte liegen ungefähr zwischen {unten} und {oben}? "
                "(auf eine Nachkommastelle)", F(wert_).limit_denominator(10 ** 9),
                ["σ-Regeln: zwischen μ ± σ rund 68,3 %, μ ± 2σ rund 95,4 %, μ ± 3σ rund 99,7 %.", f"Hier ist der Abstand {k}σ."], [],
                gerundet=1, einheit="%", normal_p={"mu": mu, "sigma": sigma, "von": unten, "bis": oben, "prozent": True})


AUFGABEN = [("F1.1", f1_1, 6), ("F1.2", f1_2, 6), ("F1.3", f1_3, 6), ("F1.4", f1_4, 6), ("F1.5", f1_5, 5),
            ("F2.1", f2_1, 5), ("F2.2", f2_2, 5), ("F2.3", f2_3, 4), ("F2.4", f2_4, 6), ("F2.5", f2_5, 6),
            ("F3.1", f3_1, 6), ("F3.2", f3_2, 6), ("F3.5", f3_5, 6),
            ("F4.1", f4_1, 3), ("F4.2", f4_2, 5), ("F4.3", f4_3, 5)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261029)
    for lid, fn, n in AUFGABEN:
        schreibe(lid, erzeuge(lid, r, fn, n), "f.py")


if __name__ == "__main__":
    main()
