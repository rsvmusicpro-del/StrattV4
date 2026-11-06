#!/usr/bin/env python3
"""Regression checks for SMART harmonization, MIDI lifecycle and inherited PLAY colors."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts/apply_push1_smart.py"
TRANSACTIONAL = ROOT / "scripts/apply_push1_palette_transactional.py"
PALETTE = ROOT / "scripts/apply_push1_palette.py"
LIFECYCLE = ROOT / "scripts/apply_push1_midi_lifecycle.py"


class Push1SmartModeTests(unittest.TestCase):
    def test_smart_keeps_harmonization_and_inherits_play_colors(self):
        source = PATCH.read_text(encoding="utf-8")
        self.assertIn("public class SmartView extends PlayView", source)
        self.assertIn("this.scales.getThirdChord (rootNote)", source)
        self.assertNotIn("protected String getGridColor", source)
        self.assertNotIn("DAWColor.DAW_COLOR_ORANGE.name ()", source)
        self.assertNotIn("import de.mossgrabers.framework.daw.DAWColor;", source)
        self.assertNotIn("import de.mossgrabers.framework.daw.data.ITrack;", source)
        self.assertNotIn("import de.mossgrabers.framework.view.AbstractPlayView;", source)
        self.assertNotIn("def replace_count", source)
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        self.assertIn("this.chordNotes.noteOn (key", lifecycle)
        self.assertIn("this.chordNotes.noteOff (key", lifecycle)
        self.assertIn("this.chordNotes.releaseAll", lifecycle)
        self.assertIn("public void updateNoteMapping ()", lifecycle)
        self.assertIn("this.surface.setKeyTranslationTable (EMPTY_TABLE)", lifecycle)
        self.assertIn("this.surface.getModeManager ().addChangeListener", lifecycle)
        self.assertIn("this.keyManager.clearPressedKeys ()", lifecycle)
        smart_patch_anchor = lifecycle.index("smart_path = ROOT / \"controller/ableton/push/view/SmartView.java\"")
        observer_start = lifecycle.index("this.model.getTrackBank ().addSelectionObserver", smart_patch_anchor)
        observer_end = lifecycle.index("this.surface.getModeManager ().addChangeListener", observer_start)
        track_observer = lifecycle[observer_start:observer_end]
        self.assertIn("this.releaseChordNotes ()", track_observer)
        self.assertNotIn("clearPressedKeys", track_observer)
        self.assertIn("this.chordNotes.noteOn (key, channel, additionalNotes, chordVelocity, this.chordMidiSender)", lifecycle)
        self.assertNotIn("noteOn (key, channel, rootNote, additionalNotes", lifecycle)
        self.assertNotIn("new int [additionalNotes.length + 1]", lifecycle)
        self.assertIn("public void onDeactivate ()", lifecycle)
        self.assertIn("super.onGridNote (key, velocity)", source)
        self.assertNotIn("CHEAT", lifecycle)

    def test_smart_releases_stale_chord_when_no_valid_extensions_exist(self):
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        smart = lifecycle.split('new_smart_method = """', 1)[1].split('"""', 1)[0]
        self.assertIn("if (!hasValidChordExtension (additionalNotes))", smart)
        self.assertIn("private static boolean hasValidChordExtension (final int [] notes)", smart)
        guard = smart.index("if (!hasValidChordExtension (additionalNotes))")
        tracker_call = smart.index("this.chordNotes.noteOn (key, channel, additionalNotes", guard)
        release_call = smart.index("this.releaseChordNote (key);", guard)
        self.assertLess(release_call, tracker_call)
        self.assertIn("note >= 0 && note <= 127", smart)

    def test_chords_releases_stale_notes_for_invalid_or_out_of_range_extensions(self):
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        chord = lifecycle.split('new_chord_method = """', 1)[1].split('"""', 1)[0]
        self.assertIn("if (!hasValidChordExtension (chord, note))", chord)
        self.assertIn("private static boolean hasValidChordExtension (final int [] notes, final int excludedNote)", chord)
        self.assertIn("this.chordNotes.noteOff (key, this.chordMidiSender);", chord)
        self.assertIn("note != excludedNote && note >= 0 && note <= 127", chord)

    def test_smart_note_tracking_avoids_temporary_chord_array(self):
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        self.assertIn("private final PadMidiNoteTracker.MidiSender chordMidiSender", lifecycle)
        self.assertIn("this.chordNotes.noteOn (key, channel, additionalNotes", lifecycle)
        self.assertNotIn("new int [additionalNotes.length + 1]", lifecycle)
        self.assertIn("invalid replacement must not release", (ROOT / "tests/java/PadMidiNoteTrackerTest.java").read_text(encoding="utf-8"))
        self.assertIn("Math.min (127, velocity)", lifecycle)
        self.assertIn("containsValidNote (requestedNotes)", lifecycle)

    def test_native_chords_mode_tracks_shared_note_ownership(self):
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        self.assertIn("framework/view/AbstractChordView.java", lifecycle)
        self.assertIn("native CHORDS exact note lifecycle", lifecycle)
        self.assertIn("this.chordNotes.noteOnExcept (key, channel, note, chord, chordVelocity, this.chordMidiSender)", lifecycle)
        self.assertIn("this.chordNotes.noteOff (key, this.chordMidiSender)", lifecycle)
        self.assertIn("this.chordNotes.releaseAll (this.chordMidiSender)", lifecycle)
        self.assertIn("remove direct chord MIDI input after ownership tracking", lifecycle)

    def test_smart_is_additive_and_preserves_existing_view_ordinals(self):
        source = PATCH.read_text(encoding="utf-8")
        self.assertIn('"    DUMMY6;"', source)
        self.assertIn('SMART;', source)
        self.assertIn("NOTE_VIEWS.add (SMART)", source)
        self.assertIn("VIEW_NAMES.put (NAME_SMART, SMART)", source)

    def test_smart_selector_position_and_physical_row_correction_are_preserved(self):
        source = PATCH.read_text(encoding="utf-8")
        self.assertIn("Views.POLY_SEQUENCER,\n        Views.SMART,\n        Views.DRUM", source)
        self.assertIn("this.activateView (VIEWS_TOP[index]);", source)
        self.assertIn("this.activateView (VIEWS[index]);", source)

    def test_push1_preserves_program_change_and_clip_length_tools(self):
        source = PATCH.read_text(encoding="utf-8") + PALETTE.read_text(encoding="utf-8")
        self.assertIn("import de.mossgrabers.controller.ableton.push.view.PrgChangeView;", source)
        self.assertIn("viewManager.register (Views.PRG_CHANGE, new PrgChangeView (surface, this.model));", source)
        self.assertIn("Views.CLIP_LENGTH", source)
        self.assertIn('display.setBlock (2, 3, "Tools:");', source)
        self.assertIn('titleBottom = "Tools";', source)
        self.assertIn("Existing Push 1 Program Change view/registration must be preserved", source)
        for token in ("RaindropsView", "Drum4View", "Drum8View"):
            self.assertIn(token, source)

    def test_transactional_build_runs_smart_after_palette_without_retired_patch(self):
        source = TRANSACTIONAL.read_text(encoding="utf-8")
        self.assertLess(source.index("apply_push1_palette.py"), source.index("apply_push1_smart.py"))
        self.assertNotIn("apply_push1_cheat.py", source)
        self.assertIn('"SmartView.java"', source)


if __name__ == "__main__":
    unittest.main()
