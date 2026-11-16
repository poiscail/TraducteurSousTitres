# Traducteur de sous-titres

Traduit des sous-titres `.srt`, `.vtt` ou `.ass` (ou ceux d'une vidéo `.mkv`/`.mp4`) vers une ou plusieurs
langues en gardant exactement les numéros et les timings.
Le résultat est un nouveau fichier : `film.srt` devient `film.fr.srt`. Une traduction existante n'est jamais
écrasée : la suivante s'appelle `film.fr (2).srt`.

- Moteurs : Google (gratuit, sans clé), DeepL (clé gratuite sur deepl.com/pro-api), Argos (hors ligne).
- Plusieurs langues cibles d'un coup. Langue d'origine détectée automatiquement, ou choisie.
- Glossaire : termes jamais traduits (noms propres) ou toujours traduits pareil.
- Aperçu avant d'enregistrer : original et traduction côte à côte, double-clic pour corriger.
- Réparation optionnelle : renumérote, retire doublons et sous-titres vides, corrige les chevauchements.
- Décalage de tous les timings (ex. +1,5 s ou -2 s) et conversion SRT / VTT / ASS, avec ou sans traduction.
- Intégration de la traduction dans la vidéo, en nouvelle piste de sous-titres (`film.fr.mkv`, ffmpeg requis).
- Prévient quand une nouvelle version est publiée sur GitHub.
- Bouton « Arrêter », thème sombre, fenêtre redimensionnable.
- Garde les balises `<i>`, `<b>`, `{\an8}`…, coupe en deux les lignes trop longues (plus de 42 caractères).
- Lit l'UTF-8 et le Windows-1252, écrit en UTF-8. Réessaie seul si le service limite.

## Installation

1. Installer [Python 3.10+](https://www.python.org/downloads/) (cocher « Add to PATH »).
2. Aucune autre dépendance. En option :
   - `pip install tkinterdnd2` pour glisser des fichiers dans la fenêtre ;
   - `pip install argostranslate` pour le moteur hors ligne (le modèle de langue se télécharge une fois) ;
   - [ffmpeg](https://ffmpeg.org/) (`winget install ffmpeg`) pour lire les sous-titres d'une vidéo
     (1re piste texte ; les sous-titres en image ne sont pas lisibles) ;
   - `pip install -r requirements.txt` pour les tests.

**Sans Python** : télécharger `TraducteurSousTitres-Setup.exe` (ou l'exe seul) dans les
[Releases](https://github.com/poiscail/TraducteurSousTitres/releases). L'installateur crée les raccourcis
Bureau et menu Démarrer, et peut ajouter le clic droit.

Pour les fabriquer soi-même (sur un PC qui a Python) : `Creer_exe.bat` crée `dist\TraducteurSousTitres.exe`,
puis `Creer_installateur.bat` crée `dist\TraducteurSousTitres-Setup.exe`
(demande [Inno Setup 6](https://jrsoftware.org/isinfo.php) : `winget install JRSoftware.InnoSetup`).

## Utilisation

**Interface** : double-cliquer sur `Traduire.bat` (ou l'exe), ou glisser des fichiers dessus.
Choisir des fichiers ou un dossier, une ou plusieurs langues (clic pour cocher), puis « Traduire ».
Sans langue cochée, « Format » et « Décalage (s) » s'appliquent seuls (`film.vtt`, `film.modifie.srt`).
« Intégrer à la vidéo » ajoute la traduction en piste dans une copie de la vidéo d'origine.
Les réglages sont retenus. « Ajouter au clic droit » ajoute « Traduire les sous-titres » au menu
du clic droit des fichiers de sous-titres et des vidéos.

**Glossaire** : bouton « Glossaire… ». Un terme par ligne :

```
Winterfell
Hand of the King = Main du Roi
```

**Ligne de commande** :

```bash
python traducteur.py film.srt -l fr
python traducteur.py episode1.srt episode2.mkv -l fr,es,de
python traducteur.py "Saison 1" -l de -s en --reparer
python traducteur.py film.srt -l fr -m deepl --cle VOTRE_CLE
python traducteur.py film.srt --decaler -1.5 --format vtt
python traducteur.py film.mkv -l fr --integrer
python traducteur.py --installer-menu
```

`-l` : langue(s) cible (`fr`, `en`, `es`, `de`, `it`, `pt`, `ja`, `zh-CN`…), séparées par des virgules.
`-s` : langue d'origine (détection automatique par défaut ; obligatoire avec Argos).
`-m` : moteur `google` (défaut), `deepl` ou `argos`. `--cle` : clé DeepL (ou variable `DEEPL_API_KEY`).
`--reparer` : répare le fichier avant de traduire.
`--decaler SECONDES` : décale tous les sous-titres (négatif : plus tôt). `--format srt|vtt|ass` : convertit.
`--integrer` : ajoute la traduction en piste dans la vidéo (sans réencoder). `--desinstaller-menu` retire l'entrée du clic droit.
Un dossier traduit tous ses sous-titres, sauf ceux déjà traduits (`*.fr.srt`…).

**Tests** :

```bash
python -m pytest
```
