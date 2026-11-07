package de.mossgrabers.controller.ableton.push.view;

import de.mossgrabers.framework.view.PadMidiNoteTracker;

import java.util.Random;


/**
 * Deterministic model-based stress test for MIDI note ownership.
 *
 * Exercises rapid pad replacement, overlapping pitches, channel isolation,
 * invalid inputs and repeated global cleanup without external dependencies.
 */
public final class PadMidiNoteTrackerStressTest
{
    private static final int PAD_COUNT = 128;
    private static final int CHANNEL_COUNT = 16;
    private static final int NOTE_COUNT = 128;
    private static final int OPERATIONS = 6000;

    private static final class Recorder implements PadMidiNoteTracker.MidiSender
    {
        final int [][] noteOns = new int [CHANNEL_COUNT][NOTE_COUNT];
        final int [][] noteOffs = new int [CHANNEL_COUNT][NOTE_COUNT];

        @Override
        public void send (final int channel, final int note, final int velocity)
        {
            if (velocity == 0)
                this.noteOffs[channel][note]++;
            else
                this.noteOns[channel][note]++;
        }
    }


    public static void main (final String [] args)
    {
        final PadMidiNoteTracker tracker = new PadMidiNoteTracker ();
        final Recorder actual = new Recorder ();
        final Model expected = new Model ();
        final Random random = new Random (0x535452415454L);

        for (int operation = 0; operation < OPERATIONS; ++operation)
        {
            final int pad = random.nextInt (PAD_COUNT);
            final int channel = random.nextInt (CHANNEL_COUNT);
            final int kind = random.nextInt (100);

            if (kind < 48)
            {
                final int [] notes = randomNotes (random);
                final int velocity = 1 + random.nextInt (127);
                tracker.noteOn (pad, channel, notes, velocity, actual);
                expected.replacePad (pad, channel, notes);
            }
            else if (kind < 70)
            {
                tracker.noteOff (pad, actual);
                expected.releasePad (pad);
            }
            else if (kind < 76)
            {
                tracker.releaseAll (actual);
                expected.releaseAll ();
            }
            else if (kind < 86)
            {
                final int [] notes = randomNotes (random);
                tracker.noteOn (pad, channel, notes, 0, actual);
                expected.releasePad (pad);
            }
            else
            {
                // Every invalid operation must leave an existing pad untouched.
                switch (random.nextInt (4))
                {
                    case 0 -> tracker.noteOn (pad, 16, new int [] { 60, 64 }, 100, actual);
                    case 1 -> tracker.noteOn (pad, channel, new int [] { -1, 128 }, 100, actual);
                    case 2 -> tracker.noteOn (pad, channel, null, 100, actual);
                    default -> tracker.noteOn (pad, channel, new int [] { 60, 64 }, -1, actual);
                }
            }

            expected.assertMatches (tracker, actual, operation);
        }

        tracker.releaseAll (actual);
        expected.releaseAll ();
        expected.assertMatches (tracker, actual, OPERATIONS);
        tracker.releaseAll (actual);
        expected.assertMatches (tracker, actual, OPERATIONS + 1);

        System.out.println ("PadMidiNoteTrackerStressTest: " + OPERATIONS
            + " deterministic operations passed.");
    }


    private static int [] randomNotes (final Random random)
    {
        final int [] notes = new int [1 + random.nextInt (8)];
        for (int index = 0; index < notes.length; ++index)
            notes[index] = random.nextInt (NOTE_COUNT);
        return notes;
    }


    private static final class Model
    {
        private final boolean [][][] owned = new boolean [PAD_COUNT][CHANNEL_COUNT][NOTE_COUNT];
        private final int [][] ownerCounts = new int [CHANNEL_COUNT][NOTE_COUNT];
        private final int [][] expectedOns = new int [CHANNEL_COUNT][NOTE_COUNT];
        private final int [][] expectedOffs = new int [CHANNEL_COUNT][NOTE_COUNT];


        void replacePad (final int pad, final int channel, final int [] notes)
        {
            this.releasePad (pad);
            for (final int note: notes)
            {
                if (!this.owned[pad][channel][note])
                {
                    if (this.ownerCounts[channel][note] == 0)
                        this.expectedOns[channel][note]++;
                    this.owned[pad][channel][note] = true;
                    this.ownerCounts[channel][note]++;
                }
            }
        }


        void releasePad (final int pad)
        {
            for (int channel = 0; channel < CHANNEL_COUNT; ++channel)
                for (int note = 0; note < NOTE_COUNT; ++note)
                    if (this.owned[pad][channel][note])
                    {
                        this.owned[pad][channel][note] = false;
                        this.ownerCounts[channel][note]--;
                        if (this.ownerCounts[channel][note] == 0)
                            this.expectedOffs[channel][note]++;
                    }
        }


        void releaseAll ()
        {
            for (int pad = 0; pad < PAD_COUNT; ++pad)
                this.releasePad (pad);
        }


        void assertMatches (final PadMidiNoteTracker tracker, final Recorder actual, final int operation)
        {
            int activePads = 0;
            for (int pad = 0; pad < PAD_COUNT; ++pad)
            {
                boolean active = false;
                for (int channel = 0; channel < CHANNEL_COUNT && !active; ++channel)
                    for (int note = 0; note < NOTE_COUNT; ++note)
                        if (this.owned[pad][channel][note])
                        {
                            active = true;
                            break;
                        }
                if (active)
                    activePads++;
            }

            if (tracker.getActivePadCount () != activePads)
                throw new AssertionError ("operation " + operation + ": active pads expected "
                    + activePads + ", got " + tracker.getActivePadCount ());

            for (int channel = 0; channel < CHANNEL_COUNT; ++channel)
                for (int note = 0; note < NOTE_COUNT; ++note)
                {
                    if (actual.noteOns[channel][note] != this.expectedOns[channel][note])
                        throw new AssertionError ("operation " + operation + ": Note On count mismatch at "
                            + channel + ":" + note + ", expected " + this.expectedOns[channel][note]
                            + ", got " + actual.noteOns[channel][note]);
                    if (actual.noteOffs[channel][note] != this.expectedOffs[channel][note])
                        throw new AssertionError ("operation " + operation + ": Note Off count mismatch at "
                            + channel + ":" + note + ", expected " + this.expectedOffs[channel][note]
                            + ", got " + actual.noteOffs[channel][note]);
                }
        }
    }
}
