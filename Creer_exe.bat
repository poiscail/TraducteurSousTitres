@echo off
rem Crée dist\TraducteurSousTitres.exe (aucun Python requis pour le lancer).
cd /d "%~dp0"
python -m pip install -q pyinstaller
python -c "import tkinterdnd2" 2>nul && set DND=--collect-all tkinterdnd2
python -m PyInstaller --noconfirm --onefile --windowed --name TraducteurSousTitres ^
  --icon icone.ico --add-data "icone.ico;." %DND% traducteur.py
pause
