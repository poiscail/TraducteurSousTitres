# Graph Report - TraducteurSousTitres  (2026-11-16)

## Corpus Check
- 5 files · ~1,197 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: .srt 2, (none) 1, .bat 1)

## Summary
- 57 nodes · 91 edges · 9 communities (5 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `690f2bdd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CLI et interface
- Parseur SRT
- Documentation README
- Traduction de fichier
- Découpage des balises
- Moteur Google
- Traduction par lots
- Répartition des lignes
- Tests pytest

## God Nodes (most connected - your core abstractions)
1. `traduire_fichier()` - 11 edges
2. `parser()` - 8 edges
3. `traduire_blocs()` - 7 edges
4. `Traduction de fichier SRT` - 7 edges
5. `Bloc` - 5 edges
6. `lire_fichier()` - 5 edges
7. `traduire_textes()` - 5 edges
8. `ecrire()` - 4 edges
9. `interface()` - 4 edges
10. `main()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `test_traduction_garde_numeros_timings_et_balises()` --calls--> `parser()`  [EXTRACTED]
  tests/test_srt.py → srt.py
- `test_lot_mal_decoupe_repasse_un_par_un()` --calls--> `traduire_textes()`  [EXTRACTED]
  tests/test_srt.py → traduction.py
- `test_crlf_et_bom()` --calls--> `lire_fichier()`  [EXTRACTED]
  tests/test_srt.py → srt.py
- `test_windows_1252()` --calls--> `lire_fichier()`  [EXTRACTED]
  tests/test_srt.py → srt.py
- `test_aller_retour_identique()` --calls--> `parser()`  [EXTRACTED]
  tests/test_srt.py → srt.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Flux de traduction SRT** — readme_traduire_bat, readme_traducteur_py, readme_srt_translation, readme_google_translate, readme_language_codes [INFERRED 0.75]

## Communities (9 total, 4 thin omitted)

### Community 0 - "CLI et interface"
Cohesion: 0.23
Nodes (3): test_lot_mal_decoupe_repasse_un_par_un(), interface(), main()

### Community 1 - "Parseur SRT"
Cohesion: 0.27
Nodes (7): Bloc, ecrire(), lire_fichier(), parser(), test_aller_retour_identique(), test_crlf_et_bom(), test_windows_1252()

### Community 2 - "Documentation README"
Cohesion: 0.18
Nodes (9): Lecture UTF-8 et Windows-1252, ecriture UTF-8, Google Translate (moteur gratuit sans cle), Codes de langue (-l), Nommage de sortie (film.srt vers film.fr.srt), Python 3.10+ (prerequis), Traduction de fichier SRT, traducteur.py (ligne de commande), Traducteur de sous-titres (+1 more)

### Community 3 - "Traduction de fichier"
Cohesion: 0.40
Nodes (5): test_traduction_garde_numeros_timings_et_balises(), chemin_sortie(), lancer(), travail(), traduire_fichier()

### Community 5 - "Moteur Google"
Cohesion: 0.50
Nodes (3): google(), traduire(), vider()

## Knowledge Gaps
- **9 isolated node(s):** `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)`, `Codes de langue (-l)`, `Nommage de sortie (film.srt vers film.fr.srt)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 23 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `traduire_fichier()` connect `Traduction de fichier` to `CLI et interface`, `Parseur SRT`, `Moteur Google`, `Traduction par lots`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **What connects `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `traduire_blocs()` connect `Traduction par lots` to `Parseur SRT`, `Traduction de fichier`, `Découpage des balises`, `Répartition des lignes`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `traduire_textes()` connect `Traduction par lots` to `CLI et interface`, `Découpage des balises`, `Moteur Google`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._