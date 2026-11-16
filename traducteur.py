"""Traducteur de sous-titres .srt.

Ligne de commande : python traducteur.py film.srt -l fr
Interface : python traducteur.py   (ou glisser un .srt sur Traduire.bat)
"""
import argparse
import sys
import threading
from pathlib import Path

import srt
import traduction

LANGUES = {"Français": "fr", "Anglais": "en", "Espagnol": "es", "Allemand": "de", "Italien": "it",
           "Portugais": "pt", "Néerlandais": "nl", "Russe": "ru", "Arabe": "ar", "Japonais": "ja",
           "Chinois": "zh-CN", "Coréen": "ko", "Turc": "tr", "Polonais": "pl"}


def chemin_sortie(entree: Path, langue: str) -> Path:
    return entree.with_name(f"{entree.stem}.{langue}.srt")


def traduire_fichier(entree, langue: str, traduire=None) -> Path:
    entree = Path(entree)
    blocs = srt.parser(srt.lire_fichier(entree))
    traduits = traduction.traduire_blocs(blocs, traduire or traduction.google(langue))
    sortie = chemin_sortie(entree, langue)
    sortie.write_text(srt.ecrire(traduits), encoding="utf-8")
    return sortie


def interface(fichier=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    fen = tk.Tk()
    fen.title("Traducteur de sous-titres")
    icone = Path(__file__).with_name("icone.ico")
    if icone.exists():
        fen.iconbitmap(icone)
    fen.resizable(False, False)
    chemin = tk.StringVar(value=fichier or "")
    langue = tk.StringVar(value="Français")
    etat = tk.StringVar(value="Choisis un fichier .srt et une langue.")

    def choisir():
        f = filedialog.askopenfilename(filetypes=[("Sous-titres", "*.srt")])
        if f:
            chemin.set(f)

    def lancer():
        if not Path(chemin.get()).is_file():
            messagebox.showerror("Erreur", "Fichier introuvable.")
            return
        bouton.config(state="disabled")
        etat.set("Traduction en cours…")

        def travail():
            try:
                sortie = traduire_fichier(chemin.get(), LANGUES[langue.get()])
                fen.after(0, etat.set, f"Terminé : {sortie.name}")
            except Exception as e:  # erreur réseau, fichier invalide…
                fen.after(0, messagebox.showerror, "Erreur", str(e))
                fen.after(0, etat.set, "Échec.")
            fen.after(0, bouton.config, {"state": "normal"})

        threading.Thread(target=travail, daemon=True).start()

    cadre = ttk.Frame(fen, padding=12)
    cadre.grid()
    ttk.Label(cadre, text="Fichier :").grid(row=0, column=0, sticky="w")
    ttk.Entry(cadre, textvariable=chemin, width=50).grid(row=0, column=1, padx=4)
    ttk.Button(cadre, text="Parcourir…", command=choisir).grid(row=0, column=2)
    ttk.Label(cadre, text="Langue :").grid(row=1, column=0, sticky="w", pady=8)
    ttk.Combobox(cadre, textvariable=langue, values=list(LANGUES), state="readonly", width=20)\
        .grid(row=1, column=1, sticky="w", padx=4)
    bouton = ttk.Button(cadre, text="Traduire", command=lancer)
    bouton.grid(row=2, column=1, sticky="w", padx=4)
    ttk.Label(cadre, textvariable=etat).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))
    fen.mainloop()


def main():
    p = argparse.ArgumentParser(description="Traduit des sous-titres .srt en gardant le timing.")
    p.add_argument("fichiers", nargs="*", help="fichier(s) .srt")
    p.add_argument("-l", "--langue", help="langue cible (code : fr, en, es, de…)")
    args = p.parse_args()
    if not args.langue:  # pas de langue : interface (fichier pré-rempli si glissé sur Traduire.bat)
        interface(args.fichiers[0] if args.fichiers else None)
        return
    if not args.fichiers:
        p.error("indique au moins un fichier .srt")
    for f in args.fichiers:
        print(f"{f} -> {traduire_fichier(f, args.langue)}")


if __name__ == "__main__":
    sys.exit(main())
