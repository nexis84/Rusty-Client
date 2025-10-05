# RustyBot NSIS Installer Script
# NSIS handles file locking better than Inno Setup
# Download NSIS from: https://nsis.sourceforge.io/

!define PRODUCT_NAME "RustyBot"
!define PRODUCT_VERSION "1.5.0"
!define PRODUCT_PUBLISHER "Nexis84"
!define PRODUCT_WEB_SITE "https://github.com/nexis84/Rusty-Client"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

# Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"

# MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

# Welcome page
!insertmacro MUI_PAGE_WELCOME

# License page (optional - comment out if no license)
# !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

# Directory page
!insertmacro MUI_PAGE_DIRECTORY

# Instfiles page
!insertmacro MUI_PAGE_INSTFILES

# Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Launcher.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch RustyBot Launcher"
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

# Language
!insertmacro MUI_LANGUAGE "English"

# Installer attributes
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "installer_output\RustyBot_Setup_v${PRODUCT_VERSION}_NSIS.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

# Version info
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "LegalCopyright" "© 2025 ${PRODUCT_PUBLISHER}"

Section "MainSection" SEC01
  # Set output path
  SetOutPath "$INSTDIR"
  SetOverwrite on
  
  # Try to close running processes first
  DetailPrint "Checking for running RustyBot processes..."
  
  # Kill Main.exe
  nsExec::ExecToLog 'taskkill /F /T /IM Main.exe'
  Pop $0
  
  # Kill QtWebEngineProcess
  nsExec::ExecToLog 'taskkill /F /T /IM QtWebEngineProcess.exe'
  Pop $0
  
  # Kill Launcher
  nsExec::ExecToLog 'taskkill /F /T /IM Launcher.exe'
  Pop $0
  
  # Wait for processes to fully terminate
  Sleep 3000
  
  # CRITICAL: Use TryReboot flag for locked files
  # This tells NSIS to schedule file replacement on reboot if needed
  SetRebootFlag false
  
  # Install files
  DetailPrint "Installing application files..."
  
  File /r "dist\Main.dist\*.*"
  File "config.json"
  File "secure.env"
  File "README.md"
  File "SECURE_CREDENTIALS_SETUP.md"
  
  # Create launcher
  File "dist\Launcher.exe"
  
  # Create shortcuts
  DetailPrint "Creating shortcuts..."
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\Launcher.exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Launcher.exe"
  
  # Windows Defender exclusion
  DetailPrint "Adding Windows Defender exclusion..."
  nsExec::ExecToLog 'powershell -Command "Add-MpPreference -ExclusionPath \"$INSTDIR\" -ErrorAction SilentlyContinue"'
  Pop $0
  
  # Windows Firewall rules
  DetailPrint "Adding Windows Firewall rules..."
  nsExec::ExecToLog 'powershell -Command "New-NetFirewallRule -DisplayName \"RustyBot\" -Direction Inbound -Program \"$INSTDIR\Main.exe\" -Action Allow -Profile Any -ErrorAction SilentlyContinue"'
  Pop $0
  
  nsExec::ExecToLog 'powershell -Command "New-NetFirewallRule -DisplayName \"RustyBot Outbound\" -Direction Outbound -Program \"$INSTDIR\Main.exe\" -Action Allow -Profile Any -ErrorAction SilentlyContinue"'
  Pop $0
  
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Main.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  # Check if reboot is needed
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "Some files could not be replaced and a reboot is required to complete installation. Reboot now?" IDNO noreboot
    Reboot
  noreboot:
SectionEnd

Section Uninstall
  # Kill processes
  nsExec::ExecToLog 'taskkill /F /T /IM Main.exe'
  Pop $0
  nsExec::ExecToLog 'taskkill /F /T /IM QtWebEngineProcess.exe'
  Pop $0
  nsExec::ExecToLog 'taskkill /F /T /IM Launcher.exe'
  Pop $0
  
  Sleep 2000
  
  # Remove Defender exclusion
  nsExec::ExecToLog 'powershell -Command "Remove-MpPreference -ExclusionPath \"$INSTDIR\" -ErrorAction SilentlyContinue"'
  Pop $0
  
  # Remove Firewall rules
  nsExec::ExecToLog 'powershell -Command "Remove-NetFirewallRule -DisplayName \"RustyBot\" -ErrorAction SilentlyContinue"'
  Pop $0
  nsExec::ExecToLog 'powershell -Command "Remove-NetFirewallRule -DisplayName \"RustyBot Outbound\" -ErrorAction SilentlyContinue"'
  Pop $0
  
  # Delete files
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\*.*"
  
  # Delete shortcuts
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.*"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  
  # Remove directories
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir /r "$INSTDIR"
  
  # Remove registry keys
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  
  SetAutoClose true
SectionEnd
