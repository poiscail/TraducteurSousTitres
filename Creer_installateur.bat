@echo off
rem Crée dist\TraducteurSousTitres-Setup.exe (installateur avec raccourcis Bureau et menu Démarrer).
rem Demande Inno Setup 6 : winget install JRSoftware.InnoSetup
cd /d "%~dp0"
if not exist dist\TraducteurSousTitres.exe call Creer_exe.bat
set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" (
  echo Inno Setup 6 introuvable : winget install JRSoftware.InnoSetup
  pause
  exit /b 1
)
"%ISCC%" installateur.iss
pause
