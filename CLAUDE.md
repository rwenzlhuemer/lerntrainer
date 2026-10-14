# CLAUDE.md

## Projekt

Offline-Lerntrainer für Mathematik (AHS-Oberstufe Österreich bis zur Matura = SRP Mathematik AHS).
Zielgruppe: eine Schülerin, die **allein und in kurzen Einheiten (ca. 30 Minuten)** übt, bevorzugt am
**iPad mit Apple Pencil**, schwaches Ausgangsniveau und Mathe-Angst. Der Lernpfad beginnt deshalb bei den
Grundlagen (negative Zahlen, Brüche, Gleichungen umformen). Später soll **Spanisch** dazukommen.

**Das Repository ist öffentlich.** Keine persönlichen Daten, keine Angaben zur Nutzerin, keine Keys.

## Verbindliche Dokumente

- `docs/ARCHITEKTUR.md` – technische Grundsätze, Datenmodell, Prüftypen
- `docs/LERNPFAD.md` – Kapitel und Lernschritte mit IDs und Grundkompetenzen
- `quellen/srp_mat_grundkompetenzen_2024-10-25.pdf` (lokal) – offizieller GK-Katalog (Normalverteilung ab Mai 2027)

## Harte Regeln

- **Zur Laufzeit keine API-Calls, kein Netz.** Inhalte werden vorab erstellt und gebündelt.
- **Jede Mathe-Lösung wird beim Build mit sympy nachgerechnet** (`python tools/build.py`). Ein Fehler bricht den Build ab.
- YAML in `inhalte/` ist die einzige Quelle; `app/daten/` wird generiert, nie von Hand bearbeitet.
- Ton: warm, ermutigend; Fehler in Orange (#FFF2CC), nie Rot; keine Serien oder Tageszähler.
- Österreichische Fachbegriffe (Herausheben, Hochpunkt/Tiefpunkt, rechtwinkelig, Kurvendiskussion).
- Keine CDN-Abhängigkeit zur Laufzeit; alles liegt in `app/`.

## Befehle

```
python tools/build.py          # Inhalte prüfen und app/daten/ erzeugen
python -m http.server -d app   # lokal testen: http://localhost:8000
```

Veröffentlicht wird `app/` über GitHub Pages (Workflow in `.github/workflows/`).

## Ordner

- `_alt/` – frühere KI-basierte Python-App; ruht, gitignored, nicht weiterentwickeln
- `quellen/` – Schulbuch- und Matura-PDFs, gitignored (zu groß, nur lokal)

## Umgebung

Windows; das Bash-Tool startet hier nicht → PowerShell verwenden.
