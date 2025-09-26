; installer.iss
[Setup]
AppId={{bec9e34f-e344-4fb2-a074-8ec1b1ce8ec8}}
AppName=Sylo
AppVersion=1.0.0
AppPublisher=Java2Tech
DefaultDirName={autopf}\Sylo
DefaultGroupName=Sylo
OutputBaseFilename=Sylo-Setup-1.0.0
OutputDir=.\dist
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\Sylo.exe
SetupLogging=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Files]
Source: ".\src\build\windows\*"; DestDir: "{app}"; \
    Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Sylo"; Filename: "{app}\Sylo.exe"
Name: "{autodesktop}\Sylo"; Filename: "{app}\Sylo.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 작업:"

[Run]
Filename: "{app}\Sylo.exe"; Description: "설치 후 Sylo 실행"; Flags: nowait postinstall skipifsilent
