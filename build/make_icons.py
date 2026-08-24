# -*- coding: utf-8 -*-
"""Erzeugt das App-Icon (Trikolore) als PNG, ICO und ICNS in assets/."""
import pathlib
import struct

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

BLEU = (0, 35, 149)
BLANC = (255, 255, 255)
ROUGE = (237, 41, 57)
RAND = (198, 198, 198)          # Haarlinie, damit der weisse Streifen nicht verschwindet


def flagge(size, ss=8):
    """Quadratische Trikolore mit abgerundeten Ecken, kantengeglättet."""
    n = size * ss
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    maske = Image.new("L", (n, n), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, n - 1, n - 1],
                                            radius=int(n * 0.18), fill=255)
    streifen = Image.new("RGBA", (n, n))
    d = ImageDraw.Draw(streifen)
    d.rectangle([0, 0, n // 3, n], fill=BLEU + (255,))
    d.rectangle([n // 3, 0, 2 * n // 3, n], fill=BLANC + (255,))
    d.rectangle([2 * n // 3, 0, n, n], fill=ROUGE + (255,))
    img.paste(streifen, (0, 0), maske)

    kante = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(kante).rounded_rectangle(
        [ss // 2, ss // 2, n - 1 - ss // 2, n - 1 - ss // 2],
        radius=int(n * 0.18), outline=RAND + (255,), width=max(1, ss))
    img.alpha_composite(kante)
    return img.resize((size, size), Image.LANCZOS)


def icns(pfad, quelle):
    """ICNS aus PNG-Blöcken schreiben (kein macOS-Werkzeug nötig)."""
    typen = [(b"icp4", 16), (b"icp5", 32), (b"ic11", 32), (b"ic12", 64),
             (b"ic07", 128), (b"ic08", 256), (b"ic13", 256),
             (b"ic09", 512), (b"ic14", 512), (b"ic10", 1024)]
    import io
    bloecke = b""
    for kennung, groesse in typen:
        puffer = io.BytesIO()
        quelle.resize((groesse, groesse), Image.LANCZOS).save(puffer, "PNG")
        daten = puffer.getvalue()
        bloecke += kennung + struct.pack(">I", len(daten) + 8) + daten
    pfad.write_bytes(b"icns" + struct.pack(">I", len(bloecke) + 8) + bloecke)


gross = flagge(1024)
gross.save(OUT / "voci.png")
gross.save(OUT / "voci.ico",
           sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
icns(OUT / "voci.icns", gross)
for p in ("voci.png", "voci.ico", "voci.icns"):
    print(p, (OUT / p).stat().st_size, "Bytes")
