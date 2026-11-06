#!/usr/bin/env python3
"""Regression tests for reversible Push 1 encoder touch bindings."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_touch_lifecycle.py"

SOURCE = """    private int                                  control;

    public void bindTouch (final TriggerCommand command, final IMidiInput input, final BindType type, final int channel, final int control)
    {
        this.touchCommand = command;

        this.hardwareKnob.beginTouchAction ().addBinding (this.controllerHost.createAction ( () -> this.triggerTouch (true), () -> ""));
        this.hardwareKnob.endTouchAction ().addBinding (this.controllerHost.createAction ( () -> this.triggerTouch (false), () -> ""));

        input.bindTouch (this, type, channel, control);
    }

    public void unbind ()
    {
        if (this.input != null)
            this.input.unbind (this);
    }

    public void rebind ()
    {
        if (this.input != null)
            this.input.bind (this, this.type, this.channel, this.control, this.encoding);
    }
"""

class Push1TouchLifecycleTests(unittest.TestCase):
    def test_unbind_releases_touch_and_rebind_restores_both_matchers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers/bitwig/framework/hardware"
            root.mkdir(parents=True)
            target = root / "HwRelativeKnobImpl.java"
            target.write_text(SOURCE, encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                                    check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            patched = target.read_text(encoding="utf-8")
            self.assertIn("private IMidiInput                           touchInput;", patched)
            self.assertIn("this.touchInput = input;", patched)
            self.assertIn("if (this.isTouched ())\n            this.triggerTouch (false);", patched)
            self.assertIn("this.hardwareKnob.beginTouchAction ().setActionMatcher (null);", patched)
            self.assertIn("this.hardwareKnob.endTouchAction ().setActionMatcher (null);", patched)
            self.assertIn("this.touchInput.bindTouch (this, this.touchType, this.touchChannel, this.touchControl);", patched)
            self.assertIn("this.input.bind (this, this.type, this.channel, this.control, this.encoding);", patched)

if __name__ == "__main__":
    unittest.main()
