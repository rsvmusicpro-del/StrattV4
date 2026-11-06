# StrattV4 — déplacement des pistes et Group Tracks sur Push 1

## Fonctionnement de référence

Le geste d'origine DrivenByMoss 19.2.2 est conservé : SHIFT + flèche gauche/droite dans les modes de piste qui héritent de \`AbstractTrackMode\`.

Le routage reste celui de DrivenByMoss :
1. \`PushCursorCommand\` transmet les flèches au mode actif.
2. \`AbstractTrackMode\` interprète SHIFT et appelle \`ICursorTrack.swapWithPrevious/Next()\`.
3. \`CursorTrackImpl\` effectue le déplacement via les points d'insertion Bitwig.

## Défaut corrigé dans StrattV4

La version amont 19.2.2 résout le voisin à partir d'une banque globale aplatie de 400 pistes et de \`Track.position()\`. Dans un projet hiérarchique, deux éléments consécutifs de cette banque ne sont pas nécessairement frères : après un Group Track développé, l'élément suivant peut être son enfant. Un simple contrôle \`!hasParent()\` sur la piste courante ne protège donc pas le déplacement d'un groupe contre l'un de ses enfants.

La correction StrattV4 remplace uniquement la résolution du voisin : elle utilise \`CursorTrack.createSiblingsTrackBank(400, 0, 0, false, false)\` et \`TrackBank.cursorIndex()\`. Le voisin est ainsi recherché dans la banque des pistes de même niveau que le curseur. Les limites sont contrôlées dans la banque sœur. La disponibilité du voisin est vérifiée par `CursorTrack.hasPrevious/hasNext` (`canSelectPrevious/Next`), valeurs suivies par DrivenByMoss. Le patch n'interroge pas `Track.exists()` sur un objet brut non abonné, ce qui évite une lecture potentiellement périmée.

Aucun nouveau gestionnaire de touches n'est ajouté. Le routage Push 1 et le geste SHIFT natifs restent ceux de DrivenByMoss.

## Périmètre hiérarchique

- Une piste racine se déplace parmi les pistes et groupes racines.
- Un Group Track se déplace parmi ses groupes/pistes frères ; ses enfants restent dans le groupe.
- Une piste enfant se déplace parmi les enfants du même groupe, si le contexte Bitwig la rend disponible.
- Aucun déplacement ne doit franchir une frontière de groupe.
- Les limites de début et de fin sont des opérations sans effet.

## Validation automatisée

La suite de tests vérifie :
- la délégation native des flèches ;
- le traitement SHIFT dans \`AbstractTrackMode\` ;
- l'usage de la banque de frères au lieu de la banque globale ;
- les contrôles de limites et d'existence ;
- le maintien des points d'insertion Bitwig ;
- l'absence d'un second gestionnaire de déplacement personnalisé.

Ces tests statiques et la compilation ne prouvent pas le comportement dans une session Bitwig réelle.

## Recette matérielle obligatoire

Sur Push 1 et Bitwig Studio 4.3.10 :
1. Déplacer une piste racine vers la gauche puis vers la droite.
2. Déplacer un Group Track replié dans les deux directions.
3. Déplacer un Group Track déplié et vérifier que ses enfants ne sont jamais pris comme voisins.
4. Entrer dans un groupe et déplacer une piste enfant ; vérifier qu'elle reste dans ce groupe.
5. Tester la première et la dernière piste de chaque niveau.
6. Répéter les commandes et vérifier que chaque appui ne déplace qu'un seul rang et ne change pas de niveau hiérarchique.
7. Vérifier que les flèches sans SHIFT, les autres commandes Push et les fonctions déjà validées restent inchangées.

Statut matériel : NON VALIDÉ jusqu'à la recette sur le nouveau binaire et la confirmation du propriétaire.
