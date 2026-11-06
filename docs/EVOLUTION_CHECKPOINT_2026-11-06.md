# StrattV4 — point de sauvegarde et état de non-régression

## Sauvegarde de référence la plus récente — 2026-11-06

- Commit : `5978d89e4deeacb93f415111511d2fdf98763041` — [StrattV4 backup](https://github.com/rsvmusicpro-del/StrattV4/commit/5978d89e4deeacb93f415111511d2fdf98763041).
- Branches `evolution` et `v4-foundation` positionnées sur ce même commit après la sauvegarde ; arbre identique `3222a047e110c37a63161169ebf0979ecdb02e6a`.
- Le commit est un snapshot sans changement de fichier par rapport au HEAD source `b08d03ec0e39187e5f200f14f051ce3eb0e82550` ; l'ancien baseline `ec5871a` est conservé comme parent historique.
- Le propriétaire confirme un test matériel positif sur Push 1 avec Bitwig le 2026-11-06. Cette déclaration est enregistrée comme validation utilisateur ; la matrice détaillée des scénarios et le SHA du binaire testé ne sont pas indépendamment documentés.
- Aucun build CI n'est associé à `b08d03e` ni au commit de sauvegarde. Le dernier build CI vérifié reste le run `42265014484` (#21), succès sur `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`, artefact `13526433106`, digest `sha256:2d9f70c125e5a9d407ced37a66753f80c259a198de24bcb8f1a23703cb258dd4`. Ce build précède de 22 commits le HEAD source sauvegardé et ne constitue pas une preuve de compilation du snapshot.

La sauvegarde prouve l'identité de l'arbre Git avant/après le commit de sauvegarde ; elle ne constitue pas une preuve de build ni une validation indépendante du matériel.

---

# StrattV4 — point de sauvegarde et état de non-régression

Date : 2026-11-06
Branche de travail : `evolution`
Baseline immuable : `v4-foundation` — `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`

## Point de sauvegarde validé

- Commit de code et de workflow testé : `084dad306accae879ecc72e94c8a531fbaeb3aeb`
- Branche : `evolution`
- Build CI : run `42256896568`
- Résultat CI : `success`
- Artefact unique : `StrattV4-Push1-Test`
- Artifact ID : `13522418500`
- Taille : `12,265,639 bytes`
- Digest : `sha256:4d578854652c96048253d33bcd3a7989adc11a08157b533e625acf1b669c6a93`
- Expiration GitHub indiquée : 2026-11-13. Archiver le binaire hors GitHub avant cette date si une conservation binaire à long terme est requise.

Le workflow publie exactement un artefact de test. Les tests du workflow vérifient qu'il n'existe qu'un seul appel d'upload et que le nom publié est `StrattV4-Push1-Test`.

## Évolutions incluses dans ce jalon

1. Registre MIDI des notes aplati : les matrices `long[][]` et `int[][]` sont remplacées par des tableaux linéaires préalloués, avec calcul explicite des index pad/word et channel/note. Cela supprime 144 sous-tableaux. Aucun gain chiffré de latence ou de mémoire n'est revendiqué faute de benchmark.
2. Renforcement du cycle de vie MIDI et des mappings différés, incluant protections contre l'application de mises à jour obsolètes, nettoyage de l'état des pads à la désactivation et libération lors de l'arrêt.
3. Couverture de tests comportementaux Java MIDI et assertions de régression Python conservées et exécutées dans le workflow.
4. Simplification de la livraison CI : un seul artefact de test, sans double publication du même binaire.

## Preuves automatisées

Sur le run `42256896568` associé au commit `084dad306accae879ecc72e94c8a531fbaeb3aeb` :
- vérification de la révision amont épinglée : réussie ;
- patcher transactionnel : réussi ;
- tests comportementaux Java MIDI : réussis ;
- suite de tests Python : réussie ;
- compilation Maven, vérification de l'enregistrement exclusif Push 1 et intégrité de l'archive : run global réussi ;
- publication de l'unique artefact `StrattV4-Push1-Test` : confirmée.

## Validation matérielle

Le propriétaire du projet a confirmé dans la conversation du 2026-11-06 que le test matériel a été effectué et concluant. Cette entrée consigne cette déclaration du propriétaire ; le détail du scénario, de la configuration Bitwig/Push et des contrôles effectués n'a pas été fourni dans ce jalon.

## Référence anti-régression

La comparaison GitHub entre `v4-foundation` et `evolution` au moment de ce jalon indique :
- `evolution` en avance de 7 commits ;
- 0 commit de retard ;
- base commune : `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.

Les différences doivent rester explicables et conformes à `docs/REGRESSION_POLICY.md`. La branche `v4-foundation` demeure intouchable. Toute évolution ultérieure doit se faire sur `evolution`, préserver les tests existants, exécuter la suite complète et refaire une recette matérielle lorsque le comportement matériel est concerné.

## Reprise à froid

1. Lire `README.md`, `docs/RESUME_PROTOCOL.md` et `docs/REGRESSION_POLICY.md`.
2. Vérifier le HEAD de `evolution` et comparer avec la baseline exacte ci-dessus.
3. Vérifier le run CI `42256896568` et le digest de l'artefact.
4. Reprendre le travail sur `evolution` uniquement ; ne jamais modifier `v4-foundation`.
5. Traiter ce point comme le dernier jalon de référence validé par CI et déclaré concluant sur matériel par le propriétaire, sans extrapoler au-delà des tests réellement effectués.


## Confirmation matérielle du dernier build précédent

Le propriétaire du projet confirme que le dernier commit et son build de test ont été utilisés sur le Push 1 et que tout fonctionne parfaitement. Cette confirmation est enregistrée comme validation matérielle positive de l'état précédent, sans extrapolation à des scénarios non décrits.

- Commit validé : `098443b6197539beced6536d223d89e1c44e3ed7`.
- Branche : `evolution`.
- Build : `Build StrattV4 Push 1` #15 — run `42260732361` — résultat `success`.
- Artefact : `StrattV4-Push1-Test`, ID `13523784316`, taille `12,262,879 bytes`.
- Digest : `sha256:c91b9fc200e6fbc02a2d8519599c7e934e9661dfb1457f224297dc72610c68b5`.
- La validation matérielle est une déclaration explicite du propriétaire du projet datée du 2026-11-06.
- La branche `v4-foundation` reste inchangée : `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.


## Réaffectation après échec matériel

Le geste SELECT + flèches du commit e08055f3d835cec71e99f930b6f0021951927b71 est rejeté matériellement. Nouveau geste : SHIFT+LEFT déplace le top-level track/group vers la gauche ; SHIFT+RIGHT vers la droite, dans Session, Track et Volume. SELECT+LEFT/RIGHT ne doit plus déplacer les pistes. Les pistes enfants restent protégées par l'API globale d'insertion. Validation matérielle en attente.


## Audit de restauration du déplacement des pistes — 2026-11-06

### Cause de la disparition

L'historique Git confirme que l'ancien patch personnalisé de navigation modifiait directement `PushCursorCommand.scrollLeft/scrollRight`. Il remplaçait la délégation native vers `activeMode.selectPreviousItemPage()` et `activeMode.selectNextItemPage()` par une logique de navigation de banque et des conditions de déplacement ajoutées dans le curseur. Ce détournement empêchait le mode de piste natif de recevoir le geste SHIFT + flèche et donc d'exécuter le déplacement DrivenByMoss.

Le commit `50ec514c68b3fd4bd08df69f3f9db15a1fa70225` retire cette surcharge de `scripts/apply_push1_navigation.py` et rétablit le chemin natif. Dans DrivenByMoss 19.2.2, `AbstractTrackMode` interprète SHIFT + gauche/droite et appelle respectivement `ICursorTrack.swapWithPrevious()` / `swapWithNext()`. L'adaptateur Bitwig déplace le Track via `TrackInsertionPoint.moveTracks()`.

### Affectation restaurée

- SHIFT + flèche gauche/droite dans les modes de piste/mixage qui héritent du comportement natif : déplacement de la piste sélectionnée d'une position.
- Sans SHIFT : navigation de page native inchangée.
- Le patch de navigation IN/OUT reste distinct.
- Aucun second gestionnaire de déplacement de piste n'est installé : le mécanisme amont est conservé.
- Les vérifications source confirment le routage PushCursorCommand → AbstractTrackMode → CursorTrackImpl. Elles ne remplacent pas une recette physique détaillée, en particulier pour les Group Tracks imbriqués et les limites.

### État des preuves au moment de l'audit

- Commit HEAD avant ce point de sauvegarde : `328089255626ec39ed2f400bea32db6f4a6f7bd5`.
- Comparaison avec `v4-foundation` : 38 commits en avance, 0 en retard ; baseline `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.
- Dernier build CI consultable : #21, run `42265014484`, succès sur `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`, artefact ID `13526433106`, SHA-256 `2d9f70c125e5a9d407ced37a66753f80c259a198de24bcb8f1a23703cb258dd4`.
- Aucun run CI n'était associé au HEAD `3280892` au moment de l'audit. Le build #21 ne doit donc pas être présenté comme une compilation de ce HEAD.
- Le propriétaire a confirmé le 2026-11-06 la validation matérielle positive du dernier test du dernier commit en date. Le scénario exact et le SHA du binaire testé n'ont pas été précisés dans son rapport ; cette confirmation est conservée comme déclaration utilisateur, sans étendre sa portée à des scénarios non décrits.

La prochaine compilation CI doit être associée au nouveau commit de ce point de sauvegarde. Une validation CI prouvera la compilation et les tests automatisés, pas à elle seule la validation de chaque combinaison matérielle.


## Révocation de la validation matérielle — déplacement des pistes

Le propriétaire a rejeté matériellement le geste SHIFT + flèches précédent : les déplacements étaient aléatoires. La conclusion antérieure selon laquelle la restauration du chemin natif suffisait est annulée. La fonctionnalité doit être considérée NON VALIDÉE.

Cause technique retenue pour correction : le backend amont choisit les voisins dans une banque globale aplatie de 400 pistes. Une piste adjacente dans cette banque peut être un enfant d'un Group Track développé, pas un frère. La nouvelle correction doit résoudre les voisins dans une banque \`createSiblingsTrackBank\`, au même niveau hiérarchique.

Le nouveau patch StrattV4 ne réécrit pas le geste physique ni le routage Push. Il corrige seulement la résolution du voisin. Le build #40 / run \`42280252862\` / artefact \`13534363252\` reste un build de l'ancienne logique ; ne pas l'utiliser comme preuve de la correction.
