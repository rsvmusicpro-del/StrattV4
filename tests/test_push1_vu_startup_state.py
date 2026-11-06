#!/usr/bin/env python3
"""Tests for startup synchronization of the Push VU-meter setting."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_vu_startup_state.py"

SOURCE = """    protected void activateEnableVUMetersSetting (final ISettingsUI settingsUI, final String category)
    {
        this.enableVUMetersSetting = settingsUI.getEnumSetting ("VU Meters", category, ON_OFF_OPTIONS, ON_OFF_OPTIONS[1]);
        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });

        this.isSettingActive.add (ENABLE_VU_METERS);
    }
"""


class Push1VUStartupStateTests(unittest.TestCase):
    def test_startup_value_is_read_once_without_changing_observer_behavior(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/configuration/AbstractConfiguration.java"
            )
            path.parent.mkdir(parents=True)
            path.write_text(SOURCE, encoding="utf-8")
            subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                           check=True, capture_output=True, text=True)
            patched = path.read_text(encoding="utf-8")
            self.assertIn('this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());', patched)
            self.assertEqual(patched.count('this.enableVUMeters = "On".equals (value);'), 1)
            self.assertEqual(patched.count('this.notifyObservers (ENABLE_VU_METERS);'), 1)
            self.assertLess(patched.index("addValueObserver"), patched.index("this.enableVUMetersSetting.get ()"))
            self.assertLess(patched.index("this.enableVUMetersSetting.get ()"), patched.index("this.isSettingActive.add"))

    def test_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/configuration/AbstractConfiguration.java"
            )
            path.parent.mkdir(parents=True)
            path.write_text(SOURCE, encoding="utf-8")
            for _ in range(2):
                subprocess.run([sys.executable, "-B", str(PATCH)], cwd=temporary,
                               check=True, capture_output=True, text=True)
            patched = path.read_text(encoding="utf-8")
            self.assertEqual(patched.count('this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());'), 1)


if __name__ == "__main__":
    unittest.main()
