; Inno Setup Script for Bank Statement Extractor
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#define AppName "Bank Statement Extractor"
#define AppExeName "BankStatementExtractor.exe"
#define AppFolderName "BankStatementExtractor"
#define AppInstallerName "BankStatementExtractorSetup-" + AppVersion

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
DefaultDirName={autopf}\{#AppFolderName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
PrivilegesRequired=admin
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename={#AppInstallerName}
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} Installer

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\BankStatementExtractor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
