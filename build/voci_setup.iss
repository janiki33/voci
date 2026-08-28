; Inno-Setup-Skript für Voci.
;
; Legt die Ordnerfassung an einem festen Ort ab, damit der Updater weiss, wo er
; die Dateien austauschen muss - beim Entpacken einer ZIP in den Download-Ordner
; ist das nicht verlässlich. Standardziel ist der Benutzerbereich, damit weder
; Installation noch Update Administratorrechte brauchen (wichtig auf Schul-PCs);
; das Ziel lässt sich im Setup frei ändern.

#define Name "Voci"
#define Beschreibung "Voci - Vokabeltrainer Französisch/Deutsch"
#define Herausgeber "Janosch Salzgeber"
#ifndef Version
  #define Version "1.0.0"
#endif

[Setup]
AppId={{7F2C1E4A-9B3D-4C58-A6E1-VOCI00000001}
AppName={#Name}
AppVersion={#Version}
AppVerName={#Name}
AppPublisher={#Herausgeber}
VersionInfoDescription={#Beschreibung}
VersionInfoVersion=1.0.0.0
DefaultDirName={autopf}\{#Name}
DefaultGroupName={#Name}
DisableProgramGroupPage=yes
AllowNoIcons=yes
; Ohne Adminrechte installieren; wer will, kann im Setup für alle Nutzer wählen
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=Voci-Setup
SetupIconFile=..\assets\voci.ico
UninstallDisplayIcon={app}\Voci.exe
UninstallDisplayName={#Name}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Der Zielordner soll frei wählbar bleiben
DisableDirPage=no
DirExistsWarning=no

[Languages]
Name: "deutsch"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Verknüpfung auf dem Desktop anlegen"; \
    GroupDescription: "Zusätzliche Verknüpfungen:"
Name: "startmenu"; Description: "Eintrag im Startmenü anlegen"; \
    GroupDescription: "Zusätzliche Verknüpfungen:"
Name: "autostart"; Description: "Voci beim Anmelden automatisch starten"; \
    GroupDescription: "Zusätzliche Verknüpfungen:"; Flags: unchecked

[Files]
Source: "..\setup-quelle\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#Name}"; Filename: "{app}\Voci.exe"; Tasks: startmenu
Name: "{autodesktop}\{#Name}"; Filename: "{app}\Voci.exe"; Tasks: desktopicon
Name: "{userstartup}\{#Name}"; Filename: "{app}\Voci.exe"; Tasks: autostart

[Run]
Filename: "{app}\Voci.exe"; Description: "Voci jetzt starten"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Der Updater tauscht Dateien im Programmordner aus; die Reste sollen beim
; Deinstallieren mitgehen.
Type: filesandordirs; Name: "{app}"
