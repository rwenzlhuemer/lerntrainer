"""
Generator für Kapitel B2 (Formeln umformen). Einmal laufen lassen, Ergebnis wird eingecheckt:

    python tools/generatoren/b2.py

Die Formeln sind handverlesen (Geometrie, Physik, Alltag); Lösungswege und typische Fehler stehen dabei.
Geprüft wird beim Build mit sympy (solve) – jede Lösung, jede Zeile des Lösungswegs, jede Fehler-Antwort.
"""

import random
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
from gemeinsam import erzeuge, schreibe  # noqa: E402

UMKEHR = "Mach die Rechnung rückgängig: Aus „mal“ wird „durch“, aus „plus“ wird „minus“ – und umgekehrt."
GANZE_SEITE = "Was du auf einer Seite machst, machst du auch auf der anderen – immer mit der **ganzen** Seite."

# (Formel, nach, Lösung, Lösungsweg, [(Fehler-Antwort, Hinweis)])
B21 = {
    1: [("A = a·b", "a", "A/b", ["A/b = a | :b"], [("A·b", "a wird mit b multipliziert – rückgängig machst du das mit **durch** b.")]),
        ("A = a·b", "b", "A/a", ["A/a = b | :a"], [("A - a", "Zwischen a und b steht ein Mal – rückgängig: durch a, nicht minus.")]),
        ("v = s/t", "s", "v·t", ["v·t = s | ·t"], [("v/t", "s wird durch t dividiert – rückgängig machst du das mit **mal** t.")]),
        ("d = 2r", "r", "d/2", ["d/2 = r | :2"], [("2d", "Rückgängig machen: durch 2, nicht mal 2.")]),
        ("U = 4a", "a", "U/4", ["U/4 = a | :4"], [("U - 4", "4a heißt 4 · a – rückgängig: durch 4.")]),
        ("y = x + d", "d", "y - x", ["y - x = d | −x"], [("y + x", "Aus plus wird minus: Bring x mit −x auf die andere Seite.")]),
        ("G = m·g", "m", "G/g", ["G/g = m | :g"], [("G·g", "Rückgängig machen: durch g, nicht mal g.")]),
        ("W = F·s", "F", "W/s", ["W/s = F | :s"], [("W - s", "F und s werden multipliziert – rückgängig: durch s.")]),
        ("P = W/t", "W", "P·t", ["P·t = W | ·t"], [("P/t", "W wird durch t dividiert – rückgängig: mal t.")]),
        ("c = a - b", "a", "c + b", ["c + b = a | +b"], [("c - b", "Aus minus wird plus: Bring −b mit +b auf die andere Seite.")])],
    2: [("v = s/t", "t", "s/v", ["v·t = s | ·t", "t = s/v | :v"],
         [("v·s", "t steht im Nenner. Zuerst mal t, dann durch v."), ("v/s", "Fast – prüf mit Zahlen: s = 100, t = 2 ergibt v = 50. Dann muss t = 100 : 50 sein.")]),
        ("I = U/R", "R", "U/I", ["I·R = U | ·R", "R = U/I | :I"], [("I·U", "R steht im Nenner: zuerst mal R, dann durch I."), ("I/U", "Umgekehrt: R = U : I.")]),
        ("p = F/A", "A", "F/p", ["p·A = F | ·A", "A = F/p | :p"], [("p·F", "A steht im Nenner: zuerst mal A, dann durch p.")]),
        ("c = a - b", "b", "a - c", ["c + b = a | +b", "b = a - c | −c"], [("c - a", "Vorsicht mit dem Minus vor b: Bring b zuerst mit +b auf die andere Seite.")]),
        ("y = k·x", "x", "y/k", ["y/k = x | :k"], [("y - k", "k·x heißt k mal x – rückgängig: durch k.")]),
        ("z = 5 - x", "x", "5 - z", ["z + x = 5 | +x", "x = 5 - z | −z"], [("z - 5", "Vorsicht mit dem Minus vor x: zuerst +x auf beiden Seiten.")]),
        ("A = a·b/2", "a", "2A/b", ["2A = a·b | ·2", "2A/b = a | :b"], [("A/(2b)", "Das „durch 2“ machst du mit „mal 2“ rückgängig."), ("2A·b", "Zum Schluss durch b, nicht mal b.")]),
        ("m = d·V", "V", "m/d", ["m/d = V | :d"], [("m·d", "Rückgängig machen: durch d.")]),
        ("t = s/v", "v", "s/t", ["t·v = s | ·v", "v = s/t | :t"], [("t·s", "v steht im Nenner: zuerst mal v, dann durch t.")])],
    3: [("U = 2a + 2b", "a", "(U - 2b)/2", ["U - 2b = 2a | −2b", "(U - 2b)/2 = a | :2"],
         [("U/2 - 2b", "Wenn du durch 2 dividierst, dann die **ganze** Seite: `(U - 2b)/2`."), ("(U + 2b)/2", "+2b wird mit −2b rückgängig gemacht.")]),
        ("y = k·x + d", "x", "(y - d)/k", ["y - d = k·x | −d", "(y - d)/k = x | :k"],
         [("y/k - d", "Zuerst −d, dann durch k – und zwar die ganze Seite."), ("(y + d)/k", "+d machst du mit −d rückgängig.")]),
        ("y = k·x + d", "k", "(y - d)/x", ["y - d = k·x | −d", "(y - d)/x = k | :x"], [("y/x - d", "Zuerst −d, dann die ganze Seite durch x.")]),
        ("F = 1,8·C + 32", "C", "(F - 32)/1,8", ["F - 32 = 1,8·C | −32", "(F - 32)/1,8 = C | :1,8"],
         [("F/1,8 - 32", "Zuerst −32, dann die ganze Seite durch 1,8."), ("(F + 32)/1,8", "+32 machst du mit −32 rückgängig.")]),
        ("K = 50 + 0,2·x", "x", "(K - 50)/0,2", ["K - 50 = 0,2·x | −50", "(K - 50)/0,2 = x | :0,2"],
         [("K/0,2 - 50", "Zuerst −50, dann die ganze Seite durch 0,2.")]),
        ("s = v·t + a", "t", "(s - a)/v", ["s - a = v·t | −a", "(s - a)/v = t | :v"], [("s/v - a", "Zuerst −a, dann die ganze Seite durch v.")]),
        ("y = 3 - 2x", "x", "(3 - y)/2", ["y + 2x = 3 | +2x", "2x = 3 - y | −y", "x = (3 - y)/2 | :2"],
         [("(y - 3)/2", "Vorsicht mit dem Minus vor 2x: Prüf mit einer Zahl, z. B. x = 1 → y = 1."), ("(3 - y)/(-2)", "Prüf das Vorzeichen mit einer Zahl.")]),
        ("A = a·h/2", "h", "2A/a", ["2A = a·h | ·2", "2A/a = h | :a"], [("A/(2a)", "Das „durch 2“ machst du mit „mal 2“ rückgängig.")])],
    4: [("U = 2(a + b)", "a", "U/2 - b", ["U/2 = a + b | :2", "U/2 - b = a | −b"], [("U - 2b", "Zuerst durch 2 (die ganze Seite), dann −b."), ("(U - b)/2", "Die 2 gilt für die ganze Klammer: zuerst durch 2, dann −b.")]),
        ("y = (x - 3)/2", "x", "2y + 3", ["2y = x - 3 | ·2", "2y + 3 = x | +3"], [("2y - 3", "−3 machst du mit +3 rückgängig."), ("y/2 + 3", "Das „durch 2“ machst du mit „mal 2“ rückgängig.")]),
        ("a = (v - u)/t", "v", "a·t + u", ["a·t = v - u | ·t", "a·t + u = v | +u"], [("a·t - u", "−u machst du mit +u rückgängig."), ("(a + u)·t", "Zuerst mal t, dann +u.")]),
        ("a = (v - u)/t", "t", "(v - u)/a", ["a·t = v - u | ·t", "t = (v - u)/a | :a"], [("a·(v - u)", "t steht im Nenner: zuerst mal t, dann durch a.")]),
        ("m = (a + b)/2", "a", "2m - b", ["2m = a + b | ·2", "2m - b = a | −b"], [("m/2 - b", "Das „durch 2“ machst du mit „mal 2“ rückgängig."), ("2(m - b)", "Zuerst mal 2, dann −b.")]),
        ("p = 100·W/G", "G", "100W/p", ["p·G = 100W | ·G", "G = 100W/p | :p"], [("p·W/100", "G steht im Nenner: zuerst mal G, dann durch p.")]),
        ("k = (y - d)/x", "d", "y - k·x", ["k·x = y - d | ·x", "k·x + d = y | +d", "d = y - k·x | −k·x"], [("k·x - y", "Vorsicht mit dem Minus vor d.")]),
        ("z = (x + y)/(2y)", "x", "2y·z - y", ["2y·z = x + y | ·2y", "2y·z - y = x | −y"], [("2z - y", "Mal den **ganzen** Nenner 2y."), ("z/(2y) - y", "Der Nenner 2y wird mit „mal 2y“ rückgängig gemacht.")])],
}

B22 = {
    1: [("A = (a + c)/2 · h", "h", "2A/(a + c)", ["2A = (a + c)·h | ·2", "2A/(a + c) = h | :(a + c)"],
         [("2A - (a + c)", "a + c wird mit h **multipliziert** – rückgängig: durch (a + c)."), ("2A/a + c", "Durch die **ganze** Klammer: (a + c).")]),
        ("V = a·b·c", "c", "V/(a·b)", ["V/(a·b) = c | :(a·b)"], [("V·a·b", "Rückgängig machen: durch a·b."), ("V/a·b", "Durch a **und** durch b – also durch (a·b).")]),
        ("u = 2r·π", "r", "u/(2π)", ["u/(2π) = r | :(2π)"], [("u/2·π", "Durch 2 **und** durch π – also durch (2π)."), ("u - 2π", "2rπ ist ein Produkt – rückgängig: durch 2π.")]),
        ("A = g·h/2", "g", "2A/h", ["2A = g·h | ·2", "2A/h = g | :h"], [("A/(2h)", "Das „durch 2“ machst du mit „mal 2“ rückgängig.")]),
        ("V = G·h/3", "h", "3V/G", ["3V = G·h | ·3", "3V/G = h | :G"], [("V/(3G)", "Das „durch 3“ machst du mit „mal 3“ rückgängig.")]),
        ("V = a²·h", "h", "V/a²", ["V/a² = h | :a²"], [("V/a", "Durch a² – nicht nur durch a."), ("√V/a", "Für h brauchst du keine Wurzel – h steht nicht im Quadrat.")]),
        ("M = 2r·π·h", "h", "M/(2r·π)", ["M/(2r·π) = h | :(2rπ)"], [("M/2·r·π", "Durch das **ganze** Produkt 2rπ – mit Klammer.")])],
    2: [("A = (a + c)/2 · h", "a", "2A/h - c", ["2A = (a + c)·h | ·2", "2A/h = a + c | :h", "2A/h - c = a | −c"],
         [("2A/h + c", "+c machst du mit −c rückgängig."), ("2A - c/h", "Zuerst mal 2, dann durch h (die ganze Seite), dann −c.")]),
        ("V = r²·π·h", "h", "V/(r²·π)", ["V/(r²·π) = h | :(r²π)"], [("V/r²·π", "Durch das **ganze** Produkt r²π – mit Klammer.")]),
        ("O = 2a² + 4a·h", "h", "(O - 2a²)/(4a)", ["O - 2a² = 4a·h | −2a²", "(O - 2a²)/(4a) = h | :(4a)"],
         [("O/(4a) - 2a²", "Zuerst −2a², dann die ganze Seite durch 4a."), ("(O - 2a²)/4", "Durch 4a – also durch 4 **und** durch a.")]),
        ("V = G·h/3", "G", "3V/h", ["3V = G·h | ·3", "3V/h = G | :h"], [("V/(3h)", "Das „durch 3“ machst du mit „mal 3“ rückgängig.")]),
        ("U = 2r·π + 2a", "a", "(U - 2r·π)/2", ["U - 2r·π = 2a | −2rπ", "(U - 2r·π)/2 = a | :2"], [("U/2 - 2r·π", "Zuerst −2rπ, dann die **ganze** Seite durch 2.")]),
        ("A = a·b - c²", "b", "(A + c²)/a", ["A + c² = a·b | +c²", "(A + c²)/a = b | :a"], [("A/a + c²", "Zuerst +c², dann die ganze Seite durch a.")]),
        ("O = 2(a·b + a·c + b·c)", "c", "(O/2 - a·b)/(a + b)", ["O/2 = a·b + a·c + b·c | :2", "O/2 - a·b = c·(a + b) | −ab, c herausgehoben", "(O/2 - a·b)/(a + b) = c | :(a + b)"],
         [("O/2 - a·b - a - b", "c steht zweimal – heb c heraus: `a·c + b·c = c·(a + b)`. Dann durch (a + b).")])],
    3: [("A = a²", "a", "√A", ["√A = a | Wurzel"], [("A/2", "a² heißt a · a – rückgängig machst du das mit der **Wurzel**, nicht mit „durch 2“.")]),
        ("A = r²·π", "r", "√(A/π)", ["A/π = r² | :π", "√(A/π) = r | Wurzel"], [("A/π", "Das ist erst r². Jetzt noch die Wurzel ziehen."), ("√A/π", "Zuerst durch π, dann aus allem die Wurzel.")]),
        ("V = a²·h", "a", "√(V/h)", ["V/h = a² | :h", "√(V/h) = a | Wurzel"], [("V/h", "Das ist erst a². Jetzt noch die Wurzel ziehen.")]),
        ("c² = a² + b²", "a", "√(c² - b²)", ["c² - b² = a² | −b²", "√(c² - b²) = a | Wurzel"],
         [("c - b", "Die Wurzel aus einer Differenz ist **nicht** die Differenz der Wurzeln: `√(c² - b²)` bleibt so stehen."), ("c² - b²", "Das ist erst a². Jetzt noch die Wurzel ziehen.")]),
        ("V = r²·π·h", "r", "√(V/(π·h))", ["V/(π·h) = r² | :(πh)", "√(V/(π·h)) = r | Wurzel"], [("V/(π·h)", "Das ist erst r². Jetzt noch die Wurzel ziehen.")]),
        ("s = a·t²/2", "t", "√(2s/a)", ["2s = a·t² | ·2", "2s/a = t² | :a", "√(2s/a) = t | Wurzel"], [("2s/a", "Das ist erst t². Jetzt noch die Wurzel ziehen."), ("√(s/(2a))", "Das „durch 2“ machst du mit „mal 2“ rückgängig.")]),
        ("d² = 2a²", "a", "d/√2", ["d²/2 = a² | :2", "√(d²/2) = a | Wurzel", "a = d/√2"], [("d/2", "Zuerst durch 2, dann Wurzel: `√(d²/2) = d/√2`."), ("d²/2", "Das ist erst a². Jetzt noch die Wurzel ziehen.")])],
    4: [("1/R = 1/a + 1/b", "R", "a·b/(a + b)", ["1/R = (b + a)/(a·b) | gemeinsamer Nenner", "R = a·b/(a + b) | Kehrwert"],
         [("a + b", "Der Kehrwert einer Summe ist nicht die Summe der Kehrwerte. Erst zu **einem** Bruch zusammenfassen, dann umdrehen.")]),
        ("1/f = 1/g + 1/b", "f", "g·b/(g + b)", ["1/f = (b + g)/(g·b) | gemeinsamer Nenner", "f = g·b/(g + b) | Kehrwert"],
         [("g + b", "Erst rechts zu **einem** Bruch zusammenfassen, dann beide Seiten umdrehen.")]),
        ("A = (a + c)/2 · h", "c", "2A/h - a", ["2A = (a + c)·h | ·2", "2A/h = a + c | :h", "2A/h - a = c | −a"], [("2A/h + a", "+a machst du mit −a rückgängig.")]),
        ("V = 4/3·r³·π", "r", "(3V/(4π))^(1/3)", ["3V = 4r³·π | ·3", "3V/(4π) = r³ | :(4π)", "(3V/(4π))^(1/3) = r | dritte Wurzel"],
         [("3V/(4π)", "Das ist erst r³. Jetzt noch die dritte Wurzel (hoch 1/3)."), ("√(3V/(4π))", "r steht hoch 3 – du brauchst die **dritte** Wurzel, also hoch 1/3.")]),
        ("K = k·(1 + p/100)", "p", "100(K/k - 1)", ["K/k = 1 + p/100 | :k", "K/k - 1 = p/100 | −1", "100(K/k - 1) = p | ·100"],
         [("100K/k - 1", "Zuerst −1, dann die ganze Seite mal 100.")]),
        ("A = a·b + (a·c)/2", "a", "A/(b + c/2)", ["A = a·(b + c/2) | a herausheben", "A/(b + c/2) = a | :(b + c/2)"],
         [("A/b - c/2", "a steht zweimal – heb a zuerst heraus."), ("A - b - c/2", "a ist ein Faktor – rückgängig: durch, nicht minus.")])],
}

# B2.3: (Formel, Änderung als Text, {Variable: Faktor}, Ziel, Lösung, Erklärung)
B23 = {
    1: [("A = a·b", "a verdoppelt", {"a": 2}, "A", "2", "A ist direkt proportional zu a: doppelt so lang → doppelt so groß."),
        ("U = 4a", "a verdreifacht", {"a": 3}, "U", "3", "U ist direkt proportional zu a."),
        ("v = s/t", "s verdoppelt (t bleibt gleich)", {"s": 2}, "v", "2", "s steht im Zähler: doppelt so viel Weg in derselben Zeit → doppelt so schnell."),
        ("A = r²·π", "r verdoppelt", {"r": 2}, "A", "4", "r steht im Quadrat: `(2r)² = 4r²` – die Fläche wird viermal so groß."),
        ("V = a·b·c", "c verdreifacht", {"c": 3}, "V", "3", "V ist direkt proportional zu c."),
        ("G = m·g", "m halbiert", {"m": "1/2"}, "G", "1/2", "G ist direkt proportional zu m: halbe Masse → halbe Gewichtskraft.")],
    2: [("v = s/t", "t verdoppelt (s bleibt gleich)", {"t": 2}, "v", "1/2", "t steht im Nenner: doppelte Zeit für denselben Weg → halb so schnell."),
        ("A = r²·π", "r halbiert", {"r": "1/2"}, "A", "1/4", "`(r/2)² = r²/4` – die Fläche wird ein Viertel so groß."),
        ("V = a^3", "a verdoppelt", {"a": 2}, "V", "8", "`(2a)³ = 8a³` – achtmal so groß."),
        ("I = U/R", "R verdreifacht", {"R": 3}, "I", "1/3", "R steht im Nenner: dreifacher Widerstand → ein Drittel des Stroms."),
        ("A = a²", "a verdreifacht", {"a": 3}, "A", "9", "`(3a)² = 9a²`."),
        ("p = F/A", "A verdoppelt", {"A": 2}, "p", "1/2", "A steht im Nenner: doppelte Fläche → halber Druck.")],
    3: [("V = r²·π·h", "r verdoppelt und h halbiert", {"r": 2, "h": "1/2"}, "V", "2", "`2² · 1/2 = 2` – doppelt so groß."),
        ("W = m·v²/2", "v verdreifacht", {"v": 3}, "W", "9", "v steht im Quadrat: `3² = 9`."),
        ("A = a·b", "a verdoppelt und b halbiert", {"a": 2, "b": "1/2"}, "A", "1", "`2 · 1/2 = 1` – die Fläche bleibt gleich."),
        ("V = a²·h", "a verdoppelt und h verdoppelt", {"a": 2, "h": 2}, "V", "8", "`2² · 2 = 8`."),
        ("v = s/t", "s verdoppelt und t verdoppelt", {"s": 2, "t": 2}, "v", "1", "`2 : 2 = 1` – die Geschwindigkeit bleibt gleich."),
        ("F = m·a", "m halbiert und a verdreifacht", {"m": "1/2", "a": 3}, "F", "3/2", "`1/2 · 3 = 3/2` – eineinhalbmal so groß.")],
    4: [("V = 4/3·r³·π", "r halbiert", {"r": "1/2"}, "V", "1/8", "`(1/2)³ = 1/8`."),
        ("v = s/t", "s verdoppelt und t verdreifacht", {"s": 2, "t": 3}, "v", "2/3", "`2 : 3 = 2/3`."),
        ("F = m·v²/r", "v verdoppelt und r verdoppelt", {"v": 2, "r": 2}, "F", "2", "`2² : 2 = 2`."),
        ("p = F/A", "A auf ein Viertel verkleinert", {"A": "1/4"}, "p", "4", "A steht im Nenner: ein Viertel der Fläche → vierfacher Druck."),
        ("I = U/R", "U verdoppelt und R halbiert", {"U": 2, "R": "1/2"}, "I", "4", "`2 : 1/2 = 4`."),
        ("A = r²·π", "r um 10 % vergrößert", {"r": "1,1"}, "A", "1,21", "`1,1² = 1,21` – die Fläche wächst um 21 %, nicht um 10 %.")],
}


def b2_1(r, s, tabelle=B21):
    formel, nach, loesung, weg, fehler = r.choice(tabelle[s])
    return {"typ": "formel", "formel": formel, "nach": nach, "loesung": loesung, "weg": [formel] + weg,
            "tipps": [f"Ziel: {nach} soll allein auf einer Seite stehen. Was passiert mit {nach} in der Formel?",
                      UMKEHR, GANZE_SEITE],
            "fehler": [{"antwort": a, "hinweis": h} for a, h in fehler]}


def b2_2(r, s):
    return b2_1(r, s, B22)


def b2_3(r, s):
    formel, text, aenderung, ziel, loesung, erk = r.choice(B23[s])
    return {"typ": "zahl", "frage": f"In der Formel `{formel}` wird {text}. Mit welchem Faktor ändert sich {ziel}? "
                                     "(Zum Beispiel 2 für „doppelt so groß“, 1/2 für „halb so groß“.)",
            "loesung": loesung, "formel_faktor": {"formel": formel, "ziel": ziel, "aenderung": aenderung},
            "erklaerung": erk,
            "tipps": ["Setz für die geänderte Größe das Vielfache ein, z. B. statt r jetzt 2r.",
                      "Steht die Größe im Zähler, wirkt die Änderung direkt. Steht sie im Nenner, wirkt sie umgekehrt.",
                      "Steht die Größe im Quadrat, wird auch der Faktor quadriert."],
            "fehler": []}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    r = random.Random(20261021)
    for lid, fn, n in [("B2.1", b2_1, 7), ("B2.2", b2_2, 6), ("B2.3", b2_3, 5)]:
        schreibe(lid, erzeuge(lid, r, fn, n), "b2.py")


if __name__ == "__main__":
    main()
