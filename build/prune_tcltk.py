# -*- coding: utf-8 -*-
"""Dünnt die mitgelieferten Tcl/Tk-Daten aus.

Tcl bringt Zeitzonendaten, Sprachkataloge und rund 80 Zeichensatztabellen mit.
Voci braucht davon nichts: keine Zeitzonen, keine übersetzten Dialoge, und die
Texte liegen ohnehin als Unicode im Programm. Das spart mehrere hundert Dateien.

Aufruf: python build/prune_tcltk.py [--vorsichtig] <ordner> [...]

Mit --vorsichtig fallen nur Zeitzonen und Sprachkataloge weg. Das wird für
macOS verwendet, weil dort nicht getestet werden kann, ob Tk die Bilddateien
oder weitere Zeichensätze doch anfasst.
"""
import pathlib
import shutil
import sys

# Ganze Verzeichnisse, die wegfallen
WEG = ("tzdata", "msgs", "images", "demos")

# Zeichensatztabellen, die bleiben: Systemkodierungen von Windows, macOS und
# Linux plus die Grundlagen, die Tcl beim Start selbst anfasst.
BEHALTEN = {"ascii.enc", "utf-8.enc", "unicode.enc", "iso8859-1.enc",
            "iso8859-15.enc", "cp1252.enc", "cp437.enc", "cp850.enc",
            "macRoman.enc"}


def ausduennen(wurzel, vorsichtig=False):
    wurzel = pathlib.Path(wurzel)
    vorher = sum(1 for _ in wurzel.rglob("*") if _.is_file())
    entfernt = 0

    weg = ("tzdata", "msgs") if vorsichtig else WEG
    for ordner in wurzel.rglob("*"):
        if ordner.is_dir() and ordner.name in weg and _in_tcltk(ordner):
            entfernt += sum(1 for _ in ordner.rglob("*") if _.is_file())
            shutil.rmtree(ordner)

    for ordner in ([] if vorsichtig else wurzel.rglob("encoding")):
        if not ordner.is_dir():
            continue
        for datei in ordner.iterdir():
            if datei.is_file() and datei.name not in BEHALTEN:
                datei.unlink()
                entfernt += 1

    nachher = sum(1 for _ in wurzel.rglob("*") if _.is_file())
    print(f"{wurzel}: {vorher} -> {nachher} Dateien ({entfernt} entfernt)")
    return nachher


def _in_tcltk(ordner):
    """Nur innerhalb der Tcl/Tk-Daten aufräumen, nicht irgendwo sonst."""
    # macOS nennt die Ordner "_tcl_data"/"_tk_data", Windows "tcl"/"tk8.6".
    return any(teil.lower().lstrip("_").startswith(("tcl", "tk"))
               for teil in ordner.parts)


if __name__ == "__main__":
    argumente = sys.argv[1:]
    vorsichtig = "--vorsichtig" in argumente
    ziele = [a for a in argumente if not a.startswith("--")]
    if not ziele:
        sys.exit("Aufruf: python build/prune_tcltk.py [--vorsichtig] <ordner> [...]")
    for ziel in ziele:
        ausduennen(ziel, vorsichtig)
