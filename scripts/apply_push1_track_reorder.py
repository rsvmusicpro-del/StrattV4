#!/usr/bin/env python3
"""Additive Select + Left/Right track and group reordering for Push 1."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
TRIGGER = ROOT / "controller/ableton/push/command/trigger"


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


HELPER_SOURCE = r"""// Written for StrattV4.
package de.mossgrabers.controller.ableton.push.command.trigger;

import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;
import de.mossgrabers.framework.daw.IModel;
import de.mossgrabers.framework.daw.data.ICursorTrack;
import de.mossgrabers.framework.view.Views;


/**
 * Additive Select + Left/Right gesture for reordering top-level tracks and groups.
 */
final class Push1TrackMoveCommand
{
    private Push1TrackMoveCommand ()
    {
        // Utility class.
    }


    /**
     * True only for the new chord in Session view. Shift remains reserved for native paging.
     *
     * @param surface The Push control surface
     * @return True if the track-move chord is active
     */
    static boolean isGestureActive (final PushControlSurface surface)
    {
        return surface.isSelectPressed () && !surface.isShiftPressed () && surface.getViewManager ().isActive (Views.SESSION);
    }


    /**
     * Execute one adjacent track/group move when the new chord is active.
     *
     * @param model The DAW model
     * @param surface The Push control surface
     * @param moveLeft True to move one position left, false to move right
     * @return True if the chord is consumed, including when movement is not permitted
     */
    static boolean executeIfRequested (final IModel model, final PushControlSurface surface, final boolean moveLeft)
    {
        if (!isGestureActive (surface))
            return false;

        final ICursorTrack cursorTrack = model.getCursorTrack ();
        if (cursorTrack != null && cursorTrack.doesExist () && !cursorTrack.hasParent ())
        {
            if (moveLeft && cursorTrack.canSelectPrevious ())
                cursorTrack.swapWithPrevious ();
            else if (!moveLeft && cursorTrack.canSelectNext ())
                cursorTrack.swapWithNext ();
        }

        // Do not let the arrow fall through to normal track-page navigation while Select is held.
        return true;
    }
}
"""


def patch_cursor_command() -> None:
    path = TRIGGER / "PushCursorCommand.java"
    source = path.read_text(encoding="utf-8")
    source = replace_once(\n        source,\n        "import de.mossgrabers.framework.daw.IModel;\\n",\n        "import de.mossgrabers.framework.daw.IModel;\\n"\n        "import de.mossgrabers.framework.daw.data.ICursorTrack;\\n",\n        "PushCursorCommand ICursorTrack import",\n    )\n    left_anchor = """    protected void scrollLeft ()
    {
        final IMode activeMode = this.surface.getModeManager ().getActive ();
"""
    left_insert = """    protected void scrollLeft ()
    {
        if (Push1TrackMoveCommand.executeIfRequested (this.model, this.surface, true))
            return;

        final IMode activeMode = this.surface.getModeManager ().getActive ();
"""
    source = replace_once(source, left_anchor, left_insert, "PushCursorCommand left track move")
    right_anchor = """    protected void scrollRight ()
    {
        final IMode activeMode = this.surface.getModeManager ().getActive ();
"""
    right_insert = """    protected void scrollRight ()
    {
        if (Push1TrackMoveCommand.executeIfRequested (this.model, this.surface, false))
            return;

        final IMode activeMode = this.surface.getModeManager ().getActive ();
"""
    source = replace_once(source, right_anchor, right_insert, "PushCursorCommand right track move")
    state_anchor = """        this.canScrollUp = sceneBank.canScrollBackwards ();
        this.canScrollDown = sceneBank.canScrollForwards ();

        final IMode mode = this.surface.getModeManager ().getActive ();
"""
    state_insert = """        this.canScrollUp = sceneBank.canScrollBackwards ();
        this.canScrollDown = sceneBank.canScrollForwards ();

        if (Push1TrackMoveCommand.isGestureActive (this.surface))
        {
            final ICursorTrack cursorTrack = this.model.getCursorTrack ();
            final boolean canMove = cursorTrack != null && cursorTrack.doesExist () && !cursorTrack.hasParent ();
            this.canScrollLeft = canMove && cursorTrack.canSelectPrevious ();
            this.canScrollRight = canMove && cursorTrack.canSelectNext ();
            return;
        }

        final IMode mode = this.surface.getModeManager ().getActive ();
"""
    source = replace_once(source, state_anchor, state_insert, "PushCursorCommand track move arrow states")
    path.write_text(source, encoding="utf-8")


helper_path = TRIGGER / "Push1TrackMoveCommand.java"
if helper_path.exists():
    raise SystemExit(f"Refusing to overwrite an existing source: {helper_path}")
helper_path.write_text(HELPER_SOURCE, encoding="utf-8")
patch_cursor_command()

print("StrattV4 additive track reorder applied: Select + Left/Right moves a top-level track or group in Session view.")
