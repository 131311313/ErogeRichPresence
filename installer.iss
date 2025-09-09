[Setup]
AppName=ErogeRichPresence
AppVersion=1.0
DefaultDirName={autopf}\ErogeRichPresence
DefaultGroupName=ErogeRichPresence
OutputDir=Output
OutputBaseFilename=ErogeRichPresence_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\ErogeRichPresence.exe
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start with Windows"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "ErogeRichPresence.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ErogeRichPresence"; Filename: "{app}\ErogeRichPresence.exe"
Name: "{group}\{cm:UninstallProgram,ErogeRichPresence}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ErogeRichPresence"; Filename: "{app}\ErogeRichPresence.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ErogeRichPresence"; ValueData: "{app}\ErogeRichPresence.exe"; Tasks: startup

[Run]
Filename: "{app}\ErogeRichPresence.exe"; Description: "{cm:LaunchProgram,ErogeRichPresence}"; Flags: nowait postinstall skipifsilent
