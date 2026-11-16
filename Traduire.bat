@echo off
rem Double-clic : ouvre l'interface. Glisser un .srt dessus : l'ouvre pré-rempli.
start "" pythonw "%~dp0traducteur.py" %*
