"""App-Icons erzeugen (einmalig; Ergebnis liegt in app/icons/).  python tools/icons.py"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ZIEL = Path(__file__).resolve().parent.parent / "app" / "icons"
HINTERGRUND = (47, 111, 126)   # --akzent
PAPIER = (250, 246, 239)


def schrift(groesse):
    for name in ("cambriai.ttf", "timesi.ttf", "DejaVuSerif-Italic.ttf"):
        try:
            return ImageFont.truetype(name, groesse)
        except OSError:
            continue
    return ImageFont.load_default()


def icon(px: int):
    bild = Image.new("RGB", (px, px), HINTERGRUND)
    d = ImageDraw.Draw(bild)
    # Papierblatt mit sanfter Ecke
    rand = px * 0.16
    d.rounded_rectangle([rand, rand, px - rand, px - rand], radius=px * 0.08, fill=PAPIER)
    text = "x="
    f = schrift(int(px * 0.36))
    box = d.textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((px - w) / 2 - box[0], (px - h) / 2 - box[1]), text, font=f, fill=HINTERGRUND)
    return bild


if __name__ == "__main__":
    ZIEL.mkdir(parents=True, exist_ok=True)
    for px in (180, 192, 512):
        icon(px).save(ZIEL / f"icon-{px}.png", optimize=True)
    print("Icons geschrieben:", ZIEL)
