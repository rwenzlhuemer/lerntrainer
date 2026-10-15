# Architektur – Lerntrainer (Entwurf v1, 14.10.2026)

## Grundsätze

1. **Zur Laufzeit keine KI, kein Internet.** Die App läuft offline auf dem iPad (Safari, „Zum Home-Bildschirm“)
   und im Browser am Laptop.
2. **Inhalte werden vorab erstellt** (von Claude) und beim Build **maschinell geprüft**: In Mathe rechnet
   sympy jede Lösung nach. Was die Prüfung nicht besteht, kommt nicht in die App.
3. **Eine kanonische Quelle, alles andere wird abgeleitet.** Die Aufgaben liegen als YAML in `inhalte/`,
   ein Build-Skript erzeugt daraus die JSON-Pakete für die App. Bei Fehlern bricht der Build ab.
4. **Fachneutral.** Mathe ist das erste Fach, Spanisch soll ohne Umbau folgen können.
5. **Lernstand bleibt auf dem Gerät** (IndexedDB), mit Export/Import als Datei zur Sicherung.
   Es gibt keine Server-Daten über die Nutzerin.

## Struktur (geplant)

```
inhalte/<fach>/<kapitel>/<lernschritt>.yaml   kanonische Quelle (Erklärung, Beispiel, Aufgaben)
tools/                                        Build und Prüfung (Python + sympy)
app/                                          Web-App (HTML/JS/CSS, ohne Build-Framework)
app/vendor/                                   lokal mitgelieferte Bibliotheken (KaTeX, math.js)
app/daten/<fach>/                             generierte JSON-Pakete (nicht von Hand bearbeiten)
docs/                                         Lernpfad, Architektur
```

## Fachneutrales Datenmodell

Fach → Kapitel → Lernschritt → Aufgaben. Jede Aufgabe hat einen **Prüftyp**; die App kennt die Prüftypen,
die Fächer liefern nur Daten.

| Prüftyp | Mathe | Spanisch |
|---------|-------|----------|
| `zahl` | 3,5 / 7/2 / -0,25 (Komma oder Punkt, Toleranz); optional `form: gekuerzt / nenner / dezimal` | – |
| `term` | Term-Äquivalenz numerisch geprüft, dazu die verlangte Form: `zusammengefasst`, `ausmultipliziert`, `faktor` (mit `faktor`), `gekuerzt`, `frei`. Zwischenschritte zeilenweise | – |
| `loesungsmenge` | {−2; 3}, Reihenfolge egal | – |
| `schritte` | Gleichung zeilenweise umformen, jede Zeile geprüft | – |
| `auswahl` | Multiple Choice, „2 aus 5“ | ja |
| `zuordnung` | Graph ↔ Gleichung | Wort ↔ Bedeutung |
| `luecke` | Lückentext (Matura-Format) | Konjugation, Präpositionen |
| `text` | – | Übersetzung; tolerant bei Groß-/Kleinschreibung, Hinweis bei fehlendem Akzent |
| `selbst` | Original-Maturaaufgabe mit Lösung zum Aufdecken, Selbsteinschätzung | Schreibaufgaben |

Jede Aufgabe kann **typische Fehler** mit eigenem Hinweis haben, z. B. Vorzeichenfehler → gezielter Tipp
statt bloß „leider falsch“.

## Spanisch (später) – was schon jetzt mitgedacht ist

- Prüftypen `text` und `luecke` sind fachneutral; Akzente/ñ mit eigener Symbolleiste (á é í ó ú ñ ¿ ¡).
- **Vokabeln mit Wiederholungsplan** (verteiltes Wiederholen) – ohne Serien, ohne „verpasste Tage“.
- **Vorlesen** über die Sprachausgabe des iPads (offline, spanische Stimme).
- Scribble (Apple Pencil) funktioniert auch für Spanisch.

## iPad-Eingabe

- **Scribble:** Handschrift mit Apple Pencil direkt in die Antwortfelder (eingebaut in iPadOS, offline).
- **Symbolleiste:** große Knöpfe für ², ³, √, Bruch, π, ≤, ≥ …
- **Schmierzettel:** Zeichenfläche mit Pencil neben jeder Aufgabe (wird nicht ausgewertet, nur zum Rechnen).

## Rücksicht auf die Nutzerin

- Kurze Einheiten (Länge wählbar: 10 / 20 / 30 Minuten), jederzeit unterbrechbar, Stand bleibt erhalten.
- **Keine Serien, keine Tageszähler**, nichts, was Pausen bestraft. Fortschritt zeigt, was sie *kann*.
- Nach längerer Pause: zuerst ein kurzes Aufwärmen mit Bekanntem.
- Falsche Antworten in warmem Orange (#FFF2CC), nie Rot; jede Rückmeldung freundlich, mit einem
  ermutigenden Satz am Schluss.
- Österreichische Fachbegriffe (Herausheben, Hochpunkt/Tiefpunkt, Kurvendiskussion, rechtwinkelig …).
