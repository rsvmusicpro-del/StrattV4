#!/usr/bin/env python3
"""Regression checks for Shift+arrow Push 1 track/group reordering."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"

class Push1TrackReorderTests(unittest.TestCase):
    def sections(self):
        source=(JAVA/"controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
        left=source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right=source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        return source,left,right

    def test_shift_arrows_are_the_only_reorder_gesture(self):
        _,left,right=self.sections()
        for part in (left,right):
            self.assertIn("this.surface.isShiftPressed () && this.isTrackReorderContext ()",part)
            self.assertNotIn("isSelectPressed",part)
            self.assertNotIn("Views.SESSION",part)
        self.assertIn("cursorTrack.swapWithPrevious ()",left)
        self.assertIn("cursorTrack.swapWithNext ()",right)

    def test_session_track_and_volume_contexts(self):
        source,_,_=self.sections()
        start=source.index("private boolean isTrackReorderContext ()")
        end=source.index("private boolean isScenePlay ()",start)
        context=source[start:end]
        for token in ("Views.SESSION","Modes.TRACK","Modes.VOLUME"): self.assertIn(token,context)

    def test_both_directions_check_existence_parent_and_boundary(self):
        _,left,right=self.sections()
        for part,direction in ((left,"Previous"),(right,"Next")):
            for token in ("cursorTrack != null","cursorTrack.doesExist ()","!cursorTrack.hasParent ()",f"cursorTrack.canSelect{direction} ()",f"cursorTrack.swapWith{direction} ()"):
                self.assertIn(token,part)

    def test_leds_follow_shift_move_availability(self):
        source,_,_=self.sections(); update=source[source.index("protected void updateArrowStates"):]
        for token in ("this.surface.isShiftPressed () && this.isTrackReorderContext ()","!cursorTrack.hasParent ()","this.canScrollLeft = canMove && cursorTrack.canSelectPrevious ();","this.canScrollRight = canMove && cursorTrack.canSelectNext ();"):
            self.assertIn(token,update)

    def test_unmodified_navigation_and_browser_remain(self):
        _,left,right=self.sections()
        for token in ("Modes.BROWSER","activeMode.selectPreviousItemPage ()","trackBank.selectPreviousItem ()","trackBank.selectPreviousPage ()"): self.assertIn(token,left)
        for token in ("Modes.BROWSER","activeMode.selectNextItemPage ()","trackBank.selectNextItem ()","trackBank.selectNextPage ()"): self.assertIn(token,right)

    def test_bitwig_insertion_api_and_group_track_type_remain(self):
        cursor=(JAVA/"bitwig/framework/daw/data/CursorTrackImpl.java").read_text(encoding="utf-8")
        track=(JAVA/"bitwig/framework/daw/data/TrackImpl.java").read_text(encoding="utf-8")
        for token in ("this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);","this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);","prevTrack.selectInEditor ();","nextTrack.selectInEditor ();"): self.assertIn(token,cursor)
        self.assertIn("public boolean isGroup ()",track)

    def test_page_commands_do_not_move_tracks(self):
        for name,method in (("PageLeftCommand.java","swapWithPrevious"),("PageRightCommand.java","swapWithNext")):
            self.assertNotIn(method,(JAVA/"controller/ableton/push/command/trigger"/name).read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
