"""Gemeinsame Helfer für die Aufgaben-Generatoren (ab Kapitel A).

Jeder Generator liefert pro Lernschritt eine Funktion macher(r, stufe) → dict | None.
erzeuge() sammelt daraus verschiedene Aufgaben je Stufe, schreibe() legt die YAML-Datei ab.
Geprüft wird unabhängig davon beim Build (tools/build.py) mit sympy.
"""

import math
from fractions import Fraction as F
from pathlib import Path

import yaml

INHALTE = Path(__file__).resolve().parents[2] / "inhalte" / "mathe"


# ── Zahlen als Text ───────────────────────────────────────

def z(q) -> str:
    """Zahl in Schulnotation: 5, -3, 5/2"""
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def endlich(q) -> bool:
    d = F(q).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def dez(q) -> str:
    """Dezimalzahl mit Komma (nur endliche Dezimalbrüche): 2,5 / -0,125"""
    q = F(q)
    assert endlich(q), q
    if q.denominator == 1:
        return str(q.numerator)
    stellen = 0
    while (q * 10 ** stellen).denominator != 1:
        stellen += 1
    ziffern = str(abs((q * 10 ** stellen).numerator)).rjust(stellen + 1, "0")
    return ("-" if q < 0 else "") + ziffern[:-stellen] + "," + ziffern[-stellen:]


def kl(q, f=z) -> str:
    """Negative Zahlen in Klammern: 3 / (-3) / (-3/4)"""
    return f"({f(q)})" if F(q) < 0 else f(q)



def ggt(a, b):
    return math.gcd(int(a), int(b))


# ── Zufall ────────────────────────────────────────────────

def nz(r, lo, hi, ohne=(0,)):
    while True:
        v = r.randint(lo, hi)
        if v not in ohne:
            return v


def echter_bruch(r, nenner, lo=1, hi=None, negativ=False):
    """Gekürzter, nicht ganzer Bruch mit Nenner aus der Liste (Zähler 1..hi)"""
    while True:
        n = r.choice(nenner)
        zz = r.randint(lo, hi or n - 1)
        q = F(zz, n)
        if q.denominator != 1:
            return -q if negativ and r.random() < 0.5 else q


# ── Gerüst ────────────────────────────────────────────────

def erzeuge(lid, r, macher, pro_stufe=10, stufen=(1, 2, 3, 4)):
    """Ruft macher(r, stufe) so oft auf, bis jede Stufe genug verschiedene Aufgaben hat."""
    aus, gesehen, nr = [], set(), 0
    for stufe in stufen:
        n = 0
        for _ in range(20000):
            if n == pro_stufe:
                break
            try:
                a = macher(r, stufe)
            except (ZeroDivisionError, AssertionError):
                a = None
            if not a:
                continue
            schluessel = a.get("frage") or a.get("term") or a.get("gleichung") or a.get("ungleichung") or " | ".join(a.get("gleichungen", [])) or f"{a.get('formel')} nach {a.get('nach')}"
            schluessel = f"{schluessel} {a.get('graph')} {a.get('tabelle')} {a.get('optionen')} {a.get('dreieck')} {a.get('diagramm')}"
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            nr += 1
            n += 1
            aus.append({"id": f"{lid}-{nr:03d}", "typ": a.pop("typ"), "stufe": stufe, **a})
        else:
            raise RuntimeError(f"{lid} Stufe {stufe}: nicht genug Aufgaben ({n})")
    return aus


def schreibe(lid, aufgaben, generator):
    kapitel = lid.split(".")[0]
    ziel = INHALTE / kapitel
    ziel.mkdir(parents=True, exist_ok=True)
    kopf = (f"# ERZEUGT von tools/generatoren/{generator} – nicht von Hand bearbeiten.\n"
            f"# Geprüft wird beim Build (tools/build.py) mit sympy.\n")
    text = yaml.safe_dump(aufgaben, allow_unicode=True, sort_keys=False, width=200)
    (ziel / f"{lid}.aufgaben.yaml").write_text(kopf + text, encoding="utf-8")
    print(f"{lid}: {len(aufgaben)} Aufgaben")


def fehler_zahlen(loesung, kandidaten):
    """Nur echte, voneinander verschiedene Fehler-Antworten behalten (Zahlen)."""
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
