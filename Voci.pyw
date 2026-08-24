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

Wenn das Fenster den Fokus verliert und das aktuelle Wort schon mehr als
einmal geflippt wurde, kommt nach 5 Sekunden automatisch das nächste Wort
(ein feiner Balken unten zählt runter) – ausser man tabbt vorher zurück.
"""

import json
import math
import random
import sys
import tkinter as tk
import tkinter.font as tkfont

VOCAB = json.loads(r'''[{"fr": "Se présenter", "de": "sich jemandem vorstellen"}, {"fr": "la présentation", "de": "die Vorstellung von etwas oder jemandem"}, {"fr": "caractériser", "de": "charakterisieren"}, {"fr": "le caractère", "de": "der Charakter"}, {"fr": "enchanté/enchantée (adj.)", "de": "Sehr erfreut!"}, {"fr": "une adresse", "de": "eine Adresse"}, {"fr": "s’adresser à", "de": "sich wenden/richten an"}, {"fr": "mémoriser", "de": "sich einprägen/sich merken"}, {"fr": "la mémoire", "de": "das Gedächtnis/die Erinnerung"}, {"fr": "la date de naissance", "de": "das Geburtsdatum"}, {"fr": "la naissance", "de": "die Geburt"}, {"fr": "naître", "de": "geboren werden"}, {"fr": "Je suis né/née le 15 août 1994", "de": "Ich bin am 15. August 1994 geboren"}, {"fr": "le mois/les mois", "de": "der Monat/die Monate"}, {"fr": "janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre, décembre", "de": "Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"}, {"fr": "en janvier, en août, en juin", "de": "im Januar, im August, im Juni"}, {"fr": "les jours (le jour) de la semaine :", "de": "die Tage der Woche:"}, {"fr": "lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche", "de": "Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag"}, {"fr": "le lundi, le samedi, le dimanche", "de": "am/immer am Montag, am Samstag, am Sonntag"}, {"fr": "à ce soir – à demain – à samedi", "de": "bis heute Abend - bis morgen – bis am Samstag"}, {"fr": "le matin – ce matin", "de": "der/am Morgen – heute Morgen"}, {"fr": "l’après-midi, (m.) – cet après-midi", "de": "der/am Nachmittag – heute Nachmittag"}, {"fr": "le soir – ce soir", "de": "der/am Abend – heute Abend"}, {"fr": "les quatre saisons, (f.):", "de": "die 4 Jahreszeiten:"}, {"fr": "l’été (m.), l’automne(m.), l’hiver (m.), le printemps", "de": "der Sommer, der Herbst, der Winter, der Frühling"}, {"fr": "en été, en automne, en hiver, au printemps", "de": "im Sommer, im Herbst, im Winter, im Frühling"}, {"fr": "un état civil", "de": "ein Zivilstand"}, {"fr": "marié/mariée (adj.)", "de": "verheiratet"}, {"fr": "célibataire (adj.)", "de": "ledig"}, {"fr": "divorcé/divorcée (adj.)", "de": "geschieden"}, {"fr": "veuf/veuve (adj.)", "de": "verwitwet"}, {"fr": "la langue maternelle", "de": "die Muttersprache"}, {"fr": "la langue étrangère", "de": "die Fremdsprache"}, {"fr": "apprendre une langue", "de": "eine Sprache lernen"}, {"fr": "un enregistrement", "de": "eine (Radio-/Musik...)-Aufnahme"}, {"fr": "enregistrer", "de": "(Musik,…) aufnehmen"}, {"fr": "une émission", "de": "eine Fernsehsendung"}, {"fr": "regarder la télévision", "de": "fernsehen"}, {"fr": "écouter la radio", "de": "Radio hören"}, {"fr": "être d’origine italienne/suisse/allemande", "de": "ital./schweiz./deutscher Herkunft sein"}, {"fr": "traduire : je traduis", "de": "übersetzen: ich übersetze"}, {"fr": "la traduction", "de": "die Übersetzung"}, {"fr": "le portable", "de": "das Handy"}, {"fr": "téléphoner à quelqu’un - appeler quelqu‘un", "de": "jemandem telefonieren/jem. anrufen"}, {"fr": "se décider", "de": "sich entscheiden"}, {"fr": "la décision", "de": "die Entscheidung"}, {"fr": "se reposer", "de": "sich ausruhen, sich erholen"}, {"fr": "s’inscrire", "de": "sich einschreiben"}, {"fr": "répondre", "de": "antworten"}, {"fr": "la réponse", "de": "die Antwort"}, {"fr": "cocher la réponse correcte", "de": "die richtige Antwort ankreuzen"}, {"fr": "faire des études (f.)", "de": "ein Studium machen"}, {"fr": "aller en boîte", "de": "in die Disco gehen"}, {"fr": "choisir", "de": "auswählen"}, {"fr": "le choix", "de": "(die Aus)-Wahl"}, {"fr": "le numéro de portable", "de": "die Handynummer"}, {"fr": "demander quelque chose à quelqu’un", "de": "jemanden um etwas bitten"}, {"fr": "participer à", "de": "teilnehmen an"}, {"fr": "la participation", "de": "die Teilnahme"}, {"fr": "poser une question", "de": "eine Frage stellen"}, {"fr": "s‘amuser", "de": "sich amüsieren"}, {"fr": "se coucher, aller au lit", "de": "ins Bett gehen"}, {"fr": "se dépêcher", "de": "sich beeilen"}, {"fr": "se doucher", "de": "sich duschen"}, {"fr": "s’ énerver", "de": "sich aufregen"}, {"fr": "s ’habiller", "de": "sich anziehen"}, {"fr": "se maquiller", "de": "sich schminken"}, {"fr": "s’occuper de", "de": "sich beschäftigen mit, sich kümmern um"}, {"fr": "se réveiller", "de": "aufwachen"}, {"fr": "à mon avis/selon moi", "de": "meiner Meinung nach"}, {"fr": "par contre", "de": "hingegen"}, {"fr": "avoir raison", "de": "Recht haben"}, {"fr": "avoir tort", "de": "unrecht haben"}, {"fr": "exagérer", "de": "übertreiben"}, {"fr": "trouver", "de": "finden"}, {"fr": "un emploi", "de": "eine (Arbeits-)Stelle"}, {"fr": "une erreur/une faute", "de": "ein Fehler"}, {"fr": "un projet d’avenir", "de": "ein Zukunftsplan/ein Projekt für die Zukunft"}, {"fr": "rendre visite à quelqu’un", "de": "jemanden besuchen"}, {"fr": "visiter un musée/une ville", "de": "ein Museum/eine Stadt besichtigen"}, {"fr": "fréquenter/faire l’école de Maturité Professionnelle", "de": "die BMS besuchen"}, {"fr": "la maturité professionnelle", "de": "die BM/Berufsmatura"}, {"fr": "le groupe", "de": "die Gruppe"}, {"fr": "parler anglais-espagnol-français-italien-japonais-polonais-russe-turc-allemand", "de": "englisch-spanisch-französisch-italienisch-japanisch-polnisch-russisch-türkisch-deutsch sprechen"}, {"fr": "avoir besoin de (j’ai besoin d’une langue étrangère)", "de": "brauchen (ich brauche eine Fremdsprache)"}, {"fr": "savoir parler français", "de": "französisch sprechen können"}, {"fr": "savoir", "de": "wissen, können (weil gelernt!)"}, {"fr": "connaître", "de": "kennen, kennenlernen"}, {"fr": "pouvoir", "de": "können, dürfen"}, {"fr": "l’Angleterre (f.)", "de": "England"}, {"fr": "un Anglais/une Anglaise", "de": "ein Engländer/eine Engländerin"}, {"fr": "anglais,e (adj.)", "de": "englisch"}, {"fr": "l‘ Espagne (f.)", "de": "Spanien"}, {"fr": "un Espagnol/une Espagnole", "de": "ein Spanier/eine Spanierin"}, {"fr": "espagnol,e (adj.)", "de": "spanisch"}, {"fr": "la France", "de": "Frankreich"}, {"fr": "un Français/une Française", "de": "ein Franzose/eine Französin"}, {"fr": "français,e (adj.)", "de": "französisch"}, {"fr": "l’Italie (f.)", "de": "Italien"}, {"fr": "un Italien/une Italienne", "de": "ein Italiener/eine Italienerin"}, {"fr": "italien/italienne (adj.)", "de": "italienisch"}, {"fr": "le Japon", "de": "Japan"}, {"fr": "un Japonais/une Japonaise", "de": "ein Japaner/eine Japanerin"}, {"fr": "japonais,e (adj.)", "de": "japanisch"}, {"fr": "la Russie", "de": "Russland"}, {"fr": "un Russe/une Russe", "de": "ein Russe/eine Russin"}, {"fr": "russe m,f (adj.)", "de": "russisch"}, {"fr": "l’Allemagne (f.)", "de": "Deutschland"}, {"fr": "un Allemand/une Allemande", "de": "ein Deutscher/eine Deutsche"}, {"fr": "allemand,e (adj.)", "de": "deutsch"}, {"fr": "la Croatie", "de": "Kroatien"}, {"fr": "croate (adj.)", "de": "kroatisch"}, {"fr": "la Serbie", "de": "Serbien"}, {"fr": "serbe (adj.)", "de": "serbisch"}, {"fr": "maîtriser quelque chose", "de": "etwas beherrschen"}, {"fr": "maîtriser une langue/une situation", "de": "eine Sprache/eine Situation beherrschen"}, {"fr": "utiliser qc comme", "de": "etwas benutzen als"}, {"fr": "apprendre qc", "de": "etw. lernen"}, {"fr": "apprendre à faire qc", "de": "lernen etw. zu machen"}, {"fr": "un apprentissage", "de": "eine Lehre/ein Lernen"}, {"fr": "un apprenti/une apprentie", "de": "ein Lehrling, ein Lernender/eine Lernende"}, {"fr": "améliorer qc", "de": "etw. verbessern"}, {"fr": "améliorer la prononciation", "de": "die Aussprache verbessern"}, {"fr": "accompagner", "de": "begleiten"}, {"fr": "être utile m,f (adj.)", "de": "nützlich sein"}, {"fr": "riche m,f (adj.)", "de": "reich"}, {"fr": "la richesse", "de": "der Reichtum"}, {"fr": "construire une phrase/une maison", "de": "einen Satz bilden, ein Haus bauen"}, {"fr": "disponible m,f (adj.)", "de": "verfügbar"}, {"fr": "partout", "de": "überall"}, {"fr": "nulle part", "de": "nirgends, nirgendwo"}, {"fr": "accéder à", "de": "Zugang erlangen"}, {"fr": "un accès (à l’internet)", "de": "ein (Internet-)Zugang"}, {"fr": "apprendre par coeur", "de": "auswendig lernen"}, {"fr": "un oeil-les yeux (pl.m)", "de": "ein Auge-die Augen"}, {"fr": "la vue", "de": "der Blick/das Sehen"}, {"fr": "voir", "de": "sehen"}, {"fr": "regarder", "de": "anschauen/schauen"}, {"fr": "le son", "de": "der Ton/Klang"}, {"fr": "sonner", "de": "tönen/läuten/klingeln"}, {"fr": "une oreille", "de": "ein Ohr"}, {"fr": "écouter", "de": "(zu-)hören"}, {"fr": "entendre", "de": "hören"}, {"fr": "une odeur", "de": "ein Geruch"}, {"fr": "un goût", "de": "ein Geschmack"}, {"fr": "ensemble", "de": "gemeinsam"}, {"fr": "parfois/de temps en temps", "de": "bisweilen/ hie und da,/ ab und zu"}, {"fr": "entier/entière (adj.)", "de": "ganz, gesamt"}, {"fr": "le lait entier", "de": "die Vollmilch"}, {"fr": "le monde entier", "de": "die ganze Welt"}, {"fr": "tout le monde (3. pers.sg.!)", "de": "jedermann; alle"}, {"fr": "quand, comment, où, pourquoi, combien, quel(s) quelle(s)", "de": "wann, wie, wo, warum, wieviel, welche"}, {"fr": "les aliments (m. pl.)", "de": "die Nahrungsmittel"}, {"fr": "le légume", "de": "das Gemüse"}, {"fr": "l’épinard (m.)", "de": "der Spinat"}, {"fr": "l’ail (m.)", "de": "der Knoblauch"}, {"fr": "la courgette", "de": "die Zucchetti"}, {"fr": "une asperge", "de": "eine Spargel"}, {"fr": "le chou", "de": "der Kohl"}, {"fr": "la pomme de terre", "de": "die Kartoffel"}, {"fr": "la tomate", "de": "die Tomate"}, {"fr": "la carotte", "de": "die Karotte"}, {"fr": "le champignon", "de": "der Pilz"}, {"fr": "l’oignon (m.)", "de": "die Zwiebel"}, {"fr": "le produit laitier", "de": "das Milchprodukt"}, {"fr": "le beurre", "de": "die Butter"}, {"fr": "la crème", "de": "der Rahm"}, {"fr": "le yaourt", "de": "das Joghurt"}, {"fr": "le fromage (la fondue, la raclette)", "de": "der Käse (das Fondue, das Raclette)"}, {"fr": "les fruits (m.pl.)", "de": "die Früchte"}, {"fr": "la fraise", "de": "die Erdbeere"}, {"fr": "la framboise", "de": "die Himbeere"}, {"fr": "la pomme", "de": "der Apfel"}, {"fr": "la poire", "de": "die Birne"}, {"fr": "le raisin", "de": "die Traube"}, {"fr": "l’abricot (m.)", "de": "die Aprikose"}, {"fr": "une orange", "de": "eine Orange"}, {"fr": "un citron", "de": "die Zitrone"}, {"fr": "un melon", "de": "eine Melone"}, {"fr": "une banane", "de": "eine Banane"}, {"fr": "un ananas", "de": "eine Ananas"}, {"fr": "une prune", "de": "eine Zwetschge"}, {"fr": "le pain", "de": "das Brot"}, {"fr": "le croissant", "de": "das Gipfeli"}, {"fr": "la baguette", "de": "das Stangenbrot, das Baguette"}, {"fr": "une tartine (de miel)", "de": "ein Brot mit Aufstrich (Honigbrot)"}, {"fr": "le muesli", "de": "das Müsli"}, {"fr": "cru, crue (adj.)", "de": "roh"}, {"fr": "cuit,e (adj.)", "de": "gekocht"}, {"fr": "le miel", "de": "der Honig"}, {"fr": "un œuf", "de": "ein Ei"}, {"fr": "la viande (la viande séchée)", "de": "das Fleisch (das Trockenfleisch)"}, {"fr": "la confiture", "de": "die Marmelade, die Konfitüre"}, {"fr": "le petit déjeuner, le déjeuner, le dîner", "de": "das Frühstück, das Mittagessen, das Abendessen"}, {"fr": "un repas", "de": "das Essen, die Mahlzeit"}, {"fr": "une boisson", "de": "ein Getränk"}, {"fr": "le plat (le plat préféré)", "de": "das Gericht (das Lieblingsessen)"}, {"fr": "un escargot", "de": "eine Schnecke"}, {"fr": "le saumon", "de": "der Lachs"}, {"fr": "le poireau", "de": "der Lauch"}, {"fr": "un filet de bœuf", "de": "ein Rinderfilet"}, {"fr": "faire un barbecue / une grillade", "de": "grillen"}, {"fr": "une épice, épicer", "de": "ein Gewürz, würzen"}, {"fr": "pimenté,e (adj.)", "de": "pikant, scharf (kulinarisch)"}, {"fr": "la volaille", "de": "das Geflügel"}, {"fr": "le poisson", "de": "der Fisch"}, {"fr": "le veau", "de": "das Kalb"}, {"fr": "la tarte", "de": "flacher Obstkuchen"}, {"fr": "le gâteau", "de": "der Kuchen"}, {"fr": "une carafe (d’eau)", "de": "eine Karaffe (Wasser)"}, {"fr": "oublier", "de": "vergessen"}, {"fr": "s’intéresser à", "de": "sich interessieren für"}, {"fr": "je m’intéresse aux langues", "de": "ich interessiere mich für Sprachen"}, {"fr": "bon/bonne (adj.)", "de": "gut, gütig"}, {"fr": "gentil/gentille (adj.)", "de": "nett, freundlich"}, {"fr": "méchant/méchante (adj.)", "de": "böse, gemein, boshaft"}, {"fr": "aimable (adj.)", "de": "liebenswürdig, freundlich"}, {"fr": "cher/chère (adj.)", "de": "lieb, teuer"}, {"fr": "être fier/fière de", "de": "stolz sein auf"}, {"fr": "paresseux/paresseuse (adj.)", "de": "faul"}, {"fr": "patient,e(adj.)", "de": "geduldig"}, {"fr": "impatient,e (adj.)", "de": "ungeduldig"}, {"fr": "la patience", "de": "die Geduld"}, {"fr": "prudent,e (adj.)", "de": "vorsichtig"}, {"fr": "adroit,e (adj.)", "de": "geschickt"}, {"fr": "aimer", "de": "lieben, mögen, gerne tun"}, {"fr": "il aime danser", "de": "er tanzt gerne"}, {"fr": "l’amour m.", "de": "die Liebe"}, {"fr": "être content/contente de", "de": "zufrieden sein mit"}, {"fr": "heureux/heureuse (adj.)", "de": "glücklich"}, {"fr": "malheureux-malheureuse (adj.", "de": "unglücklich"}, {"fr": "la joie", "de": "die Freude, das Vergnügen"}, {"fr": "le plaisir", "de": "das Vergnügen, die Freude"}, {"fr": "agréable m,f (adj.)", "de": "angenehm"}, {"fr": "désagréable m,f (adj.)", "de": "unangenehm"}, {"fr": "avoir envie de", "de": "Lust haben auf"}, {"fr": "l’espoir (m.)", "de": "die Hoffnung"}, {"fr": "espérer", "de": "hoffen"}, {"fr": "la surprise", "de": "die Überraschung"}, {"fr": "surprendre", "de": "überraschen"}, {"fr": "triste m,f (adj.)", "de": "traurig"}, {"fr": "regretter", "de": "bedauern"}, {"fr": "détester, haïr", "de": "verabscheuen, hassen"}]''')

# Fenstersymbol (Trikolore) als eingebettetes PNG - ohne das zeigt Tk in der
# Taskleiste sein eigenes Feder-Logo.
ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAEbklEQVR4nO2bT2gcVRzHv7/fm5ndpGlim6QEogfRgxikIInEgiJWaVMlImVDb71II1QEwVOKBxFz8iJYSAseUgRrlkBTS2qxmoqXgLmUoigULybSNn/dJLs7b+a9n4fd1QhpspjUZzbzYeeyvH3zfZ99w8xhvoR/QsAIA31GRPjpo5+9encpPl4I4+4osg8LpB6Q0rB1UIoQ/xHiwlAPXn/5UURG4Kn1x1aNMYBS0F9PYOXtAVBTY+m7DWAgT743Tan0pOxrGP147PMr7xNZARQAS6VFVBZcQQggMCAdh4dfm16Iz6zmbZc2BNgYgFnzs/UhRZClIkYu9CLT8xiMBRRvYfEAYC3AjOjqdeTeeAf0UNPmAgjwiBAwI1IKJp36odCy/8O28S/GpLzmigReu3iRCdX27KdDv/wulxZztktHoUCKBhQLqDx6g4O5fPYyIpsYq4byHFJZWRWHJUIIyLI1pqC1pJZXu5pn7l6ae/6VoRsiqjwflQUIAX0sMqHanrk9emfB79fFlRgILYgIIAXQFvfxfw8BRCDFRLQMsbliIW5eXO5/6lDP6A2ZUABYAGJksszImvbu22dnc6leq3MaTB5AW928/xsYYDB781rr5pVC7xPPfXSWAINMhhnZPvPkS8PHZpf9U1bnIjAFrgM/KIgpWNRh1LqSP3XvaN8xymYNT01N+b/dKwxGYSTg2vnX74dl4jgMBXPzg1NT53w+OfDjkbxWByGhoHSbqGkIUCtipV5HB9ve+/YIzy3oE1FMAtrsJldDEMQ3Vvxc7oRX1LYbVqj0CLBbINbWEIW624uNbQcsduKt7t9CAMUiIGPbGaD0Ltr8f2EFACS9i7b9+iQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXMCDF+3SgappSs4eK7CmeKb0lvx0Fn52BAOIRQRTPcDrgSbAnKL0xvUsQG7ASSQWT3LI/uOh7QpBddCEIKFJMUWPjRR4e7LhWH5iboBQB2LiQVwMIYBqIKR/4N+988OI17uzsjB45UDfgp3yClZq/DNiK9VIpQkvzQGdnf8TIjKifrp8cb90bneeg0YcV7Trkg0Ks6H1Byp9tqD9/4KuRcclkFCObsRYZNTP5+OnWxvAyB40BrMRA7ewGC1hYGzcHQTDfUHf55+/fPS2AQjZrPYAEEEtEEJk43n7o10/mlhr6tY4ACQUEC4B3WqVGSh8rAt5LzCpdx/NNe87d+u7KWy8QGaDUH/ZKw0kAISIyDLzZcXj46vQCn1nNp7q0IVVtedoSKl2U0qzb4aw8B6E8d+XYgHJ5mgJWKlIK4drydDlUpTztrTmTACCLEXXrm74xEfny7/q8dEcRVVefjzwwCawxiI0A21Sfjwmwe+pA9elN2+MA8pHvTcdV1Of/BKK/3Wv1D3rrAAAAAElFTkSuQmCC"

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
BG = (255, 255, 255)          # Karte
FG = (17, 17, 17)             # Text / Icons
HOVER = (235, 235, 235)       # Knopf beim Hovern
BORDER = "#d8d8d8"            # Kartenrand
TIMER = "#ededed"             # Countdown-Balken (dezent)
KEY = "#00fe00"               # Farbschlüssel für runde Ecken (Windows)
FALLBACK_VOID = "#bdbdbd"     # falls die Plattform keine Transparenz kann

# ---------------------------------------------------------------- Verhalten
AUTO_DELAY_MS = 5000          # 5 s bis zum Auto-Weiter
FLIPS_NEEDED = 2              # "mehr als 1 mal geflippt"
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
        self.deck = list(range(len(VOCAB)))
        random.shuffle(self.deck)
        self.pos = 0
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
        self.imgcache = {}
        self._wrapcache = {}

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
            self.root.bind("<FocusIn>", self._on_focus_in)
            self.root.bind("<FocusOut>", lambda e: self.set_active(False))

        self.root.lift()
        self.draw()
        self.root.mainloop()

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
        return VOCAB[self.deck[self.pos]]

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

        # Der Text staucht mit der Karte mit; die Zeilen stehen dabei fest.
        lines, full = self.wrapped(self.word[self.side])
        self.font_word.configure(size=-max(1, int(round(full * self.scale))))
        c.create_text(cx, h / 2.0, text=lines, font=self.font_word,
                      fill=hexc(FG), justify="center")

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
                    size=-max(1, int(round(self.tiny_px * self.scale))))
                c.create_text(x, by, text=self.start_side.upper(),
                              font=self.font_tiny, fill=hexc(FG))

        if self.countdown_frac and rest:
            bw = (w - 2 * (self.pad + self.br + 12 * self.k)) * self.countdown_frac
            if bw > 0:
                y = h - 11 * self.k
                c.create_rectangle(cx - bw / 2, y, cx + bw / 2, y + 3 * self.k,
                                   fill=TIMER, width=0)

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
