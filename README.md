# Voci – Vokabel-Karte, immer im Vordergrund

Kleines Flashcard-Fenster (wie der Taschenrechner im „Immer im Vordergrund"-Modus),
das die Französisch-Vokabeln aus *Reprise étape 1* abfragt (243 Wortpaare).

![Screenshot](docs/screenshot.png)

## Herunterladen

Unter **[Releases → latest](../../releases/latest)** liegen zwei Dateien:

| Datei | Wofür |
|---|---|
| `Voci.exe` | Einfach herunterladen und doppelklicken – **kein Python nötig**. |
| `Voci.pyw` | Die Python-Variante, eine einzige Datei. Braucht ein installiertes Python. |

Die Dateien werden bei jeder Änderung automatisch von GitHub Actions neu gebaut
(siehe `.github/workflows/build.yml`). Beim ersten Start der `.exe` zeigt Windows
eventuell „Der Computer wurde geschützt" – das ist normal bei unsignierten
Programmen: *Weitere Informationen* → *Trotzdem ausführen*.

Wer lieber die `.pyw` nimmt: Python von [python.org](https://www.python.org/downloads/)
installieren (Häkchen bei **„Add Python to PATH"** setzen), dann Doppelklick.
Zusätzliche Pakete braucht es keine – tkinter ist bei Python dabei.

## Bedienung

| Aktion | Wirkung |
|---|---|
| Klick auf die Karte | flippt FR ↔ DE (in beide Richtungen, beliebig oft) |
| Kreis oben links (FR/DE) | Startsprache umschalten |
| Kreis oben rechts (×) | beenden |
| Kreis unten links (←) | ein Wort zurück (max. 10) |
| Kreis unten rechts (→) | nächstes Wort |
| Karte ziehen | Fenster verschieben |
| Rand/Ecke ziehen | Fenster grösser/kleiner ziehen |

Der **Zurück-Knopf springt ein Wort zurück** – Flips und der Sprachumschalter
zählen nicht als Schritt. Das vorherige Wort erscheint genau so, wie man es
verlassen hat: War es auf FR sichtbar, kommt es auf FR zurück, auch wenn die
Startsprache inzwischen auf DE steht. Maximal 10 Wörter; ohne Historie ist der
Knopf ausgeblendet.

Beim Flip staucht sich die ganze Karte – Knöpfe und Text gehen mit, der Text
bricht dabei laufend neu um.

Das Fenster ist **immer im Vordergrund**, hat keinen Titel, kein Minimieren und
kein Maximieren, weisse Karte mit schwarzem Text in Graustufen, abgerundete Ecken
und randlose Knöpfe, die nur beim Draufzeigen grau werden.

**Auto-Weiter:** Tabbt man aus dem Fenster raus, nachdem das aktuelle Wort schon
mehr als einmal geflippt wurde, kommt nach 5 Sekunden automatisch das nächste Wort
(ein feiner Balken unten zählt runter) – ausser man tabbt vorher wieder rein.

## Vokabeln ändern

Die Wortpaare liegen in `vokabeln.json` (`fr` / `de`). Nach einer Änderung die App
neu bauen – das bettet die Vokabeln in `Voci.pyw` ein, damit die Datei alleine
lauffähig ist:

```
python build/make_app.py
```

Beim Push auf `main` baut GitHub Actions daraus automatisch eine neue `Voci.exe`.

Quelle der Vokabeln: `Voca_étape_R1_BMV_B_2025` (Word-Dokument, Tabelle FR|DE).
