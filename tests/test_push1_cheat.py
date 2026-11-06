#!/usr/bin/env python3
"""Regression checks that the retired Note Mode is absent and SMART inherits PLAY colors."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "scripts/apply_push1_palette_transactional.py"
SMART_PATCH = ROOT / "scripts/apply_push1_smart.py"
LIFECYCLE = ROOT / "scripts/apply_push1_midi_lifecycle.py"


class NoteModeRemovalTests(unittest.TestCase):
    def test_build_does_not_run_or_require_retired_view(self):
        pipeline = PIPELINE.read_text(encoding="utf-8")
        self.assertNotIn("apply_push1_cheat.py", pipeline)
        self.assertNotIn("CheatView.java", pipeline)
        self.assertNotIn("Views.CHEAT", pipeline)

    def test_smart_inherits_play_pad_colors(self):
        smart = SMART_PATCH.read_text(encoding="utf-8")
        self.assertNotIn("protected String getGridColor", smart)
        self.assertNotIn("DAWColor.DAW_COLOR_ORANGE.name ()", smart)
        self.assertIn("public class SmartView extends PlayView", smart)
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        self.assertNotIn("CheatView", lifecycle)
        self.assertNotIn("Views.CHEAT", lifecycle)

    def test_smart_harmonization_and_midi_lifecycle_remain(self):
        smart = SMART_PATCH.read_text(encoding="utf-8")
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        self.assertIn("this.scales.getThirdChord (rootNote)", smart)
        self.assertIn("PadMidiNoteTracker", lifecycle)
        self.assertIn("this.chordNotes.noteOn (key", lifecycle)
        self.assertIn("this.chordNotes.noteOff (key", lifecycle)
        self.assertIn("this.chordNotes.releaseAll", lifecycle)
        self.assertIn("PadViewTaskGuard", lifecycle)
        self.assertIn("beginNoteMappingUpdate ()", lifecycle)
        self.assertIn("isNoteMappingUpdateCurrent (generation)", lifecycle)


if __name__ == "__main__":
    unittest.main()
