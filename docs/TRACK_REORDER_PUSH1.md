# Déplacer une piste ou un Group Track avec Push 1

## Geste disponible dans StrattV4

1. Passer en mode **Track** sur le Push 1.
2. Sélectionner la piste à déplacer avec les boutons de sélection de piste sous l'écran.
3. Maintenir **SHIFT** et presser la flèche **LEFT** pour déplacer la piste d'une position vers la gauche.
4. Maintenir **SHIFT** et presser la flèche **RIGHT** pour la déplacer d'une position vers la droite.

Le geste utilise le curseur de piste Bitwig : `ICursorTrack.swapWithPrevious()` / `swapWithNext()`. Le contrôleur DrivenByMoss le réalise avec les points d'insertion de piste Bitwig (`afterTrackInsertionPoint()` / `beforeTrackInsertionPoint()`) puis resélectionne la piste déplacée.

Un Group Track est un objet `Track` sélectionnable comme les autres pistes. Il passe par la même opération de déplacement ; la conservation de toute sa hiérarchie d'enfants doit néanmoins être confirmée sur le matériel et dans la version Bitwig cible.

## Commandes préservées

- **LEFT / RIGHT sans SHIFT** : navigation de page existante.
- **IN / OUT (PAGE LEFT / PAGE RIGHT)** : restent dédiés à leur navigation existante ; ils ne sont pas détournés pour déplacer des pistes.
- Aucun mapping central PushControllerSetup ni identifiant MIDI n'est remplacé pour cette fonction.

Le chemin est déjà présent dans la révision DrivenByMoss épinglée par le projet : `PushCursorCommand` délègue aux méthodes de page du mode actif, et `AbstractTrackMode` transforme ces méthodes en déplacement de piste lorsque SHIFT est maintenu.

## Précision sur Ableton Live 10

Cette affectation n'est pas présentée comme une commande native Ableton Live 10. La documentation Push d'Ableton décrit notamment SHIFT + LEFT/RIGHT en Session comme un déplacement de la fenêtre de huit pistes, pas comme un réordonnancement de pistes. StrattV4 conserve donc le geste de réordonnancement fourni par DrivenByMoss/Bitwig, dans le contexte Track, sans détourner les commandes de navigation Session.

## Recette matérielle à effectuer

Sur Push 1 avec Bitwig Studio 4.3.10 :

1. En mode Track, déplacer une piste ordinaire vers la gauche puis vers la droite.
2. Vérifier que la piste reste sélectionnée après chaque déplacement.
3. Répéter avec un Group Track replié, puis déplié ; vérifier que tous ses enfants restent dans le groupe et conservent leur ordre.
4. Tester les première et dernière pistes ; aucune piste ne doit disparaître ni changer de groupe.
5. Vérifier que LEFT/RIGHT sans SHIFT, IN/OUT et les autres commandes restent inchangés.

La CI valide le câblage source et la compilation ; elle ne remplace pas cette recette sur le Push 1 physique.
