// Handballen-Schutz für das ganze Blatt: Wer mit dem Apple Pencil schreibt, legt die Hand auf.
// Solche Berührungen dürfen nichts markieren, keine Knöpfe drücken und kein Feld auswählen.
// Gesperrt wird eine Berührung, wenn der Pencil gerade benutzt wird (oder eben benutzt wurde)
// oder wenn die Auflagefläche so groß ist, dass es kein Finger sein kann.

const NACHLAUF_MS = 1500; // so lange nach dem letzten Pencil-Strich gilt jede Berührung als Hand
const HANDBALLEN_RADIUS = 22; // CSS-Pixel; Fingerkuppen liegen deutlich darunter

let stiftZeit = -Infinity;
let stiftUnten = false;

const stiftAktiv = () => stiftUnten || performance.now() - stiftZeit < NACHLAUF_MS;
const istStift = (t) => t.touchType === "stylus";
const istHand = (t) => !istStift(t) && (stiftAktiv() || Math.max(t.radiusX || 0, t.radiusY || 0) >= HANDBALLEN_RADIUS);

function merkeStift(e) {
  if (e.pointerType !== "pen") return;
  stiftZeit = performance.now();
  if (e.type === "pointerdown") stiftUnten = true;
  if (e.type === "pointerup" || e.type === "pointercancel") stiftUnten = false;
}
for (const art of ["pointerdown", "pointermove", "pointerup", "pointercancel"]) {
  document.addEventListener(art, merkeStift, { capture: true, passive: true });
}

// iPad: touchstart mit preventDefault verhindert Markieren, Lupe, Klick und Fokuswechsel
const gesperrt = new Set();
function beiBeruehrung(e) {
  for (const t of e.changedTouches) {
    if (istStift(t)) stiftZeit = performance.now();
    else if (e.type === "touchstart" && istHand(t)) gesperrt.add(t.identifier);
  }
  const hand = [...e.changedTouches].some((t) => gesperrt.has(t.identifier));
  if (hand && e.cancelable) e.preventDefault();
  if (e.type === "touchend" || e.type === "touchcancel") {
    for (const t of e.changedTouches) gesperrt.delete(t.identifier);
  }
}
for (const art of ["touchstart", "touchmove", "touchend", "touchcancel"]) {
  document.addEventListener(art, beiBeruehrung, { capture: true, passive: false });
}

// Falls doch eine Auswahl entsteht, während der Pencil schreibt: wieder aufheben (nicht in Eingabefeldern)
document.addEventListener("selectstart", (e) => {
  if (stiftAktiv() && !e.target.closest?.("input, textarea")) e.preventDefault();
}, { capture: true });
document.addEventListener("contextmenu", (e) => {
  if (stiftAktiv() || gesperrt.size) e.preventDefault();
}, { capture: true });

// Für Zeichenflächen: Ist dieses Pointer-Ereignis eine aufgelegte Hand? (width/height = Durchmesser)
export const istHandZeiger = (e) => e.pointerType === "touch" &&
  (stiftAktiv() || Math.max(e.width || 0, e.height || 0) >= 2 * HANDBALLEN_RADIUS);
