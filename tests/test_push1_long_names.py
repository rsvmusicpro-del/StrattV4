#!/usr/bin/env python3
"""Regression tests for one-line, dot-marked Push 1 long-name rendering."""

from pathlib import Path
import sys
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from patch_manifest import PATCH_STEPS

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push")
DISPLAY = ROOT / "controller/Push1Display.java"
TRACKS = ROOT / "mode/track/AbstractTrackMode.java"
SESSION = ROOT / "mode/SessionMode.java"
DETAILS = ROOT / "mode/track/TrackDetailsMode.java"
LAYERS = ROOT / "mode/device/DeviceLayerMode.java"
LAYER_DETAILS = ROOT / "mode/device/DeviceLayerDetailsMode.java"
BROWSER = ROOT / "mode/device/DeviceBrowserMode.java"
NOTE_MODE = ROOT / "mode/NoteViewSelectMode.java"
PATCHER = Path("scripts/apply_push1_palette_transactional.py")


def fit_text(value: str, width: int) -> str:
    """Reference behavior for the Java Push1Display.fitText contract."""
    if not value or width <= 0:
        return ""
    value = value.rstrip()
    if len(value) <= width:
        return value
    if width == 1:
        return "."
    return value[:width - 1] + "."


class Push1LongNameDisplayTests(unittest.TestCase):
    def test_fit_text_boundaries_and_dot(self):
        cases = (
            ("Short", 8, "Short"),
            ("12345678", 8, "12345678"),
            ("123456789", 8, "1234567."),
            ("12345678901234567", 17, "12345678901234567"),
            ("123456789012345678", 17, "1234567890123456."),
            ("Long clip name", 9, "Long cli."),
            ("Long clip name", 8, "Long cl."),
            ("12345678   ", 8, "12345678"),
            (">SEQUENCER", 8, ">SEQUEN."),
            ("123456789", 1, "."),
        )
        for source, width, expected in cases:
            with self.subTest(source=source, width=width):
                self.assertEqual(fit_text(source, width), expected)
                self.assertLessEqual(len(fit_text(source, width)), width)

    def test_note_mode_labels_are_uppercase_and_dot_truncated(self):
        labels = (
            ("Play", "PLAY"),
            ("Chords", "CHORDS"),
            ("Piano", "PIANO"),
            ("Drum", "DRUM"),
            ("Drum 64", "DRUM 64"),
            ("Sequencer", "SEQUENC."),
            ("Poly Seq.", "POLY SE."),
            ("SMART", "SMART"),
            ("CHEAT", "CHEAT"),
        )
        for source, expected in labels:
            with self.subTest(source=source):
                self.assertEqual(fit_text(source.upper(), 8), expected)
                self.assertLessEqual(len(fit_text(source.upper(), 8)), 8)
        self.assertEqual(fit_text(">SEQUENCER", 8), ">SEQUEN.")
        self.assertEqual(fit_text(">POLY SEQ.", 8), ">POLY S.")

    def test_note_mode_java_formatter_preserves_translation_then_uppercases(self):
        patch = Path("scripts/apply_push1_long_names.py").read_text(encoding="utf-8")
        self.assertIn("public static String fitModeName (final String value, final int width)", patch)
        self.assertIn("return fitText (value, width, true);", patch)
        self.assertIn("Push1French.translate (value)", patch)
        self.assertIn("text.toUpperCase (java.util.Locale.ROOT)", patch)
        self.assertIn("Push1Display.fitModeName", patch)
        self.assertNotIn('NAME_SEQUENCER      = "SEQUENCER"', patch)

    def test_java_display_owns_final_cell_and_block_truncation(self):
        source = DISPLAY.read_text(encoding="utf-8")
        self.assertIn("public static String fitText (final String value, final int width)", source)
        self.assertIn("public static String fitModeName (final String value, final int width)", source)
        self.assertIn("fitText (value, 17)", source)
        self.assertIn("fitText (value, 8)", source)
        self.assertIn('text.substring (0, width - 1) + "."', source)
        self.assertIn("Push1French.toAscii (Push1French.translate (value))", source)

    def test_final_formatter_handles_null_and_invalid_widths_in_java(self):
        source = Path("scripts/apply_push1_long_names.py").read_text(encoding="utf-8")
        self.assertIn("if (value == null || value.isEmpty () || width <= 0)", source)
        self.assertIn("if (width == 1)", source)
        self.assertIn("return \".\";", source)
        self.assertIn("stripTrailing ()", source)
        self.assertIn("Push1French.toAscii (Push1French.translate (value))", source)

    def test_every_physical_text_output_uses_the_final_formatter(self):
        source = Path("scripts/apply_push1_long_names.py").read_text(encoding="utf-8")
        self.assertIn("final String fitted = fitText (value, 17);", source)
        self.assertIn("StringUtils.pad (fitText (value, 8), 8, ' ')", source)
        self.assertIn("text.toUpperCase (java.util.Locale.ROOT)", source)
        french = Path("scripts/apply_push1_french.py").read_text(encoding="utf-8")
        self.assertIn("Push1French.toAscii (text)", french)
        self.assertIn("StringUtils.asciiToHex (Push1French.toAscii (text))", french)
        self.assertIn("c == 0x7F || c == 0x02 || c == 0x07 || c == 0x03 || c == 0x04 || c == 0x05 || c == 0x06 || c == 0x09 || c == 0x18 || c == 0x1E", french)
        self.assertIn("else if (c < 0x20)", french)
        self.assertIn("ascii.append (' ')", french)
        self.assertIn("// Preserve Push 1 selection, group, folder, value-bar, degree and arrow glyphs.", french)

    def test_group_open_closed_and_selection_glyphs_survive_ascii_conversion(self):
        french = Path("scripts/apply_push1_french.py").read_text(encoding="utf-8")
        self.assertIn("c == 0x7F || c == 0x02 || c == 0x07 || c == 0x03 || c == 0x04 || c == 0x05 || c == 0x06 || c == 0x09 || c == 0x18 || c == 0x1E", french)
        self.assertIn("value-bar, degree and arrow glyphs", french)
        self.assertIn("else if (c < 0x20)", french)
        track = TRACKS.read_text(encoding="utf-8")
        self.assertIn("trackName = (t.isGroupExpanded () ? Push1Display.THREE_ROWS : Push1Display.FOLDER) + trackName;", track)
        self.assertIn("d.setCell (3, i, isSel ? Push1Display.SELECT_ARROW + n.stripLeading () : n);", track)

    def test_push1_meter_and_display_control_glyphs_survive_ascii_conversion(self):
        french = Path("scripts/apply_push1_french.py").read_text(encoding="utf-8")
        # Push1Display uses these control codes for bars, degree, arrows,
        # selection and group/folder indicators. They must not become spaces.
        preserved = (0x7F, 0x02, 0x07, 0x03, 0x04, 0x05, 0x06, 0x09, 0x18, 0x1E)
        condition = next(line for line in french.splitlines() if "if (c == 0x7F" in line)
        for code in preserved:
            with self.subTest(code=code):
                self.assertIn(f"0x{code:02X}", condition)
        self.assertIn("ascii.append (c);", french)
        self.assertIn("else if (c < 0x20)", french)

    def test_track_clip_layer_and_browser_names_are_not_pretruncated(self):
        track = TRACKS.read_text(encoding="utf-8")
        session = SESSION.read_text(encoding="utf-8")
        layers = LAYERS.read_text(encoding="utf-8")
        layer_details = LAYER_DETAILS.read_text(encoding="utf-8")
        browser = BROWSER.read_text(encoding="utf-8")
        self.assertIn("String trackName = t.getName ().stripLeading ();", track)
        self.assertIn("final String n = trackName;", track)
        self.assertIn("d.setCell (3, i, isSel ? Push1Display.SELECT_ARROW + n.stripLeading () : n);", track)
        self.assertIn("n.stripLeading ()", track)
        self.assertNotIn("fitTrackName", track)
        self.assertEqual(track.count("d.setCell (3, i,"), 1)
        self.assertNotIn("shortenAndFixASCII (trackName", track)
        self.assertIn("slot.getName (128)", session)
        self.assertIn("scene.getName (128)", session)
        self.assertIn("final String n = scene.getName (128);", session)
        self.assertIn("display.setCell (row, col, isSel ? Push1Display.SELECT_ARROW + n : n);", session)
        self.assertIn("display.setCell (row, col, Push1Display.fitText (name, 8));", session)
        self.assertNotIn("display.setCell (row, col, name);", session)
        self.assertNotIn("shortenAndFixASCII (name, 8)", session)
        self.assertIn("final String n = layer.getName ();", layers)
        self.assertIn("display.setBlock (0, 0, firstBlock);", layer_details)
        self.assertNotIn("firstBlock.substring (17)", layer_details)
        self.assertIn("Push1Display.fitText", browser)
        self.assertIn("display.setBlock (3, 2, selectedResult);", browser)
        self.assertNotIn("shortenAndFixASCII (column.get ().getName (), 8)", browser)
        self.assertNotIn("selectedResult.substring (17)", browser)
        self.assertNotIn("setCell (3, 6, sel2)", browser)

    def test_track_details_does_not_continue_name_in_adjacent_block(self):
        source = DETAILS.read_text(encoding="utf-8")
        self.assertIn("display.setBlock (0, 0, firstBlock);", source)
        self.assertNotIn("firstBlock.substring (17)", source)
        self.assertNotIn("display.setBlock (0, 1, firstBlock", source)

    def test_note_mode_names_reach_final_single_line_cell_fitter(self):
        patch = Path("scripts/apply_push1_long_names.py").read_text(encoding="utf-8")
        self.assertIn('value = Push1Display.fitModeName ((viewManager.isActive (VIEWS[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);', patch)
        self.assertIn('value = Push1Display.fitModeName ((viewManager.isActive (VIEWS_TOP[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);', patch)
        self.assertIn('"DrivenByMoss triangle selection marker in Note View first row"', patch)
        self.assertIn('"DrivenByMoss triangle selection marker in Note View second row"', patch)
        self.assertIn("if note_mode.count (\"Push1Display.SELECT_ARROW\") != 2 or '? \"O\" : \"\"' in note_mode:", patch)
        self.assertIn('if "StringUtils.optimizeName (view.getName (), 8)" in note_mode:', patch)
        self.assertIn('if note_mode.count ("Push1Display.fitModeName") != 2:', patch)
        self.assertIn("text.toUpperCase (java.util.Locale.ROOT)", patch)

    def test_note_view_has_one_driven_by_moss_triangle_marker_per_row(self):
        source = NOTE_MODE.read_text(encoding="utf-8")
        self.assertIn('value = Push1Display.fitModeName ((viewManager.isActive (VIEWS[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);', source)
        self.assertIn('value = Push1Display.fitModeName ((viewManager.isActive (VIEWS_TOP[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);', source)
        self.assertEqual(source.count("Push1Display.SELECT_ARROW"), 2)
        self.assertNotIn('? "O" : ""', source)
        self.assertNotIn("StringUtils", source)

    def test_long_name_patch_runs_inside_transactional_staging(self):
        patch_names = tuple(step.script for step in PATCH_STEPS)
        self.assertIn("apply_push1_long_names.py", patch_names)
        self.assertLess(patch_names.index("apply_push1_french.py"), patch_names.index("apply_push1_long_names.py"))


if __name__ == "__main__":
    unittest.main()
