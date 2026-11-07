# StrattV4 — récupération d'environnement et continuité de travail

## Objectif

Éviter qu'une panne DNS, une machine sans JDK, un sous-module inaccessible ou un cache Maven défaillant bloque toute progression ou conduise à une livraison non vérifiée.

## 1. Vérifications initiales

Depuis la racine du dépôt :

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
git submodule status --recursive
java -version
javac -version
python3 --version
mvn -version
```

Conditions attendues : branche `evolution`, JDK/Javac 17, Python 3, Maven disponible, sous-module DrivenByMoss à la révision épinglée dans `.github/workflows/main.yml`.

Ne jamais corriger un environnement en changeant silencieusement une version cible ou le SHA amont.

## 2. Clone / DNS indisponible

1. Vérifier le DNS et l'accès HTTPS à GitHub depuis la machine.
2. Ne pas interpréter un échec réseau comme un défaut du code.
3. Ne pas construire depuis un sous-module vide, un clone partiel ou un ancien dossier non identifié.
4. Utiliser GitHub Actions comme voie de build distante : onglet Actions → **Build StrattV4 Push 1** → **Run workflow** → branche `evolution`.
5. Attendre la fin du run ; vérifier chaque étape, pas seulement le statut global.
6. Télécharger `StrattV4-Push1-Test` uniquement depuis le run du SHA visé.
7. Noter l'identifiant du run, le commit et le digest de l'artefact.

La CI distante permet de produire un artefact malgré une machine locale indisponible. Elle ne permet pas de déclarer que des tests locaux ou matériels ont été exécutés.

## 3. Clone propre après rétablissement du réseau

```bash
git clone --branch evolution --recurse-submodules https://github.com/rsvmusicpro-del/StrattV4.git
cd StrattV4
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

Comparer le SHA du sous-module à la valeur attendue dans le workflow. Si différent, arrêter et corriger le checkout ; ne pas créer de commit qui met à jour le sous-module.

## 4. Environnement Java / Maven

- Utiliser JDK 17 (pas uniquement un JRE).
- Confirmer que `JAVA_HOME` désigne le JDK 17 et que `javac -version` retourne 17.
- En cas d'échec Maven, conserver le log intégral et identifier si l'échec vient du réseau, du cache, d'une dépendance ou du code.
- Ne pas supprimer le cache global en premier réflexe ; préférer un build isolé ou la relance CI.
- Ne pas remplacer une dépendance ni modifier l'API Bitwig pour faire disparaître une erreur d'environnement.

## 5. Patcher transactionnel

Le point d'entrée unique est :

```bash
python3 -B scripts/apply_push1_palette_transactional.py
```

Ne pas lancer les patchers individuels en parallèle. En cas d'échec, ne pas relancer aveuglément sur un arbre partiellement transformé : conserver le log, repartir d'un checkout propre et vérifier que la transaction a restauré ou isolé les fichiers modifiés.

## 6. Dépannage CI

- **Checkout/submodule** : vérifier accès et SHA amont.
- **Checksum amont** : ne pas mettre à jour le checksum attendu sans vérifier le fichier source et justifier la modification.
- **Java tests** : identifier la classe et l'assertion en échec.
- **Python tests** : identifier le test précis et conserver la trace.
- **Maven** : vérifier version Java, résolution de dépendances et compilation.
- **Service Push 1** : l'artefact doit enregistrer uniquement `Push1ControllerExtensionDefinition`.
- **ZIP** : `unzip -t` doit réussir avant publication.

Une relance peut diagnostiquer une panne transitoire, mais ne remplace pas la correction de sa cause.

## 7. Informations à transmettre lors d'une reprise

Toujours joindre : SHA du commit, branche, run CI, étape en échec, log pertinent, SHA du sous-module et état du checkout. Ne jamais transmettre uniquement « ça bloque » ou « CI rouge ».
