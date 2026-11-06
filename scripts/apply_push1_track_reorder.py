#!/usr/bin/env python3
"""Use the cursor's actual sibling bank for deterministic Push 1 track moves.

DrivenByMoss 19.2.2 used a flat 400-track bank and absolute Track.position().
That can select a child of an expanded Group Track as the "next" track.
This patch resolves neighbours from createSiblingsTrackBank instead.
"""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


from patch_utils import replace_once



path = ROOT / "bitwig/framework/daw/data/CursorTrackImpl.java"
source = path.read_text(encoding="utf-8")

source = replace_once(
    source,
    "import de.mossgrabers.bitwig.framework.daw.HostImpl;\n",
    "",
    "Remove global flat-bank HostImpl dependency",
)
source = replace_once(
    source,
    "    private final TrackBank            largeTrackBank;\n",
    "    private final TrackBank            siblingTrackBank;\n",
    "Replace flat project bank with cursor sibling bank",
)
source = replace_once(
    source,
    "        this.largeTrackBank = ((HostImpl) host).getControllerHost ().createTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, true);\n",
    "        this.siblingTrackBank = cursorTrack.createSiblingsTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, false, false);\n"
    "        this.siblingTrackBank.cursorIndex ().markInterested ();\n",
    "Create a sibling-scoped track bank following the cursor",
)

old_previous = """    @Override
    public void swapWithPrevious ()
    {
        final ITrackBank tb = this.model.getCurrentTrackBank ();
        if (tb == null)
            return;
        final int position = this.getPosition ();
        if (position == 0)
            return;
        final Track prevTrack = this.largeTrackBank.getItemAt (position - 1);
        this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);
        prevTrack.selectInEditor ();
    }
"""
new_previous = """    @Override
    public void swapWithPrevious ()
    {
        final ITrackBank tb = this.model.getCurrentTrackBank ();
        if (tb == null || !this.canSelectPrevious ())
            return;
        final Track prevTrack = this.getSiblingTrackAtCursorOffset (-1);
        if (prevTrack == null)
            return;
        this.track.afterTrackInsertionPoint ().moveTracks (prevTrack);
        prevTrack.selectInEditor ();
    }
"""
source = replace_once(source, old_previous, new_previous, "Previous sibling-only track move")

old_next = """    @Override
    public void swapWithNext ()
    {
        final ITrackBank tb = this.model.getCurrentTrackBank ();
        if (tb == null)
            return;
        final int position = this.getPosition ();
        if (position >= NUM_TRACKS_LARGE_BANK - 1)
            return;
        final Track nextTrack = this.largeTrackBank.getItemAt (position + 1);
        this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);
        nextTrack.selectInEditor ();
    }
"""
new_next = """    @Override
    public void swapWithNext ()
    {
        final ITrackBank tb = this.model.getCurrentTrackBank ();
        if (tb == null || !this.canSelectNext ())
            return;
        final Track nextTrack = this.getSiblingTrackAtCursorOffset (1);
        if (nextTrack == null)
            return;
        this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack);
        nextTrack.selectInEditor ();
    }


    /**
     * Resolve a neighbour in the cursor track's sibling bank, never in the
     * flattened project-wide track list.
     *
     * @param offset -1 for the previous sibling, +1 for the next sibling
     * @return The existing sibling, or null if the cursor/boundary is invalid
     */
    private Track getSiblingTrackAtCursorOffset (final int offset)
    {
        final int cursorIndex = this.siblingTrackBank.cursorIndex ().get ();
        final int targetIndex = cursorIndex + offset;
        if (cursorIndex < 0 || targetIndex < 0 || targetIndex >= NUM_TRACKS_LARGE_BANK)
            return null;

        final Track target = this.siblingTrackBank.getItemAt (targetIndex);
        // CursorTrack.hasPrevious/hasNext is the subscribed availability guard.
        // Do not read Track.exists() here: this raw TrackBank item has no observer
        // wrapper, so an unmarked exists value can be stale or permanently false.
        return target;
    }
"""
source = replace_once(source, old_next, new_next, "Next sibling-only track move and resolver")

if "largeTrackBank" in source or "createTrackBank (NUM_TRACKS_LARGE_BANK" in source:
    raise SystemExit("Flat global track bank reference remains")
for token in (
    "createSiblingsTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, false, false)",
    "siblingTrackBank.cursorIndex ().markInterested ()",
    "this.siblingTrackBank.cursorIndex ().get ()",
    "this.siblingTrackBank.getItemAt (targetIndex)",
    "this.track.afterTrackInsertionPoint ().moveTracks (prevTrack)",
    "this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack)",
):
    if token not in source:
        raise SystemExit(f"Sibling track reorder postcondition missing: {token}")

path.write_text(source, encoding="utf-8")
print("StrattV4 track reorder now resolves only same-parent siblings through Bitwig's sibling track bank.")
