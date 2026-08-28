# -*- coding: utf-8 -*-
"""
Voci – Vokabel-Flashcard, immer im Vordergrund. Gebaut auf Qt (PySide6).
Läuft unter Windows, macOS und Linux.

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

Wenn das Programm den Fokus verliert und das aktuelle Wort schon geflippt
wurde, kommt nach 5 Sekunden automatisch das nächste Wort (ein feiner Balken
unten zählt runter) – ausser man tabbt vorher zurück.
"""

import base64
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
import urllib.error
import urllib.request
import zipfile

try:
    from PySide6.QtCore import (Qt, QTimer, QRectF, QPointF, QVariantAnimation,
                                QEasingCurve, QSize, QEvent, QObject)
    from PySide6.QtGui import (QAction, QColor, QFont, QFontMetrics, QGuiApplication,
                               QIcon, QPainter, QPainterPath, QPen, QPixmap, QCursor,
                               QTransform)
    from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame,
                                   QHBoxLayout, QLabel, QMenu, QPushButton,
                                   QScrollArea, QVBoxLayout, QWidget)
except ImportError:                                  # Python-Fassung ohne PySide6
    sys.stderr.write(
        "Voci braucht PySide6. Einmalig installieren mit:\n"
        "    pip install PySide6\n")
    try:
        import tkinter.messagebox
        tkinter.messagebox.showinfo(
            "Voci", "Voci braucht PySide6.\n\nEinmalig installieren mit:\n"
                    "pip install PySide6")
    except Exception:
        pass
    sys.exit(1)

EINGEBAUTE_VOCAB = json.loads(r'''[{"fr": "Se présenter", "de": "sich jemandem vorstellen"}, {"fr": "la présentation", "de": "die Vorstellung von etwas oder jemandem"}, {"fr": "caractériser", "de": "charakterisieren"}, {"fr": "le caractère", "de": "der Charakter"}, {"fr": "enchanté/enchantée (adj.)", "de": "Sehr erfreut!"}, {"fr": "une adresse", "de": "eine Adresse"}, {"fr": "s’adresser à", "de": "sich wenden/richten an"}, {"fr": "mémoriser", "de": "sich einprägen/sich merken"}, {"fr": "la mémoire", "de": "das Gedächtnis/die Erinnerung"}, {"fr": "la date de naissance", "de": "das Geburtsdatum"}, {"fr": "la naissance", "de": "die Geburt"}, {"fr": "naître", "de": "geboren werden"}, {"fr": "Je suis né/née le 15 août 1994", "de": "Ich bin am 15. August 1994 geboren"}, {"fr": "le mois/les mois", "de": "der Monat/die Monate"}, {"fr": "janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre, décembre", "de": "Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"}, {"fr": "en janvier, en août, en juin", "de": "im Januar, im August, im Juni"}, {"fr": "les jours (le jour) de la semaine :", "de": "die Tage der Woche:"}, {"fr": "lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche", "de": "Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag"}, {"fr": "le lundi, le samedi, le dimanche", "de": "am/immer am Montag, am Samstag, am Sonntag"}, {"fr": "à ce soir – à demain – à samedi", "de": "bis heute Abend - bis morgen – bis am Samstag"}, {"fr": "le matin – ce matin", "de": "der/am Morgen – heute Morgen"}, {"fr": "l’après-midi, (m.) – cet après-midi", "de": "der/am Nachmittag – heute Nachmittag"}, {"fr": "le soir – ce soir", "de": "der/am Abend – heute Abend"}, {"fr": "les quatre saisons, (f.):", "de": "die 4 Jahreszeiten:"}, {"fr": "l’été (m.), l’automne(m.), l’hiver (m.), le printemps", "de": "der Sommer, der Herbst, der Winter, der Frühling"}, {"fr": "en été, en automne, en hiver, au printemps", "de": "im Sommer, im Herbst, im Winter, im Frühling"}, {"fr": "un état civil", "de": "ein Zivilstand"}, {"fr": "marié/mariée (adj.)", "de": "verheiratet"}, {"fr": "célibataire (adj.)", "de": "ledig"}, {"fr": "divorcé/divorcée (adj.)", "de": "geschieden"}, {"fr": "veuf/veuve (adj.)", "de": "verwitwet"}, {"fr": "la langue maternelle", "de": "die Muttersprache"}, {"fr": "la langue étrangère", "de": "die Fremdsprache"}, {"fr": "apprendre une langue", "de": "eine Sprache lernen"}, {"fr": "un enregistrement", "de": "eine (Radio-/Musik...)-Aufnahme"}, {"fr": "enregistrer", "de": "(Musik,…) aufnehmen"}, {"fr": "une émission", "de": "eine Fernsehsendung"}, {"fr": "regarder la télévision", "de": "fernsehen"}, {"fr": "écouter la radio", "de": "Radio hören"}, {"fr": "être d’origine italienne/suisse/allemande", "de": "ital./schweiz./deutscher Herkunft sein"}, {"fr": "traduire : je traduis", "de": "übersetzen: ich übersetze"}, {"fr": "la traduction", "de": "die Übersetzung"}, {"fr": "le portable", "de": "das Handy"}, {"fr": "téléphoner à quelqu’un - appeler quelqu‘un", "de": "jemandem telefonieren/jem. anrufen"}, {"fr": "se décider", "de": "sich entscheiden"}, {"fr": "la décision", "de": "die Entscheidung"}, {"fr": "se reposer", "de": "sich ausruhen, sich erholen"}, {"fr": "s’inscrire", "de": "sich einschreiben"}, {"fr": "répondre", "de": "antworten"}, {"fr": "la réponse", "de": "die Antwort"}, {"fr": "cocher la réponse correcte", "de": "die richtige Antwort ankreuzen"}, {"fr": "faire des études (f.)", "de": "ein Studium machen"}, {"fr": "aller en boîte", "de": "in die Disco gehen"}, {"fr": "choisir", "de": "auswählen"}, {"fr": "le choix", "de": "(die Aus)-Wahl"}, {"fr": "le numéro de portable", "de": "die Handynummer"}, {"fr": "demander quelque chose à quelqu’un", "de": "jemanden um etwas bitten"}, {"fr": "participer à", "de": "teilnehmen an"}, {"fr": "la participation", "de": "die Teilnahme"}, {"fr": "poser une question", "de": "eine Frage stellen"}, {"fr": "s‘amuser", "de": "sich amüsieren"}, {"fr": "se coucher, aller au lit", "de": "ins Bett gehen"}, {"fr": "se dépêcher", "de": "sich beeilen"}, {"fr": "se doucher", "de": "sich duschen"}, {"fr": "s’ énerver", "de": "sich aufregen"}, {"fr": "s ’habiller", "de": "sich anziehen"}, {"fr": "se maquiller", "de": "sich schminken"}, {"fr": "s’occuper de", "de": "sich beschäftigen mit, sich kümmern um"}, {"fr": "se réveiller", "de": "aufwachen"}, {"fr": "à mon avis/selon moi", "de": "meiner Meinung nach"}, {"fr": "par contre", "de": "hingegen"}, {"fr": "avoir raison", "de": "Recht haben"}, {"fr": "avoir tort", "de": "unrecht haben"}, {"fr": "exagérer", "de": "übertreiben"}, {"fr": "trouver", "de": "finden"}, {"fr": "un emploi", "de": "eine (Arbeits-)Stelle"}, {"fr": "une erreur/une faute", "de": "ein Fehler"}, {"fr": "un projet d’avenir", "de": "ein Zukunftsplan/ein Projekt für die Zukunft"}, {"fr": "rendre visite à quelqu’un", "de": "jemanden besuchen"}, {"fr": "visiter un musée/une ville", "de": "ein Museum/eine Stadt besichtigen"}, {"fr": "fréquenter/faire l’école de Maturité Professionnelle", "de": "die BMS besuchen"}, {"fr": "la maturité professionnelle", "de": "die BM/Berufsmatura"}, {"fr": "le groupe", "de": "die Gruppe"}, {"fr": "parler anglais-espagnol-français-italien-japonais-polonais-russe-turc-allemand", "de": "englisch-spanisch-französisch-italienisch-japanisch-polnisch-russisch-türkisch-deutsch sprechen"}, {"fr": "avoir besoin de (j’ai besoin d’une langue étrangère)", "de": "brauchen (ich brauche eine Fremdsprache)"}, {"fr": "savoir parler français", "de": "französisch sprechen können"}, {"fr": "savoir", "de": "wissen, können (weil gelernt!)"}, {"fr": "connaître", "de": "kennen, kennenlernen"}, {"fr": "pouvoir", "de": "können, dürfen"}, {"fr": "l’Angleterre (f.)", "de": "England"}, {"fr": "un Anglais/une Anglaise", "de": "ein Engländer/eine Engländerin"}, {"fr": "anglais,e (adj.)", "de": "englisch"}, {"fr": "l‘ Espagne (f.)", "de": "Spanien"}, {"fr": "un Espagnol/une Espagnole", "de": "ein Spanier/eine Spanierin"}, {"fr": "espagnol,e (adj.)", "de": "spanisch"}, {"fr": "la France", "de": "Frankreich"}, {"fr": "un Français/une Française", "de": "ein Franzose/eine Französin"}, {"fr": "français,e (adj.)", "de": "französisch"}, {"fr": "l’Italie (f.)", "de": "Italien"}, {"fr": "un Italien/une Italienne", "de": "ein Italiener/eine Italienerin"}, {"fr": "italien/italienne (adj.)", "de": "italienisch"}, {"fr": "le Japon", "de": "Japan"}, {"fr": "un Japonais/une Japonaise", "de": "ein Japaner/eine Japanerin"}, {"fr": "japonais,e (adj.)", "de": "japanisch"}, {"fr": "la Russie", "de": "Russland"}, {"fr": "un Russe/une Russe", "de": "ein Russe/eine Russin"}, {"fr": "russe m,f (adj.)", "de": "russisch"}, {"fr": "l’Allemagne (f.)", "de": "Deutschland"}, {"fr": "un Allemand/une Allemande", "de": "ein Deutscher/eine Deutsche"}, {"fr": "allemand,e (adj.)", "de": "deutsch"}, {"fr": "la Croatie", "de": "Kroatien"}, {"fr": "croate (adj.)", "de": "kroatisch"}, {"fr": "la Serbie", "de": "Serbien"}, {"fr": "serbe (adj.)", "de": "serbisch"}, {"fr": "maîtriser quelque chose", "de": "etwas beherrschen"}, {"fr": "maîtriser une langue/une situation", "de": "eine Sprache/eine Situation beherrschen"}, {"fr": "utiliser qc comme", "de": "etwas benutzen als"}, {"fr": "apprendre qc", "de": "etw. lernen"}, {"fr": "apprendre à faire qc", "de": "lernen etw. zu machen"}, {"fr": "un apprentissage", "de": "eine Lehre/ein Lernen"}, {"fr": "un apprenti/une apprentie", "de": "ein Lehrling, ein Lernender/eine Lernende"}, {"fr": "améliorer qc", "de": "etw. verbessern"}, {"fr": "améliorer la prononciation", "de": "die Aussprache verbessern"}, {"fr": "accompagner", "de": "begleiten"}, {"fr": "être utile m,f (adj.)", "de": "nützlich sein"}, {"fr": "riche m,f (adj.)", "de": "reich"}, {"fr": "la richesse", "de": "der Reichtum"}, {"fr": "construire une phrase/une maison", "de": "einen Satz bilden, ein Haus bauen"}, {"fr": "disponible m,f (adj.)", "de": "verfügbar"}, {"fr": "partout", "de": "überall"}, {"fr": "nulle part", "de": "nirgends, nirgendwo"}, {"fr": "accéder à", "de": "Zugang erlangen"}, {"fr": "un accès (à l’internet)", "de": "ein (Internet-)Zugang"}, {"fr": "apprendre par coeur", "de": "auswendig lernen"}, {"fr": "un oeil-les yeux (pl.m)", "de": "ein Auge-die Augen"}, {"fr": "la vue", "de": "der Blick/das Sehen"}, {"fr": "voir", "de": "sehen"}, {"fr": "regarder", "de": "anschauen/schauen"}, {"fr": "le son", "de": "der Ton/Klang"}, {"fr": "sonner", "de": "tönen/läuten/klingeln"}, {"fr": "une oreille", "de": "ein Ohr"}, {"fr": "écouter", "de": "(zu-)hören"}, {"fr": "entendre", "de": "hören"}, {"fr": "une odeur", "de": "ein Geruch"}, {"fr": "un goût", "de": "ein Geschmack"}, {"fr": "ensemble", "de": "gemeinsam"}, {"fr": "parfois/de temps en temps", "de": "bisweilen/ hie und da,/ ab und zu"}, {"fr": "entier/entière (adj.)", "de": "ganz, gesamt"}, {"fr": "le lait entier", "de": "die Vollmilch"}, {"fr": "le monde entier", "de": "die ganze Welt"}, {"fr": "tout le monde (3. pers.sg.!)", "de": "jedermann; alle"}, {"fr": "quand, comment, où, pourquoi, combien, quel(s) quelle(s)", "de": "wann, wie, wo, warum, wieviel, welche"}, {"fr": "les aliments (m. pl.)", "de": "die Nahrungsmittel"}, {"fr": "le légume", "de": "das Gemüse"}, {"fr": "l’épinard (m.)", "de": "der Spinat"}, {"fr": "l’ail (m.)", "de": "der Knoblauch"}, {"fr": "la courgette", "de": "die Zucchetti"}, {"fr": "une asperge", "de": "eine Spargel"}, {"fr": "le chou", "de": "der Kohl"}, {"fr": "la pomme de terre", "de": "die Kartoffel"}, {"fr": "la tomate", "de": "die Tomate"}, {"fr": "la carotte", "de": "die Karotte"}, {"fr": "le champignon", "de": "der Pilz"}, {"fr": "l’oignon (m.)", "de": "die Zwiebel"}, {"fr": "le produit laitier", "de": "das Milchprodukt"}, {"fr": "le beurre", "de": "die Butter"}, {"fr": "la crème", "de": "der Rahm"}, {"fr": "le yaourt", "de": "das Joghurt"}, {"fr": "le fromage (la fondue, la raclette)", "de": "der Käse (das Fondue, das Raclette)"}, {"fr": "les fruits (m.pl.)", "de": "die Früchte"}, {"fr": "la fraise", "de": "die Erdbeere"}, {"fr": "la framboise", "de": "die Himbeere"}, {"fr": "la pomme", "de": "der Apfel"}, {"fr": "la poire", "de": "die Birne"}, {"fr": "le raisin", "de": "die Traube"}, {"fr": "l’abricot (m.)", "de": "die Aprikose"}, {"fr": "une orange", "de": "eine Orange"}, {"fr": "un citron", "de": "die Zitrone"}, {"fr": "un melon", "de": "eine Melone"}, {"fr": "une banane", "de": "eine Banane"}, {"fr": "un ananas", "de": "eine Ananas"}, {"fr": "une prune", "de": "eine Zwetschge"}, {"fr": "le pain", "de": "das Brot"}, {"fr": "le croissant", "de": "das Gipfeli"}, {"fr": "la baguette", "de": "das Stangenbrot, das Baguette"}, {"fr": "une tartine (de miel)", "de": "ein Brot mit Aufstrich (Honigbrot)"}, {"fr": "le muesli", "de": "das Müsli"}, {"fr": "cru, crue (adj.)", "de": "roh"}, {"fr": "cuit,e (adj.)", "de": "gekocht"}, {"fr": "le miel", "de": "der Honig"}, {"fr": "un œuf", "de": "ein Ei"}, {"fr": "la viande (la viande séchée)", "de": "das Fleisch (das Trockenfleisch)"}, {"fr": "la confiture", "de": "die Marmelade, die Konfitüre"}, {"fr": "le petit déjeuner, le déjeuner, le dîner", "de": "das Frühstück, das Mittagessen, das Abendessen"}, {"fr": "un repas", "de": "das Essen, die Mahlzeit"}, {"fr": "une boisson", "de": "ein Getränk"}, {"fr": "le plat (le plat préféré)", "de": "das Gericht (das Lieblingsessen)"}, {"fr": "un escargot", "de": "eine Schnecke"}, {"fr": "le saumon", "de": "der Lachs"}, {"fr": "le poireau", "de": "der Lauch"}, {"fr": "un filet de bœuf", "de": "ein Rinderfilet"}, {"fr": "faire un barbecue / une grillade", "de": "grillen"}, {"fr": "une épice, épicer", "de": "ein Gewürz, würzen"}, {"fr": "pimenté,e (adj.)", "de": "pikant, scharf (kulinarisch)"}, {"fr": "la volaille", "de": "das Geflügel"}, {"fr": "le poisson", "de": "der Fisch"}, {"fr": "le veau", "de": "das Kalb"}, {"fr": "la tarte", "de": "flacher Obstkuchen"}, {"fr": "le gâteau", "de": "der Kuchen"}, {"fr": "une carafe (d’eau)", "de": "eine Karaffe (Wasser)"}, {"fr": "oublier", "de": "vergessen"}, {"fr": "s’intéresser à", "de": "sich interessieren für"}, {"fr": "je m’intéresse aux langues", "de": "ich interessiere mich für Sprachen"}, {"fr": "bon/bonne (adj.)", "de": "gut, gütig"}, {"fr": "gentil/gentille (adj.)", "de": "nett, freundlich"}, {"fr": "méchant/méchante (adj.)", "de": "böse, gemein, boshaft"}, {"fr": "aimable (adj.)", "de": "liebenswürdig, freundlich"}, {"fr": "cher/chère (adj.)", "de": "lieb, teuer"}, {"fr": "être fier/fière de", "de": "stolz sein auf"}, {"fr": "paresseux/paresseuse (adj.)", "de": "faul"}, {"fr": "patient,e(adj.)", "de": "geduldig"}, {"fr": "impatient,e (adj.)", "de": "ungeduldig"}, {"fr": "la patience", "de": "die Geduld"}, {"fr": "prudent,e (adj.)", "de": "vorsichtig"}, {"fr": "adroit,e (adj.)", "de": "geschickt"}, {"fr": "aimer", "de": "lieben, mögen, gerne tun"}, {"fr": "il aime danser", "de": "er tanzt gerne"}, {"fr": "l’amour m.", "de": "die Liebe"}, {"fr": "être content/contente de", "de": "zufrieden sein mit"}, {"fr": "heureux/heureuse (adj.)", "de": "glücklich"}, {"fr": "malheureux-malheureuse (adj.", "de": "unglücklich"}, {"fr": "la joie", "de": "die Freude, das Vergnügen"}, {"fr": "le plaisir", "de": "das Vergnügen, die Freude"}, {"fr": "agréable m,f (adj.)", "de": "angenehm"}, {"fr": "désagréable m,f (adj.)", "de": "unangenehm"}, {"fr": "avoir envie de", "de": "Lust haben auf"}, {"fr": "l’espoir (m.)", "de": "die Hoffnung"}, {"fr": "espérer", "de": "hoffen"}, {"fr": "la surprise", "de": "die Überraschung"}, {"fr": "surprendre", "de": "überraschen"}, {"fr": "triste m,f (adj.)", "de": "traurig"}, {"fr": "regretter", "de": "bedauern"}, {"fr": "détester, haïr", "de": "verabscheuen, hassen"}]''')
VERSION = "dev"

# Fenstersymbol (Trikolore) als eingebettetes PNG.
ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAEbklEQVR4nO2bT2gcVRzHv7/fm5ndpGlim6QEogfRgxikIInEgiJWaVMlImVDb71II1QEwVOKBxFz8iJYSAseUgRrlkBTS2qxmoqXgLmUoigULybSNn/dJLs7b+a9n4fd1QhpspjUZzbzYeeyvH3zfZ99w8xhvoR/QsAIA31GRPjpo5+9encpPl4I4+4osg8LpB6Q0rB1UIoQ/xHiwlAPXn/5UURG4Kn1x1aNMYBS0F9PYOXtAVBTY+m7DWAgT743Tan0pOxrGP147PMr7xNZARQAS6VFVBZcQQggMCAdh4dfm16Iz6zmbZc2BNgYgFnzs/UhRZClIkYu9CLT8xiMBRRvYfEAYC3AjOjqdeTeeAf0UNPmAgjwiBAwI1IKJp36odCy/8O28S/GpLzmigReu3iRCdX27KdDv/wulxZztktHoUCKBhQLqDx6g4O5fPYyIpsYq4byHFJZWRWHJUIIyLI1pqC1pJZXu5pn7l6ae/6VoRsiqjwflQUIAX0sMqHanrk9emfB79fFlRgILYgIIAXQFvfxfw8BRCDFRLQMsbliIW5eXO5/6lDP6A2ZUABYAGJksszImvbu22dnc6leq3MaTB5AW928/xsYYDB781rr5pVC7xPPfXSWAINMhhnZPvPkS8PHZpf9U1bnIjAFrgM/KIgpWNRh1LqSP3XvaN8xymYNT01N+b/dKwxGYSTg2vnX74dl4jgMBXPzg1NT53w+OfDjkbxWByGhoHSbqGkIUCtipV5HB9ve+/YIzy3oE1FMAtrsJldDEMQ3Vvxc7oRX1LYbVqj0CLBbINbWEIW624uNbQcsduKt7t9CAMUiIGPbGaD0Ltr8f2EFACS9i7b9+iQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXJAJcB3BNIsB1ANckAlwHcE0iwHUA1yQCXAdwTSLAdQDXMCDF+3SgappSs4eK7CmeKb0lvx0Fn52BAOIRQRTPcDrgSbAnKL0xvUsQG7ASSQWT3LI/uOh7QpBddCEIKFJMUWPjRR4e7LhWH5iboBQB2LiQVwMIYBqIKR/4N+988OI17uzsjB45UDfgp3yClZq/DNiK9VIpQkvzQGdnf8TIjKifrp8cb90bneeg0YcV7Trkg0Ks6H1Byp9tqD9/4KuRcclkFCObsRYZNTP5+OnWxvAyB40BrMRA7ewGC1hYGzcHQTDfUHf55+/fPS2AQjZrPYAEEEtEEJk43n7o10/mlhr6tY4ACQUEC4B3WqVGSh8rAt5LzCpdx/NNe87d+u7KWy8QGaDUH/ZKw0kAISIyDLzZcXj46vQCn1nNp7q0IVVtedoSKl2U0qzb4aw8B6E8d+XYgHJ5mgJWKlIK4drydDlUpTztrTmTACCLEXXrm74xEfny7/q8dEcRVVefjzwwCawxiI0A21Sfjwmwe+pA9elN2+MA8pHvTcdV1Of/BKK/3Wv1D3rrAAAAAElFTkSuQmCC"

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

# ---------------------------------------------------------------- Farben
# Zwei Paletten (Apple-Systemtöne), umschaltbar mit der Taste d
THEMEN = {
    "hell": {
        "bg": (255, 255, 255),      # Karte
        "fg": (29, 29, 31),         # Text/Icons (Apple-Tinte)
        "zweit": (134, 134, 139),   # Sekundärtext
        "hover": (242, 242, 247),   # Knopf beim Hovern
        "gruppe": (242, 242, 247),  # Gruppenflächen im Menü
        "rand": (227, 227, 232),    # Haarlinie
        "timer": (232, 232, 237),   # Countdown-Balken (dezent)
        "akzent": (10, 132, 255),   # Systemblau
        "gruen": (52, 199, 89),     # Schalter an
        "grau": (209, 209, 214),    # Schalter aus
        "schatten": (0, 0, 0, 46),
    },
    "dunkel": {
        "bg": (0, 0, 0),
        "fg": (245, 245, 247),
        "zweit": (152, 152, 157),
        "hover": (28, 28, 30),
        "gruppe": (22, 22, 24),
        "rand": (44, 44, 46),
        "timer": (44, 44, 46),
        "akzent": (10, 132, 255),
        "gruen": (48, 209, 88),
        "grau": (57, 57, 61),
        "schatten": (0, 0, 0, 110),
    },
}
MAC_ROT = (255, 95, 87)             # Schliessknopf beim Hovern
MAC_ROT_SYMBOL = (96, 8, 4)

# ---------------------------------------------------------------- Verhalten
FLIPS_NEEDED = 1                    # Auto-Weiter schon nach dem ersten Flip
HISTORY_MAX = 10                    # max. 10 Wörter zurück

FONT_WUNSCH = (["SF Pro Text", "Helvetica Neue"] if IS_MAC else
               ["Segoe UI Variable", "Segoe UI"] if IS_WIN else
               ["Inter", "Cantarell", "DejaVu Sans"])


def hexc(c):
    return "#%02x%02x%02x" % (int(c[0]), int(c[1]), int(c[2]))


def qfarbe(c):
    return QColor(int(c[0]), int(c[1]), int(c[2]), int(c[3]) if len(c) > 3 else 255)


def blend(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


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
    "pfeil_knoepfe": True,        # ← → Knöpfe auf der Karte zeigen
    "auto_weiter": True,          # beim Raustabben automatisch weiter
    "auto_dauer": 5,              # Sekunden bis zum Auto-Weiter
    "flip_animation": True,
    "immer_vorne": True,          # Fenster immer im Vordergrund
    "sets": ["etape1"],
    "schwere_modus": False,       # nur Wörter mit Faktor >= 1 üben
    "taste_c": "C",               # kann ich nicht (austauschbar)
    "taste_v": "V",               # neutral (austauschbar)
    "taste_b": "B",               # kann ich (austauschbar)
    "hinweis_gesehen": False,     # Bedienungshinweis beim ersten Start
}
FESTE_TASTEN = {"D", "U", "M"}    # dürfen nicht als Wertungstaste belegt werden

# Bewertung: c = kann ich noch nicht, v = neutral, b = kann ich schon.
# Jeder Eintrag trägt einen Faktor (Start 1), der die Ziehungswahrscheinlichkeit
# gewichtet: b senkt ihn um 0.2, c erhöht ihn um 0.1, v lässt ihn stehen.
# Bei Faktor 0 kommt das Wort nicht mehr dran.
WERTUNG_DELTA = {"c": +0.1, "v": 0.0, "b": -0.2}
WERTUNG_BLITZ = {"c": (255, 105, 97), "v": (255, 214, 10), "b": (50, 215, 75)}
FAKTOR_MIN, FAKTOR_MAX = 0.0, 3.0
BLITZ_MS = 260                    # so lange leuchtet die Karte nach c/v/b
BLITZ_ANTEIL = 0.2                # Farbanteil des Blitzes - bewusst dezent


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
    """Startet ein Hilfsprogramm, das wartet, bis Voci beendet ist, und dann
    tauscht - ein laufendes Programm kann sich nicht selbst ersetzen.

    Ordner werden gespiegelt statt verschoben: 'move' kann Verzeichnisse nicht
    über Laufwerksgrenzen bewegen, und der temporäre Ordner liegt oft auf einem
    anderen Laufwerk als die entpackte Anwendung. Ausserdem wird am Ende immer
    neu gestartet - scheitert der Tausch, läuft wenigstens die alte Fassung
    weiter, statt dass gar nichts mehr da ist. Was passiert ist, steht im
    Protokoll neben den Einstellungen."""
    pid = os.getpid()
    ordner = pathlib.Path(neu).is_dir()
    try:
        protokoll = datenordner() / "update.log"
    except Exception:
        protokoll = pathlib.Path(tempfile.gettempdir()) / "voci-update.log"

    if IS_WIN:
        skript = pathlib.Path(neu).parent / "voci_update.cmd"
        if ordner:
            # /MIR spiegelt den Ordner, /R und /W begrenzen Wiederholungen.
            # robocopy meldet 0-7 als Erfolg, erst ab 8 ist etwas schiefgegangen.
            tausch = ('robocopy "%s" "%s" /MIR /NFL /NDL /NJH /NJS /R:2 /W:1 '
                      '>>"%s" 2>&1\r\n'
                      'if errorlevel 8 (echo FEHLER robocopy >>"%s") '
                      'else (echo Ordner ersetzt >>"%s")\r\n'
                      % (neu, ziel, protokoll, protokoll, protokoll))
        else:
            tausch = ('copy /y "%s" "%s" >>"%s" 2>&1\r\n'
                      'if errorlevel 1 (echo FEHLER copy >>"%s") '
                      'else (echo Datei ersetzt >>"%s")\r\n'
                      % (neu, ziel, protokoll, protokoll, protokoll))
        skript.write_text(
            "@echo off\r\n"
            'echo ---- %%date%% %%time%% Update >>"{log}"\r\n'
            ":warten\r\n"
            'tasklist /fi "PID eq {pid}" 2>nul | find "{pid}" >nul\r\n'
            "if not errorlevel 1 (\r\n"
            "  timeout /t 1 /nobreak >nul\r\n"
            "  goto warten\r\n"
            ")\r\n"
            "{tausch}"
            'start "" {start}\r\n'.format(log=protokoll, pid=pid,
                                           tausch=tausch, start=startbefehl),
            encoding="utf-8")
        subprocess.Popen(["cmd", "/c", str(skript)], cwd=str(skript.parent),
                         creationflags=0x08000000)   # ohne Konsolenfenster
    else:
        skript = pathlib.Path(neu).parent / "voci_update.sh"
        if ordner:
            tausch = ('if cp -a "%s/." "%s/" >>"%s" 2>&1; then\n'
                      '  echo "Ordner ersetzt" >>"%s"\n'
                      'else\n  echo "FEHLER beim Kopieren" >>"%s"\nfi\n'
                      % (neu, ziel, protokoll, protokoll, protokoll))
        else:
            tausch = ('if cp -a "%s" "%s" >>"%s" 2>&1; then\n'
                      '  echo "Datei ersetzt" >>"%s"\n'
                      'else\n  echo "FEHLER beim Kopieren" >>"%s"\nfi\n'
                      % (neu, ziel, protokoll, protokoll, protokoll))
        skript.write_text(
            "#!/bin/sh\n"
            'echo "---- $(date) Update" >>"%s"\n'
            "while kill -0 %d 2>/dev/null; do sleep 0.5; done\n"
            "%s"
            "%s &\n"
            % (protokoll, pid, tausch, startbefehl),
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




# ---------------------------------------------------------------- Eigene Sets
def sets_ordner():
    ordner = datenordner() / "sets"
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner


def lade_eigene_sets():
    """Importierte Voci-Sets aus dem Benutzerordner."""
    ergebnis = []
    for datei in sorted(sets_ordner().glob("*.json")):
        try:
            daten = json.loads(datei.read_text(encoding="utf-8"))
            if (isinstance(daten, dict) and vokabeln_gueltig_locker(daten.get("vocab"))
                    and daten.get("name")):
                ergebnis.append({"id": datei.stem, "name": str(daten["name"]),
                                 "vocab": daten["vocab"]})
        except Exception:
            continue
    return ergebnis


def vokabeln_gueltig_locker(daten):
    """Wie vokabeln_gueltig, aber schon ab einem Eintrag - ein kleines
    selbst importiertes Set ist auch ein Set."""
    return (isinstance(daten, list) and len(daten) >= 1
            and all(isinstance(e, dict) and e.get("fr") and e.get("de")
                    for e in daten))


def speichere_eigenes_set(name, vocab):
    kennung = "set-%d" % int(__import__("time").time())
    (sets_ordner() / ("%s.json" % kennung)).write_text(
        json.dumps({"name": name, "vocab": vocab}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    return kennung


def loesche_eigenes_set(kennung):
    try:
        (sets_ordner() / ("%s.json" % kennung)).unlink()
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------- PDF-Import
ENTRY_NUMMER = __import__("re").compile(r"^(\d+)\.$")


def pdf_verfuegbar():
    try:
        import pdfplumber  # noqa: F401
        return True
    except ImportError:
        return False


def _zeilen_gruppieren(woerter, toleranz=3):
    """Wörter mit etwa gleicher Höhe zu Zeilen zusammenfassen."""
    zeilen = []
    for wort in sorted(woerter, key=lambda w: (w["top"], w["x0"])):
        for zeile in zeilen:
            if abs(zeile[0]["top"] - wort["top"]) <= toleranz:
                zeile.append(wort)
                break
        else:
            zeilen.append([wort])
    return [sorted(z, key=lambda w: w["x0"]) for z in zeilen]


def _zeile_ignorieren(text):
    re = __import__("re")
    return (not text
            or text.startswith("Reprise étape")
            or text.startswith("Lerne online")
            or re.fullmatch(r"\d+\s*/\s*\d+", text) is not None)


def pdf_importieren(pfad):
    """Liest eine zweispaltige Vokabel-PDF (links Französisch, rechts Deutsch,
    Einträge mit '1.'-Nummern) und liefert (name, [{fr, de}, ...]).

    Unvollständige Einträge werden übersprungen statt den ganzen Import
    scheitern zu lassen - eine PDF mit ein paar unlesbaren Zeilen ist besser
    als gar keine."""
    import pdfplumber

    eintraege = []
    aktuell = None
    with pdfplumber.open(pfad) as pdf:
        for seite in pdf.pages:
            grenze = seite.width / 2      # Spaltengrenze relativ zur Seite
            woerter = seite.extract_words(use_text_flow=False,
                                          keep_blank_chars=False)
            for zeile in _zeilen_gruppieren(woerter):
                text = " ".join(w["text"] for w in zeile).strip()
                if _zeile_ignorieren(text):
                    continue
                treffer = ENTRY_NUMMER.match(zeile[0]["text"])
                if treffer:
                    aktuell = {"fr": "", "de": ""}
                    eintraege.append(aktuell)
                    inhalt = zeile[1:]
                else:
                    inhalt = zeile        # Folgezeile des vorherigen Eintrags
                if aktuell is None:
                    continue
                links = " ".join(w["text"] for w in inhalt if w["x0"] < grenze)
                rechts = " ".join(w["text"] for w in inhalt if w["x0"] >= grenze)
                if links:
                    aktuell["fr"] = ("%s %s" % (aktuell["fr"], links)).strip()
                if rechts:
                    aktuell["de"] = ("%s %s" % (aktuell["de"], rechts)).strip()

    brauchbar = [e for e in eintraege if e["fr"] and e["de"]]
    if not brauchbar:
        raise ValueError("In der PDF wurden keine Vokabeln gefunden. Erwartet "
                         "werden zwei Spalten (links Französisch, rechts "
                         "Deutsch) mit nummerierten Einträgen wie '1.'.")
    name = pathlib.Path(pfad).stem
    name = __import__("re").sub(r"[-_]+", " ", name).strip() or "Importiertes Set"
    return name, brauchbar


# ---------------------------------------------------------------- Qt-Grundlagen
SCHATTEN = 22                     # weicher Rand um jedes Panel
RADIUS = 20                       # Eckenradius der Karten
TAKT_MS = 16                      # ~60 Bilder je Sekunde für weiche Übergänge


def strecke(wert, ziel, tempo):
    """Nähert einen Wert seinem Ziel an - Grundlage aller weichen Übergänge."""
    if abs(ziel - wert) < 0.002:
        return ziel
    return wert + (ziel - wert) * tempo


def kurve(t):
    """Sanftes Ein- und Ausschwingen (cubic in/out)."""
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


class Ablauf(QVariantAnimation):
    """Ein Animationsdurchlauf von 0 nach 1 mit optionalem Wendepunkt."""

    def __init__(self, eltern, dauer, schritt, mitte=None, fertig=None,
                 mitte_bei=0.5):
        super().__init__(eltern)
        self.setDuration(dauer)
        self.setStartValue(0.0)
        self.setEndValue(1.0)
        self.setEasingCurve(QEasingCurve.Type.Linear)
        self._mitte, self._mitte_bei = mitte, mitte_bei
        self._gewendet = False
        self.valueChanged.connect(lambda w: self._takt(w, schritt))
        if fertig:
            self.finished.connect(fertig)

    def _takt(self, wert, schritt):
        if (self._mitte and not self._gewendet and wert >= self._mitte_bei):
            self._gewendet = True
            self._mitte()
        schritt(wert)


def basisfont(pixel, fett=False):
    f = QFont()
    f.setFamilies(FONT_WUNSCH)
    f.setPixelSize(int(pixel))
    f.setWeight(QFont.Weight.DemiBold if fett else QFont.Weight.Normal)
    return f


def panel_zeichnen(p, breite, hoehe, thema):
    """Weicher Schatten, Kartenfläche, Haarlinie – gemeinsame Basis aller
    Fenster. Liefert das innere Karten-Rechteck."""
    t = THEMEN[thema]
    rect = QRectF(SCHATTEN, SCHATTEN, breite - 2 * SCHATTEN, hoehe - 2 * SCHATTEN)
    grund = qfarbe(t["schatten"])
    for i in range(SCHATTEN - 4, 0, -2):
        w = QColor(grund)
        w.setAlpha(int(grund.alpha() * (1 - i / SCHATTEN) ** 2 * 0.5))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(w)
        p.drawRoundedRect(rect.adjusted(-i, -i + 2, i, i + 2), RADIUS + i, RADIUS + i)
    p.setBrush(qfarbe(t["bg"]))
    p.setPen(QPen(qfarbe(t["rand"]), 1))
    p.drawRoundedRect(rect, RADIUS, RADIUS)
    return rect


class Panel(QWidget):
    """Randloses, durchscheinend gerahmtes Fenster mit Titelzeile und X."""

    def __init__(self, app, titel, breite, hoehe):
        super().__init__(None)
        self.app = app
        self.titel = titel
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(breite + 2 * SCHATTEN, hoehe + 2 * SCHATTEN)
        self._zieh = None
        self._x_heiss = False
        self.setMouseTracking(True)

        self.inhalt = QWidget(self)
        self.inhalt.setGeometry(SCHATTEN + 16, SCHATTEN + 40,
                                breite - 32, hoehe - 52)
        self.inhalt.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # -- Zeichnen
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = THEMEN[self.app.thema]
        rect = panel_zeichnen(p, self.width(), self.height(), self.app.thema)
        p.setPen(qfarbe(t["fg"]))
        p.setFont(basisfont(15, fett=True))
        p.drawText(QRectF(rect.x() + 16, rect.y() + 8, rect.width() - 60, 28),
                   Qt.AlignmentFlag.AlignVCenter, self.titel)
        # X-Knopf
        bx, by, r = self._x_pos()
        if self._x_heiss:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(qfarbe(MAC_ROT))
            p.drawEllipse(QPointF(bx, by), r, r)
            stift = qfarbe(MAC_ROT_SYMBOL)
        else:
            stift = qfarbe(t["zweit"])
        p.setPen(QPen(stift, 1.6, c=Qt.PenCapStyle.RoundCap))
        a = r * 0.42
        p.drawLine(QPointF(bx - a, by - a), QPointF(bx + a, by + a))
        p.drawLine(QPointF(bx - a, by + a), QPointF(bx + a, by - a))

    def _x_pos(self):
        return self.width() - SCHATTEN - 22, SCHATTEN + 22, 10

    # -- Maus: X, sonst ziehen
    def mousePressEvent(self, e):
        bx, by, r = self._x_pos()
        pos = e.position()
        if (pos.x() - bx) ** 2 + (pos.y() - by) ** 2 <= (r + 4) ** 2:
            self.close()
            return
        self._zieh = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        bx, by, r = self._x_pos()
        pos = e.position()
        heiss = (pos.x() - bx) ** 2 + (pos.y() - by) ** 2 <= (r + 4) ** 2
        if heiss != self._x_heiss:
            self._x_heiss = heiss
            self.update()
        if self._zieh is not None and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._zieh)

    def mouseReleaseEvent(self, _):
        self._zieh = None

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()
        elif not self.app.taste(e.key()):
            super().keyPressEvent(e)

    def einblenden(self):
        """Panel gleitet leicht hoch und blendet ein."""
        self.setWindowOpacity(0.0)
        self._ziel_y = self.y()
        self.move(self.x(), self._ziel_y + 12)

        def schritt(w):
            t = kurve(w)
            self.setWindowOpacity(t)
            self.move(self.x(), int(self._ziel_y + 12 * (1 - t)))

        def fertig():
            self.setWindowOpacity(1.0)
            self.move(self.x(), self._ziel_y)
        self._anim = Ablauf(self, 220, schritt, fertig=fertig)
        self._anim.start()

    def neben_karte(self):
        k = self.app.karte.frameGeometry()
        schirm = self.screen().availableGeometry() if self.screen() else None
        x = k.right() - SCHATTEN + 8
        if schirm and x + self.width() > schirm.right():
            x = max(0, k.left() - self.width() + SCHATTEN - 8)
        self.move(x, k.top())


class Schalter(QWidget):
    """Apple-Kippschalter: der Knauf gleitet, die Farbe wandert mit."""

    def __init__(self, app, wert, cb):
        super().__init__()
        self.app, self.wert, self.cb = app, wert, cb
        self.setFixedSize(40, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lage = 1.0 if wert else 0.0
        self.druck = 0.0                  # Knauf wird beim Klick kurz breiter
        self._takt = QTimer(self)
        self._takt.timeout.connect(self._schritt)

    def _schritt(self):
        ziel = 1.0 if self.wert else 0.0
        self.lage = strecke(self.lage, ziel, 0.28)
        self.druck = strecke(self.druck, 0.0, 0.2)
        self.update()
        if self.lage == ziel and self.druck == 0.0:
            self._takt.stop()

    def paintEvent(self, _):
        t = THEMEN[self.app.thema]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qfarbe(blend(t["grau"], t["gruen"], self.lage)))
        p.drawRoundedRect(QRectF(0, 1, 40, 22), 11, 11)
        p.setBrush(QColor("white"))
        kx = 11 + self.lage * 18
        breit = 9 + 2.5 * self.druck
        p.drawRoundedRect(QRectF(kx - breit, 3, 2 * breit, 18), 9, 9)

    def mouseReleaseEvent(self, _):
        self.wert = not self.wert
        self.druck = 1.0
        if not self._takt.isActive():
            self._takt.start(TAKT_MS)
        self.cb(self.wert)


class Segmente(QWidget):
    """Segmentregler: Pillenhintergrund, aktives Segment als helle Karte."""

    def __init__(self, app, optionen, wert, cb, dehnen=False):
        super().__init__()
        self.app, self.optionen, self.wert, self.cb = app, optionen, wert, cb
        self.dehnen = dehnen
        self.font_n = basisfont(12)
        self.font_f = basisfont(12, fett=True)
        fm = QFontMetrics(self.font_f)
        self._breiten = [fm.horizontalAdvance(text) + 22 for _, text in optionen]
        self.setFixedHeight(26)
        if not dehnen:
            self.setFixedWidth(sum(self._breiten))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lage = float(self._index(wert))
        self._takt = QTimer(self)
        self._takt.timeout.connect(self._schritt)

    def _spalten(self):
        if self.dehnen:
            teil = self.width() / len(self.optionen)
            return [teil] * len(self.optionen)
        return self._breiten

    def _index(self, wert):
        for n, (w, _) in enumerate(self.optionen):
            if w == wert:
                return n
        return 0

    def _kachel(self, index):
        spalten = self._spalten()
        return sum(spalten[:index]), spalten[index]

    def _schritt(self):
        ziel = float(self._index(self.wert))
        self.lage = strecke(self.lage, ziel, 0.3)
        self.update()
        if self.lage == ziel:
            self._takt.stop()

    def paintEvent(self, _):
        t = THEMEN[self.app.thema]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qfarbe(t["gruppe"]))
        p.drawRoundedRect(QRectF(0, 0, self.width(), 26), 13, 13)

        # Der helle Reiter gleitet zwischen den Segmenten
        unten, oben = int(self.lage), min(int(self.lage) + 1,
                                          len(self.optionen) - 1)
        anteil = self.lage - unten
        x0, b0 = self._kachel(unten)
        x1, b1 = self._kachel(oben)
        rx = x0 + (x1 - x0) * anteil
        rb = b0 + (b1 - b0) * anteil
        p.setBrush(qfarbe(t["bg"]))
        p.setPen(QPen(qfarbe(t["rand"]), 1))
        p.drawRoundedRect(QRectF(rx + 2, 2, rb - 4, 22), 11, 11)

        x = 0.0
        for n, ((wert, text), b) in enumerate(zip(self.optionen, self._spalten())):
            naehe = max(0.0, 1.0 - abs(self.lage - n))
            p.setPen(qfarbe(t["fg"]))
            p.setFont(self.font_f if naehe > 0.5 else self.font_n)
            p.drawText(QRectF(x, 0, b, 26), Qt.AlignmentFlag.AlignCenter, text)
            p.setPen(Qt.PenStyle.NoPen)
            x += b

    def mouseReleaseEvent(self, e):
        x = 0.0
        for (wert, _), b in zip(self.optionen, self._spalten()):
            if x <= e.position().x() < x + b:
                if wert != self.wert:
                    self.wert = wert
                    if not self._takt.isActive():
                        self._takt.start(TAKT_MS)
                    self.cb(wert)
                return
            x += b


class HakenKreis(QWidget):
    """Blauer Haken-Kreis für die Set-Auswahl."""

    def __init__(self, app, wert, cb):
        super().__init__()
        self.app, self.wert, self.cb = app, wert, cb
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, _):
        t = THEMEN[self.app.thema]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.wert:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(qfarbe(t["akzent"]))
            p.drawEllipse(QPointF(12, 12), 10, 10)
            p.setPen(QPen(QColor("white"), 2,
                          c=Qt.PenCapStyle.RoundCap, j=Qt.PenJoinStyle.RoundJoin))
            pfad = QPainterPath(QPointF(7.2, 12.4))
            pfad.lineTo(10.6, 15.8)
            pfad.lineTo(16.8, 8.6)
            p.drawPath(pfad)
        else:
            p.setPen(QPen(qfarbe(t["grau"]), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(12, 12), 10, 10)

    def mouseReleaseEvent(self, _):
        self.cb()


class TastenKachel(QWidget):
    """Kleine Tastatur-Kachel wie auf einem Keyboard. Austauschbare Tasten
    sind klickbar: nach dem Klick übernimmt der nächste Tastendruck."""

    def __init__(self, app, text, wofuer=None):
        super().__init__()
        self.app, self.text, self.wofuer = app, text, wofuer
        breite = max(26, 12 + QFontMetrics(basisfont(11, fett=True))
                     .horizontalAdvance(text))
        self.setFixedSize(breite, 22)
        if wofuer:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("Klicken und neue Taste drücken")

    def paintEvent(self, _):
        t = THEMEN[self.app.thema]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        aufnahme = self.wofuer and self.app.warte_auf_taste == self.wofuer
        p.setBrush(qfarbe(t["akzent"]) if aufnahme else qfarbe(t["bg"]))
        p.setPen(QPen(qfarbe(t["rand"]), 1))
        p.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, 21), 6, 6)
        p.setPen(QColor("white") if aufnahme else qfarbe(t["fg"]))
        p.setFont(basisfont(11, fett=True))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                   "…" if aufnahme else self.text)

    def mouseReleaseEvent(self, _):
        if self.wofuer:
            a = self.app
            a.warte_auf_taste = None if a.warte_auf_taste == self.wofuer \
                else self.wofuer
            self.update()


class Gruppe(QFrame):
    """Abgerundete Gruppenfläche im Stil der macOS-Systemeinstellungen."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        t = THEMEN[app.thema]
        self.setStyleSheet("QFrame { background: %s; border-radius: 10px; }"
                           % hexc(t["gruppe"]))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 2, 12, 2)
        lay.setSpacing(0)
        self.lay = lay
        self._erste = True

    def zeile(self, links, rechts):
        if not self._erste:
            strich = QFrame()
            strich.setFixedHeight(1)
            strich.setStyleSheet("background: %s; border-radius: 0;"
                                 % hexc(THEMEN[self.app.thema]["rand"]))
            self.lay.addWidget(strich)
        self._erste = False
        z = QWidget()
        z.setStyleSheet("background: transparent;")
        h = QHBoxLayout(z)
        h.setContentsMargins(0, 7, 0, 7)
        if isinstance(links, str):
            lab = QLabel(links)
            lab.setFont(basisfont(13))
            lab.setStyleSheet("color: %s; background: transparent;"
                              % hexc(THEMEN[self.app.thema]["fg"]))
            h.addWidget(lab)
        else:
            h.addWidget(links)
        h.addStretch(1)
        for w in (rechts if isinstance(rechts, (list, tuple)) else [rechts]):
            h.addWidget(w)
        self.lay.addWidget(z)
        return z


# ---------------------------------------------------------------- Menü
class MenuFenster(Panel):
    def __init__(self, app, tab="einstellungen"):
        super().__init__(app, "Voci", 320, 620)
        self.tab = tab
        self.regionen = {}           # Name -> Wirkung (auch für Tests)
        self._bauen()
        self.neben_karte()

    def ausloesen(self, name):
        if name in self.regionen:
            self.regionen[name]()
            return True
        return False

    def _bauen(self):
        for kind in self.inhalt.findChildren(QWidget):
            kind.setParent(None)
        self.regionen = {}
        wurzel = QVBoxLayout(self.inhalt) if self.inhalt.layout() is None \
            else self.inhalt.layout()
        while wurzel.count():
            rest = wurzel.takeAt(0)
            if rest.widget():
                rest.widget().deleteLater()
        wurzel.setContentsMargins(0, 0, 0, 0)
        wurzel.setSpacing(12)

        tabs = Segmente(self.app, [("einstellungen", "Einstellungen"),
                                   ("sets", "Voci-Sets")],
                        self.tab, self._tab_wechsel, dehnen=True)
        wurzel.addWidget(tabs)
        self.regionen["tab-einstellungen"] = lambda: self._tab_wechsel("einstellungen")
        self.regionen["tab-sets"] = lambda: self._tab_wechsel("sets")
        self.regionen["close"] = self.close

        if self.tab == "einstellungen":
            self._tab_einstellungen(wurzel)
        else:
            self._tab_sets(wurzel)
        wurzel.addStretch(1)

    def _tab_wechsel(self, tab):
        self.tab = tab
        self._bauen()

    def _tab_einstellungen(self, wurzel):
        a = self.app
        g1 = Gruppe(a)

        def schalter(name, text, wert, cb):
            s = Schalter(a, wert, lambda _an: cb())
            g = g1 if name in ("dark", "vorne", "knoepfe", "flip") else g2
            g.zeile(text, s)
            self.regionen[name] = cb

        schalter("dark", "Dark Mode", a.thema == "dunkel", a.toggle_thema)
        schalter("vorne", "Immer im Vordergrund", a.einst["immer_vorne"],
                 lambda: a.einstellung_kippen("vorne", "immer_vorne"))
        schalter("knoepfe", "Pfeil-Knöpfe auf der Karte",
                 a.einst["pfeil_knoepfe"],
                 lambda: a.einstellung_kippen("knoepfe", "pfeil_knoepfe"))
        schalter("flip", "Flip-Animation", a.einst["flip_animation"],
                 lambda: a.einstellung_kippen("flip", "flip_animation"))
        wurzel.addWidget(g1)

        g2 = Gruppe(a)
        s = Schalter(a, a.einst["auto_weiter"],
                     lambda _an: a.einstellung_kippen("auto", "auto_weiter"))
        g2.zeile("Auto-Weiter", s)
        self.regionen["auto"] = lambda: a.einstellung_kippen("auto", "auto_weiter")

        def dauer(w):
            a.einst["auto_dauer"] = w
            speichere_einstellungen(a.einst)
        seg = Segmente(a, [(3, "3 s"), (5, "5 s"), (10, "10 s")],
                       int(a.einst["auto_dauer"]), dauer)
        g2.zeile("Wartezeit", seg)
        for wert in (3, 5, 10):
            self.regionen["dauer-%d" % wert] = lambda w=wert: (dauer(w),
                                                               self._bauen())

        def sprache(w):
            if w != a.start_side:
                a.toggle_start()
        seg2 = Segmente(a, [("fr", "FR"), ("de", "DE")], a.start_side, sprache)
        g2.zeile("Startsprache", seg2)
        for wert in ("fr", "de"):
            self.regionen["sprache-%s" % wert] = lambda w=wert: (sprache(w),
                                                                 self._bauen())
        wurzel.addWidget(g2)

        titel = QLabel("Steuerung")
        titel.setFont(basisfont(11, fett=True))
        titel.setStyleSheet("color: %s; background: transparent;"
                            % hexc(THEMEN[a.thema]["zweit"]))
        wurzel.addWidget(titel)
        g3 = Gruppe(a)
        for kacheln, text, wofuer in (
                ([a.einst["taste_c"]], "kann ich nicht", "c"),
                ([a.einst["taste_v"]], "neutral", "v"),
                ([a.einst["taste_b"]], "kann ich schon", "b"),
                (["←", "→"], "zurück · weiter", None),
                (["D"], "Dark Mode", None),
                (["M"], "Menü", None)):
            links = QWidget()
            links.setStyleSheet("background: transparent;")
            h = QHBoxLayout(links)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(4)
            for k in kacheln:
                h.addWidget(TastenKachel(a, k, wofuer))
            pfeil = QLabel("→")
            pfeil.setFont(basisfont(11))
            pfeil.setStyleSheet("color: %s; background: transparent;"
                                % hexc(THEMEN[a.thema]["zweit"]))
            h.addSpacing(4)
            h.addWidget(pfeil)
            lab = QLabel(text)
            lab.setFont(basisfont(12))
            lab.setStyleSheet("color: %s; background: transparent;"
                              % hexc(THEMEN[a.thema]["fg"]))
            h.addWidget(lab)
            g3.zeile(links, [])
        wurzel.addWidget(g3)

    def _tab_sets(self, wurzel):
        a = self.app
        g = Gruppe(a)
        for satz in a.sets:
            aktiv = satz["id"] in a.einst["sets"]

            def kippen(sid=satz["id"]):
                gewaehlt = set(a.einst["sets"])
                if sid in gewaehlt and len(gewaehlt) > 1:
                    gewaehlt.discard(sid)
                else:
                    gewaehlt.add(sid)
                a.einst["sets"] = sorted(gewaehlt)
                speichere_einstellungen(a.einst)
                self._bauen()

            haken = HakenKreis(a, aktiv, kippen)
            name = QLabel("%s   " % satz["name"])
            name.setFont(basisfont(13))
            name.setStyleSheet("color: %s; background: transparent;"
                               % hexc(THEMEN[a.thema]["fg"]))
            anzahl = QLabel("%d Wörter" % len(satz["indizes"]))
            anzahl.setFont(basisfont(11))
            anzahl.setStyleSheet("color: %s; background: transparent;"
                                 % hexc(THEMEN[a.thema]["zweit"]))
            links = QWidget()
            links.setStyleSheet("background: transparent;")
            h = QHBoxLayout(links)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(haken)
            h.addSpacing(8)
            h.addWidget(name)
            h.addWidget(anzahl)

            punkte = QPushButton("⋯")
            punkte.setFlat(True)
            punkte.setFont(basisfont(15, fett=True))
            punkte.setCursor(Qt.CursorShape.PointingHandCursor)
            punkte.setFixedWidth(30)
            punkte.setStyleSheet(
                "QPushButton { color: %s; background: transparent; border: none; }"
                % hexc(THEMEN[a.thema]["zweit"]))
            punkte.clicked.connect(
                lambda _=False, k=punkte, sz=satz: self._optionen(k, sz))
            g.zeile(links, punkte)
            self.regionen["set-%s" % satz["id"]] = kippen
            self.regionen["punkte"] = lambda k=punkte: self._optionen(k)
        wurzel.addWidget(g)

        importieren = QPushButton("＋  PDF importieren …")
        importieren.setFlat(True)
        importieren.setFont(basisfont(13))
        importieren.setCursor(Qt.CursorShape.PointingHandCursor)
        importieren.setStyleSheet(
            "QPushButton { color: %s; background: %s; border: none;"
            " border-radius: 10px; padding: 8px; text-align: center; }"
            "QPushButton:hover { background: %s; }"
            % (hexc(THEMEN[a.thema]["akzent"]), hexc(THEMEN[a.thema]["gruppe"]),
               hexc(THEMEN[a.thema]["hover"])))
        if pdf_verfuegbar():
            importieren.clicked.connect(self._pdf_waehlen)
        else:
            importieren.setText("PDF-Import braucht das Paket pdfplumber")
            importieren.setEnabled(False)
        wurzel.addWidget(importieren)
        self.regionen["import"] = self._pdf_waehlen

        if a.import_status:
            status = QLabel(a.import_status)
            status.setFont(basisfont(11))
            status.setWordWrap(True)
            status.setStyleSheet("color: %s; background: transparent;"
                                 % hexc(THEMEN[a.thema]["zweit"]))
            wurzel.addWidget(status)

    def _pdf_waehlen(self):
        pfad, _ = QFileDialog.getOpenFileName(
            self, "Vokabel-PDF auswählen", "", "PDF-Dateien (*.pdf)")
        if pfad:
            self.app.set_importieren(pfad)

    def _optionen(self, anker, satz=None):
        a = self.app
        t = THEMEN[a.thema]
        menue = QMenu(self)
        menue.setStyleSheet(
            "QMenu { background: %s; color: %s; border: 1px solid %s;"
            " border-radius: 8px; padding: 4px; }"
            "QMenu::item { padding: 6px 14px; border-radius: 5px; }"
            "QMenu::item:selected { background: %s; }"
            % (hexc(t["bg"]), hexc(t["fg"]), hexc(t["rand"]), hexc(t["hover"])))
        schwer = QAction("Schwere Wörter üben (Faktor ≥ 1)", menue)
        schwer.setCheckable(True)
        schwer.setChecked(a.einst["schwere_modus"])
        schwer.triggered.connect(a.schwere_kippen)
        menue.addAction(schwer)
        liste = QAction("Wörterliste anzeigen", menue)
        liste.triggered.connect(a.liste_zeigen)
        menue.addAction(liste)
        if satz is not None and satz.get("eigen"):
            menue.addSeparator()
            entfernen = QAction("„%s“ entfernen" % satz["name"], menue)
            entfernen.triggered.connect(
                lambda _=False, k=satz["id"]: a.set_loeschen(k))
            menue.addAction(entfernen)
        menue.exec(anker.mapToGlobal(anker.rect().bottomLeft()))


# ---------------------------------------------------------------- Hinweis
class HinweisFenster(Panel):
    """Kurzanleitung beim allerersten Start."""

    def __init__(self, app):
        super().__init__(app, "Willkommen bei Voci", 340, 400)
        t = THEMEN[app.thema]
        lay = QVBoxLayout(self.inhalt)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        for text in (
                "Klick auf die Karte deckt die Übersetzung auf.",
                "",
                "Bewerte jedes Wort mit einer Taste:",
                "   %s → kann ich nicht (kommt öfter)" % app.einst["taste_c"],
                "   %s → neutral" % app.einst["taste_v"],
                "   %s → kann ich schon (kommt seltener)" % app.einst["taste_b"],
                "",
                "←  → blättern zurück und weiter.",
                "M öffnet das Menü (Einstellungen, eigene",
                "Sets, Wörterliste), D den Dark Mode.",
                "",
                "Das Fenster bleibt immer im Vordergrund -",
                "einfach neben die Arbeit legen."):
            z = QLabel(text)
            z.setFont(basisfont(12))
            z.setStyleSheet("color: %s; background: transparent;"
                            % hexc(t["fg"] if text.strip() else t["zweit"]))
            lay.addWidget(z)
        lay.addStretch(1)

        los = QPushButton("Los geht's")
        los.setFont(basisfont(13, fett=True))
        los.setCursor(Qt.CursorShape.PointingHandCursor)
        los.setFixedHeight(34)
        los.setStyleSheet(
            "QPushButton { color: white; background: %s; border: none;"
            " border-radius: 17px; } QPushButton:hover { background: %s; }"
            % (hexc(t["akzent"]), hexc(blend(t["akzent"], (0, 0, 0), 0.15))))
        los.clicked.connect(self.close)
        lay.addWidget(los)

    def closeEvent(self, e):
        self.app.einst["hinweis_gesehen"] = True
        speichere_einstellungen(self.app.einst)
        self.app.hinweis = None
        super().closeEvent(e)


# ---------------------------------------------------------------- Wörterliste
class ListeFenster(Panel):
    def __init__(self, app):
        super().__init__(app, "Wörterliste", 370, 430)
        self.sortierung = getattr(app, "liste_sortierung", "wertung")
        self.regionen = {"close": self.close}
        self._bauen()
        self.neben_karte()

    def ausloesen(self, name):
        if name in self.regionen:
            self.regionen[name]()
            return True
        return False

    def _bauen(self):
        a = self.app
        t = THEMEN[a.thema]
        wurzel = QVBoxLayout(self.inhalt)
        wurzel.setContentsMargins(0, 0, 0, 0)
        wurzel.setSpacing(8)

        kopf = QWidget()
        kopf.setStyleSheet("background: transparent;")
        h = QHBoxLayout(kopf)
        h.setContentsMargins(0, 0, 0, 0)
        seg = Segmente(a, [("az", "A–Z"), ("wertung", "Wertung")],
                       self.sortierung, self._sortieren)
        h.addWidget(seg)
        h.addStretch(1)
        alle = QPushButton("Alle zurücksetzen")
        alle.setFlat(True)
        alle.setFont(basisfont(11))
        alle.setCursor(Qt.CursorShape.PointingHandCursor)
        alle.setStyleSheet("QPushButton { color: %s; background: transparent;"
                           " border: none; }" % hexc(WERTUNG_BLITZ["c"]))
        alle.clicked.connect(self.alle_zuruecksetzen)
        h.addWidget(alle)
        wurzel.addWidget(kopf)
        self.regionen["reset-alle"] = self.alle_zuruecksetzen
        for wert in ("az", "wertung"):
            self.regionen["sortier-%s" % wert] = lambda w=wert: self._sortieren(w)

        self.rollbereich = QScrollArea()
        self.rollbereich.setWidgetResizable(False)
        self.rollbereich.setAlignment(Qt.AlignmentFlag.AlignHCenter
                                      | Qt.AlignmentFlag.AlignTop)
        self.rollbereich.setFrameShape(QFrame.Shape.NoFrame)
        self.rollbereich.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: transparent; width: 8px;"
            " margin: 2px 0 2px 0; border: none; }"
            "QScrollBar::handle:vertical { background: %s; border-radius: 4px;"
            " min-height: 40px; }"
            "QScrollBar::handle:vertical:hover { background: %s; }"
            "QScrollBar::add-line, QScrollBar::sub-line { height: 0; }"
            "QScrollBar::add-page, QScrollBar::sub-page { background: none; }"
            % (hexc(t["grau"]), hexc(t["zweit"])))
        wurzel.addWidget(self.rollbereich, 1)
        self._fuellen()

    def _sortieren(self, wie):
        self.sortierung = wie
        self.app.liste_sortierung = wie
        self._fuellen()

    def reihenfolge(self):
        a = self.app
        indizes = list(a.aktive_indizes())
        if self.sortierung == "wertung":
            indizes.sort(key=lambda i: (-wertung_prozent(a.faktor(i)),
                                        a.vocab[i]["fr"].lower()))
        else:
            indizes.sort(key=lambda i: a.vocab[i]["fr"].lower())
        return indizes

    def _fuellen(self):
        """Zwei bündige Spalten (FR | DE) statt eines Gedankenstrich-Texts;
        die Liste sitzt horizontal mittig im Fenster."""
        a = self.app
        t = THEMEN[a.thema]
        self.zeilen = self.reihenfolge()
        fm = QFontMetrics(basisfont(12))
        FR_B, DE_B = 128, 118

        rumpf = QWidget()
        rumpf.setFixedWidth(316)
        rumpf.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(rumpf)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        for n, i in enumerate(self.zeilen):
            if n:
                strich = QFrame()
                strich.setFixedHeight(1)
                strich.setStyleSheet("background: %s;" % hexc(t["rand"]))
                lay.addWidget(strich)
            prozent = wertung_prozent(a.faktor(i))
            z = QWidget()
            z.setStyleSheet("background: transparent;")
            h = QHBoxLayout(z)
            h.setContentsMargins(2, 7, 0, 7)
            h.setSpacing(8)
            fr = QLabel(fm.elidedText(a.vocab[i]["fr"],
                                      Qt.TextElideMode.ElideRight, FR_B))
            fr.setFont(basisfont(12))
            fr.setFixedWidth(FR_B)
            fr.setStyleSheet("color: %s; background: transparent;"
                             % hexc(t["fg"]))
            h.addWidget(fr)
            de = QLabel(fm.elidedText(a.vocab[i]["de"],
                                      Qt.TextElideMode.ElideRight, DE_B))
            de.setFont(basisfont(12))
            de.setFixedWidth(DE_B)
            de.setStyleSheet("color: %s; background: transparent;"
                             % hexc(t["zweit"]))
            h.addWidget(de)
            h.addStretch(1)
            punkt = QLabel("●")
            punkt.setFont(basisfont(11))
            punkt.setStyleSheet("color: %s; background: transparent;"
                                % hexc(wertung_farbe(prozent)))
            h.addWidget(punkt)
            pz = QLabel("%d%%" % prozent)
            pz.setFont(basisfont(11))
            pz.setFixedWidth(34)
            pz.setAlignment(Qt.AlignmentFlag.AlignRight
                            | Qt.AlignmentFlag.AlignVCenter)
            pz.setStyleSheet("color: %s; background: transparent;"
                             % hexc(t["zweit"]))
            h.addWidget(pz)
            reset = QPushButton("↺")
            reset.setFlat(True)
            reset.setFixedWidth(22)
            reset.setCursor(Qt.CursorShape.PointingHandCursor)
            reset.setStyleSheet(
                "QPushButton { color: %s; background: transparent;"
                " border: none; } QPushButton:hover { color: %s; }"
                % (hexc(t["zweit"]), hexc(t["fg"])))
            reset.clicked.connect(lambda _=False, idx=i: self.reset(idx))
            h.addWidget(reset)
            lay.addWidget(z)
        rumpf.adjustSize()
        self.rollbereich.setWidget(rumpf)

    def reset(self, idx):
        self.app.setze_faktor(idx, 1.0)
        self._fuellen()

    def alle_zuruecksetzen(self):
        self.app.faktoren.clear()
        speichere_faktoren(self.app.faktoren)
        self._fuellen()


# ---------------------------------------------------------------- Karte
class Karte(QWidget):
    KANTE = 7                      # Greifzone für das Grössenziehen

    def __init__(self, app):
        super().__init__(None)
        self.app = app
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(280 + 2 * SCHATTEN, 170 + 2 * SCHATTEN)
        self.resize(400 + 2 * SCHATTEN, 250 + 2 * SCHATTEN)
        self.move(140, 140)

        self.scale = 1.0            # Restbreite beim Flip (1 = voll)
        self.winkel = 0.0           # Drehung um die Hochachse, echter 3D-Flip
        self.versatz = 0.0          # seitliches Gleiten beim Wortwechsel
        self.inhalt = 1.0           # Deckkraft der ganzen Karte (Flip)
        self.wort_alpha = 1.0       # Deckkraft nur des Worts (Gleiten)
        self.puls = 0.0             # kurzes Aufpoppen nach einer Wertung
        self.blitz_staerke = 0.0    # Farbanteil des Wertungs-Blitzes
        self.start_anim = 0.0       # Einblenden beim Programmstart
        self.hover = None
        self.hover_werte = {}       # Knopf -> 0..1, weich nachgeführt
        self._presse = None
        self._zieh = None
        self._resize = None
        self._wrapcache = {}
        self.anim = None
        self._hovertakt = QTimer(self)
        self._hovertakt.timeout.connect(self._hover_schritt)

    # ---- Geometrie
    def karte_rect(self):
        return QRectF(SCHATTEN, SCHATTEN, self.width() - 2 * SCHATTEN,
                      self.height() - 2 * SCHATTEN)

    def buttons(self):
        """Sichtbare Knöpfe. Die Pfeile lassen sich im Menü ausblenden; da
        Zeichnen und Trefferzonen dieselbe Liste nutzen, verschwinden mit
        ihnen auch ihre Klickflächen."""
        r = self.karte_rect()
        pad, kr = 30, 15
        alle = (("lang", r.x() + pad, r.y() + pad, kr),
                ("close", r.right() - pad, r.y() + pad, kr),
                ("back", r.x() + pad, r.bottom() - pad, kr),
                ("next", r.right() - pad, r.bottom() - pad, kr))
        if not self.app.einst["pfeil_knoepfe"]:
            return tuple(b for b in alle if b[0] not in ("back", "next"))
        return alle

    # ---- weiche Übergänge
    def _hover_schritt(self):
        ruhig = True
        for tag, _, _, _ in self.buttons():
            ziel = 1.0 if self.hover == tag else 0.0
            wert = strecke(self.hover_werte.get(tag, 0.0), ziel, 0.25)
            self.hover_werte[tag] = wert
            if wert != ziel:
                ruhig = False
        self.update()
        if ruhig:
            self._hovertakt.stop()

    def _hover_wecken(self):
        if not self._hovertakt.isActive():
            self._hovertakt.start(TAKT_MS)

    def einblenden(self):
        """Karte fährt beim Start sanft heran."""
        self.start_anim = 0.0

        def schritt(w):
            self.start_anim = kurve(w)
            self.update()
        self.anim_start = Ablauf(self, 420, schritt,
                                 fertig=lambda: setattr(self, "start_anim", 1.0))
        self.anim_start.start()

    # ---- Zeichnen
    def paintEvent(self, _):
        a = self.app
        t = THEMEN[a.thema]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        voll = self.karte_rect()
        cx, cy = voll.center().x(), voll.center().y()

        # Beim Start heranfahren
        if self.start_anim < 1.0:
            p.setOpacity(max(0.0, self.start_anim))
            s0 = 0.92 + 0.08 * self.start_anim
            p.translate(cx, cy + (1 - self.start_anim) * 14)
            p.scale(s0, s0)
            p.translate(-cx, -cy)

        # Wertung lässt die Karte kurz aufpoppen (der Wortwechsel bewegt
        # weiter unten nur den Text, damit das Fenster ruhig stehen bleibt)
        if self.puls:
            s1 = 1.0 + 0.045 * self.puls
            p.translate(cx, cy)
            p.scale(s1, s1)
            p.translate(-cx, -cy)

        # Echter Flip: Drehung um die Hochachse mit Perspektive
        if self.winkel:
            dreh = QTransform()
            dreh.translate(cx, cy)
            dreh.rotate(self.winkel, Qt.Axis.YAxis)
            dreh.translate(-cx, -cy)
            p.setTransform(dreh, True)

        halb = voll.width() / 2 * max(self.scale, 0.02)
        rect = QRectF(cx - halb, voll.y(), 2 * halb, voll.height())

        # Schatten nur im Ruhezustand (während der Bewegung flackert er sonst)
        if self.scale > 0.999 and not self.winkel:
            grund = qfarbe(t["schatten"])
            for i in range(SCHATTEN - 4, 0, -2):
                w = QColor(grund)
                w.setAlpha(int(grund.alpha() * (1 - i / SCHATTEN) ** 2 * 0.5))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(w)
                p.drawRoundedRect(rect.adjusted(-i, -i + 2, i, i + 2),
                                  RADIUS + i, RADIUS + i)
        flaeche = (blend(t["bg"], a.blitz, self.blitz_staerke * BLITZ_ANTEIL)
                   if a.blitz else t["bg"])
        p.setBrush(qfarbe(flaeche))
        p.setPen(QPen(qfarbe(t["rand"]), 1))
        p.drawRoundedRect(rect, RADIUS, RADIUS)

        if self.scale <= 0.12 or self.inhalt <= 0.02:
            return
        p.setOpacity(p.opacity() * self.inhalt)

        zeilen, groesse = self.wrapped(a.word[a.side])
        p.setFont(basisfont(max(1, groesse)))
        p.setPen(qfarbe(t["fg"]))
        textfeld = rect.adjusted(20, 20, -20, -20)
        p.setOpacity(p.opacity() * self.wort_alpha)
        if self.versatz:
            # Der Text zieht durch die Karte; ausserhalb wird abgeschnitten,
            # damit nichts über den Rand hinausläuft.
            beschnitt = QPainterPath()
            beschnitt.addRoundedRect(rect, RADIUS, RADIUS)
            p.save()
            p.setClipPath(beschnitt)
            p.translate(self.versatz * rect.width(), 0)
            p.drawText(textfeld, Qt.AlignmentFlag.AlignCenter, zeilen)
            p.restore()
        else:
            p.drawText(textfeld, Qt.AlignmentFlag.AlignCenter, zeilen)

        p.setOpacity(self.inhalt if self.start_anim >= 1.0
                     else self.inhalt * self.start_anim)
        ruhe = self.scale > 0.999 and abs(self.winkel) < 1
        for tag, bx, by, r in self.buttons():
            if tag == "back" and not a.history:
                continue
            x = cx + (bx - cx) * self.scale
            hv = self.hover_werte.get(tag, 0.0) if ruhe else 0.0
            if hv > 0.01:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(qfarbe(blend(t["bg"],
                                        MAC_ROT if tag == "close" else t["hover"],
                                        hv)))
                p.drawEllipse(QPointF(x, by), r * (0.82 + 0.18 * hv),
                              r * (0.82 + 0.18 * hv))
            grund = qfarbe(t["zweit"] if tag == "lang" else t["fg"])
            stift = (qfarbe(blend(t["fg"], MAC_ROT_SYMBOL, hv))
                     if tag == "close" else grund)
            p.setPen(QPen(stift, 1.7, c=Qt.PenCapStyle.RoundCap))
            for (x1, y1, x2, y2) in icon_segs(tag, r):
                p.drawLine(QPointF(x + x1 * self.scale, by + y1),
                           QPointF(x + x2 * self.scale, by + y2))
            if tag == "lang":
                p.setFont(basisfont(max(1, 11 * self.scale), fett=True))
                p.drawText(QRectF(x - r, by - r, 2 * r, 2 * r),
                           Qt.AlignmentFlag.AlignCenter, a.start_side.upper())

        if ruhe and a.countdown_frac:
            bw = (rect.width() - 120) * a.countdown_frac
            if bw > 5:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(qfarbe(t["timer"]))
                p.drawRoundedRect(QRectF(cx - bw / 2, rect.bottom() - 14,
                                         bw, 4), 2, 2)
        elif ruhe and a.update_hinweis():
            p.setFont(basisfont(11))
            p.setPen(qfarbe(t["zweit"]))
            p.drawText(QRectF(rect.x(), rect.bottom() - 26, rect.width(), 18),
                       Qt.AlignmentFlag.AlignCenter, a.update_hinweis())

    def wrapped(self, text):
        """Zeilenumbruch einmal bei voller Breite bestimmen und merken."""
        breite = int(self.karte_rect().width() - 76)
        groesse = self.wortgroesse(text)
        key = (text, groesse, breite)
        if key in self._wrapcache:
            return self._wrapcache[key]
        fm = QFontMetrics(basisfont(groesse))
        zeilen, cur = [], ""
        for token in text.split(" "):
            probe = token if not cur else cur + " " + token
            if cur and fm.horizontalAdvance(probe) > breite:
                zeilen.append(cur)
                cur = token
            else:
                cur = probe
        if cur:
            zeilen.append(cur)
        ergebnis = ("\n".join(zeilen), groesse)
        self._wrapcache[key] = ergebnis
        return ergebnis

    def wortgroesse(self, text):
        r = self.karte_rect()
        basis = min(r.width() / 19.0, r.height() / 11.5)
        n = len(text)
        if n > 70:
            basis *= 0.60
        elif n > 45:
            basis *= 0.74
        elif n > 28:
            basis *= 0.87
        return max(9, int(basis))

    # ---- Bewegungen
    def _ohne_animation(self, commit):
        commit()
        self.scale, self.winkel, self.versatz = 1.0, 0.0, 0.0
        self.inhalt, self.wort_alpha, self.puls = 1.0, 1.0, 0.0
        self.app.animating = False
        self.update()

    def uebergang(self, commit, richtung=+1):
        """Wortwechsel (weiter/zurück): Karte dreht sich; ist die
        Flip-Animation abgeschaltet, gleitet stattdessen nur das Wort."""
        if self.app.einst["flip_animation"]:
            self.drehe(commit, richtung)
        else:
            self.gleite(commit, richtung)

    def aufdecken(self, commit):
        """FR/DE aufdecken: Karte dreht sich; ist die Flip-Animation
        abgeschaltet, blendet das Wort nur um - beim Aufdecken bleibt es
        an Ort, seitliches Gleiten gehört zum Wortwechsel."""
        if self.app.einst["flip_animation"]:
            self.drehe(commit, +1)
        else:
            self.fade(commit)

    def fade(self, commit):
        """Wort weich aus- und mit neuem Inhalt wieder einblenden."""
        a = self.app
        if a.animating:
            return
        a.animating = True

        def schritt(w):
            if w < 0.5:
                self.wort_alpha = 1.0 - kurve(w * 2)
            else:
                self.wort_alpha = kurve((w - 0.5) * 2)
            self.update()

        def fertig():
            self.wort_alpha = 1.0
            a.animating = False
            self.update()

        self.anim = Ablauf(self, 260, schritt, mitte=commit, fertig=fertig)
        self.anim.start()

    def drehe(self, commit, richtung=+1):
        """Echter Flip: Die Karte dreht sich um die Hochachse, auf halbem Weg
        wechselt der Inhalt - vor und zurück in entgegengesetzter Richtung.
        Die zweite Hälfte läuft von -90 zurück, sonst stünde die Schrift
        spiegelverkehrt."""
        a = self.app
        if a.animating:
            return
        a.animating = True

        def schritt(w):
            t = kurve(w)
            grad = t * 180.0
            if grad > 90:
                grad -= 180.0
            self.winkel = richtung * grad
            # kurz vor der Kante ausblenden, dahinter wieder auf
            self.inhalt = min(1.0, abs(math.cos(math.radians(t * 180))) * 2.2)
            self.update()

        def fertig():
            self.winkel, self.inhalt = 0.0, 1.0
            a.animating = False
            self.update()

        self.anim = Ablauf(self, 400, schritt, mitte=commit, fertig=fertig)
        self.anim.start()

    def gleite(self, commit, richtung):
        """Wortwechsel: das alte Wort zieht zur Seite ab, das neue kommt von
        der anderen Seite herein - Richtung passend zu vor/zurück."""
        a = self.app
        if a.animating:
            return
        a.animating = True

        def schritt(w):
            if w < 0.5:
                t = kurve(w * 2)
                self.versatz = -richtung * 0.75 * t
                self.wort_alpha = 1.0 - t
            else:
                t = kurve((w - 0.5) * 2)
                self.versatz = richtung * 0.75 * (1.0 - t)
                self.wort_alpha = t
            self.update()

        def fertig():
            self.versatz, self.wort_alpha = 0.0, 1.0
            a.animating = False
            self.update()

        self.anim = Ablauf(self, 320, schritt, mitte=commit, fertig=fertig)
        self.anim.start()

    def pulse(self, dann):
        """Wertung: Farbe schwillt an, die Karte poppt kurz auf, dann weiter."""
        if not self.app.einst["flip_animation"]:
            self.blitz_staerke = 1.0
            self.update()
            QTimer.singleShot(BLITZ_MS, dann)
            return

        def schritt(w):
            self.blitz_staerke = min(1.0, w * 3) if w < 0.7 else \
                max(0.0, 1.0 - (w - 0.7) / 0.3)
            self.puls = math.sin(min(1.0, w * 1.6) * math.pi)
            self.update()

        def fertig():
            self.blitz_staerke, self.puls = 0.0, 0.0
            self.update()
            dann()

        self.anim_puls = Ablauf(self, 300, schritt, fertig=fertig)
        self.anim_puls.start()

    # ---- Maus
    def _kante(self, pos):
        r = self.karte_rect()
        k = self.KANTE
        seite = ""
        if abs(pos.y() - r.y()) <= k:
            seite += "n"
        elif abs(pos.y() - r.bottom()) <= k:
            seite += "s"
        if abs(pos.x() - r.x()) <= k:
            seite += "w"
        elif abs(pos.x() - r.right()) <= k:
            seite += "e"
        if not (r.adjusted(-k, -k, k, k).contains(pos)):
            return None
        return seite or None

    def _knopf(self, pos):
        for tag, bx, by, r in self.buttons():
            if tag == "back" and not self.app.history:
                continue
            if (pos.x() - bx) ** 2 + (pos.y() - by) ** 2 <= (r + 3) ** 2:
                return tag
        return None

    def mousePressEvent(self, e):
        self.app.set_active(True)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        pos = e.position()
        kante = self._kante(pos)
        if kante:
            self._resize = (kante, e.globalPosition().toPoint(),
                            self.geometry())
            return
        self._presse = pos
        self._zieh = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
        self._bewegt = False

    def mouseMoveEvent(self, e):
        pos = e.position()
        if self._resize:
            kante, start, geo = self._resize
            d = e.globalPosition().toPoint() - start
            x, y, b, h = geo.x(), geo.y(), geo.width(), geo.height()
            minb, minh = self.minimumWidth(), self.minimumHeight()
            if "e" in kante:
                b = max(minb, geo.width() + d.x())
            if "s" in kante:
                h = max(minh, geo.height() + d.y())
            if "w" in kante:
                b = max(minb, geo.width() - d.x())
                x = geo.x() + geo.width() - b
            if "n" in kante:
                h = max(minh, geo.height() - d.y())
                y = geo.y() + geo.height() - h
            self._wrapcache.clear()
            self.setGeometry(x, y, b, h)
            return
        if self._zieh is not None and e.buttons() & Qt.MouseButton.LeftButton:
            if self._presse is not None and \
                    (pos - self._presse).manhattanLength() > 5:
                self._bewegt = True
            if self._bewegt:
                self.move(e.globalPosition().toPoint() - self._zieh)
            return
        kante = self._kante(pos)
        if kante:
            zeiger = {"n": Qt.CursorShape.SizeVerCursor,
                      "s": Qt.CursorShape.SizeVerCursor,
                      "w": Qt.CursorShape.SizeHorCursor,
                      "e": Qt.CursorShape.SizeHorCursor,
                      "nw": Qt.CursorShape.SizeFDiagCursor,
                      "se": Qt.CursorShape.SizeFDiagCursor,
                      "ne": Qt.CursorShape.SizeBDiagCursor,
                      "sw": Qt.CursorShape.SizeBDiagCursor}[kante]
            self.setCursor(zeiger)
            neu = None
        else:
            neu = self._knopf(pos)
            self.setCursor(Qt.CursorShape.PointingHandCursor if neu
                           else Qt.CursorShape.ArrowCursor)
        if neu != self.hover:
            self.hover = neu
            self._hover_wecken()

    def mouseReleaseEvent(self, e):
        resize, self._resize = self._resize, None
        bewegt = getattr(self, "_bewegt", False)
        self._zieh = None
        self._presse = None
        if resize or bewegt:
            return
        knopf = self._knopf(e.position())
        a = self.app
        if knopf == "close":
            QApplication.instance().quit()
        elif knopf == "next":
            a.next_word()
        elif knopf == "back":
            a.go_back()
        elif knopf == "lang":
            a.toggle_start()
        elif self.karte_rect().contains(e.position()):
            a.flip()

    def keyPressEvent(self, e):
        if not self.app.taste(e.key()):
            super().keyPressEvent(e)

    def resizeEvent(self, _):
        self._wrapcache.clear()


# ---------------------------------------------------------------- Anwendung
class Tastenfilter(QObject):
    """Fängt Tastendrücke für die ganze Anwendung ab.

    Nötig, weil Qt die Pfeiltasten sonst für seine eigene Fokus-Navigation
    verbraucht, bevor sie beim Fenster ankommen - und damit die Tasten auch
    dann wirken, wenn gerade das Menü oder die Wörterliste vorne ist."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def eventFilter(self, ziel, ereignis):
        if ereignis.type() == QEvent.Type.KeyPress:
            if ereignis.key() == Qt.Key.Key_Escape:
                return False                  # schliesst das jeweilige Fenster
            if self.app.taste(ereignis.key()):
                return True
        return False


class Voci:
    def __init__(self, qapp):
        self.qapp = qapp
        self.einst = lade_einstellungen()
        self.faktoren = lade_faktoren()
        self.import_status = None       # Text im Sets-Tab (lädt/Fehler)
        self.import_ergebnis = None     # (name, vocab) aus dem Import-Faden
        self._sets_aufbauen()
        self.thema = self.einst["thema"]
        self.start_side = self.einst["startsprache"]
        self.side = self.start_side
        self.flips = 0
        self.idx = None
        self.idx = self.ziehe_wort()
        self.history = []
        self.undo_delta = None
        self.blitz = None
        self.animating = False
        self.countdown_frac = None
        self.auto_timer = None
        self.war_aktiv = True
        self.update_version = None
        self.update_status = None
        self.update_fertig = None
        self.menu = None
        self.liste = None
        self.hinweis = None
        self.warte_auf_taste = None      # "c"/"v"/"b" während der Neubelegung
        self.liste_sortierung = "wertung"

        self.karte = Karte(self)
        self.karte.setWindowTitle("")
        try:
            bild = QPixmap()
            bild.loadFromData(base64.b64decode(ICON_B64))
            qapp.setWindowIcon(QIcon(bild))
        except Exception:
            pass
        if not self.einst["immer_vorne"]:
            self._topmost(False)
        self.karte.show()
        self.karte.einblenden()
        self.karte.activateWindow()
        self.karte.setFocus()
        self._tastenfilter = Tastenfilter(self)
        qapp.installEventFilter(self._tastenfilter)
        if not self.einst["hinweis_gesehen"]:
            QTimer.singleShot(600, self.hinweis_zeigen)

        qapp.applicationStateChanged.connect(self._app_zustand)
        self._takt = QTimer()
        self._takt.timeout.connect(self._ui_takt)
        self._takt.start(500)
        self._starte_hintergrund()

    # ---- Tastatur
    def taste(self, key):
        """Eine Stelle für alle Tastenkürzel. Liefert True, wenn die Taste
        verbraucht wurde."""
        zeichen = chr(key).upper() if 32 <= key < 127 else None

        # Neue Wertungstaste aufnehmen (Klick auf eine Kachel im Menü)
        if self.warte_auf_taste:
            wofuer = self.warte_auf_taste
            self.warte_auf_taste = None
            belegt = FESTE_TASTEN | {self.einst["taste_%s" % w]
                                     for w in ("c", "v", "b") if w != wofuer}
            if zeichen and zeichen.isalpha() and zeichen not in belegt:
                self.einst["taste_%s" % wofuer] = zeichen
                speichere_einstellungen(self.einst)
            if self.menu and self.menu.isVisible():
                self.menu._bauen()
            return True

        for wofuer in ("c", "v", "b"):
            if zeichen and zeichen == self.einst["taste_%s" % wofuer]:
                self.bewerte(wofuer)
                return True
        if key == Qt.Key.Key_D:
            self.toggle_thema()
        elif key == Qt.Key.Key_U:
            self.update_starten()
        elif key == Qt.Key.Key_M:
            self.menu_umschalten()
        elif key == Qt.Key.Key_Left:
            self.go_back()
        elif key == Qt.Key.Key_Right:
            self.next_word()
        else:
            return False
        return True

    # ---- Fenster
    def _topmost(self, an):
        k = self.karte
        sichtbar = k.isVisible()
        k.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, an)
        if sichtbar:
            k.show()

    # ---- Sets
    def _sets_aufbauen(self):
        """Grundliste plus importierte Sets zu einer Wortliste verbinden;
        jedes Set kennt seine Indizes darin."""
        self.vocab = list(lade_vokabeln())
        self.sets = [{"id": "etape1", "name": "Étape 1",
                      "indizes": list(range(len(self.vocab))), "eigen": False}]
        for satz in lade_eigene_sets():
            start = len(self.vocab)
            self.vocab.extend(satz["vocab"])
            self.sets.append({"id": satz["id"], "name": satz["name"],
                              "indizes": list(range(start, len(self.vocab))),
                              "eigen": True})
        bekannt = {satz["id"] for satz in self.sets}
        self.einst["sets"] = sorted(set(self.einst["sets"]) & bekannt) \
            or ["etape1"]

    def set_importieren(self, pfad):
        """PDF im Hintergrund einlesen; das Ergebnis holt der UI-Takt ab."""
        if self.import_status == "lädt":
            return
        self.import_status = "lädt"
        self._menu_sets_auffrischen()

        def arbeit():
            try:
                self.import_ergebnis = pdf_importieren(pfad)
            except Exception as fehler:
                self.import_ergebnis = ("FEHLER", str(fehler))
        threading.Thread(target=arbeit, daemon=True).start()

    def _import_abschliessen(self):
        name, daten = self.import_ergebnis
        self.import_ergebnis = None
        if name == "FEHLER":
            self.import_status = "Import fehlgeschlagen: %s" % daten
            self._menu_sets_auffrischen()
            return
        kennung = speichere_eigenes_set(name, daten)
        self._sets_aufbauen()
        self.einst["sets"] = sorted(set(self.einst["sets"]) | {kennung})
        speichere_einstellungen(self.einst)
        self.import_status = "„%s“ importiert (%d Wörter)" % (name, len(daten))
        self.history.clear()
        self.undo_delta = None
        self.idx = self.ziehe_wort()
        self.karte.update()
        self._menu_sets_auffrischen()

    def set_loeschen(self, kennung):
        loesche_eigenes_set(kennung)
        self._sets_aufbauen()
        speichere_einstellungen(self.einst)
        self.history.clear()
        self.undo_delta = None
        self.idx = self.ziehe_wort()
        self.karte.update()
        self._menu_sets_auffrischen()

    def _menu_sets_auffrischen(self):
        if self.menu and self.menu.isVisible() and self.menu.tab == "sets":
            self.menu._bauen()
        if self.liste and self.liste.isVisible():
            self.liste._fuellen()

    # ---- Wortlogik (identisch zur bisherigen Fassung)
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
        """Gewichtete Zufallswahl: der Faktor eines Worts ist sein Gewicht."""
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
        self.history.append({"idx": self.idx, "delta": delta})
        if len(self.history) > HISTORY_MAX:
            self.history.pop(0)

    def next_word(self):
        if self.animating or self.blitz:
            return
        self.cancel_auto()
        self.remember(self.undo_delta)
        self.undo_delta = None
        neu = self.ziehe_wort()

        def commit():
            self.idx = neu
            self.flips = 0
            self.side = self.start_side
        self.karte.uebergang(commit, +1)

    def go_back(self):
        """Ein Wort zurück, in der gerade sichtbaren Sprache."""
        if not self.history or self.animating or self.blitz:
            return
        self.cancel_auto()
        eintrag = self.history.pop()
        self.undo_delta = eintrag["delta"]

        def commit():
            self.idx = eintrag["idx"]
            self.flips = 0
        self.karte.uebergang(commit, -1)

    def flip(self):
        if self.animating or self.blitz:
            return
        self.cancel_auto()

        def commit():
            self.side = "de" if self.side == "fr" else "fr"
            self.flips += 1
        self.karte.aufdecken(commit)

    def bewerte(self, taste):
        """c/v/b: Faktor anpassen, Karte aufleuchten lassen, weiter. Nach
        einem Zurück ersetzt die neue Wertung die alte."""
        if self.animating or self.blitz:
            return
        self.cancel_auto()
        delta = WERTUNG_DELTA[taste]
        alter_anteil = self.undo_delta or 0.0
        self.setze_faktor(self.idx, self.faktor(self.idx) - alter_anteil + delta)
        self.undo_delta = delta
        self.blitz = WERTUNG_BLITZ[taste]
        self.karte.pulse(self._blitz_ende)

    def _blitz_ende(self):
        self.blitz = None
        self.next_word()

    def toggle_start(self):
        if self.animating:
            return
        self.start_side = "de" if self.start_side == "fr" else "fr"
        self.einst["startsprache"] = self.start_side
        speichere_einstellungen(self.einst)
        if self.flips == 0 and self.side != self.start_side:

            def commit():
                self.side = self.start_side
            self.karte.aufdecken(commit)
        else:
            self.karte.update()

    def toggle_thema(self):
        self.thema = "dunkel" if self.thema == "hell" else "hell"
        self.einst["thema"] = self.thema
        speichere_einstellungen(self.einst)
        self.karte.update()
        self.menu_neu_aufbauen()

    def einstellung_kippen(self, name, schluessel):
        self.einst[schluessel] = not self.einst[schluessel]
        speichere_einstellungen(self.einst)
        if schluessel == "immer_vorne":
            self._topmost(self.einst[schluessel])
        self.karte.update()

    def schwere_kippen(self):
        self.einst["schwere_modus"] = not self.einst["schwere_modus"]
        speichere_einstellungen(self.einst)

    # ---- Auto-Weiter
    def _app_zustand(self, zustand):
        self.set_active(zustand == Qt.ApplicationState.ApplicationActive)

    def set_active(self, aktiv):
        if aktiv and not self.war_aktiv:
            self.cancel_auto()
        elif (not aktiv and self.war_aktiv and self.flips >= FLIPS_NEEDED
              and self.einst["auto_weiter"]):
            self.start_auto()
        self.war_aktiv = aktiv

    def start_auto(self):
        self.cancel_auto()
        self._auto_rest = int(self.einst["auto_dauer"]) * 1000
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self._auto_tick)
        self.auto_timer.start(100)

    def _auto_tick(self):
        self._auto_rest -= 100
        if self._auto_rest <= 0:
            self.cancel_auto()
            self.next_word()
            return
        self.countdown_frac = self._auto_rest / (int(self.einst["auto_dauer"]) * 1000)
        self.karte.update()

    def cancel_auto(self):
        if self.auto_timer:
            self.auto_timer.stop()
            self.auto_timer = None
        self.countdown_frac = None
        self.karte.update()

    # ---- Menü / Liste
    def menu_umschalten(self):
        if self.menu and self.menu.isVisible():
            self.menu.close()
            self.menu = None
            return
        self.menu = MenuFenster(self)
        self.menu.show()
        self.menu.einblenden()

    def menu_neu_aufbauen(self):
        if self.menu and self.menu.isVisible():
            tab = self.menu.tab
            pos = self.menu.pos()
            self.menu.close()
            self.menu = MenuFenster(self, tab)
            self.menu.move(pos)
            self.menu.show()
        if self.liste and self.liste.isVisible():
            pos = self.liste.pos()
            self.liste.close()
            self.liste = ListeFenster(self)
            self.liste.move(pos)
            self.liste.show()

    def hinweis_zeigen(self):
        self.hinweis = HinweisFenster(self)
        k = self.karte.frameGeometry()
        self.hinweis.move(k.center().x() - self.hinweis.width() // 2,
                          max(0, k.center().y() - self.hinweis.height() // 2))
        self.hinweis.show()
        self.hinweis.einblenden()

    def liste_zeigen(self):
        if self.liste and self.liste.isVisible():
            self.liste.raise_()
            return
        self.liste = ListeFenster(self)
        self.liste.show()
        self.liste.einblenden()

    # ---- Updates (Netz in Fäden, UI im Takt)
    def _starte_hintergrund(self):
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

    def update_hinweis(self):
        if self.update_status == "lädt":
            return "Update wird geladen …"
        if self.update_status == "fehlgeschlagen":
            return "Update fehlgeschlagen"
        if self.update_version:
            return "Update verfügbar · Taste u"
        return None

    def _ui_takt(self):
        if self.update_fertig:
            self._tauschen()
            return
        if self.import_ergebnis:
            self._import_abschliessen()
        self.karte.update()

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
            return
        self.qapp.quit()


def main():
    QApplication.setApplicationName("Voci")
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    voci = Voci(qapp)
    qapp.aboutToQuit.connect(lambda: None)
    rueckgabe = qapp.exec()
    del voci
    sys.exit(rueckgabe)


if __name__ == "__main__":
    main()
