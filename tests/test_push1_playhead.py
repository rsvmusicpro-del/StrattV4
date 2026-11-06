#!/usr/bin/env python3
"""Regression tests for the Push 1 Play Position encoder patch."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_playhead.py"


class Push1PlayheadTests(unittest.TestCase):
    def test_patch_removes_only_the_unrelated_tempo_touch_indication(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "controller/ableton/push/command/trigger/PlayPositionKnobCommand.java"
            )
            command.parent.mkdir(parents=True)
            original = (
                "    public void execute (final int value)\n"
                "    {\n"
                "        if (this.surface.isSelectPressed ())\n"
                "        {\n"
                "            this.transport.changeLoopLength (this.model.getValueChanger ().isIncrease (value), this.surface.isKnobSensitivitySlow ());\n"
                "            return;\n"
                "        }\n"
                "        super.execute (value);\n"
                "        this.displayPosition ();\n"
                "    }\n"
                "    public void execute (final ButtonEvent event, final int velocity)\n"
                "    {\n"
                "        final boolean activate = event != ButtonEvent.UP;\n"
                "        if (this.surface.isSelectPressed ())\n"
                "        {\n"
                "            if (activate)\n"
                "                this.mvHelper.delayDisplay ( () -> \"Loop Length: \" + this.transport.getLoopLengthBeatText ());\n"
                "            return;\n"
                "        }\n"
                "        this.transport.setTempoIndication (activate);\n"
                "        if (activate)\n"
                "            this.displayPosition ();\n"
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
            self.assertNotIn("setTempoIndication", patched)
            self.assertIn("this.transport.changeLoopLength (this.model.getValueChanger ().isIncrease (value), this.surface.isKnobSensitivitySlow ());", patched)
            self.assertIn("super.execute (value);", patched)
            self.assertIn("this.displayPosition ();", patched)
            self.assertIn("final boolean activate = event != ButtonEvent.UP;", patched)


if __name__ == "__main__":
    unittest.main()
