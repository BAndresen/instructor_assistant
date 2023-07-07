# Instruct Assistant App .exe compiler script for NSIS



# -------------------------------------
# Include Modern UI
	!include "MUI2.nsh"



# -------------------------------------
# General 

	Name "Instructor_Assistant"

# App name varible 
	!define APP_NAME "Instructor_Assistant"

# Output .exe file name
	OutFile "Instructor Assistant Windows Installer v0.1.0.exe"

	RequestExecutionLevel admin

# Abort warning for user
	!define MUI_ABORTWARNING

	Unicode True


# Default program install location
	#Var InstallDir  $LOCALAPPDATA\${APP_NAME}
	#InstallDir
	InstallDir "$LOCALAPPDATA\${APP_NAME}"

# Get installations folder from registry if available
	InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"


!define MUI_ICON "C:\Users\brend\PycharmProjects\instructor_assistant_app\assets\logo.ico"

!define MUI_UNICON "C:\Users\brend\PycharmProjects\instructor_assistant_app\assets\logo.ico"

# -------------------------------------
# Pages
	!insertmacro MUI_PAGE_WELCOME
	!define MUI_WELCOMEPAGE_TEXT "Welcome to the Instructor Assistant Installer"

	!insertmacro MUI_PAGE_LICENSE "C:\Users\brend\PycharmProjects\instructor_assistant_app\LICENSE.txt"
	!insertmacro MUI_PAGE_COMPONENTS
	!insertmacro MUI_PAGE_DIRECTORY
	!insertmacro MUI_PAGE_INSTFILES
	!insertmacro MUI_PAGE_FINISH
	  
	!insertmacro MUI_UNPAGE_CONFIRM
	!insertmacro MUI_UNPAGE_INSTFILES

	!insertmacro MUI_LANGUAGE "English"

# License 
	LicenseData "C:\Users\brend\PycharmProjects\instructor_assistant_app\LICENSE.txt"



# -------------------------------------
# Installer Sections 

Section "Instructor Assistant (required)" AppSec

	SetOutPath $INSTDIR

# Source file to crate "/r" for entire file directory
	File /r "C:\Users\brend\PycharmProjects\instructor_assistant_app\dist\instructor_assistant_app\"

# Write the installation path into the registry
	WriteRegStr HKLM "SOFTWARE\${APP_NAME}" "Install_Dir" "$INSTDIR"

# Write the uninstall keys for Windows
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
	
	#WriteRegStr HKCU "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${APP_NAME}\instructor_assistant_app.exe" "RUNASADMIN" 
	
	WriteUninstaller "$INSTDIR\uninstall.exe" 
   
SectionEnd

Section "Start Menu Shortcuts" Menu

# create a start menu .exe link
	#SetShellVarContext current
	

	
	#CreateDirectory "$SMPROGRAMS\${APP_NAME}"
	CreateShortcut "$SMPROGRAMS\Instructor Assistant.lnk" "$INSTDIR\instructor_assistant_app.exe"

	

SectionEnd


Section "Desktop Shortcuts" Desktop

# create a desktop .exe link
	#StrCpy $0 $INSTDIR ${APP_NAME}
	CreateShortcut "$DESKTOP\Instructor Assistant.lnk" "$INSTDIR\instructor_assistant_app.exe"
	#"$INSTDIR\${APP_NAME}\instructor_assistant_app.exe"
 

SectionEnd



# -------------------------------------
# Section descriptions for the User

	LangString DESC_AppSec ${LANG_ENGLISH} "Install the Main Application"
	LangString DESC_Menu ${LANG_ENGLISH} "Create a Start Menu Shortcut"
	LangString DESC_Desktop ${LANG_ENGLISH} "Create a Desktop Shortcut"

	;Assign language strings to sections
	!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN

	!insertmacro MUI_DESCRIPTION_TEXT ${AppSec} $(DESC_AppSec)
	!insertmacro MUI_DESCRIPTION_TEXT ${Menu} $(DESC_Menu)
	!insertmacro MUI_DESCRIPTION_TEXT ${Desktop} $(DESC_Desktop)

	!insertmacro MUI_FUNCTION_DESCRIPTION_END



# -------------------------------------
# Uninstaller

Section "Uninstall"


	# Remove registry keys
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
	DeleteRegKey HKLM SOFTWARE\Instructor_Assistant

	# Remove files and uninstaller
	RMDir /r $INSTDIR


	# Remove shortcuts, if any
	Delete "$SMPROGRAMS\Instructor Assistant.lnk"
	Delete "$DESKTOP\Instructor Assistant.lnk"

	# Remove directories
	#RMDir "$INSTDIR"

SectionEnd




