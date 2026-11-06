package de.mossgrabers.framework.command.trigger.mode;

/** Behavioral tests for mode ownership across a held encoder gesture. */
public final class KnobTouchOwnerTest
{
    private static int tests;

    public static void main (final String [] args)
    {
        capturesOriginalModeAcrossModeSwitch ();
        ignoresDuplicateTouchDown ();
        ignoresReleaseWithoutTouchDown ();
        rejectsMissingActiveMode ();
        System.out.println ("KnobTouchOwner: " + tests + " behavioral tests passed.");
    }

    private static void capturesOriginalModeAcrossModeSwitch ()
    {
        final KnobTouchOwner<Object> owner = new KnobTouchOwner<> ();
        final Object firstMode = new Object ();
        final Object secondMode = new Object ();
        check (owner.begin (firstMode), "first touch must acquire owner");
        final Object released = owner.end ();
        check (released == firstMode, "release must return original mode, not current mode");
        check (released != secondMode, "mode switch must not steal the release");
        check (owner.end () == null, "owner must clear after release");
        ++tests;
    }

    private static void ignoresDuplicateTouchDown ()
    {
        final KnobTouchOwner<Object> owner = new KnobTouchOwner<> ();
        final Object first = new Object ();
        final Object second = new Object ();
        check (owner.begin (first), "first down accepted");
        check (!owner.begin (second), "duplicate down ignored");
        check (owner.end () == first, "duplicate down must not replace owner");
        ++tests;
    }

    private static void ignoresReleaseWithoutTouchDown ()
    {
        final KnobTouchOwner<Object> owner = new KnobTouchOwner<> ();
        check (owner.end () == null, "orphan release has no owner");
        check (owner.begin (new Object ()), "router remains usable after orphan release");
        ++tests;
    }

    private static void rejectsMissingActiveMode ()
    {
        final KnobTouchOwner<Object> owner = new KnobTouchOwner<> ();
        check (!owner.begin (null), "null active mode cannot own a touch");
        check (owner.end () == null, "null owner must not leak into release");
        ++tests;
    }

    private static void check (final boolean condition, final String message)
    {
        if (!condition)
            throw new AssertionError (message);
    }
}
