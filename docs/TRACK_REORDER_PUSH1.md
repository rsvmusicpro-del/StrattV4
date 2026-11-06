# Push 1 track and group-track move

## New assignment

- Hold SHIFT and press LEFT to move the selected top-level track or Group Track one position left.
- Hold SHIFT and press RIGHT to move it one position right.
- Available in Session view and Track and Volume modes.
- SELECT is not part of the gesture; the previous SELECT+arrow assignment is removed.

The physical cursor-arrow command uses the global Bitwig cursor track, not the active mode's item-page selection. It checks that the cursor track exists, is a top-level track (has no parent group), and has a neighbour in the requested direction before calling the cursor-track swap API. The Bitwig adapter performs the move through track insertion points.

A top-level Group Track moves as one track object. Tracks inside a group are deliberately not moved: the current adapter uses the global track position and does not prove safe sibling-only moves across nested group boundaries.

## Preserved controls

- LEFT/RIGHT without SHIFT: existing single-item navigation.
- SHIFT + LEFT/RIGHT in Session, Track and Volume: move selected top-level track/group one position.
- SHIFT + LEFT/RIGHT elsewhere: retain pre-existing page navigation.
- Browser arrows retain Browser content-type navigation.
- IN/OUT retain Browser, Device, Rack and sequencer navigation.
- Central MIDI mappings are unchanged.

## Implementation and regression coverage

The patch is applied to PushCursorCommand, registered for the physical LEFT/RIGHT buttons. The same Shift/context/top-level/boundary conditions govern execution and arrow LED availability. Patch postconditions and regression tests reject the obsolete SELECT assignment.

Tests cover both directions, all three contexts, SELECT removal, parent/boundary guards, arrow LEDs, normal navigation, Browser routing and Bitwig's insertion-point implementation. They are source-level checks, not a substitute for Push 1 hardware validation.

## Hardware test required

On Push 1 with Bitwig Studio 4.3.10:
1. In Session, test SHIFT+LEFT/RIGHT on a normal top-level track.
2. Repeat in Track mode.
3. Repeat in Volume mode.
4. Repeat with collapsed and expanded top-level Group Tracks; verify children remain grouped and ordered.
5. Test first/last top-level entries; no disappearance, wrap or group change.
6. Verify SELECT+LEFT/RIGHT no longer moves tracks.
7. Verify unmodified LEFT/RIGHT still navigates normally.
8. Verify SHIFT+LEFT/RIGHT in Browser, Device, Rack and sequencer contexts retains prior behavior.
9. Verify IN/OUT, device reordering, scene navigation, clip selection and Note view.

CI proves automated checks and packaging, not hardware behavior. This gesture remains unvalidated until the owner completes this recipe.
