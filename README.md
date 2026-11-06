# StrattV4 — Ableton Push 1 pour Bitwig Studio

StrattV4 est une extension Bitwig autonome dédiée à l'Ableton Push 1, ciblant Bitwig Studio 4.3.10 et Java 17.

## Fonctions

- Palette Push 1 de 64 couleurs et mapping LED dédié.
- Navigation contextuelle Browser, Device, Rack, Session et séquenceur.
- Vues Play, SMART et CHORDS avec gestion du cycle de vie MIDI.
- Gestion des encodeurs, des gestes modificateurs et du toucher.
- Affichage français, gestion des noms longs et VU.
- Création de scènes et protections contre les tâches différées obsolètes.

## Construction

Le dépôt épingle la source DrivenByMoss 19.2.2 comme sous-module à la révision déclarée dans le workflow. Les personnalisations sont appliquées transactionnellement à une copie de travail. La CI exécute les tests Python et Java, compile avec Maven, vérifie que seul le contrôleur Push 1 est enregistré, puis produit `StrattV4.bwextension`.

Un build réussi valide la compilation et le packaging. Il ne remplace pas une recette sur Push 1 physique avec Bitwig Studio 4.3.10.

## Prérequis

- Git avec prise en charge des sous-modules
- Java 17
- Python 3
- Maven (fourni via le wrapper de build upstream ou installé dans l'environnement)

## Build local

```bash
git clone --recurse-submodules https://github.com/rsvmusicpro-del/StrattV4.git
cd StrattV4
python3 -B scripts/apply_push1_palette_transactional.py
cd vendor/DrivenByMoss
mvn -B package
```

Le paquet de sortie est construit depuis le JAR compilé du contrôleur Push 1.

## Licence et notices

La base logicielle DrivenByMoss est distribuée sous GNU LGPL version 3. Les fichiers de licence et notices amont doivent être conservés avec les sources et tout artefact redistribué. Vérifier également les licences des composants et ressources intégrés avant distribution.
