package de.mossgrabers.controller.ableton.push.view;

import java.util.ArrayDeque;
import java.util.Deque;


/** Behavioral tests for stale delayed view-mapping task invalidation. */
public final class PadViewTaskGuardTest
{
    private static final class MappingHarness
    {
        private final PadViewTaskGuard guard = new PadViewTaskGuard ();
        private final Deque<Runnable> pending = new ArrayDeque<> ();
        private boolean active = true;
        private int applied = -1;

        void request (final int matrix)
        {
            final long token = this.guard.begin ();
            // Production mapping uses a delayed calculation followed by a
            // second delayed application. Model both scheduler stages.
            this.pending.addLast ( () -> {
                if (!this.active || !this.guard.isCurrent (token))
                    return;
                this.pending.addLast ( () -> {
                    if (this.active && this.guard.isCurrent (token))
                        this.applied = matrix;
                });
            });
        }

        void deactivate ()
        {
            this.active = false;
            this.guard.invalidate ();
        }

        void activate ()
        {
            this.active = true;
        }

        void runNext ()
        {
            final Runnable task = this.pending.pollFirst ();
            if (task != null)
                task.run ();
        }

        void runPending ()
        {
            while (!this.pending.isEmpty ())
                this.runNext ();
        }
    }


    public static void main (final String [] args)
    {
        aNewerRequestSupersedesAnOlderDelayedMapping ();
        deactivationInvalidatesTheFirstScheduledStage ();
        deactivationBetweenStagesInvalidatesTheFinalApplication ();
        reactivationDoesNotReviveOldMappingWork ();
        System.out.println ("PadViewTaskGuard: 4 behavioral tests passed.");
    }


    private static void aNewerRequestSupersedesAnOlderDelayedMapping ()
    {
        final MappingHarness view = new MappingHarness ();
        view.request (1);
        view.request (2);
        view.runPending ();
        if (view.applied != 2)
            throw new AssertionError ("an obsolete mapping overwrote the latest request");
    }


    private static void deactivationInvalidatesTheFirstScheduledStage ()
    {
        final MappingHarness view = new MappingHarness ();
        view.request (7);
        view.deactivate ();
        view.runPending ();
        if (view.applied != -1)
            throw new AssertionError ("a delayed mapping calculation ran after view deactivation");
    }


    private static void deactivationBetweenStagesInvalidatesTheFinalApplication ()
    {
        final MappingHarness view = new MappingHarness ();
        view.request (8);
        view.runNext (); // Run the delayed matrix calculation only.
        view.deactivate ();
        view.runPending (); // The delayed matrix application must now be stale.
        if (view.applied != -1)
            throw new AssertionError ("the second scheduled stage applied a stale mapping");
    }


    private static void reactivationDoesNotReviveOldMappingWork ()
    {
        final MappingHarness view = new MappingHarness ();
        view.request (3);
        view.runNext ();
        view.deactivate ();
        view.activate ();
        view.runPending ();
        if (view.applied != -1)
            throw new AssertionError ("reactivation revived a stale mapping request");
        view.request (4);
        view.runPending ();
        if (view.applied != 4)
            throw new AssertionError ("the active view rejected its fresh mapping request");
    }
}
