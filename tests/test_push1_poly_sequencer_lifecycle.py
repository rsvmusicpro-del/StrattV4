#!/usr/bin/env python3
"""Regression checks for Poly Sequencer transient editing-state cleanup."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_poly_sequencer_lifecycle.py"


class Push1PolySequencerLifecycleTests(unittest.TestCase):
    def test_patch_clears_note_memory_copy_source_and_timestamp(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/view/sequencer/AbstractPolySequencerView.java"
            )
            source.parent.mkdir(parents=True)
            source.write_text(
                "public class AbstractPolySequencerView\n{\n"
                "    protected final Map<Integer, Integer> noteMemory = new HashMap<> ();\n"
                "    protected int copyStep = -1;\n"
                "    protected long lastPressedNoteTime = 0;\n"
                "    protected AbstractPolySequencerView ()\n    {\n"
                "        tb.addSelectionObserver ( (index, isSelected) -> this.keyManager.clearPressedKeys ());\n"
                "    }\n"
                "    /** {@inheritDoc} */\n"
                "    @Override\n"
                "    public void onOctaveDown (final ButtonEvent event)\n    {\n    }\n"
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
            self.assertIn("this.noteMemory.clear ();", patched)
            self.assertIn("this.copyStep = -1;", patched)
            self.assertIn("this.lastPressedNoteTime = 0;", patched)

    def test_patch_rejects_ambiguous_source_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "framework/view/sequencer/AbstractPolySequencerView.java"
            )
            source.parent.mkdir(parents=True)
            source.write_text("not the pinned source", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_text(encoding="utf-8"), "not the pinned source")


if __name__ == "__main__":
    unittest.main()
