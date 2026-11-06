package de.mossgrabers.framework.mode;

/** Behavioral tests for Note Mode edit transaction ownership. */
public final class NoteEditTouchOwnerTest
{
    public static void main (final String [] args)
    {
        releaseUsesTheClipCapturedAtFirstTouch ();
        simultaneousTouchesShareOneEditTransaction ();
        changingClipDuringTouchCannotStealTheOwner ();
        duplicateDownAndOrphanUpAreIgnored ();
        clearingCancelsAllTouchesAndReturnsTheOwner ();
        invalidKnobIndicesAreIgnored ();
        System.out.println ("NoteEditTouchOwner: 6 behavioral tests passed.");
    }

    private static void releaseUsesTheClipCapturedAtFirstTouch ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clipA = new Object ();
        final Object clipB = new Object ();
        check (owner.begin (0, clipA), "first touch must start edit on clip A");
        check (owner.end (0) == clipA, "release must stop edit on original clip A");
        check (owner.begin (1, clipB), "next gesture may acquire clip B");
        check (owner.end (1) == clipB, "second gesture must stop clip B");
    }

    private static void simultaneousTouchesShareOneEditTransaction ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clip = new Object ();
        check (owner.begin (0, clip), "first knob starts edit");
        check (!owner.begin (1, clip), "second knob joins without a second startEdit");
        check (owner.end (0) == null, "first release must not stop while another knob is touched");
        check (owner.end (1) == clip, "last release stops the shared edit transaction");
    }

    private static void changingClipDuringTouchCannotStealTheOwner ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clipA = new Object ();
        final Object clipB = new Object ();
        check (owner.begin (0, clipA), "clip A acquired");
        check (!owner.begin (1, clipB), "clip B must not steal an active clip A edit");
        check (owner.end (1) == null, "ignored clip B touch has no release effect");
        check (owner.end (0) == clipA, "clip A remains owner until its own release");
    }

    private static void duplicateDownAndOrphanUpAreIgnored ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clip = new Object ();
        check (!owner.begin (0, null), "null clip rejected");
        check (owner.end (0) == null, "orphan release ignored");
        check (owner.begin (0, clip), "valid touch accepted");
        check (!owner.begin (0, clip), "duplicate DOWN does not increment touch count");
        check (owner.end (0) == clip, "one UP releases one accepted DOWN");
    }

    private static void clearingCancelsAllTouchesAndReturnsTheOwner ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clip = new Object ();
        check (owner.begin (0, clip), "first touch starts");
        check (!owner.begin (1, clip), "second touch joins");
        check (owner.clear () == clip, "deactivation returns clip that must be stopped");
        check (owner.end (0) == null && owner.end (1) == null, "late releases after clear are harmless");
        check (owner.begin (2, clip), "owner can be reused after clear");
        check (owner.end (2) == clip, "new transaction ends normally");
    }

    private static void invalidKnobIndicesAreIgnored ()
    {
        final NoteEditTouchOwner<Object> owner = new NoteEditTouchOwner<> ();
        final Object clip = new Object ();
        check (!owner.begin (-1, clip), "negative knob index rejected");
        check (!owner.begin (8, clip), "out-of-range knob index rejected");
        check (owner.end (8) == null, "out-of-range release rejected");
    }

    private static void check (final boolean condition, final String message)
    {
        if (!condition)
            throw new AssertionError (message);
    }
}
