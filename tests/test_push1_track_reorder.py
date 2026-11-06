#!/usr/bin/env python3
"""Regression checks for native DrivenByMoss Push 1 track/group reordering."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"


class Push1TrackReorderTests(unittest.TestCase):
    def test_navigation_patch_does_not_override_native_cursor_command(self):
        patcher = (ROOT / "scripts/apply_push1_navigation.py").read_text(encoding="utf-8")
        self.assertNotIn("PushCursorCommand.java", patcher)
        self.assertNotIn("ICursorTrack", patcher)
        self.assertNotIn("isTrackReorderContext", patcher)
        self.assertNotIn("swapWithPrevious", patcher)
        self.assertNotIn("swapWithNext", patcher)

    def test_cursor_arrows_delegate_to_active_mode(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        left = source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right = source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        self.assertIn("activeMode.selectPreviousItemPage ()", left)
        self.assertIn("activeMode.selectNextItemPage ()", right)
        self.assertNotIn("cursorTrack.swapWith", left + right)

    def test_native_track_mode_owns_shift_reorder_gesture(self):
        source = (JAVA / "controller/ableton/push/mode/track/AbstractTrackMode.java").read_text(encoding="utf-8")
        previous = source[source.index("public void selectPreviousItemPage ()"):source.index("public void selectNextItemPage ()")]
        next_item = source[source.index("public void selectNextItemPage ()"):source.index("Handle the selection of a send effect")]
        self.assertIn("this.surface.isShiftPressed ()", previous)
        self.assertIn("cursorTrack.swapWithPrevious ()", previous)
        self.assertIn("this.surface.isShiftPressed ()", next_item)
        self.assertIn("cursorTrack.swapWithNext ()", next_item)

    def test_native_bitwig_move_uses_track_insertion_points(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);", source)
        self.assertIn("this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);")
        self.assertIn("prevTrack.selectInEditor ();", source)
        self.assertIn("nextTrack.selectInEditor ();", source)

    def test_track_and_group_are_the_same_native_track_object(self):
        source = (JAVA / "bitwig/framework/daw/data/TrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("protected final Track            track;", source)
        self.assertIn("public boolean isGroup ()", source)
        self.assertIn("return this.track.isGroup ().get ();", source)


if __name__ == "__main__":
    unittest.main()
