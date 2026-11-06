# Réimplémentation — déplacement des pistes et Group Tracks sur Push 1

## Décision

Ne plus ajouter de seconde implémentation de déplacement dans `PushCursorCommand`.
Le contrôleur doit retrouver le chemin natif DrivenByMoss :

1. `PushCursorCommand.scrollLeft/scrollRight` délègue à `activeMode.selectPreviousItemPage()` / `selectNextItemPage()`.
2. En mode Track (et ses modes de mixage dérivés), `AbstractTrackMode` interprète SHIFT comme un déplacement de piste et appelle `ICursorTrack.swapWithPrevious/Next()`.
3. Le backend Bitwig déplace le Track sélectionné via son `TrackInsertionPoint` et sélectionne le voisin déplacé.

La documentation DrivenByMoss décrit précisément SHIFT + flèches gauche/droite comme déplacement de la piste sélectionnée. Elle indique aussi que le déplacement fonctionne au-delà des frontières de pages depuis la version 16.3.

## Ce que les essais précédents nous apprennent

- SELECT + flèches est abandonné : ce geste interfère avec d'autres gestes SELECT du Push.
- La logique ajoutée dans `PushCursorCommand` a doublonné le routage que le mode Track sait déjà effectuer.
- La restriction `!cursorTrack.hasParent()` a également empêché le déplacement des pistes enfants, alors que le besoin principal porte sur une piste ou un groupe sélectionné.
- Les tests précédents vérifiaient surtout la présence de fragments de code. Ils ne prouvaient pas le chemin d'événement complet du Push jusqu'au mode Track.

## Nouvelle règle d'implémentation

- Aucun appel direct à `swapWithPrevious/Next` depuis `PushCursorCommand`.
- Aucun second état LED de déplacement calculé dans `PushCursorCommand`.
- Le routage natif du curseur reste intact ; le mode actif est seul responsable de la sémantique SHIFT.
- Le patch de navigation IN/OUT continue de traiter uniquement les commandes IN/OUT, le navigateur et les pages d'appareils.
- Le geste doit être exercé depuis les modes Track/Volume documentés, pas depuis la vue Session si celle-ci ne fournit pas le mode Track correspondant.

## Couverture de régression

Les tests vérifient désormais les trois étages distincts : délégation des flèches, interprétation SHIFT dans `AbstractTrackMode`, puis déplacement Bitwig par insertion avant/après. Ils interdisent également au patcher de navigation de réécrire `PushCursorCommand`.

Ces tests restent des contrôles de contrat source et de compilation ; ils ne remplacent pas la recette physique.

## Recette matérielle obligatoire

Sur Push 1 + Bitwig Studio 4.3.10 :

1. Entrer en mode Track, sélectionner une piste ordinaire qui n'est ni première ni dernière.
2. Maintenir SHIFT + flèche gauche, puis SHIFT + flèche droite ; vérifier le changement réel d'ordre dans Bitwig.
3. Refaire avec un Group Track et vérifier que le groupe et ses enfants restent ensemble.
4. Tester une piste aux deux extrémités et vérifier l'absence de déplacement hors limites.
5. Vérifier que les flèches seules conservent la navigation et que SHIFT + flèches ne perturbent pas les autres modes.
6. Vérifier les autres fonctions Push déjà validées.

Aucune validation matérielle ne sera revendiquée sur la seule base de la CI.
