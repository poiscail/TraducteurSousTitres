; Installateur Windows (Inno Setup 6) : crée dist\TraducteurSousTitres-Setup.exe
; Compiler avec Creer_installateur.bat (après Creer_exe.bat).
#define Version "1.1.0"

[Setup]
AppId={{6B2E4C1A-7F3D-4E8B-9A21-5C0D3F8E7B42}
AppName=Traducteur de sous-titres
AppVersion={#Version}
AppPublisher=poiscail
AppPublisherURL=https://github.com/poiscail/TraducteurSousTitres
DefaultDirName={autopf}\TraducteurSousTitres
DefaultGroupName=Traducteur de sous-titres
; installation pour l'utilisateur courant : pas de droits administrateur demandés
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=dist
OutputBaseFilename=TraducteurSousTitres-Setup
SetupIconFile=icone.ico
UninstallDisplayIcon={app}\TraducteurSousTitres.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "bureau"; Description: "Créer un raccourci sur le Bureau"
Name: "clicdroit"; Description: "Ajouter « Traduire les sous-titres » au clic droit"

[Files]
Source: "dist\TraducteurSousTitres.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Traducteur de sous-titres"; Filename: "{app}\TraducteurSousTitres.exe"
Name: "{group}\Désinstaller"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Traducteur de sous-titres"; Filename: "{app}\TraducteurSousTitres.exe"; Tasks: bureau

[Run]
Filename: "{app}\TraducteurSousTitres.exe"; Parameters: "--installer-menu"; Flags: runhidden; Tasks: clicdroit
Filename: "{app}\TraducteurSousTitres.exe"; Description: "Lancer le traducteur"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\TraducteurSousTitres.exe"; Parameters: "--desinstaller-menu"; Flags: runhidden; RunOnceId: "menu"
