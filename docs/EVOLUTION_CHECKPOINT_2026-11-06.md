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
