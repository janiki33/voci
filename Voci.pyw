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

VOCAB = json.loads(r'''[{"fr": "Se présenter", "de": "sich jemandem vorstellen"}, {"fr": "la présentation", "de": "die Vorstellung von etwas oder jemandem"}, {"fr": "caractériser", "de": "charakterisieren"}, {"fr": "le caractère", "de": "der Charakter"}, {"fr": "enchanté/enchantée (adj.)", "de": "Sehr erfreut!"}, {"fr": "une adresse", "de": "eine Adresse"}, {"fr": "s’adresser à", "de": "sich wenden/richten an"}, {"fr": "mémoriser", "de": "sich einprägen/sich merken"}, {"fr": "la mémoire", "de": "das Gedächtnis/die Erinnerung"}, {"fr": "la date de naissance", "de": "das Geburtsdatum"}, {"fr": "la naissance", "de": "die Geburt"}, {"fr": "naître", "de": "geboren werden"}, {"fr": "Je suis né/née le 15 août 1994", "de": "Ich bin am 15. August 1994 geboren"}, {"fr": "le mois/les mois", "de": "der Monat/die Monate"}, {"fr": "janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre, décembre", "de": "Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"}, {"fr": "en janvier, en août, en juin", "de": "im Januar, im August, im Juni"}, {"fr": "les jours (le jour) de la semaine :", "de": "die Tage der Woche:"}, {"fr": "lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche", "de": "Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag"}, {"fr": "le lundi, le samedi, le dimanche", "de": "am/immer am Montag, am Samstag, am Sonntag"}, {"fr": "à ce soir – à demain – à samedi", "de": "bis heute Abend - bis morgen – bis am Samstag"}, {"fr": "le matin – ce matin", "de": "der/am Morgen – heute Morgen"}, {"fr": "l’après-midi, (m.) – cet après-midi", "de": "der/am Nachmittag – heute Nachmittag"}, {"fr": "le soir – ce soir", "de": "der/am Abend – heute Abend"}, {"fr": "les quatre saisons, (f.):", "de": "die 4 Jahreszeiten:"}, {"fr": "l’été (m.), l’automne(m.), l’hiver (m.), le printemps", "de": "der Sommer, der Herbst, der Winter, der Frühling"}, {"fr": "en été, en automne, en hiver, au printemps", "de": "im Sommer, im Herbst, im Winter, im Frühling"}, {"fr": "un état civil", "de": "ein Zivilstand"}, {"fr": "marié/mariée (adj.)", "de": "verheiratet"}, {"fr": "célibataire (adj.)", "de": "ledig"}, {"fr": "divorcé/divorcée (adj.)", "de": "geschieden"}, {"fr": "veuf/veuve (adj.)", "de": "verwitwet"}, {"fr": "la langue maternelle", "de": "die Muttersprache"}, {"fr": "la langue étrangère", "de": "die Fremdsprache"}, {"fr": "apprendre une langue", "de": "eine Sprache lernen"}, {"fr": "un enregistrement", "de": "eine (Radio-/Musik...)-Aufnahme"}, {"fr": "enregistrer", "de": "(Musik,…) aufnehmen"}, {"fr": "une émission", "de": "eine Fernsehsendung"}, {"fr": "regarder la télévision", "de": "fernsehen"}, {"fr": "écouter la radio", "de": "Radio hören"}, {"fr": "être d’origine italienne/suisse/allemande", "de": "ital./schweiz./deutscher Herkunft sein"}, {"fr": "traduire : je traduis", "de": "übersetzen: ich übersetze"}, {"fr": "la traduction", "de": "die Uebersetzung"}, {"fr": "le portable", "de": "das Handy"}, {"fr": "téléphoner à quelqu’un - appeler quelqu‘un", "de": "jemandem telefonieren/jem. anrufen"}, {"fr": "se décider", "de": "sich entscheiden"}, {"fr": "la décision", "de": "die Entscheidung"}, {"fr": "se reposer", "de": "sich ausruhen, sich erholen"}, {"fr": "s’inscrire", "de": "sich einschreiben"}, {"fr": "répondre", "de": "antworten"}, {"fr": "la réponse", "de": "die Antwort"}, {"fr": "cocher la réponse correcte", "de": "die richtige Antwort ankreuzen"}, {"fr": "faire des études (f.)", "de": "ein Studium machen"}, {"fr": "aller en boîte", "de": "in die Disco gehen"}, {"fr": "choisir", "de": "auswählen"}, {"fr": "le choix", "de": "(die Aus)-Wahl"}, {"fr": "le numéro de portable", "de": "die Handynummer"}, {"fr": "demander quelque chose à quelqu’un", "de": "jemanden um etwas bitten"}, {"fr": "participer à", "de": "teilnehmen an"}, {"fr": "la participation", "de": "die Teilnahme"}, {"fr": "poser une question", "de": "eine Frage stellen"}, {"fr": "s‘amuser", "de": "sich amüsieren"}, {"fr": "se coucher, aller au lit", "de": "ins Bett gehen"}, {"fr": "se dépêcher", "de": "sich beeilen"}, {"fr": "se doucher", "de": "sich duschen"}, {"fr": "s’ énerver", "de": "sich aufregen"}, {"fr": "s ’habiller", "de": "sich anziehen"}, {"fr": "se maquiller", "de": "sich schminken"}, {"fr": "s’occuper de", "de": "sich beschäftigen mit, sich kümmern um"}, {"fr": "se réveiller", "de": "aufwachen"}, {"fr": "à mon avis/selon moi", "de": "meiner Meinung nach"}, {"fr": "par contre", "de": "hingegen"}, {"fr": "avoir raison", "de": "Recht haben"}, {"fr": "avoir tort", "de": "unrecht haben"}, {"fr": "exagérer", "de": "übertreiben"}, {"fr": "trouver", "de": "finden"}, {"fr": "un emploi", "de": "eine (Arbeits-)Stelle"}, {"fr": "une erreur/une faute", "de": "ein Fehler"}, {"fr": "un projet d’avenir", "de": "ein Zukunftsplan/ein Projekt für die Zukunft"}, {"fr": "rendre visite à quelqu’un", "de": "jemanden besuchen"}, {"fr": "visiter un musée/une ville", "de": "ein Museum/eine Stadt besichtigen"}, {"fr": "fréquenter/faire l’école de Maturité Professionnelle", "de": "die BMS besuchen"}, {"fr": "la maturité professionnelle", "de": "die BM/Berufsmatura"}, {"fr": "le groupe", "de": "die Gruppe"}, {"fr": "parler anglais-espagnol-français-italien-japonais-polonais-russe-turc-allemand", "de": "englisch-spanisch-französisch-italienisch-japanisch-polnisch-russisch-türkisch-deutsch sprechen"}, {"fr": "avoir besoin de (j’ai besoin d’une langue étrangère)", "de": "brauchen (ich brauche eine Fremdsprache)"}, {"fr": "savoir parler français", "de": "französisch sprechen können"}, {"fr": "savoir", "de": "wissen, können (weil gelernt!)"}, {"fr": "connaître", "de": "kennen, kennenlernen"}, {"fr": "pouvoir", "de": "können, dürfen"}, {"fr": "l’Angleterre (f.)", "de": "England"}, {"fr": "un Anglais/une Anglaise", "de": "ein Engländer/eine Engländerin"}, {"fr": "anglais,e (adj.)", "de": "englisch"}, {"fr": "l‘ Espagne (f.)", "de": "Spanien"}, {"fr": "un Espagnol/une Espagnole", "de": "ein Spanier/eine Spanierin"}, {"fr": "espagnol,e (adj.)", "de": "spanisch"}, {"fr": "la France", "de": "Frankreich"}, {"fr": "un Français/une Française", "de": "ein Franzose/eine Französin"}, {"fr": "français,e (adj.)", "de": "französisch"}, {"fr": "l’Italie (f.)", "de": "Italien"}, {"fr": "un Italien/une Italienne", "de": "ein Italiener/eine Italienerin"}, {"fr": "italien/italienne (adj.)", "de": "italienisch"}, {"fr": "le Japon", "de": "Japan"}, {"fr": "un Japonais/une Japonaise", "de": "ein Japaner/eine Japanerin"}, {"fr": "japonais,e (adj.)", "de": "japanisch"}, {"fr": "la Russie", "de": "Russland"}, {"fr": "un Russe/une Russe", "de": "ein Russe/eine Russin"}, {"fr": "russe m,f (adj.)", "de": "russisch"}, {"fr": "l’Allemagne (f.)", "de": "Deutschland"}, {"fr": "un Allemand/une Allemande", "de": "ein Deutscher/eine Deutsche"}, {"fr": "allemand,e (adj.)", "de": "deutsch"}, {"fr": "la Croatie", "de": "Kroatien"}, {"fr": "croate (adj.)", "de": "kroatisch"}, {"fr": "la Serbie", "de": "Serbien"}, {"fr": "serbe (adj.)", "de": "serbisch"}, {"fr": "maîtriser quelque chose", "de": "etwas beherrschen"}, {"fr": "maîtriser une langue/une situation", "de": "eine Sprache/eine Situation beherrschen"}, {"fr": "utiliser qc comme", "de": "etwas benutzen als"}, {"fr": "apprendre qc", "de": "etw. lernen"}, {"fr": "apprendre à faire qc", "de": "lernen etw. zu machen"}, {"fr": "un apprentissage", "de": "eine Lehre/ein Lernen"}, {"fr": "un apprenti/une apprentie", "de": "ein Lehrling, ein Lernender/eine Lernende"}, {"fr": "améliorer qc", "de": "etw. verbessern"}, {"fr": "améliorer la prononciation", "de": "die Aussprache verbessern"}, {"fr": "accompagner", "de": "begleiten"}, {"fr": "être utile m,f (adj.)", "de": "nützlich sein"}, {"fr": "riche m,f (adj.)", "de": "reich"}, {"fr": "la richesse", "de": "der Reichtum"}, {"fr": "construire une phrase/une maison", "de": "einen Satz bilden, ein Haus bauen"}, {"fr": "disponible m,f (adj.)", "de": "verfügbar"}, {"fr": "partout", "de": "überall"}, {"fr": "nulle part", "de": "nirgends, nirgendwo"}, {"fr": "accéder à", "de": "Zugang erlangen"}, {"fr": "un accès (à l’internet)", "de": "ein (Internet-)Zugang"}, {"fr": "apprendre par coeur", "de": "auswendig lernen"}, {"fr": "un oeil-les yeux (pl.m)", "de": "ein Auge-die Augen"}, {"fr": "la vue", "de": "der Blick/das Sehen"}, {"fr": "voir", "de": "sehen"}, {"fr": "regarder", "de": "anschauen/schauen"}, {"fr": "le son", "de": "der Ton/Klang"}, {"fr": "sonner", "de": "tönen/läuten/klingeln"}, {"fr": "une oreille", "de": "ein Ohr"}, {"fr": "écouter", "de": "(zu-)hören"}, {"fr": "entendre", "de": "hören"}, {"fr": "une odeur", "de": "ein Geruch"}, {"fr": "un goût", "de": "ein Geschmack"}, {"fr": "ensemble", "de": "gemeinsam"}, {"fr": "parfois/de temps en temps", "de": "bisweilen/ hie und da,/ ab und zu"}, {"fr": "entier/entière (adj.)", "de": "ganz, gesamt"}, {"fr": "le lait entier", "de": "die Vollmilch"}, {"fr": "le monde entier", "de": "die ganze Welt"}, {"fr": "tout le monde (3. pers.sg.!)", "de": "jedermann; alle"}, {"fr": "quand, comment, où, pourquoi, combien, quel(s) quelle(s)", "de": "wann, wie, wo, warum, wieviel, welche"}, {"fr": "les aliments (m. pl.)", "de": "die Nahrungsmittel"}, {"fr": "le légume", "de": "das Gemüse"}, {"fr": "l’épinard (m.)", "de": "der Spinat"}, {"fr": "l’ail (m.)", "de": "der Knoblauch"}, {"fr": "la courgette", "de": "die Zucchetti"}, {"fr": "une asperge", "de": "eine Spargel"}, {"fr": "le chou", "de": "der Kohl"}, {"fr": "la pomme de terre", "de": "die Kartoffel"}, {"fr": "la tomate", "de": "die Tomate"}, {"fr": "la carotte", "de": "die Karotte"}, {"fr": "le champignon", "de": "der Pilz"}, {"fr": "l’oignon (m.)", "de": "die Zwiebel"}, {"fr": "le produit laitier", "de": "das Milchprodukt"}, {"fr": "le beurre", "de": "die Butter"}, {"fr": "la crème", "de": "der Rahm"}, {"fr": "le yaourt", "de": "das Joghurt"}, {"fr": "le fromage (la fondue, la raclette)", "de": "der Käse (das Fondue, das Raclette)"}, {"fr": "les fruits (m.pl.)", "de": "die Früchte"}, {"fr": "la fraise", "de": "die Erdbeere"}, {"fr": "la framboise", "de": "die Himbeere"}, {"fr": "la pomme", "de": "der Apfel"}, {"fr": "la poire", "de": "die Birne"}, {"fr": "le raisin", "de": "die Traube"}, {"fr": "l’abricot (m.)", "de": "die Aprikose"}, {"fr": "une orange", "de": "eine Orange"}, {"fr": "un citron", "de": "die Zitrone"}, {"fr": "un melon", "de": "eine Melone"}, {"fr": "une banane", "de": "eine Banane"}, {"fr": "un ananas", "de": "eine Ananas"}, {"fr": "une prune", "de": "eine Zwetschge"}, {"fr": "le pain", "de": "das Brot"}, {"fr": "le croissant", "de": "das Gipfeli"}, {"fr": "la baguette", "de": "das Stangenbrot, das Baguette"}, {"fr": "une tartine (de miel)", "de": "ein Brot mit Aufstrich (Honigbrot)"}, {"fr": "le muesli", "de": "das Müsli"}, {"fr": "cru, crue (adj.)", "de": "roh"}, {"fr": "cuit,e (adj.)", "de": "gekocht"}, {"fr": "le miel", "de": "der Honig"}, {"fr": "un œuf", "de": "ein Ei"}, {"fr": "la viande (la viande séchée)", "de": "das Fleisch (das Trockenfleisch)"}, {"fr": "la confiture", "de": "die Marmelade, die Konfitüre"}, {"fr": "le petit déjeuner, le déjeuner, le dîner", "de": "das Frühstück, das Mittagessen, das Abendessen"}, {"fr": "un repas", "de": "das Essen, die Mahlzeit"}, {"fr": "une boisson", "de": "ein Getränk"}, {"fr": "le plat (le plat préféré)", "de": "das Gericht (das Lieblingsessen)"}, {"fr": "un escargot", "de": "eine Schnecke"}, {"fr": "le saumon", "de": "der Lachs"}, {"fr": "le poireau", "de": "der Lauch"}, {"fr": "un filet de bœuf", "de": "ein Rinderfilet"}, {"fr": "faire un barbecue / une grillade", "de": "grillen"}, {"fr": "une épice, épicer", "de": "ein Gewürz, würzen"}, {"fr": "pimenté,e (adj.)", "de": "pikant, scharf (kulinarisch)"}, {"fr": "la volaille", "de": "das Geflügel"}, {"fr": "le poisson", "de": "der Fisch"}, {"fr": "le veau", "de": "das Kalb"}, {"fr": "la tarte", "de": "flacher Obstkuchen"}, {"fr": "le gâteau", "de": "der Kuchen"}, {"fr": "une carafe (d’eau)", "de": "eine Karaffe (Wasser)"}, {"fr": "oublier", "de": "vergessen"}, {"fr": "s’intéresser à", "de": "sich interessieren für"}, {"fr": "je m’intéresse aux langues", "de": "ich interessiere mich für Sprachen"}, {"fr": "bon/bonne (adj.)", "de": "gut, gütig"}, {"fr": "gentil/gentille (adj.)", "de": "nett, freundlich"}, {"fr": "méchant/méchante (adj.)", "de": "böse, gemein, boshaft"}, {"fr": "aimable (adj.)", "de": "liebenswürdig, freundlich"}, {"fr": "cher/chère (adj.)", "de": "lieb, teuer"}, {"fr": "être fier/fière de", "de": "stolz sein auf"}, {"fr": "paresseux/paresseuse (adj.)", "de": "faul"}, {"fr": "patient,e(adj.)", "de": "geduldig"}, {"fr": "impatient,e (adj.)", "de": "ungeduldig"}, {"fr": "la patience", "de": "die Geduld"}, {"fr": "prudent,e (adj.)", "de": "vorsichtig"}, {"fr": "adroit,e (adj.)", "de": "geschickt"}, {"fr": "aimer", "de": "lieben, mögen, gerne tun"}, {"fr": "il aime danser", "de": "er tanzt gerne"}, {"fr": "l’amour m.", "de": "die Liebe"}, {"fr": "être content/contente de", "de": "zufrieden sein mit"}, {"fr": "heureux/heureuse (adj.)", "de": "glücklich"}, {"fr": "malheureux-malheureuse (adj.", "de": "unglücklich"}, {"fr": "la joie", "de": "die Freude, das Vergnügen"}, {"fr": "le plaisir", "de": "das Vergnügen, die Freude"}, {"fr": "agréable m,f (adj.)", "de": "angenehm"}, {"fr": "désagréable m,f (adj.)", "de": "unangenehm"}, {"fr": "avoir envie de", "de": "Lust haben auf"}, {"fr": "l’espoir (m.)", "de": "die Hoffnung"}, {"fr": "espérer", "de": "hoffen"}, {"fr": "la surprise", "de": "die Überraschung"}, {"fr": "surprendre", "de": "überraschen"}, {"fr": "triste m,f (adj.)", "de": "traurig"}, {"fr": "regretter", "de": "bedauern"}, {"fr": "détester, haïr", "de": "verabscheuen, hassen"}]''')

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
