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


def test_balises_au_milieu_gardees_ou_retirees():
    blocs = [srt.Bloc("1", "00:00:01,000 --> 00:00:02,000", ["Il est <i>très</i> tard"])]
    assert traduction.traduire_blocs(blocs, lambda t: t.replace("tard", "late"))[0].lignes == \
        ["Il est <i>très</i> late"]
    # balise abîmée par le moteur : retirée plutôt que laissée cassée
    abime = traduction.traduire_blocs(blocs, lambda t: t.replace("</i>", "< / i>"))
    assert abime[0].lignes == ["Il est très tard"]


def test_ligne_trop_longue_coupee_en_deux():
    blocs = [srt.Bloc("1", "00:00:01,000 --> 00:00:02,000", ["<i>court</i>"])]
    long = "un deux trois quatre cinq six sept huit neuf dix onze douze"
    lignes = traduction.traduire_blocs(blocs, lambda t: long)[0].lignes
    assert lignes[0].startswith("<i>un") and lignes[0].endswith("</i>") and lignes[0].count("\n") == 1
    assert all(len(l) <= 42 for l in lignes[0].split("\n"))


def test_progression():
    vu = []
    traduction.traduire_textes(["a", "b"], str.upper, lambda fait, total: vu.append((fait, total)))
    assert vu[-1] == (2, 2)


def test_vtt(tmp_path):
    f = tmp_path / "a.vtt"
    f.write_text("WEBVTT\n\nNOTE commentaire\n\n00:01.000 --> 00:02.000 align:start\nHello\n\n"
                 "2\n00:00:03.000 --> 00:00:04.000\nBye\n", encoding="utf-8")
    sortie = traducteur.traduire_fichier(f, "fr", traduire=str.upper)
    assert sortie.name == "a.fr.vtt"
    assert sortie.read_text(encoding="utf-8") == ("WEBVTT\n\nNOTE commentaire\n\n00:01.000 --> 00:02.000 align:start\n"
                                                  "HELLO\n\n2\n00:00:03.000 --> 00:00:04.000\nBYE\n")


def test_ass(tmp_path):
    f = tmp_path / "a.ass"
    f.write_text("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                 r"Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\i1}Hello, you\Nthere{\i0}" "\n",
                 encoding="utf-8")
    sortie = traducteur.traduire_fichier(f, "fr", traduire=str.upper)
    assert sortie.read_text(encoding="utf-8").splitlines()[2] == \
        r"Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\i1}HELLO,\NYOU THERE{\i0}"


def test_dossier_ignore_les_traductions(tmp_path):
    for nom in ("a.srt", "a.fr.srt", "b.vtt", "notes.txt"):
        (tmp_path / nom).write_text("", encoding="utf-8")
    assert [f.name for f in traducteur.lister([tmp_path])] == ["a.srt", "b.vtt"]


def test_reessaie_si_429(monkeypatch):
    import io
    import urllib.error
    appels = []

    def faux_urlopen(req, timeout):
        appels.append(1)
        if len(appels) < 3:
            raise urllib.error.HTTPError("u", 429, "Too Many Requests", {}, None)
        return io.BytesIO(b'[[["Bonjour",null]]]')

    monkeypatch.setattr("urllib.request.urlopen", faux_urlopen)
    monkeypatch.setattr("time.sleep", lambda s: None)
    assert traduction.google("fr")("Hello") == "Bonjour" and len(appels) == 3
