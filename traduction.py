"""Traduction des blocs SRT en gardant les balises de début/fin de ligne (<i>, {\\an8}...)."""
import re

from srt import Bloc

# balises en début de ligne / en fin de ligne
BALISE = r"(?:<[^>]+>|\{[^}]*\})"
LIGNE = re.compile(rf"^((?:{BALISE}|\s)*)(.*?)((?:{BALISE}|\s)*)$", re.S)
TAILLE_LOT = 4500  # limite ~5000 caractères du service gratuit


def decouper(ligne: str) -> tuple[str, str, str]:
    debut, coeur, fin = LIGNE.match(ligne).groups()
    # shortcut: balises au milieu d'une ligne supprimées, à gérer si besoin réel
    return debut, re.sub(BALISE, "", coeur), fin


def repartir(texte: str, n: int) -> list[str]:
    """Coupe le texte traduit en n lignes de longueur proche."""
    mots, lignes = texte.split(), []
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


def traduire_textes(textes: list[str], traduire) -> list[str]:
    """Envoie les textes par lots (un par ligne) ; repasse un par un si le lot revient mal découpé."""
    resultats, lot = [], []

    def vider():
        if not lot:
            return
        sortie = (traduire("\n".join(lot)) or "").split("\n")
        resultats.extend(sortie if len(sortie) == len(lot) else [traduire(t) or t for t in lot])
        lot.clear()

    for t in textes:
        if lot and len("\n".join(lot + [t])) > TAILLE_LOT:
            vider()
        lot.append(t)
    vider()
    return resultats


def traduire_blocs(blocs: list[Bloc], traduire) -> list[Bloc]:
    """`traduire(texte) -> texte` ; numéros et timings recopiés tels quels."""
    morceaux = [[decouper(l) for l in b.lignes] for b in blocs]
    # segment = (bloc, lignes concernées, texte) ; une phrase sur 2 lignes est traduite d'un coup,
    # mais les dialogues ("- ...") ligne par ligne
    segments = []
    for i, m in enumerate(morceaux):
        pleines = [k for k, (_, c, _) in enumerate(m) if c.strip()]
        if any(m[k][1].lstrip().startswith("-") for k in pleines):
            segments += [(i, [k], m[k][1].strip()) for k in pleines]
        elif pleines:
            segments.append((i, pleines, " ".join(m[k][1].strip() for k in pleines)))
    traduits = traduire_textes([t for _, _, t in segments], traduire)

    nouvelles = [dict() for _ in blocs]
    for (i, ks, _), t in zip(segments, traduits):
        nouvelles[i].update(zip(ks, repartir(t.strip(), len(ks))))
    return [Bloc(b.numero, b.timing, [d + n.get(k, c) + f for k, (d, c, f) in enumerate(m)])
            for b, m, n in zip(blocs, morceaux, nouvelles)]


def google(langue: str):
    """Moteur gratuit sans clé : point d'accès public de Google Translate (internet requis)."""
    import json
    import urllib.parse
    import urllib.request

    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "auto", "tl": langue, "dt": "t"})

    def traduire(texte: str) -> str:
        donnees = urllib.parse.urlencode({"q": texte}).encode()
        with urllib.request.urlopen(urllib.request.Request(url, donnees), timeout=30) as r:
            return "".join(morceau[0] for morceau in json.load(r)[0] if morceau[0])

    return traduire
