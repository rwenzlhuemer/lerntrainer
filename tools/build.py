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
TYPEN = {"gleichung", "zahl", "auswahl"}


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
    if "rechnung" in a:
        try:
            if sympy.simplify(notation.zahl(a["rechnung"]) - soll) != 0:
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
    for f in a.get("fehler", []):
        try:
            if sympy.simplify(notation.zahl(str(f["antwort"])) - soll) == 0:
                fehler.melde(wo, f"Fehler-Antwort {f['antwort']!r} ist in Wahrheit richtig")
        except Exception as e:  # noqa: BLE001
            fehler.melde(wo, f"Fehler-Antwort nicht lesbar ({e})")


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


PRUEFER = {"gleichung": pruefe_gleichung, "zahl": pruefe_zahl, "auswahl": pruefe_auswahl}


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
                    text = a.get("gleichung") if a.get("typ") == "gleichung" else a.get("frage")
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
                    if g and "=" in teil_gl:
                        try:
                            if notation.loesungsmenge(teil_gl) != notation.loesungsmenge(g):
                                fehler.melde(lid, f"Beispiel-Zeile {zeile!r} ist keine Äquivalenzumformung")
                        except Exception as e:  # noqa: BLE001
                            fehler.melde(lid, f"Beispiel-Zeile {zeile!r} nicht lesbar ({e})")
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
