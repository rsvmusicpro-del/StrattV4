# StrattV4 — audit et reconstruction du déplacement des pistes Push 1

Date : 2026-11-06
Branche : \`evolution\`
Baseline immuable : \`v4-foundation\` / \`ec5871aed16ae1fe8a40ec27943f5561b5b7b168\`
Sous-module : DrivenByMoss 19.2.2 / \`013620c1330cdcf896e96ef8fdc8a2123e4fce6a\`

## Rapport matériel

Le propriétaire rejette la dernière tentative : les déplacements observés sont aléatoires. Le précédent statut de restauration du geste natif est donc révoqué. La fonctionnalité est NON VALIDÉE.

## Historique des tentatives abandonnées

- \`3ab7097\` : interception SELECT + flèches dans \`PushCursorCommand\`.
- \`847ae92\` : commande personnalisée de déplacement des pistes racines et groupes.
- \`e08055f\` : nouvelle restriction de contexte Session + SELECT.
- \`e2f81d3\` : réaffectation SHIFT + flèches dans plusieurs modes.
- \`50ec514\` : retrait de la surcharge de commande et retour au routage natif.
- \`fc9f181\` : tests/documentation protégeant le chemin natif, mais sans correction du backend de résolution des voisins.

Les commandes personnalisées et surcharges de \`PushCursorCommand\` des essais précédents ne sont plus présentes dans le pipeline courant. Les anciens documents et tests qui les présentaient comme une solution validée sont remplacés par le présent audit.

## Fonctionnement amont

Dans DrivenByMoss 19.2.2 :
1. \`PushCursorCommand.scrollLeft/scrollRight\` délègue au mode actif.
2. \`AbstractTrackMode.selectPreviousItemPage/selectNextItemPage\` transforme SHIFT + flèche en \`ICursorTrack.swapWithPrevious/Next\`.
3. \`CursorTrackImpl\` effectue l'opération avec \`TrackInsertionPoint.moveTracks()\`.

Le routage physique et le geste SHIFT ne sont pas réécrits par StrattV4.

## Défaut identifié

Le backend amont crée une banque globale de 400 pistes avec \`createTrackBank(..., true)\`, puis utilise \`Track.position()\` pour choisir le voisin. Dans une hiérarchie Bitwig, cette banque aplatie peut placer un enfant immédiatement après son Group Track parent. Le fait que le curseur courant soit au niveau racine ne garantit pas que le voisin choisi le soit également. Une garde \`!hasParent()\` sur le seul curseur ne suffit pas.

Cette incohérence est une cause technique plausible et directement étayée par le code pour les déplacements qui changent de niveau hiérarchique. Elle explique particulièrement les cas où les Group Tracks sont développés. La validation matérielle doit confirmer le résultat.

## Nouvelle implémentation

Le nouveau patch \`scripts/apply_push1_track_reorder.py\` remplace la banque globale par \`CursorTrack.createSiblingsTrackBank(400, 0, 0, false, false)\`. Il utilise \`cursorIndex()\` pour sélectionner le voisin dans la banque de même niveau, vérifie les limites et l'existence, puis conserve les points d'insertion DrivenByMoss.

Le patch n'ajoute pas de commande Push personnalisée et ne change pas la navigation IN/OUT, les mappings MIDI ou les autres modes.

## Preuves et statut

- HEAD parent : \`fc9f1813a2fa67a9ce58ae07f08ff371059c20f6\`.
- Baseline : \`ec5871aed16ae1fe8a40ec27943f5561b5b7b168\`.
- Comparaison avant modification : evolution 39 commits en avance, 0 en retard.
- Build précédent #40 : run \`42280252862\`, succès sur \`fc9f181\`; artefact ID \`13534363252\`, digest \`sha256:4b6af8c510b5d98d1112f9f2b8643c1e5e75fbdd773868f170d79daff4661f6c\`. Ce build contient encore l'ancienne résolution des voisins et ne valide pas la nouvelle correction.
- Validation matérielle de la nouvelle correction : en attente.

