#!/usr/bin/env python3
"""Regression tests for the Push 1 Master volume bar/position marker."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_master_display.py"

SOURCE = """package de.mossgrabers.controller.ableton.push.mode.track;

import de.mossgrabers.framework.controller.display.Format;

public class MasterMode
{
    public void updateDisplay1 (final ITextDisplay display)
    {
        final IMasterTrack master = this.model.getMasterTrack ();
        display.setCell (2, 0, this.surface.getConfiguration ().isEnableVUMeters () ? master.getVu () : master.getVolume (), Format.FORMAT_VALUE);
        display.setCell (2, 1, master.getPan (), Format.FORMAT_PAN);
    }

    public void updateDisplay2 (final IGraphicDisplay display)
    {
        display.addChannelElement ("Volume", false, master.getName (), ChannelType.MASTER,
            master.getVolume (), master.getModulatedVolume (), master.getVuLeft (), master.getVuRight ());
    }
}
"""


class Push1MasterDisplayTests(unittest.TestCase):
    def test_patch_restores_volume_marker_over_vu_and_preserves_other_master_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            master = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "controller/ableton/push/mode/track/MasterMode.java"
            )
            master.parent.mkdir(parents=True)
            master.write_text(SOURCE, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            patched = master.read_text(encoding="utf-8")
            self.assertIn("import de.mossgrabers.controller.ableton.push.controller.Push1Display;", patched)
            self.assertIn("Push1Display.formatValue (master.getVolume (), master.getVu (), upperBound)", patched)
            self.assertIn("Push1Display.formatValue (master.getVolume (), upperBound)", patched)
            self.assertIn("display.setCell (2, 1, master.getPan (), Format.FORMAT_PAN);", patched)
            self.assertIn("master.getModulatedVolume ()", patched)
            self.assertIn("master.getVuLeft ()", patched)
            self.assertIn("master.getVuRight ()", patched)

    def test_patch_is_idempotent_and_rejects_unknown_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            master = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "controller/ableton/push/mode/track/MasterMode.java"
            )
            master.parent.mkdir(parents=True)
            master.write_text(SOURCE, encoding="utf-8")
            for _ in range(2):
                result = subprocess.run(
                    [sys.executable, "-B", str(PATCH)],
                    cwd=temporary, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            patched = master.read_text(encoding="utf-8")
            self.assertEqual(patched.count("Push1Display.formatValue (master.getVolume (), master.getVu (), upperBound)"), 1)
            self.assertEqual(patched.count("Push1Display.formatValue (master.getVolume (), upperBound)"), 1)

if __name__ == "__main__":
    unittest.main()
