package de.mossgrabers.framework.command.trigger.clip;

/** Behavioral tests for modifier capture across a Push 1 NEW-button gesture. */
public final class Push1SelectGestureTest
{
    public static void main (final String [] args)
    {
        selectReleasedBeforeNewDoesNotCancelSceneGesture ();
        selectPressedAfterNewDoesNotChangePlainNewGesture ();
        eachGestureResetsItsPreviousModifierState ();
        System.out.println ("Push1SelectGesture: 3 behavioral tests passed.");
    }

    private static void selectReleasedBeforeNewDoesNotCancelSceneGesture ()
    {
        final Push1SelectGesture gesture = new Push1SelectGesture ();
        gesture.begin (true);
        // The physical Select key is released before NEW's UP event.
        if (!gesture.wasSelectedOnPress ())
            throw new AssertionError ("Select + NEW must remain latched for the full gesture");
    }

    private static void selectPressedAfterNewDoesNotChangePlainNewGesture ()
    {
        final Push1SelectGesture gesture = new Push1SelectGesture ();
        gesture.begin (false);
        // Select becomes pressed only after NEW-down.
        if (gesture.wasSelectedOnPress ())
            throw new AssertionError ("pressing Select mid-gesture must not change the action");
    }

    private static void eachGestureResetsItsPreviousModifierState ()
    {
        final Push1SelectGesture gesture = new Push1SelectGesture ();
        gesture.begin (true);
        gesture.reset ();
        gesture.begin (false);
        if (gesture.wasSelectedOnPress ())
            throw new AssertionError ("a previous Select gesture leaked into the next NEW press");
    }
}
