#!/usr/bin/env python3
"""Require a real touch on Push 1's two small encoders before accepting rotation."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


from patch_utils import replace_once



def patch_command(relative_path: str, class_declaration: str, execute_anchor: str,
                  execute_replacement: str, touch_anchor: str, touch_replacement: str,
                  label: str) -> None:
    path = ROOT / relative_path
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, class_declaration,
                          class_declaration + "    private boolean isKnobTouched;\n\n",
                          label + " touch state")
    source = replace_once(source, execute_anchor, execute_replacement,
                          label + " rotation guard")
    source = replace_once(source, touch_anchor, touch_replacement,
                          label + " touch handling")
    if source.count("if (!this.isKnobTouched)") != 1:
        raise SystemExit(label + ": missing unique touch guard")
    if "event != ButtonEvent.UP" not in source:
        raise SystemExit(label + ": touch release handling is missing")
    path.write_text(source, encoding="utf-8")


patch_command(
    "controller/ableton/push/command/trigger/RasteredKnobCommand.java",
    "public class RasteredKnobCommand extends TempoCommand<PushControlSurface, PushConfiguration>\n{\n",
    """    public void execute (final int value)
    {
        final ModeManager modeManager = this.surface.getModeManager ();
""",
    """    public void execute (final int value)
    {
        // The Push 1 touch sensor is the safety gate: ignore stray CC/noise
        // while the encoder is not physically touched.
        if (!this.isKnobTouched)
            return;

        final ModeManager modeManager = this.surface.getModeManager ();
""",
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        final boolean activate = event != ButtonEvent.UP;

        if (this.surface.isSelectPressed ())
        {
            if (activate)
                this.mvHelper.delayDisplay ( () -> "Loop Start: " + this.transport.getLoopStartBeatText ());
            return;
        }

        this.transport.setTempoIndication (activate);
        if (activate)
            this.mvHelper.notifyTempo ();
    }
""",
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        final boolean activate = event != ButtonEvent.UP;
        this.isKnobTouched = activate;

        if (this.surface.isSelectPressed ())
        {
            if (activate)
                this.mvHelper.delayDisplay ( () -> "Loop Start: " + this.transport.getLoopStartBeatText ());
            return;
        }

        this.transport.setTempoIndication (activate);
        if (activate)
            this.mvHelper.notifyTempo ();
    }
""",
    "Tempo encoder",
)

patch_command(
    "controller/ableton/push/command/trigger/PlayPositionKnobCommand.java",
    "public class PlayPositionKnobCommand extends PlayPositionCommand<PushControlSurface, PushConfiguration> implements TriggerCommand\n{\n",
    """    public void execute (final int value)
    {
        if (this.surface.isSelectPressed ())
""",
    """    public void execute (final int value)
    {
        // Ignore unrequested relative CC events unless the encoder is touched.
        if (!this.isKnobTouched)
            return;

        if (this.surface.isSelectPressed ())
""",
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        final boolean activate = event != ButtonEvent.UP;

        if (this.surface.isSelectPressed ())
        {
            if (activate)
                this.mvHelper.delayDisplay ( () -> "Loop Length: " + this.transport.getLoopLengthBeatText ());
            return;
        }

        if (activate)
            this.displayPosition ();
    }
""",
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        final boolean activate = event != ButtonEvent.UP;
        this.isKnobTouched = activate;

        if (this.surface.isSelectPressed ())
        {
            if (activate)
                this.mvHelper.delayDisplay ( () -> "Loop Length: " + this.transport.getLoopLengthBeatText ());
            return;
        }

        if (activate)
            this.displayPosition ();
    }
""",
    "Play Position encoder",
)

print("Push 1 small encoders now accept rotation only while physically touched.")
