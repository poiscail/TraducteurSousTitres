# Graph Report - TraducteurSousTitres  (2026-11-17)

## Corpus Check
- 5 files · ~5,584 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: .bat 3, .srt 2, (none) 1)

## Summary
- 162 nodes · 312 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a10df6e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- traducteur.py
- test_srt.py
- Documentation README
- Path
- traduction.py
- travail
- test_srt.py
- Tests pytest

## God Nodes (most connected - your core abstractions)
1. `traduire_contenu()` - 15 edges
2. `interface()` - 15 edges
3. `traduire_blocs()` - 15 edges
4. `Bloc` - 13 edges
5. `parser()` - 12 edges
6. `traduire_fichier()` - 12 edges
7. `decaler()` - 9 edges
8. `main()` - 9 edges
9. `vers_cues()` - 8 edges
10. `lister()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_dossier_ignore_les_traductions()` --calls--> `lister()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_traduction_garde_numeros_timings_et_balises()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_progression()` --calls--> `traduire_textes()`  [EXTRACTED]
  tests/test_srt.py → traduction.py
- `test_vtt()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py
- `test_ass()` --calls--> `traduire_fichier()`  [EXTRACTED]
  tests/test_srt.py → traducteur.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Flux de traduction SRT** — readme_traduire_bat, readme_traducteur_py, readme_srt_translation, readme_google_translate, readme_language_codes [INFERRED 0.75]

## Communities (8 total, 1 thin omitted)

### Community 0 - "traducteur.py"
Cohesion: 0.09
Nodes (22): test_decaler_et_convertir_sans_traduire(), test_menu_contextuel(), test_plus_recente(), test_plusieurs_langues_en_ligne_de_commande(), Annule, commande_menu(), derniere_version(), ecrire_config() (+14 more)

### Community 1 - "test_srt.py"
Cohesion: 0.11
Nodes (24): _ass_hms(), _ass_vers_html(), decaler(), ecrire(), ecrire_ass(), ecrire_format(), _hms(), _html_vers_ass() (+16 more)

### Community 2 - "Documentation README"
Cohesion: 0.18
Nodes (9): Lecture UTF-8 et Windows-1252, ecriture UTF-8, Google Translate (moteur gratuit sans cle), Codes de langue (-l), Nommage de sortie (film.srt vers film.fr.srt), Python 3.10+ (prerequis), Traduction de fichier SRT, traducteur.py (ligne de commande), Traducteur de sous-titres (+1 more)

### Community 3 - "Path"
Cohesion: 0.20
Nodes (7): test_nom_unique_sans_ecraser(), chemin_sortie(), deja_traduit(), enregistrer(), extraire_sous_titres(), ffmpeg(), integrer_video()

### Community 4 - "traduction.py"
Cohesion: 0.09
Nodes (20): Bloc, test_balises_au_milieu_gardees_ou_retirees(), test_glossaire_protege_les_termes(), test_ligne_trop_longue_coupee_en_deux(), test_repartir(), argos(), balises_intactes(), decouper() (+12 more)

### Community 6 - "travail"
Cohesion: 0.29
Nodes (8): travail(), progres(), ouvrir_apercu(), modifier(), valider(), sauver(), une_ligne(), theme()

### Community 7 - "test_srt.py"
Cohesion: 0.12
Nodes (14): test_arret_pendant_la_traduction(), test_ass(), test_deepl(), test_dossier_ignore_les_traductions(), test_integrer_dans_la_video(), test_lot_mal_decoupe_repasse_un_par_un(), test_progression(), test_reessaie_si_429() (+6 more)

## Knowledge Gaps
- **9 isolated node(s):** `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)`, `Codes de langue (-l)`, `Nommage de sortie (film.srt vers film.fr.srt)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 54 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `interface()` connect `traducteur.py` to `travail`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `interface()` (e.g. with `choisir_dossier()` and `choisir_fichiers()`) actually correct?**
  _`interface()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Traduire.bat (interface)`, `Lecture UTF-8 et Windows-1252, ecriture UTF-8`, `Google Translate (moteur gratuit sans cle)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `traducteur.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09411764705882353 - nodes in this community are weakly interconnected._
- **Why does `traduire_contenu()` connect `test_srt.py` to `traducteur.py`, `Path`, `traduction.py`, `travail`, `test_srt.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Should `test_srt.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10510510510510511 - nodes in this community are weakly interconnected._
- **Why does `traduire_blocs()` connect `traduction.py` to `test_srt.py`, `test_srt.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._