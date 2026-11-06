#!/usr/bin/env python3
"""Regression checks for additive Push 1 top-level track/group reordering."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "scripts/apply_push1_palette_transactional.py"
SCRIPT = ROOT / "scripts/apply_push1_track_reorder.py"


class Push1TrackReorderTests(unittest.TestCase):
    def test_patch_runs_after_device_reordering(self):
        patcher = PATCHER.read_text(encoding="utf-8")
        device = patcher.index('"apply_push1_device_reorder.py"')
        track = patcher.index('"apply_push1_track_reorder.py"')
        self.assertLess(device, track)
        self.assertIn('"Push1TrackMoveCommand.java"', patcher)

    def test_new_chord_is_select_plus_arrows_in_session_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("surface.isSelectPressed ()", source)
        self.assertIn("!surface.isShiftPressed ()", source)
        self.assertIn("Views.SESSION", source)
        self.assertIn("Push1TrackMoveCommand.executeIfRequested", source)

    def test_only_top_level_tracks_and_groups_can_be_moved(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("cursorTrack.doesExist ()", source)
        self.assertIn("!cursorTrack.hasParent ()", source)
        self.assertIn("cursorTrack.canSelectPrevious ()", source)
        self.assertIn("cursorTrack.swapWithPrevious ()", source)
        self.assertIn("cursorTrack.canSelectNext ()", source)
        self.assertIn("cursorTrack.swapWithNext ()", source)

    def test_arrow_navigation_and_led_state_are_preserved_outside_new_chord(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("final IMode activeMode = this.surface.getModeManager ().getActive ();", source)
        self.assertIn("this.canScrollUp = sceneBank.canScrollBackwards ();", source)
        self.assertIn("this.canScrollDown = sceneBank.canScrollForwards ();", source)
        self.assertIn("final IMode mode = this.surface.getModeManager ().getActive ();", source)
        self.assertIn("Push1TrackMoveCommand.isGestureActive (this.surface)", source)

    def test_patch_is_limited_to_cursor_navigation_not_hardware_mapping(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("PushControllerSetup.java", source)
        self.assertNotIn("ButtonID.", source)
        self.assertNotIn("PageLeftCommand.java", source)
        self.assertNotIn("PageRightCommand.java", source)
        self.assertIn('path = TRIGGER / "PushCursorCommand.java"', source)

    def test_patch_applies_once_to_expected_upstream_shape(self):
        with tempfile.TemporaryDirectory() as temporary:
            trigger = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push/command/trigger"
            trigger.mkdir(parents=True)
            (trigger / "PushCursorCommand.java").write_text(
                "import de.mossgrabers.framework.view.Views;\n"
                "class PushCursorCommand {\n"
                "    protected void scrollLeft ()\n    {\n"
                "        final IMode activeMode = this.surface.getModeManager ().getActive ();\n"
                "        if (activeMode != null)\n            activeMode.selectPreviousItemPage ();\n"
                "    }\n"
                "    protected void scrollRight ()\n    {\n"
                "        final IMode activeMode = this.surface.getModeManager ().getActive ();\n"
                "        if (activeMode != null)\n            activeMode.selectNextItemPage ();\n"
                "    }\n"
                "    protected void updateArrowStates ()\n    {\n"
                "        final ISceneBank sceneBank = this.getSceneBank ();\n"
                "        this.canScrollUp = sceneBank.canScrollBackwards ();\n"
                "        this.canScrollDown = sceneBank.canScrollForwards ();\n"
                "        final IMode mode = this.surface.getModeManager ().getActive ();\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "-B", str(SCRIPT)],
                cwd=temporary,
                check=True,
                capture_output=True,
                text=True,
            )
            patched = (trigger / "PushCursorCommand.java").read_text(encoding="utf-8")
            self.assertEqual(patched.count("Push1TrackMoveCommand.executeIfRequested"), 2)
            self.assertEqual(patched.count("Push1TrackMoveCommand.isGestureActive"), 1)
            self.assertIn("activeMode.selectPreviousItemPage ();", patched)
            self.assertIn("activeMode.selectNextItemPage ();", patched)
            self.assertTrue((trigger / "Push1TrackMoveCommand.java").is_file())


if __name__ == "__main__":
    unittest.main()
