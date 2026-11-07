# StrattV4 — organisation et exploitation du projet

## 1. Source de vérité

- Dépôt : `rsvmusicpro-del/StrattV4`
- Branche de travail : `evolution` uniquement.
- Cible : Bitwig Studio 4.3.10 / API 17 / Java 17.
- Amont : DrivenByMoss 19.2.2, sous-module verrouillé au SHA `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`.
- Point de comparaison historique : commit `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`.
- HEAD constaté à la rédaction : `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`.

Le SHA d'un commit est la référence exacte ; un nom de branche est un pointeur mobile. Ne jamais déduire l'intégrité d'une baseline du seul nom `v4-foundation`. Au contrôle du 2026-11-07, `v4-foundation` pointait sur le même commit que `evolution` (`2b26d12`) et non sur `ec5871a`. Ce dépôt ne doit donc pas présenter cette branche comme une sauvegarde intacte de `ec5871a`. Le commit historique `ec5871a` demeure le point de comparaison par SHA. La restauration d'un pointeur ou la protection GitHub exige une action d'administration séparée ; ne pas la simuler par une modification de documentation.

## 2. Architecture du dépôt

| Répertoire / fichier | Responsabilité | Règle |
|---|---|---|
| `.github/workflows/main.yml` | Orchestration CI et livraison d'un artefact | Toute évolution doit passer par ce pipeline |
| `scripts/apply_push1_*.py` | Patchers unitaires, ciblés sur le code amont | Idempotence et préconditions explicites ; pas de patch silencieux |
| `scripts/apply_push1_palette_transactional.py` | Orchestrateur transactionnel | Point d'entrée unique pour appliquer l'ensemble |
| `tests/test_*.py` | Tests de structure, patchers et régressions | Ajouter ; ne jamais supprimer pour faire passer CI |
| `tests/java/*Test.java` | Tests comportementaux Java isolés | Garder les tests indépendants et déterministes |
| `vendor/DrivenByMoss` | Dépendance amont épinglée | Lecture seule ; ne pas committer dans le sous-module |
| `docs/` | Contrats, procédure, preuves et décisions | Mettre à jour à chaque changement de procédure |

Ne pas déplacer les scripts ou les tests en masse : le workflow et les tests référencent leurs chemins. Toute réorganisation physique ultérieure doit être atomique, avec mise à jour des références et tests dédiés.

## 3. Chemin de livraison unique

1. Vérifier le dépôt et le HEAD de `evolution`.
2. Comparer le commit candidat au point historique `ec5871a` ; expliquer chaque différence.
3. Vérifier le sous-module et son SHA exact.
4. Appliquer les patchers via le seul orchestrateur transactionnel.
5. Exécuter tous les tests Java et Python.
6. Construire avec Maven sur Java 17.
7. Vérifier le service d'enregistrement : Push 1 uniquement.
8. Vérifier l'intégrité de `StrattV4.bwextension`.
9. Publier un seul artefact CI `StrattV4-Push1-Test`.
10. Effectuer les tests Bitwig puis la recette Push 1 physique lorsque le comportement matériel est concerné.
11. Consigner commit, run, tests, artefact/digest et résultat matériel dans le journal/checkpoint.

Aucune étape ne peut être considérée réussie sur la base d'une étape ultérieure. En particulier, un JAR compilé ne prouve pas que les patchers ou les tests sont corrects ; une CI verte ne prouve pas le comportement sur matériel.

## 4. Règles anti-blocage

- **Un seul point d'entrée de build** : le workflow GitHub Actions est la voie de secours officielle si le poste local est indisponible.
- **Versions explicites** : Java 17, API 17, SHA du sous-module contrôlé par CI.
- **Échecs précoces** : une précondition absente, un SHA différent ou un checksum inattendu doit arrêter le pipeline avec un message explicite.
- **Pas de modifications partielles** : patcher transactionnel, arbre propre après échec, pas de patchers concurrents.
- **Tests non destructifs** : aucune suppression ou désactivation de test pour rendre la CI verte.
- **Un artefact identifié** : nom stable, digest relevé, commit source consigné.
- **Reprise documentée** : chaque session commence par le protocole de reprise, jamais par une hypothèse sur l'état local.
- **État distant vérifié** : si le clone local échoue, utiliser GitHub Actions et les fichiers distants en lecture ; ne pas inventer un résultat local.
- **Aucune validation extrapolée** : distinguer statique, unitaire, compilation, intégration Bitwig et matériel.

## 5. Procédure d'échec

| Symptôme | Action sûre |
|---|---|
| DNS / clone GitHub indisponible | Ne pas modifier un checkout incomplet. Lancer le workflow CI sur `evolution` ; réessayer le clone quand le réseau revient. Voir `ENVIRONMENT_RECOVERY.md`. |
| Sous-module absent ou mauvais SHA | Arrêter ; réinitialiser récursivement depuis le SHA épinglé. Ne jamais avancer le sous-module automatiquement. |
| Patcher échoué | Abandonner l'arbre de travail temporaire et repartir d'un checkout propre ; conserver le log et l'étape fautive. |
| Test rouge | Identifier la première assertion fautive ; ne pas désactiver le test ni poursuivre vers une livraison. |
| Maven rouge | Conserver le log complet, vérifier Java 17 et le cache/dépôt Maven ; ne pas modifier la version d'API pour contourner l'erreur. |
| Archive invalide / mauvais service | Bloquer la publication ; inspecter le JAR et la liste de services. |
| CI verte, matériel non testé | Statut : build vérifié, matériel non vérifié. Ne pas déclarer la livraison validée. |

## 6. Découpage des responsabilités techniques

- **MIDI** : émission/réception, Note On/Off, suivi des notes actives, nettoyage à la désactivation/arrêt, ownership tactile et transitions de vues.
- **Affichage** : formatage des libellés, noms longs, français, VU, écrans et correspondance LED.
- **Synchronisation** : cohérence Bitwig ↔ modèle interne ↔ Push ; invalidation des tâches différées et changements rapides de contexte.
- **Navigation/gestes** : commandes de page, sélection, création de scène et réordonnancement de chaîne.
- **Build/livraison** : patchers, tests, compilation, enregistrement Push 1, archive et provenance.

Tout changement doit indiquer les domaines touchés et les invariants à retester.

## 7. Journal de livraison

Pour chaque commit candidat, consigner au minimum :

```text
Commit:
Branche:
SHA DrivenByMoss:
Run CI:
Tests Java:
Tests Python:
Maven:
Service Push 1 exclusif:
Intégrité archive:
Artefact / ID / SHA-256:
Test Bitwig 4.3.10:
Push 1 physique (scénario, résultat, date):
Risques / limites connus:
```

Une case non exécutée est marquée « non exécutée », jamais « OK ».
