"""Lecture / écriture de sous-titres (.srt, .vtt, .ass) sans toucher aux numéros ni aux timings."""
import re
from dataclasses import dataclass

TIMING = re.compile(r"^(?:\d{1,2}:)?\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*(?:\d{1,2}:)?\d{2}:\d{2}[,.]\d{1,3}.*$")


@dataclass
class Bloc:
    numero: str
    timing: str  # vide : bloc recopié tel quel (en-tête WEBVTT, NOTE, STYLE)
    lignes: list[str]


def lire_fichier(chemin) -> str:
    """Lit en UTF-8 (avec ou sans BOM), sinon en Windows-1252."""
    with open(chemin, "rb") as f:
        brut = f.read()
    try:
        return brut.decode("utf-8-sig")
    except UnicodeDecodeError:
        return brut.decode("cp1252")


def parser(texte: str) -> list[Bloc]:
    """SRT ou WebVTT : le timing est en 1re ligne (VTT sans identifiant) ou en 2e."""
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    blocs = []
    for morceau in re.split(r"\n\s*\n", texte.strip("\n")):
        lignes = morceau.split("\n")
        if TIMING.match(lignes[0].strip()):
            blocs.append(Bloc("", lignes[0].strip(), lignes[1:]))
        elif len(lignes) > 1 and TIMING.match(lignes[1].strip()):
            blocs.append(Bloc(lignes[0].strip(), lignes[1].strip(), lignes[2:]))
        elif blocs or texte.startswith("WEBVTT"):
            blocs.append(Bloc("", "", lignes))
        else:
            raise ValueError(f"Bloc de sous-titre invalide : {morceau[:60]!r}")
    if not any(b.timing for b in blocs):
        raise ValueError("Aucun sous-titre trouvé dans le fichier.")
    return blocs


def ecrire(blocs: list[Bloc]) -> str:
    return "\n\n".join("\n".join([x for x in (b.numero, b.timing) if x] + b.lignes) for b in blocs) + "\n"


def parser_ass(texte: str) -> tuple[list[str], list[Bloc]]:
    """ASS/SSA : chaque « Dialogue: » devient un bloc ; numero = n° de ligne, timing = début jusqu'au texte."""
    lignes = texte.replace("\r\n", "\n").split("\n")
    blocs = []
    for i, ligne in enumerate(lignes):
        parties = ligne.split(",", 9)
        if ligne.startswith("Dialogue:") and len(parties) == 10:
            blocs.append(Bloc(str(i), ",".join(parties[:9]) + ",", parties[9].split("\\N")))
    if not blocs:
        raise ValueError("Aucune ligne « Dialogue: » trouvée dans le fichier.")
    return lignes, blocs


def ecrire_ass(lignes: list[str], blocs: list[Bloc]) -> str:
    lignes = list(lignes)
    for b in blocs:
        lignes[int(b.numero)] = b.timing + "\\N".join(b.lignes).replace("\n", "\\N")
    return "\n".join(lignes)
