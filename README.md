# Traducteur de sous-titres

Traduit un fichier `.srt` vers une autre langue en gardant exactement les numéros et les timings.
Le résultat est un nouveau fichier : `film.srt` devient `film.fr.srt`.

- Moteur gratuit, sans clé : Google Translate (connexion internet requise).
- Lit l'UTF-8 et le Windows-1252, écrit en UTF-8.
- Garde les balises `<i>`, `<b>`, `{\an8}`… en début et fin de ligne.

## Installation

1. Installer [Python 3.10+](https://www.python.org/downloads/) (cocher « Add to PATH »).
2. Aucune autre dépendance. Pour les tests seulement : `pip install -r requirements.txt`.

## Utilisation

**Interface** : double-cliquer sur `Traduire.bat`, ou glisser un `.srt` dessus.
Choisir la langue, puis cliquer sur « Traduire ».

**Ligne de commande** :

```bash
python traducteur.py film.srt -l fr
python traducteur.py episode1.srt episode2.srt -l es
```

`-l` prend un code de langue : `fr`, `en`, `es`, `de`, `it`, `pt`, `ja`, `zh-CN`…

**Tests** :

```bash
python -m pytest
```
