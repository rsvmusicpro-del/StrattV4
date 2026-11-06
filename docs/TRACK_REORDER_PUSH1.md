# Push 1 track and group-track move

## Gesture

1. Enter Track mode.
2. Select the track or group track.
3. Hold SELECT and press LEFT to move it one position left.
4. Hold SELECT and press RIGHT to move it one position right.

The command checks that a previous or next track exists, then calls the cursor-track swap API. The Bitwig adapter performs the move through the track insertion points and keeps the moved track selected.

Group tracks use the same Bitwig Track object path. Verify on hardware that all child tracks remain inside the group and keep their order.

## Preserved controls

- LEFT/RIGHT without SELECT or SHIFT: existing one-track navigation.
- SHIFT + LEFT/RIGHT: existing eight-track page navigation.
- SELECT + LEFT/RIGHT in Track mode: move the selected track by one position.
- IN/OUT (PAGE LEFT/PAGE RIGHT): existing Browser, Device, Rack and sequencer navigation; not repurposed.
- The new gesture is limited to Track mode and does not replace central MIDI mappings.

## Ableton Live 10 distinction

This is not claimed as a native Ableton Live 10 command. Ableton's Push documentation describes SHIFT + LEFT/RIGHT in Session as moving the eight-track window, not reordering tracks. StrattV4 adds SELECT + arrow as a separate track-reorder gesture.

## Hardware test required

On Push 1 with Bitwig Studio 4.3.10:
1. Move a normal track left and right in Track mode.
2. Confirm the moved track stays selected.
3. Repeat with a collapsed and expanded group track; confirm its children remain grouped and ordered.
4. Test the first and last tracks; no track should disappear or change group.
5. Confirm normal arrows, SHIFT + arrows, IN/OUT and other commands remain unchanged.

CI checks source wiring and compilation; it does not replace the physical Push 1 test.
