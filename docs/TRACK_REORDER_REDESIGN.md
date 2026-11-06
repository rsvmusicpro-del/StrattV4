# StrattV4 — reconstruction du déplacement Push 1

## Décision d'architecture

Conserver le routage d'origine DrivenByMoss 19.2.2 et corriger uniquement la résolution des voisins dans le backend Bitwig.

Aucune interception supplémentaire dans \`PushCursorCommand\`, aucun nouveau mapping MIDI, aucune commande concurrente.

## Cause racine retenue

\`CursorTrackImpl\` amont utilisait \`createTrackBank(400, 0, 0, true)\`, puis \`Track.position()\` pour prendre l'élément précédent/suivant. Cette banque est une vue globale aplatie. La proximité d'index ne garantit pas l'appartenance au même parent. En particulier, un Group Track développé peut être suivi immédiatement par son enfant dans la banque globale. La garde \`!cursorTrack.hasParent()\` de l'une des tentatives précédentes ne protégeait pas le voisin.

La résolution doit se faire à partir de \`CursorTrack.createSiblingsTrackBank(...)\`, puis de \`TrackBank.cursorIndex()\`. La banque de frères exprime le niveau hiérarchique pertinent et élimine le choix d'un enfant comme voisin d'un groupe parent.

## Reconstruction

Le patch \`scripts/apply_push1_track_reorder.py\` :
- remplace la banque globale par une banque de frères qui suit le CursorTrack ;
- marque \`cursorIndex\` comme intéressé ;
- résout le voisin par index relatif dans cette banque ;
- vérifie les limites dans la banque sœur et la disponibilité via les indicateurs `CursorTrack.hasPrevious/hasNext` déjà suivis par DrivenByMoss ;
- n'effectue pas de lecture `exists().get()` sur un objet `Track` brut non abonné ;
- conserve les points d'insertion et la sémantique d'échange DrivenByMoss ;
- ne modifie ni les commandes Push ni les mappings physiques.

Le patch est appliqué à la copie de staging par le pipeline transactionnel. Si une ancre ou une postcondition échoue, le sous-module source reste intact.

## Limites de preuve

Les tests Python contrôlent le contrat source après application des patchs. La CI valide la compilation Java 17, les tests, l'enregistrement Push 1 et le packaging. Aucun de ces contrôles ne remplace un test de l'extension dans Bitwig 4.3.10 sur Push 1.

