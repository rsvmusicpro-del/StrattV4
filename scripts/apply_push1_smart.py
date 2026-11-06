#!/usr/bin/env python3
"""Add the Bitwig-native SMART harmonic play view to the Push 1 build."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


# Append SMART to the shared enum so no existing Views ordinal changes.
views_path = ROOT / "framework/view/Views.java"
views = views_path.read_text(encoding="utf-8")
views = replace_once(
    views,
    "    DUMMY6;",
    "    DUMMY6,\n\n    /** Bitwig-scale-aware harmonized play view. */\n    SMART;",
    "SMART view ID",
)
views = replace_once(
    views,
    '    public static final String              NAME_POLY_SEQUENCER = "Poly Seq.";\n',
    '    public static final String              NAME_POLY_SEQUENCER = "Poly Seq.";\n'
    '    /** The name of the SMART harmonic view. */\n'
    '    public static final String              NAME_SMART          = "SMART";\n',
    "SMART view name",
)
views = replace_once(
    views,
    "        NOTE_VIEWS.add (POLY_SEQUENCER);\n",
    "        NOTE_VIEWS.add (POLY_SEQUENCER);\n"
    "        NOTE_VIEWS.add (SMART);\n"
    "        VIEW_NAMES.put (NAME_SMART, SMART);\n",
    "SMART note view registration",
)
views_path.write_text(views, encoding="utf-8")


# SMART uses Bitwig's active scale for triads. PlayView's native track-colour
# rendering calls ITrack.getColor(), so no Ableton Live integration is involved.
smart_source = """// Written for StrattV3 - Bitwig Studio / Ableton Push 1
// Licensed under the same LGPL terms as the pinned DrivenByMoss source.

package de.mossgrabers.controller.ableton.push.view;

import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;
import de.mossgrabers.framework.controller.ButtonID;
import de.mossgrabers.framework.daw.IModel;
import de.mossgrabers.framework.daw.midi.IMidiInput;
import de.mossgrabers.framework.daw.midi.MidiConstants;
import de.mossgrabers.framework.view.Views;


/**
 * SMART harmonic play view.
 *
 * All 64 pads remain scale-mapped play positions. Each pad triggers a diatonic
 * triad (root, third and fifth) calculated from Bitwig's active scale and root.
 * The inherited PlayView renderer retains the standard melodic pad palette and
 * uses the selected Bitwig track color for octave pads.
 */
public class SmartView extends PlayView
{
    /**
     * Constructor.
     *
     * @param surface The Push control surface
     * @param model The Bitwig model
     */
    public SmartView (final PushControlSurface surface, final IModel model)
    {
        super (Views.NAME_SMART, surface, model);
    }


    /** {@inheritDoc} */
    @Override
    public void onGridNote (final int key, final int velocity)
    {
        // Keep PlayView's established Delete + pad behavior unchanged.
        if (this.isButtonCombination (ButtonID.DELETE))
        {
            super.onGridNote (key, velocity);
            return;
        }

        if (!this.model.canSelectedTrackHoldNotes ())
            return;

        final int rootNote = this.keyManager.map (key);
        super.onGridNote (key, velocity);
        if (rootNote < 0)
            return;

        final int [] additionalNotes = this.scales.getThirdChord (rootNote);
        if (additionalNotes.length == 0)
            return;

        final IMidiInput input = this.surface.getMidiInput ();
        final int channel = this.surface.getConfiguration ().getMidiEditChannel ();
        final int chordVelocity = velocity > 0
            ? (this.surface.getConfiguration ().isAccentActive ()
                ? this.surface.getConfiguration ().getFixedAccentValue ()
                : velocity)
            : 0;

        // Velocity zero sends the corresponding note-off for both added chord tones.
        for (final int chordNote: additionalNotes)
        {
            if (chordNote >= 0 && chordNote <= 127)
                input.sendRawMidiEvent (MidiConstants.CMD_NOTE_ON + channel, chordNote, chordVelocity);
        }
    }
}
"""
smart_path = ROOT / "controller/ableton/push/view/SmartView.java"
smart_path.write_text(smart_source, encoding="utf-8")


# Register SMART only for Push 1. The shared enum is additive; all existing IDs
# retain their ordinals and all existing Push 1 views remain registered.
setup_path = ROOT / "controller/ableton/push/PushControllerSetup.java"
setup = setup_path.read_text(encoding="utf-8")
setup = replace_once(
    setup,
    "import de.mossgrabers.controller.ableton.push.view.SessionView;\n",
    "import de.mossgrabers.controller.ableton.push.view.SessionView;\n"
    "import de.mossgrabers.controller.ableton.push.view.SmartView;\n",
    "SMART Push view import",
)
setup = replace_once(
    setup,
    "        viewManager.register (Views.PIANO, new PianoView (surface, this.model));\n",
    "        viewManager.register (Views.PIANO, new PianoView (surface, this.model));\n"
    "        viewManager.register (Views.SMART, new SmartView (surface, this.model));\n",
    "SMART Push registration",
)
setup_path.write_text(setup, encoding="utf-8")

# Preserve the existing Program Change view and its Push 1 registration.
prg_source = ROOT / "controller/ableton/push/view/PrgChangeView.java"
if (not prg_source.is_file() or "import de.mossgrabers.controller.ableton.push.view.PrgChangeView;" not in setup
        or "viewManager.register (Views.PRG_CHANGE, new PrgChangeView (surface, this.model));" not in setup):
    raise SystemExit("Existing Push 1 Program Change view/registration must be preserved")


# SMART is the third item in the upper physical row: Sequencer, Poly Seq.,
# SMART, Drum. Keep the lower-row Tools entries Clip Length and Program Change.
selector_path = ROOT / "controller/ableton/push/mode/NoteViewSelectMode.java"
selector = selector_path.read_text(encoding="utf-8")
selector = replace_once(
    selector,
    """        Views.SEQUENCER,
        Views.POLY_SEQUENCER,
        null,
        Views.DRUM,
        null,
        null,
        null,
        null
""",
    """        Views.SEQUENCER,
        Views.POLY_SEQUENCER,
        Views.SMART,
        Views.DRUM,
        null,
        null,
        null,
        null
""",
    "SMART upper-row selector placement",
)
# Palette patch already swaps physical row selection and LED feedback. Preserve it.
selector_path.write_text(selector, encoding="utf-8")


# Add SMART to the Push 1 preferred note-view setting without removing defaults.
config_path = ROOT / "controller/ableton/push/PushConfiguration.java"
config = config_path.read_text(encoding="utf-8")
config = replace_once(
    config,
    """        Views.DRUM64,
        Views.DRUM,
        Views.SEQUENCER,
        Views.POLY_SEQUENCER
""",
    """        Views.DRUM64,
        Views.DRUM,
        Views.SEQUENCER,
        Views.POLY_SEQUENCER,
        Views.SMART
""",
    "Push preferred note views",
)
# ClipLengthView remains registered, selectable from Tools and available as
# the existing internal preferred view for audio tracks.
config_path.write_text(config, encoding="utf-8")


# Layout cycling mirrors the reduced upper-row choices and includes SMART.
layout_path = ROOT / "controller/ableton/push/command/trigger/LayoutCommand.java"
layout = layout_path.read_text(encoding="utf-8")
layout = replace_once(
    layout,
    """        else if (viewManager.isActive (Views.SEQUENCER))
            this.activatePreferredView (Views.DRUM);
        else if (viewManager.isActive (Views.DRUM))
            this.activatePreferredView (Views.SEQUENCER);
""",
    """        else if (viewManager.isActive (Views.SEQUENCER))
            this.activatePreferredView (Views.POLY_SEQUENCER);
        else if (viewManager.isActive (Views.POLY_SEQUENCER))
            this.activatePreferredView (Views.SMART);
        else if (viewManager.isActive (Views.SMART))
            this.activatePreferredView (Views.DRUM);
        else if (viewManager.isActive (Views.DRUM))
            this.activatePreferredView (Views.SEQUENCER);
""",
    "Push layout cycle for retained note views",
)
layout_path.write_text(layout, encoding="utf-8")


# Postconditions: SMART is additive; existing Tools views and physical row
# inversion remain available alongside the retained Push 1 note views.
updated_setup = setup_path.read_text(encoding="utf-8")
updated_selector = selector_path.read_text(encoding="utf-8")
updated_config = config_path.read_text(encoding="utf-8")
updated_layout = layout_path.read_text(encoding="utf-8")
if "Views.SMART, new SmartView" not in updated_setup:
    raise SystemExit("SMART view was not registered")
if "Views.SMART" not in updated_selector or "Views.PRG_CHANGE" not in updated_selector or "Views.CLIP_LENGTH" not in updated_selector:
    raise SystemExit("SMART or an existing Note Mode Tools entry is missing")
if 'display.setBlock (2, 3, "Tools:");' not in updated_selector or 'titleBottom = "Tools";' not in updated_selector:
    raise SystemExit("Existing Tools category display was not preserved")
if "Views.RAINDROPS" in updated_setup + updated_selector + updated_config + updated_layout:
    raise SystemExit("Raindrops reference remains in Push 1 setup")
if any(token in updated_setup + updated_selector + updated_config + updated_layout
       for token in ("Views.DRUM4", "Views.DRUM8", "Drum4View", "Drum8View")):
    raise SystemExit("Drum 4/8 reference remains in Push 1 setup")
if ("PrgChangeView" not in updated_setup or "viewManager.register (Views.PRG_CHANGE" not in updated_setup
        or "viewManager.register (Views.CLIP_LENGTH" not in updated_setup or not prg_source.is_file()):
    raise SystemExit("Existing Push 1 Program Change or Clip Length view/registration was removed")
if "this.activateView (VIEWS_TOP[index]);" not in updated_selector or "this.activateView (VIEWS[index]);" not in updated_selector:
    raise SystemExit("Physical Note Mode row inversion was not preserved")
smart_path = ROOT / "controller/ableton/push/view/SmartView.java"
if not smart_path.is_file():
    raise SystemExit("SMART view source is missing")
smart = smart_path.read_text(encoding="utf-8")
for token in ("getThirdChord (rootNote)", "getMidiEditChannel ()", "super.onGridNote (key, velocity)"):
    if token not in smart:
        raise SystemExit(f"SMART view missing harmonic/play behavior: {token}")
if "getGridColor (" in smart:
    raise SystemExit("SMART must inherit PLAY pad-color rendering")
print("SMART harmonic view registered; existing Clip Length and Program Change tools preserved.")
