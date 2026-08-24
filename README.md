# Voci – Vokabel-Karte, immer im Vordergrund

Kleines Flashcard-Fenster (wie der Taschenrechner im „Immer im Vordergrund"-Modus),
das die Französisch-Vokabeln aus *Reprise étape 1* abfragt (243 Wortpaare).
Läuft unter Windows, macOS und Linux.

![Screenshot](docs/screenshot.png)

## Herunterladen

Unter **[Releases → latest](../../releases/latest)** liegen die fertigen Dateien:

| Datei | Für wen |
|---|---|
| `Voci.exe` | Windows, eine einzige Datei. Herunterladen, doppelklicken, **kein Python nötig**. |
| `Voci-Windows-Ordner.zip` | Windows-Alternative, falls ein Virenscanner die EXE anmeckert. Entpacken, `Voci.exe` im Ordner starten. |
| `Voci-macOS.zip` | macOS mit Apple Silicon (M1–M4). Entpacken, `Voci.app` starten. |
| `Voci.pyw` | Alle Systeme mit installiertem Python – die einzige Variante ganz ohne Warnung. |

Auf **Intel-Macs** läuft die `Voci-macOS.zip` nicht; dort nimmst du die `Voci.pyw`
und startest sie mit `python3 Voci.pyw`.

Alles wird bei jeder Änderung automatisch von GitHub Actions neu gebaut
(siehe `.github/workflows/build.yml`).

### Windows warnt beim ersten Start

Beim Start der EXE kommt **„Der Computer wurde durch Windows geschützt"**. Das ist
keine Virenmeldung — Windows warnt bei jedem Programm ohne gekauftes
Signaturzertifikat. Zwei Wege daran vorbei:

- Im Warnfenster auf **Weitere Informationen** → **Trotzdem ausführen**.
- Oder vorher: Rechtsklick auf die heruntergeladene `Voci.exe` → **Eigenschaften**
  → unten bei *Sicherheit* den Haken bei **Zulassen** setzen → **OK**.

### macOS warnt beim ersten Start

**„Voci" kann nicht geöffnet werden, da Apple es nicht auf Schadsoftware
überprüfen kann.** Auch das ist keine Virenmeldung, sondern die fehlende
Apple-Signatur (99 USD pro Jahr für ein Entwicklerkonto).

- **macOS 15 (Sequoia) und neuer:** Doppelklick, Meldung wegklicken, dann
  **Systemeinstellungen → Datenschutz & Sicherheit** öffnen, ganz nach unten
  scrollen und dort **Dennoch öffnen** wählen (mit Touch ID oder Passwort
  bestätigen).
- **macOS 14 und älter:** Rechtsklick (oder Ctrl-Klick) auf `Voci.app` →
  **Öffnen** → im Dialog nochmals **Öffnen**.
- **Per Terminal:** `xattr -dr com.apple.quarantine /Pfad/zu/Voci.app`

Beides ist einmal pro heruntergeladener Datei nötig. Ganz wegbekommen liesse sich
die Warnung nur über den jeweiligen App-Store: Laut
[Microsofts Vergleich der Signatur-Optionen](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)
bauen selbst gekaufte OV- und EV-Zertifikate ihre Reputation erst über Zeit auf —
seit 2024 umgeht auch EV die SmartScreen-Warnung nicht mehr sofort.

Gegen **Virenscanner-Fehlalarme** (etwas anderes als die Warnungen oben) ist die
EXE bereits so gebaut, wie es empfohlen wird: mit Icon, mit Versionsinformationen
und ohne UPX-Komprimierung. Falls ein Scanner trotzdem anschlägt, nimm die
Ordner-Variante — die packt sich beim Start nicht selbst aus und fällt Heuristiken
seltener auf.

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
zählen nicht als Schritt. Das vorherige Wort erscheint in der Sprache, die
gerade angezeigt wird: Ist man gerade auf DE, kommt es auf DE, egal wie man es
verlassen hat. Maximal 10 Wörter; ohne Historie ist der Knopf ausgeblendet.

Beim Flip staucht sich die ganze Karte – Knöpfe und Text gehen mit. Die Zeilen
des Textes stehen dabei fest, es skaliert nur die Schrift, damit nichts
umspringt.

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

## Icon

Das App-Icon (Trikolore) wird aus `build/make_icons.py` erzeugt und liegt als
`assets/voci.png`, `assets/voci.ico` (Windows) und `assets/voci.icns` (macOS) im
Repo. Nach einer Änderung neu erzeugen mit `python build/make_icons.py`.
