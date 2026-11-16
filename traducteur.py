"""Traducteur de sous-titres (.srt, .vtt, .ass).

Ligne de commande : python traducteur.py film.srt -l fr
Interface : python traducteur.py   (ou glisser des fichiers sur Traduire.bat)
"""
import argparse
import json
import os
import sys
import threading
from pathlib import Path

import srt
import traduction

LANGUES = {"Français": "fr", "Anglais": "en", "Espagnol": "es", "Allemand": "de", "Italien": "it",
           "Portugais": "pt", "Néerlandais": "nl", "Russe": "ru", "Arabe": "ar", "Japonais": "ja",
           "Chinois": "zh-CN", "Coréen": "ko", "Turc": "tr", "Polonais": "pl"}
AUTO = "Détection auto"
EXTENSIONS = {".srt", ".vtt", ".ass", ".ssa"}
CONFIG = Path(os.environ.get("APPDATA", Path.home())) / "TraducteurSousTitres.json"


def chemin_sortie(entree: Path, langue: str) -> Path:
    return entree.with_name(f"{entree.stem}.{langue}{entree.suffix}")


def deja_traduit(f: Path) -> bool:
    """film.fr.srt : sortie d'une traduction précédente, à ne pas retraduire."""
    return Path(f.stem).suffix[1:] in LANGUES.values()


def lister(chemins) -> list[Path]:
    """Fichiers de sous-titres donnés directement ou contenus dans les dossiers donnés."""
    fichiers = []
    for c in map(Path, chemins):
        if c.is_dir():
            fichiers += sorted(f for f in c.iterdir() if f.suffix.lower() in EXTENSIONS and not deja_traduit(f))
        elif c.suffix.lower() in EXTENSIONS:
            fichiers.append(c)
    return fichiers


def traduire_fichier(entree, langue: str, traduire=None, source="auto", progres=None) -> Path:
    entree = Path(entree)
    texte = srt.lire_fichier(entree)
    traduire = traduire or traduction.google(langue, source)
    if entree.suffix.lower() in (".ass", ".ssa"):
        lignes, blocs = srt.parser_ass(texte)
        resultat = srt.ecrire_ass(lignes, traduction.traduire_blocs(blocs, traduire, progres))
    else:
        resultat = srt.ecrire(traduction.traduire_blocs(srt.parser(texte), traduire, progres))
    sortie = chemin_sortie(entree, langue)
    sortie.write_text(resultat, encoding="utf-8")
    return sortie


def lire_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def ecrire_config(**valeurs):
    try:
        CONFIG.write_text(json.dumps(valeurs, ensure_ascii=False), encoding="utf-8")
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

    fen.title("Traducteur de sous-titres")
    icone = Path(__file__).with_name("icone.ico")
    if icone.exists():
        fen.iconbitmap(icone)
    fen.resizable(False, False)
    config = lire_config()
    choix = lister(fichiers)
    resume = tk.StringVar()
    langue = tk.StringVar(value=config.get("langue", "Français"))
    source = tk.StringVar(value=config.get("source", AUTO))
    etat = tk.StringVar(value="Choisis des sous-titres (.srt, .vtt, .ass) et une langue.")

    def montrer():
        resume.set(str(choix[0]) if len(choix) == 1 else f"{len(choix)} fichiers" if choix else "")

    def remplacer(nouveaux):
        choix[:] = lister(nouveaux)
        montrer()

    def choisir_fichiers():
        f = filedialog.askopenfilenames(filetypes=[("Sous-titres", "*.srt *.vtt *.ass *.ssa")])
        if f:
            remplacer(f)

    def choisir_dossier():
        d = filedialog.askdirectory()
        if d:
            remplacer([d])

    def lancer():
        if not choix:
            messagebox.showerror("Erreur", "Aucun fichier de sous-titres choisi.")
            return
        ecrire_config(langue=langue.get(), source=source.get())
        cible, src = LANGUES[langue.get()], LANGUES.get(source.get(), "auto")
        bouton.config(state="disabled")
        barre["value"] = 0
        a_faire = list(choix)

        def travail():
            erreurs = []
            for n, f in enumerate(a_faire):
                fen.after(0, etat.set, f"Traduction {n + 1}/{len(a_faire)} : {f.name}")

                def progres(fait, total, n=n):
                    fen.after(0, barre.config, {"value": 100 * (n + fait / max(total, 1)) / len(a_faire)})

                try:
                    traduire_fichier(f, cible, source=src, progres=progres)
                except Exception as e:  # erreur réseau, fichier invalide…
                    erreurs.append(f"{f.name} : {e}")
            fen.after(0, barre.config, {"value": 100})
            fen.after(0, etat.set, f"Terminé : {len(a_faire) - len(erreurs)}/{len(a_faire)} fichier(s) traduit(s).")
            if erreurs:
                fen.after(0, messagebox.showerror, "Erreurs", "\n".join(erreurs))
            fen.after(0, bouton.config, {"state": "normal"})

        threading.Thread(target=travail, daemon=True).start()

    cadre = ttk.Frame(fen, padding=12)
    cadre.grid()
    ttk.Label(cadre, text="Fichiers :").grid(row=0, column=0, sticky="w")
    ttk.Entry(cadre, textvariable=resume, width=50, state="readonly").grid(row=0, column=1, padx=4)
    boutons = ttk.Frame(cadre)
    boutons.grid(row=0, column=2)
    ttk.Button(boutons, text="Fichiers…", command=choisir_fichiers).grid(row=0, column=0)
    ttk.Button(boutons, text="Dossier…", command=choisir_dossier).grid(row=0, column=1, padx=(4, 0))
    ttk.Label(cadre, text="De :").grid(row=1, column=0, sticky="w", pady=(8, 0))
    ttk.Combobox(cadre, textvariable=source, values=[AUTO, *LANGUES], state="readonly", width=20)\
        .grid(row=1, column=1, sticky="w", padx=4, pady=(8, 0))
    ttk.Label(cadre, text="Vers :").grid(row=2, column=0, sticky="w", pady=8)
    ttk.Combobox(cadre, textvariable=langue, values=list(LANGUES), state="readonly", width=20)\
        .grid(row=2, column=1, sticky="w", padx=4)
    bouton = ttk.Button(cadre, text="Traduire", command=lancer)
    bouton.grid(row=3, column=1, sticky="w", padx=4)
    barre = ttk.Progressbar(cadre, length=420, maximum=100)
    barre.grid(row=4, column=0, columnspan=3, sticky="we", pady=(10, 0))
    ttk.Label(cadre, textvariable=etat).grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))
    if DND_FILES:
        fen.drop_target_register(DND_FILES)
        fen.dnd_bind("<<Drop>>", lambda e: remplacer(fen.tk.splitlist(e.data)))
        etat.set(etat.get() + " Glisse-les ici.")
    montrer()
    fen.mainloop()


def main():
    p = argparse.ArgumentParser(description="Traduit des sous-titres (.srt, .vtt, .ass) en gardant le timing.")
    p.add_argument("fichiers", nargs="*", help="fichier(s) ou dossier(s) de sous-titres")
    p.add_argument("-l", "--langue", help="langue cible (code : fr, en, es, de…)")
    p.add_argument("-s", "--source", default="auto", help="langue d'origine (défaut : détection auto)")
    args = p.parse_args()
    if not args.langue:  # pas de langue : interface (fichiers pré-remplis si glissés sur Traduire.bat)
        interface(args.fichiers)
        return
    fichiers = lister(args.fichiers)
    if not fichiers:
        p.error("indique au moins un fichier .srt, .vtt ou .ass (ou un dossier)")
    for f in fichiers:
        print(f"{f} -> {traduire_fichier(f, args.langue, source=args.source)}")


if __name__ == "__main__":
    sys.exit(main())
