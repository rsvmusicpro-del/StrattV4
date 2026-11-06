# StrattV4 — Ableton Push 1 pour Bitwig Studio

StrattV4 est une extension Bitwig autonome dédiée à l'Ableton Push 1, ciblant Bitwig Studio 4.3.10 et Java 17.

## Fonctions

- Palette Push 1 de 64 couleurs et mapping LED dédié.
- Navigation contextuelle Browser, Device, Rack, Session et séquenceur.
- Vues Play, SMART et CHORDS avec gestion du cycle de vie MIDI.
- Gestion des encodeurs, des gestes modificateurs et du toucher.
- Affichage français, gestion des noms longs et VU.
- Création de scènes et protections contre les tâches différées obsolètes.

## Construction et architecture

Le dépôt épingle la source DrivenByMoss 19.2.2 à la révision `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`. Les 22 personnalisations sont décrites dans `scripts/patch_manifest.py` avec leur ordre, leur objectif et les sources Java requises. Le moteur `scripts/apply_push1_palette_transactional.py` vérifie l'amont, applique les patchs sur une copie temporaire, valide les sorties puis installe la copie avec restauration de l'original si le remplacement final échoue.

La CI vérifie la baseline `v4-foundation` à son SHA exact, refuse les suppressions de fichiers par rapport à cette baseline, valide la syntaxe Python, exécute les tests Java et Python, compile Maven, vérifie l'enregistrement exclusif Push 1 et l'intégrité de l'archive.

Jalons techniques :
- [Phase 1 — durcissement du moteur de patchs](docs/EVOLUTION_PHASE_1_2026-11-06.md)
- [Phase 2 — registre centralisé, orchestration testée et garde-fou baseline](docs/EVOLUTION_PHASE_2_2026-11-06.md)

Un build réussi valide la compilation et le packaging, pas le comportement physique. Une recette sur Push 1 avec Bitwig Studio 4.3.10 reste nécessaire après les changements concernés.

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
