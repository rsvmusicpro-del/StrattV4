#!/usr/bin/env python3
"""Static regression tests for Push 1 French UI rendering."""

from pathlib import Path
import unittest

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push")
FRENCH = ROOT / "controller/Push1French.java"
DISPLAY = ROOT / "controller/Push1Display.java"
BROWSER = ROOT / "mode/device/DeviceBrowserMode.java"


class Push1FrenchDisplayTests(unittest.TestCase):
    def test_contextual_french_labels_are_present(self):
        source = FRENCH.read_text(encoding="utf-8")
        for phrase in (
            '{"Selected Device:", "Composant actif:"}',
            '{"Device Chains:", "Chaines comp.:"}',
            '{"Selection:", "Choix :"}',
            '{"Preview:", "Ecoute :"}',
            '{"Pad Threshold", "Seuil pad"}',
            '{"Velocity Curve", "Courbe velo."}',
            '{"Automation Mode:", "Mode automation:"}',
            '{"Record Quantize:", "Quantif. rec :"}',
            '{"Please select a note to edit...", "Choisir une note..."}',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)

    def test_dynamic_names_are_preserved_after_translated_prefixes(self):
        source = FRENCH.read_text(encoding="utf-8")
        self.assertIn('{"Replace:", "Remplacer :"}', source)
        self.assertIn('{"Add device to:", "Ajouter a :"}', source)
        self.assertIn('{"Insert device before:", "Inserer avant :"}', source)
        self.assertIn('{"Insert device after:", "Inserer apres :"}', source)
        # BrowserImpl keeps its dynamic selected name separate from the label.
        self.assertIn('return entry[1] + source.substring (entry[0].length ());', source)

    def test_display_translates_before_clipping_and_guards_sysex(self):
        source = DISPLAY.read_text(encoding="utf-8")
        self.assertIn("Push1French.translate (value)", source)
        self.assertIn("Push1French.toAscii (text)", source)

    def test_browser_keeps_original_encoder_logic_and_resets_offset(self):
        source = BROWSER.read_text(encoding="utf-8")
        self.assertIn("this.changeFilterColumnValue (this.filterColumn, value)", source)
        self.assertIn("public void onActivate ()", source)
        self.assertIn("this.displayColumnOffset = 0;", source)
        self.assertIn("private void changeFilterColumnValue", source)

    def test_push_payload_has_ascii_transliteration(self):
        source = FRENCH.read_text(encoding="utf-8")
        for token in (
            '.replace ("œ", "oe")',
            '.replace ("æ", "ae")',
            '.replace ("’", "\'")',
            "Normalizer.Form.NFD",
            "Character.NON_SPACING_MARK",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
