#!/usr/bin/env python3
"""Regression checks for all Push 1 relative encoders and live VU meter setup."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_all_encoder_vu.py"

KNOB = """            if (parameter instanceof final ParameterImpl param)
            {
                target = param.getParameter ();
                HwUtils.enableObservers (true, this.hardwareKnob, param);
            }
    public void handleValue (final double value)
    {
        if (this.command == null)
            return;
        this.command.execute (1);
    }
    private void handleSimpleParameterValue (final double value)
    {
        if (this.parameter == null)
            return;
        this.parameter.changeValue (1);
    }
"""

CONFIG = """        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });

        this.isSettingActive.add (ENABLE_VU_METERS);
"""

class Push1AllEncoderVUTests(unittest.TestCase):
    def test_patch_gates_command_path_preserves_native_binding_and_initializes_vu(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"
            knob = root / "bitwig/framework/hardware/HwRelativeKnobImpl.java"
            config = root / "framework/configuration/AbstractConfiguration.java"
            knob.parent.mkdir(parents=True)
            config.parent.mkdir(parents=True)
            knob.write_text(KNOB, encoding="utf-8")
            config.write_text(CONFIG, encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                                    check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            patched_knob = knob.read_text(encoding="utf-8")
            self.assertEqual(patched_knob.count("this.touchCommand != null && !this.isTouched ()"), 1)
            self.assertIn("target = param.getParameter ();", patched_knob)
            self.assertNotIn("target = this.touchCommand == null ? param.getParameter () : this.defaultSimpleParameterAction;", patched_knob)
            self.assertIn("this.command.execute (1);", patched_knob)
            self.assertIn("this.parameter.changeValue (1);", patched_knob)

            patched_config = config.read_text(encoding="utf-8")
            self.assertIn('this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());', patched_config)

    def test_upstream_push1_modes_render_live_vu_and_glyph_patch_preserves_bars(self):
        root = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
        volume = (root / "controller/ableton/push/mode/track/VolumeMode.java").read_text(encoding="utf-8")
        track = (root / "controller/ableton/push/mode/track/TrackMode.java").read_text(encoding="utf-8")
        channel = (root / "bitwig/framework/daw/data/ChannelImpl.java").read_text(encoding="utf-8")
        french = (root / "controller/ableton/push/controller/Push1French.java").read_text(encoding="utf-8")
        self.assertIn("Push1Display.formatValue (t.getVolume (), t.getVu (), upperBound)", volume)
        self.assertIn("Push1Display.formatValue (t.getVolume (), t.getVu (), upperBound)", track)
        self.assertIn("channel.addVuMeterObserver (MAX_RESOLUTION, 0, true, this::handleVULeftMeter);", channel)
        self.assertIn("channel.addVuMeterObserver (MAX_RESOLUTION, 1, true, this::handleVURightMeter);", channel)
        for code in ("0x03", "0x04", "0x05", "0x06"):
            self.assertIn(code, french)


if __name__ == "__main__":
    unittest.main()
