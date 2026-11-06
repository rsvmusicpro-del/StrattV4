#!/usr/bin/env python3
"""Preserve SMART MIDI note lifetimes and guard Push 1 mapping tasks."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


tracker_source = """// Written for StrattV3 - Bitwig Studio / Ableton Push 1
// Licensed under the same LGPL terms as the pinned DrivenByMoss source.

package de.mossgrabers.framework.view;


/**
 * Bounded note ownership ledger for the Push pad grid.
 *
 * Storage is preallocated for the physical MIDI domain. A note is emitted once
 * per channel and receives Note Off only after its final pad owner releases it.
 * Methods are called from Bitwig's controller callback/scheduler thread.
 */
public final class PadMidiNoteTracker
{
    @FunctionalInterface
    public interface MidiSender
    {
        void send (int channel, int note, int velocity);
    }

    private static final int PAD_COUNT = 128;
    private static final int CHANNEL_COUNT = 16;
    private static final int NOTE_COUNT = 128;
    private static final int NOTE_WORD_COUNT = NOTE_COUNT / Long.SIZE;

    // Flat, preallocated storage avoids 128 nested arrays and keeps each pad's
    // two pitch words adjacent for predictable, allocation-free note handling.
    private final long [] padNotes = new long [PAD_COUNT * NOTE_WORD_COUNT];
    private final int [] padChannels = new int [PAD_COUNT];
    private final boolean [] activePads = new boolean [PAD_COUNT];
    // One flat table avoids 16 nested arrays while preserving channel isolation.
    private final int [] references = new int [CHANNEL_COUNT * NOTE_COUNT];
    private int activePadCount;


    public void noteOn (final int pad, final int channel, final int [] requestedNotes, final int velocity, final MidiSender sender)
    {
        if (!isValidPad (pad))
            return;
        if (velocity == 0)
        {
            this.noteOff (pad, sender);
            return;
        }
        if (velocity < 0)
            return;
        if (channel < 0 || channel >= CHANNEL_COUNT || !containsValidNote (requestedNotes))
            return;

        this.noteOff (pad, sender);
        int accepted = 0;
        for (final int note: requestedNotes)
            if (this.addNote (pad, channel, note, Math.min (127, velocity), sender))
                ++accepted;
        this.finishNoteOn (pad, channel, accepted);
    }


    /**
     * SMART overload: add the root and chord tones without allocating a
     * temporary combined pitch array on every pad press.
     */
    public void noteOn (final int pad, final int channel, final int rootNote, final int [] additionalNotes,
                 final int velocity, final MidiSender sender)
    {
        if (!isValidPad (pad))
            return;
        if (velocity == 0)
        {
            this.noteOff (pad, sender);
            return;
        }
        if (velocity < 0)
            return;
        if (channel < 0 || channel >= CHANNEL_COUNT
                || (!isValidNote (rootNote) && !containsValidNote (additionalNotes)))
            return;

        this.noteOff (pad, sender);
        final int safeVelocity = Math.min (127, velocity);
        int accepted = this.addNote (pad, channel, rootNote, safeVelocity, sender) ? 1 : 0;
        if (additionalNotes != null)
            for (final int note: additionalNotes)
                if (this.addNote (pad, channel, note, safeVelocity, sender))
                    ++accepted;
        this.finishNoteOn (pad, channel, accepted);
    }


    /**
     * Track only chord extensions while the native PlayView owns the root pitch.
     * The excluded pitch is never emitted or reference-counted by this ledger.
     */
    public void noteOnExcept (final int pad, final int channel, final int excludedNote, final int [] requestedNotes,
                              final int velocity, final MidiSender sender)
    {
        if (!isValidPad (pad))
            return;
        if (velocity == 0)
        {
            this.noteOff (pad, sender);
            return;
        }
        if (velocity < 0 || channel < 0 || channel >= CHANNEL_COUNT
                || !containsValidNoteExcept (requestedNotes, excludedNote))
            return;

        this.noteOff (pad, sender);
        int accepted = 0;
        if (requestedNotes != null)
            for (final int note: requestedNotes)
                if (note != excludedNote && this.addNote (pad, channel, note, Math.min (127, velocity), sender))
                    ++accepted;
        this.finishNoteOn (pad, channel, accepted);
    }


    private static boolean containsValidNoteExcept (final int [] notes, final int excludedNote)
    {
        if (notes == null)
            return false;
        for (final int note: notes)
            if (note != excludedNote && isValidNote (note))
                return true;
        return false;
    }


    private boolean addNote (final int pad, final int channel, final int note, final int velocity, final MidiSender sender)
    {
        if (!isValidNote (note))
            return false;
        final int word = note >>> 6;
        final int padNoteIndex = pad * NOTE_WORD_COUNT + word;
        final long mask = 1L << (note & 63);
        if ((this.padNotes[padNoteIndex] & mask) != 0)
            return false;

        this.padNotes[padNoteIndex] |= mask;
        final int referenceIndex = channel * NOTE_COUNT + note;
        final int owners = this.references[referenceIndex];
        if (owners == 0)
            sender.send (channel, note, velocity);
        this.references[referenceIndex] = owners + 1;
        return true;
    }


    private void finishNoteOn (final int pad, final int channel, final int accepted)
    {
        if (accepted == 0)
            return;
        this.padChannels[pad] = channel;
        this.activePads[pad] = true;
        ++this.activePadCount;
    }


    public void noteOff (final int pad, final MidiSender sender)
    {
        if (!isValidPad (pad) || !this.activePads[pad])
            return;

        final int channel = this.padChannels[pad];
        final int padNoteOffset = pad * NOTE_WORD_COUNT;
        for (int word = 0; word < NOTE_WORD_COUNT; ++word)
        {
            long activeNotes = this.padNotes[padNoteOffset + word];
            while (activeNotes != 0)
            {
                final int bit = Long.numberOfTrailingZeros (activeNotes);
                activeNotes &= activeNotes - 1;
                final int note = (word << 6) + bit;
                this.padNotes[padNoteOffset + word] &= ~(1L << bit);

                final int referenceIndex = channel * NOTE_COUNT + note;
                final int owners = this.references[referenceIndex];
                if (owners <= 1)
                {
                    this.references[referenceIndex] = 0;
                    sender.send (channel, note, 0);
                }
                else
                    this.references[referenceIndex] = owners - 1;
            }
        }

        this.activePads[pad] = false;
        --this.activePadCount;
    }


    public void releaseAll (final MidiSender sender)
    {
        for (int pad = 0; pad < PAD_COUNT; ++pad)
            if (this.activePads[pad])
                this.noteOff (pad, sender);
    }


    public int getActivePadCount ()
    {
        return this.activePadCount;
    }


    private static boolean containsValidNote (final int [] notes)
    {
        if (notes == null)
            return false;
        for (final int note: notes)
            if (isValidNote (note))
                return true;
        return false;
    }


    private static boolean isValidNote (final int note)
    {
        return note >= 0 && note < NOTE_COUNT;
    }


    private static boolean isValidPad (final int pad)
    {
        return pad >= 0 && pad < PAD_COUNT;
    }
}
"""

tracker_path = ROOT / "framework/view/PadMidiNoteTracker.java"
tracker_path.write_text(tracker_source, encoding="utf-8")


# Native CHORDS mode emits additional chord tones alongside the hardware-mapped
# root. Share the same bounded ownership ledger so overlapping chord tones from
# multiple held pads cannot be cut off by an early Note Off.
chord_path = ROOT / "framework/view/AbstractChordView.java"
chord = chord_path.read_text(encoding="utf-8")
chord = replace_once(
    chord,
    "import de.mossgrabers.framework.daw.midi.IMidiInput;\n",
    "",
    "remove direct chord MIDI input after ownership tracking",
)
chord = replace_once(
    chord,
    "public class AbstractChordView<S extends IControlSurface<C>, C extends Configuration> extends AbstractPlayView<S, C>\n{\n",
    "public class AbstractChordView<S extends IControlSurface<C>, C extends Configuration> extends AbstractPlayView<S, C>\n{\n"
    "    private final PadMidiNoteTracker chordNotes = new PadMidiNoteTracker ();\n"
    "    private final PadMidiNoteTracker.MidiSender chordMidiSender = (channel, note, velocity) ->\n"
    "        this.surface.getMidiInput ().sendRawMidiEvent (MidiConstants.CMD_NOTE_ON + channel, note, velocity);\n\n",
    "native CHORDS note ownership fields",
)
chord = replace_once(
    chord,
    "        super (name, surface, model, useTrackColor);\n",
    "        super (name, surface, model, useTrackColor);\n"
    "        this.model.getTrackBank ().addSelectionObserver ( (index, isSelected) -> {\n"
    "            if (isSelected)\n"
    "                this.chordNotes.releaseAll (this.chordMidiSender);\n"
    "        });\n"
    "        this.surface.getModeManager ().addChangeListener ( (previousMode, activeMode) ->\n"
    "            this.chordNotes.releaseAll (this.chordMidiSender));\n",
    "native CHORDS track/mode cleanup",
)
old_chord_method = """    /** {@inheritDoc} */
    @Override
    public void onGridNote (final int key, final int velocity)
    {
        if (!this.model.canSelectedTrackHoldNotes ())
            return;

        super.onGridNote (key, velocity);

        final int index = key - 36;
        final int row = index / this.surface.getPadGrid ().getCols ();

        final int note = this.keyManager.map (key);

        final int [] chord = this.scales.getChord (note, CHORD_INTERVALS[row]);
        // Send additional chord notes to the DAW
        final IMidiInput input = this.surface.getMidiInput ();
        final C config = this.surface.getConfiguration ();
        final int channel = config.getMidiEditChannel ();
        int vel = 0;
        if (velocity > 0)
            vel = config.isAccentActive () ? config.getFixedAccentValue () : velocity;
        for (final int element: chord)
            input.sendRawMidiEvent (MidiConstants.CMD_NOTE_ON + channel, element, vel);
    }
"""
new_chord_method = """    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        this.chordNotes.releaseAll (this.chordMidiSender);
        super.onDeactivate ();
    }


    /** {@inheritDoc} */
    @Override
    public void onGridNote (final int key, final int velocity)
    {
        // Always release tracked chord tones, even if the selected track changed
        // or can no longer receive notes since the corresponding Note On.
        if (velocity == 0)
        {
            this.chordNotes.noteOff (key, this.chordMidiSender);
            super.onGridNote (key, velocity);
            return;
        }
        if (velocity < 0 || !this.model.canSelectedTrackHoldNotes ())
            return;

        super.onGridNote (key, velocity);

        final int index = key - 36;
        final int row = index / this.surface.getPadGrid ().getCols ();
        final int note = this.keyManager.map (key);
        if (note < 0 || row < 0 || row >= CHORD_INTERVALS.length)
        {
            this.chordNotes.noteOff (key, this.chordMidiSender);
            return;
        }

        final int [] chord = this.scales.getChord (note, CHORD_INTERVALS[row]);
        if (!hasValidChordExtension (chord, note))
        {
            this.chordNotes.noteOff (key, this.chordMidiSender);
            return;
        }

        final C config = this.surface.getConfiguration ();
        final int channel = config.getMidiEditChannel ();
        final int chordVelocity = config.isAccentActive () ? config.getFixedAccentValue () : velocity;
        this.chordNotes.noteOnExcept (key, channel, note, chord, chordVelocity, this.chordMidiSender);
    }


    private static boolean hasValidChordExtension (final int [] notes, final int excludedNote)
    {
        if (notes == null)
            return false;
        for (final int note: notes)
            if (note != excludedNote && note >= 0 && note <= 127)
                return true;
        return false;
    }
"""
chord = replace_once(chord, old_chord_method, new_chord_method, "native CHORDS exact note lifecycle")
chord_path.write_text(chord, encoding="utf-8")

guard_path = ROOT / "controller/ableton/push/view/PadViewTaskGuard.java"
guard_path.write_text("// Written for StrattV3 - Bitwig Studio / Ableton Push 1\n// Licensed under the same LGPL terms as the pinned DrivenByMoss source.\n\npackage de.mossgrabers.controller.ableton.push.view;\n\n\n/**\n * Invalidates delayed pad-mapping work when a newer update or view deactivation occurs.\n * All access is made on Bitwig's scheduled host thread.\n */\nfinal class PadViewTaskGuard\n{\n    private long generation;\n\n\n    long begin ()\n    {\n        return ++this.generation;\n    }\n\n\n    void invalidate ()\n    {\n        ++this.generation;\n    }\n\n\n    boolean isCurrent (final long token)\n    {\n        return token == this.generation;\n    }\n}\n", encoding="utf-8")


# SMART: keep the exact additional pitches and channel from each Note On.
smart_path = ROOT / "controller/ableton/push/view/SmartView.java"
smart = smart_path.read_text(encoding="utf-8")
smart = replace_once(
    smart,
    "import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;\n",
    "import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;\n"
    "import de.mossgrabers.framework.view.PadMidiNoteTracker;\n",
    "shared framework MIDI ledger import",
)
smart = replace_once(
    smart,
    "public class SmartView extends PlayView\n{\n",
    "public class SmartView extends PlayView\n{\n"
    "    private final PadMidiNoteTracker chordNotes = new PadMidiNoteTracker ();\n"
    "    private final PadViewTaskGuard noteMappingGuard = new PadViewTaskGuard ();\n"
    "    private final PadMidiNoteTracker.MidiSender chordMidiSender = (noteChannel, note, noteVelocity) ->\n"
    "        this.surface.getMidiInput ().sendRawMidiEvent (MidiConstants.CMD_NOTE_ON + noteChannel, note, noteVelocity);\n\n",
    "SMART note ledger field",
)
smart = replace_once(
    smart,
    "        super (Views.NAME_SMART, surface, model);\n",
    "        super (Views.NAME_SMART, surface, model);\n"
    "        this.model.getTrackBank ().addSelectionObserver ( (index, isSelected) -> {\n"
    "            if (isSelected)\n"
    "                this.releaseChordNotes ();\n"
    "        });\n"
    "        this.surface.getModeManager ().addChangeListener ( (previousMode, activeMode) -> {\n"
    "            this.releaseChordNotes ();\n"
    "            this.keyManager.clearPressedKeys ();\n"
    "        });\n",
    "SMART track-change cleanup",
)
old_smart_method = """    @Override
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
"""
new_smart_method = """    @Override
    public void updateNoteMapping ()
    {
        // Ignore mapping notifications delivered while this view is inactive.
        if (this.surface.getViewManager ().getActive () != this)
            return;

        // Each delayed stage must still belong to the active view and the
        // newest mapping request. This prevents stale tasks from overwriting
        // the next view's MIDI translation after a rapid view/track change.
        final long generation = this.noteMappingGuard.begin ();
        this.surface.setKeyTranslationTable (EMPTY_TABLE);
        this.surface.scheduleTask ( () -> {
            if (!this.noteMappingGuard.isCurrent (generation) || this.surface.getViewManager ().getActive () != this)
                return;

            final int [] matrix = this.getMapping ();
            this.surface.scheduleTask ( () -> {
                if (!this.noteMappingGuard.isCurrent (generation) || this.surface.getViewManager ().getActive () != this)
                    return;

                this.keyManager.clearPressedKeys ();
                this.keyManager.setNoteMatrix (matrix);
                this.surface.setKeyTranslationTable (EMPTY_TABLE);
            }, 6);
        }, 100);
    }


    @Override
    public void onGridNote (final int key, final int velocity)
    {
        if (this.isButtonCombination (ButtonID.DELETE))
        {
            if (velocity == 0)
            {
                this.releaseChordNote (key);
                this.keyManager.setKeyPressed (key, 0);
            }
            super.onGridNote (key, velocity);
            return;
        }

        // Note Off must be handled even if the selected track has changed.
        if (velocity == 0)
        {
            this.releaseChordNote (key);
            this.keyManager.setKeyPressed (key, 0);
            super.onGridNote (key, velocity);
            return;
        }
        if (!this.model.canSelectedTrackHoldNotes ())
            return;

        final int rootNote = this.keyManager.map (key);
        super.onGridNote (key, velocity);
        if (rootNote < 0)
        {
            this.releaseChordNote (key);
            return;
        }

        final int [] additionalNotes = this.scales.getThirdChord (rootNote);
        // An out-of-scale root or a chord above MIDI 127 has no playable
        // extensions. Clear any previous pad-owned tones instead of leaving
        // stale notes alive when a mapping is retriggered or invalidated.
        if (!hasValidChordExtension (additionalNotes))
        {
            this.releaseChordNote (key);
            return;
        }
        final int channel = this.surface.getConfiguration ().getMidiEditChannel ();
        final int chordVelocity = this.surface.getConfiguration ().isAccentActive ()
            ? this.surface.getConfiguration ().getFixedAccentValue ()
            : velocity;
        this.chordNotes.noteOn (key, channel, additionalNotes, chordVelocity, this.chordMidiSender);
    }


    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        this.noteMappingGuard.invalidate ();
        this.releaseChordNotes ();
        this.keyManager.clearPressedKeys ();
        super.onDeactivate ();
    }


    private static boolean hasValidChordExtension (final int [] notes)
    {
        if (notes == null)
            return false;
        for (final int note: notes)
            if (note >= 0 && note <= 127)
                return true;
        return false;
    }


    private void releaseChordNote (final int key)
    {
        this.chordNotes.noteOff (key, this.chordMidiSender);
    }


    private void releaseChordNotes ()
    {
        this.chordNotes.releaseAll (this.chordMidiSender);
    }
"""
smart = replace_once(smart, old_smart_method, new_smart_method, "SMART exact note lifecycle")
smart = replace_once(
    smart,
    "import de.mossgrabers.framework.daw.midi.IMidiInput;\n",
    "",
    "remove obsolete IMidiInput import after explicit MIDI tracking",
)
if "IMidiInput" in smart:
    raise SystemExit("SMART retains an unused IMidiInput import after MIDI tracking")
smart_path.write_text(smart, encoding="utf-8")

# Apply the same generation guard to every native Play-family view, not
# only the two custom harmonic views. The 100 ms calculation and the 6 ms
# translation-table write must belong to the currently active view and to the
# latest request; deactivation/reactivation invalidates earlier work.
abstract_view_path = ROOT / "framework/featuregroup/AbstractView.java"
abstract_view = abstract_view_path.read_text(encoding="utf-8")
abstract_view = replace_once(
    abstract_view,
    "    private AftertouchCommand     aftertouchCommand;\n",
    "    private AftertouchCommand     aftertouchCommand;\n"
    "    private long                  noteMappingGeneration;\n",
    "global note mapping generation field",
)
abstract_view = replace_once(
    abstract_view,
    """    public void onActivate ()
    {
        this.updateNoteMapping ();
    }
""",
    """    public void onActivate ()
    {
        ++this.noteMappingGeneration;
        this.updateNoteMapping ();
    }
""",
    "invalidate older mappings on view activation",
)
abstract_view = replace_once(
    abstract_view,
    """    public void onDeactivate ()
    {
        // Intentionally empty
    }
""",
    """    public void onDeactivate ()
    {
        ++this.noteMappingGeneration;
        this.keyManager.clearPressedKeys ();
    }
""",
    "invalidate pending mappings on view deactivation",
)
abstract_view = replace_once(
    abstract_view,
    """    protected void delayedUpdateNoteMapping (final int [] matrix)
    {
        this.surface.scheduleTask ( () -> {
            this.keyManager.setNoteMatrix (matrix);
            if (matrix.length == 128)
                this.surface.setKeyTranslationTable (this.scales.translateMatrixToGrid (matrix));
        }, 6);
    }
""",
    """    protected final long beginNoteMappingUpdate ()
    {
        return ++this.noteMappingGeneration;
    }


    protected final boolean isNoteMappingUpdateCurrent (final long generation)
    {
        return generation == this.noteMappingGeneration && this.surface.getViewManager ().getActive () == this;
    }


    protected void delayedUpdateNoteMapping (final int [] matrix)
    {
        this.delayedUpdateNoteMapping (matrix, this.beginNoteMappingUpdate ());
    }


    protected void delayedUpdateNoteMapping (final int [] matrix, final long generation)
    {
        this.surface.scheduleTask ( () -> {
            if (!this.isNoteMappingUpdateCurrent (generation))
                return;
            this.keyManager.setNoteMatrix (matrix);
            if (matrix.length == 128)
                this.surface.setKeyTranslationTable (this.scales.translateMatrixToGrid (matrix));
        }, 6);
    }
""",
    "guard final delayed mapping application for every view",
)
abstract_view_path.write_text(abstract_view, encoding="utf-8")

abstract_play_path = ROOT / "framework/view/AbstractPlayView.java"
abstract_play = abstract_play_path.read_text(encoding="utf-8")
abstract_play = replace_once(
    abstract_play,
    """    public void updateNoteMapping ()
    {
        this.surface.scheduleTask ( () -> this.delayedUpdateNoteMapping (this.getMapping ()), 100);
    }
""",
    """    public void updateNoteMapping ()
    {
        final long generation = this.beginNoteMappingUpdate ();
        this.surface.scheduleTask ( () -> {
            if (!this.isNoteMappingUpdateCurrent (generation))
                return;
            this.delayedUpdateNoteMapping (this.getMapping (), generation);
        }, 100);
    }
""",
    "guard first delayed mapping calculation for every Play-family view",
)
abstract_play_path.write_text(abstract_play, encoding="utf-8")

for path, tokens in (
    (abstract_view_path, ("private long                  noteMappingGeneration;", "++this.noteMappingGeneration;", "beginNoteMappingUpdate ()", "isNoteMappingUpdateCurrent (final long generation)", "this.surface.getViewManager ().getActive () == this", "delayedUpdateNoteMapping (final int [] matrix, final long generation)")),
    (abstract_play_path, ("final long generation = this.beginNoteMappingUpdate ();", "this.isNoteMappingUpdateCurrent (generation)", "this.delayedUpdateNoteMapping (this.getMapping (), generation)", "}, 100);")),
):
    content = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in content:
            raise SystemExit(f"{path.name}: missing global mapping guard postcondition: {token}")

# Shutdown: Bitwig calls AbstractControlSurface.shutdown(), which delegates
# to PushControlSurface.internalShutdown(). The upstream implementation turns
# off LEDs/displays but does not deactivate the active view. Explicitly invoke
# the active view's lifecycle hook before hardware shutdown so tracked MIDI
# notes and delayed view work are released even when Bitwig exits directly.
surface_path = ROOT / "controller/ableton/push/controller/PushControlSurface.java"
surface = surface_path.read_text(encoding="utf-8")
surface = replace_once(
    surface,
    "import de.mossgrabers.framework.controller.grid.PadGridImpl;\n",
    "import de.mossgrabers.framework.controller.grid.PadGridImpl;\n"
    "import de.mossgrabers.framework.featuregroup.IView;\n",
    "PushControlSurface active view import",
)
surface = replace_once(
    surface,
    """    protected void internalShutdown ()
    {
        this.setRibbonMode (PUSH_RIBBON_PITCHBEND);
        this.setRibbonValue (0);

        super.internalShutdown ();
    }
""",
    """    protected void internalShutdown ()
    {
        // A direct Bitwig shutdown does not necessarily pass through
        // FeatureGroupManager's normal view-deactivation path.
        final IView activeView = this.getViewManager ().getActive ();
        if (activeView != null)
            activeView.onDeactivate ();

        this.setRibbonMode (PUSH_RIBBON_PITCHBEND);
        this.setRibbonValue (0);

        super.internalShutdown ();
    }
""",
    "Push 1 active view shutdown cleanup",
)
surface_path.write_text(surface, encoding="utf-8")
updated_surface = surface_path.read_text(encoding="utf-8")
for token in ("final IView activeView = this.getViewManager ().getActive ();",
              "if (activeView != null)", "activeView.onDeactivate ();",
              "super.internalShutdown ();"):
    if token not in updated_surface:
        raise SystemExit(f"PushControlSurface shutdown postcondition failed: {token}")

print("SMART MIDI lifecycle, async guards and Push 1 shutdown cleanup applied.")
