#!/usr/bin/env python3
"""Regression checks for the additive Push 1 track-reorder gesture."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"

class Push1TrackReorderTests(unittest.TestCase):
    def test_select_arrows_move_cursor_track_only_in_track_mode(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        self.assertIn("this.surface.isSelectPressed () && this.surface.getModeManager ().isActive (Modes.TRACK)", source)
        self.assertIn("cursorTrack.canSelectPrevious ()", source)
        self.assertIn("cursorTrack.swapWithPrevious ()", source)
        self.assertIn("cursorTrack.canSelectNext ()", source)
        self.assertIn("cursorTrack.swapWithNext ()", source)

    def test_normal_and_shift_navigation_are_preserved(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        for token in ("trackBank.selectPreviousItem ()", "trackBank.selectNextItem ()", "trackBank.selectPreviousPage ()", "trackBank.selectNextPage ()"):
            self.assertIn(token, source)

    def test_cursor_track_moves_tracks_using_bitwig_insertion_points(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);", source)
        self.assertIn("this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);", source)
        self.assertIn("prevTrack.selectInEditor ();", source)
        self.assertIn("nextTrack.selectInEditor ();", source)

    def test_group_tracks_are_track_objects_and_use_same_cursor_path(self):
        track = (JAVA / "bitwig/framework/daw/data/TrackImpl.java").read_text(encoding="utf-8")
        cursor = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("public class TrackImpl extends ChannelImpl implements ITrack", track)
        self.assertIn("public boolean isGroup ()", track)
        self.assertIn("public void swapWithPrevious ()", cursor)
        self.assertIn("public void swapWithNext ()", cursor)

    def test_page_buttons_are_not_used_as_track_move_controls(self):
        left = (JAVA / "controller/ableton/push/command/trigger/PageLeftCommand.java").read_text(encoding="utf-8")
        right = (JAVA / "controller/ableton/push/command/trigger/PageRightCommand.java").read_text(encoding="utf-8")
        self.assertNotIn("swapWithPrevious", left)
        self.assertNotIn("swapWithNext", right)

if __name__ == "__main__":
    unittest.main()
