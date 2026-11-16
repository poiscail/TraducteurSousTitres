import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import srt
import traducteur
import traduction

EXEMPLE = Path(__file__).resolve().parent.parent / "exemple" / "film.srt"


def test_aller_retour_identique():
    texte = EXEMPLE.read_text(encoding="utf-8")
    assert srt.ecrire(srt.parser(texte)) == texte


def test_crlf_et_bom(tmp_path):
    f = tmp_path / "a.srt"
    f.write_bytes("﻿1\r\n00:00:01,000 --> 00:00:02,000\r\nSalut\r\n".encode("utf-8"))
    blocs = srt.parser(srt.lire_fichier(f))
    assert blocs[0].numero == "1" and blocs[0].lignes == ["Salut"]


def test_windows_1252(tmp_path):
    f = tmp_path / "a.srt"
    f.write_bytes("1\n00:00:01,000 --> 00:00:02,000\nCafé à côté\n".encode("cp1252"))
    assert srt.parser(srt.lire_fichier(f))[0].lignes == ["Café à côté"]


def test_traduction_garde_numeros_timings_et_balises(tmp_path):
    entree = tmp_path / "film.srt"
    entree.write_text(EXEMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    sortie = traducteur.traduire_fichier(entree, "fr", traduire=str.upper)

    avant, apres = srt.parser(EXEMPLE.read_text(encoding="utf-8")), srt.parser(sortie.read_text(encoding="utf-8"))
    assert sortie.name == "film.fr.srt"
    assert [(b.numero, b.timing, len(b.lignes)) for b in avant] == [(b.numero, b.timing, len(b.lignes)) for b in apres]
    assert apres[1].lignes[0].startswith("<i>") and apres[1].lignes[-1].endswith("</i>")
    assert apres[3].lignes[0] == "{\\an8}THANK YOU VERY MUCH, MY FRIEND."


def test_lot_mal_decoupe_repasse_un_par_un():
    def faux(t):
        return t.replace("\n", " ") if "\n" in t else t + "!"

    assert traduction.traduire_textes(["a", "b"], faux) == ["a!", "b!"]


def test_repartir():
    assert traduction.repartir("un deux trois quatre", 2) == ["un deux", "trois quatre"]
    assert traduction.repartir("seul", 1) == ["seul"]
