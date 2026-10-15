"""
Generator für Kapitel A5 (Prozent, Verhältnisse, Proportionalität). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/a5.py
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import dez, endlich, erzeuge, fehler_zahlen, schreibe  # noqa: E402


def zahl(frage, ergebnis, rechnung, tipps, fehler, einheit=None, weg=None):
    """Ergebnis exakt (endliche Dezimalzahl) oder auf Cent gerundet."""
    ergebnis = F(ergebnis)
    a = {"typ": "zahl", "frage": frage}
    if endlich(ergebnis) and (ergebnis * 1000).denominator == 1:
        a["loesung"] = dez(ergebnis)
        a["weg"] = weg or [f"{rechnung} = {dez(ergebnis)}"]
    else:
        a["loesung"] = f"{float(ergebnis):.2f}".replace(".", ",")
        a["gerundet"] = 2
        a["weg"] = weg or [f"{rechnung} | ergibt gerundet {a['loesung']}"]
    if einheit:
        a["einheit"] = einheit
    a["rechnung"] = rechnung
    a["tipps"] = tipps
    a["fehler"] = [f for f in fehler_zahlen(ergebnis, [(w, h) for w, h in fehler if w is not None])
                   if abs(F(f["antwort"]) - ergebnis) > F(1, 100)]
    return a


def p_text(p):
    return dez(F(p))


# ── A5.1 Prozentwert, Grundwert, Prozentsatz ──────────────

KONTEXTE = [("€", "eines Betrags", "Betrag"), ("kg", "einer Lieferung", "Gewicht der Lieferung")]


def a5_1(r, s):
    p = F(r.choice({1: [10, 20, 25, 50, 5], 2: [15, 30, 35, 40, 75, 12, 60, 8], 3: [F(25, 2), F(5, 2), F(1, 2), 16, 85, 4, 72],
                    4: [F(35, 2), 3, 24, 36, 45, F(15, 2), 64]}[s]))
    G = F(r.choice({1: [40, 60, 80, 120, 200, 300, 500], 2: [60, 80, 120, 140, 240, 360], 3: [80, 160, 240, 320, 480, 640],
                    4: [840, 1260, 2400, 360, 720]}[s]))
    W = G * p / 100
    if not endlich(W):
        return None
    art = r.choice(["wert", "grund", "satz"]) if s > 1 else r.choice(["wert", "wert", "satz"])
    pt, Gt, Wt = p_text(p), dez(G), dez(W)
    if s == 4:
        ctx = r.choice([
            (f"Von {Gt} Jugendlichen einer Schule fahren {pt} % mit dem Rad. Wie viele sind das?", "wert", ""),
            (f"{Wt} Jugendliche einer Schule fahren mit dem Rad, das sind {pt} % aller. Wie viele Jugendliche hat die Schule?", "grund", ""),
            (f"Bei einer Wahl bekommt eine Liste {Wt} von {Gt} Stimmen. Wie viel Prozent sind das?", "satz", "%"),
        ])
        frage, art, einheit = ctx
    else:
        einheit = "€"
        frage = {"wert": f"Wie viel sind {pt} % von {Gt} €?",
                 "grund": f"{Wt} € sind {pt} % eines Betrags. Wie groß ist der ganze Betrag?",
                 "satz": f"Wie viel Prozent sind {Wt} € von {Gt} €?"}[art]
        if art == "satz":
            einheit = "%"
    if art == "wert":
        return zahl(frage, W, f"{Gt} · {pt}/100",
                    ["Prozentwert = Grundwert · Prozentsatz. „Prozent“ heißt „Hundertstel“.",
                     f"`{pt} %` ist `{pt}/100 = {dez(p / 100)}`. Rechne `{Gt} · {dez(p / 100)}`."],
                    [(G * p, "Vergiss nicht: Prozent heißt Hundertstel – noch durch 100 dividieren."),
                     (G * 100 / p, "Hier ist der Grundwert gegeben, gesucht ist der Anteil: Grundwert mal Prozentsatz.")],
                    einheit=einheit)
    if art == "grund":
        return zahl(frage, G, f"{Wt} : {pt} · 100",
                    ["Gesucht ist das Ganze (100 %). Rechne zuerst aus, wie viel 1 % ist.",
                     f"1 % sind `{Wt} : {pt}`. Das Ganze ist 100-mal so viel."],
                    [(W * p / 100, "Gesucht ist nicht der Anteil, sondern das Ganze: `Prozentwert : Prozentsatz · 100`."),
                     (W + W * p / 100, "Gesucht ist das Ganze: Wenn {pt} % = {Wt} sind, wie viel sind dann 100 %?".format(pt=pt, Wt=Wt))],
                    einheit=einheit if einheit != "%" else None)
    return zahl(frage, p, f"{Wt} : {Gt} · 100",
                ["Prozentsatz = Prozentwert : Grundwert · 100.", f"`{Wt} : {Gt}` ergibt den Anteil, mal 100 sind das Prozent."],
                [(p / 100, "Das ist der Anteil als Dezimalzahl – noch mal 100 für Prozent."),
                 (G / W * 100, "Umgekehrt: Der Teil kommt in den Zähler, das Ganze in den Nenner.")],
                einheit="%")


# ── A5.2 Prozentuelle Änderung, Änderungsfaktor ───────────

def a5_2(r, s):
    w = r.random()
    if s == 1:
        p = F(r.choice([5, 10, 20, 25, 3, 15, 30, 50]))
        auf = r.random() < .6
        fak = 1 + p / 100 if auf else 1 - p / 100
        return zahl(f"Mit welcher Zahl multiplizierst du bei einer {'Zunahme' if auf else 'Abnahme'} um {p_text(p)} %?", fak,
                    f"1 {'+' if auf else '-'} {dez(p / 100)}",
                    ["Der alte Wert ist 100 % = 1. Bei einer Zunahme kommt etwas dazu, bei einer Abnahme fällt etwas weg.",
                     f"{'1 + ' if auf else '1 - '}{dez(p / 100)}"],
                    [(p / 100, f"Das ist nur die Änderung. Der Faktor ist `1 {'+' if auf else '-'} {dez(p / 100)}`."),
                     (1 - p / 100 if auf else 1 + p / 100, "Zunahme heißt plus, Abnahme heißt minus.")])
    if s == 2:
        p = F(r.choice([5, 8, 12, 15, 20, 25, 30, 40]))
        G = F(r.choice([40, 60, 80, 120, 150, 250, 400, 640]))
        auf = r.random() < .5
        fak = 1 + p / 100 if auf else 1 - p / 100
        return zahl(f"Ein Preis von {dez(G)} € wird um {p_text(p)} % {'erhöht' if auf else 'gesenkt'}. Wie hoch ist der neue Preis?",
                    G * fak, f"{dez(G)} · {dez(fak)}",
                    [f"Änderungsfaktor: `{dez(fak)}`.", f"Neuer Preis = alter Preis · Faktor = `{dez(G)} · {dez(fak)}`."],
                    [(G * p / 100, "Das ist nur die Änderung, nicht der neue Preis."),
                     (G * (1 - p / 100) if auf else G * (1 + p / 100), "Erhöhen heißt mehr, senken heißt weniger.")],
                    einheit="€")
    if s == 3:
        p = F(r.choice([10, 20, 25, 15, 5, 30, 12]))
        G = F(r.choice([40, 80, 120, 200, 360, 500, 60]))
        auf = w < .6
        fak = 1 + p / 100 if auf else 1 - p / 100
        N = G * fak
        return zahl(f"Nach einer {'Erhöhung' if auf else 'Senkung'} um {p_text(p)} % kostet ein Gerät {dez(N)} €. "
                    "Wie viel hat es vorher gekostet?", G, f"{dez(N)} : {dez(fak)}",
                    ["Der neue Preis ist der alte Preis mal dem Änderungsfaktor. Rückwärts heißt: **durch** den Faktor.",
                     f"Alter Preis = `{dez(N)} : {dez(fak)}`."],
                    [(N * (1 - p / 100) if auf else N * (1 + p / 100),
                      "Vorsicht: Die %-Angabe bezieht sich auf den **alten** Preis. Du darfst nicht einfach vom neuen Preis "
                      f"{p_text(p)} % {'abziehen' if auf else 'dazurechnen'} – dividiere durch den Faktor.")],
                    einheit="€")
    p, q = F(r.choice([10, 20, 25, 50])), F(r.choice([10, 20, 25, 50]))
    erst_auf = w < .5
    f1 = 1 + p / 100 if erst_auf else 1 - p / 100
    f2 = 1 - q / 100 if erst_auf else 1 + q / 100
    ges = (f1 * f2 - 1) * 100
    if ges == 0:
        return None
    return zahl(f"Ein Preis wird zuerst um {p_text(p)} % {'erhöht' if erst_auf else 'gesenkt'} und danach um {p_text(q)} % "
                f"{'gesenkt' if erst_auf else 'erhöht'}. Um wie viel Prozent hat er sich insgesamt geändert? "
                "(Abnahme mit Minus angeben.)", ges, f"({dez(f1)} · {dez(f2)} - 1) · 100",
                ["Multipliziere die beiden Änderungsfaktoren.", f"`{dez(f1)} · {dez(f2)} = {dez(f1 * f2)}`.",
                 "Vergleiche mit 1: Wie viel Prozent mehr oder weniger ist das?"],
                [((p - q) if erst_auf else (q - p), "Prozente darf man nicht einfach addieren oder abziehen – die zweite Änderung "
                                                     "bezieht sich auf den schon geänderten Preis."),
                 (f1 * f2 * 100, "Das ist der neue Preis in Prozent des alten. Die **Änderung** ist das minus 100 %.")],
                einheit="%")


# ── A5.3 Absolute und relative Änderung ───────────────────

def a5_3(r, s):
    a = F(r.choice({1: [40, 50, 80, 100, 200], 2: [60, 80, 120, 250, 400], 3: [160, 320, 450, 1200], 4: [2400, 3600, 12500, 48000]}[s]))
    p = F(r.choice({1: [10, 20, 25, 50], 2: [-10, -20, 15, 30, -25], 3: [-15, 12, -35, 5, -8], 4: [F(5, 2), -6, 14, F(-25, 2)]}[s]))
    b = a * (1 + p / 100)
    if not endlich(b):
        return None
    art = r.choice(["abs", "rel"] if s < 3 else ["rel", "rel", "dez"])
    einh = "€" if s < 4 else ""
    ding = "Der Preis" if s < 4 else "Die Einwohnerzahl einer Gemeinde"
    von = f"{dez(a)}{' ' + einh if einh else ''}"
    auf = f"{dez(b)}{' ' + einh if einh else ''}"
    basis = f"{ding} ändert sich von {von} auf {auf}."
    if art == "abs":
        return zahl(f"{basis} Wie groß ist die **absolute** Änderung? (Abnahme mit Minus.)", b - a, f"{dez(b)} - {dez(a)}",
                    ["Absolute Änderung = neuer Wert − alter Wert.", "Bei einer Abnahme ist sie negativ."],
                    [(a - b, "Neuer Wert minus alter Wert – nicht umgekehrt.")], einheit=einh or None)
    if art == "rel":
        return zahl(f"{basis} Um wie viel Prozent hat sich der Wert geändert? (Abnahme mit Minus.)", p,
                    f"({dez(b)} - {dez(a)}) : {dez(a)} · 100",
                    ["Relative Änderung = (neu − alt) : alt.", f"Die absolute Änderung ist `{dez(b - a)}`. Teile durch den **alten** Wert {dez(a)}.",
                     "Mal 100 ergibt Prozent."],
                    [((b - a) / b * 100, "Geteilt wird durch den **alten** Wert, nicht durch den neuen."),
                     (b - a, "Das ist die absolute Änderung. Gefragt sind Prozent.")], einheit="%")
    return zahl(f"{basis} Gib die relative Änderung als Dezimalzahl an.", p / 100, f"({dez(b)} - {dez(a)}) : {dez(a)}",
                ["Relative Änderung = (neu − alt) : alt – als Dezimalzahl, also ohne mal 100.",
                 f"`({dez(b)} - {dez(a)}) : {dez(a)}`"],
                [(p, "Das ist die Änderung in Prozent. Als Dezimalzahl: durch 100."),
                 ((b - a) / b, "Geteilt wird durch den **alten** Wert.")])


# ── A5.4 Direkte und indirekte Proportionalität ───────────

def a5_4(r, s):
    w = r.random()
    if s <= 2 and w < .5 or s == 3 and w < .4:
        n1, n2 = r.choice([(2, 5), (3, 7), (4, 6), (5, 8), (2, 9), (6, 10), (3, 4)])
        preis = F(r.choice([3, 4, 6, 9, 12, 15]), 2) if s > 1 else F(r.choice([2, 3, 4, 5]))
        p1 = preis * n1
        ding = r.choice([("kg Äpfel", "kosten", "€"), ("m Stoff", "kosten", "€"), ("Hefte", "kosten", "€")])
        return zahl(f"{n1} {ding[0]} {ding[1]} {dez(p1)} €. Wie viel kosten {n2} {ding[0]}?", preis * n2,
                    f"{dez(p1)} : {n1} · {n2}",
                    ["Doppelt so viel kostet doppelt so viel: direkte Proportionalität.",
                     f"Rechne zuerst den Preis für 1: `{dez(p1)} : {n1}`. Dann mal {n2}."],
                    [(p1 * n1 / n2, "Mehr Ware kostet mehr – hier ist es direkt proportional, nicht indirekt.")], einheit="€")
    if s <= 3:
        a, t = r.choice([(3, 8), (4, 6), (2, 9), (6, 4), (5, 12), (3, 10), (8, 3)])
        b = r.choice([x for x in (2, 3, 4, 5, 6, 8, 10, 12) if x != a and (a * t) % x == 0] or [None])
        if not b:
            return None
        ctx = r.choice([("Pumpen leeren ein Becken in", "Stunden", "Pumpen", "h"),
                        ("Malerinnen streichen ein Haus in", "Tagen", "Malerinnen", "Tage")])
        return zahl(f"{a} {ctx[0]} {t} {ctx[1]}. Wie lange brauchen {b} {ctx[2]} (gleich schnell)?", F(a * t, b),
                    f"{t} · {a} : {b}",
                    ["Mehr Helfer – weniger Zeit: indirekte Proportionalität.",
                     f"Wie lange bräuchte **eine** allein? `{t} · {a}`. Dann durch {b}."],
                    [(F(t * b, a), "Mehr Helfer brauchen **weniger** Zeit – hier ist es indirekt proportional.")], einheit=ctx[3])
    if w < .5:
        v1, t1 = r.choice([(80, 3), (60, 4), (90, 2), (100, 3), (120, 2)])
        v2 = r.choice([x for x in (40, 60, 80, 90, 100, 120, 150) if x != v1])
        t2 = F(v1 * t1, v2)
        if not endlich(t2) or (t2 * 4).denominator != 1:
            return None
        return zahl(f"Mit {v1} km/h braucht man für eine Strecke {t1} Stunden. Wie lange braucht man mit {v2} km/h?", t2,
                    f"{t1} · {v1} : {v2}",
                    ["Schneller fahren – kürzere Zeit: indirekt proportional.", f"Die Strecke ist `{v1} · {t1}` km. Durch die neue Geschwindigkeit."],
                    [(F(t1 * v2, v1), "Schneller heißt weniger Zeit – indirekt proportional.")], einheit="h")
    tiere, tage, nach, dazu = r.choice([(12, 30, 10, 3), (10, 24, 4, 2), (8, 21, 6, 4), (15, 20, 5, 5), (6, 40, 10, 4)])
    rest = F((tage - nach) * tiere, tiere + dazu)
    if rest.denominator != 1:
        return None
    return zahl(f"Ein Futtervorrat reicht für {tiere} Tiere {tage} Tage. Nach {nach} Tagen kommen {dazu} Tiere dazu. "
                "Wie viele Tage reicht der Rest des Vorrats noch?", rest, f"({tage} - {nach}) · {tiere} : {tiere + dazu}",
                [f"Nach {nach} Tagen reicht der Rest für {tiere} Tiere noch {tage - nach} Tage.",
                 f"Jetzt sind es {tiere + dazu} Tiere – mehr Tiere, weniger Tage: indirekt proportional.",
                 f"`{tage - nach} · {tiere} : {tiere + dazu}`"],
                [(F(tage * tiere, tiere + dazu), f"Die ersten {nach} Tage sind schon vorbei – rechne nur mit dem Rest."),
                 (F(tage * tiere, tiere + dazu) - nach, f"Rechne zuerst, wie lange der Rest für {tiere} Tiere reicht.")],
                einheit="Tage")


# ── A5.5 Zinseszins ───────────────────────────────────────

def a5_5(r, s):
    K = F(r.choice([500, 1000, 2000, 2500, 5000, 800, 1200]))
    i = F(r.choice({1: [2, 3, 4, 5], 2: [2, 3, 4, F(5, 2), F(3, 2)], 3: [2, 3, F(7, 2), 4], 4: [2, 3, 4, 5]}[s]))
    q = 1 + i / 100
    n = {1: 1, 2: r.randint(2, 3), 3: r.randint(3, 8), 4: r.randint(4, 10)}[s]
    Kn = K * q ** n
    it = p_text(i)
    if s == 1:
        return zahl(f"{dez(K)} € liegen ein Jahr lang auf einem Sparbuch mit {it} % Zinsen pro Jahr. Wie viel ist es nach einem Jahr?",
                    Kn, f"{dez(K)} · {dez(q)}",
                    [f"Nach einem Jahr: Kapital mal Zinsfaktor `1 + {dez(i / 100)} = {dez(q)}`.", f"`{dez(K)} · {dez(q)}`"],
                    [(K * i / 100, "Das sind nur die Zinsen. Gefragt ist das ganze Guthaben."), (K * i, "Prozent heißt Hundertstel.")],
                    einheit="€")
    if s in (2, 3) and r.random() < .7:
        frage = (f"{dez(K)} € werden {n} Jahre lang mit {it} % pro Jahr verzinst (Zinseszins). Wie hoch ist das Kapital danach? "
                 "Runde auf Cent.")
        return zahl(frage, Kn, f"{dez(K)} · {dez(q)}^{n}",
                    ["Zinseszins: Jedes Jahr wird mit dem Zinsfaktor multipliziert, auch die Zinsen werden mitverzinst.",
                     f"`Kₙ = K₀ · (1 + i)ⁿ = {dez(K)} · {dez(q)}^{n}`.", "Auf zwei Nachkommastellen runden."],
                    [(K * (1 + n * i / 100), "Das wäre ohne Zinseszins. Bei Zinseszins: hoch n, nicht mal n."),
                     (K * q * n, "Der Zinsfaktor wird hoch n genommen, nicht mal n.")],
                    einheit="€")
    if s == 3:
        return zahl(f"{dez(K)} € werden {n} Jahre lang mit {it} % pro Jahr verzinst (Zinseszins). Wie viel **Zinsen** bekommt man "
                    "insgesamt? Runde auf Cent.", Kn - K, f"{dez(K)} · {dez(q)}^{n} - {dez(K)}",
                    [f"Zuerst das Endkapital: `{dez(K)} · {dez(q)}^{n}`.", f"Zinsen = Endkapital − Anfangskapital {dez(K)}."],
                    [(Kn, "Das ist das Endkapital. Die Zinsen sind das, was dazugekommen ist."),
                     (K * n * i / 100, "Das wären einfache Zinsen. Bei Zinseszins werden auch die Zinsen verzinst.")],
                    einheit="€")
    ziel = F(r.choice([5000, 10000, 8000, 20000]))
    K0 = ziel / q ** n
    return zahl(f"Welches Anfangskapital braucht man, damit bei {it} % Zinsen pro Jahr nach {n} Jahren {dez(ziel)} € am Konto sind? "
                "Runde auf Cent.", K0, f"{dez(ziel)} : {dez(q)}^{n}",
                ["`Kₙ = K₀ · qⁿ`. Gesucht ist K₀ – also rückwärts rechnen: durch qⁿ.", f"`K₀ = {dez(ziel)} : {dez(q)}^{n}`."],
                [(ziel * (1 - n * i / 100), "Rückwärts heißt: durch den Faktor dividieren, nicht Prozente abziehen."),
                 (ziel * q ** n, "Gesucht ist das Anfangskapital: durch qⁿ, nicht mal.")],
                einheit="€")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261020)
    for lid, fn, n in [("A5.1", a5_1, 10), ("A5.2", a5_2, 10), ("A5.3", a5_3, 10), ("A5.4", a5_4, 8), ("A5.5", a5_5, 8)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "a5.py")


if __name__ == "__main__":
    main()
