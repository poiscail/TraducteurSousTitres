# Graph Report - TraducteurSousTitres  (2026-11-16)

## Corpus Check
- 5 files · ~2,244 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .bat 2, .srt 2, (none) 1)

## Summary
- 86 nodes · 150 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7999b871`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- traducteur.py
- test_srt.py
- Documentation README
- lister
- traduction.py
- traduire_textes
- interface
- Tests pytest

## God Nodes (most connected - your core abstractions)
1. `traduire_fichier()` - 15 edges
2. `traduire_blocs()` - 12 edges
3. `Bloc` - 9 edges
4. `parser()` - 9 edges
5. `interface()` - 9 edges
6. `lister()` - 8 edges
7. `Traduction de fichier SRT` - 7 edges
8. `traduire_textes()` - 6 edges
9. `lire_fichier()` - 5 edges
10. `remplacer()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `test_progression()` --calls--> `traduire_textes()`  [EXTRACTED]
  tests/test_srt.py → traduction.py
- `test_vtt()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_ass()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_dossier_ignore_les_traductions()` --calls--> `lister()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_balises_au_milieu_gardees_ou_retirees()` --calls--> `Bloc`  [EXTRACTED]
  tests/test_srt.py → srt.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Flux de traduction SRT** — readme_traduire_bat, readme_traducteur_py, readme_srt_translation, readme_google_translate, readme_language_codes [INFERRED 0.75]

## Communities (8 total, 1 thin omitted)

### Community 0 - "traducteur.py"
Cohesion: 0.27
Nodes (4): ecrire_config(), lancer(), lire_config(), main()

### Community 1 - "test_srt.py"
Cohesion: 0.16
Nodes (12): ecrire(), ecrire_ass(), lire_fichier(), parser(), parser_ass(), test_aller_retour_identique(), test_ass(), test_crlf_et_bom() (+4 more)

### Community 2 - "Documentation README"
Cohesion: 0.18
Nodes (9): Lecture UTF-8 et Windows-1252, ecriture UTF-8, Google Translate (moteur gratuit sans cle), Codes de langue (-l), Nommage de sortie (film.srt vers film.fr.srt), Python 3.10+ (prerequis), Traduction de fichier SRT, traducteur.py (ligne de commande), Traducteur de sous-titres (+1 more)

### Community 3 - "lister"
Cohesion: 0.33
Nodes (4): test_dossier_ignore_les_traductions(), chemin_sortie(), deja_traduit(), lister()

### Community 4 - "traduction.py"
Cohesion: 0.18
Nodes (9): Bloc, test_balises_au_milieu_gardees_ou_retirees(), test_ligne_trop_longue_coupee_en_deux(), test_repartir(), balises_intactes(), decouper(), nb_lignes(), repartir() (+1 more)

### Community 5 - "traduire_textes"
Cohesion: 0.15
Nodes (9): test_lot_mal_decoupe_repasse_un_par_un(), test_progression(), test_reessaie_si_429(), travail(), progres(), google(), traduire(), traduire_textes() (+1 more)

### Community 6 - "interface"
Cohesion: 0.70
Nodes (5): interface(), choisir_dossier(), choisir_fichiers(), montrer(), remplacer()

## Knowledge Gaps
- **9 isolated node(s):** `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)`, `Codes de langue (-l)`, `Nommage de sortie (film.srt vers film.fr.srt)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 31 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `traduire_fichier()` connect `test_srt.py` to `traducteur.py`, `lister`, `traduction.py`, `traduire_textes`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `interface()` (e.g. with `choisir_dossier()` and `choisir_fichiers()`) actually correct?**
  _`interface()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `interface()` connect `interface` to `traducteur.py`, `lister`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `traduire_blocs()` connect `traduction.py` to `test_srt.py`, `traduire_textes`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._