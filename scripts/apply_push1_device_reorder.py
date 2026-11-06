#!/usr/bin/env python3
"""Additive Shift + In/Out device reordering for Push 1 Device mode."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
TRIGGER = ROOT / "controller/ableton/push/command/trigger"


from patch_utils import replace_once



HELPER_SOURCE = r"""// Written for StrattV4.
package de.mossgrabers.controller.ableton.push.command.trigger;

import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;
import de.mossgrabers.framework.daw.IModel;
import de.mossgrabers.framework.daw.data.ICursorDevice;
import de.mossgrabers.framework.featuregroup.ModeManager;
import de.mossgrabers.framework.utils.ButtonEvent;


/**
 * Additive Shift + In/Out gesture for moving the selected device in its chain.
 */
final class Push1DeviceMoveCommand
{
    private Push1DeviceMoveCommand ()
    {
        // Utility class.
    }


    /**
     * Execute the device-move gesture when Shift is held in Device mode.
     *
     * @param model The DAW model
     * @param surface The Push control surface
     * @param event The button event
     * @param moveLeft True to move one position left, false to move right
     * @return True if this gesture owns the event and normal In/Out navigation must not run
     */
    static boolean executeIfRequested (final IModel model, final PushControlSurface surface, final ButtonEvent event, final boolean moveLeft)
    {
        if (!surface.isShiftPressed ())
            return false;

        final ModeManager modeManager = surface.getModeManager ();
        if (!Push1NavigationContext.isDeviceNavigationMode (modeManager))
            return false;

        if (event == ButtonEvent.DOWN)
        {
            final ICursorDevice cursorDevice = model.getCursorDevice ();
            if (cursorDevice.doesExist ())
            {
                if (moveLeft && cursorDevice.canSelectPrevious ())
                    cursorDevice.swapWithPrevious ();
                else if (!moveLeft && cursorDevice.canSelectNext ())
                    cursorDevice.swapWithNext ();
            }
        }

        // Consume the complete chord, including at either end of the chain.
        return true;
    }
}
"""


def patch_page_command(command_name: str, move_left: bool) -> None:
    path = TRIGGER / f"{command_name}.java"
    source = path.read_text(encoding="utf-8")
    anchor = """    public void execute (final ButtonEvent event, final int velocity)
    {
"""
    call = (
        "        if (Push1DeviceMoveCommand.executeIfRequested (this.model, this.surface, event, "
        + ("true" if move_left else "false")
        + "))\n"
        "            return;\n\n"
    )
    source = replace_once(
        source,
        anchor,
        anchor + call,
        f"{command_name} additive Shift + In/Out device move",
    )
    path.write_text(source, encoding="utf-8")


helper_path = TRIGGER / "Push1DeviceMoveCommand.java"
if helper_path.exists():
    raise SystemExit(f"Refusing to overwrite an existing source: {helper_path}")
helper_path.write_text(HELPER_SOURCE, encoding="utf-8")

patch_page_command("PageLeftCommand", True)
patch_page_command("PageRightCommand", False)

print("StrattV4 additive device reorder applied: Shift + In/Out moves the selected device by one position.")
