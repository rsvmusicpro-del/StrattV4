#!/usr/bin/env python3
"""Reset note-sequencer loop-range and duplicate gestures on context changes."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
SOURCE = ROOT / "framework/view/sequencer/AbstractNoteSequencerView.java"


from patch_utils import replace_once



source = SOURCE.read_text(encoding="utf-8")
source = replace_once(
    source,
    """        this.numDisplayCols = numDisplayCols;
        this.offsetY = this.startKey;
""",
    """        this.numDisplayCols = numDisplayCols;
        this.offsetY = this.startKey;

        this.model.getTrackBank ().addSelectionObserver ( (index, isSelected) -> {
            if (isSelected)
                this.clearSequencerGestureState ();
        });
""",
    "Note Sequencer track-change gesture cleanup",
)
source = replace_once(
    source,
    """    /** {@inheritDoc} */
    @Override
    public void onGridNote (final int note, final int velocity)
""",
    """    /**
     * Clear temporary range-selection and note-copy state. These gestures are
     * meaningful only while the same sequencer view and track remain active.
     */
    private void clearSequencerGestureState ()
    {
        this.loopPadPressed = -1;
        this.copyNote = null;
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
    public void onGridNote (final int note, final int velocity)
""",
    "Note Sequencer view-deactivation cleanup",
)
if source.count("this.clearSequencerGestureState ();") != 2:
    raise SystemExit("Note Sequencer cleanup must be wired to track selection and deactivation")
if "this.loopPadPressed = -1;" not in source or "this.copyNote = null;" not in source:
    raise SystemExit("Note Sequencer cleanup is incomplete")
SOURCE.write_text(source, encoding="utf-8")
print("Note Sequencer loop-range and duplicate gestures now reset on track/view changes.")
