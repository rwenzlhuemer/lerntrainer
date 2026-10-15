"""
Schulnotation → sympy.

Dieselbe Schreibweise, die die App versteht (app/js/mathe.js), wird hier für die
Build-Prüfung in sympy-Ausdrücke übersetzt:
  3x + 5 = 20   2,5·x   x²   (x − 1):2   √(x)   x^2
"""

import re

import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    rationalize,
    standard_transformations,
)

# rationalize: 0,1 wird exakt 1/10 statt Gleitkomma – sonst scheitern Vergleiche wie 0,1·55 = 5,5
_TRANSFORM = standard_transformations + (implicit_multiplication_application, convert_xor, rationalize)

_ERSETZUNGEN = [
    ("−", "-"), ("–", "-"), ("·", "*"), ("×", "*"), (":", "/"), ("÷", "/"),
    ("²", "^2"), ("³", "^3"), ("⁴", "^4"), ("√", "sqrt"), ("π", "pi"),
]


def zu_sympy_text(text: str) -> str:
    """Normalisiert Schulnotation zu einem Text, den parse_expr versteht."""
    t = text.strip()
    # „3/4 : 2/5“ – ein Zahlenbruch nach „:“ gehört zusammen (wie in app/js/mathe.js)
    t = re.sub(r"[:÷]\s*(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)(?!\s*[\^²³⁴])", r"/(\1/\2)", t)
    for alt, neu in _ERSETZUNGEN:
        t = t.replace(alt, neu)
    # Dezimalkomma: 2,5 → 2.5 (nur zwischen Ziffern)
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    return t


def ausdruck(text: str) -> sympy.Expr:
    lokal = {"x": sympy.Symbol("x"), "e": sympy.E, "pi": sympy.pi}
    return parse_expr(zu_sympy_text(text), local_dict=lokal, transformations=_TRANSFORM)


def gleichung(text: str) -> sympy.Expr:
    """'L = R' → Ausdruck L − R (Nullform)."""
    teile = text.split("=")
    if len(teile) != 2:
        raise ValueError(f"Gleichung braucht genau ein '=': {text!r}")
    return sympy.simplify(ausdruck(teile[0]) - ausdruck(teile[1]))


def loesungsmenge(text: str, var: str = "x"):
    """Lösungsmenge einer Gleichung in ℝ als sympy-Set."""
    x = sympy.Symbol(var)
    return sympy.solveset(gleichung(text), x, domain=sympy.S.Reals)


def zahl(text: str) -> sympy.Expr:
    return sympy.nsimplify(ausdruck(text))
