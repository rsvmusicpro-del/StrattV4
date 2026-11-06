#!/usr/bin/env python3
"""Regression tests for Push 1 encoder touch ownership routing."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_encoder_touch.py"

COMMAND = """package de.mossgrabers.framework.command.trigger.mode;
import de.mossgrabers.framework.featuregroup.IMode;
import de.mossgrabers.framework.utils.ButtonEvent;
public class KnobRowTouchModeCommand {
    private final int index;
    public void execute (final ButtonEvent event, final int velocity)
    {
        final IMode m = this.surface.getModeManager ().getActive ();
        if (m != null && event != ButtonEvent.LONG)
            m.onKnobTouch (this.index, event == ButtonEvent.DOWN);
    }
}
"""


class Push1EncoderTouchTests(unittest.TestCase):
    def test_release_is_delivered_to_touch_down_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/framework/command/trigger/mode"
            root.mkdir(parents=True)
            (root / "KnobRowTouchModeCommand.java").write_text(COMMAND, encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                                    check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            command = (root / "KnobRowTouchModeCommand.java").read_text(encoding="utf-8")
            owner = (root / "KnobTouchOwner.java").read_text(encoding="utf-8")
            self.assertIn("this.touchOwner.begin (activeMode)", command)
            self.assertIn("this.touchOwner.end ()", command)
            self.assertIn("touchOwner.onKnobTouch (this.index, false)", command)
            self.assertIn("public boolean begin", owner)
            self.assertIn("public T end", owner)


if __name__ == "__main__":
    unittest.main()
