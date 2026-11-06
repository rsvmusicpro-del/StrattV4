# StrattV4 — déplacement des devices avec Push 1

## Affectation ajoutée

Dans le mode **DEVICE** de StrattV4 :

- Maintenir **SHIFT** et presser **IN / PAGE LEFT** : déplacer le device sélectionné d'une position vers la gauche dans sa chaîne.
- Maintenir **SHIFT** et presser **OUT / PAGE RIGHT** : déplacer le device sélectionné d'une position vers la droite dans sa chaîne.
- **IN / OUT sans SHIFT** : conserver la navigation existante entre les devices, banques, paramètres et chaînes.
- En dehors des modes Device et Device Chains : aucune nouvelle action n'est exécutée.

Le déplacement est limité aux voisins existants. Aux extrémités de la chaîne, la commande ne fait rien et ne déclenche pas la navigation normale.

## Fondement technique

La révision DrivenByMoss épinglée expose déjà `ICursorDevice.swapWithPrevious()` et `swapWithNext()`. L'adaptateur Bitwig implémente ces opérations via les points d'insertion de devices et sélectionne le device déplacé. StrattV4 réutilise cette API plutôt que de réimplémenter le déplacement ou de manipuler directement le projet.

Le nouveau gestionnaire est isolé dans `Push1DeviceMoveCommand`. Les deux commandes In/Out ne lui délèguent que lorsque SHIFT est maintenu et que le contexte est un mode Device. Les pressions simples et les autres contextes continuent dans leur chemin de traitement existant.

## Distinction avec Ableton Live 10

La documentation officielle Ableton confirme `SHIFT + ADD EFFECT` pour **insérer un nouveau device à gauche** du device sélectionné. Elle ne décrit pas ce geste comme un déplacement d'un device existant. Le réordonnancement de StrattV4 est donc une fonction nouvelle inspirée du workflow matériel Push, implémentée grâce aux capacités de Bitwig/DrivenByMoss ; elle n'est pas présentée comme une commande native Ableton.

## Vérifications automatisées

Le patcher ajoute le gestionnaire après le patch de navigation existant, vérifie sa présence dans l'arbre temporaire et conserve le caractère transactionnel du build. Les tests Python contrôlent le contexte, les deux directions, les bornes, l'ordre du patch et l'absence de modification du mapping central PushControllerSetup.

La compilation complète Maven et les tests existants restent obligatoires dans GitHub Actions.

## Recette physique requise

Sur Push 1 avec Bitwig Studio 4.3.10 :

1. Sélectionner une piste contenant au moins trois devices.
2. Entrer en mode DEVICE et sélectionner le device du milieu.
3. Maintenir SHIFT et presser IN ; vérifier que son ordre change d'une position vers la gauche.
4. Maintenir SHIFT et presser OUT ; vérifier le déplacement inverse.
5. Presser IN puis OUT sans SHIFT ; vérifier que la navigation habituelle est inchangée.
6. Tester le premier et le dernier device ; aucune sortie de chaîne ni suppression ne doit se produire.
7. Répéter dans une chaîne imbriquée/Rack si ce contexte est exposé par le projet.

Un build CI réussi ne remplace pas cette recette sur le matériel physique.
