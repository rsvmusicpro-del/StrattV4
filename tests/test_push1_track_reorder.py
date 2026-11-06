#!/usr/bin/env python3
"""Regression checks for safe Push 1 track/group reordering."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"


class Push1TrackReorderTests(unittest.TestCase):
    def test_navigation_patcher_does_not_intercept_track_move_gesture(self):
        patcher = (ROOT / "scripts/apply_push1_navigation.py").read_text(encoding="utf-8")
        self.assertNotIn("PushCursorCommand.java", patcher)
        self.assertNotIn("swapWithPrevious", patcher)
        self.assertNotIn("swapWithNext", patcher)

    def test_track_reorder_is_a_single_adapter_patch_not_a_second_command(self):
        pipeline = (ROOT / "scripts/apply_push1_palette_transactional.py").read_text(encoding="utf-8")
        patch = (ROOT / "scripts/apply_push1_track_reorder.py").read_text(encoding="utf-8")
        self.assertIn("apply_push1_track_reorder.py", pipeline)
        self.assertNotIn("Push1TrackMoveCommand.java", pipeline)
        self.assertIn("CursorTrackImpl.java", patch)
        self.assertNotIn("PushCursorCommand.java", patch)

    def test_cursor_arrows_keep_the_native_active_mode_dispatch(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        left = source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right = source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        self.assertIn("activeMode.selectPreviousItemPage ()", left)
        self.assertIn("activeMode.selectNextItemPage ()", right)
        self.assertNotIn("swapWith", left + right)

    def test_track_mode_keeps_the_drivenbymoss_shift_gesture(self):
        source = (JAVA / "controller/ableton/push/mode/track/AbstractTrackMode.java").read_text(encoding="utf-8")
        previous = source[source.index("public void selectPreviousItemPage ()"):source.index("public void selectNextItemPage ()")]
        next_item = source[source.index("public void selectNextItemPage ()"):source.index("Handle the selection of a send effect")]
        self.assertIn("this.surface.isShiftPressed ()", previous)
        self.assertIn("cursorTrack.swapWithPrevious ()", previous)
        self.assertIn("this.surface.isShiftPressed ()", next_item)
        self.assertIn("cursorTrack.swapWithNext ()", next_item)

    def test_backend_uses_same_level_sibling_bank_not_flat_positions(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("createSiblingsTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, false, false)", source)
        self.assertIn("siblingTrackBank.cursorIndex ().markInterested ()", source)
        self.assertIn("this.siblingTrackBank.cursorIndex ().get ()", source)
        self.assertIn("this.siblingTrackBank.getItemAt (targetIndex)", source)
        self.assertNotIn("largeTrackBank", source)
        self.assertNotIn("getPosition () - 1", source)
        self.assertNotIn("getPosition () + 1", source)

    def test_moves_use_sibling_insertion_points_and_reject_missing_targets(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("!this.canSelectPrevious ()", source)
        self.assertIn("!this.canSelectNext ()", source)
        self.assertIn("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack)", source)
        self.assertIn("this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack)", source)
        self.assertIn("target.exists ().get ()", source)
        self.assertIn("targetIndex < 0 || targetIndex >= NUM_TRACKS_LARGE_BANK", source)

    def test_group_and_child_tracks_use_the_same_sibling_scoped_operation(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        track = (JAVA / "bitwig/framework/daw/data/TrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("createSiblingsTrackBank", source)
        self.assertIn("public boolean isGroup ()", track)
        self.assertIn("return this.track.isGroup ().get ();", track)


if __name__ == "__main__":
    unittest.main()
