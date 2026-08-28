# -*- coding: utf-8 -*-
"""
Voci – Vokabel-Flashcard, immer im Vordergrund. Läuft unter Windows, macOS
und Linux.

Bedienung:
  Klick auf die Karte        -> flippt FR <-> DE (beide Richtungen)
  Kreis oben links (FR/DE)   -> Startsprache umschalten
  Kreis oben rechts (x)      -> beenden
  Kreis unten links (<-)     -> ein Wort zurück (max. 10)
  Kreis unten rechts (->)    -> nächstes Wort
  Karte ziehen               -> Fenster verschieben
  Rand ziehen                -> Fenster vergrössern/verkleinern
  Taste d                    -> Dark Mode an/aus\n  Taste u                    -> gefundenes Update einspielen

Wenn das Fenster den Fokus verliert und das aktuelle Wort schon geflippt
wurde, kommt nach 5 Sekunden automatisch das nächste Wort
(ein feiner Balken unten zählt runter) – ausser man tabbt vorher zurück.
"""

import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import tkinter.font as tkfont
import urllib.error
import urllib.request
import zipfile

EINGEBAUTE_VOCAB = json.loads(r'''__VOCAB_JSON__''')
VERSION = "__VERSION__"

# Fenstersymbol (Trikolore) als eingebettetes PNG - ohne das zeigt Tk in der
# Taskleiste sein eigenes Feder-Logo.
ICON_B64 = "__ICON_B64__"

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

# DPI-Awareness MUSS vor dem ersten Tk-Fenster gesetzt werden, sonst skaliert
# Windows das Fenster als Bitmap hoch -> alles sieht verpixelt/unscharf aus.
if IS_WIN:
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)   # per-monitor
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    try:
        # Eigene Kennung, damit die Taskleiste das Fenstersymbol verwendet und
        # nicht das des startenden Programms.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ch.janiki33.voci")
    except Exception:
        pass

# ---------------------------------------------------------------- Farben
# Zwei Paletten, umschaltbar mit der Taste d
THEMEN = {
    "hell": {
        "bg": (255, 255, 255),    # Karte
        "fg": (17, 17, 17),       # Text / Icons
        "hover": (235, 235, 235), # Knopf beim Hovern
        "rand": "#d8d8d8",        # Kartenrand
        "timer": "#ededed",       # Countdown-Balken (dezent)
    },
    "dunkel": {
        "bg": (0, 0, 0),
        "fg": (255, 255, 255),
        "hover": (38, 38, 38),
        "rand": "#333333",
        "timer": "#2b2b2b",
    },
}
KEY = "#00fe00"               # Farbschlüssel für runde Ecken (Windows)
FALLBACK_VOID = "#bdbdbd"     # falls die Plattform keine Transparenz kann

# ---------------------------------------------------------------- Verhalten
AUTO_DELAY_MS = 5000          # 5 s bis zum Auto-Weiter
FLIPS_NEEDED = 1              # Timer schon nach dem ersten Flip
HISTORY_MAX = 10              # max. 10 Wörter zurück
POLL_MS = 250                 # Fokus-Polling (Windows)

CURSOR_HAND = "pointinghand" if IS_MAC else "hand2"
if IS_MAC:
    CURSOR_EDGE = {"n": "resizeupdown", "s": "resizeupdown",
                   "w": "resizeleftright", "e": "resizeleftright"}
else:
    CURSOR_EDGE = {"n": "sb_v_double_arrow", "s": "sb_v_double_arrow",
                   "w": "sb_h_double_arrow", "e": "sb_h_double_arrow",
                   "nw": "top_left_corner", "ne": "top_right_corner",
                   "sw": "bottom_left_corner", "se": "bottom_right_corner"}

FONT_WUNSCH = (("SF Pro Text", "Helvetica Neue", "Lucida Grande") if IS_MAC else
               ("Segoe UI", "Tahoma") if IS_WIN else
               ("DejaVu Sans", "Liberation Sans", "Arial"))


def hexc(c):
    return "#%02x%02x%02x" % (int(c[0]), int(c[1]), int(c[2]))


def blend(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def dist_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def render_button(size, radius, disc_color, segs, seg_w, icon_color, bg):
    """Zeichnet Kreis + Linien-Icon kantengeglättet (Distanzfeld-AA) in ein
    PhotoImage – Tk-Canvas-Formen selbst sind unter Windows hart gepixelt."""
    cx = cy = size / 2.0
    rows = []
    for y in range(size):
        py = y + 0.5
        cells = []
        for x in range(size):
            px = x + 0.5
            col = bg
            d = math.hypot(px - cx, py - cy) - radius
            a = 0.5 - d
            if a > 0:
                col = blend(col, disc_color, min(a, 1.0))
            for (x1, y1, x2, y2) in segs:
                d = dist_seg(px, py, cx + x1, cy + y1, cx + x2, cy + y2) - seg_w / 2.0
                a = 0.5 - d
                if a > 0:
                    col = blend(col, icon_color, min(a, 1.0))
            cells.append(hexc(col))
        rows.append("{" + " ".join(cells) + "}")
    img = tk.PhotoImage(width=size, height=size)
    img.put(" ".join(rows))
    return img


def icon_segs(tag, r):
    """Icon-Linien relativ zum Knopfmittelpunkt."""
    a = r * 0.40
    h = a * 0.72
    if tag == "close":
        return [(-a, -a, a, a), (-a, a, a, -a)]
    if tag == "next":
        return [(-a, 0, a, 0), (a - h, -h, a, 0), (a - h, h, a, 0)]
    if tag == "back":
        return [(a, 0, -a, 0), (-a + h, -h, -a, 0), (-a + h, h, -a, 0)]
    return []


def rounded_rect(cnv, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cnv.create_polygon(pts, smooth=True, **kw)


# ---------------------------------------------------------------- Updates
REPO = "janiki33/voci"
NETZ_TIMEOUT = 8


def _adresse(schluessel, standard):
    """Adressen sind über Umgebungsvariablen überschreibbar - nur damit sich
    der Updater gegen einen lokalen Server testen lässt."""
    return os.environ.get(schluessel, standard)


RELEASE_URL = _adresse("VOCI_RELEASE_URL",
                       "https://github.com/%s/releases/latest" % REPO)
DOWNLOAD_URL = _adresse("VOCI_DOWNLOAD_URL",
                        "https://github.com/%s/releases/latest/download" % REPO)
VOCAB_URL = _adresse("VOCI_VOCAB_URL",
                     "https://raw.githubusercontent.com/%s/main/vokabeln.json" % REPO)
TESTMODUS = bool(os.environ.get("VOCI_RELEASE_URL"))


def datenordner():
    """Pro Benutzer beschreibbarer Ort für die nachgeladene Wortliste."""
    if IS_WIN:
        wurzel = os.environ.get("APPDATA") or pathlib.Path.home()
    elif IS_MAC:
        wurzel = pathlib.Path.home() / "Library" / "Application Support"
    else:
        wurzel = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
    ordner = pathlib.Path(wurzel) / "Voci"
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner


def vokabeln_gueltig(daten):
    """Eine kaputte oder halbe Datei darf das Programm nicht lahmlegen."""
    return (isinstance(daten, list) and len(daten) >= 10
            and all(isinstance(e, dict) and e.get("fr") and e.get("de")
                    for e in daten))


def lade_vokabeln():
    """Nachgeladene Liste bevorzugen, sonst die eingebaute."""
    try:
        datei = datenordner() / "vokabeln.json"
        if datei.exists():
            daten = json.loads(datei.read_text(encoding="utf-8"))
            if vokabeln_gueltig(daten):
                return daten
    except Exception:
        pass
    return EINGEBAUTE_VOCAB


def _hole(adresse, timeout=NETZ_TIMEOUT):
    anfrage = urllib.request.Request(adresse, headers={"User-Agent": "Voci"})
    with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
        return antwort.read()


def vokabeln_auffrischen():
    """Holt die aktuelle Wortliste. Wirkt ab dem nächsten Start."""
    try:
        daten = json.loads(_hole(VOCAB_URL).decode("utf-8"))
        if not vokabeln_gueltig(daten):
            return False
        datei = datenordner() / "vokabeln.json"
        neu = json.dumps(daten, ensure_ascii=False, indent=1)
        if datei.exists() and datei.read_text(encoding="utf-8") == neu:
            return False
        datei.write_text(neu, encoding="utf-8")
        return True
    except Exception:
        return False


def neueste_version():
    """Liest die Version aus der Weiterleitung von /releases/latest. Das ist
    eine gewöhnliche Webanfrage und läuft damit in kein API-Limit."""
    class OhneWeiterleitung(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    oeffner = urllib.request.build_opener(OhneWeiterleitung)
    anfrage = urllib.request.Request(RELEASE_URL, headers={"User-Agent": "Voci"})
    try:
        with oeffner.open(anfrage, timeout=NETZ_TIMEOUT) as antwort:
            ziel = antwort.geturl()
    except urllib.error.HTTPError as fehler:
        if fehler.code not in (301, 302, 303, 307, 308):
            raise
        ziel = fehler.headers.get("Location", "")
    return ziel.rstrip("/").rsplit("/", 1)[-1] or None


def installation():
    """Was müsste ein Update ersetzen - eine Datei oder ein ganzer Ordner?"""
    if "__compiled__" in globals():                  # mit Nuitka gebaut
        pfad = pathlib.Path(sys.argv[0]).resolve()
        if os.environ.get("NUITKA_ONEFILE_PARENT"):
            return "einzeldatei", pfad
        for eltern in pfad.parents:
            if eltern.suffix == ".app":
                return "ordner", eltern
        return "ordner", pfad.parent
    if getattr(sys, "frozen", False):                # mit PyInstaller gebaut
        pfad = pathlib.Path(sys.executable).resolve()
        for eltern in pfad.parents:
            if eltern.suffix == ".app":
                return "ordner", eltern
        return "ordner", pfad.parent
    return "einzeldatei", pathlib.Path(__file__).resolve()


def asset_name(art):
    """Welche Datei aus dem Release passt zu dieser Installation?"""
    if os.environ.get("VOCI_ASSET"):                 # nur für Tests
        return os.environ["VOCI_ASSET"]
    if art == "einzeldatei":
        if IS_WIN and "__compiled__" in globals():
            return "Voci.exe"
        return "Voci.pyw"
    if IS_WIN:
        return "Voci-Windows-Ordner.zip"
    if IS_MAC:
        return "Voci-macOS.zip"
    return None                                      # dafür gibt es kein Release


def update_vorbereiten(art, ziel, arbeitsordner):
    """Lädt die passende Datei und legt daneben, was nachher an die Stelle von
    *ziel* rücken soll. Es wird noch nichts ersetzt."""
    name = asset_name(art)
    if not name:
        raise RuntimeError("für diese Fassung gibt es kein Update")
    rohdaten = _hole("%s/%s" % (DOWNLOAD_URL, name), timeout=120)
    arbeitsordner = pathlib.Path(arbeitsordner)

    if not name.endswith(".zip"):
        neu = arbeitsordner / ziel.name
        neu.write_bytes(rohdaten)
        if art == "einzeldatei" and not IS_WIN:
            neu.chmod(0o755)
        return neu

    paket = arbeitsordner / name
    paket.write_bytes(rohdaten)
    entpackt = arbeitsordner / "entpackt"
    with zipfile.ZipFile(paket) as archiv:
        archiv.extractall(entpackt)
    inhalt = [p for p in entpackt.iterdir() if not p.name.startswith("__MACOSX")]
    if len(inhalt) != 1 or not inhalt[0].is_dir():
        raise RuntimeError("unerwarteter Inhalt im Archiv")
    neu = inhalt[0]
    if not any(neu.rglob("Voci*")):
        raise RuntimeError("im Archiv fehlt das Programm")
    for datei in neu.rglob("*"):                     # Rechte gehen im ZIP verloren
        if datei.is_file() and (datei.suffix in ("", ".sh") or "MacOS" in datei.parts):
            try:
                datei.chmod(0o755)
            except OSError:
                pass
    return neu


def tausch_starten(ziel, neu, startbefehl):
    """Startet ein kleines Hilfsprogramm, das wartet, bis Voci beendet ist, und
    dann tauscht. Ein laufendes Programm kann sich nicht selbst ersetzen.
    Die alte Fassung wird erst weggeräumt, wenn die neue an Ort und Stelle ist -
    schlägt der Tausch fehl, kommt die alte zurück."""
    pid = os.getpid()
    sicherung = "%s.alt" % ziel
    if IS_WIN:
        skript = pathlib.Path(neu).parent / "voci_update.cmd"
        skript.write_text(
            "@echo off\r\n"
            ":warten\r\n"
            'tasklist /fi "PID eq %d" 2>nul | find "%d" >nul\r\n'
            "if not errorlevel 1 (\r\n"
            "  timeout /t 1 /nobreak >nul\r\n"
            "  goto warten\r\n"
            ")\r\n"
            'if exist "%s" rmdir /s /q "%s" 2>nul\r\n'
            'if exist "%s" del /q "%s" 2>nul\r\n'
            'move "%s" "%s" >nul || exit /b 1\r\n'
            'move "%s" "%s" >nul || (move "%s" "%s" >nul & exit /b 1)\r\n'
            'start "" %s\r\n'
            % (pid, pid, sicherung, sicherung, sicherung, sicherung,
               ziel, sicherung, neu, ziel, sicherung, ziel, startbefehl),
            encoding="utf-8")
        subprocess.Popen(["cmd", "/c", str(skript)], cwd=str(skript.parent),
                         creationflags=0x08000000)   # ohne Konsolenfenster
    else:
        skript = pathlib.Path(neu).parent / "voci_update.sh"
        skript.write_text(
            "#!/bin/sh\n"
            "while kill -0 %d 2>/dev/null; do sleep 0.5; done\n"
            'rm -rf "%s"\n'
            'mv "%s" "%s" || exit 1\n'
            'mv "%s" "%s" || { mv "%s" "%s"; exit 1; }\n'
            'rm -rf "%s"\n'
            "%s &\n"
            % (pid, sicherung, ziel, sicherung, neu, ziel, sicherung, ziel,
               sicherung, startbefehl),
            encoding="utf-8")
        skript.chmod(0o755)
        subprocess.Popen(["/bin/sh", str(skript)], cwd=str(skript.parent),
                         start_new_session=True)


def startbefehl_fuer(art, ziel):
    if art == "ordner":
        if IS_MAC and str(ziel).endswith(".app"):
            return 'open "%s"' % ziel
        exe = pathlib.Path(ziel) / ("Voci.exe" if IS_WIN else "Voci")
        return '"%s"' % exe
    if str(ziel).endswith(".pyw"):
        return '"%s" "%s"' % (sys.executable, ziel)
    return '"%s"' % ziel


class Voci:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # kein Titel, kein Min/Max
        self.root.attributes("-topmost", True)    # immer im Vordergrund
        try:
            self._icon = tk.PhotoImage(data=ICON_B64)   # Referenz festhalten
            self.root.iconphoto(True, self._icon)
        except Exception:
            pass

        # Alles in echten Bildschirmpixeln rechnen (DPI-Faktor unter Windows).
        dpi = self.root.winfo_fpixels("1i")
        self.k = max(1.0, dpi / 96.0)

        self.w = int(380 * self.k)
        self.h = int(230 * self.k)
        self.min_w = int(260 * self.k)
        self.min_h = int(150 * self.k)
        self.pad = int(30 * self.k)               # Knopf-Abstand zur Ecke
        self.br = int(15 * self.k)                # Knopfradius
        self.edge = max(5, int(6 * self.k))       # Greifzone am Rand
        self.corner = int(20 * self.k)            # Eckenradius der Karte
        self.root.geometry("%dx%d+%d+%d" % (self.w, self.h, 140, 140))

        self.void = self._setup_transparency()
        try:
            self.cnv = tk.Canvas(self.root, bd=0, highlightthickness=0, bg=self.void)
        except tk.TclError:                       # Plattform mag den Farbnamen nicht
            self.void = FALLBACK_VOID
            self.cnv = tk.Canvas(self.root, bd=0, highlightthickness=0, bg=self.void)
        self.cnv.pack(fill="both", expand=True)

        familie = self._pick_font()
        self.tiny_px = int(11 * self.k)
        self.font_word = tkfont.Font(family=familie, size=-int(20 * self.k))
        self.font_tiny = tkfont.Font(family=familie, size=-self.tiny_px)

        # Zustand
        self.vocab = lade_vokabeln()
        self.deck = list(range(len(self.vocab)))
        random.shuffle(self.deck)
        self.pos = 0
        self.thema = "hell"
        self.start_side = "fr"
        self.side = self.start_side
        self.flips = 0
        self.history = []            # bis zu HISTORY_MAX Wortpositionen
        self.scale = 1.0             # Flip-Animation
        self.animating = False
        self.hover = None
        self.auto_job = None
        self.countdown_frac = None
        self.was_active = True
        self.seen_focus = False      # hat die Plattform je Fokus gemeldet?
        self.update_version = None   # gefundene neuere Version
        self.update_status = None    # Text für den Hinweis auf der Karte
        self.update_fertig = None    # (art, ziel, neu) - bereit zum Tausch
        self._letzter_hinweis = (None, None)
        self.imgcache = {}
        self._wrapcache = {}

        self._drag = None
        self._resize = None
        self.cnv.bind("<ButtonPress-1>", self.on_press)
        self.cnv.bind("<B1-Motion>", self.on_move)
        self.cnv.bind("<ButtonRelease-1>", self.on_release)
        self.cnv.bind("<Motion>", self.on_hover)
        self.root.bind("<Configure>", self.on_configure)
        self.root.bind("<Key>", self.on_key)
        if IS_WIN:
            self._init_win_focus_poll()
        else:
            self.root.bind("<FocusIn>", self._on_focus_in)
            self.root.bind("<FocusOut>", lambda e: self.set_active(False))

        self.root.lift()
        self.draw()
        self._starte_hintergrund()
        self._ui_takt()
        self.root.mainloop()

    # ------------------------------------------------------------ Updates
    def _starte_hintergrund(self):
        """Netzarbeit läuft in Hintergrundfäden und darf nie etwas umwerfen -
        sie setzt nur Werte, gezeichnet wird im UI-Takt."""
        threading.Thread(target=self._pruefe_wortliste, daemon=True).start()
        if VERSION != "dev" or TESTMODUS:
            threading.Thread(target=self._pruefe_version, daemon=True).start()

    def _pruefe_wortliste(self):
        try:
            vokabeln_auffrischen()
        except Exception:
            pass

    def _pruefe_version(self):
        try:
            neu = neueste_version()
        except Exception:
            return
        if neu and neu != VERSION:
            self.update_version = neu

    def _ui_takt(self):
        """Einziger Ort, an dem Ergebnisse der Hintergrundfäden ins Bild
        kommen - Tk verträgt keine Zugriffe aus fremden Fäden."""
        if self.update_fertig:
            self._tauschen()
            return
        stand = (self.update_version, self.update_status)
        if stand != self._letzter_hinweis:
            self._letzter_hinweis = stand
            self.draw()
        self.root.after(500, self._ui_takt)

    def update_starten(self):
        if not self.update_version or self.update_status:
            return
        self.update_status = "lädt"
        threading.Thread(target=self._update_laden, daemon=True).start()

    def _update_laden(self):
        try:
            art, ziel = installation()
            arbeitsordner = tempfile.mkdtemp(prefix="voci-update-")
            neu = update_vorbereiten(art, ziel, arbeitsordner)
            self.update_fertig = (art, ziel, neu)
        except Exception:
            self.update_status = "fehlgeschlagen"

    def _tauschen(self):
        art, ziel, neu = self.update_fertig
        self.update_fertig = None
        try:
            tausch_starten(ziel, neu, startbefehl_fuer(art, ziel))
        except Exception:
            self.update_status = "fehlgeschlagen"
            self.root.after(500, self._ui_takt)
            return
        self.root.destroy()

    # ------------------------------------------------------------ Plattform
    def _setup_transparency(self):
        """Runde Ecken: Windows blendet eine Schlüsselfarbe aus, macOS kann das
        Fenster selbst transparent zeichnen, sonst bleibt ein grauer Rahmen."""
        self.keyed = False
        if IS_WIN:
            try:
                self.root.attributes("-transparentcolor", KEY)
                self.keyed = True
                return KEY
            except tk.TclError:
                return FALLBACK_VOID
        if IS_MAC:
            try:
                self.root.attributes("-transparent", True)
                self.root.configure(bg="systemTransparent")
                return "systemTransparent"
            except tk.TclError:
                return FALLBACK_VOID
        return FALLBACK_VOID

    def _pick_font(self):
        vorhanden = set(tkfont.families(self.root))
        for name in FONT_WUNSCH:
            if name in vorhanden:
                return name
        return tkfont.nametofont("TkDefaultFont").actual("family")

    def _init_win_focus_poll(self):
        self._u32 = ctypes.windll.user32
        self.root.update_idletasks()
        self._hwnds = set()
        try:
            child = self.root.winfo_id()
            self._hwnds.add(child)
            self._hwnds.add(self._u32.GetParent(child))
        except Exception:
            pass
        self._poll_focus()

    def _poll_focus(self):
        try:
            self.set_active(self._u32.GetForegroundWindow() in self._hwnds)
        except Exception:
            pass
        self.root.after(POLL_MS, self._poll_focus)

    def _on_focus_in(self, _event):
        self.seen_focus = True
        self.set_active(True)

    def set_active(self, active):
        if active and not self.was_active:
            self.cancel_auto()
        elif not active and self.was_active and self.flips >= FLIPS_NEEDED:
            # Ohne verlässliche Fokusmeldungen lieber gar nicht automatisch
            # weiterspringen, als ständig ungefragt weiterzuspringen.
            if IS_WIN or self.seen_focus:
                self.start_auto()
        self.was_active = active

    # ------------------------------------------------------------ Auto-Weiter
    def start_auto(self):
        self.cancel_auto(redraw=False)
        self._auto_left = AUTO_DELAY_MS
        self._tick_auto()

    def _tick_auto(self):
        if self._auto_left <= 0:
            self.auto_job = None
            self.countdown_frac = None
            self.next_word()
            return
        self.countdown_frac = self._auto_left / AUTO_DELAY_MS
        self.draw()
        self._auto_left -= 100
        self.auto_job = self.root.after(100, self._tick_auto)

    def cancel_auto(self, redraw=True):
        if self.auto_job is not None:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        self.countdown_frac = None
        if redraw:
            self.draw()

    # ------------------------------------------------------------ Wortlogik
    @property
    def word(self):
        return self.vocab[self.deck[self.pos]]

    def remember(self):
        """Wort merken – nur Wortwechsel landen in der Historie, Flips und der
        Sprachumschalter nicht."""
        self.history.append(self.pos)
        if len(self.history) > HISTORY_MAX:
            self.history.pop(0)

    def next_word(self):
        if self.animating:
            return
        self.cancel_auto(redraw=False)
        self.remember()

        def commit():
            self.pos = (self.pos + 1) % len(self.deck)
            self.flips = 0
            self.side = self.start_side
        self.animate(commit)

    def go_back(self):
        """Ein Wort zurück, in der gerade sichtbaren Sprache: steht man auf DE,
        kommt auch das vorherige Wort auf DE."""
        if not self.history or self.animating:
            return
        self.cancel_auto(redraw=False)
        pos = self.history.pop()

        def commit():
            self.pos = pos
            self.flips = 0
        self.animate(commit)

    def flip(self):
        if self.animating:
            return
        self.cancel_auto(redraw=False)

        def commit():
            self.side = "de" if self.side == "fr" else "fr"
            self.flips += 1
        self.animate(commit)

    def toggle_start(self):
        if self.animating:
            return
        self.start_side = "de" if self.start_side == "fr" else "fr"
        if self.flips == 0 and self.side != self.start_side:

            def commit():
                self.side = self.start_side
            self.animate(commit)
        else:
            self.draw()

    # ------------------------------------------------------------ Animation
    def animate(self, commit):
        if self.animating:
            return
        self.animating = True
        steps = 7

        def shrink(i=0):
            if i <= steps:
                self.scale = math.cos(i / steps * math.pi / 2)
                self.draw()
                self.root.after(14, lambda: shrink(i + 1))
            else:
                commit()
                grow()

        def grow(i=0):
            if i <= steps:
                self.scale = math.sin(i / steps * math.pi / 2)
                self.draw()
                self.root.after(14, lambda: grow(i + 1))
            else:
                self.scale = 1.0
                self.animating = False
                self.draw()
        shrink()

    # ------------------------------------------------------------ Darstellung
    def farbe(self, name):
        return THEMEN[self.thema][name]

    def toggle_thema(self):
        """Hell/dunkel wechseln - die Knopfbilder sind pro Palette gerendert
        und muessen deshalb neu erzeugt werden."""
        self.thema = "dunkel" if self.thema == "hell" else "hell"
        self.imgcache.clear()
        self.draw()

    def on_key(self, event):
        taste = event.keysym.lower()
        if taste == "d":
            self.toggle_thema()
        elif taste == "u":
            self.update_starten()

    # ------------------------------------------------------------ Layout
    def buttons(self):
        p, r = self.pad, self.br
        return (("lang", p, p, r),
                ("close", self.w - p, p, r),
                ("back", p, self.h - p, r),
                ("next", self.w - p, self.h - p, r))

    def button_image(self, tag, hot):
        key = (tag, hot, self.br, self.thema)
        img = self.imgcache.get(key)
        if img is None:
            size = self.br * 2 + 4
            img = render_button(size, self.br,
                                self.farbe("hover") if hot else self.farbe("bg"),
                                icon_segs(tag, self.br),
                                max(1.5, 1.7 * self.k),
                                self.farbe("fg"), self.farbe("bg"))
            self.imgcache[key] = img
        return img

    # ------------------------------------------------------------ Zeichnen
    def draw(self):
        c, w, h = self.cnv, self.w, self.h
        c.delete("all")
        cx = w / 2.0
        half = max(2.0, (w / 2.0 - 3) * max(self.scale, 0.02))

        rounded_rect(c, cx - half, 3, cx + half, h - 3, self.corner,
                     fill=hexc(self.farbe("bg")),
                     outline=self.farbe("rand"), width=1)

        if self.scale <= 0.12:
            return

        def sx(x):                       # x-Position mitflippen lassen
            return cx + (x - cx) * self.scale

        # Der Text staucht mit der Karte mit; die Zeilen stehen dabei fest.
        lines, full = self.wrapped(self.word[self.side])
        self.font_word.configure(size=-max(1, int(round(full * self.scale))))
        c.create_text(cx, h / 2.0, text=lines, font=self.font_word,
                      fill=hexc(self.farbe("fg")), justify="center")

        rest = self.scale > 0.999
        for tag, bx, by, r in self.buttons():
            if tag == "back" and not self.history:
                continue
            x = sx(bx)
            if rest:
                c.create_image(x, by, image=self.button_image(tag, self.hover == tag))
            else:
                if self.hover == tag:
                    c.create_oval(x - r * self.scale, by - r, x + r * self.scale, by + r,
                                  fill=hexc(self.farbe("hover")), width=0)
                lw = max(1.5, 1.7 * self.k)
                for (x1, y1, x2, y2) in icon_segs(tag, r):
                    c.create_line(x + x1 * self.scale, by + y1,
                                  x + x2 * self.scale, by + y2,
                                  fill=hexc(self.farbe("fg")), width=lw,
                                  capstyle="round")
            if tag == "lang":
                self.font_tiny.configure(
                    size=-max(1, int(round(self.tiny_px * self.scale))))
                c.create_text(x, by, text=self.start_side.upper(),
                              font=self.font_tiny, fill=hexc(self.farbe("fg")))

        hinweis = self.update_hinweis()
        if hinweis and rest and not self.countdown_frac:
            self.font_tiny.configure(size=-self.tiny_px)
            c.create_text(cx, h - 14 * self.k, text=hinweis,
                          font=self.font_tiny, fill=self.farbe("rand"))

        if self.countdown_frac and rest:
            bw = (w - 2 * (self.pad + self.br + 12 * self.k)) * self.countdown_frac
            if bw > 0:
                y = h - 11 * self.k
                c.create_rectangle(cx - bw / 2, y, cx + bw / 2, y + 3 * self.k,
                                   fill=self.farbe("timer"), width=0)

    def wrapped(self, text):
        """Zeilenumbruch einmal bei voller Kartenbreite bestimmen und merken.
        Während des Flips bleiben die Zeilen dann stehen – es skaliert nur die
        Schrift, statt dass der Text bei jedem Frame neu umbricht."""
        size = self.word_size(text)
        width = max(40, self.w - 78 * self.k)
        key = (text, size, int(width))
        cached = self._wrapcache.get(key)
        if cached is not None:
            return cached, size
        self.font_word.configure(size=-size)
        measure = self.font_word.measure
        lines, cur = [], ""
        for token in text.split(" "):
            for part in self._split_long(token, width, measure):
                probe = part if not cur else cur + " " + part
                if cur and measure(probe) > width:
                    lines.append(cur)
                    cur = part
                else:
                    cur = probe
        if cur:
            lines.append(cur)
        out = "\n".join(lines)
        self._wrapcache[key] = out
        return out, size

    @staticmethod
    def _split_long(token, width, measure):
        """Überlange Einzelwörter zerlegen – erst am Bindestrich, sonst hart."""
        if measure(token) <= width:
            return [token]
        parts, cur = [], ""
        for piece in token.replace("-", "-\x00").split("\x00"):
            if cur and measure(cur + piece) > width:
                parts.append(cur)
                cur = piece
            else:
                cur += piece
        if cur:
            parts.append(cur)
        out = []
        for part in parts:
            while measure(part) > width and len(part) > 1:
                n = len(part)
                while n > 1 and measure(part[:n]) > width:
                    n -= 1
                out.append(part[:n])
                part = part[n:]
            if part:
                out.append(part)
        return out

    def update_hinweis(self):
        if self.update_status == "lädt":
            return "Update wird geladen …"
        if self.update_status == "fehlgeschlagen":
            return "Update fehlgeschlagen"
        if self.update_version:
            return "Update verfügbar · Taste u"
        return None

    def word_size(self, text):
        """Schriftgrösse in Pixeln – plattformunabhängig, weil negative
        Tk-Grössen Pixel statt Punkte bedeuten."""
        base = min(self.w / 19.0, self.h / 11.5)
        n = len(text)
        if n > 70:
            base *= 0.60
        elif n > 45:
            base *= 0.74
        elif n > 28:
            base *= 0.87
        return max(8, int(base))

    # ------------------------------------------------------------ Maus
    def hit_button(self, x, y):
        for tag, bx, by, r in self.buttons():
            if tag == "back" and not self.history:
                continue
            if (x - bx) ** 2 + (y - by) ** 2 <= (r + 2) ** 2:
                return tag
        return None

    def hit_edge(self, x, y):
        e = self.edge
        side = ""
        if y <= e:
            side += "n"
        elif y >= self.h - e:
            side += "s"
        if x <= e:
            side += "w"
        elif x >= self.w - e:
            side += "e"
        return side or None

    def set_cursor(self, name):
        try:
            self.cnv.configure(cursor=name)
        except tk.TclError:
            self.cnv.configure(cursor="")

    def on_hover(self, e):
        edge = self.hit_edge(e.x, e.y)
        tag = None if edge else self.hit_button(e.x, e.y)
        if edge:
            self.set_cursor(CURSOR_EDGE.get(edge, ""))
        else:
            self.set_cursor(CURSOR_HAND if tag else "")
        if tag != self.hover:
            self.hover = tag
            self.draw()

    def on_press(self, e):
        self.set_active(True)
        try:
            self.root.focus_force()      # sonst kommen keine Tastendruecke an
        except tk.TclError:
            pass
        edge = self.hit_edge(e.x, e.y)
        if edge:
            self._resize = (edge, e.x_root, e.y_root, self.root.winfo_x(),
                            self.root.winfo_y(), self.w, self.h)
            return
        self._drag = (e.x_root, e.y_root, self.root.winfo_x(),
                      self.root.winfo_y(), False)

    def on_move(self, e):
        if self._resize:
            edge, sx, sy, wx, wy, w0, h0 = self._resize
            dx, dy = e.x_root - sx, e.y_root - sy
            nw, nh, nx, ny = w0, h0, wx, wy
            if "e" in edge:
                nw = max(self.min_w, w0 + dx)
            if "s" in edge:
                nh = max(self.min_h, h0 + dy)
            if "w" in edge:
                nw = max(self.min_w, w0 - dx)
                nx = wx + (w0 - nw)
            if "n" in edge:
                nh = max(self.min_h, h0 - dy)
                ny = wy + (h0 - nh)
            self.root.geometry("%dx%d+%d+%d" % (nw, nh, nx, ny))
            return
        if not self._drag:
            return
        sx, sy, wx, wy, moved = self._drag
        dx, dy = e.x_root - sx, e.y_root - sy
        if moved or abs(dx) > 4 or abs(dy) > 4:
            self._drag = (sx, sy, wx, wy, True)
            self.root.geometry("+%d+%d" % (wx + dx, wy + dy))

    def on_release(self, e):
        drag, self._drag, self._resize = self._drag, None, None
        if drag and drag[4]:            # war ein Verschieben, kein Klick
            return
        if self.hit_edge(e.x, e.y):
            return
        hit = self.hit_button(e.x, e.y)
        if hit == "close":
            self.root.destroy()
        elif hit == "next":
            self.next_word()
        elif hit == "back":
            self.go_back()
        elif hit == "lang":
            self.toggle_start()
        else:
            self.flip()

    def on_configure(self, e):
        if e.widget is not self.root:
            return
        if (e.width, e.height) != (self.w, self.h):
            self.w, self.h = e.width, e.height
            self._wrapcache.clear()
            self.draw()


if __name__ == "__main__":
    Voci()
