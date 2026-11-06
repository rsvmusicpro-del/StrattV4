# StrattV4 — jalon de durcissement du build et du moteur de patchs

Date : 2026-11-06  
Branche : `evolution`  
Baseline de comparaison : `v4-foundation` (ne pas modifier)

## Résultat

- Commit final validé par CI : `082e830902b92dd0881d45dc1d8f93b4c37f0a9d`.
- Commit de départ de cette étape : `ec5884063c09f551eb87b2ac6b9115e04dbbf951`.
- Workflow : [Build StrattV4 Push 1 #54](https://github.com/rsvmusicpro-del/StrattV4/actions/runs/42295463035).
- Conclusion : `success`.
- Artefact : `StrattV4-Push1-Test`, ID `13541916327`, taille 12 264 053 octets.
- SHA-256 : `d620a77672f1d3351efbae94eb5f6f4f97d4ae96e7eb534dad62bdc4b87ad08d`.
- Expiration de l'artefact : 2026-11-13.

## Modifications

1. `scripts/patch_utils.py` valide explicitement les types, refuse les ancres vides et les libellés invalides, et conserve la règle de sécurité « exactement une occurrence ».
2. Les remplacements sans changement sont autorisés intentionnellement : certains patchs s'en servent comme assertions d'unicité d'un point d'ancrage amont. La première exécution a mis en évidence ce cas dans `apply_push1_startup_message.py`; la règle a été corrigée et couverte par un test dédié.
3. `tests/test_patch_utils.py` couvre les ancres absentes, ambiguës ou vides, les assertions sans modification, les libellés invalides et l'absence de mutation en cas d'échec.
4. Le workflow vérifie maintenant la syntaxe de l'ensemble des fichiers Python sous `scripts/` et `tests/` avant les tests et la compilation.
5. Le README décrit les contrôles automatisés et les commandes locales de base.

## Résultats des contrôles du run #54

| Étape | Résultat |
|---|---|
| Checkout et vérification de la révision DrivenByMoss épinglée | Réussi |
| Réparation contrôlée du checksum POM connu dans l'espace CI | Réussi |
| Installation Java 17 et enregistrement exclusif Push 1 | Réussi |
| Application transactionnelle des personnalisations | Réussi |
| Compilation syntaxique Python | Réussi |
| Tests comportementaux Java MIDI | Réussi |
| Suite de régression Python | Réussi |
| Compilation Maven, contrôle du service Push 1 et intégrité ZIP | Réussi |
| Publication de l'artefact unique | Réussi |

## Régression rencontrée et corrigée pendant cette étape

La première tentative, run #53 (`42295385418`), a échoué volontairement à la nouvelle règle qui interdisait les remplacements sans effet. L'analyse des logs a montré qu'un script utilise cette opération comme assertion d'unicité, sans chercher à changer le code. Le comportement valide a été rétabli, documenté et testé. Le run #54, sur le commit final, est entièrement vert.

## Limites et suite du travail

- Cette étape ne constitue pas la réécriture complète de l'architecture des personnalisations : les scripts existants et leur ordre sont conservés pour éviter toute régression fonctionnelle.
- La prochaine étape technique est de séparer le registre des patchs, leur orchestration et leurs validations, puis d'augmenter les tests comportementaux autour des gestes et des états Bitwig.
- Le build CI ne vérifie pas le comportement physique du Push 1. Une recette matérielle sur Bitwig Studio 4.3.10 reste requise avant de déclarer cette nouvelle version validée sur matériel.
- Aucun changement n'a été apporté à `v4-foundation` ni au sous-module DrivenByMoss épinglé.
