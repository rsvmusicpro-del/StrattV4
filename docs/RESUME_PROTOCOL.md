# StrattV4 — protocole de reprise à froid

## Identité du projet

- Projet : StrattV4
- Extension produite : `StrattV4.bwextension`
- Dépôt : `rsvmusicpro-del/StrattV4`
- Branche de travail initiale : `v4-foundation`
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

## Procédure de reprise

Au début de chaque session :

1. Lire intégralement ce document et le README.
2. Lire l'état GitHub du dépôt et relever la branche active et son SHA.
3. Vérifier la présence du sous-module et sa révision exacte.
4. Lire les derniers commits, PR, workflows, résultats de tests et artefacts.
5. Examiner les modifications non consignées avant d'agir.
6. Reprendre la première tâche non terminée du journal de travail.
7. En cas d'incertitude sur un état, vérifier GitHub ; ne jamais supposer.

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

### Initialisation

- Commit : `fac05b2ee0f535030b0677255b42adff48429e29`
- Branche : `v4-foundation`
- Arbre initial : scripts, tests, sous-module amont, workflow et README.
- Prochaine action : obtenir un build CI sur ce dépôt, corriger les erreurs éventuelles sans affaiblir les tests, puis exécuter l'audit complet.
