"""Traduction des blocs de sous-titres en gardant les balises (<i>, {\\an8}...)."""
import re
from collections import Counter

from srt import Bloc

# balises en début de ligne / en fin de ligne
BALISE = r"(?:<[^>]+>|\{[^}]*\})"
LIGNE = re.compile(rf"^((?:{BALISE}|\s)*)(.*?)((?:{BALISE}|\s)*)$", re.S)
MOT = re.compile(rf"(?:{BALISE}|\S)+")  # un mot, balises collées comprises (<font color="x"> reste entier)
TAILLE_LOT = 4500  # limite ~5000 caractères du service gratuit
LONGUEUR_MAX = 42  # norme courante : 42 caractères par ligne, 2 lignes max


def decouper(ligne: str) -> tuple[str, str, str]:
    debut, coeur, fin = LIGNE.match(ligne).groups()
    return debut, coeur, fin


def balises_intactes(avant: str, apres: str) -> str:
    """Garde les balises du milieu si la traduction les a rendues telles quelles, sinon les retire."""
    if Counter(re.findall(BALISE, avant)) == Counter(re.findall(BALISE, apres)):
        return apres
    return re.sub(r"\s{2,}", " ", re.sub(BALISE, "", apres))


def repartir(texte: str, n: int) -> list[str]:
    """Coupe le texte traduit en n lignes de longueur proche."""
    mots, lignes = MOT.findall(texte), []
    for reste in range(n, 0, -1):
        if reste == 1:
            lignes.append(" ".join(mots))
            break
        cible = len(" ".join(mots)) / reste
        ligne = mots[:1]
        del mots[:1]
        # ajoute un mot tant que ça rapproche de la longueur visée
        while len(mots) > reste - 1:
            avec = len(" ".join(ligne + mots[:1]))
            if abs(avec - cible) >= abs(len(" ".join(ligne)) - cible):
                break
            ligne.append(mots.pop(0))
        lignes.append(" ".join(ligne))
    return lignes


def nb_lignes(texte: str, n: int) -> int:
    """Au moins n lignes ; passe à 2 si une ligne dépasserait LONGUEUR_MAX."""
    return max(n, 2) if len(texte) > LONGUEUR_MAX * n and len(MOT.findall(texte)) > 1 else n


def traduire_textes(textes: list[str], traduire, progres=None) -> list[str]:
    """Envoie les textes par lots (un par ligne) ; repasse un par un si le lot revient mal découpé."""
    resultats, lot = [], []

    def vider():
        if not lot:
            return
        sortie = (traduire("\n".join(lot)) or "").split("\n")
        resultats.extend(sortie if len(sortie) == len(lot) else [traduire(t) or t for t in lot])
        lot.clear()
        if progres:
            progres(len(resultats), len(textes))

    for t in textes:
        if lot and len("\n".join(lot + [t])) > TAILLE_LOT:
            vider()
        lot.append(t)
    vider()
    return resultats


def traduire_blocs(blocs: list[Bloc], traduire, progres=None) -> list[Bloc]:
    """`traduire(texte) -> texte` ; numéros et timings recopiés tels quels.
    Les blocs sans timing (en-tête WEBVTT, NOTE, STYLE) sont recopiés sans traduction."""
    morceaux = [[decouper(l) for l in b.lignes] if b.timing else [] for b in blocs]
    # segment = (bloc, lignes concernées, texte) ; une phrase sur 2 lignes est traduite d'un coup,
    # mais les dialogues ("- ...") ligne par ligne
    segments = []
    for i, m in enumerate(morceaux):
        pleines = [k for k, (_, c, _) in enumerate(m) if re.sub(BALISE, "", c).strip()]
        if any(m[k][1].lstrip().startswith("-") for k in pleines):
            segments += [(i, [k], m[k][1].strip(), True) for k in pleines]
        elif pleines:
            segments.append((i, pleines, " ".join(m[k][1].strip() for k in pleines), False))
    traduits = traduire_textes([s[2] for s in segments], traduire, progres)

    nouvelles = [dict() for _ in blocs]
    for (i, ks, original, dialogue), t in zip(segments, traduits):
        t = balises_intactes(original, t.strip())
        lignes = repartir(t, len(ks) if dialogue else nb_lignes(t, len(ks)))
        nouvelles[i].update(zip(ks, lignes))
        if len(lignes) > len(ks):  # ligne trop longue coupée en deux : la suite va avec la dernière
            nouvelles[i][ks[-1]] = "\n".join(lignes[len(ks) - 1:])
    return [b if not b.timing else
            Bloc(b.numero, b.timing, [d + n.get(k, c) + f for k, (d, c, f) in enumerate(m)])
            for b, m, n in zip(blocs, morceaux, nouvelles)]


def google(langue: str, source: str = "auto"):
    """Moteur gratuit sans clé : point d'accès public de Google Translate (internet requis).
    Réessaie avec une attente croissante si le service limite (erreur 429) ou coupe."""
    import json
    import time
    import urllib.error
    import urllib.parse
    import urllib.request

    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": source, "tl": langue, "dt": "t"})

    def traduire(texte: str) -> str:
        donnees = urllib.parse.urlencode({"q": texte}).encode()
        for essai in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, donnees), timeout=30) as r:
                    return "".join(morceau[0] for morceau in json.load(r)[0] if morceau[0])
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503) or essai == 5:
                    raise
            except urllib.error.URLError:
                if essai == 5:
                    raise
            time.sleep(2 ** essai)  # 1, 2, 4, 8, 16 s

    return traduire
