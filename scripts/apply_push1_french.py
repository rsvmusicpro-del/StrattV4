#!/usr/bin/env python3
"""Apply contextual French labels and 7-bit-safe text output to Push 1."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
DISPLAY = ROOT / "controller/ableton/push/controller/Push1Display.java"
BROWSER = ROOT / "controller/ableton/push/mode/device/DeviceBrowserMode.java"
FRENCH = ROOT / "controller/ableton/push/controller/Push1French.java"


from patch_utils import replace_once



# Reuse the upstream value changer and reset the horizontal viewport whenever
# the Browser mode is entered.
browser = BROWSER.read_text(encoding="utf-8")
encoder_routing = """        if (this.filterColumn < 0)
            this.changeValue (7, value);
        else
            this.changeFilterColumnValue (this.filterColumn, value);
"""
if browser.count (encoder_routing) != 1:
    raise SystemExit ("Browser encoder routing: expected one helper call site")
duplicate_method = """    private void changeFilterColumnValue (final int columnIndex, final int value)
    {
        int speed = this.model.getValueChanger ().calcSteppedKnobChange (value);
        final boolean direction = speed > 0;
        if (this.surface.isShiftPressed ())
            speed = speed * 4;

        speed = Math.abs (speed);
        final IBrowser browser = this.model.getBrowser ();
        if (direction)
        {
            for (int i = 0; i < speed; i++)
                browser.selectNextFilterItem (columnIndex);
        }
        else
        {
            for (int i = 0; i < speed; i++)
                browser.selectPreviousFilterItem (columnIndex);
        }
    }


"""
# This helper is deliberately retained: filterColumn is the absolute Bitwig
# index, whereas changeValue() accepts the visible Push-column index.
if browser.count (duplicate_method) != 1:
    raise SystemExit ("Browser absolute-index encoder helper: expected exactly one definition")
browser = replace_once(
    browser,
    """    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        super.onDeactivate ();

        this.model.getBrowser ().stopBrowsing (true);
    }


""",
    """    /** {@inheritDoc} */
    @Override
    public void onActivate ()
    {
        super.onActivate ();
        this.displayColumnOffset = 0;
        this.resetFilterColumn ();
    }


    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        super.onDeactivate ();

        this.model.getBrowser ().stopBrowsing (true);
    }


""",
    "Reset Browser horizontal page on activation",
)
BROWSER.write_text(browser, encoding="utf-8")


java = r"""// Written for StrattV4.
// Fixed controller labels are translated contextually. Dynamic names supplied
// by Bitwig (devices, tracks, presets, parameters and filter values) are kept.
package de.mossgrabers.controller.ableton.push.controller;

import java.text.Normalizer;


public final class Push1French
{
    private static final String [][] LABELS =
    {
        {"Selected Device:", "Composant actif:"},
        {"Device Chains:", "Chaines comp.:"},
        {"Selection:", "Choix :"},
        {"Preview:", "Ecoute :"},
        {"Replace:", "Remplacer :"},
        {"Add device to:", "Ajouter a :"},
        {"Insert device before:", "Inserer avant :"},
        {"Insert device after:", "Inserer apres :"},
        {"No results", "Aucun resultat"},
        {"available...", "disponible..."},
        {"Please start", "Lancer Bitwig"},
        {"None", "Aucun"},
        {"On", "Oui"},
        {"Off", "Non"},
        {"Select", "Choisir"},
        {"Up", "Haut"},
        {"'Add Effect'...", "'Ajouter effet'"},
        {"a device or press", "un composant ou"},
        {"Please create", "Creer une couche"},
        {"a Drum Pad...", "un pad batterie"},
        {"a Device Layer...", "une couche comp."},
        {"This device", "Ce composant"},
        {"does not have layers.", "sans couches."},
        {"Automation Mode:", "Mode automation:"},
        {"Pad Threshold", "Seuil pad"},
        {"Velocity Curve", "Courbe velo."},
        {"Firmware:", "Micrologiciel:"},
        {"Board Revision:", "Revision carte:"},
        {"Serial Number:", "No serie:"},
        {"Brightness", "Luminosite"},
        {"Setup", "Reglages"},
        {"Pre-roll", "Precompte"},
        {"Play Metronome", "Metronome"},
        {"during Pre-roll?", "pendant precompte?"},
        {"Markers:", "Marqueurs :"},
        {"Action:", "Action :"},
        {"Sequence:", "Sequence :"},
        {"Play:", "Lecture :"},
        {"Tools:", "Outils :"},
        {"Session view:", "Vue session :"},
        {"Session mode:", "Mode session :"},
        {"Create Clip (leng", "Creer clip (long"},
        {"th not stored):", "ueur non stockee):"},
        {"New Clip Length:", "Duree clip nouv."},
        {"Record Quantize:", "Quantif. rec :"},
        {"Quant Note", "Note quant."},
        {"Quant Amnt", "Dose quant."},
        {"Quantize", "Quantif."},
        {"Shuffle:", "Swing :"},
        {"Shuffle", "Swing"},
        {"Period:", "Periode :"},
        {"Length:", "Duree :"},
        {"Latch", "Maintien"},
        {"Octaves", "Octaves"},
        {"Chromatc", "Chromat."},
        {"In Key", "Gamme"},
        {"Scale layout:", "Dispo. gamme :"},
        {"Note range:", "Plage notes :"},
        {"INSTRUMENT", "INSTRUM."},
        {"EFFECT", "EFFET"},
        {"Instrument", "Instrum."},
        {"Effect", "Effet"},
        {"Volume", "Volume"},
        {"Pan", "Pan"},
        {"Crossfdr", "Fondu"},
        {"Project:", "Projet :"},
        {"Audio Engine", "Moteur audio"},
        {"Previous", "Prec."},
        {"Next", "Suiv."},
        {"Cue", "Ecoute"},
        {"PlayStrt", "Debut"},
        {"Play End", "Fin lect."},
        {"LoopStrt", "Deb. bouc"},
        {"LopLngth", "Long. bouc"},
        {"Loop", "Boucle"},
        {"Accent", "Accent"},
        {"Active", "Actif"},
        {"Rec Arm", "Arm rec."},
        {"Mute", "Muet"},
        {"Solo", "Solo"},
        {"Monitor", "Ecoute"},
        {"Auto Monitor", "Auto ec."},
        {"Pin Trck", "Epingler"},
        {"Pin Track", "Epingler"},
        {"Select Color", "Choix couleur"},
        {"Color", "Couleur"},
        {"Midi Ins", "Entree MIDI"},
        {"Clear Mute", "Retirer muet"},
        {"Clear Solo", "Retirer solo"},
        {"Clr Mute", "Retir. muet"},
        {"Clr Solo", "Retir. solo"},
        {"COMMON:", "COMMUN :"},
        {"MUTED", "MUET"},
        {"Step:", "Pas :"},
        {"Notes:", "Notes :"},
        {"Velocity", "Velocite"},
        {"V-Spread", "Disp. vel"},
        {"R-Velcty", "Vel. alea"},
        {"Chance", "Chance"},
        {"Occurnce", "Occur."},
        {"Recurnce", "Recurr."},
        {"EXPRESS:", "EXPRES :"},
        {"Pitch", "Hauteur"},
        {"Pressure", "Pression"},
        {"REPEAT:", "REPETER :"},
        {"Count", "Nombre"},
        {"Curve", "Courbe"},
        {"Vel-Crve", "Crbe vel"},
        {"Vel. End", "Fin vel."},
        {"Recurrence", "Recurr."},
        {"Pattern", "Motif"},
        {"Please select a note to edit...", "Choisir une note..."},
        {"Modulatn", "Modulat."},
        {"Expressn", "Express."},
        {"Sustain", "Maintien"},
        {"Function", "Fonction"},
        {"BROWSE", "PARCOURIR"},
        {"Device", "Composant"},
        {"Parameters", "Parametres"}
    };


    private static final String [][] PREFIXES =
    {
        {"Layer: ", "Couche : "},
        {"Firmware: ", "Micrologiciel : "},
        {"Board Revision: ", "Revision carte : "},
        {"Serial Number: ", "No serie : "},
        {"Edit Channel: ", "Canal edit : "},
        {"/Edit Channel: ", "/Canal edit : "}
    };


    private Push1French ()
    {
        // Utility class.
    }


    public static String translate (final String original)
    {
        if (original == null || original.isEmpty ())
            return "";

        int start = 0;
        while (start < original.length () && Character.isWhitespace (original.charAt (start)))
            start++;
        final String leading = original.substring (0, start);
        final boolean selected = start < original.length () && original.charAt (start) == 127;
        if (selected)
            start++;

        int end = original.length ();
        while (end > start && Character.isWhitespace (original.charAt (end - 1)))
            end--;
        final String trailing = original.substring (end);
        final String core = original.substring (start, end);
        return leading + (selected ? Character.toString ((char) 127) : "")
            + toAscii (translateCore (core)) + trailing;
    }


    private static String translateCore (final String source)
    {
        for (final String [] entry: LABELS)
            if (entry[0].equals (source))
                return entry[1];

        for (final String [] entry: PREFIXES)
            if (source.startsWith (entry[0]))
                return entry[1] + source.substring (entry[0].length ());

        if (source.endsWith (" to play..."))
            return source.substring (0, source.length () - " to play...".length ()) + " pour jouer...";
        return source;
    }


    public static String toAscii (final String source)
    {
        if (source == null || source.isEmpty ())
            return "";

        String expanded = source
            .replace ("œ", "oe").replace ("Œ", "OE")
            .replace ("æ", "ae").replace ("Æ", "AE")
            .replace ("ß", "ss")
            .replace ("’", "'").replace ("‘", "'")
            .replace ("“", "\"").replace ("”", "\"")
            .replace ("–", "-").replace ("—", "-")
            .replace ("…", "...")
            .replace ("→", "->").replace ("←", "<-")
            .replace ("♯", "#").replace ("♭", "b")
            .replace ("×", "x").replace ("÷", "/")
            .replace ("°", " deg ")
            .replace ("¼", "1/4");

        expanded = Normalizer.normalize (expanded, Normalizer.Form.NFD);
        final StringBuilder ascii = new StringBuilder (expanded.length ());
        for (int i = 0; i < expanded.length (); i++)
        {
            final char c = expanded.charAt (i);
            if (c == 0x7F || c == 0x02 || c == 0x07 || c == 0x03 || c == 0x04 || c == 0x05 || c == 0x06 || c == 0x09 || c == 0x18 || c == 0x1E)
                ascii.append (c); // Preserve Push 1 selection, group, folder, value-bar, degree and arrow glyphs.
            else if (c < 0x20)
                ascii.append (' '); // Replace unrelated control characters, not Push icons.
            else if (c <= 0x7F)
                ascii.append (c);
            else if (Character.getType (c) != Character.NON_SPACING_MARK
                    && Character.getType (c) != Character.COMBINING_SPACING_MARK
                    && Character.getType (c) != Character.ENCLOSING_MARK)
                ascii.append ('?');
        }
        return ascii.toString ();
    }
}
"""
FRENCH.write_text(java, encoding="utf-8")


display = DISPLAY.read_text(encoding="utf-8")
display = replace_once(
    display,
    """    public ITextDisplay setBlock (final int row, final int block, final String value)
    {
        final int cell = 2 * block;
        if (value.length () > 9)
        {
            this.cells[row * 8 + cell] = value.substring (0, 9);
            this.cells[row * 8 + cell + 1] = StringUtils.pad (value.substring (9), 8, ' ');
        }
        else
        {
            this.cells[row * 8 + cell] = StringUtils.pad (value, 9, ' ');
            this.clearCell (row, cell + 1);
        }
        return this;
    }
""",
    """    public ITextDisplay setBlock (final int row, final int block, final String value)
    {
        final String translated = Push1French.translate (value);
        final int cell = 2 * block;
        if (translated.length () > 9)
        {
            this.cells[row * 8 + cell] = translated.substring (0, 9);
            this.cells[row * 8 + cell + 1] = StringUtils.pad (translated.substring (9), 8, ' ');
        }
        else
        {
            this.cells[row * 8 + cell] = StringUtils.pad (translated, 9, ' ');
            this.clearCell (row, cell + 1);
        }
        return this;
    }
""",
    "Push 1 block translation",
)
display = replace_once(
    display,
    """    public ITextDisplay setCell (final int row, final int cell, final String value)
    {
        this.cells[row * 8 + cell] = StringUtils.pad (value, 8, ' ') + (cell % 2 == 0 ? " " : "");
        return this;
    }
""",
    """    public ITextDisplay setCell (final int row, final int cell, final String value)
    {
        this.cells[row * 8 + cell] = StringUtils.pad (Push1French.translate (value), 8, ' ') + (cell % 2 == 0 ? " " : "");
        return this;
    }
""",
    "Push 1 cell translation",
)
display = replace_once(
    display,
    """    public void writeLine (final int row, final String text)
    {
        this.output.sendSysex (Push1Display.SYSEX_MESSAGE[row] + StringUtils.asciiToHex (text) + "F7");
    }
""",
    """    public void writeLine (final int row, final String text)
    {
        this.output.sendSysex (Push1Display.SYSEX_MESSAGE[row] + StringUtils.asciiToHex (Push1French.toAscii (text)) + "F7");
    }
""",
    "7-bit ASCII SysEx output",
)
DISPLAY.write_text(display, encoding="utf-8")

for token in ("Push1French.translate (value)", "Push1French.toAscii (text)"):
    if token not in display:
        raise SystemExit(f"Push1Display: missing postcondition {token}")
for token in ("c == 0x7F || c == 0x02 || c == 0x07 || c == 0x03 || c == 0x04 || c == 0x05 || c == 0x06 || c == 0x09 || c == 0x18 || c == 0x1E", "value-bar, degree and arrow glyphs"):
    if token not in java:
        raise SystemExit(f"Push1French: missing preserved Push glyph {token}")
for token in ("this.changeFilterColumnValue (this.filterColumn, value)", "public void onActivate ()", "this.displayColumnOffset = 0;"):
    if token not in browser:
        raise SystemExit(f"DeviceBrowserMode: missing postcondition {token}")
if "private void changeFilterColumnValue" not in browser:
    raise SystemExit("DeviceBrowserMode: absolute filter encoder helper is missing")
print("Push 1 French UI and safe ASCII SysEx output applied.")
