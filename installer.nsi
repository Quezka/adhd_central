; NSIS Installer Script for ADHD Central
; Professional Windows Installer with Modern UI
; 
; Download NSIS from: https://nsis.sourceforge.io/
; Then run: makensis installer.nsi

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ============================================
; Branding & Configuration
; ============================================

Name "ADHD Central"
OutFile "dist\ADHD Central Installer.exe"
InstallDir "$PROGRAMFILES\ADHD Central"
InstallDirRegKey HKCU "Software\ADHD Central" "InstallPath"

; Request admin privileges for all users
RequestExecutionLevel admin

; ============================================
; Visual Settings
; ============================================

; MUI Settings - Use Modern UI
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Set branding text
BrandingText "ADHD Central v1.0"

; ============================================
; Installer Sections
; ============================================

Section "Install ADHD Central" SEC_INSTALL
  SetOutPath "$INSTDIR"
  
  ; Copy the executable
  File "dist\ADHD Central.exe"
  
  ; Create Registry entries
  WriteRegStr HKCU "Software\ADHD Central" "InstallPath" $INSTDIR
  WriteRegStr HKCU "Software\ADHD Central" "Version" "1.0"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\ADHD Central"
  CreateShortCut "$SMPROGRAMS\ADHD Central\ADHD Central.lnk" \
                 "$INSTDIR\ADHD Central.exe" "" \
                 "$INSTDIR\ADHD Central.exe" 0
  CreateShortCut "$SMPROGRAMS\ADHD Central\Uninstall.lnk" \
                 "$INSTDIR\Uninstall.exe"
  
  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\ADHD Central.lnk" \
                 "$INSTDIR\ADHD Central.exe" "" \
                 "$INSTDIR\ADHD Central.exe" 0
  
  ; Add to Windows Autostart via Registry
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" \
    "ADHD Central" "$INSTDIR\ADHD Central.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Write to Add/Remove Programs
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "DisplayName" "ADHD Central"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "DisplayIcon" "$INSTDIR\ADHD Central.exe,0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "DisplayVersion" "1.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "Publisher" "Quezka"
  
  SectionGetSize ${SEC_INSTALL} $0
  IntOp $0 $0 / 1024
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central" \
    "EstimatedSize" $0
  
  DetailPrint "Installation completed successfully!"
SectionEnd

; ============================================
; Uninstaller Section
; ============================================

Section "Uninstall"
  ; Remove Start Menu shortcuts
  RMDir /r "$SMPROGRAMS\ADHD Central"
  
  ; Remove Desktop shortcut
  Delete "$DESKTOP\ADHD Central.lnk"
  
  ; Remove Autostart Registry Entry
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "ADHD Central"
  
  ; Remove installation directory and all files
  RMDir /r "$INSTDIR"
  
  ; Remove registry entries
  DeleteRegKey HKCU "Software\ADHD Central"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ADHD Central"
  
  DetailPrint "Uninstall completed!"
SectionEnd

; ============================================
; Installer Attributes
; ============================================

; Show details during installation
ShowInstDetails show
ShowUninstDetails show
