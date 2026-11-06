#!/usr/bin/env python3
"""Regression checks for the existing Push 1 track-reorder gesture."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"


class Push1TrackReorderTests(unittest.TestCase):
    def test_push_cursor_routes_left_right_to_active_mode_page_handlers(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        self.assertIn("activeMode.selectPreviousItemPage ()", source)
        self.assertIn("activeMode.selectNextItemPage ()", source)

    def test_track_mode_uses_shift_left_right_for_cursor_track_swap(self):
        track_mode = (JAVA / "controller/ableton/push/mode/track/TrackMode.java").read_text(encoding="utf-8")
        abstract_mode = (JAVA / "controller/ableton/push/mode/track/AbstractTrackMode.java").read_text(encoding="utf-8")
        self.assertIn("public class TrackMode extends AbstractTrackMode", track_mode)
        self.assertIn("if (this.surface.isShiftPressed ())", abstract_mode)
        self.assertIn("cursorTrack.swapWithPrevious ();", abstract_mode)
        self.assertIn("cursorTrack.swapWithNext ();", abstract_mode)

    def test_cursor_track_moves_tracks_using_bitwig_insertion_points(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);", source)
        self.assertIn("this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);", source)
        self.assertIn("prevTrack.selectInEditor ();", source)
        self.assertIn("nextTrack.selectInEditor ();", source)

    def test_page_buttons_are_not_used_as_track_move_controls(self):
        left = (JAVA / "controller/ableton/push/command/trigger/PageLeftCommand.java").read_text(encoding="utf-8")
        right = (JAVA / "controller/ableton/push/command/trigger/PageRightCommand.java").read_text(encoding="utf-8")
        self.assertIn("selectPreviousPage ()", left)
        self.assertIn("selectNextPage ()", right)
        self.assertNotIn("swapWithPrevious", left)
        self.assertNotIn("swapWithNext", right)


if __name__ == "__main__":
    unittest.main()
