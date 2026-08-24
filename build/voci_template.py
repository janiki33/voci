# -*- coding: utf-8 -*-
"""
Voci – Vokabel-Flashcard, immer im Vordergrund.

Bedienung:
  Klick auf die Karte      -> flippt FR <-> DE (beide Richtungen)
  Kreis unten rechts (>)   -> nächstes Wort
  Kreis unten links (FR/DE)-> Startsprache umschalten
  Kreis oben rechts (x)    -> beenden
  Karte ziehen             -> Fenster verschieben

Wenn das Fenster den Fokus verliert und das aktuelle Wort schon mehr als
einmal geflippt wurde, kommt nach 5 Sekunden automatisch das nächste Wort
(ein dünner Balken unten zählt runter) – ausser man kommt vorher zurück.
"""

import json
import math
import random
import sys
import tkinter as tk
import tkinter.font as tkfont

VOCAB = json.loads(r'''__VOCAB_JSON__''')

# ---------------------------------------------------------------- Konstanten
W, H = 360, 220          # Kartengrösse
RADIUS = 22              # Eckenradius
BG = "#ffffff"           # Karte
FG = "#111111"           # Text
GRAY = "#8a8a8a"         # Sekundärtext
LIGHT = "#e6e6e6"        # Knopf-Fläche
LIGHTER = "#f3f3f3"
BORDER = "#d0d0d0"
TRANSPARENT = "#00fe00"  # Farbschlüssel für runde Ecken (Windows)

AUTO_DELAY_MS = 5000     # 5 s bis zum Auto-Weiter
FLIPS_NEEDED = 2         # "mehr als 1 mal geflippt"
POLL_MS = 300            # Fokus-Polling (Windows)

IS_WIN = sys.platform.startswith("win")


def rounded_rect(cnv, x1, y1, x2, y2, r, **kw):
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
        x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return cnv.create_polygon(pts, smooth=True, **kw)


class Voci:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # kein Titel, kein Min/Max
        self.root.attributes("-topmost", True)    # immer im Vordergrund
        self.root.geometry(f"{W}x{H}+120+120")

        self.transparent_ok = False
        if IS_WIN:
            try:
                self.root.attributes("-transparentcolor", TRANSPARENT)
                self.transparent_ok = True
            except tk.TclError:
                pass
        canvas_bg = TRANSPARENT if self.transparent_ok else "#bfbfbf"

        self.cnv = tk.Canvas(self.root, width=W, height=H, bd=0,
                             highlightthickness=0, bg=canvas_bg)
        self.cnv.pack(fill="both", expand=True)

        self.font_big = tkfont.Font(family="Segoe UI", size=16)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_btn = tkfont.Font(family="Segoe UI", size=12)

        # Zustand
        self.deck = list(range(len(VOCAB)))
        random.shuffle(self.deck)
        self.pos = 0
        self.start_side = "fr"       # Startsprache, umschaltbar
        self.side = self.start_side  # aktuell sichtbare Seite
        self.flips = 0               # Flips beim aktuellen Wort
        self.scale = 1.0             # Flip-Animation (Breitenfaktor)
        self.animating = False
        self.hover = None            # "close" | "next" | "lang" | None

        self.auto_job = None         # after-Job für Auto-Weiter
        self.was_active = True

        # Maus / Drag
        self._drag = None
        self.cnv.bind("<ButtonPress-1>", self.on_press)
        self.cnv.bind("<B1-Motion>", self.on_move)
        self.cnv.bind("<ButtonRelease-1>", self.on_release)
        self.cnv.bind("<Motion>", self.on_hover)
        self.root.bind("<Enter>", lambda e: self.set_active(True))
        self.root.bind("<FocusIn>", lambda e: self.set_active(True))
        if not IS_WIN:
            self.root.bind("<FocusOut>", lambda e: self.set_active(False))

        if IS_WIN:
            self._init_win_focus_poll()

        self.draw()
        self.root.mainloop()

    # ------------------------------------------------------------ Windows-Fokus
    def _init_win_focus_poll(self):
        import ctypes
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
            fg = self._u32.GetForegroundWindow()
            self.set_active(fg in self._hwnds)
        except Exception:
            pass
        self.root.after(POLL_MS, self._poll_focus)

    def set_active(self, active):
        if active and not self.was_active:
            self.cancel_auto()
        elif not active and self.was_active:
            if self.flips >= FLIPS_NEEDED:
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

    countdown_frac = None

    # ------------------------------------------------------------ Wörter
    @property
    def word(self):
        return VOCAB[self.deck[self.pos]]

    def next_word(self):
        self.cancel_auto(redraw=False)
        self.pos += 1
        if self.pos >= len(self.deck):
            random.shuffle(self.deck)
            self.pos = 0
        self.flips = 0
        self.side = self.start_side
        self.flip_animation(new_side=self.side, count=False)

    def flip(self):
        new_side = "de" if self.side == "fr" else "fr"
        self.flip_animation(new_side=new_side, count=True)

    def toggle_start(self):
        self.start_side = "de" if self.start_side == "fr" else "fr"
        if self.side != self.start_side and self.flips == 0:
            self.flip_animation(new_side=self.start_side, count=False)
        else:
            self.draw()

    # ------------------------------------------------------------ Animation
    def flip_animation(self, new_side, count):
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
                self.side = new_side
                if count:
                    self.flips += 1
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

    # ------------------------------------------------------------ Zeichnen
    def draw(self):
        c = self.cnv
        c.delete("all")
        cx = W / 2
        half = max(2, (W / 2 - 4) * max(self.scale, 0.02))
        x1, x2 = cx - half, cx + half

        rounded_rect(c, x1 + 2, 3, x2 - 2, H - 3, RADIUS,
                     fill=BG, outline=BORDER, width=1)

        show_text = self.scale > 0.35
        if show_text:
            # Sprach-Hinweis oben links
            c.create_text(24, 20, text=self.side.upper(), anchor="w",
                          font=self.font_small, fill=GRAY)
            # Wort
            text = self.word[self.side]
            size = 16
            if len(text) > 60:
                size = 12
            elif len(text) > 34:
                size = 14
            self.font_big.configure(size=size)
            c.create_text(cx, H / 2 - 6, text=text, font=self.font_big,
                          fill=FG, width=(x2 - x1) - 56, justify="center")

            # X oben rechts (Kreis)
            self._circle_btn(W - 30, 22, 11, "close",
                             lambda c_, x, y: (
                                 c_.create_line(x - 4, y - 4, x + 4, y + 4, fill=FG, width=1.6),
                                 c_.create_line(x - 4, y + 4, x + 4, y - 4, fill=FG, width=1.6)))
            # Weiter unten rechts (Kreis mit Pfeil)
            self._circle_btn(W - 32, H - 30, 14, "next",
                             lambda c_, x, y: (
                                 c_.create_line(x - 4, y, x + 5, y, fill=FG, width=1.8),
                                 c_.create_line(x + 1, y - 4, x + 5, y, fill=FG, width=1.8),
                                 c_.create_line(x + 1, y + 4, x + 5, y, fill=FG, width=1.8)))
            # Startsprache unten links
            self._circle_btn(32, H - 30, 14, "lang",
                             lambda c_, x, y: c_.create_text(
                                 x, y, text=self.start_side.upper(),
                                 font=self.font_small, fill=FG))

            # Countdown-Balken
            if self.countdown_frac:
                bw = (W - 120) * self.countdown_frac
                c.create_rectangle(cx - bw / 2, H - 12, cx + bw / 2, H - 10,
                                   fill=GRAY, width=0)

    def _circle_btn(self, x, y, r, tag, icon):
        fill = LIGHT if self.hover == tag else LIGHTER
        self.cnv.create_oval(x - r, y - r, x + r, y + r,
                             fill=fill, outline=BORDER, width=1, tags=tag)
        icon(self.cnv, x, y)

    # ------------------------------------------------------------ Maus
    def _hit(self, x, y):
        for tag, bx, by, br in (("close", W - 30, 22, 13),
                                ("next", W - 32, H - 30, 16),
                                ("lang", 32, H - 30, 16)):
            if (x - bx) ** 2 + (y - by) ** 2 <= br ** 2:
                return tag
        return None

    def on_hover(self, e):
        h = self._hit(e.x, e.y)
        if h != self.hover:
            self.hover = h
            self.cnv.configure(cursor="hand2" if h else "arrow")
            self.draw()

    def on_press(self, e):
        self.set_active(True)
        self._drag = (e.x_root, e.y_root,
                      self.root.winfo_x(), self.root.winfo_y(), False)

    def on_move(self, e):
        if not self._drag:
            return
        sx, sy, wx, wy, moved = self._drag
        dx, dy = e.x_root - sx, e.y_root - sy
        if moved or abs(dx) > 4 or abs(dy) > 4:
            self._drag = (sx, sy, wx, wy, True)
            self.root.geometry(f"+{wx + dx}+{wy + dy}")

    def on_release(self, e):
        drag = self._drag
        self._drag = None
        if drag and drag[4]:        # war ein Drag, kein Klick
            return
        hit = self._hit(e.x, e.y)
        if hit == "close":
            self.root.destroy()
        elif hit == "next":
            self.next_word()
        elif hit == "lang":
            self.toggle_start()
        else:
            self.flip()


if __name__ == "__main__":
    Voci()
