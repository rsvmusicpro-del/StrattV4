# StrattV4 — contrat de non-régression et référence matérielle

## Référence historique

- Commit de référence : `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.
- Build de référence consigné : Build #3, run `42248099882`, succès CI.
- Artefact consigné : `StrattV4-Push1-Test`, ID `13519277768`, digest `sha256:1a93fc5541b98b93ad98a9aebb51151452cb20b6c8c01f5a94dad892eb472dab`.
- Cette référence est un commit précis ; elle doit être comparée par SHA, jamais par supposition sur le nom d'une branche.

**Écart de pointeur à connaître :** au contrôle du 2026-11-07, les branches `evolution` et `v4-foundation` pointaient toutes deux sur `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`. La branche `v4-foundation` ne protégeait donc plus le commit `ec5871a). Le commit `ec5871a` reste le point de comparaison historique accessible par SHA, mais ne pas prétendre que le pointeur de branche est restauré ou protégé. La restauration du pointeur et la protection de branche sont des opérations GitHub administrateur séparées.

## Branche de travail

- Seule branche de travail autorisée : `evolution`.
- Ne pas développer sur `main`, `v4-foundation` ou une branche archive.
- Ne pas force-push, réécrire l'historique ou supprimer une branche.
- Les modifications fonctionnelles restent additives et doivent être testées avant livraison.

## Invariants à préserver

Aucune fonction observable de la référence ne doit être supprimée, dégradée, rendue inaccessible ou altérée involontairement :
- palette 64 couleurs et mapping LED ;
- vues Play, SMART et CHORDS ;
- séquenceurs polyphonique et de notes ;
- navigation Browser, Device, Rack, Session et séquenceur ;
- interactions pads, notes, encodeurs et commandes modificateurs ;
- gestes Select/New Scene et réordonnancement ;
- cycle de vie MIDI Note On / Note Off ;
- gestion du toucher et des propriétaires de toucher ;
- protections contre tâches différées obsolètes ;
- affichage français, noms longs, écrans et VU ;
- enregistrement exclusif du contrôleur Push 1 ;
- compatibilité Bitwig Studio 4.3.10 / API 17 / Java 17.

Cette liste est un résumé, pas une limitation : tout comportement observable de la référence est protégé.

## Conditions obligatoires pour chaque évolution

1. Lire `docs/PROJECT_OPERATIONS.md` et `docs/RESUME_PROTOCOL.md`.
2. Comparer le candidat au commit `ec5871a` et expliquer chaque différence.
3. Vérifier que le sous-module est au SHA épinglé.
4. Ne supprimer aucun fichier, test, commande ou mapping sans analyse d'impact documentée.
5. Ajouter/mettre à jour des tests pour le comportement modifié et ses invariants.
6. Exécuter l'ensemble des tests Java et Python, puis Maven, contrôle du service Push 1 et intégrité de l'archive.
7. Archiver commit, run CI, étapes, ID/digest de l'artefact.
8. Exiger une recette Bitwig/Push 1 physique pour toute évolution dont le comportement matériel peut être affecté.
9. Si un test manque, échoue ou est ambigu, bloquer la livraison et documenter précisément le blocage.
10. En cas de régression, revenir au dernier état connu comme bon sans modifier le commit historique de référence.

## Niveaux de validation

| Niveau | Ce que cela prouve | Ce que cela ne prouve pas |
|---|---|---|
| Analyse statique | Cohérence de structure / règles détectables | Exécution correcte |
| Tests Java/Python | Comportements explicitement couverts | Intégration complète Bitwig |
| Maven + archive | Compilation et packaging | Fonctionnement matériel |
| Test dans Bitwig 4.3.10 | Chargement et intégration logicielle | Tous les gestes matériels |
| Push 1 physique | Scénarios réellement exécutés sur l'appareil | Scénarios non testés |

Ne jamais fusionner ces niveaux dans une mention vague « validé ».

## Protection GitHub

Les branches étaient signalées non protégées au contrôle. L'intégration utilisée ici ne dispose pas de l'administration des règles de branche. Un administrateur doit configurer dans GitHub Settings → Branches / Rulesets :
- interdiction de suppression et de force-push ;
- PR obligatoire pour intégrer les changements ;
- checks CI requis avant fusion ;
- protection de la référence historique après restauration explicite de son pointeur.

Ne pas annoncer ces protections comme actives tant qu'elles ne sont pas vérifiées via GitHub. Définir aussi `evolution` comme branche par défaut si le propriétaire le souhaite ; cela relève des paramètres du dépôt.

## État de protection observé

- [x] SHA historique `ec5871a` identifié.
- [x] Workflow CI sur `evolution`.
- [ ] Pointeur `v4-foundation` restauré vers `ec5871a` : non effectué, hors périmètre d'écriture limité à `evolution`.
- [ ] Règle GitHub anti-suppression / anti-force-push : administration requise.
- [ ] Checks obligatoires imposés par ruleset : administration requise.
- [ ] Copie binaire de référence conservée hors rétention temporaire GitHub.
