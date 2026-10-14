# Lerntrainer Mathematik

Offline-Übungs-App für Mathematik (AHS-Oberstufe Österreich, bis zur Matura), gebaut für das iPad
(Safari → „Zum Home-Bildschirm“) und jeden Browser. Kein Konto, keine Werbung, keine Server-Daten:
Der Lernstand bleibt auf dem Gerät.

- Kleine Lernschritte vom Fundament (negative Zahlen, Gleichungen umformen) bis zur Matura
- Gleichungen Zeile für Zeile lösen – jede Umformung wird einzeln geprüft
- Gestufte Tipps, Hinweise zu typischen Fehlern, Schmierzettel für den Apple Pencil
- Alle Lösungen werden beim Build mit [sympy](https://www.sympy.org) nachgerechnet

## Entwickeln

```
pip install sympy pyyaml
python tools/build.py              # Inhalte prüfen, app/daten/ erzeugen
node tools/test_mathe.mjs          # Gegenprobe: App-Prüflogik vs. sympy
python -m http.server 8765 -d app  # http://localhost:8765
node tools/test_browser.mjs        # Browser-Test (Chrome/Edge, Server muss laufen)
```

Aufbau und Regeln: [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md) · Lernpfad: [docs/LERNPFAD.md](docs/LERNPFAD.md)
