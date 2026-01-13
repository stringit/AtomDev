; Script di esempio Inno Setup per l'installer PySide6

#define MyAppVersion "0.1.5"


[Setup]
AppId={{34B812EA-03AD-4748-832C-DFA0FB7830D4}}
AppMutex=atomdevmutex
AppName=AtomDev
AppVersion={#MyAppVersion}
DefaultDirName={commonpf}\AtomDev
DefaultGroupName=AtomDev
OutputDir=Output
OutputBaseFilename=atomdev-setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
SetupIconFile=resources\logo2.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Files]
Source: "dist\atomdev\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AtomDev"; Filename: "{app}\atomdev.exe"; IconFilename: "{app}\atomdev.exe"

[Run]
Filename: "{app}\atomdev.exe"; Description: "Avvia AtomDev"; Flags: nowait postinstall skipifsilent
