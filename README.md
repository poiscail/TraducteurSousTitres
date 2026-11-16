# Traducteur de sous-titres

Traduit des sous-titres `.srt`, `.vtt` ou `.ass` vers une autre langue en gardant exactement les numéros et les timings.
Le résultat est un nouveau fichier : `film.srt` devient `film.fr.srt`.

- Moteur gratuit, sans clé : Google Translate (connexion internet requise). Réessaie seul si le service limite.
- Langue d'origine détectée automatiquement, ou choisie.
- Lit l'UTF-8 et le Windows-1252, écrit en UTF-8.
- Garde les balises `<i>`, `<b>`, `{\an8}`…, même au milieu d'une ligne.
- Coupe en deux les lignes traduites trop longues (plus de 42 caractères).

## Installation

1. Installer [Python 3.10+](https://www.python.org/downloads/) (cocher « Add to PATH »).
2. Aucune autre dépendance. En option :
   - `pip install tkinterdnd2` pour glisser des fichiers dans la fenêtre ;
   - `pip install -r requirements.txt` pour les tests.

**Sans Python** : double-cliquer sur `Creer_exe.bat` (sur un PC qui a Python) crée
`dist\TraducteurSousTitres.exe`, à copier où l'on veut.

## Utilisation

**Interface** : double-cliquer sur `Traduire.bat`, ou glisser des fichiers dessus.
Choisir des fichiers ou un dossier entier, la langue, puis cliquer sur « Traduire ».
La dernière langue choisie est retenue.

**Ligne de commande** :

```bash
python traducteur.py film.srt -l fr
python traducteur.py episode1.srt episode2.vtt -l es
python traducteur.py "Saison 1" -l de -s en
```

`-l` : langue cible (`fr`, `en`, `es`, `de`, `it`, `pt`, `ja`, `zh-CN`…).
`-s` : langue d'origine (détection automatique par défaut).
Un dossier traduit tous ses sous-titres, sauf ceux déjà traduits (`*.fr.srt`…).

**Tests** :

```bash
python -m pytest
```
