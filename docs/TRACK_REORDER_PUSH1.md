# StrattV4 — déplacement des pistes et groupes avec Push 1

## Commande ajoutée

Dans la vue Session :

- Maintenir **SELECT** et presser **flèche gauche** : réordonner la piste ou le groupe sélectionné d'une position vers la gauche.
- Maintenir **SELECT** et presser **flèche droite** : réordonner la piste ou le groupe sélectionné d'une position vers la droite.
- **SHIFT + flèches** conserve la navigation par pages existante.
- Les flèches seules conservent leur navigation habituelle.
- En dehors de la vue Session, la nouvelle combinaison n'intercepte aucune commande.
- Les pistes imbriquées dans un groupe ne sont pas déplacées par ce premier ajout ; le geste est consommé sans action afin d'éviter de franchir une frontière de groupe ou de modifier la hiérarchie.

Le périmètre couvre les pistes de premier niveau et les Group Tracks de premier niveau. Un Group Track est déplacé comme un élément de piste ; ses enfants restent dans le groupe.

## Pourquoi ce mapping ?

La documentation Ableton Live 10 / Push 1 décrit les flèches gauche/droite comme navigation entre pistes, et SHIFT + flèches comme navigation par blocs de huit en Session. Elle ne documente pas de geste Push 1 pour réordonner une piste existante. Le maintien du bouton de sélection d'une piste avec la molette est documenté pour des générations plus récentes de Push, pas pour Push 1.

StrattV4 ajoute donc un geste propriétaire, sans détourner les commandes de navigation existantes : SELECT + flèches en vue Session, sans SHIFT.

## Implémentation

Le patch s'insère dans `PushCursorCommand`, qui reçoit déjà les flèches matérielles gauche/droite. Il délègue uniquement si SELECT est maintenu, SHIFT ne l'est pas et la vue Session est active.

Il réutilise les opérations déjà exposées par DrivenByMoss / Bitwig :
- `ICursorTrack.canSelectPrevious()` / `canSelectNext()`
- `ICursorTrack.swapWithPrevious()` / `swapWithNext()`

La condition `!cursorTrack.hasParent()` limite explicitement cette première version aux pistes de premier niveau et aux groupes de premier niveau. Le script ne modifie pas `PushControllerSetup`, les identifiants MIDI, les boutons IN/OUT, ni les commandes PageLeft/PageRight. Les LED des flèches reflètent la possibilité de déplacement pendant le geste.

## Limites et recette matérielle

La CI prouve la compilation et les tests automatisés, mais pas le comportement réel de Bitwig sur un projet utilisateur. Vérifier sur Push 1 / Bitwig Studio 4.3.10 :

1. Dans Session, sélectionner une piste simple au milieu de plusieurs pistes.
2. Maintenir SELECT + flèche gauche ; vérifier qu'elle change de position d'un rang.
3. Maintenir SELECT + flèche droite ; vérifier le déplacement inverse.
4. Refaire le test avec un Group Track contenant plusieurs pistes ; vérifier que le groupe entier et ses enfants restent ensemble.
5. Vérifier les limites de début et de fin de la liste.
6. Vérifier qu'une piste enfant dans un groupe ne sort pas du groupe.
7. Vérifier flèches seules, SHIFT + flèches, navigation des scènes, sélection des clips et mode Note.
8. Vérifier les fonctions de déplacement des devices : SHIFT + IN/OUT en mode Device.

Ne pas déclarer cette fonction matériellement validée avant cet essai.
