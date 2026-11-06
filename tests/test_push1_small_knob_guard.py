#!/usr/bin/env python3
"""Regression tests for guarded Push 1 small encoders and native touch feedback."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_small_knob_guard.py"

TEMPO = """public class RasteredKnobCommand extends TempoCommand<PushControlSurface, PushConfiguration>
{
    public void execute (final int value)
    {
        final ModeManager modeManager = this.surface.getModeManager ();
        if (modeManager.isActive (Modes.BROWSER))
            return;
        super.execute (value);
        this.mvHelper.notifyTempo ();
    }
    public void execute (final ButtonEvent event, final int velocity)
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
}
"""

PLAYHEAD = """public class PlayPositionKnobCommand extends PlayPositionCommand<PushControlSurface, PushConfiguration> implements TriggerCommand
{
    public void execute (final int value)
    {
        if (this.surface.isSelectPressed ())
        {
            this.transport.changeLoopLength (this.model.getValueChanger ().isIncrease (value), this.surface.isKnobSensitivitySlow ());
            return;
        }

        super.execute (value);
        this.displayPosition ();
    }
    public void execute (final ButtonEvent event, final int velocity)
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
}
"""


class Push1SmallKnobGuardTests(unittest.TestCase):
    def test_both_encoders_require_touch_and_preserve_native_touch_feedback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push/command/trigger"
            root.mkdir(parents=True)
            (root / "RasteredKnobCommand.java").write_text(TEMPO, encoding="utf-8")
            (root / "PlayPositionKnobCommand.java").write_text(PLAYHEAD, encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                                    check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            tempo = (root / "RasteredKnobCommand.java").read_text(encoding="utf-8")
            playhead = (root / "PlayPositionKnobCommand.java").read_text(encoding="utf-8")
            for source in (tempo, playhead):
                self.assertIn("private boolean isKnobTouched;", source)
                self.assertIn("if (!this.isKnobTouched)", source)
                self.assertIn("this.isKnobTouched = activate;", source)
                touch_method = source.split("public void execute (final ButtonEvent event, final int velocity)", 1)[1]
                touch_method = touch_method.split("\n    }", 1)[0]
                self.assertIn("this.isKnobTouched = activate;", touch_method)

            self.assertIn("this.transport.setTempoIndication (activate);", tempo)
            self.assertIn("this.mvHelper.notifyTempo ();", tempo)
            self.assertIn("Loop Start:", tempo)
            self.assertIn("this.displayPosition ();", playhead)
            self.assertIn("Loop Length:", playhead)
            self.assertIn("super.execute (value);", playhead)       # original movement mapping retained


if __name__ == "__main__":
    unittest.main()
