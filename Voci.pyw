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
  Taste d                    -> Dark Mode an/aus
  Taste u                    -> gefundenes Update einspielen
  Taste m                    -> Menü (Einstellungen, Voci-Sets)
  Taste c / v / b            -> Wort bewerten: kann ich nicht / neutral / kann ich
  Pfeil links / rechts       -> zurück / weiter (abschaltbar im Menü)

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

EINGEBAUTE_VOCAB = json.loads(r'''[{"fr": "Se présenter", "de": "sich jemandem vorstellen"}, {"fr": "la présentation", "de": "die Vorstellung von etwas oder jemandem"}, {"fr": "caractériser", "de": "charakterisieren"}, {"fr": "le caractère", "de": "der Charakter"}, {"fr": "enchanté/enchantée (adj.)", "de": "Sehr erfreut!"}, {"fr": "une adresse", "de": "eine Adresse"}, {"fr": "s’adresser à", "de": "sich wenden/richten an"}, {"fr": "mémoriser", "de": "sich einprägen/sich merken"}, {"fr": "la mémoire", "de": "das Gedächtnis/die Erinnerung"}, {"fr": "la date de naissance", "de": "das Geburtsdatum"}, {"fr": "la naissance", "de": "die Geburt"}, {"fr": "naître", "de": "geboren werden"}, {"fr": "Je suis né/née le 15 août 1994", "de": "Ich bin am 15. August 1994 geboren"}, {"fr": "le mois/les mois", "de": "der Monat/die Monate"}, {"fr": "janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre, décembre", "de": "Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"}, {"fr": "en janvier, en août, en juin", "de": "im Januar, im August, im Juni"}, {"fr": "les jours (le jour) de la semaine :", "de": "die Tage der Woche:"}, {"fr": "lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche", "de": "Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag"}, {"fr": "le lundi, le samedi, le dimanche", "de": "am/immer am Montag, am Samstag, am Sonntag"}, {"fr": "à ce soir – à demain – à samedi", "de": "bis heute Abend - bis morgen – bis am Samstag"}, {"fr": "le matin – ce matin", "de": "der/am Morgen – heute Morgen"}, {"fr": "l’après-midi, (m.) – cet après-midi", "de": "der/am Nachmittag – heute Nachmittag"}, {"fr": "le soir – ce soir", "de": "der/am Abend – heute Abend"}, {"fr": "les quatre saisons, (f.):", "de": "die 4 Jahreszeiten:"}, {"fr": "l’été (m.), l’automne(m.), l’hiver (m.), le printemps", "de": "der Sommer, der Herbst, der Winter, der Frühling"}, {"fr": "en été, en automne, en hiver, au printemps", "de": "im Sommer, im Herbst, im Winter, im Frühling"}, {"fr": "un état civil", "de": "ein Zivilstand"}, {"fr": "marié/mariée (adj.)", "de": "verheiratet"}, {"fr": "célibataire (adj.)", "de": "ledig"}, {"fr": "divorcé/divorcée (adj.)", "de": "geschieden"}, {"fr": "veuf/veuve (adj.)", "de": "verwitwet"}, {"fr": "la langue maternelle", "de": "die Muttersprache"}, {"fr": "la langue étrangère", "de": "die Fremdsprache"}, {"fr": "apprendre une langue", "de": "eine Sprache lernen"}, {"fr": "un enregistrement", "de": "eine (Radio-/Musik...)-Aufnahme"}, {"fr": "enregistrer", "de": "(Musik,…) aufnehmen"}, {"fr": "une émission", "de": "eine Fernsehsendung"}, {"fr": "regarder la télévision", "de": "fernsehen"}, {"fr": "écouter la radio", "de": "Radio hören"}, {"fr": "être d’origine italienne/suisse/allemande", "de": "ital./schweiz./deutscher Herkunft sein"}, {"fr": "traduire : je traduis", "de": "übersetzen: ich übersetze"}, {"fr": "la traduction", "de": "die Übersetzung"}, {"fr": "le portable", "de": "das Handy"}, {"fr": "téléphoner à quelqu’un - appeler quelqu‘un", "de": "jemandem telefonieren/jem. anrufen"}, {"fr": "se décider", "de": "sich entscheiden"}, {"fr": "la décision", "de": "die Entscheidung"}, {"fr": "se reposer", "de": "sich ausruhen, sich erholen"}, {"fr": "s’inscrire", "de": "sich einschreiben"}, {"fr": "répondre", "de": "antworten"}, {"fr": "la réponse", "de": "die Antwort"}, {"fr": "cocher la réponse correcte", "de": "die richtige Antwort ankreuzen"}, {"fr": "faire des études (f.)", "de": "ein Studium machen"}, {"fr": "aller en boîte", "de": "in die Disco gehen"}, {"fr": "choisir", "de": "auswählen"}, {"fr": "le choix", "de": "(die Aus)-Wahl"}, {"fr": "le numéro de portable", "de": "die Handynummer"}, {"fr": "demander quelque chose à quelqu’un", "de": "jemanden um etwas bitten"}, {"fr": "participer à", "de": "teilnehmen an"}, {"fr": "la participation", "de": "die Teilnahme"}, {"fr": "poser une question", "de": "eine Frage stellen"}, {"fr": "s‘amuser", "de": "sich amüsieren"}, {"fr": "se coucher, aller au lit", "de": "ins Bett gehen"}, {"fr": "se dépêcher", "de": "sich beeilen"}, {"fr": "se doucher", "de": "sich duschen"}, {"fr": "s’ énerver", "de": "sich aufregen"}, {"fr": "s ’habiller", "de": "sich anziehen"}, {"fr": "se maquiller", "de": "sich schminken"}, {"fr": "s’occuper de", "de": "sich beschäftigen mit, sich kümmern um"}, {"fr": "se réveiller", "de": "aufwachen"}, {"fr": "à mon avis/selon moi", "de": "meiner Meinung nach"}, {"fr": "par contre", "de": "hingegen"}, {"fr": "avoir raison", "de": "Recht haben"}, {"fr": "avoir tort", "de": "unrecht haben"}, {"fr": "exagérer", "de": "übertreiben"}, {"fr": "trouver", "de": "finden"}, {"fr": "un emploi", "de": "eine (Arbeits-)Stelle"}, {"fr": "une erreur/une faute", "de": "ein Fehler"}, {"fr": "un projet d’avenir", "de": "ein Zukunftsplan/ein Projekt für die Zukunft"}, {"fr": "rendre visite à quelqu’un", "de": "jemanden besuchen"}, {"fr": "visiter un musée/une ville", "de": "ein Museum/eine Stadt besichtigen"}, {"fr": "fréquenter/faire l’école de Maturité Professionnelle", "de": "die BMS besuchen"}, {"fr": "la maturité professionnelle", "de": "die BM/Berufsmatura"}, {"fr": "le groupe", "de": "die Gruppe"}, {"fr": "parler anglais-espagnol-français-italien-japonais-polonais-russe-turc-allemand", "de": "englisch-spanisch-französisch-italienisch-japanisch-polnisch-russisch-türkisch-deutsch sprechen"}, {"fr": "avoir besoin de (j’ai besoin d’une langue étrangère)", "de": "brauchen (ich brauche eine Fremdsprache)"}, {"fr": "savoir parler français", "de": "französisch sprechen können"}, {"fr": "savoir", "de": "wissen, können (weil gelernt!)"}, {"fr": "connaître", "de": "kennen, kennenlernen"}, {"fr": "pouvoir", "de": "können, dürfen"}, {"fr": "l’Angleterre (f.)", "de": "England"}, {"fr": "un Anglais/une Anglaise", "de": "ein Engländer/eine Engländerin"}, {"fr": "anglais,e (adj.)", "de": "englisch"}, {"fr": "l‘ Espagne (f.)", "de": "Spanien"}, {"fr": "un Espagnol/une Espagnole", "de": "ein Spanier/eine Spanierin"}, {"fr": "espagnol,e (adj.)", "de": "spanisch"}, {"fr": "la France", "de": "Frankreich"}, {"fr": "un Français/une Française", "de": "ein Franzose/eine Französin"}, {"fr": "français,e (adj.)", "de": "französisch"}, {"fr": "l’Italie (f.)", "de": "Italien"}, {"fr": "un Italien/une Italienne", "de": "ein Italiener/eine Italienerin"}, {"fr": "italien/italienne (adj.)", "de": "italienisch"}, {"fr": "le Japon", "de": "Japan"}, {"fr": "un Japonais/une Japonaise", "de": "ein Japaner/eine Japanerin"}, {"fr": "japonais,e (adj.)", "de": "japanisch"}, {"fr": "la Russie", "de": "Russland"}, {"fr": "un Russe/une Russe", "de": "ein Russe/eine Russin"}, {"fr": "russe m,f (adj.)", "de": "russisch"}, {"fr": "l’Allemagne (f.)", "de": "Deutschland"}, {"fr": "un Allemand/une Allemande", "de": "ein Deutscher/eine Deutsche"}, {"fr": "allemand,e (adj.)", "de": "deutsch"}, {"fr": "la Croatie", "de": "Kroatien"}, {"fr": "croate (adj.)", "de": "kroatisch"}, {"fr": "la Serbie", "de": "Serbien"}, {"fr": "serbe (adj.)", "de": "serbisch"}, {"fr": "maîtriser quelque chose", "de": "etwas beherrschen"}, {"fr": "maîtriser une langue/une situation", "de": "eine Sprache/eine Situation beherrschen"}, {"fr": "utiliser qc comme", "de": "etwas benutzen als"}, {"fr": "apprendre qc", "de": "etw. lernen"}, {"fr": "apprendre à faire qc", "de": "lernen etw. zu machen"}, {"fr": "un apprentissage", "de": "eine Lehre/ein Lernen"}, {"fr": "un apprenti/une apprentie", "de": "ein Lehrling, ein Lernender/eine Lernende"}, {"fr": "améliorer qc", "de": "etw. verbessern"}, {"fr": "améliorer la prononciation", "de": "die Aussprache verbessern"}, {"fr": "accompagner", "de": "begleiten"}, {"fr": "être utile m,f (adj.)", "de": "nützlich sein"}, {"fr": "riche m,f (adj.)", "de": "reich"}, {"fr": "la richesse", "de": "der Reichtum"}, {"fr": "construire une phrase/une maison", "de": "einen Satz bilden, ein Haus bauen"}, {"fr": "disponible m,f (adj.)", "de": "verfügbar"}, {"fr": "partout", "de": "überall"}, {"fr": "nulle part", "de": "nirgends, nirgendwo"}, {"fr": "accéder à", "de": "Zugang erlangen"}, {"fr": "un accès (à l’internet)", "de": "ein (Internet-)Zugang"}, {"fr": "apprendre par coeur", "de": "auswendig lernen"}, {"fr": "un oeil-les yeux (pl.m)", "de": "ein Auge-die Augen"}, {"fr": "la vue", "de": "der Blick/das Sehen"}, {"fr": "voir", "de": "sehen"}, {"fr": "regarder", "de": "anschauen/schauen"}, {"fr": "le son", "de": "der Ton/Klang"}, {"fr": "sonner", "de": "tönen/läuten/klingeln"}, {"fr": "une oreille", "de": "ein Ohr"}, {"fr": "écouter", "de": "(zu-)hören"}, {"fr": "entendre", "de": "hören"}, {"fr": "une odeur", "de": "ein Geruch"}, {"fr": "un goût", "de": "ein Geschmack"}, {"fr": "ensemble", "de": "gemeinsam"}, {"fr": "parfois/de temps en temps", "de": "bisweilen/ hie und da,/ ab und zu"}, {"fr": "entier/entière (adj.)", "de": "ganz, gesamt"}, {"fr": "le lait entier", "de": "die Vollmilch"}, {"fr": "le monde entier", "de": "die ganze Welt"}, {"fr": "tout le monde (3. pers.sg.!)", "de": "jedermann; alle"}, {"fr": "quand, comment, où, pourquoi, combien, quel(s) quelle(s)", "de": "wann, wie, wo, warum, wieviel, welche"}, {"fr": "les aliments (m. pl.)", "de": "die Nahrungsmittel"}, {"fr": "le légume", "de": "das Gemüse"}, {"fr": "l’épinard (m.)", "de": "der Spinat"}, {"fr": "l’ail (m.)", "de": "der Knoblauch"}, {"fr": "la courgette", "de": "die Zucchetti"}, {"fr": "une asperge", "de": "eine Spargel"}, {"fr": "le chou", "de": "der Kohl"}, {"fr": "la pomme de terre", "de": "die Kartoffel"}, {"fr": "la tomate", "de": "die Tomate"}, {"fr": "la carotte", "de": "die Karotte"}, {"fr": "le champignon", "de": "der Pilz"}, {"fr": "l’oignon (m.)", "de": "die Zwiebel"}, {"fr": "le produit laitier", "de": "das Milchprodukt"}, {"fr": "le beurre", "de": "die Butter"}, {"fr": "la crème", "de": "der Rahm"}, {"fr": "le yaourt", "de": "das Joghurt"}, {"fr": "le fromage (la fondue, la raclette)", "de": "der Käse (das Fondue, das Raclette)"}, {"fr": "les fruits (m.pl.)", "de": "die Früchte"}, {"fr": "la fraise", "de": "die Erdbeere"}, {"fr": "la framboise", "de": "die Himbeere"}, {"fr": "la pomme", "de": "der Apfel"}, {"fr": "la poire", "de": "die Birne"}, {"fr": "le raisin", "de": "die Traube"}, {"fr": "l’abricot (m.)", "de": "die Aprikose"}, {"fr": "une orange", "de": "eine Orange"}, {"fr": "un citron", "de": "die Zitrone"}, {"fr": "un melon", "de": "eine Melone"}, {"fr": "une banane", "de": "eine Banane"}, {"fr": "un ananas", "de": "eine Ananas"}, {"fr": "une prune", "de": "eine Zwetschge"}, {"fr": "le pain", "de": "das Brot"}, {"fr": "le croissant", "de": "das Gipfeli"}, {"fr": "la baguette", "de": "das Stangenbrot, das Baguette"}, {"fr": "une tartine (de miel)", "de": "ein Brot mit Aufstrich (Honigbrot)"}, {"fr": "le muesli", "de": "das Müsli"}, {"fr": "cru, crue (adj.)", "de": "roh"}, {"fr": "cuit,e (adj.)", "de": "gekocht"}, {"fr": "le miel", "de": "der Honig"}, {"fr": "un œuf", "de": "ein Ei"}, {"fr": "la viande (la viande séchée)", "de": "das Fleisch (das Trockenfleisch)"}, {"fr": "la confiture", "de": "die Marmelade, die Konfitüre"}, {"fr": "le petit déjeuner, le déjeuner, le dîner", "de": "das Frühstück, das Mittagessen, das Abendessen"}, {"fr": "un repas", "de": "das Essen, die Mahlzeit"}, {"fr": "une boisson", "de": "ein Getränk"}, {"fr": "le plat (le plat préféré)", "de": "das Gericht (das Lieblingsessen)"}, {"fr": "un escargot", "de": "eine Schnecke"}, {"fr": "le saumon", "de": "der Lachs"}, {"fr": "le poireau", "de": "der Lauch"}, {"fr": "un filet de bœuf", "de": "ein Rinderfilet"}, {"fr": "faire un barbecue / une grillade", "de": "grillen"}, {"fr": "une épice, épicer", "de": "ein Gewürz, würzen"}, {"fr": "pimenté,e (adj.)", "de": "pikant, scharf (kulinarisch)"}, {"fr": "la volaille", "de": "das Geflügel"}, {"fr": "le poisson", "de": "der Fisch"}, {"fr": "le veau", "de": "das Kalb"}, {"fr": "la tarte", "de": "flacher Obstkuchen"}, {"fr": "le gâteau", "de": "der Kuchen"}, {"fr": "une carafe (d’eau)", "de": "eine Karaffe (Wasser)"}, {"fr": "oublier", "de": "vergessen"}, {"fr": "s’intéresser à", "de": "sich interessieren für"}, {"fr": "je m’intéresse aux langues", "de": "ich interessiere mich für Sprachen"}, {"fr": "bon/bonne (adj.)", "de": "gut, gütig"}, {"fr": "gentil/gentille (adj.)", "de": "nett, freundlich"}, {"fr": "méchant/méchante (adj.)", "de": "böse, gemein, boshaft"}, {"fr": "aimable (adj.)", "de": "liebenswürdig, freundlich"}, {"fr": "cher/chère (adj.)", "de": "lieb, teuer"}, {"fr": "être fier/fière de", "de": "stolz sein auf"}, {"fr": "paresseux/paresseuse (adj.)", "de": "faul"}, {"fr": "patient,e(adj.)", "de": "geduldig"}, {"fr": "impatient,e (adj.)", "de": "ungeduldig"}, {"fr": "la patience", "de": "die Geduld"}, {"fr": "prudent,e (adj.)", "de": "vorsichtig"}, {"fr": "adroit,e (adj.)", "de": "geschickt"}, {"fr": "aimer", "de": "lieben, mögen, gerne tun"}, {"fr": "il aime danser", "de": "er tanzt gerne"}, {"fr": "l’amour m.", "de": "die Liebe"}, {"fr": "être content/contente de", "de": "zufrieden sein mit"}, {"fr": "heureux/heureuse (adj.)", "de": "glücklich"}, {"fr": "malheureux-malheureuse (adj.", "de": "unglücklich"}, {"fr": "la joie", "de": "die Freude, das Vergnügen"}, {"fr": "le plaisir", "de": "das Vergnügen, die Freude"}, {"fr": "agréable m,f (adj.)", "de": "angenehm"}, {"fr": "désagréable m,f (adj.)", "de": "unangenehm"}, {"fr": "avoir envie de", "de": "Lust haben auf"}, {"fr": "l’espoir (m.)", "de": "die Hoffnung"}, {"fr": "espérer", "de": "hoffen"}, {"fr": "la surprise", "de": "die Überraschung"}, {"fr": "surprendre", "de": "überraschen"}, {"fr": "triste m,f (adj.)", "de": "traurig"}, {"fr": "regretter", "de": "bedauern"}, {"fr": "détester, haïr", "de": "verabscheuen, hassen"}]''')
VERSION = "dev"

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
# Zwei Paletten, umschaltbar mit der Taste d
THEMEN = {
    "hell": {
        "bg": (255, 255, 255),      # Karte
        "fg": (29, 29, 31),         # Text/Icons (Apple-Tinte)
        "zweit": (134, 134, 139),   # Sekundärtext
        "hover": (242, 242, 247),   # Knopf beim Hovern
        "gruppe": (242, 242, 247),  # Gruppenflächen im Menü
        "rand": "#e3e3e8",          # Haarlinie
        "timer": "#e8e8ed",         # Countdown-Balken (dezent)
        "akzent": (10, 132, 255),   # Systemblau
        "gruen": (52, 199, 89),     # Schalter an
        "grau": (209, 209, 214),    # Schalter aus
    },
    "dunkel": {
        "bg": (0, 0, 0),
        "fg": (245, 245, 247),
        "zweit": (152, 152, 157),
        "hover": (28, 28, 30),
        "gruppe": (22, 22, 24),
        "rand": "#2c2c2e",
        "timer": "#2c2c2e",
        "akzent": (10, 132, 255),
        "gruen": (48, 209, 88),
        "grau": (57, 57, 61),
    },
}
MAC_ROT = (255, 95, 87)             # Schliessknopf beim Hovern
MAC_ROT_SYMBOL = (96, 8, 4)
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


STANDARD_EINSTELLUNGEN = {
    "thema": "hell",
    "startsprache": "fr",
    "pfeiltasten": True,          # mit Pfeil links/rechts navigieren
    "auto_weiter": True,          # beim Raustabben automatisch weiter
    "auto_dauer": 5,              # Sekunden bis zum Auto-Weiter
    "flip_animation": True,
    "immer_vorne": True,          # Fenster immer im Vordergrund
    "sets": ["etape1"],
    "schwere_modus": False,       # nur Wörter mit Faktor >= 1 üben
}

# Bewertung: c = kann ich noch nicht, v = neutral, b = kann ich schon.
# Jeder Eintrag trägt einen Faktor (Start 1), der die Ziehungswahrscheinlichkeit
# gewichtet: b senkt ihn um 0.2, c erhöht ihn um 0.1, v lässt ihn stehen.
# Bei Faktor 0 kommt das Wort nicht mehr dran.
WERTUNG_DELTA = {"c": +0.1, "v": 0.0, "b": -0.2}
WERTUNG_BLITZ = {"c": (255, 105, 97), "v": (255, 214, 10), "b": (50, 215, 75)}
FAKTOR_MIN, FAKTOR_MAX = 0.0, 3.0
BLITZ_MS = 260                    # so lange leuchtet die Karte nach c/v/b


def _json_datei(name, standard):
    try:
        daten = json.loads((datenordner() / name).read_text(encoding="utf-8"))
        if isinstance(daten, type(standard)):
            return daten
    except Exception:
        pass
    return standard


def _json_speichern(name, daten):
    try:
        (datenordner() / name).write_text(
            json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass


def lade_einstellungen():
    e = dict(STANDARD_EINSTELLUNGEN)
    gespeichert = _json_datei("einstellungen.json", {})
    for k in e:
        if k in gespeichert and isinstance(gespeichert[k], type(e[k])):
            e[k] = gespeichert[k]
    return e


def speichere_einstellungen(e):
    _json_speichern("einstellungen.json", e)


def lade_faktoren():
    """Wertungen pro Wort, am französischen Text festgemacht, damit sie eine
    aktualisierte Wortliste überleben."""
    roh = _json_datei("wertungen.json", {})
    return {k: float(v) for k, v in roh.items()
            if isinstance(v, (int, float)) and FAKTOR_MIN <= v <= FAKTOR_MAX}


def speichere_faktoren(f):
    _json_speichern("wertungen.json", {k: round(v, 4) for k, v in f.items()
                                       if abs(v - 1.0) > 1e-9})


def wertung_prozent(faktor):
    """Faktor 1 (oder mehr) = 0 %, Faktor 0.5 = 50 %, Faktor 0 = 100 %."""
    return int(round(max(0.0, min(1.0, 1.0 - faktor)) * 100))


def wertung_farbe(prozent):
    """Rot (0 %) über Gelb (50 %) nach Grün (100 %)."""
    rot, gelb, gruen = (255, 105, 97), (235, 204, 42), (50, 215, 75)
    if prozent <= 50:
        return blend(rot, gelb, prozent / 50.0)
    return blend(gelb, gruen, (prozent - 50) / 50.0)


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
        self.einst = lade_einstellungen()
        self.vocab = lade_vokabeln()
        self.faktoren = lade_faktoren()          # fr-Text -> Faktor
        self.sets = [{"id": "etape1", "name": "Étape 1",
                      "indizes": list(range(len(self.vocab)))}]
        self.thema = self.einst["thema"]
        self.start_side = self.einst["startsprache"]
        self.side = self.start_side
        self.flips = 0
        self.idx = None
        self.idx = self.ziehe_wort()
        self.history = []            # [{"idx": ..., "delta": ...}], max. 10
        self.undo_delta = None       # Wertung des aktuellen Worts (ersetzbar)
        self.blitz = None            # Blitzfarbe nach c/v/b
        self.menu = None             # Menüfenster
        self.liste_fenster = None    # Wörterliste
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

        self.root.attributes("-topmost", bool(self.einst["immer_vorne"]))
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
        elif (not active and self.was_active and self.flips >= FLIPS_NEEDED
              and self.einst["auto_weiter"]):
            # Ohne verlässliche Fokusmeldungen lieber gar nicht automatisch
            # weiterspringen, als ständig ungefragt weiterzuspringen.
            if IS_WIN or self.seen_focus:
                self.start_auto()
        self.was_active = active

    # ------------------------------------------------------------ Auto-Weiter
    def start_auto(self):
        self.cancel_auto(redraw=False)
        self._auto_left = int(self.einst["auto_dauer"]) * 1000
        self._tick_auto()

    def _tick_auto(self):
        if self._auto_left <= 0:
            self.auto_job = None
            self.countdown_frac = None
            self.next_word()
            return
        self.countdown_frac = self._auto_left / (int(self.einst["auto_dauer"]) * 1000)
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
        return self.vocab[self.idx]

    def faktor(self, idx):
        return self.faktoren.get(self.vocab[idx]["fr"], 1.0)

    def setze_faktor(self, idx, wert):
        wert = max(FAKTOR_MIN, min(FAKTOR_MAX, wert))
        schluessel = self.vocab[idx]["fr"]
        if abs(wert - 1.0) < 1e-9:
            self.faktoren.pop(schluessel, None)
        else:
            self.faktoren[schluessel] = wert
        speichere_faktoren(self.faktoren)

    def aktive_indizes(self):
        indizes = []
        aktiv = set(self.einst["sets"]) or {self.sets[0]["id"]}
        for satz in self.sets:
            if satz["id"] in aktiv:
                indizes.extend(satz["indizes"])
        return indizes or self.sets[0]["indizes"]

    def ziehe_wort(self):
        """Gewichtete Zufallswahl: der Faktor eines Worts ist sein Gewicht.
        Faktor 0 kommt nie, Faktor über 1 entsprechend öfter. Im Modus
        'schwere Wörter' zählen nur Einträge mit Faktor >= 1."""
        kandidaten = [i for i in self.aktive_indizes() if i != self.idx]
        if not kandidaten:
            return self.idx if self.idx is not None else 0
        if self.einst["schwere_modus"]:
            schwer = [i for i in kandidaten if self.faktor(i) >= 1.0]
            if schwer:
                kandidaten = schwer
        gewichte = [max(0.0, self.faktor(i)) for i in kandidaten]
        if sum(gewichte) <= 0:
            return random.choice(kandidaten)
        return random.choices(kandidaten, weights=gewichte, k=1)[0]

    def remember(self, delta=None):
        """Wort samt seiner (ersetzbaren) Wertung in die Historie legen."""
        self.history.append({"idx": self.idx, "delta": delta})
        if len(self.history) > HISTORY_MAX:
            self.history.pop(0)

    def next_word(self):
        if self.animating or self.blitz:
            return
        self.cancel_auto(redraw=False)
        # Wer ohne neue Wertung weitergeht, behält die alte - sie bleibt
        # über die Historie weiterhin ersetzbar.
        self.remember(self.undo_delta)
        self.undo_delta = None
        neu = self.ziehe_wort()

        def commit():
            self.idx = neu
            self.flips = 0
            self.side = self.start_side
        self.animate(commit)

    def go_back(self):
        """Ein Wort zurück, in der gerade sichtbaren Sprache. Die damals
        abgegebene Wertung wird mitgenommen und kann mit c/v/b ersetzt werden."""
        if not self.history or self.animating or self.blitz:
            return
        self.cancel_auto(redraw=False)
        eintrag = self.history.pop()
        self.undo_delta = eintrag["delta"]

        def commit():
            self.idx = eintrag["idx"]
            self.flips = 0
        self.animate(commit)

    def bewerte(self, taste):
        """c/v/b: Faktor anpassen, Karte kurz aufleuchten lassen, weiter.
        Nach einem Zurück ersetzt die neue Wertung die alte, statt sich zu
        ihr zu addieren."""
        if self.animating or self.blitz:
            return
        self.cancel_auto(redraw=False)
        delta = WERTUNG_DELTA[taste]
        alter_anteil = self.undo_delta or 0.0
        self.setze_faktor(self.idx, self.faktor(self.idx) - alter_anteil + delta)
        self.undo_delta = delta
        self.blitz = WERTUNG_BLITZ[taste]
        self.draw()
        self.root.after(BLITZ_MS, self._blitz_ende)

    def _blitz_ende(self):
        self.blitz = None
        self.next_word()

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
        self.einst["startsprache"] = self.start_side
        speichere_einstellungen(self.einst)
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
        if not self.einst["flip_animation"]:
            commit()
            self.scale = 1.0
            self.draw()
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
        self.einst["thema"] = self.thema
        speichere_einstellungen(self.einst)
        self.imgcache.clear()
        self.menu_neu_aufbauen()
        self.draw()

    def on_key(self, event):
        taste = event.keysym.lower()
        if taste == "d":
            self.toggle_thema()
        elif taste == "u":
            self.update_starten()
        elif taste == "m":
            self.menu_umschalten()
        elif taste in WERTUNG_DELTA:
            self.bewerte(taste)
        elif taste == "left" and self.einst["pfeiltasten"]:
            self.go_back()
        elif taste == "right" and self.einst["pfeiltasten"]:
            self.next_word()

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
            if tag == "close" and hot:
                flaeche, symbol = MAC_ROT, MAC_ROT_SYMBOL
            else:
                flaeche = self.farbe("hover") if hot else self.farbe("bg")
                symbol = self.farbe("fg")
            img = render_button(size, self.br, flaeche,
                                icon_segs(tag, self.br),
                                max(1.5, 1.7 * self.k),
                                symbol, self.farbe("bg"))
            self.imgcache[key] = img
        return img

    # ------------------------------------------------------------ Zeichnen
    def draw(self):
        c, w, h = self.cnv, self.w, self.h
        c.delete("all")
        cx = w / 2.0
        half = max(2.0, (w / 2.0 - 3) * max(self.scale, 0.02))

        flaeche = self.blitz or self.farbe("bg")
        rounded_rect(c, cx - half, 3, cx + half, h - 3, self.corner,
                     fill=hexc(flaeche),
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

        rest = self.scale > 0.999 and not self.blitz
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
                              font=self.font_tiny,
                              fill=hexc(self.farbe("zweit")))

        hinweis = self.update_hinweis()
        if hinweis and rest and not self.countdown_frac:
            self.font_tiny.configure(size=-self.tiny_px)
            c.create_text(cx, h - 14 * self.k, text=hinweis,
                          font=self.font_tiny, fill=hexc(self.farbe("zweit")))

        if self.countdown_frac and rest:
            bw = (w - 2 * (self.pad + self.br + 12 * self.k)) * self.countdown_frac
            hoehe = max(3.0, 4 * self.k)
            if bw > hoehe:
                y = h - 12 * self.k
                rounded_rect(c, cx - bw / 2, y, cx + bw / 2, y + hoehe,
                             hoehe / 2, fill=self.farbe("timer"), width=0)

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

    # ------------------------------------------------------------ Menü
    def menu_umschalten(self):
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()
            self.menu = None
            return
        self._menu_bauen("einstellungen")

    def menu_neu_aufbauen(self):
        """Nach einem Themawechsel mit den neuen Farben neu aufbauen."""
        if self.menu and self.menu.winfo_exists():
            tab = getattr(self, "_menu_tab", "einstellungen")
            self.menu.destroy()
            self._menu_bauen(tab)
        if self.liste_fenster and self.liste_fenster.winfo_exists():
            self.liste_fenster.destroy()
            self.liste_zeigen()

    def _menu_fonts(self):
        familie = self.font_word.actual("family")
        self.font_menu = tkfont.Font(family=familie, size=-int(13 * self.k))
        self.font_menu_fett = tkfont.Font(family=familie, size=-int(13 * self.k),
                                          weight="bold")
        self.font_menu_titel = tkfont.Font(family=familie, size=-int(15 * self.k),
                                           weight="bold")
        self.font_menu_klein = tkfont.Font(family=familie, size=-int(11 * self.k))

    def _rundes_fenster(self, breite, hoehe):
        """Randloses Zusatzfenster im Kartenstil, mit runden Ecken wo möglich."""
        f = tk.Toplevel(self.root)
        f.overrideredirect(True)
        f.attributes("-topmost", True)
        leer = FALLBACK_VOID
        if self.keyed:
            try:
                f.attributes("-transparentcolor", KEY)
                leer = KEY
            except tk.TclError:
                pass
        elif IS_MAC:
            try:
                f.attributes("-transparent", True)
                f.configure(bg="systemTransparent")
                leer = "systemTransparent"
            except tk.TclError:
                pass
        cnv = tk.Canvas(f, bd=0, highlightthickness=0, bg=leer,
                        width=breite, height=hoehe)
        cnv.pack(fill="both", expand=True)
        x = self.root.winfo_x() + self.w + 12
        y = self.root.winfo_y()
        if x + breite > f.winfo_screenwidth():
            x = max(0, self.root.winfo_x() - breite - 12)
        f.geometry("%dx%d+%d+%d" % (breite, hoehe, x, y))
        return f, cnv

    def _panel_grund(self, cnv, breite, hoehe, titel, schliessen):
        """Kartenfläche, Titelzeile und X; liefert die Starthöhe des Inhalts."""
        rounded_rect(cnv, 1, 1, breite - 1, hoehe - 1, self.corner,
                     fill=hexc(self.farbe("bg")),
                     outline=self.farbe("rand"), width=1)
        cnv.create_text(int(18 * self.k), int(22 * self.k), text=titel,
                        anchor="w", font=self.font_menu_titel,
                        fill=hexc(self.farbe("fg")))
        r = int(10 * self.k)
        bx = breite - int(22 * self.k)
        by = int(22 * self.k)
        cnv.create_oval(bx - r, by - r, bx + r, by + r, width=0,
                        fill=hexc(self.farbe("bg")), tags="xknopf")
        a = r * 0.42
        for (x1, y1, x2, y2) in (((-a), (-a), a, a), ((-a), a, a, (-a))):
            cnv.create_line(bx + x1, by + y1, bx + x2, by + y2,
                            fill=hexc(self.farbe("zweit")),
                            width=max(1.4, 1.5 * self.k), capstyle="round",
                            tags="xknopf")
        self._region(cnv, bx - r - 4, by - r - 4, bx + r + 4, by + r + 4,
                     schliessen, "close")
        return int(44 * self.k)

    def _region(self, cnv, x1, y1, x2, y2, cb, name=""):
        cnv._regionen.append((x1, y1, x2, y2, cb, name))

    def _region_klick(self, cnv, event):
        x = cnv.canvasx(event.x)
        y = cnv.canvasy(event.y)
        for x1, y1, x2, y2, cb, _ in reversed(cnv._regionen):
            if x1 <= x <= x2 and y1 <= y <= y2:
                cb()
                return True
        return False

    def _region_ausloesen(self, cnv, name):
        """Für Tests: benannte Region direkt auslösen."""
        for x1, y1, x2, y2, cb, n in cnv._regionen:
            if n == name:
                cb()
                return True
        return False

    def _schalter(self, cnv, x, y, an):
        """Apple-Kippschalter: grüne Pille mit weissem Knauf."""
        b, h = int(36 * self.k), int(21 * self.k)
        farbe = self.farbe("gruen") if an else self.farbe("grau")
        rounded_rect(cnv, x - b, y - h / 2, x, y + h / 2, h / 2,
                     fill=hexc(farbe), width=0)
        r = h / 2 - 2
        kx = x - r - 2 if an else x - b + r + 2
        cnv.create_oval(kx - r, y - r, kx + r, y + r,
                        fill="#ffffff", outline="#00000022" if False else "",
                        width=0)

    def _segmente(self, cnv, x_rechts, y, optionen, aktiv, cb_name, cb):
        """Segmentregler: Pillenhintergrund, aktives Segment als weisse Karte."""
        h = int(22 * self.k)
        pad = int(10 * self.k)
        breiten = [self.font_menu_klein.measure(text) + 2 * pad
                   for _, text in optionen]
        gesamt = sum(breiten)
        x0 = x_rechts - gesamt
        rounded_rect(cnv, x0, y - h / 2, x_rechts, y + h / 2, h / 2,
                     fill=hexc(self.farbe("gruppe")), width=0)
        lauf = x0
        for (wert, text), bw in zip(optionen, breiten):
            if wert == aktiv:
                rounded_rect(cnv, lauf + 2, y - h / 2 + 2,
                             lauf + bw - 2, y + h / 2 - 2, h / 2 - 2,
                             fill=hexc(self.farbe("bg")),
                             outline=self.farbe("rand"), width=1)
            cnv.create_text(lauf + bw / 2, y, text=text,
                            font=(self.font_menu_fett if wert == aktiv
                                  else self.font_menu_klein),
                            fill=hexc(self.farbe("fg")))
            self._region(cnv, lauf, y - h / 2, lauf + bw, y + h / 2,
                         lambda w=wert: cb(w), "%s-%s" % (cb_name, wert))
            lauf += bw

    def _gruppe(self, cnv, x1, y, breite, zeilen, zeichner):
        """Abgerundete Gruppenfläche mit Haarlinien zwischen den Zeilen."""
        zh = int(34 * self.k)
        hoehe = zh * len(zeilen)
        rounded_rect(cnv, x1, y, x1 + breite, y + hoehe, int(10 * self.k),
                     fill=hexc(self.farbe("gruppe")), width=0)
        for n, zeile in enumerate(zeilen):
            zy = y + zh * n + zh / 2
            if n:
                cnv.create_line(x1 + int(14 * self.k), y + zh * n,
                                x1 + breite - int(2 * self.k), y + zh * n,
                                fill=self.farbe("rand"))
            zeichner(zeile, x1, zy, breite)
        return y + hoehe

    def _menu_bauen(self, tab):
        self._menu_tab = tab
        self._menu_fonts()
        breite = int(320 * self.k)
        hoehe = int(392 * self.k)
        m, cnv = self._rundes_fenster(breite, hoehe)
        self.menu = m
        self.menu_cnv = cnv
        cnv._regionen = []

        def zu():
            m.destroy()
            self.menu = None
        cnv.bind("<Button-1>", lambda e: self._menu_klick(e))
        m.bind("<Key>", lambda e: (zu() if e.keysym.lower() in ("m", "escape")
                                   else None))
        self._menu_zeichnen()

    def _panel_klick(self, fenster, cnv, event):
        if self._region_klick(cnv, event):
            return
        # freie Fläche zieht das Fenster
        start = (event.x_root, event.y_root, fenster.winfo_x(), fenster.winfo_y())
        def zieh(e):
            fenster.geometry("+%d+%d" % (start[2] + e.x_root - start[0],
                                         start[3] + e.y_root - start[1]))
        cnv.bind("<B1-Motion>", zieh)
        cnv.bind("<ButtonRelease-1>",
                 lambda e: (cnv.unbind("<B1-Motion>"),
                            cnv.unbind("<ButtonRelease-1>")))

    def _menu_klick(self, event):
        self._panel_klick(self.menu, self.menu_cnv, event)

    def _menu_zeichnen(self):
        cnv = self.menu_cnv
        cnv.delete("all")
        cnv._regionen = []
        breite = int(320 * self.k)
        hoehe = int(392 * self.k)
        rand = int(16 * self.k)
        innen = breite - 2 * rand

        def zu():
            self.menu.destroy()
            self.menu = None
        y = self._panel_grund(cnv, breite, hoehe, "Voci", zu)

        # Tab-Umschalter als Segmentregler über die volle Breite
        h = int(26 * self.k)
        mitte_y = y + h / 2
        rounded_rect(cnv, rand, y, rand + innen, y + h, h / 2,
                     fill=hexc(self.farbe("gruppe")), width=0)
        haelfte = innen / 2
        for n, (wert, text) in enumerate((("einstellungen", "Einstellungen"),
                                          ("sets", "Voci-Sets"))):
            x0 = rand + haelfte * n
            if wert == self._menu_tab:
                rounded_rect(cnv, x0 + 2, y + 2, x0 + haelfte - 2, y + h - 2,
                             h / 2 - 2, fill=hexc(self.farbe("bg")),
                             outline=self.farbe("rand"), width=1)
            cnv.create_text(x0 + haelfte / 2, mitte_y, text=text,
                            font=(self.font_menu_fett if wert == self._menu_tab
                                  else self.font_menu),
                            fill=hexc(self.farbe("fg")))
            self._region(cnv, x0, y, x0 + haelfte, y + h,
                         lambda w=wert: self._tab_wechseln(w), "tab-" + wert)
        y += h + int(14 * self.k)

        if self._menu_tab == "einstellungen":
            self._tab_einstellungen(cnv, rand, y, innen)
        else:
            self._tab_sets(cnv, rand, y, innen)

    def _tab_wechseln(self, tab):
        self._menu_tab = tab
        self._menu_zeichnen()

    def _einstellung_kippen(self, schluessel, wirkung=None):
        self.einst[schluessel] = not self.einst[schluessel]
        speichere_einstellungen(self.einst)
        if wirkung:
            wirkung(self.einst[schluessel])
        self._menu_zeichnen()

    def _tab_einstellungen(self, cnv, x, y, innen):
        tx = x + int(14 * self.k)

        def schalterzeile(text, wert, cb, name):
            def zeichne(_, gx, gy, gb):
                cnv.create_text(tx, gy, text=text, anchor="w",
                                font=self.font_menu, fill=hexc(self.farbe("fg")))
                self._schalter(cnv, gx + gb - int(12 * self.k), gy, wert)
                self._region(cnv, gx, gy - 17 * self.k, gx + gb, gy + 17 * self.k,
                             cb, name)
            return zeichne

        zeilen1 = [
            schalterzeile("Dark Mode", self.thema == "dunkel",
                          self.toggle_thema, "dark"),
            schalterzeile("Immer im Vordergrund", self.einst["immer_vorne"],
                          lambda: self._einstellung_kippen(
                              "immer_vorne",
                              lambda an: self.root.attributes("-topmost", bool(an))),
                          "vorne"),
            schalterzeile("Pfeiltasten-Navigation", self.einst["pfeiltasten"],
                          lambda: self._einstellung_kippen("pfeiltasten"),
                          "pfeile"),
            schalterzeile("Flip-Animation", self.einst["flip_animation"],
                          lambda: self._einstellung_kippen("flip_animation"),
                          "flip"),
        ]
        y = self._gruppe(cnv, x, y, innen, zeilen1,
                         lambda z, gx, gy, gb: z(z, gx, gy, gb)) + int(12 * self.k)

        def auto_zeile(_, gx, gy, gb):
            cnv.create_text(tx, gy, text="Auto-Weiter", anchor="w",
                            font=self.font_menu, fill=hexc(self.farbe("fg")))
            self._schalter(cnv, gx + gb - int(12 * self.k), gy,
                           self.einst["auto_weiter"])
            self._region(cnv, gx, gy - 17 * self.k, gx + gb, gy + 17 * self.k,
                         lambda: self._einstellung_kippen("auto_weiter"), "auto")

        def dauer_zeile(_, gx, gy, gb):
            cnv.create_text(tx, gy, text="Wartezeit", anchor="w",
                            font=self.font_menu, fill=hexc(self.farbe("fg")))
            def setze(w):
                self.einst["auto_dauer"] = w
                speichere_einstellungen(self.einst)
                self._menu_zeichnen()
            self._segmente(cnv, gx + gb - int(12 * self.k), gy,
                           [(3, "3 s"), (5, "5 s"), (10, "10 s")],
                           int(self.einst["auto_dauer"]), "dauer", setze)

        def sprache_zeile(_, gx, gy, gb):
            cnv.create_text(tx, gy, text="Startsprache", anchor="w",
                            font=self.font_menu, fill=hexc(self.farbe("fg")))
            def setze(w):
                if w != self.start_side:
                    self.toggle_start()
                self._menu_zeichnen()
            self._segmente(cnv, gx + gb - int(12 * self.k), gy,
                           [("fr", "FR"), ("de", "DE")],
                           self.start_side, "sprache", setze)

        y = self._gruppe(cnv, x, y, innen, [auto_zeile, dauer_zeile, sprache_zeile],
                         lambda z, gx, gy, gb: z(z, gx, gy, gb)) + int(14 * self.k)

        cnv.create_text(x + innen / 2, y + int(6 * self.k),
                        text="Bewerten:  c kann ich nicht  ·  v neutral  ·  b kann ich",
                        font=self.font_menu_klein,
                        fill=hexc(self.farbe("zweit")))

    def _tab_sets(self, cnv, x, y, innen):
        tx = x + int(14 * self.k)

        def set_zeile(satz, gx, gy, gb):
            aktiv = satz["id"] in self.einst["sets"]
            # Haken-Kreis in Systemblau
            r = int(9 * self.k)
            hx = tx + r
            if aktiv:
                cnv.create_oval(hx - r, gy - r, hx + r, gy + r, width=0,
                                fill=hexc(self.farbe("akzent")))
                w = max(1.5, 1.7 * self.k)
                cnv.create_line(hx - r * 0.45, gy + r * 0.05,
                                hx - r * 0.1, gy + r * 0.42,
                                hx + r * 0.5, gy - r * 0.38,
                                fill="#ffffff", width=w, capstyle="round",
                                joinstyle="round")
            else:
                cnv.create_oval(hx - r, gy - r, hx + r, gy + r,
                                outline=hexc(self.farbe("grau")), width=2)
            cnv.create_text(hx + r + int(10 * self.k), gy, anchor="w",
                            text=satz["name"], font=self.font_menu,
                            fill=hexc(self.farbe("fg")))
            cnv.create_text(hx + r + int(10 * self.k) + self.font_menu.measure(
                                satz["name"]) + int(8 * self.k), gy, anchor="w",
                            text="%d Wörter" % len(satz["indizes"]),
                            font=self.font_menu_klein,
                            fill=hexc(self.farbe("zweit")))
            def kippen(sid=satz["id"]):
                gewaehlt = set(self.einst["sets"])
                if sid in gewaehlt:
                    gewaehlt.discard(sid)
                if not gewaehlt or satz["id"] not in self.einst["sets"]:
                    gewaehlt.add(sid)
                self.einst["sets"] = sorted(gewaehlt)
                speichere_einstellungen(self.einst)
                self._menu_zeichnen()
            self._region(cnv, gx, gy - 17 * self.k, gx + gb - int(40 * self.k),
                         gy + 17 * self.k, kippen, "set-" + satz["id"])
            px = gx + gb - int(22 * self.k)
            cnv.create_text(px, gy, text="⋯", font=self.font_menu_fett,
                            fill=hexc(self.farbe("zweit")))
            self._region(cnv, px - 14, gy - 14, px + 14, gy + 14,
                         lambda: self._set_optionen(px, gy), "punkte")

        self._gruppe(cnv, x, y, innen, self.sets,
                     lambda z, gx, gy, gb: set_zeile(z, gx, gy, gb))

    def _set_optionen(self, px, py):
        popup = tk.Menu(self.menu, tearoff=0,
                        bg=hexc(self.farbe("bg")), fg=hexc(self.farbe("fg")),
                        activebackground=hexc(self.farbe("hover")),
                        activeforeground=hexc(self.farbe("fg")),
                        font=self.font_menu, relief="flat", bd=1)
        schwer = tk.BooleanVar(master=self.menu,
                               value=self.einst["schwere_modus"])
        def schwer_um():
            self.einst["schwere_modus"] = not self.einst["schwere_modus"]
            speichere_einstellungen(self.einst)
        popup.add_checkbutton(label="Schwere Wörter üben (Faktor ≥ 1)",
                              variable=schwer, command=schwer_um)
        popup.add_command(label="Wörterliste anzeigen", command=self.liste_zeigen)
        popup.tk_popup(self.menu.winfo_rootx() + int(px),
                       self.menu.winfo_rooty() + int(py))

    # ------------------------------------------------------------ Wörterliste
    def liste_zeigen(self):
        if self.liste_fenster and self.liste_fenster.winfo_exists():
            self.liste_fenster.lift()
            return
        self._menu_fonts()
        self.liste_sortierung = getattr(self, "liste_sortierung", "az")
        breite = int(360 * self.k)
        hoehe = int(430 * self.k)
        f, cnv = self._rundes_fenster(breite, hoehe)
        self.liste_fenster = f
        cnv._regionen = []
        self.liste_aussen = cnv

        def zu():
            f.destroy()
            self.liste_fenster = None
        y = self._panel_grund(cnv, breite, hoehe, "Wörterliste", zu)
        cnv.bind("<Button-1>", lambda e: self._panel_klick(f, cnv, e))
        f.bind("<Key>", lambda e: zu() if e.keysym == "Escape" else None)

        rand = int(16 * self.k)
        innen = breite - 2 * rand

        def sortiere(w):
            self.liste_sortierung = w
            zu()
            self.liste_zeigen()
        self._segmente(cnv, rand + int(150 * self.k), y + int(11 * self.k),
                       [("az", "A–Z"), ("wertung", "Wertung")],
                       self.liste_sortierung, "sortier", sortiere)
        # Zurücksetzen als roter Textknopf (Apple-Stil für Löschendes)
        rx = breite - rand
        cnv.create_text(rx, y + int(11 * self.k), text="Alle zurücksetzen",
                        anchor="e", font=self.font_menu_klein,
                        fill=hexc((255, 105, 97)))
        tb = self.font_menu_klein.measure("Alle zurücksetzen")
        self._region(cnv, rx - tb, y, rx, y + int(22 * self.k),
                     self._liste_alles_zuruecksetzen, "reset-alle")
        y += int(30 * self.k)

        # Innenliste: eigener Canvas im Panel, rollt mit dem Mausrad
        rumpf_hoehe = hoehe - y - int(14 * self.k)
        rows = tk.Canvas(f, bd=0, highlightthickness=0,
                         bg=hexc(self.farbe("bg")),
                         width=innen, height=rumpf_hoehe)
        cnv.create_window(rand, y, anchor="nw", window=rows)
        self.liste_canvas = rows
        rows.bind("<Button-1>", self._liste_klick)
        for ziel in (rows, cnv):
            ziel.bind("<MouseWheel>", lambda e: rows.yview_scroll(
                -1 if e.delta > 0 else 1, "units"))
            ziel.bind("<Button-4>", lambda e: rows.yview_scroll(-1, "units"))
            ziel.bind("<Button-5>", lambda e: rows.yview_scroll(1, "units"))
        self.liste_breite = innen
        self._liste_fuellen()

    def _liste_sortieren(self, wie):
        self.liste_sortierung = wie
        f = self.liste_fenster
        if f and f.winfo_exists():
            f.destroy()
            self.liste_fenster = None
        self.liste_zeigen()

    def _liste_reihenfolge(self):
        indizes = list(self.aktive_indizes())
        if self.liste_sortierung == "wertung":
            indizes.sort(key=lambda i: (-wertung_prozent(self.faktor(i)),
                                        self.vocab[i]["fr"].lower()))
        else:
            indizes.sort(key=lambda i: self.vocab[i]["fr"].lower())
        return indizes

    def _liste_fuellen(self):
        cnv = self.liste_canvas
        cnv.delete("all")
        zh = int(30 * self.k)
        breite = self.liste_breite
        self.liste_zeilen = self._liste_reihenfolge()
        for reihe, i in enumerate(self.liste_zeilen):
            y = reihe * zh
            mitte = y + zh / 2
            prozent = wertung_prozent(self.faktor(i))
            r = int(4.5 * self.k)
            mx = breite - int(78 * self.k)
            if reihe:
                cnv.create_line(0, y, breite, y, fill=self.farbe("rand"))
            text = "%s – %s" % (self.vocab[i]["fr"], self.vocab[i]["de"])
            frei = mx - r - int(12 * self.k)
            if self.font_menu.measure(text) > frei:
                while text and self.font_menu.measure(text + "…") > frei:
                    text = text[:-1]
                text += "…"
            cnv.create_text(int(2 * self.k), mitte, text=text, anchor="w",
                            font=self.font_menu, fill=hexc(self.farbe("fg")))
            cnv.create_oval(mx - r, mitte - r, mx + r, mitte + r,
                            fill=hexc(wertung_farbe(prozent)), width=0)
            cnv.create_text(mx + int(12 * self.k), mitte, text="%d%%" % prozent,
                            anchor="w", font=self.font_menu_klein,
                            fill=hexc(self.farbe("zweit")))
            cnv.create_text(breite - int(6 * self.k), mitte, text="↺",
                            anchor="e", font=self.font_menu,
                            fill=hexc(self.farbe("zweit")),
                            tags=("reset", "reset-%d" % i))
        cnv.configure(scrollregion=(0, 0, breite, len(self.liste_zeilen) * zh))

    def _liste_klick(self, event):
        cnv = self.liste_canvas
        x = cnv.canvasx(event.x)
        y = cnv.canvasy(event.y)
        for element in cnv.find_overlapping(x - 8, y - 8, x + 8, y + 8):
            for tag in cnv.gettags(element):
                if tag.startswith("reset-"):
                    self.setze_faktor(int(tag.split("-")[1]), 1.0)
                    self._liste_fuellen()
                    return

    def _liste_alles_zuruecksetzen(self):
        self.faktoren.clear()
        speichere_faktoren(self.faktoren)
        self._liste_fuellen()

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
