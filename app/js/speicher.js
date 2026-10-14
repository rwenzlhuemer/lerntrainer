// Lernstand – bleibt nur auf diesem Gerät (localStorage). Sicherung über Export/Import als Datei.

const SCHLUESSEL = "lerntrainer.v1";
export const HOECHSTE_STUFE = 4;
const SICHER_AB = 3; // wer Stufe 3 sicher kann, hat den Schritt geschafft; Stufe 4 ist Kür

function leer() {
  return { version: 1, faecher: {}, letzter: null, letzteAktivitaet: null, hinweiseGesehen: {} };
}

let zustand = laden();

function laden() {
  try {
    const roh = localStorage.getItem(SCHLUESSEL);
    if (roh) return { ...leer(), ...JSON.parse(roh) };
  } catch { /* privates Fenster o. Ä. – dann eben ohne Speicher */ }
  return leer();
}

function sichern() {
  try { localStorage.setItem(SCHLUESSEL, JSON.stringify(zustand)); } catch { /* s. o. */ }
}

// Safari darf den Speicher sonst bei Platzmangel räumen
export function dauerhaftAnfragen() {
  try { navigator.storage?.persist?.(); } catch { /* egal */ }
}

export function lernschritt(fach, lid) {
  const f = (zustand.faecher[fach] ??= { ls: {} });
  return (f.ls[lid] ??= { stufe: 1, status: "neu", verlauf: [] });
}

// ergebnis: "richtig" (allein gelöst) | "hilfe" (mit Tipp oder nach Fehlversuch) | "gezeigt" (Lösung angesehen)
export function merkeErgebnis(fach, lid, aid, stufe, ergebnis) {
  const ls = lernschritt(fach, lid);
  ls.verlauf.push({ a: aid, s: stufe, e: ergebnis, t: Date.now() });
  if (ls.verlauf.length > 200) ls.verlauf = ls.verlauf.slice(-200);
  if (ls.status === "neu") ls.status = "angefangen";

  // Aufstieg: 3 der letzten 4 Aufgaben dieser Stufe allein gelöst
  const dieseStufe = ls.verlauf.filter((v) => v.s === ls.stufe).slice(-4);
  const allein = dieseStufe.filter((v) => v.e === "richtig").length;
  let meldung = null;
  if (dieseStufe.length >= 3 && allein >= 3) {
    if (ls.stufe >= SICHER_AB && ls.status !== "sicher") {
      ls.status = "sicher";
      meldung = "sicher";
    } else if (ls.stufe < HOECHSTE_STUFE) {
      meldung = "aufstieg";
    }
    if (ls.stufe < HOECHSTE_STUFE) ls.stufe += 1;
  }
  // Sanfter Abstieg: zweimal hintereinander die Lösung angesehen
  const letzte2 = ls.verlauf.slice(-2);
  if (ls.stufe > 1 && letzte2.length === 2 && letzte2.every((v) => v.e === "gezeigt" && v.s === ls.stufe)) {
    ls.stufe -= 1;
    meldung = "leichter";
  }
  zustand.letzter = { fach, lid };
  zustand.letzteAktivitaet = Date.now();
  sichern();
  return meldung;
}

export function setzeSicher(fach, lid) {
  const ls = lernschritt(fach, lid);
  ls.status = "sicher";
  ls.stufe = HOECHSTE_STUFE;
  sichern();
}

// „Zu leicht“: eine Stufe hinauf, ohne dass die laufende Aufgabe zählt
export function stufeHoch(fach, lid) {
  const ls = lernschritt(fach, lid);
  if (ls.stufe < HOECHSTE_STUFE) ls.stufe += 1;
  if (ls.status === "neu") ls.status = "angefangen";
  sichern();
  return ls.stufe;
}

export function merkeBesuch(fach, lid) {
  zustand.letzter = { fach, lid };
  zustand.letzteAktivitaet = Date.now();
  sichern();
}

export function letzter() { return zustand.letzter; }
export function letzteAktivitaet() { return zustand.letzteAktivitaet; }

export function hinweisGesehen(name) { return !!zustand.hinweiseGesehen[name]; }
export function hinweisMerken(name) { zustand.hinweiseGesehen[name] = true; sichern(); }

export function exportieren() {
  return JSON.stringify({ ...zustand, exportiert: new Date().toISOString() }, null, 1);
}

export function importieren(text) {
  const neu = JSON.parse(text);
  if (!neu || neu.version !== 1 || typeof neu.faecher !== "object") throw new Error("Keine gültige Sicherung");
  zustand = { ...leer(), ...neu };
  sichern();
}

export function zuruecksetzen() {
  zustand = leer();
  sichern();
}
