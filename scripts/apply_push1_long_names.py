#!/usr/bin/env python3
"""Apply one-line, dot-marked name fitting to the Push 1 text display."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


# Fit only at the final hardware display boundary. Transliteration happens before
# measuring so expanded ASCII spellings cannot overflow the physical cell.
display_path = ROOT / "controller/Push1Display.java"
display = display_path.read_text(encoding="utf-8")

anchor = """    /** {@inheritDoc} */
    @Override
    public void shutdown ()
"""
helper = """    /**
     * Fit text to one physical Push 1 display cell or block.
     *
     * Long text is cut on the same line and the last available character is a
     * period. French translation and ASCII conversion are applied before
     * measuring because transliteration can change the resulting length.
     *
     * @param value The original text
     * @param width The available number of characters
     * @return The fitted text, never wider than width
     */
    public static String fitText (final String value, final int width)
    {
        return fitText (value, width, false);
    }


    /**
     * Format a Note Mode label in uppercase at the final display boundary.
     *
     * @param value The original view name
     * @param width The available number of characters
     * @return The translated, uppercase and fitted label
     */
    public static String fitModeName (final String value, final int width)
    {
        return fitText (value, width, true);
    }


    private static String fitText (final String value, final int width, final boolean uppercase)
    {
        if (value == null || value.isEmpty () || width <= 0)
            return "";

        String text = Push1French.toAscii (Push1French.translate (value)).stripTrailing ();
        if (uppercase)
            text = text.toUpperCase (java.util.Locale.ROOT);
        if (text.length () <= width)
            return text;
        if (width == 1)
            return ".";
        return text.substring (0, width - 1) + ".";
    }


"""
display = replace_once(display, anchor, helper + anchor, "Push1Display fitText helper")

old_block = """    public ITextDisplay setBlock (final int row, final int block, final String value)
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
"""
new_block = """    public ITextDisplay setBlock (final int row, final int block, final String value)
    {
        final String fitted = fitText (value, 17);
        final int cell = 2 * block;
        if (fitted.length () > 9)
        {
            this.cells[row * 8 + cell] = fitted.substring (0, 9);
            this.cells[row * 8 + cell + 1] = StringUtils.pad (fitted.substring (9), 8, ' ');
        }
        else
        {
            this.cells[row * 8 + cell] = StringUtils.pad (fitted, 9, ' ');
            this.clearCell (row, cell + 1);
        }
        return this;
    }
"""
display = replace_once(display, old_block, new_block, "17-character block fitting")

old_cell = """    public ITextDisplay setCell (final int row, final int cell, final String value)
    {
        this.cells[row * 8 + cell] = StringUtils.pad (Push1French.translate (value), 8, ' ') + (cell % 2 == 0 ? " " : "");
        return this;
    }
"""
new_cell = """    public ITextDisplay setCell (final int row, final int cell, final String value)
    {
        this.cells[row * 8 + cell] = StringUtils.pad (fitText (value, 8), 8, ' ') + (cell % 2 == 0 ? " " : "");
        return this;
    }
"""
display = replace_once(display, old_cell, new_cell, "8-character cell fitting")
display_path.write_text(display, encoding="utf-8")


# Track labels: retain the complete source name until setCell applies the 8-char
# hardware limit. Selection and group glyphs remain part of the fitted string.
track_path = ROOT / "mode/track/AbstractTrackMode.java"
track = track_path.read_text(encoding="utf-8")
track = replace_once(
    track,
    "            String trackName = t.getName ();",
    "            String trackName = t.getName ().stripLeading ();",
    "remove leading whitespace from track and group names",
)
track = replace_once(
    track,
    "            final String n = StringUtils.shortenAndFixASCII (trackName, isSel ? 7 : 8);",
    "            final String n = trackName;",
    "explicit one-line track name fitting",
)
track = replace_once(
    track,
    "            d.setCell (3, i, isSel ? Push1Display.SELECT_ARROW + n : n);",
    "            d.setCell (3, i, isSel ? Push1Display.SELECT_ARROW + n.stripLeading () : n);",
    "remove gap after selected track marker",
)
track_path.write_text(track, encoding="utf-8")


# Session clip and scene names: request the full name from the framework instead
# of pre-truncating to eight characters before the Push display can mark it.
session_path = ROOT / "mode/SessionMode.java"
session = session_path.read_text(encoding="utf-8")
session = replace_once(
    session,
    "                final String n = StringUtils.shortenAndFixASCII (scene.getName (8), isSel ? 7 : 8);",
    "                final String n = scene.getName (128);",
    "explicit one-line scene name fitting",
)
session = replace_once(
    session,
    "                String name = slot.getName (8);",
    "                String name = slot.getName (128);",
    "full clip name before display fitting",
)
session = replace_once(
    session,
    "                display.setCell (row, col, StringUtils.shortenAndFixASCII (name, 8));",
    "                display.setCell (row, col, Push1Display.fitText (name, 8));",
    "explicit one-line clip name fitting",
)
session_path.write_text(session, encoding="utf-8")


# Track Details previously continued a long track title in the neighbouring
# block. Keep the entire information on one line and let setBlock add the dot.
details_path = ROOT / "mode/track/TrackDetailsMode.java"
details = details_path.read_text(encoding="utf-8")
details = replace_once(
    details,
    """        display.setBlock (0, 0, firstBlock);
        if (firstBlock.length () > 17)
            display.setBlock (0, 1, firstBlock.substring (17).trim ());
""",
    """        display.setBlock (0, 0, firstBlock);
""",
    "single-line track details title",
)
details_path.write_text(details, encoding="utf-8")


# Device Layer Details also used to continue one layer name in the next block.
layer_details_path = ROOT / "mode/device/DeviceLayerDetailsMode.java"
layer_details = layer_details_path.read_text(encoding="utf-8")
layer_details = replace_once(
    layer_details,
    """        display.setBlock (0, 0, firstBlock);
        if (layerName.length () > 17)
            display.setBlock (0, 1, firstBlock.substring (17).trim ());
""",
    """        display.setBlock (0, 0, firstBlock);
""",
    "single-line device layer details title",
)
layer_details_path.write_text(layer_details, encoding="utf-8")


# Device layer names are also full names until they reach the 8-character cell.
layer_path = ROOT / "mode/device/DeviceLayerMode.java"
layer = layer_path.read_text(encoding="utf-8")
layer = replace_once(
    layer,
    "            final String n = StringUtils.shortenAndFixASCII (layer.getName (), layer.isSelected () ? 7 : 8);",
    "            final String n = layer.getName ();",
    "full device layer name before display fitting",
)
layer_path.write_text(layer, encoding="utf-8")


# Browser columns, filter entries and presets use the same final-fit policy.
browser_path = ROOT / "mode/device/DeviceBrowserMode.java"
browser = browser_path.read_text(encoding="utf-8")
browser = replace_once(
    browser,
    "                    String name = column.isEmpty () ? \"\" : StringUtils.shortenAndFixASCII (column.get ().getName (), 8);",
    "                    String name = column.isEmpty () ? \"\" : column.get ().getName ();",
    "full Browser column name before display fitting",
)
browser = replace_once(
    browser,
    "                            text = (results[i].isSelected () ? Push1Display.SELECT_ARROW : \" \") + StringUtils.shortenAndFixASCII (name, 16);",
    "                            text = (results[i].isSelected () ? Push1Display.SELECT_ARROW : \" \") + name;",
    "full Browser preset name before display fitting",
)
browser = replace_once(
    browser,
    "                        String label = (selected ? Push1Display.SELECT_ARROW : \" \") + StringUtils.shortenAndFixASCII (name, Math.max (0, labelWidth - 1));",
    "                        String label = Push1Display.fitText ((selected ? Push1Display.SELECT_ARROW : \" \") + name, labelWidth);",
    "dot-marked Browser filter label",
)
browser = replace_once(
    browser,
    """                String selectedResult = browser.getSelectedResult ();
                selectedResult = selectedResult == null || selectedResult.isBlank () ? "None" : StringUtils.shortenAndFixASCII (selectedResult, 18);""",
    """                String selectedResult = browser.getSelectedResult ();
                selectedResult = selectedResult == null || selectedResult.isBlank () ? "None" : selectedResult;""",
    "full selected Browser result before display fitting",
)
browser = replace_once(
    browser,
    """                final String sel1 = selectedResult.length () > 17 ? selectedResult.substring (0, 17) : selectedResult;
                final String sel2 = selectedResult.length () > 17 ? selectedResult.substring (17, selectedResult.length ()) : "";
                display.setBlock (3, 2, sel1).setCell (3, 6, sel2);""",
    """                display.setBlock (3, 2, selectedResult);""",
    "single-block selected Browser result",
)
browser_path.write_text(browser, encoding="utf-8")


# Note View Select: preserve the complete dynamic view name until the final
# Push 1 cell formatter applies the 8-character, one-line, dot-marked policy.
note_mode_path = ROOT / "mode/NoteViewSelectMode.java"
note_mode = note_mode_path.read_text(encoding="utf-8")
note_mode = replace_once(
    note_mode,
    'value = (viewManager.isActive (VIEWS[i]) ? Push1Display.SELECT_ARROW : "") + StringUtils.optimizeName (view.getName (), 8);',
    'value = Push1Display.fitModeName ((viewManager.isActive (VIEWS[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);',
    "DrivenByMoss triangle selection marker in Note View first row",
)
note_mode = replace_once(
    note_mode,
    'value = (viewManager.isActive (VIEWS_TOP[i]) ? Push1Display.SELECT_ARROW : "") + StringUtils.optimizeName (view.getName (), 8);',
    'value = Push1Display.fitModeName ((viewManager.isActive (VIEWS_TOP[i]) ? Push1Display.SELECT_ARROW : "") + view.getName (), 8);',
    "DrivenByMoss triangle selection marker in Note View second row",
)
note_mode = replace_once(
    note_mode,
    "import de.mossgrabers.framework.utils.StringUtils;\n",
    "",
    "remove obsolete Note View StringUtils import",
)
note_mode_path.write_text(note_mode, encoding="utf-8")

# Postconditions make a changed upstream anchor or an incomplete patch fail
# the transactional staging build instead of silently shipping partial work.
updated_display = display_path.read_text(encoding="utf-8")
updated_track = track_path.read_text(encoding="utf-8")
updated_session = session_path.read_text(encoding="utf-8")
updated_details = details_path.read_text(encoding="utf-8")
updated_layer = layer_path.read_text(encoding="utf-8")
updated_layer_details = layer_details_path.read_text(encoding="utf-8")
updated_browser = browser_path.read_text(encoding="utf-8")

checks = (
    (updated_display, "fitText (value, 17)", "17-character block fitter"),
    (updated_display, "fitText (value, 8)", "8-character cell fitter"),
    (updated_display, "fitModeName (final String value, final int width)", "uppercase Note Mode formatter"),
    (note_mode, "Push1Display.fitModeName", "uppercase Note Mode display boundary"),
    (note_mode, "view.getName ()", "full Note View name before cell fitting"),
    (updated_display, 'text.substring (0, width - 1) + "."', "dot-marked truncation"),
    (updated_track, "String trackName = t.getName ().stripLeading ();", "track and group names have no leading whitespace"),
    (updated_track, "final String n = trackName;", "full track name before cell fitting"),
    (updated_track, "d.setCell (3, i, isSel ? Push1Display.SELECT_ARROW + n.stripLeading () : n);", "selected track label has no gap after marker"),
    (updated_session, "final String n = scene.getName (128);", "full scene name before cell fitting"),
    (updated_session, "display.setCell (row, col, isSel ? Push1Display.SELECT_ARROW + n : n);", "single scene cell write"),
    (updated_session, "slot.getName (128)", "full clip name"),
    (updated_session, "display.setCell (row, col, Push1Display.fitText (name, 8));", "explicit clip display fitting"),
    (updated_details, "display.setBlock (0, 0, firstBlock);", "single-line track title"),
    (updated_layer, "final String n = layer.getName ();", "full device layer name"),
    (updated_layer_details, "display.setBlock (0, 0, firstBlock);", "single-line layer details title"),
    (updated_browser, "Push1Display.fitText", "Browser filter fitting"),
    (updated_browser, "display.setBlock (3, 2, selectedResult);", "single-block selected result"),
    (updated_browser, 'String name = column.isEmpty () ? "" : column.get ().getName ();', "full Browser header name"),
)
for source, token, label in checks:
    if token not in source:
        raise SystemExit(f"Long-name display postcondition failed: {label}")

if "StringUtils.optimizeName (view.getName (), 8)" in note_mode:
    raise SystemExit("Note View names must reach the final display formatter unshortened")
if note_mode.count ("Push1Display.fitModeName") != 2:
    raise SystemExit("Both Note View rows must use the uppercase display formatter")
if note_mode.count ("Push1Display.SELECT_ARROW") != 2 or '? "O" : ""' in note_mode:
    raise SystemExit("Each Note View row must use exactly one DrivenByMoss triangle selection marker")
if "StringUtils" in note_mode:
    raise SystemExit("Obsolete StringUtils import must be removed from Note View Select")

if ("firstBlock.substring (17)" in updated_details or "firstBlock.substring (17)" in updated_layer_details
        or "selectedResult.substring (17)" in updated_browser or "setCell (3, 6, sel2)" in updated_browser
        or "shortenAndFixASCII (selectedResult" in updated_browser):
    raise SystemExit("Track or layer Details must not split one name across display blocks")
if "shortenAndFixASCII (trackName" in updated_track:
    raise SystemExit("Track names must reach the final display fitter unshortened")
if "shortenAndFixASCII (name, 8)" in updated_session:
    raise SystemExit("Clip names must reach the final display fitter unshortened")

print("Push 1 long-name display fitting applied: 8-char cells, 17-char blocks, one line, final period, DrivenByMoss triangle Note View marker.")
