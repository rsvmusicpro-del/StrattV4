#!/usr/bin/env python3
"""Regression checks for Push 1 Select/Delete modifier gesture latching."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_modifier_gestures.py"


class Push1ModifierGesturePatchTests(unittest.TestCase):
    def test_patch_latches_select_for_mute_and_solo(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push/command/trigger"
            root.mkdir(parents=True)
            for name, action, field in (
                ("MuteCommand", "clearMute", "clearMuteGesture"),
                ("SoloCommand", "clearSolo", "clearSoloGesture"),
            ):
                (root / f"{name}.java").write_text(
                    f"public class {name} extends AbstractTriggerCommand<PushControlSurface, PushConfiguration>\n{{\n"
                    "    public void execute (final ButtonEvent event, final int velocity)\n    {\n"
                    "        // Update for key combinations\n"
                    "        this.surface.getViewManager ().getActive ().updateNoteMapping ();\n\n"
                    "        if (this.surface.isSelectPressed ())\n        {\n"
                    f"            if (event == ButtonEvent.UP)\n                this.model.getProject ().{action} ();\n"
                    "            return;\n        }\n    }\n}\n",
                    encoding="utf-8",
                )
            automation = root / "PushAutomationCommand.java"
            automation.write_text(
                "public class PushAutomationCommand extends AbstractTriggerCommand<PushControlSurface, PushConfiguration>\n{\n"
                "    public void execute (final ButtonEvent event, final int velocity)\n    {\n"
                "        if (this.surface.isDeletePressed ())\n        {\n"
                "            this.surface.setTriggerConsumed (ButtonID.DELETE);\n"
                "            if (event == ButtonEvent.DOWN)\n"
                "                this.model.getTransport ().resetAutomationOverrides ();\n"
                "            return;\n        }\n\n"
                "        switch (event)\n        {\n        }\n    }\n"
                "    private void doCommand ()\n    {\n    }\n}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                check=True,
                capture_output=True,
                text=True,
            )
            for name, field in (("MuteCommand", "clearMuteGesture"), ("SoloCommand", "clearSoloGesture")):
                patched = (root / f"{name}.java").read_text(encoding="utf-8")
                self.assertIn(f"this.{field} = this.surface.isSelectPressed ();", patched)
                self.assertIn(f"if (this.{field})", patched)
                self.assertIn(f"this.{field} = false;", patched)
                self.assertNotIn("if (this.surface.isSelectPressed ())", patched)
            patched = automation.read_text(encoding="utf-8")
            self.assertIn("this.resetAutomationGesture = this.surface.isDeletePressed ();", patched)
            self.assertIn("if (this.resetAutomationGesture)", patched)
            self.assertIn("this.resetAutomationGesture = false;", patched)
            self.assertNotIn("if (this.surface.isDeletePressed ())", patched)

    def test_patch_rejects_incomplete_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push/command/trigger"
            root.mkdir(parents=True)
            for name in ("MuteCommand", "SoloCommand", "PushAutomationCommand"):
                (root / f"{name}.java").write_text("unexpected", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            for name in ("MuteCommand", "SoloCommand", "PushAutomationCommand"):
                self.assertEqual((root / f"{name}.java").read_text(encoding="utf-8"), "unexpected")


if __name__ == "__main__":
    unittest.main()
