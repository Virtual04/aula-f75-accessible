; Az AULA F75 beállítóprogram telepítője (Inno Setup 6).
; Fordítás a projektmappából: packaging\build.cmd

#define AppName "AULA F75 beállítások"
#define AppVersion "1.0.0"
#define AppExe "AULA F75 beallitasok.exe"
#define SourceDir "..\build\dist\AULA F75 beallitasok"

[Setup]
AppId={{6C1E2F4B-8A3D-4F7E-9B21-F75A11A0F75B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Virtual04
DefaultDirName={autopf}\AULA F75 beallitasok
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\build\installer
OutputBaseFilename=AULA_F75_beallitasok_telepito_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesEnvironment=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}

[Languages]
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"

[Tasks]
Name: "desktopicon"; Description: "Ikon létrehozása az &asztalon"; Flags: unchecked
Name: "addtopath"; Description: "Az f75 &parancs legyen elérhető bármelyik parancssorból"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; DestName: "Leiras.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Leírás"; Filename: "{app}\Leiras.txt"
Name: "{group}\{#AppName} eltávolítása"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Tasks: addtopath; Check: NeedsAddPath(ExpandConstant('{app}'))

[Run]
Filename: "{app}\{#AppExe}"; Description: "A program indítása most"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsAddPath(Dir: string): Boolean;
var
  Paths: string;
begin
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Paths) then
    Paths := '';
  Result := Pos(';' + Uppercase(Dir) + ';', ';' + Uppercase(Paths) + ';') = 0;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Paths, Dir: string;
  P: Integer;
begin
  { Eltávolításkor a programmappát kivesszük a felhasználó PATH-jából. }
  if CurUninstallStep <> usPostUninstall then
    Exit;
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Paths) then
    Exit;
  Dir := ExpandConstant('{app}');
  P := Pos(';' + Uppercase(Dir), Uppercase(Paths));
  if P > 0 then
  begin
    Delete(Paths, P, Length(Dir) + 1);
    RegWriteExpandStringValue(HKCU, 'Environment', 'Path', Paths);
  end;
end;
