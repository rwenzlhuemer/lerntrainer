// Funktionsgraphen als SVG – offline, ohne Bibliothek.
// spec: { x: [xmin, xmax], y: [ymin, ymax], kurven: [{ term: "2x - 1", name?: "f" }],
//         punkte: [{ x, y, name? }], achsen?: { x: "t in h", y: "T in °C" }, schritt?: [sx, sy] }
import { versuche, werte } from "./mathe.js";

const FARBEN = ["#2f6f7e", "#c0622b", "#6b4fa0", "#3f8a4a"];
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let zaehler = 0;
const zahl = (v) => String(Math.round(v * 1000) / 1000).replace(".", ",").replace("-", "−");

export function graphSVG(spec) {
  const [x0, x1] = spec.x, [y0, y1] = spec.y;
  const [sx, sy] = spec.schritt || [1, 1];
  const B = 340, H = Math.round(B * Math.min(1.2, Math.max(0.55, (y1 - y0) / (x1 - x0) * (sx / sy) || 1)));
  const rand = 26;
  const px = (x) => rand + ((x - x0) / (x1 - x0)) * (B - 2 * rand);
  const py = (y) => H - rand - ((y - y0) / (y1 - y0)) * (H - 2 * rand);
  const teile = [];
  const clip = `g-clip-${++zaehler}`;
  teile.push(`<clipPath id="${clip}"><rect x="${px(x0)}" y="${py(y1)}" width="${px(x1) - px(x0)}" height="${py(y0) - py(y1)}"/></clipPath>`);
  // Raster
  for (let x = Math.ceil(x0 / sx) * sx; x <= x1 + 1e-9; x += sx) teile.push(`<line class="g-raster" x1="${px(x)}" y1="${py(y0)}" x2="${px(x)}" y2="${py(y1)}"/>`);
  for (let y = Math.ceil(y0 / sy) * sy; y <= y1 + 1e-9; y += sy) teile.push(`<line class="g-raster" x1="${px(x0)}" y1="${py(y)}" x2="${px(x1)}" y2="${py(y)}"/>`);
  // Achsen mit Pfeilen
  const ax = y0 <= 0 && y1 >= 0 ? 0 : y0, ay = x0 <= 0 && x1 >= 0 ? 0 : x0;
  teile.push(`<line class="g-achse" x1="${px(x0)}" y1="${py(ax)}" x2="${px(x1) + 10}" y2="${py(ax)}" marker-end="url(#pfeil)"/>`);
  teile.push(`<line class="g-achse" x1="${px(ay)}" y1="${py(y0)}" x2="${px(ay)}" y2="${py(y1) - 10}" marker-end="url(#pfeil)"/>`);
  // Beschriftung: jede zweite Linie bei dichtem Raster
  const nx = Math.round((x1 - x0) / sx), ny = Math.round((y1 - y0) / sy);
  const jx = nx > 12 ? 2 : 1, jy = ny > 12 ? 2 : 1;
  let i = 0;
  for (let x = Math.ceil(x0 / sx) * sx; x <= x1 + 1e-9; x += sx, i++) {
    if (Math.abs(x) < 1e-9 || i % jx) continue;
    teile.push(`<text class="g-zahl" x="${px(x)}" y="${py(ax) + 14}" text-anchor="middle">${zahl(x)}</text>`);
  }
  i = 0;
  for (let y = Math.ceil(y0 / sy) * sy; y <= y1 + 1e-9; y += sy, i++) {
    if (Math.abs(y) < 1e-9 || i % jy) continue;
    teile.push(`<text class="g-zahl" x="${px(ay) - 5}" y="${py(y) + 4}" text-anchor="end">${zahl(y)}</text>`);
  }
  if (ax === 0 && ay === 0) teile.push(`<text class="g-zahl" x="${px(0) - 5}" y="${py(0) + 14}" text-anchor="end">0</text>`);
  const ach = spec.achsen || { x: "x", y: "y" };
  teile.push(`<text class="g-achsname" x="${px(x1) + 8}" y="${py(ax) - 6}" text-anchor="end">${esc(ach.x)}</text>`);
  teile.push(`<text class="g-achsname" x="${px(ay) + 6}" y="${py(y1) - 2}">${esc(ach.y)}</text>`);
  // Kurven
  (spec.kurven || []).forEach((k, n) => {
    const g = versuche(k.term);
    if (!g || g.gleichung) return;
    const pfad = [];
    let offen = false;
    const N = 240;
    for (let s = 0; s <= N; s++) {
      const x = x0 + ((x1 - x0) * s) / N;
      let y;
      try { y = werte(g.term, { x }); } catch { y = NaN; }
      if (!Number.isFinite(y) || y < y0 - (y1 - y0) || y > y1 + (y1 - y0)) { offen = false; continue; }
      pfad.push(`${offen ? "L" : "M"}${px(x).toFixed(1)},${py(y).toFixed(1)}`);
      offen = true;
    }
    const farbe = FARBEN[n % FARBEN.length];
    teile.push(`<path class="g-kurve" d="${pfad.join("")}" stroke="${farbe}" clip-path="url(#${clip})"/>`);
    if (k.name) {
      // Name am rechten Rand, wo die Kurve sichtbar ist
      for (let s = Math.round(N * 0.85); s >= 0; s -= 8) {
        const x = x0 + ((x1 - x0) * s) / N;
        let y;
        try { y = werte(g.term, { x }); } catch { continue; }
        if (Number.isFinite(y) && y > y0 && y < y1) {
          teile.push(`<text class="g-name" x="${px(x) - 4}" y="${py(y) - 8}" fill="${farbe}" text-anchor="end">${esc(k.name)}</text>`);
          break;
        }
      }
    }
  });
  // Punkte
  for (const p of spec.punkte || []) {
    teile.push(`<circle class="g-punkt" cx="${px(p.x)}" cy="${py(p.y)}" r="4.5"/>`);
    if (p.name) teile.push(`<text class="g-name" x="${px(p.x) + 7}" y="${py(p.y) - 7}">${esc(p.name)}</text>`);
  }
  return `<svg class="graph" viewBox="0 0 ${B + 14} ${H}" role="img" aria-label="Graph">
    <defs><marker id="pfeil" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
    ${teile.join("\n")}</svg>`;
}
