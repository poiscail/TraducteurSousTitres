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


def _ms(temps: str) -> int:
    hms, ms = re.match(r"([\d:]+)[,.](\d+)", temps).groups()
    h, m, s = ([0, 0] + [int(x) for x in hms.split(":")])[-3:]
    return ((h * 60 + m) * 60 + s) * 1000 + int(ms.ljust(3, "0")[:3])


def _hms(ms: int, sep: str) -> str:
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}{sep}{ms % 1000:03}"


def _temps(timing: str) -> tuple[int, int, str, str]:
    debut, fin, reste = re.match(r"^(\S+)\s*-->\s*(\S+)(.*)$", timing).groups()
    return _ms(debut), _ms(fin), reste, "," if "," in debut else "."


def reparer(blocs: list[Bloc], numeroter: bool = True) -> list[Bloc]:
    """Retire les sous-titres vides et les doublons qui se suivent, corrige les chevauchements
    (fin après le début du suivant) et renumérote à partir de 1."""
    sortie, n = [], 0
    for b in blocs:
        if not b.timing:
            sortie.append(b)
            continue
        if not any(l.strip() for l in b.lignes):
            continue
        debut, fin, _, _ = _temps(b.timing)
        prec = sortie[-1] if sortie and sortie[-1].timing else None
        if prec:
            d, f, reste, sep = _temps(prec.timing)
            if prec.lignes == b.lignes:  # doublon : on prolonge le précédent
                prec.timing = f"{_hms(d, sep)} --> {_hms(max(f, fin), sep)}{reste}"
                continue
            if f > debut:
                prec.timing = f"{_hms(d, sep)} --> {_hms(max(d, debut - 1), sep)}{reste}"
        n += 1
        sortie.append(Bloc(str(n) if numeroter else b.numero, b.timing, list(b.lignes)))
    return sortie


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
