#!/usr/bin/env python3
"""Regression tests for the Push 1 SELECT + NEW scene-copy mapping."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_new_scene.py"


class Push1NewSceneTests(unittest.TestCase):
    def test_select_new_creates_scene_and_preserves_plain_and_shifted_new(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/command/trigger/clip/NewCommand.java"
            )
            command.parent.mkdir(parents=True)
            original = (
                "    public void execute ()\n"
                "    {\n"
                "        this.handleExecute (true);\n"
                "    }\n"
                "    public void executeNormal (final ButtonEvent event)\n"
                "    {\n"
                "        if (event == ButtonEvent.UP)\n"
                "            this.handleExecute (true);\n"
                "    }\n"
                "    public void executeShifted (final ButtonEvent event)\n"
                "    {\n"
                "        if (event == ButtonEvent.UP)\n"
                "            this.handleExecute (false);\n"
                "    }\n"
            )
            command.write_text(original, encoding="utf-8")

            subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                check=True,
                capture_output=True,
                text=True,
            )

            patched = command.read_text(encoding="utf-8")
            self.assertIn("if (this.surface.isSelectPressed ())", patched)
            self.assertIn("this.model.getProject ().createSceneFromPlayingLauncherClips ();", patched)
            self.assertIn("this.handleExecute (true);", patched)
            self.assertIn("this.handleExecute (false);", patched)
            self.assertIn("if (event != ButtonEvent.UP)", patched)


if __name__ == "__main__":
    unittest.main()
