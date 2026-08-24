# Voci – Vokabel-Karte, immer im Vordergrund

Kleines Flashcard-Fenster (wie der Taschenrechner im „Immer im Vordergrund"-Modus),
das die Französisch-Vokabeln aus *Reprise étape 1* abfragt (243 Wortpaare).

![Screenshot](docs/screenshot.png)

## Starten

Windows: **Doppelklick auf `Voci.pyw`** (Python von [python.org](https://www.python.org/downloads/)
muss installiert sein – tkinter ist da standardmässig dabei, es braucht keine
zusätzlichen Pakete). Es öffnet sich ohne Konsolenfenster.

Linux/macOS: `python3 Voci.pyw`

## Bedienung

| Aktion | Wirkung |
|---|---|
| Klick auf die Karte | flippt FR ↔ DE (funktioniert in beide Richtungen, beliebig oft) |
| Kreis unten rechts (→) | nächstes Wort |
| Kreis unten links (FR/DE) | Startsprache umschalten (Wort erscheint zuerst auf Deutsch statt Französisch) |
| Kreis oben rechts (×) | beenden |
| Karte ziehen | Fenster verschieben |

Das Fenster ist **immer im Vordergrund**, hat keinen Titel, kein Minimieren
und kein Maximieren, weisse Karte mit schwarzem Text in Graustufen und
abgerundete Ecken.

**Auto-Weiter:** Wenn man aus dem Fenster raustabbt, nachdem das aktuelle Wort
schon mehr als einmal geflippt wurde, kommt nach 5 Sekunden automatisch das
nächste Wort (ein dünner grauer Balken unten zählt runter) – ausser man tabbt
vorher wieder rein.

## Vokabeln ändern

Die Wortpaare liegen in `vokabeln.json` (`fr` / `de`). Nach einer Änderung
die App neu bauen (bettet die Vokabeln in `Voci.pyw` ein, damit die Datei
alleine per Doppelklick funktioniert):

```
python3 build/make_app.py
```

Quelle der Vokabeln: `Voca_étape_R1_BMV_B_2025` (Word-Dokument, Tabelle FR|DE).
