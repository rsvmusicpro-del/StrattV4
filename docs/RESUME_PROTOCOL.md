# StrattV4 — protocole de reprise à froid

## Identité et source de vérité

- Dépôt : `rsvmusicpro-del/StrattV4`
- Branche de travail unique : `evolution`
- Cible : Ableton Push 1 / Bitwig Studio 4.3.10 / API 17 / Java 17
- DrivenByMoss : 19.2.2, SHA amont `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`
- Référence historique anti-régression : commit `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`
- Guide opérationnel : `docs/PROJECT_OPERATIONS.md`
- Dépannage environnement : `docs/ENVIRONMENT_RECOVERY.md`
- Contrat anti-régression : `docs/REGRESSION_POLICY.md`

Les SHA de commits sont les références fiables ; les branches sont des pointeurs mobiles. Au contrôle du 2026-11-07, `v4-foundation` pointait sur `2b26d12`, pas sur `ec5871a`. Ne pas la traiter comme une copie de sauvegarde de la référence. Ne pas tenter de la corriger dans le cadre d'un travail limité à `evolution`.

## Règles impératives

1. Toutes les modifications du projet se font sur `evolution` exclusivement.
2. Ne pas force-push, réécrire l'historique ou supprimer des branches.
3. Ne jamais modifier ni pousser dans le sous-module DrivenByMoss.
4. Ne jamais supprimer, désactiver ou affaiblir un test pour obtenir une CI verte.
5. Appliquer les transformations via `scripts/apply_push1_palette_transactional.py` uniquement.
6. Ne pas exécuter plusieurs patchers en parallèle.
7. Préserver toutes les fonctions observables de la référence historique.
8. Ne jamais déclarer une validation matérielle sur la seule base d'un build CI.
9. Toute différence ou tout résultat ambigu doit être expliqué avant livraison.
10. Consigner les preuves et les limites de validation.

## Procédure de reprise

1. Lire ce document, `README.md`, `docs/PROJECT_OPERATIONS.md`, `docs/REGRESSION_POLICY.md` et `docs/ENVIRONMENT_RECOVERY.md`.
2. Vérifier le HEAD distant de `evolution` et confirmer la branche de travail.
3. Comparer le HEAD à `ec5871a` et examiner les commits/diffs.
4. Lire les derniers runs CI, leurs étapes, artefacts et éventuels échecs.
5. Vérifier le SHA du sous-module.
6. Si le clone local est impossible (DNS/réseau), ne pas bricoler un arbre partiel : utiliser le workflow CI distant selon `ENVIRONMENT_RECOVERY.md`.
7. Reprendre la première tâche non terminée dans le checkpoint le plus récent.
8. Avant toute écriture, confirmer que le parent du commit est toujours le HEAD observé ; refuser une mise à jour si la branche a avancé.

## Pipeline attendu

Le workflow `.github/workflows/main.yml` doit vérifier le SHA amont, appliquer les transformations de manière transactionnelle, exécuter les tests Java et Python, compiler sous Java 17, vérifier l'enregistrement exclusif Push 1, contrôler l'intégrité de l'archive et publier un artefact unique `StrattV4-Push1-Test`.

## Journal de preuve obligatoire

```text
Commit / branche:
SHA DrivenByMoss:
Run CI:
Tests Java:
Tests Python:
Maven:
Service Push 1 exclusif:
Intégrité archive:
Artefact / ID / SHA-256:
Test Bitwig 4.3.10:
Test Push 1 physique (scénario/date/résultat):
Risques et tests non exécutés:
```

## Checkpoint distant constaté au 2026-11-07

- HEAD `evolution` : `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`.
- Build CI #64 : run `42299038808`, succès.
- Artefact `StrattV4-Push1-Test`, ID `13542369228`, SHA-256 `ce0b36f96e9881a707e19ca54fa49d348f19ebd2084f968bd6831ec63f1877d3`.
- Ce build préexiste à la réorganisation documentaire ; ne pas le présenter comme produit par celle-ci.
- Le succès CI confirme uniquement les étapes automatisées du workflow. Toute recette matérielle de ce commit doit être consignée séparément.
