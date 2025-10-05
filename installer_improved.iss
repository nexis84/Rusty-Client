; RustyBot Professional Installer
; Inno Setup Script - Industry Standard Windows Installer
; Version: 1.4.0

#define MyAppName "RustyBot"
#define MyAppVersion "1.7.6.0"
#define MyAppPublisher "Nexis84"
#define MyAppURL "https://github.com/nexis84/Rusty-Client"
#define MyAppExeName "Launcher.exe"
#define MyAppDescription "Twitch Giveaway Bot for EVE Online"

[Setup]
; Application Information
AppId={{8F7A3B2C-1D4E-4F5A-9B8C-2E3D4F5A6B7C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppComments={#MyAppDescription}

; Installation Paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output Settings
OutputDir=installer_output
OutputBaseFilename=RustyBot_Setup_v{#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Installer UI
WizardStyle=modern

; Privileges & Architecture
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppDescription} Installer
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Uninstall
UninstallDisplayName={#MyAppName}
UninstallFilesDir={app}\uninstall

; Misc
AllowNoIcons=yes
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=auto
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "defenderexclusion"; Description: "Add Windows Defender exclusion (recommended)"; GroupDescription: "Security:"
Name: "firewallrule"; Description: "Add Windows Firewall rule (recommended)"; GroupDescription: "Security:"

[Files]
; Main Application Files - Launcher checks for updates
Source: "Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\RustyBot.exe"; DestDir: "{app}"; Flags: ignoreversion

; Configuration Files
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: ".tio.tokens.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Assets - Copy to main folders for runtime access
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Fonts\*"; DestDir: "{app}\Fonts"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "SECURE_CREDENTIALS_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch {#MyAppName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Configuration"; Filename: "notepad.exe"; Parameters: """{app}\config.json"""; Comment: "Edit configuration"
Name: "{group}\Documentation"; Filename: "{app}\README.md"; Comment: "Read documentation"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Comment: "Uninstall {#MyAppName}"

; Desktop Icon (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch {#MyAppName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
; Launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

; Open documentation
Filename: "{app}\README.md"; Description: "View README"; Flags: postinstall skipifsilent shellexec unchecked

[UninstallRun]
; Remove firewall rules on uninstall
Filename: "powershell.exe"; Parameters: "-Command ""Remove-NetFirewallRule -DisplayName 'RustyBot' -ErrorAction SilentlyContinue"""; Flags: runhidden; RunOnceId: "RemoveFirewallInbound"
Filename: "powershell.exe"; Parameters: "-Command ""Remove-NetFirewallRule -DisplayName 'RustyBot Outbound' -ErrorAction SilentlyContinue"""; Flags: runhidden; RunOnceId: "RemoveFirewallOutbound"

[Code]
var
  WelcomePage: TWizardPage;
  DefenderStatusLabel: TLabel;
  
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  InstallPath: String;
begin
  Result := True;
  
  // Add Windows Defender exclusion BEFORE extracting files
  InstallPath := ExpandConstant('{autopf}\{#MyAppName}');
  Log('Pre-adding Windows Defender exclusion for: ' + InstallPath);
  
  if Exec('powershell.exe', '-Command "Add-MpPreference -ExclusionPath ''' + InstallPath + ''' -ErrorAction SilentlyContinue"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Log('Windows Defender exclusion pre-added successfully')
    else
      Log('Warning: Failed to pre-add Windows Defender exclusion (Code: ' + IntToStr(ResultCode) + ')');
  end
  else
    Log('Warning: Could not execute PowerShell to pre-add Defender exclusion');
  
  // PyInstaller bundles all required dependencies, no additional checks needed
end;

procedure InitializeWizard();
var
  WelcomeLabel: TLabel;
  FeatureLabel: TLabel;
begin
  // Custom welcome message
  WelcomeLabel := TLabel.Create(WizardForm);
  WelcomeLabel.Parent := WizardForm.WelcomePage;
  WelcomeLabel.Caption := 
    'This wizard will install RustyBot on your computer.' + #13#10 + #13#10 +
    'RustyBot is a Twitch giveaway bot with:' + #13#10 +
    '  • Beautiful animated interface' + #13#10 +
    '  • Encrypted credential storage' + #13#10 +
    '  • Automatic updates' + #13#10 +
    '  • EVE Online integration' + #13#10 + #13#10 +
    'IMPORTANT: This installer will:' + #13#10 +
    '  ✓ Add Windows Defender exclusion (prevents false positives)' + #13#10 +
    '  ✓ Configure Windows Firewall (allows network access)' + #13#10 +
    '  ✓ Create desktop & start menu shortcuts' + #13#10 + #13#10 +
    'Administrator privileges are required for security settings.' + #13#10 + #13#10 +
    'Click Next to continue.';
  WelcomeLabel.Left := WizardForm.WelcomeLabel2.Left;
  WelcomeLabel.Top := WizardForm.WelcomeLabel2.Top + WizardForm.WelcomeLabel2.Height + 20;
  WelcomeLabel.Width := WizardForm.WelcomeLabel2.Width;
  WelcomeLabel.Height := 280;
  WelcomeLabel.WordWrap := True;
  WelcomeLabel.AutoSize := False;
  
  // Hide the default welcome label
  WizardForm.WelcomeLabel2.Visible := False;
end;

procedure AddWindowsDefenderExclusion();
var
  ResultCode: Integer;
  InstallPath: String;
begin
  if IsTaskSelected('defenderexclusion') then
  begin
    InstallPath := ExpandConstant('{app}');
    Log('Adding Windows Defender exclusion for: ' + InstallPath);
    
    if Exec('powershell.exe', '-Command "Add-MpPreference -ExclusionPath ''' + InstallPath + ''' -ErrorAction SilentlyContinue"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      if ResultCode = 0 then
        Log('Windows Defender exclusion added successfully')
      else
        Log('Warning: Failed to add Windows Defender exclusion (Code: ' + IntToStr(ResultCode) + ')');
    end
    else
      Log('Warning: Could not execute PowerShell to add Defender exclusion');
  end;
end;

procedure AddWindowsFirewallRule();
var
  ResultCode: Integer;
  ExePath: String;
begin
  if IsTaskSelected('firewallrule') then
  begin
  ExePath := ExpandConstant('{app}\{#MyAppExeName}');
    Log('Adding Windows Firewall rule for: ' + ExePath);
    
    // Inbound rule
    Exec('powershell.exe', '-Command "New-NetFirewallRule -DisplayName ''RustyBot'' -Direction Inbound -Program ''' + ExePath + ''' -Action Allow -Profile Any -ErrorAction SilentlyContinue"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Outbound rule  
    Exec('powershell.exe', '-Command "New-NetFirewallRule -DisplayName ''RustyBot Outbound'' -Direction Outbound -Program ''' + ExePath + ''' -Action Allow -Profile Any -ErrorAction SilentlyContinue"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    Log('Firewall rules added');
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Add Windows Defender exclusion after files are copied
    AddWindowsDefenderExclusion();
    
    // Add Windows Firewall rule
    AddWindowsFirewallRule();
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  NeedsRestart := False;
  
  // Terminate any running RustyBot processes right before installation
  // Note: We don't kill Launcher.exe here because the user might have launched the installer from it
  Log('Terminating running RustyBot processes...');
  Exec('taskkill', '/F /IM RustyBot.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('Terminated RustyBot.exe (if running)');
  Exec('taskkill', '/F /IM QtWebEngineProcess.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Log('Terminated QtWebEngineProcess.exe (if running)');
  Sleep(1000); // Wait for processes to fully terminate and release file handles
  Log('Process termination complete, ready to install');
  
  // Return empty string means success - continue with installation
  Result := '';
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
  UninstallPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    UninstallPath := ExpandConstant('{app}');
    
    // Remove Windows Defender exclusion
    Log('Removing Windows Defender exclusion for: ' + UninstallPath);
    Exec('powershell.exe',
      Format('-Command "Remove-MpPreference -ExclusionPath ''%s'' -ErrorAction SilentlyContinue"', [UninstallPath]),
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Ask if user wants to keep configuration files
    if MsgBox('Do you want to keep your configuration and credential files?' + #13#10 + #13#10 +
              'Choose Yes to keep your settings for future reinstallation.' + #13#10 +
              'Choose No to completely remove all RustyBot data.',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      // Delete config files
      DeleteFile(UninstallPath + '\config.json');
      DeleteFile(UninstallPath + '\.env');
      Log('Configuration files deleted');
    end
    else
      Log('Configuration files kept');
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  if MsgBox('Are you sure you want to uninstall RustyBot?', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;

procedure DeinitializeUninstall();
var
  ErrorCode: Integer;
begin
  if MsgBox('RustyBot has been uninstalled successfully.' + #13#10 + #13#10 +
            'Thank you for using RustyBot!' + #13#10 + #13#10 +
            'Would you like to visit the GitHub page?',
            mbInformation, MB_YESNO) = IDYES then
  begin
    ShellExec('open', '{#MyAppURL}', '', '', SW_SHOW, ewNoWait, ErrorCode);
  end;
end;
