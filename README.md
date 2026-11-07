# StrattV4 — Ableton Push 1 pour Bitwig Studio

StrattV4 est une extension Bitwig dédiée à l'Ableton Push 1. Cible de référence : Bitwig Studio 4.3.10, API 17, Java 17 et DrivenByMoss 19.2.2 (révision amont épinglée dans le workflow).

## Démarrage rapide

1. Lire [le guide d'exploitation](docs/PROJECT_OPERATIONS.md).
2. Lire [le protocole de reprise](docs/RESUME_PROTOCOL.md) et [la politique anti-régression](docs/REGRESSION_POLICY.md).
3. Travailler exclusivement sur la branche `evolution`.
4. Lancer le workflow GitHub Actions **Build StrattV4 Push 1** sur `evolution` (ou ouvrir une PR vers `evolution`).
5. Télécharger l'artefact `StrattV4-Push1-Test` uniquement si le run est vert, puis effectuer la recette matérielle requise.

## Structure du dépôt

| Chemin | Rôle |
|---|---|
| `.github/workflows/main.yml` | Pipeline CI reproductible : sous-module, patchers, tests, Maven, packaging |
| `scripts/apply_push1_*.py` | Transformations ciblées du code DrivenByMoss |
| `scripts/apply_push1_palette_transactional.py` | Point d'entrée transactionnel des transformations |
| `tests/` | Tests Python de non-régression et tests Java comportementaux |
| `docs/` | Contrats, procédures, checkpoints et consignes d'exploitation |
| `vendor/DrivenByMoss` | Sous-module amont, révision verrouillée ; ne pas modifier ni pousser dedans |

## Construction

### Construction recommandée : GitHub Actions

Le workflow est la référence de construction, notamment lorsque le poste local ne peut pas résoudre GitHub, télécharger les dépendances Maven ou initialiser les sous-modules. Depuis l'onglet **Actions**, lancer **Build StrattV4 Push 1** sur `evolution`. Le workflow vérifie la révision amont, applique les patchers de manière transactionnelle, exécute les tests Java et Python, compile, vérifie l'enregistrement exclusif Push 1 et l'intégrité de l'archive, puis publie un seul artefact.

### Construction locale

Prérequis : Git avec sous-modules, Python 3, JDK 17, Maven et accès réseau aux dépôts GitHub/Maven.

```bash
git clone --branch evolution --recurse-submodules https://github.com/rsvmusicpro-del/StrattV4.git
cd StrattV4
git submodule status --recursive
python3 -B scripts/apply_push1_palette_transactional.py
cd vendor/DrivenByMoss
mvn -B package
```

Ne pas lancer plusieurs patchers concurrents sur le même arbre. Repartir d'un checkout propre si une transformation échoue ou si son état est incertain. Les procédures détaillées sont dans [PROJECT_OPERATIONS.md](docs/PROJECT_OPERATIONS.md).

## Niveaux de preuve

- **Tests** : vérifient les comportements couverts par les tests Java/Python.
- **Build CI** : prouve que le commit a passé le pipeline et que l'artefact a été empaqueté.
- **Test Bitwig** : vérifie le chargement et le fonctionnement dans la version cible.
- **Test matériel** : vérifie réellement le Push 1 physique. Un build vert ne vaut jamais validation matérielle.

## Références et sécurité des changements

- Politique anti-régression : [REGRESSION_POLICY.md](docs/REGRESSION_POLICY.md)
- Procédure de reprise : [RESUME_PROTOCOL.md](docs/RESUME_PROTOCOL.md)
- Organisation et dépannage : [PROJECT_OPERATIONS.md](docs/PROJECT_OPERATIONS.md)
- Environnement et récupération : [ENVIRONMENT_RECOVERY.md](docs/ENVIRONMENT_RECOVERY.md)

Ne jamais force-push, réécrire l'historique, supprimer un test pour obtenir une CI verte, ni modifier la révision du sous-module sans campagne de validation dédiée.

## Licence

Conserver les licences et notices amont DrivenByMoss et vérifier les licences de tous les composants avant redistribution.
