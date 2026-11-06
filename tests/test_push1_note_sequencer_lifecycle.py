#!/usr/bin/env python3
"""Regression checks for Note Sequencer transient gesture cleanup."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_note_sequencer_lifecycle.py"


class Push1NoteSequencerLifecycleTests(unittest.TestCase):
    def test_patch_resets_loop_and_copy_gestures_on_track_change_and_deactivation(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/view/sequencer/AbstractNoteSequencerView.java"
            )
            source.parent.mkdir(parents=True)
            source.write_text(
                "public abstract class AbstractNoteSequencerView\n{\n"
                "    protected int loopPadPressed = -1;\n"
                "    protected IStepInfo copyNote;\n"
                "    protected AbstractNoteSequencerView ()\n    {\n"
                "        this.numDisplayCols = numDisplayCols;\n"
                "        this.offsetY = this.startKey;\n"
                "    }\n"
                "    /** {@inheritDoc} */\n"
                "    @Override\n"
                "    public void onGridNote (final int note, final int velocity)\n    {\n    }\n"
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
            patched = source.read_text(encoding="utf-8")
            self.assertIn("if (isSelected)\n                this.clearSequencerGestureState ();", patched)
            self.assertIn("public void onDeactivate ()", patched)
            self.assertIn("this.clearSequencerGestureState ();\n        super.onDeactivate ();", patched)
            self.assertIn("this.loopPadPressed = -1;", patched)
            self.assertIn("this.copyNote = null;", patched)

    def test_patch_rejects_ambiguous_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/view/sequencer/AbstractNoteSequencerView.java"
            )
            source.parent.mkdir(parents=True)
            source.write_text("unexpected source", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_text(encoding="utf-8"), "unexpected source")


if __name__ == "__main__":
    unittest.main()
