// Schmierzettel: Zeichenfläche für Apple Pencil (und Finger, solange kein Stift benutzt wurde).
// Wird nicht ausgewertet – nur zum Rechnen wie auf Papier.

export function schmierzettel(behaelter) {
  behaelter.innerHTML = `
    <div class="sz-leiste">
      <span class="sz-titel">Schmierzettel</span>
      <button type="button" class="knopf klein" data-sz="zurueck">↶ Zurück</button>
      <button type="button" class="knopf klein" data-sz="leeren">Leeren</button>
    </div>
    <canvas class="sz-flaeche"></canvas>`;
  const canvas = behaelter.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const striche = [];
  let aktuell = null;
  let stiftGesehen = false;

  function groesse() {
    const r = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(r.width * dpr);
    canvas.height = Math.round(r.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    zeichneAlles();
  }

  function linie(s) {
    if (s.punkte.length < 2) {
      const [p] = s.punkte;
      ctx.beginPath();
      ctx.arc(p.x, p.y, s.dicke / 2, 0, Math.PI * 2);
      ctx.fill();
      return;
    }
    ctx.beginPath();
    ctx.moveTo(s.punkte[0].x, s.punkte[0].y);
    for (let i = 1; i < s.punkte.length - 1; i++) {
      const p = s.punkte[i], q = s.punkte[i + 1];
      ctx.quadraticCurveTo(p.x, p.y, (p.x + q.x) / 2, (p.y + q.y) / 2);
    }
    const l = s.punkte[s.punkte.length - 1];
    ctx.lineTo(l.x, l.y);
    ctx.lineWidth = s.dicke;
    ctx.stroke();
  }

  function zeichneAlles() {
    const r = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, r.width, r.height);
    ctx.strokeStyle = ctx.fillStyle = getComputedStyle(canvas).color;
    ctx.lineCap = ctx.lineJoin = "round";
    striche.forEach(linie);
  }

  function punkt(e) {
    const r = canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  canvas.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "pen") stiftGesehen = true;
    if (stiftGesehen && e.pointerType === "touch") return; // Handballen ignorieren
    e.preventDefault();
    canvas.setPointerCapture(e.pointerId);
    aktuell = { punkte: [punkt(e)], dicke: e.pointerType === "pen" ? 2.2 : 3 };
    striche.push(aktuell);
    zeichneAlles();
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!aktuell) return;
    e.preventDefault();
    const ereignisse = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
    for (const k of ereignisse) aktuell.punkte.push(punkt(k));
    zeichneAlles();
  });
  const ende = () => { aktuell = null; };
  canvas.addEventListener("pointerup", ende);
  canvas.addEventListener("pointercancel", ende);

  // iPad: Ohne das löst der Pencil Markieren, Lupe oder Kontextmenü aus, statt zu zeichnen
  for (const art of ["touchstart", "touchmove", "touchend"]) {
    canvas.addEventListener(art, (e) => e.preventDefault(), { passive: false });
  }
  canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  document.addEventListener("selectstart", (e) => { if (aktuell) e.preventDefault(); });

  behaelter.addEventListener("click", (e) => {
    const was = e.target.closest("[data-sz]")?.dataset.sz;
    if (was === "zurueck") { striche.pop(); zeichneAlles(); }
    if (was === "leeren") { striche.length = 0; zeichneAlles(); }
  });

  new ResizeObserver(groesse).observe(canvas);
  return { leeren() { striche.length = 0; zeichneAlles(); } };
}
