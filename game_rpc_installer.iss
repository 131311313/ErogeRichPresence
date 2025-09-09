[Setup]
AppName=Game Rich Presence
AppVersion=1.0.0
DefaultDirName={autopf}\GameRichPresence
DefaultGroupName=Game Rich Presence
OutputDir=Output
OutputBaseFilename=GameRichPresence_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ECHO は <OFF> です。
[Files]
Source: "dist\GameRichPresence.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\icon.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
ECHO は <OFF> です。
[Icons]
Name: "{group}\Game Rich Presence"; Filename: "{app}\GameRichPresence.exe"
Name: "{group}\{cm:UninstallProgram,Game Rich Presence}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Game Rich Presence"; Filename: "{app}\GameRichPresence.exe"; Tasks: desktopicon
ECHO は <OFF> です。
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start with Windows"; GroupDescription: "Startup Options"
ECHO は <OFF> です。
[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "GameRichPresence"; ValueData: "{app}\GameRichPresence.exe"; Flags: uninsdeletevalue; Tasks: startup
ECHO は <OFF> です。
[Run]
Filename: "{app}\GameRichPresence.exe"; Description: "{cm:LaunchProgram,Game Rich Presence}"; Flags: nowait postinstall skipifsilent
