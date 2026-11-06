# Push 1 track and group-track move

## Gesture

1. Enter Session view.
2. Select the top-level track or Group Track to move.
3. Hold SELECT (without SHIFT) and press LEFT to move it one position left.
4. Hold SELECT (without SHIFT) and press RIGHT to move it one position right.

The command is handled by the physical cursor-arrow command in Session view. It checks that the cursor track exists, is a top-level track (has no parent group), and has a neighbour in the requested direction before calling the cursor-track swap API. The Bitwig adapter performs the move through track insertion points.

A top-level Group Track moves as one track object; its children are expected to remain within the group. Child tracks inside a group are deliberately not moved across group boundaries by this gesture.

## Preserved controls

- LEFT/RIGHT without SELECT: existing one-track navigation.
- SHIFT + LEFT/RIGHT: existing eight-track page navigation.
- SELECT + LEFT/RIGHT in Session view, without SHIFT: move the selected top-level track or Group Track by one position.
- SELECT + SHIFT + LEFT/RIGHT: does not invoke the move gesture; SHIFT paging remains the existing modifier path.
- IN/OUT (PAGE LEFT/PAGE RIGHT): existing Browser, Device, Rack and sequencer navigation; not repurposed.
- The new gesture does not replace central MIDI mappings.

## Implementation and regression coverage

The patch is applied to `PushCursorCommand`, which is the command registered for the physical LEFT/RIGHT cursor buttons. The same Session/SELECT/no-SHIFT/top-level conditions govern command execution and arrow LED availability. This avoids a mismatch where the LEDs advertise a gesture that the command does not accept, or vice versa.

Automated tests verify the patch's context gate, both movement directions, parent/boundary guards, the unchanged normal and SHIFT navigation paths, and the existing Bitwig insertion-point implementation. These are source-level regression checks; they do not simulate Bitwig's runtime or replace hardware validation.

## Hardware test required

On Push 1 with Bitwig Studio 4.3.10:

1. In Session view, move a normal top-level track left and right.
2. Confirm the moved track remains selected and only moves one position.
3. Repeat with a collapsed and expanded top-level Group Track; confirm all children remain in that group and retain their order.
4. Test the first and last top-level entries; no track should disappear or change group.
5. Confirm SELECT + arrows outside Session does not reorder tracks.
6. Confirm SHIFT + arrows and arrows alone retain their previous navigation.
7. Confirm IN/OUT, device reordering, scene navigation, clip selection and Note view remain unchanged.

A successful CI build proves the automated checks and packaging, not physical Push 1 behavior. The new gesture remains unvalidated on hardware until the owner completes this recipe.
