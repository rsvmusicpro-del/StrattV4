# StrattV4 — phase 2 : architecture du pipeline et protection de la baseline

Date : 2026-11-06  
Branche de travail : `evolution`  
Baseline : `v4-foundation` / `5978d89e4deeacb93f415111511d2fdf98763041`

## Commit de code validé

- Commit : `78d71c23dfa4dfbed5003223e2489eae8c7dbbec`.
- Build : [Build StrattV4 Push 1 #62](https://github.com/rsvmusicpro-del/StrattV4/actions/runs/42296857696).
- Résultat : `success`.
- Artefact : `StrattV4-Push1-Test`, ID `13541798425`.
- Taille : 12 264 456 octets.
- SHA-256 : `8b5e78a1761ec5528818e533f7833c7849c143f30ee0c2d789835825b2511ea1`.
- Expiration GitHub : 2026-11-13.

## Refactorisation réalisée

### 1. Registre unique des patchs

Le nouveau fichier `scripts/patch_manifest.py` devient la source de vérité pour :
- les 22 scripts de personnalisation, dans leur ordre d'exécution ;
- la finalité de chaque étape ;
- la révision DrivenByMoss attendue ;
- les 24 fichiers Java qui doivent exister après application.

La résolution vérifie l'unicité des noms, la forme des chemins et la présence de chaque script. Les tests de navigation, de déplacement de pistes, de déplacement de périphériques, de SMART et de noms longs contrôlent désormais le registre, plutôt que d'analyser artificiellement le texte de l'orchestrateur.

### 2. Orchestrateur transactionnel découpé en fonctions testables

`scripts/apply_push1_palette_transactional.py` sépare désormais :
- `verify_upstream_revision` : contrôle du SHA amont épinglé ;
- `ensure_clean_source_tree` : refus des modifications locales dans les sources Java amont ;
- `run_patch_steps` : exécution ordonnée et arrêt au premier patch en échec, avec le nom de l'étape dans le diagnostic ;
- `validate_staged_sources` : contrôle des sorties attendues ;
- `install_staged_source` : remplacement atomique et restauration de l'original si le dernier remplacement échoue.

Le pipeline conserve le principe de staging temporaire : aucune modification destructive du sous-module n'est installée avant la réussite de tous les patchs et de leurs validations.

### 3. Tests comportementaux du pipeline Python

Le nouveau fichier `tests/test_patch_pipeline.py` teste notamment :
- l'acceptation et le refus des sorties Java attendues ;
- l'installation réussie de l'arbre préparé ;
- l'injection d'un échec au moment du remplacement et la restauration effective de l'arbre original ;
- l'acceptation du SHA amont épinglé et le refus d'une révision différente ;
- le refus d'un arbre amont localement modifié ;
- l'ordre d'exécution du registre ;
- l'arrêt immédiat sur un patch en erreur et le diagnostic de l'étape fautive.

La suite Python a exécuté 106 tests avec succès sur le run #62. Les tests Java comportementaux, la compilation Maven, la vérification du service Push 1 et l'intégrité ZIP sont également passés.

## Protection automatisée de la baseline

Le workflow vérifie maintenant que la branche `v4-foundation` pointe toujours exactement sur `5978d89e4deeacb93f415111511d2fdf98763041`. Il compare ensuite directement les arbres Git et fait échouer le build si un fichier a été supprimé par rapport à cette base.

Le premier essai a échoué car le checkout GitHub est superficiel et la notation à trois points nécessitait une base de fusion absente. La comparaison a été corrigée en comparaison directe des deux arbres (`git diff ... FETCH_HEAD HEAD`), sans téléchargement de l'historique complet du sous-module. Le run #62 confirme que ce contrôle passe.

Cette barrière CI ne remplace pas une règle de protection GitHub contre la suppression ou le force-push. La protection administrative de la branche reste à activer par un administrateur du dépôt.

## Vérification de non-régression du dépôt

Comparaison vérifiée entre la baseline et le commit de code testé :
- `evolution` : 19 commits en avance ;
- retard : 0 commit ;
- fichiers supprimés : aucun ;
- `v4-foundation` : SHA inchangé `5978d89e4deeacb93f415111511d2fdf98763041`.

Le sous-module DrivenByMoss reste épinglé à `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`.

## Limites restantes

- Cette phase modernise l'outillage de patch, son orchestration et sa preuve de non-régression. Elle ne constitue pas encore une réécriture complète des comportements Java personnalisés.
- Le run CI prouve la compilation et le packaging, pas une nouvelle recette matérielle. La validation du nouveau binaire sur Push 1 physique avec Bitwig Studio 4.3.10 reste à effectuer.
- Les règles GitHub de protection de branche nécessitent des droits administrateur non disponibles via l'intégration utilisée.
- L'artefact de test est temporaire ; il doit être archivé ailleurs avant son expiration si une conservation longue durée est souhaitée.
