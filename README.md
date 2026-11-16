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

**Sans Python** : double-cliquer sur `Creer_exe.bat` (sur un PC qui a Python) crée
`dist\TraducteurSousTitres.exe`, à copier où l'on veut.

## Utilisation

**Interface** : double-cliquer sur `Traduire.bat` (ou l'exe), ou glisser des fichiers dessus.
Choisir des fichiers ou un dossier, une ou plusieurs langues (clic pour cocher), puis « Traduire ».
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
python traducteur.py --installer-menu
```

`-l` : langue(s) cible (`fr`, `en`, `es`, `de`, `it`, `pt`, `ja`, `zh-CN`…), séparées par des virgules.
`-s` : langue d'origine (détection automatique par défaut ; obligatoire avec Argos).
`-m` : moteur `google` (défaut), `deepl` ou `argos`. `--cle` : clé DeepL (ou variable `DEEPL_API_KEY`).
`--reparer` : répare le fichier avant de traduire. `--desinstaller-menu` retire l'entrée du clic droit.
Un dossier traduit tous ses sous-titres, sauf ceux déjà traduits (`*.fr.srt`…).

**Tests** :

```bash
python -m pytest
```
