#!/usr/bin/env python3
"""Regression tests for Push 1 Clip Accent and Play End encoder handling."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_clip_accent.py"


class Push1ClipAccentTests(unittest.TestCase):
    def test_patch_scales_accent_and_inverts_only_play_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"
            constants = root / "framework/daw/constants/TransportConstants.java"
            clip_mode = root / "controller/ableton/push/mode/track/ClipMode.java"
            cursor_clip = root / "bitwig/framework/daw/CursorClipImpl.java"
            constants.parent.mkdir(parents=True)
            clip_mode.parent.mkdir(parents=True)
            cursor_clip.parent.mkdir(parents=True)
            constants.write_text(
                "    public static final double INC_FRACTION_ACCENT      = 1.0;\n"
                "    public static final double INC_FRACTION_ACCENT_SLOW = 1.0 / 16;\n",
                encoding="utf-8",
            )
            clip_mode.write_text(
                "        if (!this.increaseKnobMovement ())\n"
                "            return;\n\n"
                "        final IClip clip = this.model.getCursorClip ();\n",
                encoding="utf-8",
            )
            cursor_clip.write_text(
                "    public void changePlayEnd (final int control, final boolean slow)\n"
                "    {\n"
                "        final boolean increase = this.valueChanger.isIncrease (control);\n"
                "        final double frac = slow ? TransportConstants.INC_FRACTION_TIME_SLOW : TransportConstants.INC_FRACTION_TIME;\n"
                "        this.getClip ().getPlayStop ().inc (increase ? frac : -frac);\n"
                "    }\n",
                encoding="utf-8",
            )

            subprocess.run(
                [sys.executable, str(PATCH)],
                cwd=temporary,
                check=True,
                capture_output=True,
                text=True,
            )

            patched_constants = constants.read_text(encoding="utf-8")
            self.assertIn("INC_FRACTION_ACCENT      = 0.005;", patched_constants)
            self.assertIn("INC_FRACTION_ACCENT_SLOW = 0.005 / 16;", patched_constants)
            patched_mode = clip_mode.read_text(encoding="utf-8")
            self.assertIn("if (index != 7 && !this.increaseKnobMovement ())", patched_mode)

            patched_cursor = cursor_clip.read_text(encoding="utf-8")
            self.assertIn("this.getClip ().getPlayStop ().inc (increase ? -frac : frac);", patched_cursor)
            self.assertNotIn("this.getClip ().getPlayStop ().inc (increase ? frac : -frac);", patched_cursor)

    def test_display_mapping_means_one_percent_point_is_half_a_percent_normalized(self):
        # getFormattedAccent maps normalized [0, 1] to displayed [-100, 100].
        self.assertEqual(0.005 * 200, 1.0)


if __name__ == "__main__":
    unittest.main()
