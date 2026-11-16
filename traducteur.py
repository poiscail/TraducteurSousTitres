"""Traducteur de sous-titres (.srt, .vtt, .ass, vidéos .mkv/.mp4).

Ligne de commande : python traducteur.py film.srt -l fr,es
Interface : python traducteur.py   (ou glisser des fichiers sur Traduire.bat)
"""
import argparse
import json
import os
import re
import sys
import threading
from pathlib import Path

import srt
import traduction

VERSION = "1.1.0"
DEPOT = "poiscail/TraducteurSousTitres"
LANGUES = {"Français": "fr", "Anglais": "en", "Espagnol": "es", "Allemand": "de", "Italien": "it",
           "Portugais": "pt", "Néerlandais": "nl", "Russe": "ru", "Arabe": "ar", "Japonais": "ja",
           "Chinois": "zh-CN", "Coréen": "ko", "Turc": "tr", "Polonais": "pl"}
AUTO = "Détection auto"
EXTENSIONS = {".srt", ".vtt", ".ass", ".ssa"}
VIDEOS = {".mkv", ".mp4"}
FORMATS = {"Identique": None, "SRT": "srt", "VTT": "vtt", "ASS": "ass"}
# codes ISO 639-2 attendus par les pistes de sous-titres des vidéos
ISO3 = {"fr": "fre", "en": "eng", "es": "spa", "de": "ger", "it": "ita", "pt": "por", "nl": "dut", "ru": "rus",
        "ar": "ara", "ja": "jpn", "zh-CN": "chi", "ko": "kor", "tr": "tur", "pl": "pol"}
CONFIG = Path(os.environ.get("APPDATA", Path.home())) / "TraducteurSousTitres.json"
GLOSSAIRE = CONFIG.with_name("TraducteurSousTitres_glossaire.txt")
MODELE_GLOSSAIRE = """# Glossaire du traducteur de sous-titres
# Un terme par ligne :
#   Winterfell              -> jamais traduit
#   Hand of the King = Main du Roi   -> toujours traduit pareil
"""


class Annule(Exception):
    """Traduction arrêtée par l'utilisateur."""


def chemin_sortie(entree: Path, langue: str, suffixe: str = "") -> Path:
    """film.fr.srt, ou film.fr (2).srt s'il existe déjà : on n'écrase jamais une traduction."""
    suffixe, base = suffixe or entree.suffix, f"{entree.stem}.{langue}" if langue else entree.stem
    sortie, n = entree.with_name(base + suffixe), 2
    while sortie.exists():
        sortie, n = entree.with_name(f"{base} ({n}){suffixe}"), n + 1
    return sortie


def deja_traduit(f: Path) -> bool:
    """film.fr.srt ou film.fr (2).srt : sortie d'une traduction précédente, à ne pas retraduire."""
    m = re.search(r"\.([\w-]+)(?: \(\d+\))?$", f.stem)
    return bool(m) and m[1] in LANGUES.values()


def lister(chemins) -> list[Path]:
    """Fichiers de sous-titres (ou vidéos) donnés directement ou contenus dans les dossiers donnés."""
    fichiers = []
    for c in map(Path, chemins):
        if c.is_dir():
            fichiers += sorted(f for f in c.iterdir()
                               if f.suffix.lower() in EXTENSIONS and not deja_traduit(f)
                               or f.suffix.lower() in VIDEOS and not f.with_suffix(".srt").exists())
        elif c.suffix.lower() in EXTENSIONS | VIDEOS:
            fichiers.append(c)
    return fichiers


def ffmpeg(*arguments):
    """Lance ffmpeg (à installer à part) sans ouvrir de console."""
    import shutil
    import subprocess

    exe = shutil.which("ffmpeg")
    if not exe:
        raise ValueError("ffmpeg introuvable : installe-le (winget install ffmpeg) pour les vidéos.")
    return subprocess.run([exe, "-y", "-v", "error", *map(str, arguments)], capture_output=True, text=True,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def extraire_sous_titres(video: Path) -> Path:
    """Sort la piste de sous-titres d'une vidéo en film.srt."""
    sortie = video.with_suffix(".srt")
    if sortie.exists():
        return sortie
    # shortcut: 1re piste de sous-titres seulement ; ajouter un choix de piste si on en a besoin
    r = ffmpeg("-i", video, "-map", "0:s:0", sortie)
    if r.returncode or not sortie.exists():
        sortie.unlink(missing_ok=True)
        raise ValueError("Pas de piste de sous-titres texte dans la vidéo (les sous-titres en image ne sont pas lisibles).")
    return sortie


def integrer_video(video: Path, sous_titres: Path, langue: str | None = None) -> Path:
    """Copie la vidéo avec les sous-titres en 1re piste (film.fr.mkv), sans réencoder image ni son."""
    sortie = chemin_sortie(video, langue or "sous-titres")
    mp4 = video.suffix.lower() == ".mp4"
    r = ffmpeg("-i", video, "-i", sous_titres, "-map", "0:v?", "-map", "0:a?", "-map", "1", "-map", "0:s?",
               *([] if mp4 else ["-map", "0:t?"]), "-c", "copy", *(["-c:s", "mov_text"] if mp4 else []),
               "-metadata:s:s:0", f"language={ISO3.get(langue, 'und')}", "-disposition:s:0", "default", sortie)
    if r.returncode or not sortie.exists():
        sortie.unlink(missing_ok=True)
        raise ValueError(f"Intégration dans la vidéo impossible : {(r.stderr or '').strip()[-200:]}")
    return sortie


def glossaire() -> list[tuple[str, str]]:
    try:
        return traduction.lire_glossaire(GLOSSAIRE.read_text(encoding="utf-8"))
    except OSError:
        return []


def traduire_contenu(entree, langue: str | None, traduire=None, source="auto", progres=None, moteur="google",
                     cle="", glossaire=(), reparer=False, decalage=0.0, fmt=None):
    """Renvoie (fichier lu, blocs d'origine, blocs finaux, fonction qui produit le texte, extension de sortie).
    Sans langue : seulement réparation, décalage (en secondes) et conversion de format (srt, vtt, ass)."""
    entree = Path(entree)
    if entree.suffix.lower() in VIDEOS:
        entree = extraire_sous_titres(entree)
    texte = srt.lire_fichier(entree)
    ass = entree.suffix.lower() in (".ass", ".ssa")
    if ass:
        lignes, blocs = srt.parser_ass(texte)
        rendre = lambda b: srt.ecrire_ass(lignes, b)  # noqa: E731
    else:
        blocs, rendre = srt.parser(texte), srt.ecrire
        if reparer:
            blocs = srt.reparer(blocs, numeroter=entree.suffix.lower() == ".srt")
    if decalage:
        blocs = srt.decaler(blocs, round(decalage * 1000), ass)
    suffixe = entree.suffix
    if fmt and fmt != ("ass" if ass else suffixe.lower()[1:]):
        rendre, suffixe = (lambda b: srt.ecrire_format(srt.vers_cues(b, ass), fmt)), f".{fmt}"
    if langue:
        finaux = traduction.traduire_blocs(blocs, traduire or traduction.moteur(moteur, langue, source, cle),
                                           progres, glossaire)
    else:
        finaux = blocs
    return entree, blocs, finaux, rendre, suffixe


def enregistrer(origine, entree: Path, langue, texte: str, suffixe: str, integrer=False) -> Path:
    """Écrit film.fr.srt (film.vtt si seulement converti, film.modifie.srt si seulement décalé ou réparé),
    puis l'intègre à la vidéo d'origine si demandé."""
    etiquette = langue or ("" if suffixe.lower() != entree.suffix.lower() else "modifie")
    sortie = chemin_sortie(entree, etiquette, suffixe)
    sortie.write_text(texte, encoding="utf-8")
    if integrer and Path(origine).suffix.lower() in VIDEOS:
        return integrer_video(Path(origine), sortie, langue)
    return sortie


def traduire_fichier(entree, langue: str | None = None, integrer=False, **options) -> Path:
    lu, _, finaux, rendre, suffixe = traduire_contenu(entree, langue, **options)
    return enregistrer(entree, lu, langue, rendre(finaux), suffixe, integrer)


def derniere_version() -> tuple[str, str]:
    """(numéro, page) de la dernière version publiée sur GitHub."""
    import urllib.request

    requete = urllib.request.Request(f"https://api.github.com/repos/{DEPOT}/releases/latest",
                                     headers={"User-Agent": "TraducteurSousTitres"})
    with urllib.request.urlopen(requete, timeout=5) as r:
        donnees = json.load(r)
    return donnees["tag_name"].lstrip("v"), donnees["html_url"]


def plus_recente(version: str, actuelle: str = VERSION) -> bool:
    def nombres(v):
        return tuple(int(x) for x in re.findall(r"\d+", v))
    return nombres(version) > nombres(actuelle)


def commande_menu() -> str:
    if getattr(sys, "frozen", False):  # .exe
        return f'"{sys.executable}" "%1"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    return f'"{pythonw if pythonw.exists() else sys.executable}" "{Path(__file__).resolve()}" "%1"'


def menu_contextuel(installer: bool = True):
    """Ajoute (ou retire) « Traduire les sous-titres » au clic droit sur les fichiers, pour l'utilisateur courant."""
    import winreg

    for ext in sorted(EXTENSIONS | VIDEOS):
        cle = rf"Software\Classes\SystemFileAssociations\{ext}\shell\TraduireSousTitres"
        if installer:
            winreg.SetValue(winreg.HKEY_CURRENT_USER, cle, winreg.REG_SZ, "Traduire les sous-titres")
            winreg.SetValue(winreg.HKEY_CURRENT_USER, cle + r"\command", winreg.REG_SZ, commande_menu())
        else:
            for sous in (cle + r"\command", cle):
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sous)
                except FileNotFoundError:
                    pass


def lire_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def ecrire_config(**valeurs):
    try:
        CONFIG.write_text(json.dumps({**lire_config(), **valeurs}, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass  # préférence non retenue : pas grave


def interface(fichiers=()):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    try:  # glisser-déposer dans la fenêtre : optionnel (pip install tkinterdnd2)
        from tkinterdnd2 import DND_FILES, TkinterDnD
        fen = TkinterDnD.Tk()
    except ImportError:
        DND_FILES, fen = None, tk.Tk()

    fen.title(f"Traducteur de sous-titres {VERSION}")
    icone = Path(__file__).with_name("icone.ico")
    if icone.exists():
        fen.iconbitmap(icone)
    fen.minsize(600, 420)
    fen.columnconfigure(0, weight=1)
    fen.rowconfigure(0, weight=1)
    config = lire_config()
    choix = lister(fichiers)
    resume = tk.StringVar()
    source = tk.StringVar(value=config.get("source", AUTO))
    nom_moteur = tk.StringVar(value=config.get("moteur", next(iter(traduction.MOTEURS))))
    cle = tk.StringVar(value=config.get("cle_deepl", os.environ.get("DEEPL_API_KEY", "")))
    reparer = tk.BooleanVar(value=config.get("reparer", False))
    apercu = tk.BooleanVar(value=config.get("apercu", False))
    sombre = tk.BooleanVar(value=config.get("sombre", False))
    integrer = tk.BooleanVar(value=config.get("integrer", False))
    fmt = tk.StringVar(value=config.get("format", "Identique"))
    decalage = tk.StringVar(value="0")
    etat = tk.StringVar(value="Choisis des sous-titres (.srt, .vtt, .ass, .mkv) et une ou plusieurs langues.")
    stop = threading.Event()
    style = ttk.Style(fen)
    style.theme_use("clam")

    def theme():
        fond, texte, champ, bouton_ = (("#1e1e1e", "#e6e6e6", "#2b2b2b", "#3a3a3a") if sombre.get()
                                       else ("#f0f0f0", "#000000", "#ffffff", "#e1e1e1"))
        style.configure(".", background=fond, foreground=texte, fieldbackground=champ, insertcolor=texte)
        style.configure("TButton", background=bouton_)
        style.map("TButton", background=[("active", "#4a6fa5" if sombre.get() else "#cfe0f5")])
        style.map("TCombobox", fieldbackground=[("readonly", champ)], foreground=[("readonly", texte)])
        style.map("TEntry", fieldbackground=[("readonly", champ)])
        style.configure("Treeview", background=champ, fieldbackground=champ, foreground=texte)
        fen.option_add("*TCombobox*Listbox.background", champ)
        fen.option_add("*TCombobox*Listbox.foreground", texte)
        fen.configure(background=fond)
        for w in (liste, *ouvertes):
            w.configure(background=champ, foreground=texte, selectbackground="#4a6fa5")
        for w in ouvertes:
            w.configure(insertbackground=texte)

    ouvertes = []  # zones de texte tk (hors ttk) à recolorer avec le thème

    def montrer():
        resume.set(str(choix[0]) if len(choix) == 1 else f"{len(choix)} fichiers" if choix else "")

    def remplacer(nouveaux):
        choix[:] = lister(nouveaux)
        montrer()

    def choisir_fichiers():
        f = filedialog.askopenfilenames(filetypes=[("Sous-titres ou vidéos", "*.srt *.vtt *.ass *.ssa *.mkv *.mp4")])
        if f:
            remplacer(f)

    def choisir_dossier():
        d = filedialog.askdirectory()
        if d:
            remplacer([d])

    def ouvrir_glossaire():
        if not GLOSSAIRE.exists():
            GLOSSAIRE.write_text(MODELE_GLOSSAIRE, encoding="utf-8")
        os.startfile(GLOSSAIRE)

    def installer_menu():
        try:
            menu_contextuel(True)
            messagebox.showinfo("Clic droit", "« Traduire les sous-titres » est ajouté au clic droit des fichiers.")
        except OSError as e:
            messagebox.showerror("Erreur", str(e))

    def ouvrir_apercu(code, origine, entree, blocs, traduits, rendre, suffixe):
        """Original et traduction côte à côte ; double-clic pour corriger, puis enregistrer."""
        win = tk.Toplevel(fen)
        win.title(f"Aperçu : {entree.name} → {code or suffixe}")
        win.geometry("900x500")
        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)
        arbre = ttk.Treeview(win, columns=("temps", "orig", "trad"), show="headings")
        for col, titre, large in (("temps", "Début", 90), ("orig", "Original", 380), ("trad", "Traduction", 380)):
            arbre.heading(col, text=titre)
            arbre.column(col, width=large, stretch=col != "temps")
        defil = ttk.Scrollbar(win, orient="vertical", command=arbre.yview)
        arbre.configure(yscrollcommand=defil.set)
        arbre.grid(row=0, column=0, sticky="nsew")
        defil.grid(row=0, column=1, sticky="ns")

        def une_ligne(b):
            return " | ".join(b.lignes).replace("\n", " | ")

        for i, (avant, apres) in enumerate(zip(blocs, traduits)):
            if apres.timing:
                arbre.insert("", "end", iid=str(i), values=(apres.timing.split()[0], une_ligne(avant), une_ligne(apres)))

        def modifier(_):
            i = arbre.focus()
            if not i:
                return
            bloc = traduits[int(i)]
            boite = tk.Toplevel(win)
            boite.title("Corriger la traduction")
            zone = tk.Text(boite, width=60, height=4, wrap="word")
            zone.insert("1.0", "\n".join(bloc.lignes))
            zone.grid(padx=8, pady=8)
            ouvertes.append(zone)
            theme()

            def valider():
                bloc.lignes = zone.get("1.0", "end-1c").split("\n")
                arbre.set(i, "trad", une_ligne(bloc))
                ouvertes.remove(zone)
                boite.destroy()

            ttk.Button(boite, text="OK", command=valider).grid(pady=(0, 8))
            zone.focus_set()

        def sauver():
            try:
                sortie = enregistrer(origine, entree, code, rendre(traduits), suffixe, integrer.get())
            except (OSError, ValueError) as e:
                messagebox.showerror("Erreur", str(e))
                return
            etat.set(f"Enregistré : {sortie.name}")
            win.destroy()

        arbre.bind("<Double-1>", modifier)
        bas = ttk.Frame(win, padding=6)
        bas.grid(row=1, column=0, columnspan=2, sticky="e")
        ttk.Label(bas, text="Double-clic sur une ligne pour la corriger.").grid(row=0, column=0, padx=8)
        ttk.Button(bas, text="Enregistrer", command=sauver).grid(row=0, column=1)
        ttk.Button(bas, text="Annuler", command=win.destroy).grid(row=0, column=2, padx=(4, 0))

    def lancer():
        cibles = [liste.get(i) for i in liste.curselection()]
        try:
            secondes = float(decalage.get().replace(",", ".") or 0)
        except ValueError:
            messagebox.showerror("Erreur", "Décalage invalide : un nombre de secondes, par ex. 1.5 ou -2.")
            return
        modifier_seul = secondes or FORMATS[fmt.get()] or reparer.get()
        if not choix or not (cibles or modifier_seul):
            messagebox.showerror("Erreur", "Choisis au moins un fichier et une langue cible "
                                           "(ou un décalage, un format, la réparation).")
            return
        ecrire_config(langues=cibles, source=source.get(), moteur=nom_moteur.get(), cle_deepl=cle.get().strip(),
                      reparer=reparer.get(), apercu=apercu.get(), sombre=sombre.get(), integrer=integrer.get(),
                      format=fmt.get())
        options = dict(source=LANGUES.get(source.get(), "auto"), moteur=traduction.MOTEURS[nom_moteur.get()],
                       cle=cle.get().strip(), glossaire=glossaire(), reparer=reparer.get(), decalage=secondes,
                       fmt=FORMATS[fmt.get()])
        taches = [(f, LANGUES[c]) for f in choix for c in cibles] or [(f, None) for f in choix]
        voir = apercu.get() and len(taches) == 1
        stop.clear()
        bouton.config(state="disabled")
        arreter.config(state="normal")
        barre["value"] = 0

        def travail():
            erreurs, faits = [], 0
            for n, (f, code) in enumerate(taches):
                if stop.is_set():
                    break
                fen.after(0, etat.set, f"Traitement {n + 1}/{len(taches)} : {f.name} → {code or 'modifié'}")

                def progres(fait, total, n=n):
                    if stop.is_set():
                        raise Annule
                    fen.after(0, barre.config, {"value": 100 * (n + fait / max(total, 1)) / len(taches)})

                try:
                    if voir:
                        fen.after(0, ouvrir_apercu, code, f, *traduire_contenu(f, code, progres=progres, **options))
                    else:
                        traduire_fichier(f, code, integrer=integrer.get(), progres=progres, **options)
                    faits += 1
                except Annule:
                    break
                except Exception as e:  # erreur réseau, fichier invalide…
                    erreurs.append(f"{f.name} → {code or 'modifié'} : {e}")
            fin = "Arrêté" if stop.is_set() else "Terminé"
            fen.after(0, barre.config, {"value": 0 if stop.is_set() else 100})
            fen.after(0, etat.set, f"{fin} : {faits}/{len(taches)} fichier(s).")
            if erreurs:
                fen.after(0, messagebox.showerror, "Erreurs", "\n".join(erreurs))
            fen.after(0, bouton.config, {"state": "normal"})
            fen.after(0, arreter.config, {"state": "disabled"})

        threading.Thread(target=travail, daemon=True).start()

    cadre = ttk.Frame(fen, padding=12)
    cadre.grid(sticky="nsew")
    cadre.columnconfigure(1, weight=1)
    cadre.rowconfigure(2, weight=1)

    ttk.Label(cadre, text="Fichiers :").grid(row=0, column=0, sticky="w")
    ttk.Entry(cadre, textvariable=resume, state="readonly").grid(row=0, column=1, sticky="we", padx=4)
    boutons = ttk.Frame(cadre)
    boutons.grid(row=0, column=2, sticky="e")
    ttk.Button(boutons, text="Fichiers…", command=choisir_fichiers).grid(row=0, column=0)
    ttk.Button(boutons, text="Dossier…", command=choisir_dossier).grid(row=0, column=1, padx=(4, 0))

    reglages = ttk.Frame(cadre)
    reglages.grid(row=1, column=0, columnspan=3, sticky="we", pady=8)
    ttk.Label(reglages, text="De :").grid(row=0, column=0, sticky="w")
    ttk.Combobox(reglages, textvariable=source, values=[AUTO, *LANGUES], state="readonly", width=16)\
        .grid(row=0, column=1, sticky="w", padx=4)
    ttk.Label(reglages, text="Moteur :").grid(row=0, column=2, sticky="w", padx=(12, 0))
    ttk.Combobox(reglages, textvariable=nom_moteur, values=list(traduction.MOTEURS), state="readonly", width=18)\
        .grid(row=0, column=3, sticky="w", padx=4)
    ttk.Label(reglages, text="Clé DeepL :").grid(row=0, column=4, sticky="w", padx=(12, 0))
    ttk.Entry(reglages, textvariable=cle, show="•", width=16).grid(row=0, column=5, sticky="w", padx=4)
    ttk.Label(reglages, text="Format :").grid(row=1, column=0, sticky="w", pady=(6, 0))
    ttk.Combobox(reglages, textvariable=fmt, values=list(FORMATS), state="readonly", width=16)\
        .grid(row=1, column=1, sticky="w", padx=4, pady=(6, 0))
    ttk.Label(reglages, text="Décalage (s) :").grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(6, 0))
    ttk.Entry(reglages, textvariable=decalage, width=8).grid(row=1, column=3, sticky="w", padx=4, pady=(6, 0))

    ttk.Label(cadre, text="Vers :").grid(row=2, column=0, sticky="nw")
    zone_liste = ttk.Frame(cadre)
    zone_liste.grid(row=2, column=1, sticky="nsew", padx=4)
    zone_liste.columnconfigure(0, weight=1)
    zone_liste.rowconfigure(0, weight=1)
    liste = tk.Listbox(zone_liste, selectmode="multiple", exportselection=False, height=6, borderwidth=1)
    liste.grid(row=0, column=0, sticky="nsew")
    defil = ttk.Scrollbar(zone_liste, orient="vertical", command=liste.yview)
    defil.grid(row=0, column=1, sticky="ns")
    liste.configure(yscrollcommand=defil.set)
    deja = config.get("langues") or [config.get("langue", "Français")]
    for n, nom in enumerate(LANGUES):
        liste.insert("end", nom)
        if nom in deja:
            liste.selection_set(n)

    options = ttk.Frame(cadre)
    options.grid(row=2, column=2, sticky="nw")
    ttk.Checkbutton(options, text="Réparer le fichier", variable=reparer).grid(sticky="w")
    ttk.Checkbutton(options, text="Aperçu avant d'enregistrer", variable=apercu).grid(sticky="w")
    ttk.Checkbutton(options, text="Intégrer à la vidéo", variable=integrer).grid(sticky="w")
    ttk.Checkbutton(options, text="Thème sombre", variable=sombre, command=theme).grid(sticky="w")
    ttk.Button(options, text="Glossaire…", command=ouvrir_glossaire).grid(sticky="we", pady=(6, 0))
    ttk.Button(options, text="Ajouter au clic droit", command=installer_menu).grid(sticky="we", pady=(4, 0))

    actions = ttk.Frame(cadre)
    actions.grid(row=3, column=1, sticky="w", padx=4, pady=(10, 0))
    bouton = ttk.Button(actions, text="Traduire", command=lancer)
    bouton.grid(row=0, column=0)
    arreter = ttk.Button(actions, text="Arrêter", command=stop.set, state="disabled")
    arreter.grid(row=0, column=1, padx=(4, 0))
    barre = ttk.Progressbar(cadre, maximum=100)
    barre.grid(row=4, column=0, columnspan=3, sticky="we", pady=(10, 0))
    ttk.Label(cadre, textvariable=etat).grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))
    maj = ttk.Button(cadre)

    def verifier_maj():
        try:
            version, page = derniere_version()
        except Exception:  # hors ligne : pas de vérification, sans gêner
            return
        if plus_recente(version):
            import webbrowser
            fen.after(0, lambda: (maj.config(text=f"Nouvelle version {version} disponible : télécharger",
                                             command=lambda: webbrowser.open(page)),
                                  maj.grid(row=6, column=0, columnspan=3, sticky="w", pady=(6, 0))))

    threading.Thread(target=verifier_maj, daemon=True).start()
    if DND_FILES:
        fen.drop_target_register(DND_FILES)
        fen.dnd_bind("<<Drop>>", lambda e: remplacer(fen.tk.splitlist(e.data)))
        etat.set(etat.get() + " Glisse-les ici.")
    theme()
    montrer()
    fen.mainloop()


def main():
    p = argparse.ArgumentParser(description="Traduit, décale ou convertit des sous-titres (.srt, .vtt, .ass, .mkv).")
    p.add_argument("fichiers", nargs="*", help="fichier(s) ou dossier(s) de sous-titres")
    p.add_argument("-l", "--langue", help="langue(s) cible, séparées par des virgules : fr ou fr,es,de")
    p.add_argument("-s", "--source", default="auto", help="langue d'origine (défaut : détection auto)")
    p.add_argument("-m", "--moteur", choices=sorted(set(traduction.MOTEURS.values())), default="google")
    p.add_argument("--cle", default=os.environ.get("DEEPL_API_KEY", ""), help="clé DeepL (ou DEEPL_API_KEY)")
    p.add_argument("--reparer", action="store_true", help="renumérote, retire doublons et chevauchements")
    p.add_argument("--decaler", type=float, default=0, metavar="SECONDES",
                   help="décale tous les sous-titres (négatif : plus tôt), ex. 1.5 ou -2")
    p.add_argument("--format", choices=["srt", "vtt", "ass"], help="convertit dans ce format")
    p.add_argument("--integrer", action="store_true", help="ajoute la traduction en piste dans la vidéo (ffmpeg)")
    p.add_argument("--version", action="version", version=VERSION)
    p.add_argument("--installer-menu", action="store_true", help="ajoute « Traduire les sous-titres » au clic droit")
    p.add_argument("--desinstaller-menu", action="store_true", help="retire l'entrée du clic droit")
    if sys.stdout is None:  # .exe sans console (lancé par l'installateur) : print ne doit pas planter
        sys.stdout = sys.stderr = open(os.devnull, "w")
    args = p.parse_args()
    if args.installer_menu or args.desinstaller_menu:
        menu_contextuel(args.installer_menu)
        print("Clic droit " + ("ajouté." if args.installer_menu else "retiré."))
        return
    if not (args.langue or args.decaler or args.format or args.reparer):
        # rien à faire en ligne de commande : interface (fichiers pré-remplis si glissés sur Traduire.bat)
        interface(args.fichiers)
        return
    fichiers = lister(args.fichiers)
    if not fichiers:
        p.error("indique au moins un fichier .srt, .vtt, .ass, .mkv (ou un dossier)")
    options = dict(source=args.source, moteur=args.moteur, cle=args.cle, glossaire=glossaire(), reparer=args.reparer,
                   decalage=args.decaler, fmt=args.format, integrer=args.integrer)
    for f in fichiers:
        for langue in args.langue.split(",") if args.langue else [None]:
            print(f"{f} -> {traduire_fichier(f, langue and langue.strip(), **options)}")


if __name__ == "__main__":
    sys.exit(main())
