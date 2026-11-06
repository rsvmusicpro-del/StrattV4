#!/usr/bin/env python3
"""Regression checks for the Push 1 track/group reorder gesture."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"


class Push1TrackReorderTests(unittest.TestCase):
    def test_select_arrows_are_limited_to_session_view_without_shift(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        left = source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right = source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        gesture = (
            "this.surface.isSelectPressed () && !this.surface.isShiftPressed () "
            "&& this.surface.getViewManager ().isActive (Views.SESSION)"
        )
        self.assertIn(gesture, left)
        self.assertIn(gesture, right)
        self.assertNotIn("Modes.TRACK", left)
        self.assertNotIn("Modes.TRACK", right)

    def test_both_directions_require_an_existing_top_level_cursor_track(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        left = source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right = source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        for section, direction in ((left, "Previous"), (right, "Next")):
            with self.subTest(direction=direction):
                self.assertIn("cursorTrack != null", section)
                self.assertIn("cursorTrack.doesExist ()", section)
                self.assertIn("!cursorTrack.hasParent ()", section)
                self.assertIn(f"cursorTrack.canSelect{direction} ()", section)
                self.assertIn(f"cursorTrack.swapWith{direction} ()", section)

    def test_arrow_leds_use_the_same_session_select_gesture_and_parent_guard(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        update = source[source.index("protected void updateArrowStates"):]
        self.assertIn("!this.surface.isShiftPressed ()", update)
        self.assertIn("this.surface.getViewManager ().isActive (Views.SESSION)", update)
        self.assertIn("!cursorTrack.hasParent ()", update)
        self.assertIn("this.canScrollLeft = canMove && cursorTrack.canSelectPrevious ();", update)
        self.assertIn("this.canScrollRight = canMove && cursorTrack.canSelectNext ();", update)

    def test_normal_and_shift_track_navigation_are_preserved(self):
        source = (JAVA / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        for token in (
            "trackBank.selectPreviousItem ()",
            "trackBank.selectNextItem ()",
            "trackBank.selectPreviousPage ()",
            "trackBank.selectNextPage ()",
        ):
            self.assertIn(token, source)

    def test_cursor_track_moves_tracks_using_bitwig_insertion_points(self):
        source = (JAVA / "bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        self.assertIn("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);", source)
        self.assertIn("this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);", source)
        self.assertIn("prevTrack.selectInEditor ();", source)
        self.assertIn("nextTrack.selectInEditor ();", source)

    def test_group_tracks_share_the_track_object_move_path(self):
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
