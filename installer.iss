; Script di esempio Inno Setup per l'installer PySide6

#define MyAppVersion "0.1.4"


[Setup]
AppId={{0f0058d8-3cc1-4707-b86a-ed74d880c26a}}
AppMutex=devlizmutex
AppName=Devliz
AppVersion={#MyAppVersion}
DefaultDirName={commonpf}\Devliz
DefaultGroupName=Devliz
OutputDir=Output
OutputBaseFilename=devliz-setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
SetupIconFile=resources\logo2.ico

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Files]
Source: "dist\devliz\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Devliz"; Filename: "{app}\devliz.exe"; IconFilename: "{app}\devliz.exe"

[Run]
Filename: "{app}\devliz.exe"; Description: "Avvia Devliz"; Flags: nowait postinstall skipifsilent
