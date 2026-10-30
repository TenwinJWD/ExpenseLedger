; Daily Fresh setup wizard (Inno Setup 6). Built by build.ps1:
;   ISCC.exe /DAppVersion=1.2.3 /DDistDir=<PyInstaller output\ExpenseLedger> /O<output folder> DailyFresh.iss
;
; Pages: language-free modern wizard with Welcome, License, install scope (just me / all users), folder,
; shortcut choices, progress, and a Finish page with "Launch Daily Fresh". Installing over an older version
; upgrades it in place and closes the running app first. Uninstall is in Settings > Apps.
; Entries and sub-heads are never touched; uninstalling removes only the login file, as the MSI did.
;
; AppId must never change, or Windows treats a new version as a different program (a test guards it).

#ifndef AppVersion
  #error Pass /DAppVersion=x.y.z
#endif
#ifndef DistDir
  #error Pass /DDistDir=<PyInstaller output folder>
#endif

#define AppName "Daily Fresh"
#define AppExe "ExpenseLedger.exe"
#define CertFile "TenwinJames-CodeSigning.cer"
#define CertThumbprint "32A107DC9E44CEC16E4E5FA71864431976967E92"

[Setup]
AppId={{B7F3A9E2-6C41-4D58-9E0A-3F5C1D7A8B24}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Tenwin James
VersionInfoVersion={#AppVersion}.0
VersionInfoProductName={#AppName}
VersionInfoDescription={#AppName} setup
DefaultDirName={autopf}\ExpenseLedger
DefaultGroupName={#AppName}
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
LicenseFile=License.rtf
SetupIconFile=..\assets\app.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
WizardStyle=modern
WizardImageFile=wizard-large.bmp
WizardSmallImageFile=wizard-small.bmp
OutputBaseFilename=ExpenseLedger-Setup-{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Ask "install for all users or just me" at the start; just-me needs no administrator approval.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=no
ShowLanguageDialog=no

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Shortcuts:"
; Off by default and offered only for an all-users install (it changes the PC's certificate stores).
Name: "trustcert"; Description: "&Trust the Tenwin James publisher certificate on this PC (thumbprint {#CertThumbprint})"; GroupDescription: "Publisher:"; Flags: unchecked; Check: IsAdminInstallMode

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "{#CertFile}"; DestDir: "{tmp}"; Flags: deleteafterinstall; Tasks: trustcert

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: startmenuicon
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{sys}\certutil.exe"; Parameters: "-f -addstore TrustedPublisher ""{tmp}\{#CertFile}"""; Flags: runhidden waituntilterminated; Tasks: trustcert; StatusMsg: "Trusting the publisher certificate..."
Filename: "{sys}\certutil.exe"; Parameters: "-f -addstore Root ""{tmp}\{#CertFile}"""; Flags: runhidden waituntilterminated; Tasks: trustcert
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\certutil.exe"; Parameters: "-delstore TrustedPublisher {#CertThumbprint}"; Flags: runhidden; RunOnceId: "UntrustCertPublisher"; Tasks: trustcert
Filename: "{sys}\certutil.exe"; Parameters: "-delstore Root {#CertThumbprint}"; Flags: runhidden; RunOnceId: "UntrustCertRoot"; Tasks: trustcert

[Code]
{ The login file goes on uninstall (as the MSI did); entries, sub-heads and settings stay. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    DeleteFile(ExpandConstant('{userappdata}\ExpenseLedger\account.json'));
end;

{ Versions up to 1.0.2 were installed with Windows Installer (.msi). Two copies must not sit side by side,
  so the old one is removed first. Nothing in the data folder or AppData is touched. }
function FindMsiProductCode(var ProductCode: String): Boolean;
var
  Roots: array[0..2] of Integer;
  Names: TArrayOfString;
  Root, I: Integer;
  Installer: Cardinal;
  Path, DisplayName: String;
begin
  Result := False;
  Roots[0] := HKLM64;
  Roots[1] := HKLM32;
  Roots[2] := HKCU;
  Path := 'Software\Microsoft\Windows\CurrentVersion\Uninstall';
  for Root := 0 to 2 do
    if RegGetSubkeyNames(Roots[Root], Path, Names) then
      for I := 0 to GetArrayLength(Names) - 1 do
        if (Copy(Names[I], 1, 1) = '{') and
           RegQueryStringValue(Roots[Root], Path + '\' + Names[I], 'DisplayName', DisplayName) and
           (DisplayName = '{#AppName}') and
           RegQueryDWordValue(Roots[Root], Path + '\' + Names[I], 'WindowsInstaller', Installer) and (Installer = 1) then
        begin
          ProductCode := Names[I];
          Result := True;
          Exit;
        end;
end;

function InitializeSetup(): Boolean;
var
  ProductCode: String;
  ResultCode: Integer;
begin
  Result := True;
  if FindMsiProductCode(ProductCode) then
  begin
    if MsgBox('An earlier version of {#AppName} was installed with a different installer.' + #13#10 +
              'It will be removed first. Your entries and settings are kept.' + #13#10#13#10 + 'Continue?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
    if (not Exec('msiexec.exe', '/x ' + ProductCode + ' /passive /norestart', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode))
       or ((ResultCode <> 0) and (ResultCode <> 3010)) then
    begin
      MsgBox('The earlier version could not be removed (code ' + IntToStr(ResultCode) + '). Please uninstall it from Settings > Apps, then run this setup again.',
             mbError, MB_OK);
      Result := False;
    end;
  end;
end;
