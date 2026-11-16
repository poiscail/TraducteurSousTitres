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


def test_glossaire_protege_les_termes():
    g = traduction.lire_glossaire("# commentaire\nWinterfell\nHand of the King = Main du Roi\n")
    blocs = [srt.Bloc("1", "00:00:01,000 --> 00:00:02,000", ["The Hand of the King is in Winterfell"])]
    sortie = traduction.traduire_blocs(blocs, str.upper, glossaire=g)[0].lignes
    assert sortie == ["THE Main du Roi IS IN Winterfell"]


def test_deepl(monkeypatch):
    import io
    vu = {}

    def faux_urlopen(req, timeout):
        vu["url"], vu["auth"] = req.full_url, req.get_header("Authorization")
        return io.BytesIO(b'{"translations":[{"text":"Bonjour"}]}')

    monkeypatch.setattr("urllib.request.urlopen", faux_urlopen)
    assert traduction.moteur("deepl", "fr", cle="abc:fx")("Hello") == "Bonjour"
    assert vu["url"] == "https://api-free.deepl.com/v2/translate" and vu["auth"] == "DeepL-Auth-Key abc:fx"


def test_nom_unique_sans_ecraser(tmp_path):
    entree = tmp_path / "film.srt"
    assert traducteur.chemin_sortie(entree, "fr").name == "film.fr.srt"
    (tmp_path / "film.fr.srt").write_text("", encoding="utf-8")
    assert traducteur.chemin_sortie(entree, "fr").name == "film.fr (2).srt"
    assert traducteur.deja_traduit(tmp_path / "film.fr (2).srt")


def test_reparer():
    blocs = srt.parser("5\n00:00:01,000 --> 00:00:03,000\nA\n\n9\n00:00:02,000 --> 00:00:04,000\nB\n\n"
                       "10\n00:00:04,000 --> 00:00:05,000\nB\n\n11\n00:00:06,000 --> 00:00:07,000\n \n")
    assert [(b.numero, b.timing, b.lignes) for b in srt.reparer(blocs)] == [
        ("1", "00:00:01,000 --> 00:00:01,999", ["A"]),
        ("2", "00:00:02,000 --> 00:00:05,000", ["B"])]


def test_plusieurs_langues_en_ligne_de_commande(tmp_path, monkeypatch):
    f = tmp_path / "a.srt"
    f.write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n", encoding="utf-8")
    monkeypatch.setattr(traduction, "moteur", lambda *a, **k: str.upper)
    monkeypatch.setattr(sys, "argv", ["traducteur.py", str(f), "-l", "fr,es"])
    traducteur.main()
    assert (tmp_path / "a.fr.srt").exists() and (tmp_path / "a.es.srt").exists()


def test_video_avec_ffmpeg(tmp_path, monkeypatch):
    import shutil
    import subprocess
    video = tmp_path / "film.mkv"
    video.write_bytes(b"")

    def faux_run(cmd, **k):
        Path(cmd[-1]).write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(shutil, "which", lambda n: "ffmpeg")
    monkeypatch.setattr(subprocess, "run", faux_run)
    assert traducteur.traduire_fichier(video, "fr", traduire=str.upper).name == "film.fr.srt"


def test_arret_pendant_la_traduction():
    import pytest

    def progres(fait, total):
        raise traducteur.Annule

    with pytest.raises(traducteur.Annule):
        traduction.traduire_textes(["a"], str.upper, progres)


def test_menu_contextuel(monkeypatch):
    import types
    ecrit = {}
    faux = types.SimpleNamespace(HKEY_CURRENT_USER=0, REG_SZ=1,
                                 SetValue=lambda racine, cle, t, v: ecrit.__setitem__(cle, v))
    monkeypatch.setitem(sys.modules, "winreg", faux)
    traducteur.menu_contextuel(True)
    cle = r"Software\Classes\SystemFileAssociations\.srt\shell\TraduireSousTitres"
    assert ecrit[cle] == "Traduire les sous-titres" and ecrit[cle + r"\command"].endswith('"%1"')


def test_decaler_srt_et_ass():
    blocs = srt.parser("1\n00:00:01,000 --> 00:00:02,500\nA\n")
    assert srt.decaler(blocs, 1500)[0].timing == "00:00:02,500 --> 00:00:04,000"
    assert srt.decaler(blocs, -5000)[0].timing == "00:00:00,000 --> 00:00:00,000"
    _, ass = srt.parser_ass("Dialogue: 0,0:00:01.00,0:00:02.50,Default,,0,0,0,,Salut")
    assert srt.decaler(ass, 1000, ass=True)[0].timing == "Dialogue: 0,0:00:02.00,0:00:03.50,Default,,0,0,0,,"


def test_conversion_de_format():
    cues = srt.vers_cues(srt.parser("1\n00:00:01,000 --> 00:00:02,000\n<i>Salut</i>\ntoi\n"))
    assert srt.ecrire_format(cues, "vtt") == "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<i>Salut</i>\ntoi\n"
    ass = srt.ecrire_format(cues, "ass")
    assert ass.endswith("Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,," r"{\i1}Salut{\i0}\Ntoi" "\n")
    _, blocs = srt.parser_ass(ass)
    assert srt.ecrire_format(srt.vers_cues(blocs, ass=True), "srt") == \
        "1\n00:00:01,000 --> 00:00:02,000\n<i>Salut</i>\ntoi\n"


def test_decaler_et_convertir_sans_traduire(tmp_path, monkeypatch):
    f = tmp_path / "a.srt"
    f.write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["traducteur.py", str(f), "--decaler", "2", "--format", "vtt"])
    traducteur.main()
    assert (tmp_path / "a.vtt").read_text(encoding="utf-8") == "WEBVTT\n\n00:00:03.000 --> 00:00:04.000\nHi\n"
    assert traducteur.traduire_fichier(f, decalage=-0.5).name == "a.modifie.srt"


def test_integrer_dans_la_video(tmp_path, monkeypatch):
    import shutil
    import subprocess
    video = tmp_path / "film.mp4"
    video.write_bytes(b"")
    commandes = []

    def faux_run(cmd, **k):
        commandes.append(cmd)
        Path(cmd[-1]).write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(shutil, "which", lambda n: "ffmpeg")
    monkeypatch.setattr(subprocess, "run", faux_run)
    sortie = traducteur.traduire_fichier(video, "fr", traduire=str.upper, integrer=True)
    assert sortie.name == "film.fr.mp4"
    assert "mov_text" in commandes[-1] and "language=fre" in commandes[-1]


def test_plus_recente():
    assert traducteur.plus_recente("1.10.0", "1.9.2") and not traducteur.plus_recente("1.1.0", "1.1.0")
