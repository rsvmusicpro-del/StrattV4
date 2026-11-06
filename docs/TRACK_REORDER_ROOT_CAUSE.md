# StrattV4 — analyse de cause racine du déplacement des pistes Push 1

Date : 2026-11-06
Branche : `evolution`
Baseline immuable : `v4-foundation` / `ec5871aed16ae1fe8a40ec27943f5561b5b7b168`
Source amont : DrivenByMoss 19.2.2, commit `013620c1330cdcf896e96ef8fdc8a2123e4fce6a`

## Symptôme

La commande de déplacement des pistes et Group Tracks, disponible dans le DrivenByMoss amont sur Push 1, ne répondait plus après certaines personnalisations de StrattV4.

## Cause racine

Le patch de navigation StrattV4 avait modifié directement `PushCursorCommand.scrollLeft()` et `scrollRight()`. Au lieu de déléguer aux méthodes du mode actif, le patch remplaçait le traitement par une navigation directe de banque et des conditions spécifiques de réordonnancement. Cette interception empêchait le mode natif de recevoir la combinaison SHIFT + flèche.

Le mécanisme de déplacement n'avait pas disparu de l'API Bitwig : il était rendu inaccessible par le détournement du chemin d'événement dans le patch personnalisé.

## Chemin natif attendu

1. Les flèches du Push 1 arrivent dans `PushCursorCommand`.
2. `PushCursorCommand` délègue à `activeMode.selectPreviousItemPage()` ou `selectNextItemPage()`.
3. `AbstractTrackMode` vérifie SHIFT et appelle `ICursorTrack.swapWithPrevious()` ou `swapWithNext()`.
4. `CursorTrackImpl` utilise les points d'insertion Bitwig et `TrackInsertionPoint.moveTracks()`.

La documentation DrivenByMoss décrit SHIFT + flèches comme déplacement de la piste sélectionnée dans les modes de mixage Push 1. La navigation normale par pages reste associée aux flèches sans SHIFT.

## Correction conservée dans evolution

Le commit `50ec514c68b3fd4bd08df69f3f9db15a1fa70225` retire la surcharge de `PushCursorCommand` du patcher de navigation et restaure le chemin natif. Aucun second gestionnaire personnalisé de déplacement de piste ne doit être ajouté.

Le déplacement de devices via SHIFT + IN/OUT reste une fonctionnalité séparée et continue d'être géré par `apply_push1_device_reorder.py`.

## Garde-fous

- Le test `tests/test_push1_track_reorder.py` vérifie la délégation native, le traitement SHIFT du mode de piste et l'utilisation de l'API d'insertion Bitwig.
- Le garde-fou ajouté dans ce point de sauvegarde interdit au pipeline transactionnel d'installer un patch concurrent `apply_push1_track_reorder.py` / `Push1TrackMoveCommand.java`.
- La suite Python complète, les tests Java, Maven, le contrôle du service Push 1 et l'intégrité de l'archive doivent passer.
- Les contrôles source et la compilation ne prouvent pas à eux seuls le déplacement physique dans chaque contexte. Les tests Push 1 + Bitwig 4.3.10, notamment avec Group Tracks, restent la preuve matérielle.

## Historique et état

- HEAD contrôlé avant ce point : `328089255626ec39ed2f400bea32db6f4a6f7bd5`.
- Comparaison baseline : 38 commits en avance, 0 en retard.
- Dernier build CI connu : #21 / run `42265014484`, sur `2b26d1203e8c3923a27df0a1b1f95d83235c9e7d`, artefact `13526433106`, digest `sha256:2d9f70c125e5a9d407ced37a66753f80c259a198de24bcb8f1a23703cb258dd4`.
- Ce run #21 n'est pas associé au HEAD contrôlé `3280892`.
- Le propriétaire a déclaré le 2026-11-06 que le dernier test matériel du dernier commit en date était validé. Le scénario détaillé et le SHA du binaire testé n'ont pas été fournis ; aucune portée supplémentaire n'est inférée.

## Règle de reprise

À chaque reprise, relire ce document, `docs/RESUME_PROTOCOL.md` et `docs/REGRESSION_POLICY.md`, vérifier le HEAD réel de `evolution`, comparer à la baseline immuable et contrôler le dernier run CI/artifact avant toute modification.
