#!/usr/bin/env python3
"""Regression checks that the retired Note Mode is absent and SMART inherits PLAY colors."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from patch_manifest import PATCH_STEPS, REQUIRED_SOURCES
SMART_PATCH = ROOT / "scripts/apply_push1_smart.py"
LIFECYCLE = ROOT / "scripts/apply_push1_midi_lifecycle.py"


class NoteModeRemovalTests(unittest.TestCase):
    def test_build_does_not_run_or_require_retired_view(self):
        patch_names = tuple(step.script for step in PATCH_STEPS)
        self.assertNotIn("apply_push1_cheat.py", patch_names)
        self.assertFalse(any("CheatView.java" in path for path in REQUIRED_SOURCES))
        self.assertNotIn("Views.CHEAT", patch_names)

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
