# StrattV4 — protocole de reprise à froid

## Identité du projet

- Projet : StrattV4
- Extension produite : `StrattV4.bwextension`
- Dépôt : `rsvmusicpro-del/StrattV4`
- Branche de travail unique : `evolution`
- Branche baseline immuable : `v4-foundation` (ne jamais modifier)
- Commit baseline validé : `5978d89e4deeacb93f415111511d2fdf98763041`
- Build associé au snapshot courant : non disponible à ce stade. Dernier build CI vérifié : run `42265014484` (#21), commit `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`, artefact `13526433106`, digest `sha256:2d9f70c125e5a9d407ced37a66753f80c259a198de24bcb8f1a23703cb258dd4` (22 commits avant le snapshot)
- Politique anti-régression : `docs/REGRESSION_POLICY.md`
- Cible : Ableton Push 1 et Bitwig Studio 4.3.10
- Java : 17
- Source amont : DrivenByMoss 19.2.2
- Révision amont épinglée : `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`

## Règles impératives

1. Ce dépôt est le seul espace de travail du projet.
2. Ne jamais introduire de nom, lien, branche, issue, commit, badge ou documentation faisant référence à un autre projet applicatif.
3. Conserver le sous-module amont à la révision épinglée. Ne jamais modifier ni pousser dans le sous-module.
4. Toutes les personnalisations sont appliquées transactionnellement à une copie de travail.
5. Ne jamais supprimer, désactiver ou affaiblir un test pour obtenir une CI verte.
6. Ne pas déclarer une validation matérielle sur la seule base d'un build CI.
7. Ne pas réécrire l'historique, force-push ou supprimer de branche.
8. Tout changement fonctionnel doit être accompagné d'un test de non-régression et d'un compte rendu.
9. La baseline actuelle `v4-foundation` / `5978d89e4deeacb93f415111511d2fdf98763041` est désormais le snapshot de référence immuable. Le commit historique `ec5871a` reste conservé dans son ascendance. Toutes les évolutions se font exclusivement sur `evolution`.
10. Aucun comportement du snapshot source sauvegardé sous `5978d89` et déclaré validé matériellement par le propriétaire ne peut être supprimé ou dégradé. Lire `docs/REGRESSION_POLICY.md` avant chaque changement.

## Procédure de reprise

Au début de chaque session :

1. Lire intégralement ce document, le README et `docs/REGRESSION_POLICY.md`.
2. Vérifier que la branche active est `evolution`. Toute autre branche est en lecture seule, notamment `v4-foundation`.
3. Comparer le HEAD de `evolution` à la baseline `5978d89e4deeacb93f415111511d2fdf98763041` et expliquer chaque différence.
4. Lire l'état GitHub du dépôt et relever la branche active et son SHA.
5. Vérifier la présence du sous-module et sa révision exacte.
6. Lire les derniers commits, PR, workflows, résultats de tests et artefacts.
7. Examiner les modifications non consignées avant d'agir.
8. Reprendre la première tâche non terminée du journal de travail.
9. En cas d'incertitude sur un état, vérifier GitHub ; ne jamais supposer.

Marqueurs de procédure : `STRATTV4_RESUME`, `STRATTV4_ONLY`.

## Périmètre fonctionnel initial

- Palette 64 couleurs et correspondance LED Push 1.
- Vues SMART et gestion des notes MIDI.
- Gestion du cycle de vie des notes, des mappings différés et des changements de vue.
- Séquenceurs polyphonique et de notes.
- Navigation contextuelle Browser, Device, Rack, Session et séquenceur.
- Gestes Select/New et commandes modificateurs.
- Gestion du toucher et des encodeurs.
- Affichage français, noms longs et VU.
- Création de scènes et garde-fous de commandes.

Les scripts `scripts/apply_push1_*.py` décrivent les transformations appliquées au code amont. Les tests Python et Java sous `tests/` constituent le socle de non-régression à préserver.

## Build et preuves attendues

La workflow GitHub Actions doit :

1. récupérer le dépôt et son sous-module ;
2. vérifier le SHA amont épinglé ;
3. configurer Java 17 ;
4. enregistrer exclusivement le contrôleur Push 1 ;
5. exécuter le patcher transactionnel ;
6. exécuter les tests Java comportementaux et Python ;
7. compiler le projet avec Maven ;
8. vérifier le service d'enregistrement et l'intégrité de l'archive ;
9. publier l'artefact `StrattV4-Push1-Test`.

À chaque reprise, noter le SHA du commit, le run CI, les résultats de chaque étape, l'identifiant et le digest de l'artefact, ainsi que les tests matériels réellement effectués.

## État initial

- [x] Dépôt initialisé avec une branche de fondation.
- [x] Scripts de personnalisation et tests copiés dans ce dépôt.
- [x] Sous-module amont épinglé.
- [x] Workflow de build autonome ajouté.
- [ ] Premier build CI vérifié sur ce dépôt.
- [ ] Audit de l'ensemble des transformations et tests.
- [ ] Validation sur Push 1 physique avec Bitwig Studio 4.3.10.
- [ ] Vérification de la conformité des licences et notices avant toute redistribution.

## Journal de reprise

### Point de sauvegarde — évolution validée du 2026-11-06

- Commit de code testé : `084dad306accae879ecc72e94c8a531fbaeb3aeb`.
- Build CI : run `42256896568`, résultat `success`.
- Artefact unique : `StrattV4-Push1-Test`, ID `13522418500`, SHA-256 `4d578854652c96048253d33bcd3a7989adc11a08157b533e625acf1b669c6a93`.
- Le propriétaire confirme que le test matériel est effectué et concluant.
- Détails, changements, preuves et limites consignés dans `docs/EVOLUTION_CHECKPOINT_2026-11-06.md`.
- Comparaison avec la baseline : 7 commits en avance, 0 en retard. Baseline inchangée : `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.


### Initialisation

- Commit : `fac05b2ee0f535030b0677255b42adff48429e29`
- Branche : `v4-foundation`
- Arbre initial : scripts, tests, sous-module amont, workflow et README.
- Prochaine action : obtenir un build CI sur ce dépôt, corriger les erreurs éventuelles sans affaiblir les tests, puis exécuter l'audit complet.


## Baseline validée et branche unique

Voir impérativement `docs/REGRESSION_POLICY.md`. La baseline matérielle est le commit `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`, build #3, run `42248099882`, artefact digest `sha256:1a93fc5541b98b93ad98a9aebb51151452cb20b6c8c01f5a94dad892eb472dab`. La seule branche d'évolution autorisée est `evolution`. `v4-foundation` est réservée à la comparaison et ne doit recevoir aucun commit.


### Validation matérielle la plus récente — 2026-11-06

- Le propriétaire confirme que le dernier commit/build précédent fonctionne parfaitement sur le Push 1 ; cet état est enregistré comme testé et validé matériellement.
- Commit : `098443b6197539beced6536d223d89e1c44e3ed7` sur `evolution`.
- CI : build #15, run `42260732361`, résultat `success`.
- Artefact : `StrattV4-Push1-Test`, ID `13523784316`, digest `sha256:c91b9fc200e6fbc02a2d8519599c7e934e9661dfb1457f224297dc72610c68b5`.
- Baseline immuable : `v4-foundation` — `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.
- Cette validation ne remplace pas les contrôles automatisés du prochain commit ni sa propre recette matérielle.


### Reprise à froid — correction du réordonnancement des pistes (2026-11-06)

- HEAD examiné avant correction : `3ab70978e6d58f54a613dd4d75a353e39ea62bbf`.
- Dernier commit matériellement validé déclaré : `098443b6197539beced6536d223d89e1c44e3ed7`.
- Baseline immuable : `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.
- Échec signalé : SELECT + flèches ne déplaçait pas la piste ou le Group Track attendu.
- Cause identifiée dans le patch généré de `PushCursorCommand` : la condition avait dérivé de la vue Session vers `Modes.TRACK`, avait perdu l'exclusion de SHIFT et la protection `!cursorTrack.hasParent()` de la conception initiale.
- Correction préparée : limiter le geste à Session + SELECT sans SHIFT ; exiger un curseur existant, de premier niveau et un voisin disponible ; faire correspondre les LED à ces mêmes conditions.
- Tests renforcés : vérification des deux directions, du contexte, de SHIFT, de la hiérarchie parent/enfant, des limites et de la conservation de la navigation normale.
- État matériel : NON VALIDÉ jusqu'à un nouvel essai sur Push 1 / Bitwig Studio 4.3.10.


### Reprise — affectation SHIFT + flèches après échec matériel

- HEAD initial : `e08055f3d835cec71e99f930b6f0021951927b71` sur `evolution`.
- Échec matériel : SELECT + LEFT/RIGHT rejeté par le propriétaire.
- Nouvelle affectation : SHIFT + LEFT/RIGHT pour déplacer le top-level track/group d'un rang.
- Contextes : Session, Track et Volume ; pas de restriction Session seule.
- SELECT + flèches supprimé.
- Cursor track global Bitwig, vérification existence/voisin/niveau supérieur.
- Les pistes enfants sont protégées car l'API globale ne prouve pas un déplacement sûr dans les limites d'un groupe.
- Les LED reflètent la disponibilité réelle du déplacement.
- Tests couvrent les deux sens, les trois contextes, la suppression SELECT, les limites, les groupes et la navigation existante.
- État matériel : NON VALIDÉ.


### Audit de reprise — restauration du déplacement natif des pistes (2026-11-06)

- Parent contrôlé : `328089255626ec39ed2f400bea32db6f4a6f7bd5` sur `evolution`.
- Cause : `apply_push1_navigation.py` surchargeait auparavant `PushCursorCommand` et court-circuitait la délégation au mode actif ; le mode natif `AbstractTrackMode` ne recevait donc plus SHIFT + flèches.
- Correction présente : commit `50ec514c68b3fd4bd08df69f3f9db15a1fa70225`, qui retire cette surcharge et rétablit la délégation DrivenByMoss 19.2.2.
- Chemin natif : `PushCursorCommand` → `AbstractTrackMode.selectPrevious/NextItemPage` → `ICursorTrack.swapWithPrevious/Next` → `CursorTrackImpl` / `TrackInsertionPoint.moveTracks`.
- Ne pas réintroduire de `Push1TrackMoveCommand` ou de patch concurrent de `PushCursorCommand`.
- Test de garde ajouté au contrat de régression pour empêcher le pipeline transactionnel d'installer un second patch de déplacement.
- Le dernier run CI connu avant ce point est #21 / `42265014484`, associé à `2b26d12`, et non au parent `3280892`. Contrôler le nouveau run après ce commit et enregistrer son artefact/digest.
- Rapport utilisateur reçu : validation matérielle positive du dernier test matériel du dernier commit en date ; scénarios et SHA de l'extension testée non détaillés.
- Baseline immuable : `v4-foundation` / `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`. Continuer exclusivement sur `evolution`.


### Reprise à froid — reconstruction après rejet matériel du déplacement

- Rapport matériel propriétaire : déplacement des pistes/groupes aléatoire, dernière tentative rejetée.
- Révoquer le statut validé du geste SHIFT + flèches ; aucune validation matérielle de cette fonction n'est acquise.
- HEAD de départ : \`fc9f1813a2fa67a9ce58ae07f08ff371059c20f6\`.
- Dernier build avant correction : run #40 \`42280252862\`, succès ; artefact \`13534363252\`, digest \`sha256:4b6af8c510b5d98d1112f9f2b8643c1e5e75fbdd773868f170d79daff4661f6c\`. Ce build ne contient pas la correction sibling-bank.
- Historique des tentatives : \`3ab7097\`, \`847ae92\`, \`e08055f\`, \`e2f81d3\`, \`50ec514\`, \`fc9f181\`. Ne pas restaurer les anciennes interceptions personnalisées de \`PushCursorCommand\`.
- Défaut de l'algorithme amont : banque globale aplatie de 400 pistes + \`Track.position()\` pour choisir un voisin ; un Group Track développé peut être adjacent à son enfant dans cette banque. Une garde sur le seul parent du curseur ne suffit pas.
- Correction StrattV4 : \`scripts/apply_push1_track_reorder.py\` remplace la banque globale par \`CursorTrack.createSiblingsTrackBank(400, 0, 0, false, false)\` et résout le voisin via \`TrackBank.cursorIndex()\`. Le geste SHIFT + flèches et le routage natif sont conservés.
- Contrôler les tests, Maven, l'enregistrement Push 1, le contenu du JAR, le digest du nouvel artefact et la comparaison avec baseline + parent.
- Essai matériel obligatoire sur pistes racines, groupes repliés/dépliés, pistes enfants, limites et répétition des commandes. Jusqu'à confirmation, statut NON VALIDÉ.


## Dernière reprise — sauvegarde StrattV4 backup (2026-11-06)

- Commit de sauvegarde : `5978d89e4deeacb93f415111511d2fdf98763041`.
- Les branches `evolution` et `v4-foundation` ont été alignées sur ce commit ; arbre Git `3222a047e110c37a63161169ebf0979ecdb02e6a` identique au HEAD source antérieur `b08d03e`.
- Le propriétaire déclare le test matériel Push 1 + Bitwig positif. Le détail des scénarios et le SHA du binaire testé ne sont pas indépendamment établis.
- Build CI exact : run `42287559330` (#43), succès sur le SHA `5978d89e4deeacb93f415111511d2fdf98763041`.
- Artefact `StrattV4-Push1-Test`, ID `13538012774`, SHA-256 `24a4bc45be4505903aabd9ab14e56209585ff3dd08c5e1e00b6522db00003600`.
- Tests Java MIDI, suite Python, Maven, service Push 1 et intégrité ZIP : toutes les étapes réussies.
- Le run #21 n'est pas le build du snapshot ; utiliser le run #43.
- La baseline initiale `ec5871a` reste présente dans l'historique et dans les anciens points de sauvegarde.
