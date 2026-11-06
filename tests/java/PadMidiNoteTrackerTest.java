package de.mossgrabers.controller.ableton.push.view;

import de.mossgrabers.framework.view.PadMidiNoteTracker;

import java.util.ArrayList;
import java.util.List;


/** Dependency-free behavioral tests for PadMidiNoteTracker. */
public final class PadMidiNoteTrackerTest
{
    private static final class Event
    {
        final int channel;
        final int note;
        final int velocity;

        Event (final int channel, final int note, final int velocity)
        {
            this.channel = channel;
            this.note = note;
            this.velocity = velocity;
        }

        @Override
        public String toString ()
        {
            return this.channel + ":" + this.note + ":" + this.velocity;
        }
    }

    private static final class Recorder implements PadMidiNoteTracker.MidiSender
    {
        final List<Event> events = new ArrayList<> ();

        @Override
        public void send (final int channel, final int note, final int velocity)
        {
            this.events.add (new Event (channel, note, velocity));
        }

        void expect (final int index, final int channel, final int note, final int velocity)
        {
            final Event actual = this.events.get (index);
            if (actual.channel != channel || actual.note != note || actual.velocity != velocity)
                throw new AssertionError ("event " + index + ": expected "
                    + channel + ":" + note + ":" + velocity + ", got " + actual);
        }
    }


    public static void main (final String [] args)
    {
        sharedNotesStayOnUntilTheLastPadReleases ();
        aRootNoteSharedWithAnotherPadsChordIsReferenceCounted ();
        noteOffUsesTheOriginalNotesAfterScaleChanges ();
        deactivationReleasesEveryOutstandingNoteExactlyOnce ();
        channelsAreIndependentAndDuplicatePitchesAreDeduplicated ();
        retriggeringOnePadReleasesItsPreviousNotes ();
        retriggeringOnePadPreservesSharedNotesOwnedByAnotherPad ();
        invalidMidiInputsAndUnknownReleasesAreIgnored ();
        padBoundsAndMaximumGridIndexAreSafe ();
        invalidReplacementDoesNotReleaseAnActivePad ();
        smartRootAndChordShareOneAllocationFreeLedgerEntry ();
        all128PitchBitsAreEmittedAndReleasedInTheirOwnWord ();
        nativeRootIsExcludedFromTrackedChordExtensions ();
        System.out.println ("PadMidiNoteTracker: 13 behavioral tests passed.");
    }


    private static void sharedNotesStayOnUntilTheLastPadReleases ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 64, 67 }, 100, midi);
        tracker.noteOn (37, 0, new int [] { 64, 71 }, 90, midi);
        if (midi.events.size () != 3)
            throw new AssertionError ("shared note should receive only one Note On");
        midi.expect (0, 0, 64, 100);
        midi.expect (1, 0, 67, 100);
        midi.expect (2, 0, 71, 90);

        tracker.noteOff (36, midi);
        if (midi.events.size () != 4)
            throw new AssertionError ("shared note was released while pad 37 still owns it");
        midi.expect (3, 0, 67, 0);

        tracker.noteOff (37, midi);
        if (midi.events.size () != 6)
            throw new AssertionError ("last release must stop both remaining notes");
        midi.expect (4, 0, 64, 0);
        midi.expect (5, 0, 71, 0);
    }


    private static void aRootNoteSharedWithAnotherPadsChordIsReferenceCounted ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();

        // Pad 36 owns a chord containing 64; pad 37 plays 64 as its root.
        // Both must share one ledger entry, irrespective of each note's role.
        tracker.noteOn (36, 0, new int [] { 60, 64, 67 }, 100, midi);
        tracker.noteOn (37, 0, new int [] { 64, 71, 74 }, 90, midi);
        if (midi.events.size () != 5)
            throw new AssertionError ("shared root/chord pitch should be emitted once");
        midi.expect (0, 0, 60, 100);
        midi.expect (1, 0, 64, 100);
        midi.expect (2, 0, 67, 100);
        midi.expect (3, 0, 71, 90);
        midi.expect (4, 0, 74, 90);

        tracker.noteOff (36, midi);
        if (midi.events.size () != 7)
            throw new AssertionError ("first pad must release only its unshared pitches");
        midi.expect (5, 0, 60, 0);
        midi.expect (6, 0, 67, 0);

        tracker.noteOff (37, midi);
        if (midi.events.size () != 10)
            throw new AssertionError ("last root/chord owner did not release shared pitches");
        midi.expect (7, 0, 64, 0);
        midi.expect (8, 0, 71, 0);
        midi.expect (9, 0, 74, 0);
    }


    private static void noteOffUsesTheOriginalNotesAfterScaleChanges ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (40, 2, new int [] { 60, 64 }, 100, midi);
        // The current scale may now map the held pad to 62/65. The ledger must
        // still release the actual pitches emitted before that change.
        tracker.noteOff (40, midi);
        midi.expect (0, 2, 60, 100);
        midi.expect (1, 2, 64, 100);
        midi.expect (2, 2, 60, 0);
        midi.expect (3, 2, 64, 0);
        if (midi.events.size () != 4)
            throw new AssertionError ("scale change produced unexpected MIDI events");
    }


    private static void deactivationReleasesEveryOutstandingNoteExactlyOnce ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 60, 64 }, 100, midi);
        tracker.noteOn (37, 0, new int [] { 64, 67 }, 100, midi);
        tracker.releaseAll (midi);
        if (tracker.getActivePadCount () != 0)
            throw new AssertionError ("deactivation left active pads in the ledger");
        int offs64 = 0;
        for (final Event event: midi.events)
            if (event.note == 64 && event.velocity == 0)
                offs64++;
        if (offs64 != 1)
            throw new AssertionError ("shared note must receive exactly one final Note Off");
        tracker.releaseAll (midi);
        if (midi.events.size () != 6)
            throw new AssertionError ("second cleanup must be idempotent");
    }


    private static void channelsAreIndependentAndDuplicatePitchesAreDeduplicated ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 60, 60, 128, -1 }, 100, midi);
        tracker.noteOn (37, 1, new int [] { 60 }, 100, midi);
        if (midi.events.size () != 2)
            throw new AssertionError ("channel-specific notes must be independent");
        tracker.noteOff (36, midi);
        tracker.noteOff (37, midi);
        if (midi.events.size () != 4)
            throw new AssertionError ("each channel must receive its own Note Off");
        midi.expect (0, 0, 60, 100);
        midi.expect (1, 1, 60, 100);
        midi.expect (2, 0, 60, 0);
        midi.expect (3, 1, 60, 0);
    }



    private static void retriggeringOnePadPreservesSharedNotesOwnedByAnotherPad ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 60, 64 }, 100, midi);
        tracker.noteOn (37, 0, new int [] { 60, 67 }, 100, midi);
        tracker.noteOn (36, 0, new int [] { 60, 65 }, 90, midi);

        if (midi.events.size () != 5)
            throw new AssertionError ("retriggering one pad cut or duplicated another pad's shared note");
        midi.expect (0, 0, 60, 100);
        midi.expect (1, 0, 64, 100);
        midi.expect (2, 0, 67, 100);
        midi.expect (3, 0, 64, 0);
        midi.expect (4, 0, 65, 90);

        tracker.noteOff (37, midi);
        if (midi.events.size () != 6)
            throw new AssertionError ("shared note was released before the retriggered pad");
        midi.expect (5, 0, 67, 0);
        tracker.noteOff (36, midi);
        if (midi.events.size () != 8)
            throw new AssertionError ("last owner did not release the shared note and retriggered tone");
        midi.expect (6, 0, 60, 0);
        midi.expect (7, 0, 65, 0);
    }


    private static void invalidMidiInputsAndUnknownReleasesAreIgnored ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 16, new int [] { 60 }, 100, midi);
        tracker.noteOn (37, 0, new int [] { -1, 128 }, 100, midi);
        tracker.noteOn (38, 0, null, 100, midi);
        tracker.noteOn (39, 0, new int [] { 60 }, 0, midi);
        tracker.noteOff (999, midi);
        tracker.releaseAll (midi);
        if (!midi.events.isEmpty () || tracker.getActivePadCount () != 0)
            throw new AssertionError ("invalid MIDI input or unknown release changed tracker state");
    }

    private static void padBoundsAndMaximumGridIndexAreSafe ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (-1, 0, new int [] { 60 }, 100, midi);
        tracker.noteOn (128, 0, new int [] { 61 }, 100, midi);
        tracker.noteOn (127, 15, new int [] { 127 }, 100, midi);
        if (tracker.getActivePadCount () != 1 || midi.events.size () != 1)
            throw new AssertionError ("pad bounds or highest MIDI channel/note were mishandled");
        midi.expect (0, 15, 127, 100);
        tracker.noteOff (127, midi);
        tracker.noteOff (127, midi);
        if (tracker.getActivePadCount () != 0 || midi.events.size () != 2)
            throw new AssertionError ("maximum pad release was not safe and idempotent");
        midi.expect (1, 15, 127, 0);
    }

    private static void invalidReplacementDoesNotReleaseAnActivePad ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 60, 64 }, 200, midi);
        tracker.noteOn (36, 16, new int [] { 67 }, 100, midi);
        tracker.noteOn (36, 0, new int [] { -1, 128 }, 100, midi);
        if (tracker.getActivePadCount () != 1 || midi.events.size () != 2)
            throw new AssertionError ("invalid replacement must not release a valid held chord");
        midi.expect (0, 0, 60, 127);
        midi.expect (1, 0, 64, 127);

        // A zero-velocity Note On is a valid release for the original owner.
        tracker.noteOn (36, 0, new int [] { 61 }, 0, midi);
        if (tracker.getActivePadCount () != 0 || midi.events.size () != 4)
            throw new AssertionError ("zero-velocity Note On did not release the original chord");
        midi.expect (2, 0, 60, 0);
        midi.expect (3, 0, 64, 0);
    }

    private static void smartRootAndChordShareOneAllocationFreeLedgerEntry ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 3, 60, new int [] { 64, 67, 64 }, 100, midi);
        tracker.noteOn (37, 3, 64, new int [] { 67, 71 }, 90, midi);
        if (midi.events.size () != 4)
            throw new AssertionError ("SMART root/chord overload did not deduplicate shared pitches");
        midi.expect (0, 3, 60, 100);
        midi.expect (1, 3, 64, 100);
        midi.expect (2, 3, 67, 100);
        midi.expect (3, 3, 71, 90);
        tracker.noteOff (36, midi);
        if (midi.events.size () != 5)
            throw new AssertionError ("SMART shared chord notes were released too early");
        midi.expect (4, 3, 60, 0);
        tracker.noteOff (37, midi);
        if (midi.events.size () != 8)
            throw new AssertionError ("SMART root/chord owners did not release exactly once");
        midi.expect (5, 3, 64, 0);
        midi.expect (6, 3, 67, 0);
        midi.expect (7, 3, 71, 0);

        tracker.noteOn (38, 3, 60, new int [] { 64 }, 100, midi);
        tracker.noteOn (38, 3, 62, new int [] { 65 }, -1, midi);
        if (tracker.getActivePadCount () != 1 || midi.events.size () != 10)
            throw new AssertionError ("negative velocity must not release a valid SMART pad");
        tracker.noteOff (38, midi);
        if (midi.events.size () != 12)
            throw new AssertionError ("SMART pad remained active after final release");
    }

    private static void nativeRootIsExcludedFromTrackedChordExtensions ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        // PlayView sends root 60 natively; the ledger must own only extensions.
        tracker.noteOnExcept (36, 0, 60, new int [] { 60, 64, 67, 60 }, 100, midi);
        if (midi.events.size () != 2)
            throw new AssertionError ("native root must not be duplicated by chord tracking");
        midi.expect (0, 0, 64, 100);
        midi.expect (1, 0, 67, 100);
        tracker.noteOff (36, midi);
        if (midi.events.size () != 4)
            throw new AssertionError ("only tracked chord extensions should be released");
        midi.expect (2, 0, 64, 0);
        midi.expect (3, 0, 67, 0);
    }


    private static void all128PitchBitsAreEmittedAndReleasedInTheirOwnWord ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        final int [] notes = new int [128];
        for (int note = 0; note < notes.length; ++note)
            notes[note] = note;

        tracker.noteOn (127, 15, notes, 100, midi);
        if (midi.events.size () != 128 || tracker.getActivePadCount () != 1)
            throw new AssertionError ("all 128 MIDI pitches must be represented by the two-word pad bitset");
        for (int note = 0; note < 128; ++note)
            midi.expect (note, 15, note, 100);

        tracker.noteOff (127, midi);
        if (midi.events.size () != 256 || tracker.getActivePadCount () != 0)
            throw new AssertionError ("all 128 MIDI pitches must be released exactly once");
        for (int note = 0; note < 128; ++note)
            midi.expect (128 + note, 15, note, 0);

        tracker.noteOff (127, midi);
        if (midi.events.size () != 256)
            throw new AssertionError ("repeated release must remain idempotent");
    }


    private static void retriggeringOnePadReleasesItsPreviousNotes ()
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder midi = new Recorder ();
        tracker.noteOn (36, 0, new int [] { 60, 64 }, 100, midi);
        tracker.noteOn (36, 0, new int [] { 62, 65 }, 100, midi);
        if (tracker.getActivePadCount () != 1)
            throw new AssertionError ("retriggering created duplicate pad ownership");
        midi.expect (2, 0, 60, 0);
        midi.expect (3, 0, 64, 0);
        midi.expect (4, 0, 62, 100);
        midi.expect (5, 0, 65, 100);
        tracker.noteOff (36, midi);
        if (midi.events.size () != 8)
            throw new AssertionError ("retriggered notes were not fully released");
    }
}
