#!/usr/bin/env python3
"""Apply the StrattV4 64-colour Push 1 palette to pinned DrivenByMoss 19.2.2."""

from pathlib import Path
import re

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")

EXTRA_COLORS = [
    ("ABLETON_01", "Red 02", (255, 76, 76), 4),
    ("ABLETON_02", "Orange 07", (255, 189, 108), 8),
    ("ABLETON_03", "Orange 02", (255, 84, 0), 9),
    ("ABLETON_04", "Yellow 04", (255, 255, 76), 12),
    ("ABLETON_05", "Yellow 03", (255, 255, 0), 13),
    ("ABLETON_06", "Green 10", (136, 255, 76), 16),
    ("ABLETON_07", "Green 11", (84, 255, 0), 17),
    ("ABLETON_08", "Green 16", (76, 255, 76), 20),
    ("ABLETON_09", "Green 18", (76, 255, 94), 24),
    ("ABLETON_10", "Green 17", (0, 255, 25), 25),
    ("ABLETON_11", "Green 21", (76, 255, 136), 28),
    ("ABLETON_12", "Green 20", (0, 255, 85), 29),
    ("ABLETON_13", "Green 24", (76, 255, 183), 32),
    ("ABLETON_14", "Green 25", (0, 255, 153), 33),
    ("ABLETON_15", "Blue 01", (76, 195, 255), 36),
    ("ABLETON_16", "Blue 04", (76, 136, 255), 40),
    ("ABLETON_17", "Blue 05", (0, 85, 255), 41),
    ("ABLETON_18", "Violet 03", (135, 76, 255), 48),
    ("ABLETON_19", "Magenta 03", (255, 76, 255), 52),
    ("ABLETON_20", "Magenta 02", (255, 0, 255), 53),
    ("ABLETON_21", "Pink 02", (255, 76, 135), 56),
    ("ABLETON_22", "Pink 03", (255, 0, 84), 57),
    ("ABLETON_23", "Red 03", (255, 21, 0), 60),
    ("ABLETON_24", "Blue 03", (0, 84, 127), 66),
    ("ABLETON_25", "Yellow 02", (185, 176, 0), 97),
    ("ABLETON_26", "Green 06", (144, 255, 0), 98),
    ("ABLETON_27", "Red 04", (222, 81, 61), 107),
    ("ABLETON_28", "Orange 03", (216, 106, 28), 108),
    ("ABLETON_29", "Yellow 01", (255, 225, 38), 109),
    ("ABLETON_30", "Green 04", (158, 225, 47), 110),
    ("ABLETON_31", "Green 07", (103, 181, 15), 111),
    ("ABLETON_32", "Green 01", (220, 255, 107), 113),
    ("ABLETON_33", "Green 22", (128, 255, 189), 114),
    ("ABLETON_34", "Blue 09", (154, 153, 255), 115),
    ("ABLETON_35", "Violet 02", (142, 102, 255), 116),
    ("ABLETON_36", "Green 12", (26, 208, 0), 122),
    ("ABLETON_37", "Orange 06", (179, 95, 0), 126),
]

ORIGINAL_UPDATES = [
    ("DAW_COLOR_DARK_GRAY", "Charcoal", (127, 127, 127), 70),
    ("DAW_COLOR_GRAY", "Mid Grey", (32, 32, 32), 71),
    ("DAW_COLOR_GRAY_HALF", "Red 01", (255, 0, 0), 72),
    ("DAW_COLOR_LIGHT_GRAY", "Green 03", (189, 255, 45), 73),
    ("DAW_COLOR_SILVER", "Green 02", (175, 237, 6), 74),
    ("DAW_COLOR_DARK_BROWN", "Green 09", (100, 255, 9), 75),
    ("DAW_COLOR_BROWN", "Green 13", (16, 139, 0), 76),
    ("DAW_COLOR_DARK_BLUE", "Green 23", (0, 255, 135), 77),
    ("DAW_COLOR_PURPLE_BLUE", "Blue 02", (0, 169, 255), 78),
    ("DAW_COLOR_PURPLE", "Blue 08", (0, 42, 255), 79),
    ("DAW_COLOR_PINK", "Violet 01", (63, 0, 255), 80),
    ("DAW_COLOR_RED", "Violet 04", (122, 0, 255), 81),
    ("DAW_COLOR_ORANGE", "Magenta 04", (178, 26, 125), 82),
    ("DAW_COLOR_LIGHT_ORANGE", "Orange 05", (64, 33, 0), 83),
    ("DAW_COLOR_MOSS_GREEN", "Orange 01", (255, 74, 0), 84),
    ("DAW_COLOR_GREEN", "Green 05", (136, 225, 6), 85),
    ("DAW_COLOR_COLD_GREEN", "Green 08", (114, 255, 21), 86),
    ("DAW_COLOR_BLUE", "Green 15", (0, 255, 0), 87),
    ("DAW_COLOR_LIGHT_PURPLE", "Green 14", (59, 255, 38), 88),
    ("DAW_COLOR_LIGHT_PINK", "Green 19", (89, 255, 113), 89),
    ("DAW_COLOR_ROSE", "Turquoise 01", (56, 255, 204), 90),
    ("DAW_COLOR_REDDISH_BROWN", "Blue 06", (91, 138, 255), 91),
    ("DAW_COLOR_LIGHT_BROWN", "Blue 07", (49, 81, 198), 92),
    ("DAW_COLOR_LIGHT_GREEN", "Blue 10", (135, 127, 233), 93),
    ("DAW_COLOR_BLUISH_GREEN", "Magenta 01", (211, 29, 255), 94),
    ("DAW_COLOR_GREEN_BLUE", "Pink 01", (255, 0, 93), 95),
    ("DAW_COLOR_LIGHT_BLUE", "Orange 04", (255, 127, 0), 96),
]

# The visual order is arranged as an 8 x 8 chromatic swatch. The original
# 28 DAWColor entries remain unchanged and appear exactly once.
PALETTE_ORDER = [
    "DAW_COLOR_DAW_COLOR_GRAY", "DAW_COLOR_DAW_COLOR_DARK_GRAY", "DAW_COLOR_DAW_COLOR_GRAY_HALF", "DAW_COLOR_ABLETON_01",
    "DAW_COLOR_ABLETON_23", "DAW_COLOR_ABLETON_27", "DAW_COLOR_DAW_COLOR_MOSS_GREEN", "DAW_COLOR_ABLETON_03",
    "DAW_COLOR_ABLETON_28", "DAW_COLOR_DAW_COLOR_LIGHT_BLUE", "DAW_COLOR_DAW_COLOR_LIGHT_ORANGE", "DAW_COLOR_ABLETON_37",
    "DAW_COLOR_ABLETON_02", "DAW_COLOR_ABLETON_29", "DAW_COLOR_ABLETON_25", "DAW_COLOR_ABLETON_05",
    "DAW_COLOR_ABLETON_04", "DAW_COLOR_ABLETON_32", "DAW_COLOR_DAW_COLOR_SILVER", "DAW_COLOR_DAW_COLOR_LIGHT_GRAY",
    "DAW_COLOR_ABLETON_30", "DAW_COLOR_DAW_COLOR_GREEN", "DAW_COLOR_ABLETON_26", "DAW_COLOR_ABLETON_31",
    "DAW_COLOR_DAW_COLOR_COLD_GREEN", "DAW_COLOR_DAW_COLOR_DARK_BROWN", "DAW_COLOR_ABLETON_06", "DAW_COLOR_ABLETON_07",
    "DAW_COLOR_ABLETON_36", "DAW_COLOR_DAW_COLOR_BROWN", "DAW_COLOR_DAW_COLOR_LIGHT_PURPLE", "DAW_COLOR_DAW_COLOR_BLUE",
    "DAW_COLOR_ABLETON_08", "DAW_COLOR_ABLETON_10", "DAW_COLOR_ABLETON_09", "DAW_COLOR_DAW_COLOR_LIGHT_PINK",
    "DAW_COLOR_ABLETON_12", "DAW_COLOR_ABLETON_11", "DAW_COLOR_ABLETON_33", "DAW_COLOR_DAW_COLOR_DARK_BLUE",
    "DAW_COLOR_ABLETON_13", "DAW_COLOR_ABLETON_14", "DAW_COLOR_DAW_COLOR_ROSE", "DAW_COLOR_ABLETON_15",
    "DAW_COLOR_DAW_COLOR_PURPLE_BLUE", "DAW_COLOR_ABLETON_24", "DAW_COLOR_ABLETON_16", "DAW_COLOR_ABLETON_17",
    "DAW_COLOR_DAW_COLOR_REDDISH_BROWN", "DAW_COLOR_DAW_COLOR_LIGHT_BROWN", "DAW_COLOR_DAW_COLOR_PURPLE", "DAW_COLOR_ABLETON_34",
    "DAW_COLOR_DAW_COLOR_LIGHT_GREEN", "DAW_COLOR_DAW_COLOR_PINK", "DAW_COLOR_ABLETON_35", "DAW_COLOR_ABLETON_18",
    "DAW_COLOR_DAW_COLOR_RED", "DAW_COLOR_DAW_COLOR_BLUISH_GREEN", "DAW_COLOR_ABLETON_20", "DAW_COLOR_ABLETON_19",
    "DAW_COLOR_DAW_COLOR_ORANGE", "DAW_COLOR_DAW_COLOR_GREEN_BLUE", "DAW_COLOR_ABLETON_21", "DAW_COLOR_ABLETON_22",
]

ORIGINAL_COLORS = [
    "DAW_COLOR_DARK_GRAY",
    "DAW_COLOR_GRAY",
    "DAW_COLOR_GRAY_HALF",
    "DAW_COLOR_LIGHT_GRAY",
    "DAW_COLOR_SILVER",
    "DAW_COLOR_DARK_BROWN",
    "DAW_COLOR_BROWN",
    "DAW_COLOR_DARK_BLUE",
    "DAW_COLOR_PURPLE_BLUE",
    "DAW_COLOR_PURPLE",
    "DAW_COLOR_PINK",
    "DAW_COLOR_RED",
    "DAW_COLOR_ORANGE",
    "DAW_COLOR_LIGHT_ORANGE",
    "DAW_COLOR_MOSS_GREEN",
    "DAW_COLOR_GREEN",
    "DAW_COLOR_COLD_GREEN",
    "DAW_COLOR_BLUE",
    "DAW_COLOR_LIGHT_PURPLE",
    "DAW_COLOR_LIGHT_PINK",
    "DAW_COLOR_ROSE",
    "DAW_COLOR_REDDISH_BROWN",
    "DAW_COLOR_LIGHT_BROWN",
    "DAW_COLOR_LIGHT_GREEN",
    "DAW_COLOR_BLUISH_GREEN",
    "DAW_COLOR_GREEN_BLUE",
    "DAW_COLOR_LIGHT_BLUE",
]


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


if len(EXTRA_COLORS) != 37 or len(PALETTE_ORDER) != 64:
    raise SystemExit("Palette definition must contain exactly 37 additions and 64 positions")
if len(set(PALETTE_ORDER)) != 64:
    raise SystemExit("Palette contains duplicate positions")
if not set(ORIGINAL_COLORS).issubset(PALETTE_ORDER):
    raise SystemExit("One or more original DrivenByMoss colors are missing")
if len({entry[3] for entry in EXTRA_COLORS + ORIGINAL_UPDATES}) != 64:
    raise SystemExit("All 64 Push 1 LED indices must be unique")

# Extend DAWColor without changing the original enum entries or their ordinals.
daw_path = ROOT / "framework/daw/DAWColor.java"
daw = daw_path.read_text(encoding="utf-8")
anchor = '    DAW_COLOR_LIGHT_BLUE("Light Blue", new ColorEx (0, 0.6000000238418579, 0.8509804010391235));'
enum_lines = []
for suffix, label, rgb, _index in EXTRA_COLORS:
    red, green, blue = rgb
    enum_lines.append(
        f'    DAW_COLOR_{suffix}("{label}", new ColorEx '
        f'({red} / 255.0, {green} / 255.0, {blue} / 255.0))'
    )
enum_lines[-1] += ";"
daw = replace_once(daw, anchor, anchor[:-1] + ",\n" + ",\n".join(enum_lines), "DAWColor enum")
for suffix, label, rgb, _index in ORIGINAL_UPDATES:
    pattern = re.compile(rf'^(\s*{re.escape(suffix)}\()"[^"]+"(,\s*new ColorEx\s*\()[^)]+(\)\),?)$', re.MULTILINE)
    daw, count = pattern.subn(
        lambda match: match.group(1) + '"' + label + '"' + match.group(2) + ", ".join(f"{channel} / 255.0" for channel in rgb) + match.group(3),
        daw,
    )
    if count != 1:
        raise SystemExit(f"DAWColor {suffix}: expected one original enum entry, found {count}")

daw_path.write_text(daw, encoding="utf-8")

# Give each added color its exact Push 1 hardware palette index.
manager_path = ROOT / "controller/ableton/push/controller/PushColorManager.java"
manager = manager_path.read_text(encoding="utf-8")
anchor = "        this.registerColorIndex (DAWColor.DAW_COLOR_LIGHT_BLUE, isPush2 ? 96 : 41);"
registration_lines = [
    f"        this.registerColorIndex (DAWColor.DAW_COLOR_{suffix}, {index});"
    for suffix, _label, _rgb, index in EXTRA_COLORS
]
manager = replace_once(
    manager,
    anchor,
    anchor + "\n" + "\n".join(registration_lines),
    "PushColorManager registrations",
)
for suffix, _label, _rgb, index in ORIGINAL_UPDATES:
    pattern = re.compile(rf'(this\.registerColorIndex \(DAWColor\.{re.escape(suffix)}, isPush2 \? [^:]+ : )[^)]+(\);)')
    manager, count = pattern.subn(lambda match: match.group(1) + str(index) + match.group(2), manager)
    if count != 1:
        raise SystemExit(f"PushColorManager {suffix}: expected one original mapping, found {count}")

manager_path.write_text(manager, encoding="utf-8")

# Present one 64-colour palette over the Push 1's 8 x 8 pad grid.
view_path = ROOT / "framework/view/ColorView.java"
view = view_path.read_text(encoding="utf-8")
class_anchor = (
    "public class ColorView<S extends IControlSurface<C>, C extends Configuration> extends AbstractView<S, C>\n"
    "{"
)
palette_lines = [
    "        " + ", ".join(f"DAWColor.{name}" for name in PALETTE_ORDER[i:i + 4]) + ","
    for i in range(0, len(PALETTE_ORDER), 4)
]
palette_block = (
    class_anchor
    + "\n    private static final DAWColor [] COLOR_PALETTE =\n    {\n"
    + "\n".join(palette_lines)
    + "\n    };"
)
view = replace_once(view, class_anchor, palette_block, "ColorView palette declaration")
count = view.count("DAWColor.values ()")
if count != 3:
    raise SystemExit(f"ColorView: expected three DAWColor.values() uses, found {count}")
view = view.replace("DAWColor.values ()", "COLOR_PALETTE")
view_path.write_text(view, encoding="utf-8")

# StrattV4 product decision: remove the Raindrops sequencer from the Push 1 view menu.
# Keep the upstream submodule pinned and untouched; apply this small adaptation at build time.
setup_path = ROOT / "controller/ableton/push/PushControllerSetup.java"
setup = setup_path.read_text(encoding="utf-8")
setup = replace_once(
    setup,
    "import de.mossgrabers.controller.ableton.push.view.RaindropsView;\n",
    "",
    "RaindropsView import",
)
setup = replace_once(
    setup,
    "        viewManager.register (Views.RAINDROPS, new RaindropsView (surface, this.model));\n",
    "",
    "RaindropsView registration",
)
# Remove the Raindrop feature implementation and every Push 1 entry point.
config_path = ROOT / "controller/ableton/push/PushConfiguration.java"
config = config_path.read_text(encoding="utf-8")
config = replace_once(config, "        Views.RAINDROPS,\n", "", "Raindrop preferred view")
config_path.write_text(config, encoding="utf-8")

layout_path = ROOT / "controller/ableton/push/command/trigger/LayoutCommand.java"
layout = layout_path.read_text(encoding="utf-8")
layout = replace_once(
    layout,
    "        else if (viewManager.isActive (Views.SEQUENCER))\n            this.activatePreferredView (Views.RAINDROPS);\n        else if (viewManager.isActive (Views.RAINDROPS))\n            this.activatePreferredView (Views.DRUM);\n",
    "        else if (viewManager.isActive (Views.SEQUENCER))\n            this.activatePreferredView (Views.DRUM);\n",
    "Raindrop layout cycling",
)
layout_path.write_text(layout, encoding="utf-8")

selector_path = ROOT / "controller/ableton/push/mode/NoteViewSelectMode.java"
selector = selector_path.read_text(encoding="utf-8")
selector = replace_once(
    selector,
    "        Views.POLY_SEQUENCER,\n        Views.RAINDROPS,\n        Views.DRUM,\n",
    "        Views.POLY_SEQUENCER,\n        null,\n        Views.DRUM,\n",
    "Raindrop note view selector",
)
selector_path.write_text(selector, encoding="utf-8")

raindrop_source = ROOT / "controller/ableton/push/view/RaindropsView.java"
if not raindrop_source.is_file():
    raise SystemExit("Expected Push-specific RaindropsView.java is missing")
raindrop_source.unlink()
setup = replace_once(
    setup,
    "import de.mossgrabers.controller.ableton.push.view.Drum4View;\n",
    "",
    "Drum4View import",
)
setup = replace_once(
    setup,
    "import de.mossgrabers.controller.ableton.push.view.Drum8View;\n",
    "",
    "Drum8View import",
)
setup = replace_once(
    setup,
    "        viewManager.register (Views.DRUM4, new Drum4View (surface, this.model));\n",
    "",
    "Drum 4 view registration",
)
setup = replace_once(
    setup,
    "        viewManager.register (Views.DRUM8, new Drum8View (surface, this.model));\n",
    "",
    "Drum 8 view registration",
)
# DRUM4 and DRUM8 remain in the shared framework enum for other controllers;
# StrattV4 removes all Push 1 registrations, selection paths and implementations.

config_path = ROOT / "controller/ableton/push/PushConfiguration.java"
config = config_path.read_text(encoding="utf-8")
config = replace_once(config, "        Views.DRUM4,\n", "", "Drum 4 preferred view")
config = replace_once(config, "        Views.DRUM8,\n", "", "Drum 8 preferred view")
config_path.write_text(config, encoding="utf-8")

layout_path = ROOT / "controller/ableton/push/command/trigger/LayoutCommand.java"
layout = layout_path.read_text(encoding="utf-8")
layout = replace_once(
    layout,
    "        else if (viewManager.isActive (Views.DRUM))\n            this.activatePreferredView (Views.DRUM4);\n        else if (viewManager.isActive (Views.DRUM4))\n            this.activatePreferredView (Views.DRUM8);\n        else if (viewManager.isActive (Views.DRUM8))\n            this.activatePreferredView (Views.SEQUENCER);\n",
    "        else if (viewManager.isActive (Views.DRUM))\n            this.activatePreferredView (Views.SEQUENCER);\n",
    "Drum 4/8 layout cycling",
)
layout_path.write_text(layout, encoding="utf-8")

selector_path = ROOT / "controller/ableton/push/mode/NoteViewSelectMode.java"
selector = selector_path.read_text(encoding="utf-8")
selector = replace_once(
    selector,
    "        Views.DRUM,\n        Views.DRUM4,\n        Views.DRUM8,\n        null,\n",
    "        Views.DRUM,\n        null,\n        null,\n        null,\n",
    "Drum 4/8 note view selector slots",
)
selector_path.write_text(selector, encoding="utf-8")

# Align Note Mode's displayed upper/lower menu rows with the corresponding
# physical Push 1 button rows. DrivenByMoss renders VIEWS at the bottom and
# VIEWS_TOP at the top; route both button presses and LED feedback accordingly.
note_selector_path = ROOT / "controller/ableton/push/mode/NoteViewSelectMode.java"
note_selector = note_selector_path.read_text(encoding="utf-8")
note_selector = replace_once(
    note_selector,
    """    public void onFirstRow (final int index, final ButtonEvent event)
    {
        if (event == ButtonEvent.UP)
            this.activateView (VIEWS[index]);
    }
""",
    """    public void onFirstRow (final int index, final ButtonEvent event)
    {
        if (event == ButtonEvent.UP)
            this.activateView (VIEWS_TOP[index]);
    }
""",
    "Note Mode first-row selection alignment",
)
note_selector = replace_once(
    note_selector,
    """    public void onSecondRow (final int index, final ButtonEvent event)
    {
        if (event == ButtonEvent.UP)
            this.activateView (VIEWS_TOP[index]);
    }
""",
    """    public void onSecondRow (final int index, final ButtonEvent event)
    {
        if (event == ButtonEvent.UP)
            this.activateView (VIEWS[index]);
    }
""",
    "Note Mode second-row selection alignment",
)
note_selector = replace_once(
    note_selector,
    """    @Override
    public String getButtonColorID (final ButtonID buttonID)
    {
        int index = this.isButtonRow (0, buttonID);
        if (index >= 0)
        {
            final ViewManager viewManager = this.surface.getViewManager ();
            if (VIEWS[index] == null)
                return AbstractFeatureGroup.BUTTON_COLOR_OFF;
            return viewManager.isActive (VIEWS[index]) ? AbstractMode.BUTTON_COLOR_HI : AbstractFeatureGroup.BUTTON_COLOR_ON;
        }

        index = this.isButtonRow (1, buttonID);
        if (index >= 0)
        {
            final ViewManager viewManager = this.surface.getViewManager ();
            if (VIEWS_TOP[index] == null)
                return AbstractFeatureGroup.BUTTON_COLOR_OFF;
            return viewManager.isActive (VIEWS_TOP[index]) ? AbstractMode.BUTTON_COLOR_HI : AbstractFeatureGroup.BUTTON_COLOR_ON;
        }

        return AbstractFeatureGroup.BUTTON_COLOR_OFF;
    }
""",
    """    @Override
    public String getButtonColorID (final ButtonID buttonID)
    {
        int index = this.isButtonRow (0, buttonID);
        if (index >= 0)
        {
            final ViewManager viewManager = this.surface.getViewManager ();
            if (VIEWS_TOP[index] == null)
                return AbstractFeatureGroup.BUTTON_COLOR_OFF;
            return viewManager.isActive (VIEWS_TOP[index]) ? AbstractMode.BUTTON_COLOR_HI : AbstractFeatureGroup.BUTTON_COLOR_ON;
        }

        index = this.isButtonRow (1, buttonID);
        if (index >= 0)
        {
            final ViewManager viewManager = this.surface.getViewManager ();
            if (VIEWS[index] == null)
                return AbstractFeatureGroup.BUTTON_COLOR_OFF;
            return viewManager.isActive (VIEWS[index]) ? AbstractMode.BUTTON_COLOR_HI : AbstractFeatureGroup.BUTTON_COLOR_ON;
        }

        return AbstractFeatureGroup.BUTTON_COLOR_OFF;
    }
""",
    "Note Mode LED row alignment",
)
note_selector_path.write_text(note_selector, encoding="utf-8")

# Do not compile or package the Push-specific Drum 4 / Drum 8 implementations.
for class_name in ("Drum4View.java", "Drum8View.java"):
    source_file = ROOT / "controller/ableton/push/view" / class_name
    if not source_file.is_file():
        raise SystemExit(f"Expected Push-specific source file is missing: {class_name}")
    source_file.unlink()

# Remember the note range independently for every selected Push 1 track.
setup = replace_once(
    setup,
    "import java.util.Optional;\n",
    "import de.mossgrabers.framework.utils.ButtonEvent;\nimport java.util.HashMap;\nimport java.util.Map;\nimport java.util.Optional;\n",
    "per-track note state imports",
)
setup = replace_once(
    setup,
    "    private final boolean isPush2;\n",
    """    private final boolean isPush2;
    private final Map<Integer, TrackNoteState> trackNoteStates = new HashMap<> ();
    private int activeTrackPosition = -1;

    private static final class TrackNoteState
    {
        private final int octave;
        private final int pianoOctave;
        private final int drumOffset;

        TrackNoteState (final int octave, final int pianoOctave, final int drumOffset)
        {
            this.octave = octave;
            this.pianoOctave = pianoOctave;
            this.drumOffset = drumOffset;
        }
    }
""",
    "per-track note state fields",
)
setup = replace_once(
    setup,
    "        this.model = this.factory.createModel (this.configuration, this.colorManager, this.valueChanger, this.scales, ms);\n",
    "        this.model = this.factory.createModel (this.configuration, this.colorManager, this.valueChanger, this.scales, ms);\n"
    "        if (this.model.getCursorTrack ().doesExist ())\n"
    "            this.activeTrackPosition = this.model.getCursorTrack ().getPosition ();\n",
    "initial selected track position",
)
setup = replace_once(
    setup,
    "    private boolean getMuteState ()\n",
    """    /**
     * Save the outgoing track's note range and restore the incoming track's range.
     *
     * @param isSelected True if a track has just become selected
     */
    @Override
    protected void handleTrackChange (final boolean isSelected)
    {
        if (!isSelected)
        {
            this.saveTrackNoteState ();
            return;
        }

        final ITrack selectedTrack = this.model.getCursorTrack ();
        if (selectedTrack.doesExist ())
        {
            // The outgoing track was saved by the deselection callback.
            // Saving again here would capture Bitwig's reset note range and
            // overwrite the outgoing track's previously remembered octave.
            this.activeTrackPosition = selectedTrack.getPosition ();
        }

        super.handleTrackChange (true);
    }


    /**
     * Restore the note range remembered for the selected track.
     */
    @Override
    protected void resetDrumOctave ()
    {
        final TrackNoteState state = this.trackNoteStates.get (Integer.valueOf (this.activeTrackPosition));
        if (state == null)
        {
            // A track with no history starts at the standard Push note range.
            this.scales.setOctave (0);
            this.scales.setPianoOctave (0);
            this.scales.resetDrumOctave ();
        }
        else
        {
            this.scales.setOctave (state.octave);
            this.scales.setPianoOctave (state.pianoOctave);
            this.scales.resetDrumOctave ();
            final int drumOffsetDelta = state.drumOffset - this.scales.getDrumOffset ();
            if (drumOffsetDelta > 0)
                this.scales.incDrumOffset (drumOffsetDelta);
            else if (drumOffsetDelta < 0)
                this.scales.decDrumOffset (-drumOffsetDelta);
        }

        final ViewManager viewManager = this.getSurface ().getViewManager ();
        if (viewManager.isActive (Views.DRUM))
        {
            // Bitwig resets the Drum Machine pad-bank scroll position on track
            // selection as well as the note mapping. Restore both to the saved
            // MIDI offset; otherwise the Push still displays the C1 bank.
            this.model.getDrumDevice ().getDrumPadBank ().scrollTo (this.scales.getDrumOffset (), true);
        }
        if (viewManager.isActive (Views.DRUM, Views.DRUM64, Views.PLAY, Views.PIANO, Views.CHORDS))
            viewManager.getActive ().updateNoteMapping ();
    }


    /**
     * Store the current note range for the track that is being left.
     */
    private void saveTrackNoteState ()
    {
        if (this.activeTrackPosition < 0)
            return;
        this.trackNoteStates.put (
            Integer.valueOf (this.activeTrackPosition),
            new TrackNoteState (this.scales.getOctave (), this.scales.getPianoOctave (), this.scales.getDrumOffset ()));
    }


    private boolean getMuteState ()
""",
    "per-track note state handlers",
)
# Save the drum offset at the moment it changes, rather than depending on
# Bitwig's asynchronous deselection callback to capture the outgoing track.
# This ensures the latest 0/16/32/... bank offset is already stored before
# Bitwig resets the Drum Machine bank during a track switch.
setup = replace_once(
    setup,
    "new DrumView (surface, this.model)",
    """new DrumView (surface, this.model)
        {
            @Override
            public void onOctaveUp (final ButtonEvent event)
            {
                super.onOctaveUp (event);
                if (event == ButtonEvent.DOWN)
                    PushControllerSetup.this.saveTrackNoteState ();
            }

            @Override
            public void onOctaveDown (final ButtonEvent event)
            {
                super.onOctaveDown (event);
                if (event == ButtonEvent.DOWN)
                    PushControllerSetup.this.saveTrackNoteState ();
            }
        }""",
    "live per-track drum offset persistence",
)
setup_path.write_text(setup, encoding="utf-8")


# Make Push 1 browser navigation immediate and render each bank slot from one
# local read of its current Bitwig state. Do not debounce or hold stale display frames.
browser_path = ROOT / "controller/ableton/push/mode/device/DeviceBrowserMode.java"
browser = browser_path.read_text(encoding="utf-8")
old_knob_handler = """    @Override
    public void onKnobValue (final int index, final int value)
    {
        if (!this.isKnobTouched (index))
            return;

        if (this.increaseKnobMovement ())
            this.changeValue (index, value);
    }
"""
new_knob_handler = """    @Override
    public void onKnobValue (final int index, final int value)
    {
        if (!this.isKnobTouched (index))
            return;

        // Browser navigation must react to every encoder event. The generic Push
        // mode throttle (one event out of eight) makes browsing feel unresponsive.
        this.changeValue (index, value);
    }
"""
browser = replace_once(browser, old_knob_handler, new_knob_handler, "immediate browser encoder handler")
old_filter_case = """            case DeviceBrowserMode.SELECTION_FILTER:
                final IBrowserColumnItem [] items = browser.getFilterColumn (this.filterColumn).getItems ();
                for (int i = 0; i < 16; i++)
                {
                    String text = (items[i].isSelected () ? Push1Display.SELECT_ARROW : " ") + StringUtils.shortenAndFixASCII (items[i].getName (), 18) + "                ";
                    if (!items[i].getName ().isEmpty ())
                    {
                        final String hitStr = "(" + items[i].getHitCount () + ")";
                        text = text.substring (0, 17 - hitStr.length ()) + hitStr;
                    }
                    display.setBlock (i % 4, i / 4, text);
                }
                break;
"""
new_filter_case = """            case DeviceBrowserMode.SELECTION_FILTER:
                this.updateFilterColumnDisplay (display, browser.getFilterColumn (this.filterColumn).getItems ());
                break;
"""
browser = replace_once(browser, old_filter_case, new_filter_case, "live filter column display")
old_results_case = """            case DeviceBrowserMode.SELECTION_PRESET:
                final IBrowserColumnItem [] results = browser.getResultColumnItems ();

                if (!results[0].doesExist ())
                {
                    display.clear ().setBlock (1, 1, "       No results").setBlock (1, 2, "available...").allDone ();
                    return;
                }

                for (int i = 0; i < 16; i++)
                {
                    if (i < results.length)
                        display.setBlock (i % 4, i / 4, (results[i].isSelected () ? Push1Display.SELECT_ARROW : " ") + StringUtils.shortenAndFixASCII (results[i].getName (), 16));
                    else
                        display.setBlock (i % 4, i / 4, "");
                }
                break;
"""
new_results_case = """            case DeviceBrowserMode.SELECTION_PRESET:
                final IBrowserColumnItem [] results = browser.getResultColumnItems ();

                if (results.length == 0 || !results[0].doesExist ())
                {
                    display.clear ().setBlock (1, 1, "       No results").setBlock (1, 2, "available...").allDone ();
                    return;
                }

                for (int i = 0; i < 16; i++)
                {
                    String text = "";
                    if (i < results.length && results[i].doesExist ())
                    {
                        final String name = results[i].getName ();
                        if (name != null && !name.isEmpty ())
                            text = (results[i].isSelected () ? Push1Display.SELECT_ARROW : " ") + StringUtils.shortenAndFixASCII (name, 16);
                    }
                    display.setBlock (i % 4, i / 4, text);
                }
                break;
"""
browser = replace_once(browser, old_results_case, new_results_case, "safe live preset result display")
method_anchor = """    private static String getColumnName (final Optional<IBrowserColumn> column)
"""
method = """    /**
     * Render the current Bitwig filter bank without a debounce window. Each slot's
     * values are read once into local variables so one display cell cannot combine
     * names, selection state and hit counts from different asynchronous updates.
     *
     * @param display The Push 1 text display
     * @param items The current filter bank items
     */
    private void updateFilterColumnDisplay (final ITextDisplay display, final IBrowserColumnItem [] items)
    {
        for (int i = 0; i < 16; i++)
        {
            String text = "";
            if (i < items.length)
            {
                final IBrowserColumnItem item = items[i];
                if (item.doesExist ())
                {
                    final String name = item.getName ();
                    if (name != null && !name.isEmpty ())
                    {
                        final boolean selected = item.isSelected ();
                        final int hitCount = Math.max (0, item.getHitCount ());
                        final String hitText = "(" + hitCount + ")";
                        final int labelWidth = Math.max (0, 17 - hitText.length ());
                        String label = (selected ? Push1Display.SELECT_ARROW : " ") + StringUtils.shortenAndFixASCII (name, Math.max (0, labelWidth - 1));
                        if (label.length () > labelWidth)
                            label = label.substring (0, labelWidth);
                        text = StringUtils.pad (label, labelWidth, ' ') + hitText;
                    }
                }
            }
            display.setBlock (i % 4, i / 4, text);
        }
    }


"""
browser = replace_once(browser, method_anchor, method + method_anchor, "single-read filter display renderer")
browser_path.write_text(browser, encoding="utf-8")

# StrattV4 playback-column rendering: upstream only applies the playhead color
# to empty pads through getStepColor's second overload. Its first overload
# returns the ordinary pad color for empty pads, hiding most of the vertical line.
# Restore the full-height playhead column without changing page navigation.
sequence_path = ROOT / "controller/ableton/push/view/SequencerView.java"
sequence = sequence_path.read_text(encoding="utf-8")
sequence = replace_once(
    sequence,
    "import de.mossgrabers.framework.daw.clip.INoteClip;\n",
    "import de.mossgrabers.framework.daw.clip.INoteClip;\n"
    "import de.mossgrabers.framework.daw.clip.IStepInfo;\n"
    "import de.mossgrabers.framework.daw.clip.StepState;\n",
    "SequencerView step information imports",
)
sequence = replace_once(
    sequence,
    "import de.mossgrabers.framework.view.Views;\n",
    "import de.mossgrabers.framework.view.Views;\n"
    "import de.mossgrabers.framework.view.sequencer.AbstractSequencerView;\n\n"
    "import java.util.List;\n",
    "SequencerView sequencer and collection imports",
)
sequence_anchor = """    /** {@inheritDoc} */
    @Override
    public void onGridNoteLongPress (final int note)
"""
sequence_method = """    /**
     * Keep the playhead column visible on empty pads as well as note pads.
     *
     * @param stepInfo The information about the step
     * @param highlight True if this column is the currently played step
     * @param channel The MIDI channel
     * @param step The step
     * @param pad The pad
     * @param note The note
     * @param editNotes The notes currently selected for editing
     * @return The color to display
     */
    @Override
    protected String getStepColor (final IStepInfo stepInfo, final boolean highlight, final int channel, final int step, final int pad, final int note, final List<NotePosition> editNotes)
    {
        if (highlight && (stepInfo == null || stepInfo.getState () == StepState.OFF))
            return AbstractSequencerView.COLOR_STEP_HILITE_NO_CONTENT;
        return super.getStepColor (stepInfo, highlight, channel, step, pad, note, editNotes);
    }


"""
sequence = replace_once(
    sequence,
    sequence_anchor,
    sequence_method + sequence_anchor,
    "SequenceView playhead-render insertion point",
)
sequence_path.write_text(sequence, encoding="utf-8")

# Postconditions: exactly one 64-colour selection array and all 36 new IDs.
updated_daw = daw_path.read_text(encoding="utf-8")
updated_manager = manager_path.read_text(encoding="utf-8")
updated_view = view_path.read_text(encoding="utf-8")
updated_setup = setup_path.read_text(encoding="utf-8")
for suffix, _label, _rgb, _index in EXTRA_COLORS:
    token = f"DAW_COLOR_{suffix}"
    if (updated_daw.count(f"    {token}(") != 1
            or updated_manager.count(f"(DAWColor.{token},") != 1
            or updated_view.count(f"DAWColor.{token},") != 1):
        raise SystemExit(f"Incomplete palette registration: {token}")
if updated_view.count("DAWColor.") < 64:
    raise SystemExit("ColorView palette array is incomplete")
if "RaindropsView" in updated_setup or "Views.RAINDROPS" in updated_setup:
    raise SystemExit("Raindrops sequencer must not be registered for StrattV4 Push 1")
updated_sequence = sequence_path.read_text(encoding="utf-8")
if updated_sequence.count("COLOR_STEP_HILITE_NO_CONTENT") != 1 or "clip.scrollToPage (playingPage)" in updated_sequence:
    raise SystemExit("Sequence full-height playhead rendering was not applied correctly")
updated_config = config_path.read_text(encoding="utf-8")
updated_layout = layout_path.read_text(encoding="utf-8")
updated_selector = selector_path.read_text(encoding="utf-8")
if "Views.RAINDROPS" in updated_config + updated_layout + updated_selector:
    raise SystemExit("Raindrop references remain in the Push 1 feature configuration")
if (ROOT / "controller/ableton/push/view/RaindropsView.java").exists():
    raise SystemExit("Raindrop implementation source was not removed")
if any(token in updated_setup for token in ("Drum4View", "Drum8View", "Views.DRUM4", "Views.DRUM8")):
    raise SystemExit("Drum 4 and Drum 8 views must not be registered for StrattV4 Push 1")
updated_config = config_path.read_text(encoding="utf-8")
updated_layout = layout_path.read_text(encoding="utf-8")
updated_selector = selector_path.read_text(encoding="utf-8")
if any(token in updated_config + updated_layout + updated_selector
       for token in ("Views.DRUM4", "Views.DRUM8", "NAME_DRUM4", "NAME_DRUM8")):
    raise SystemExit("Drum 4/8 references remain in the Push 1 feature configuration")
if any((ROOT / "controller/ableton/push/view" / name).exists()
       for name in ("Drum4View.java", "Drum8View.java")):
    raise SystemExit("Drum 4/8 implementation source was not removed")
print("StrattV4 palette applied: 64 Ableton colors, 64 unique Push 1 LED indices, one 8x8 page.")
