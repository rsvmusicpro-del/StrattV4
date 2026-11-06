#!/usr/bin/env python3
"""Regression tests for Push 1 Select + NEW modifier latching."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_new_scene_gesture.py"


class Push1NewSceneGesturePatchTests(unittest.TestCase):
    def test_patch_latches_select_on_down_and_resets_after_up(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/command/trigger/clip/NewCommand.java"
            )
            command.parent.mkdir(parents=True)
            command.write_text(
                "public class NewCommand<S extends IControlSurface<C>, C extends Configuration> extends AbstractTriggerCommand<S, C>\n{\n"
                "    /** {@inheritDoc} */\n"
                "    @Override\n"
                "    public void executeNormal (final ButtonEvent event)\n"
                "    {\n"
                "        if (event != ButtonEvent.UP)\n"
                "            return;\n\n"
                "        // SELECT + NEW creates a scene from all clips currently playing in\n"
                "        // the launcher. Plain NEW and SHIFT + NEW retain their original logic.\n"
                "        if (this.surface.isSelectPressed ())\n"
                "        {\n"
                "            this.model.getProject ().createSceneFromPlayingLauncherClips ();\n"
                "            return;\n"
                "        }\n\n"
                "        this.handleExecute (true);\n"
                "    }\n"
                "    public void executeShifted (final ButtonEvent event)\n"
                "    {\n"
                "        if (event == ButtonEvent.UP)\n"
                "            this.handleExecute (false);\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                check=True,
                capture_output=True,
                text=True,
            )
            patched = command.read_text(encoding="utf-8")
            self.assertIn("this.selectGesture.begin (this.surface.isSelectPressed ());", patched)
            self.assertIn("if (this.selectGesture.wasSelectedOnPress ())", patched)
            self.assertIn("if (event == ButtonEvent.UP)\n                this.selectGesture.reset ();", patched)
            normal = patched.split("public void executeNormal", 1)[1].split("public void executeShifted", 1)[0]
            self.assertNotIn("this.surface.isSelectPressed ()", normal)
            self.assertIn("this.handleExecute (true);", normal)
            self.assertIn("this.handleExecute (false);", patched)

    def test_patch_refuses_unexpected_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/command/trigger/clip/NewCommand.java"
            )
            command.parent.mkdir(parents=True)
            command.write_text("unexpected source", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(command.read_text(encoding="utf-8"), "unexpected source")


if __name__ == "__main__":
    unittest.main()
