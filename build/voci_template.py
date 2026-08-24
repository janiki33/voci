# -*- coding: utf-8 -*-
"""
Voci - Vokabel-Flashcard, immer im Vordergrund.

Bedienung:
  Klick auf die Karte        -> flippt FR <-> DE (beide Richtungen)
  Kreis oben links (FR/DE)   -> Startsprache umschalten
  Kreis oben rechts (x)      -> beenden
  Kreis unten links (<-)     -> ein Wort zurueck (max. 10)
  Kreis unten rechts (->)    -> naechstes Wort
  Karte ziehen               -> Fenster verschieben
  Rand ziehen                -> Fenster vergroessern/verkleinern

Wenn das Fenster den Fokus verliert und das aktuelle Wort schon mehr als
einmal geflippt wurde, kommt nach 5 Sekunden automatisch das naechste Wort
(ein feiner Balken unten zaehlt runter) - ausser man tabbt vorher zurueck.
"""

import json
import math
import random
import sys
import tkinter as tk
import tkinter.font as tkfont

VOCAB = json.loads(r'''__VOCAB_JSON__''')

IS_WIN = sys.platform.startswith("win")

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

# ---------------------------------------------------------------- Farben
BG = (255, 255, 255)          # Karte
FG = (17, 17, 17)             # Text / Icons
HOVER = (235, 235, 235)       # Knopf beim Hovern
BORDER = "#d8d8d8"            # Kartenrand
TIMER = "#ededed"             # Countdown-Balken (dezent)
KEY = "#00fe00"               # Farbschluessel fuer runde Ecken (Windows)

# ---------------------------------------------------------------- Verhalten
AUTO_DELAY_MS = 5000          # 5 s bis zum Auto-Weiter
FLIPS_NEEDED = 2              # "mehr als 1 mal geflippt"
HISTORY_MAX = 10              # max. 10 Schritte zurueck
POLL_MS = 250                 # Fokus-Polling (Windows)


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
    """Zeichnet Kreis + Linien-Icon kantengeglaettet (Distanzfeld-AA) in ein
    PhotoImage - Tk-Canvas-Formen selbst sind hart gepixelt."""
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


class Voci:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # kein Titel, kein Min/Max
        self.root.attributes("-topmost", True)    # immer im Vordergrund

        # Alles in echten Bildschirmpixeln rechnen (DPI-Faktor).
        dpi = self.root.winfo_fpixels("1i")
        self.k = max(1.0, dpi / 96.0)
        self.root.tk.call("tk", "scaling", dpi / 72.0)

        self.w = int(380 * self.k)
        self.h = int(230 * self.k)
        self.min_w = int(260 * self.k)
        self.min_h = int(150 * self.k)
        self.pad = int(30 * self.k)               # Knopf-Abstand zur Ecke
        self.br = int(15 * self.k)                # Knopfradius
        self.edge = max(5, int(6 * self.k))       # Greifzone am Rand
        self.corner = int(20 * self.k)            # Eckenradius der Karte
        self.root.geometry("%dx%d+%d+%d" % (self.w, self.h, 140, 140))

        self.keyed = False
        if IS_WIN:
            try:
                self.root.attributes("-transparentcolor", KEY)
                self.keyed = True
            except tk.TclError:
                pass
        self.void = KEY if self.keyed else "#bdbdbd"

        self.cnv = tk.Canvas(self.root, bd=0, highlightthickness=0, bg=self.void)
        self.cnv.pack(fill="both", expand=True)

        self.font_word = tkfont.Font(family="Segoe UI", size=15)
        self.tiny_size = 8
        self.font_tiny = tkfont.Font(family="Segoe UI", size=self.tiny_size)

        # Zustand
        self.deck = list(range(len(VOCAB)))
        random.shuffle(self.deck)
        self.pos = 0
        self.start_side = "fr"
        self.side = self.start_side
        self.flips = 0
        self.history = []            # bis zu HISTORY_MAX Zustaende
        self.scale = 1.0             # Flip-Animation
        self.animating = False
        self.hover = None
        self.auto_job = None
        self.countdown_frac = None
        self.was_active = True
        self.imgcache = {}

        self._drag = None
        self._resize = None
        self.cnv.bind("<ButtonPress-1>", self.on_press)
        self.cnv.bind("<B1-Motion>", self.on_move)
        self.cnv.bind("<ButtonRelease-1>", self.on_release)
        self.cnv.bind("<Motion>", self.on_hover)
        self.root.bind("<Configure>", self.on_configure)
        if IS_WIN:
            self._init_win_focus_poll()
        else:
            self.root.bind("<FocusIn>", lambda e: self.set_active(True))
            self.root.bind("<FocusOut>", lambda e: self.set_active(False))

        self.draw()
        self.root.mainloop()

    # ------------------------------------------------------------ Fokus
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

    def set_active(self, active):
        if active and not self.was_active:
            self.cancel_auto()
        elif not active and self.was_active and self.flips >= FLIPS_NEEDED:
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
        return VOCAB[self.deck[self.pos]]

    def remember(self):
        """Wort-Zustand merken - nur Wortwechsel landen in der Historie,
        Flips und der Sprachumschalter nicht."""
        self.history.append((self.pos, self.side, self.flips))
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
        """Ein Wort zurueck - genau so, wie es verlassen wurde (gleiche Seite,
        auch wenn die Startsprache inzwischen umgestellt wurde)."""
        if not self.history or self.animating:
            return
        self.cancel_auto(redraw=False)
        pos, side, flips = self.history.pop()

        def commit():
            self.pos, self.side, self.flips = pos, side, flips
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

    # ------------------------------------------------------------ Layout
    def buttons(self):
        p, r = self.pad, self.br
        return (("lang", p, p, r),
                ("close", self.w - p, p, r),
                ("back", p, self.h - p, r),
                ("next", self.w - p, self.h - p, r))

    def button_image(self, tag, hot):
        key = (tag, hot, self.br)
        img = self.imgcache.get(key)
        if img is None:
            size = self.br * 2 + 4
            img = render_button(size, self.br,
                                HOVER if hot else BG,
                                icon_segs(tag, self.br),
                                max(1.5, 1.7 * self.k), FG, BG)
            self.imgcache[key] = img
        return img

    # ------------------------------------------------------------ Zeichnen
    def draw(self):
        c, w, h = self.cnv, self.w, self.h
        c.delete("all")
        cx = w / 2.0
        half = max(2.0, (w / 2.0 - 3) * max(self.scale, 0.02))

        rounded_rect(c, cx - half, 3, cx + half, h - 3, self.corner,
                     fill=hexc(BG), outline=BORDER, width=1)

        if self.scale <= 0.12:
            return

        def sx(x):                       # x-Position mitflippen lassen
            return cx + (x - cx) * self.scale

        # Der Text staucht mit der Karte mit und bricht dabei neu um.
        text = self.word[self.side]
        self.font_word.configure(
            size=max(1, int(round(self.word_size(text) * self.scale))))
        c.create_text(cx, h / 2.0, text=text, font=self.font_word, fill=hexc(FG),
                      width=max(20, (2 * half) - 70 * self.k * self.scale),
                      justify="center")

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
                                  fill=hexc(HOVER), width=0)
                lw = max(1.5, 1.7 * self.k)
                for (x1, y1, x2, y2) in icon_segs(tag, r):
                    c.create_line(x + x1 * self.scale, by + y1,
                                  x + x2 * self.scale, by + y2,
                                  fill=hexc(FG), width=lw, capstyle="round")
            if tag == "lang":
                self.font_tiny.configure(
                    size=max(1, int(round(self.tiny_size * self.scale))))
                c.create_text(x, by, text=self.start_side.upper(),
                              font=self.font_tiny, fill=hexc(FG))

        if self.countdown_frac and rest:
            bw = (w - 2 * (self.pad + self.br + 12 * self.k)) * self.countdown_frac
            if bw > 0:
                y = h - 11 * self.k
                c.create_rectangle(cx - bw / 2, y, cx + bw / 2, y + 3 * self.k,
                                   fill=TIMER, width=0)

    def word_size(self, text):
        base = min(self.w / 24.0, self.h / 14.0) / self.k
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
            self.set_cursor({"n": "sb_v_double_arrow", "s": "sb_v_double_arrow",
                             "w": "sb_h_double_arrow", "e": "sb_h_double_arrow",
                             "nw": "top_left_corner", "ne": "top_right_corner",
                             "sw": "bottom_left_corner",
                             "se": "bottom_right_corner"}.get(edge, ""))
        else:
            self.set_cursor("hand2" if tag else "")
        if tag != self.hover:
            self.hover = tag
            self.draw()

    def on_press(self, e):
        self.set_active(True)
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
            self.draw()


if __name__ == "__main__":
    Voci()
