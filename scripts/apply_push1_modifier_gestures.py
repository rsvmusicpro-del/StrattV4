#!/usr/bin/env python3
"""Latch Select/Delete modifiers for complete Push 1 command gestures."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
TRIGGER = ROOT / "controller/ableton/push/command/trigger"


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


def patch_select_clear(command_name: str, clear_call: str, field_name: str) -> None:
    path = TRIGGER / f"{command_name}.java"
    source = path.read_text(encoding="utf-8")
    declaration = f"public class {command_name} extends AbstractTriggerCommand<PushControlSurface, PushConfiguration>\n{{\n"
    source = replace_once(
        source,
        declaration,
        declaration + f"    private boolean {field_name};\n\n",
        f"{command_name} Select gesture field",
    )
    source = replace_once(
        source,
        """        // Update for key combinations
        this.surface.getViewManager ().getActive ().updateNoteMapping ();

        if (this.surface.isSelectPressed ())
        {
            if (event == ButtonEvent.UP)
                this.model.getProject ().CLEAR_CALL ();
            return;
        }
""".replace("CLEAR_CALL", clear_call),
        """        // Update for key combinations
        this.surface.getViewManager ().getActive ().updateNoteMapping ();

        if (event == ButtonEvent.DOWN)
            this.FIELD = this.surface.isSelectPressed ();

        if (this.FIELD)
        {
            if (event == ButtonEvent.UP)
            {
                this.model.getProject ().CLEAR_CALL ();
                this.FIELD = false;
            }
            return;
        }
""".replace("FIELD", field_name).replace("CLEAR_CALL", clear_call),
        f"{command_name} latched Select clear gesture",
    )
    if source.count(f"this.{field_name} = this.surface.isSelectPressed ();") != 1:
        raise SystemExit(f"{command_name}: Select modifier is not captured exactly once")
    path.write_text(source, encoding="utf-8")


patch_select_clear("MuteCommand", "clearMute", "clearMuteGesture")
patch_select_clear("SoloCommand", "clearSolo", "clearSoloGesture")

automation_path = TRIGGER / "PushAutomationCommand.java"
automation = automation_path.read_text(encoding="utf-8")
automation = replace_once(
    automation,
    "public class PushAutomationCommand extends AbstractTriggerCommand<PushControlSurface, PushConfiguration>\n{\n",
    "public class PushAutomationCommand extends AbstractTriggerCommand<PushControlSurface, PushConfiguration>\n{\n"
    "    private boolean resetAutomationGesture;\n",
    "Automation Delete gesture state",
)
automation = replace_once(
    automation,
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        if (this.surface.isDeletePressed ())
        {
            this.surface.setTriggerConsumed (ButtonID.DELETE);
            if (event == ButtonEvent.DOWN)
                this.model.getTransport ().resetAutomationOverrides ();
            return;
        }

        switch (event)
""",
    """    public void execute (final ButtonEvent event, final int velocity)
    {
        if (event == ButtonEvent.DOWN)
            this.resetAutomationGesture = this.surface.isDeletePressed ();

        if (this.resetAutomationGesture)
        {
            if (event == ButtonEvent.DOWN)
            {
                this.surface.setTriggerConsumed (ButtonID.DELETE);
                this.model.getTransport ().resetAutomationOverrides ();
            }
            if (event == ButtonEvent.UP)
                this.resetAutomationGesture = false;
            return;
        }

        switch (event)
""",
    "Automation latched Delete gesture",
)
if "if (this.surface.isDeletePressed ())" in automation[automation.index("public void execute"):automation.index("private void doCommand")]:
    raise SystemExit("Automation still samples Delete throughout the gesture")
automation_path.write_text(automation, encoding="utf-8")
print("Push 1 Select + Mute/Solo and Delete + Automation modifiers are now latched at button-down.")
