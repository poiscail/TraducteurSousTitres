# Graph Report - TraducteurSousTitres  (2026-11-16)

## Corpus Check
- 5 files · ~4,261 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .bat 2, .srt 2, (none) 1)

## Summary
- 135 nodes · 246 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0d0cc32b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- traducteur.py
- test_srt.py
- Documentation README
- traduire_fichier
- traduction.py
- moteur
- travail
- traduire_textes
- Tests pytest

## God Nodes (most connected - your core abstractions)
1. `traduire_blocs()` - 15 edges
2. `interface()` - 14 edges
3. `traduire_contenu()` - 12 edges
4. `Bloc` - 11 edges
5. `parser()` - 10 edges
6. `traduire_fichier()` - 10 edges
7. `lister()` - 8 edges
8. `main()` - 8 edges
9. `reparer()` - 7 edges
10. `traduire_textes()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `test_glossaire_protege_les_termes()` --calls--> `Bloc`  [EXTRACTED]
  tests/test_srt.py → srt.py
- `test_traduction_garde_numeros_timings_et_balises()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_balises_au_milieu_gardees_ou_retirees()` --calls--> `traduire_blocs()`  [EXTRACTED]
  tests/test_srt.py → traduction.py
- `test_ligne_trop_longue_coupee_en_deux()` --calls--> `traduire_blocs()`  [EXTRACTED]
  tests/test_srt.py → traduction.py
- `test_progression()` --calls--> `traduire_textes()`  [EXTRACTED]
  tests/test_srt.py → traduction.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Flux de traduction SRT** — readme_traduire_bat, readme_traducteur_py, readme_srt_translation, readme_google_translate, readme_language_codes [INFERRED 0.75]

## Communities (9 total, 1 thin omitted)

### Community 0 - "traducteur.py"
Cohesion: 0.12
Nodes (18): test_dossier_ignore_les_traductions(), test_menu_contextuel(), test_plusieurs_langues_en_ligne_de_commande(), Annule, commande_menu(), ecrire_config(), glossaire(), interface() (+10 more)

### Community 1 - "test_srt.py"
Cohesion: 0.13
Nodes (18): Bloc, ecrire(), ecrire_ass(), _hms(), lire_fichier(), _ms(), parser(), parser_ass() (+10 more)

### Community 2 - "Documentation README"
Cohesion: 0.18
Nodes (9): Lecture UTF-8 et Windows-1252, ecriture UTF-8, Google Translate (moteur gratuit sans cle), Codes de langue (-l), Nommage de sortie (film.srt vers film.fr.srt), Python 3.10+ (prerequis), Traduction de fichier SRT, traducteur.py (ligne de commande), Traducteur de sous-titres (+1 more)

### Community 3 - "traduire_fichier"
Cohesion: 0.18
Nodes (8): test_ass(), test_nom_unique_sans_ecraser(), test_video_avec_ffmpeg(), test_vtt(), chemin_sortie(), deja_traduit(), extraire_sous_titres(), traduire_fichier()

### Community 4 - "traduction.py"
Cohesion: 0.16
Nodes (10): test_glossaire_protege_les_termes(), test_repartir(), balises_intactes(), decouper(), lire_glossaire(), nb_lignes(), proteger(), repartir() (+2 more)

### Community 5 - "moteur"
Cohesion: 0.15
Nodes (11): test_deepl(), test_reessaie_si_429(), faux_urlopen(), argos(), deepl(), traduire(), _envoyer(), google() (+3 more)

### Community 6 - "travail"
Cohesion: 0.29
Nodes (8): travail(), progres(), ouvrir_apercu(), enregistrer(), modifier(), valider(), une_ligne(), theme()

### Community 7 - "traduire_textes"
Cohesion: 0.29
Nodes (4): test_arret_pendant_la_traduction(), test_lot_mal_decoupe_repasse_un_par_un(), test_progression(), traduire_textes()

## Knowledge Gaps
- **9 isolated node(s):** `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)`, `Codes de langue (-l)`, `Nommage de sortie (film.srt vers film.fr.srt)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 45 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `interface()` connect `traducteur.py` to `travail`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `interface()` (e.g. with `choisir_dossier()` and `choisir_fichiers()`) actually correct?**
  _`interface()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `traducteur.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11576354679802955 - nodes in this community are weakly interconnected._
- **Why does `traduire_contenu()` connect `test_srt.py` to `traducteur.py`, `traduire_fichier`, `traduction.py`, `moteur`, `travail`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Should `test_srt.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12561576354679804 - nodes in this community are weakly interconnected._
- **Why does `traduire_blocs()` connect `traduction.py` to `test_srt.py`, `traduire_textes`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._