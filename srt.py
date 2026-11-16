"""Lecture / écriture de fichiers SRT sans toucher aux numéros ni aux timings."""
import re
from dataclasses import dataclass

TIMING = re.compile(r"^\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}.*$")


@dataclass
class Bloc:
    numero: str
    timing: str
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
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    blocs = []
    for morceau in re.split(r"\n\s*\n", texte.strip("\n")):
        lignes = morceau.split("\n")
        if len(lignes) < 2 or not TIMING.match(lignes[1].strip()):
            raise ValueError(f"Bloc SRT invalide : {morceau[:60]!r}")
        blocs.append(Bloc(lignes[0].strip(), lignes[1].strip(), lignes[2:]))
    return blocs


def ecrire(blocs: list[Bloc]) -> str:
    return "\n\n".join("\n".join([b.numero, b.timing, *b.lignes]) for b in blocs) + "\n"
