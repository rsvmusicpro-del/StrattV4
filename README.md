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

Le dépôt épingle la source DrivenByMoss 19.2.2 comme sous-module à la révision déclarée dans le workflow. Les personnalisations sont appliquées transactionnellement à une copie de travail. La CI vérifie aussi la syntaxe de tous les scripts et tests Python, exécute les tests Java comportementaux et la suite Python, compile avec Maven, vérifie que seul le contrôleur Push 1 est enregistré, puis produit `StrattV4.bwextension`.

Le dernier jalon CI réussi est documenté dans [docs/EVOLUTION_PHASE_1_2026-11-06.md](docs/EVOLUTION_PHASE_1_2026-11-06.md). Il valide le build automatisé du commit concerné, pas une nouvelle recette matérielle. Un build réussi ne remplace jamais un essai sur Push 1 physique avec Bitwig Studio 4.3.10.

## Prérequis

- Git avec prise en charge des sous-modules
- Java 17
- Python 3
- Maven (fourni via le wrapper de build upstream ou installé dans l'environnement)

## Build local

```bash
git clone --recurse-submodules https://github.com/rsvmusicpro-del/StrattV4.git
cd StrattV4
python3 -B -m compileall -q scripts tests
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 -B scripts/apply_push1_palette_transactional.py
cd vendor/DrivenByMoss
mvn -B package
```

Le workflow GitHub Actions exécute en plus les tests Java comportementaux, vérifie l'enregistrement exclusif Push 1 et l'intégrité de l'archive produite.

## Licence et notices

La base logicielle DrivenByMoss est distribuée sous GNU LGPL version 3. Les fichiers de licence et notices amont doivent être conservés avec les sources et tout artefact redistribué. Vérifier également les licences des composants et ressources intégrés avant distribution.
