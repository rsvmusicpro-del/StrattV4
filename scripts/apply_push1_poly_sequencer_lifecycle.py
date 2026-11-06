#!/usr/bin/env python3
"""Clear transient Poly Sequencer editing state when its context is invalidated."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
SOURCE = ROOT / "framework/view/sequencer/AbstractPolySequencerView.java"


from patch_utils import replace_once



source = SOURCE.read_text(encoding="utf-8")
source = replace_once(
    source,
    "        tb.addSelectionObserver ( (index, isSelected) -> this.keyManager.clearPressedKeys ());\n",
    """        tb.addSelectionObserver ( (index, isSelected) -> {
            this.keyManager.clearPressedKeys ();
            if (isSelected)
                this.clearSequencerGestureState ();
        });
""",
    "Poly Sequencer selected-track transient state invalidation",
)
source = replace_once(
    source,
    """    /** {@inheritDoc} */
    @Override
    public void onOctaveDown (final ButtonEvent event)
""",
    """    /**
     * Clear short-lived note-entry and duplication state when its context ends.
     * A held chord from the previous track/view must never be inserted into a
     * different clip, and a copied step must not survive a context switch.
     */
    private void clearSequencerGestureState ()
    {
        this.noteMemory.clear ();
        this.copyStep = -1;
        this.lastPressedNoteTime = 0;
    }


    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        this.clearSequencerGestureState ();
        super.onDeactivate ();
    }


    /** {@inheritDoc} */
    @Override
    public void onOctaveDown (final ButtonEvent event)
""",
    "Poly Sequencer lifecycle cleanup",
)
if source.count("this.clearSequencerGestureState ();") != 2:
    raise SystemExit("Poly Sequencer transient-state cleanup is not wired to both lifecycle events")
if "this.noteMemory.clear ();" not in source or "this.copyStep = -1;" not in source or "this.lastPressedNoteTime = 0;" not in source:
    raise SystemExit("Poly Sequencer transient-state cleanup is incomplete")
SOURCE.write_text(source, encoding="utf-8")
print("Poly Sequencer note-entry memory and duplicate source now reset on track change and view deactivation.")
