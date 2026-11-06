# StrattV4 — contrat de non-régression et référence matérielle

## Référence de référence immuable (baseline)

Le snapshot source validé matériellement par le propriétaire est la référence fonctionnelle à préserver. La validation matérielle est une déclaration utilisateur ; elle ne remplace pas les preuves CI associées au SHA exact.

- Branche de référence : `v4-foundation`
- Commit exact : `5978d89e4deeacb93f415111511d2fdf98763041`
- Build : `Build StrattV4 Push 1` #3
- Workflow run : `42248099882`
- Résultat CI : `success`
- Validation matérielle : déclarée par le propriétaire du projet le 2026-11-06 (Push 1 fonctionnel)
- Artefact : `StrattV4-Push1-Test`
- Artifact ID : `13519277768`
- Taille : `12,265,279 bytes`
- Digest fourni par GitHub : `sha256:1a93fc5541b98b93ad98a9aebb51151452cb20b6c8c01f5a94dad892eb472dab`
- Expiration de l'artefact CI : 2026-11-13. Le digest et le SHA du commit constituent la référence, mais l'artefact doit être téléchargé et archivé hors GitHub avant son expiration si une copie binaire durable est nécessaire.

Cette référence est un point de comparaison, jamais une branche de développement. Ne pas y pousser, ne pas la rebaser, ne pas la fusionner dans une branche qui la modifierait, ne pas supprimer la branche.

## Branche de travail unique

- Branche d'évolution : `evolution`
- Point de départ exact : `5978d89e4deeacb93f415111511d2fdf98763041`
- Toutes les nouvelles modifications, améliorations, corrections et PR doivent partir de `evolution` et y être intégrées après validation.
- Ne plus utiliser `v4-foundation` comme branche de travail.
- Ne pas développer sur `main`.
- La branche `evolution` est la seule branche de travail autorisée par la politique du projet.

## Invariants fonctionnels

Aucune fonction présente dans le build de référence ne doit être supprimée, dégradée, rendue inaccessible ou altérée involontairement.

Cela comprend notamment :
- palette 64 couleurs et mapping LED ;
- vues Play, SMART et CHORDS ;
- séquenceurs polyphonique et de notes ;
- navigation Browser, Device, Rack, Session et séquenceur ;
- interactions pads, notes, encodeurs et commandes modificateurs ;
- gestion des gestes Select/New Scene ;
- cycle de vie MIDI Note On / Note Off ;
- gestion du toucher et des propriétaires de toucher ;
- protections contre tâches différées obsolètes ;
- affichage français, noms longs, écrans et VU ;
- enregistrement exclusif du contrôleur Push 1 ;
- compatibilité cible Bitwig Studio 4.3.10 / Java 17.

Cette liste est un résumé lisible, pas une limitation du périmètre : tout comportement observable du build de référence est protégé, même s'il n'est pas listé ici.

## Règles pour chaque évolution

1. Commencer par lire ce contrat, le protocole de reprise et le commit de référence.
2. Comparer la branche candidate à `5978d89` avant et après le changement.
3. Ne jamais accepter une suppression de fichier, de test, de commande, de mapping ou de comportement sans analyse d'impact explicite.
4. Tout changement fonctionnel doit ajouter ou mettre à jour des tests qui prouvent le nouveau comportement ET préservent les comportements existants concernés.
5. Conserver l'intégralité des tests de référence ; les tests supplémentaires s'ajoutent, ils ne remplacent pas les anciens.
6. Exécuter la suite complète Java et Python, puis Maven, les contrôles d'enregistrement Push 1 et d'intégrité de l'archive.
7. Comparer les logs, résultats et artefacts avec la baseline.
8. Pour les fonctions dépendantes du matériel, exiger une recette Push 1 physique. Un build vert ne prouve pas la non-régression matérielle.
9. En cas de test manquant, résultat ambigu ou différence inexpliquée : bloquer la livraison et signaler le risque.
10. Une régression détectée impose le retour au dernier état fonctionnel, sans écraser la baseline.

## Politique de protection Git

La branche `v4-foundation` doit être configurée dans GitHub avec une règle de protection ou ruleset :
- interdiction de suppression ;
- interdiction de force-push ;
- changements uniquement par PR ;
- checks requis avant fusion si les permissions du dépôt le permettent.

L'accès de l'intégration GitHub utilisé pendant cette session ne permet pas d'écrire les règles d'administration de branches. À la vérification, `v4-foundation` était signalée non protégée et aucun ruleset n'était présent. La protection effective doit donc être activée par un administrateur dans GitHub Settings → Branches / Rulesets. Ne pas prétendre que cette protection est déjà active.

La protection ne peut jamais garantir l'impossibilité absolue pour un propriétaire/administrateur de modifier les paramètres. Pour une conservation forte, télécharger également le commit et l'artefact de référence dans un stockage indépendant.

## Politique CI

Les workflows de build de développement doivent se déclencher sur `evolution` et sur les PR vers `evolution`. La référence `v4-foundation` ne doit pas déclencher de workflow nécessitant des commits ou des modifications sur cette branche.

Les checks obligatoires pour toute évolution sont : tests Java, tests Python, compilation Maven, enregistrement Push 1 exclusif, intégrité ZIP, artefact et comparaison de la baseline.

## État de protection au 2026-11-06

- [x] Commit de référence enregistré.
- [x] Build #3 et run CI enregistrés.
- [x] Digest de l'artefact enregistré.
- [x] Branche `evolution` créée depuis le SHA exact de référence.
- [ ] Règle GitHub empêchant suppression, force-push et modifications directes de `v4-foundation` : activation administrateur requise.
- [ ] Définir `evolution` comme branche par défaut du dépôt : opération d'administration non disponible via l'intégration actuelle.
- [ ] Archiver le binaire de référence hors de la rétention temporaire GitHub.


## État du snapshot de référence — 2026-11-06

- Baseline courante : `5978d89e4deeacb93f415111511d2fdf98763041` (`StrattV4 backup`).
- Arbre source : `3222a047e110c37a63161169ebf0979ecdb02e6a`, identique au HEAD antérieur `b08d03ec0e39187e5f200f14f051ce3eb0e82550`.
- Les branches `evolution` et `v4-foundation` ont été positionnées sur ce snapshot ; `ec5871a` reste conservé comme parent historique.
- Le dernier build CI vérifié est run `42265014484` (#21), succès sur `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`; ce SHA n'est pas celui du snapshot.
- Aucune validation CI du snapshot n'est disponible dans l'historique consulté. Un nouveau run doit être associé au SHA exact avant livraison.
- Les métadonnées GitHub ont signalé `protected: false` lors de l'audit ; la lecture détaillée des règles a été refusée à l'intégration. Ne pas prétendre que la protection est active.
