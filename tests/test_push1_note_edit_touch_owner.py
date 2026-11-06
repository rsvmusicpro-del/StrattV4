#!/usr/bin/env python3
"""Structural regression checks for Note Mode touch-session ownership."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "apply_push1_note_edit_touch_owner.py"


class Push1NoteEditTouchOwnerPatchTests(unittest.TestCase):
    def test_patch_captures_original_clip_and_cleans_up_on_deactivation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "vendor/DrivenByMoss/src/main/java/de/mossgrabers"
            mode = root / "controller/ableton/push/mode/NoteMode.java"
            mode.parent.mkdir(parents=True)
            mode.write_text(
                "import de.mossgrabers.framework.mode.NoteEditor;\n"
                "public class NoteMode\n{\n"
                "    private final NoteEditor                    noteEditor         = new NoteEditor ();\n"
                "    /** {@inheritDoc} */\n"
                "    @Override\n"
                "    public void onKnobTouch (final int index, final boolean isTouched)\n"
                "    {\n"
                "        final List<NotePosition> notes = this.noteEditor.getNotes ();\n"
                "        if (notes.isEmpty ())\n            return;\n\n"
                "        if (isTouched && this.surface.isDeletePressed ())\n"
                "        {\n"
                "            this.surface.setTriggerConsumed (ButtonID.DELETE);\n"
                "            this.defaultParameterProvider.get (index).resetValue ();\n"
                "            return;\n"
                "        }\n\n"
                "        final INoteClip clip = this.noteEditor.getClip ();\n"
                "        if (isTouched)\n            clip.startEdit (notes);\n"
                "        else\n            clip.stopEdit ();\n"
                "    }\n}\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            patched = mode.read_text(encoding="utf-8")
            self.assertIn("NoteEditTouchOwner<INoteClip>", patched)
            self.assertIn("this.editTouchOwner.begin (index, this.noteEditor.getClip ())", patched)
            self.assertIn("this.editTouchOwner.end (index)", patched)
            self.assertIn("this.editTouchOwner.clear ()", patched)
            self.assertIn("editOwner.stopEdit ();", patched)
            self.assertIn("this.deleteTouches[index] = true;", patched)
            self.assertIn("super.onDeactivate ();", patched)

    def test_patch_rejects_unexpected_mode_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            mode = Path(temporary) / (
                "vendor/DrivenByMoss/src/main/java/de/mossgrabers/"
                "controller/ableton/push/mode/NoteMode.java"
            )
            mode.parent.mkdir(parents=True)
            mode.write_text("unexpected", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(PATCH)],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(mode.read_text(encoding="utf-8"), "unexpected")


if __name__ == "__main__":
    unittest.main()
