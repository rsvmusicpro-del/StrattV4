#!/usr/bin/env python3
"""Latch the Push 1 Select modifier for the complete NEW button gesture."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
COMMAND = ROOT / "framework/command/trigger/clip/NewCommand.java"
GESTURE = ROOT / "framework/command/trigger/clip/Push1SelectGesture.java"

GESTURE_SOURCE = """package de.mossgrabers.framework.command.trigger.clip;

/**
 * Captures the Select modifier at the start of a physical NEW-button gesture.
 */
public final class Push1SelectGesture
{
    private boolean selectedOnPress;

    public void begin (final boolean selectPressed)
    {
        this.selectedOnPress = selectPressed;
    }

    public boolean wasSelectedOnPress ()
    {
        return this.selectedOnPress;
    }

    public void reset ()
    {
        this.selectedOnPress = false;
    }
}
"""


from patch_utils import replace_once



if GESTURE.exists():
    if GESTURE.read_text(encoding="utf-8") != GESTURE_SOURCE:
        raise SystemExit("Refusing to overwrite unexpected Push1SelectGesture.java")
else:
    GESTURE.write_text(GESTURE_SOURCE, encoding="utf-8")

source = COMMAND.read_text(encoding="utf-8")
source = replace_once(
    source,
    "public class NewCommand<S extends IControlSurface<C>, C extends Configuration> extends AbstractTriggerCommand<S, C>\n{\n",
    "public class NewCommand<S extends IControlSurface<C>, C extends Configuration> extends AbstractTriggerCommand<S, C>\n{\n"
    "    private final Push1SelectGesture selectGesture = new Push1SelectGesture ();\n\n",
    "NEW Select gesture state",
)
source = replace_once(
    source,
    """    /** {@inheritDoc} */
    @Override
    public void executeNormal (final ButtonEvent event)
""",
    """    /** {@inheritDoc} */
    @Override
    public void execute (final ButtonEvent event, final int velocity)
    {
        if (event == ButtonEvent.DOWN)
            this.selectGesture.begin (this.surface.isSelectPressed ());

        try
        {
            super.execute (event, velocity);
        }
        finally
        {
            if (event == ButtonEvent.UP)
                this.selectGesture.reset ();
        }
    }


    /** {@inheritDoc} */
    @Override
    public void executeNormal (final ButtonEvent event)
""",
    "NEW gesture modifier capture",
)
old = """    public void executeNormal (final ButtonEvent event)
    {
        if (event != ButtonEvent.UP)
            return;

        // SELECT + NEW creates a scene from all clips currently playing in
        // the launcher. Plain NEW and SHIFT + NEW retain their original logic.
        if (this.surface.isSelectPressed ())
        {
            this.model.getProject ().createSceneFromPlayingLauncherClips ();
            return;
        }

        this.handleExecute (true);
    }
"""
new = """    public void executeNormal (final ButtonEvent event)
    {
        if (event != ButtonEvent.UP)
            return;

        // The modifier is latched on NEW-down, so releasing Select before NEW
        // does not cancel the intended scene-copy gesture.
        if (this.selectGesture.wasSelectedOnPress ())
        {
            this.model.getProject ().createSceneFromPlayingLauncherClips ();
            return;
        }

        this.handleExecute (true);
    }
"""
source = replace_once(source, old, new, "NEW use latched Select modifier")
if "this.surface.isSelectPressed ()" in source[source.index("public void executeNormal"):source.index("public void executeShifted")]:
    raise SystemExit("NEW still samples Select at release instead of using the gesture latch")
if "this.handleExecute (false);" not in source:
    raise SystemExit("SHIFT + NEW behavior was unexpectedly removed")
COMMAND.write_text(source, encoding="utf-8")
print("SELECT + NEW now uses the modifier state captured at button-down.")
