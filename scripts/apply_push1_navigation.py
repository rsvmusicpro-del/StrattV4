#!/usr/bin/env python3
"""Apply Ableton-style Push 1 In/Out navigation to pinned DrivenByMoss."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


def patch_shift_track_cursor_arrows() -> None:
    """Disable Shift + horizontal cursor navigation in track/session modes.

    Track and group-track reordering is exclusively handled by Shift + In/Out.
    Plain horizontal page navigation and Device-mode cursor navigation remain.
    """
    path = ROOT / "controller/ableton/push/command/trigger/PushCursorCommand.java"
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "import de.mossgrabers.framework.featuregroup.IMode;\n",
        "import de.mossgrabers.framework.featuregroup.IMode;\n"
        "import de.mossgrabers.framework.mode.Modes;\n",
        "PushCursorCommand track-mode guard import",
    )
    source = replace_once(
        source,
        """    @Override
    protected void scrollLeft ()
    {
        final IMode activeMode = this.surface.getModeManager ().getActive ();
        if (activeMode != null)
            activeMode.selectPreviousItemPage ();
    }
""",
        """    @Override
    protected void scrollLeft ()
    {
        if (this.isShiftTrackNavigationDisabled ())
            return;

        final IMode activeMode = this.surface.getModeManager ().getActive ();
        if (activeMode != null)
            activeMode.selectPreviousItemPage ();
    }
""",
        "PushCursorCommand Shift + Left track navigation guard",
    )
    source = replace_once(
        source,
        """    @Override
    protected void scrollRight ()
    {
        final IMode activeMode = this.surface.getModeManager ().getActive ();
        if (activeMode != null)
            activeMode.selectNextItemPage ();
    }
""",
        """    @Override
    protected void scrollRight ()
    {
        if (this.isShiftTrackNavigationDisabled ())
            return;

        final IMode activeMode = this.surface.getModeManager ().getActive ();
        if (activeMode != null)
            activeMode.selectNextItemPage ();
    }
""",
        "PushCursorCommand Shift + Right track navigation guard",
    )
    source = replace_once(
        source,
        """    @Override
    protected void updateArrowStates ()
    {
        final ISceneBank sceneBank = this.getSceneBank ();
        this.canScrollUp = sceneBank.canScrollBackwards ();
        this.canScrollDown = sceneBank.canScrollForwards ();

        final IMode mode = this.surface.getModeManager ().getActive ();
        final boolean shiftPressed = this.surface.isShiftPressed ();
        this.canScrollLeft = mode != null && (shiftPressed ? mode.hasPreviousItem () : mode.hasPreviousItemPage ());
        this.canScrollRight = mode != null && (shiftPressed ? mode.hasNextItem () : mode.hasNextItemPage ());
    }
""",
        """    @Override
    protected void updateArrowStates ()
    {
        final ISceneBank sceneBank = this.getSceneBank ();
        this.canScrollUp = sceneBank.canScrollBackwards ();
        this.canScrollDown = sceneBank.canScrollForwards ();

        final IMode mode = this.surface.getModeManager ().getActive ();
        final boolean shiftPressed = this.surface.isShiftPressed ();
        if (this.isShiftTrackNavigationDisabled ())
        {
            this.canScrollLeft = false;
            this.canScrollRight = false;
        }
        else
        {
            this.canScrollLeft = mode != null && (shiftPressed ? mode.hasPreviousItem () : mode.hasPreviousItemPage ());
            this.canScrollRight = mode != null && (shiftPressed ? mode.hasNextItem () : mode.hasNextItemPage ());
        }
    }
""",
        "PushCursorCommand Shift + track arrow LED state",
    )
    source = replace_once(
        source,
        "    private boolean isScenePlay ()\n",
        """    /**
     * Track/group movement is assigned exclusively to Shift + In/Out.
     * Suppress the horizontal cursor gesture and its LEDs in track contexts.
     *
     * @return True if Shift + Left/Right must not navigate tracks
     */
    private boolean isShiftTrackNavigationDisabled ()
    {
        final Modes activeModeID = this.surface.getModeManager ().getActiveID ();
        return this.surface.isShiftPressed () && activeModeID != null
                && (activeModeID == Modes.SESSION || Modes.isTrackMode (activeModeID));
    }


    private boolean isScenePlay ()
""",
        "PushCursorCommand Shift + track navigation predicate",
    )

    for token in (
        "this.isShiftTrackNavigationDisabled ()",
        "activeModeID == Modes.SESSION",
        "Modes.isTrackMode (activeModeID)",
        "this.canScrollLeft = false;",
        "this.canScrollRight = false;",
    ):
        if token not in source:
            raise SystemExit(f"PushCursorCommand: missing Shift + track-navigation postcondition {token}")
    path.write_text(source, encoding="utf-8")


def patch_page_command(command_name: str, direction: str) -> None:
    path = ROOT / "controller/ableton/push/command/trigger" / f"{command_name}.java"
    source = path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        "import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;\n",
        "import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;\n"
        "import de.mossgrabers.controller.ableton.push.mode.device.DeviceBrowserMode;\n",
        f"{command_name} browser import",
    )
    source = replace_once(
        source,
        "import de.mossgrabers.framework.daw.IModel;\n",
        "import de.mossgrabers.framework.daw.IModel;\n"
        "import de.mossgrabers.framework.daw.clip.INoteClip;\n",
        f"{command_name} note clip import",
    )
    source = replace_once(
        source,
        "import de.mossgrabers.framework.featuregroup.IView;\n",
        "import de.mossgrabers.framework.featuregroup.IMode;\n"
        "import de.mossgrabers.framework.featuregroup.IView;\n"
        "import de.mossgrabers.framework.featuregroup.ModeManager;\n",
        f"{command_name} mode imports",
    )
    source = replace_once(
        source,
        "import de.mossgrabers.framework.view.Views;\n",
        "import de.mossgrabers.framework.mode.Modes;\n"
        "import de.mossgrabers.framework.view.sequencer.ClipLengthView;\n",
        f"{command_name} mode ID imports",
    )

    if direction == "left":
        old_execute = """    /** {@inheritDoc} */
    @Override
    public void execute (final ButtonEvent event, final int velocity)
    {
        final ViewManager viewManager = this.surface.getViewManager ();
        if (viewManager.isActive (Views.SESSION))
        {
            if (event == ButtonEvent.DOWN)
                this.model.getCurrentTrackBank ().selectPreviousPage ();
            return;
        }

        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView)
            sequencerView.onLeft (event);
    }
"""
        replacement = """    /**
     * Check if the previous In/Out destination is available.
     *
     * @return True if the button can perform an action in the active mode
     */
    public boolean canNavigate ()
    {
        final ModeManager modeManager = this.surface.getModeManager ();
        final IMode activeMode = modeManager.getActive ();

        if (modeManager.isActive (Modes.BROWSER))
            return activeMode instanceof final DeviceBrowserMode browserMode && browserMode.canScrollFilterColumnsLeft ();

        if (Push1NavigationContext.isDeviceNavigationMode (modeManager))
            return activeMode != null && activeMode.hasPreviousItemPage ();

        final ViewManager viewManager = this.surface.getViewManager ();
        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView))
        {
            final INoteClip clip = sequencerView.getClip ();
            return clip != null && clip.doesExist () && clip.canScrollStepsBackwards ();
        }
        return false;
    }


    /** {@inheritDoc} */
    @Override
    public void execute (final ButtonEvent event, final int velocity)
    {
        final ModeManager modeManager = this.surface.getModeManager ();
        final IMode activeMode = modeManager.getActive ();

        if (modeManager.isActive (Modes.BROWSER))
        {
            if (event == ButtonEvent.DOWN && activeMode instanceof final DeviceBrowserMode browserMode)
                browserMode.scrollFilterColumnsLeft ();
            return;
        }

        if (Push1NavigationContext.isDeviceNavigationMode (modeManager))
        {
            if (event == ButtonEvent.DOWN && activeMode != null && activeMode.hasPreviousItemPage ())
                activeMode.selectPreviousItemPage ();
            return;
        }

        final ViewManager viewManager = this.surface.getViewManager ();
        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView))
            sequencerView.onLeft (event);
    }
"""
    else:
        old_execute = """    /** {@inheritDoc} */
    @Override
    public void execute (final ButtonEvent event, final int velocity)
    {
        final ViewManager viewManager = this.surface.getViewManager ();
        if (viewManager.isActive (Views.SESSION))
        {
            if (event == ButtonEvent.DOWN)
                this.model.getCurrentTrackBank ().selectNextPage ();
            return;
        }

        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView)
            sequencerView.onRight (event);
    }
"""
        replacement = """    /**
     * Check if the next In/Out destination is available.
     *
     * @return True if the button can perform an action in the active mode
     */
    public boolean canNavigate ()
    {
        final ModeManager modeManager = this.surface.getModeManager ();
        final IMode activeMode = modeManager.getActive ();

        if (modeManager.isActive (Modes.BROWSER))
            return activeMode instanceof final DeviceBrowserMode browserMode && browserMode.canScrollFilterColumnsRight ();

        if (Push1NavigationContext.isDeviceNavigationMode (modeManager))
            return activeMode != null && activeMode.hasNextItemPage ();

        final ViewManager viewManager = this.surface.getViewManager ();
        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView))
        {
            final INoteClip clip = sequencerView.getClip ();
            return clip != null && clip.doesExist () && clip.canScrollStepsForwards ();
        }
        return false;
    }


    /** {@inheritDoc} */
    @Override
    public void execute (final ButtonEvent event, final int velocity)
    {
        final ModeManager modeManager = this.surface.getModeManager ();
        final IMode activeMode = modeManager.getActive ();

        if (modeManager.isActive (Modes.BROWSER))
        {
            if (event == ButtonEvent.DOWN && activeMode instanceof final DeviceBrowserMode browserMode)
                browserMode.scrollFilterColumnsRight ();
            return;
        }

        if (Push1NavigationContext.isDeviceNavigationMode (modeManager))
        {
            if (event == ButtonEvent.DOWN && activeMode != null && activeMode.hasNextItemPage ())
                activeMode.selectNextItemPage ();
            return;
        }

        final ViewManager viewManager = this.surface.getViewManager ();
        final IView activeView = viewManager.getActive ();
        if (activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView))
            sequencerView.onRight (event);
    }
"""
    move_left = direction == "left"
    track_move_call = (
        "        if (Push1TrackMoveCommand.executeIfRequested (this.model, this.surface, event, "
        + ("true" if move_left else "false")
        + "))\n"
        "            return;\n\n"
    )
    execute_anchor = "    public void execute (final ButtonEvent event, final int velocity)\n    {\n"
    replacement = replace_once(
        replacement,
        execute_anchor,
        execute_anchor + track_move_call,
        f"{command_name} Shift + In/Out track move",
    )
    source = replace_once(source, old_execute, replacement, f"{command_name} context-aware routing")
    path.write_text(source, encoding="utf-8")


# Shared context helper avoids identical Device-mode checks in both page commands.
context_path = ROOT / "controller/ableton/push/command/trigger/Push1NavigationContext.java"
context_path.write_text(r"""// Written for StrattV4.
package de.mossgrabers.controller.ableton.push.command.trigger;

import de.mossgrabers.framework.featuregroup.ModeManager;
import de.mossgrabers.framework.mode.Modes;


/**
 * Shared mode-context checks for Push 1 navigation commands.
 */
final class Push1NavigationContext
{
    private Push1NavigationContext ()
    {
        // Utility class.
    }


    static boolean isDeviceNavigationMode (final ModeManager modeManager)
    {
        final Modes activeModeID = modeManager.getActiveID ();
        return activeModeID != null && (activeModeID == Modes.DEVICE_CHAINS || Modes.isDeviceMode (activeModeID));
    }
}
""", encoding="utf-8")


# Track movement: use the selected cursor track and its same-level siblings.
# This avoids the historical flat-bank bug where a Group Track's child could be
# mistaken for the adjacent top-level track.
TRACK_MOVE_HELPER_SOURCE = r"""// Written for StrattV4.
package de.mossgrabers.controller.ableton.push.command.trigger;

import de.mossgrabers.controller.ableton.push.controller.PushControlSurface;
import de.mossgrabers.framework.daw.IModel;
import de.mossgrabers.framework.daw.data.ICursorTrack;
import de.mossgrabers.framework.featuregroup.ModeManager;
import de.mossgrabers.framework.mode.Modes;
import de.mossgrabers.framework.utils.ButtonEvent;


/**
 * Additive Shift + In/Out gesture for moving the selected track by one sibling.
 */
final class Push1TrackMoveCommand
{
    private Push1TrackMoveCommand ()
    {
        // Utility class.
    }


    /**
     * Execute only in Session or a track/mix mode. Device mode is handled by
     * Push1DeviceMoveCommand, which is inserted ahead of this command.
     *
     * @param model The DAW model
     * @param surface The Push control surface
     * @param event The button event
     * @param moveLeft True to move one sibling left, false to move right
     * @return True if the Shift + In/Out chord is consumed
     */
    static boolean executeIfRequested (final IModel model, final PushControlSurface surface, final ButtonEvent event, final boolean moveLeft)
    {
        if (!surface.isShiftPressed ())
            return false;

        final ModeManager modeManager = surface.getModeManager ();
        final Modes activeModeID = modeManager.getActiveID ();
        if (activeModeID != Modes.SESSION && !Modes.isTrackMode (activeModeID))
            return false;

        if (event == ButtonEvent.DOWN)
        {
            final ICursorTrack cursorTrack = model.getCursorTrack ();
            if (cursorTrack.doesExist ())
            {
                if (moveLeft && cursorTrack.canSelectPrevious ())
                    cursorTrack.swapWithPrevious ();
                else if (!moveLeft && cursorTrack.canSelectNext ())
                    cursorTrack.swapWithNext ();
            }
        }

        // Consume the chord even at a sibling boundary; do not fall through
        // into unrelated page navigation while Shift is held.
        return true;
    }
}
"""

track_helper_path = ROOT / "controller/ableton/push/command/trigger/Push1TrackMoveCommand.java"
if track_helper_path.exists():
    raise SystemExit(f"Refusing to overwrite an existing source: {track_helper_path}")
track_helper_path.write_text(TRACK_MOVE_HELPER_SOURCE, encoding="utf-8")

cursor_track_path = ROOT / "bitwig/framework/daw/data/CursorTrackImpl.java"
cursor_track = cursor_track_path.read_text(encoding="utf-8")
cursor_track = replace_once(
    cursor_track,
    "import de.mossgrabers.bitwig.framework.daw.HostImpl;\n",
    "",
    "Remove flat-bank HostImpl dependency",
)
cursor_track = replace_once(
    cursor_track,
    "    private final TrackBank            largeTrackBank;\n",
    "    private final TrackBank            siblingTrackBank;\n",
    "Use cursor-relative sibling bank",
)
cursor_track = replace_once(
    cursor_track,
    "        this.largeTrackBank = ((HostImpl) host).getControllerHost ().createTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, true);\n",
    "        this.siblingTrackBank = cursorTrack.createSiblingsTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, true, false);\n"
    "        this.siblingTrackBank.cursorIndex ().markInterested ();\n"
    "        this.cursorTrack.hasPrevious ().markInterested ();\n"
    "        this.cursorTrack.hasNext ().markInterested ();\n",
    "Initialize cursor-track navigation observables before any get()",
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
cursor_track = replace_once(cursor_track, old_previous, new_previous, "Previous sibling track move")
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
        if (cursorIndex < 0 || cursorIndex >= NUM_TRACKS_LARGE_BANK)
            return null;

        final int targetIndex = cursorIndex + offset;
        if (targetIndex < 0 || targetIndex >= NUM_TRACKS_LARGE_BANK)
            return null;

        return this.siblingTrackBank.getItemAt (targetIndex);
    }
"""
cursor_track = replace_once(cursor_track, old_next, new_next, "Next sibling track move and resolver")
if "largeTrackBank" in cursor_track or "HostImpl" in cursor_track:
    raise SystemExit("Flat global track-bank implementation remains")
for token in (
    "createSiblingsTrackBank (NUM_TRACKS_LARGE_BANK, 0, 0, true, false)",
    "siblingTrackBank.cursorIndex ().markInterested ()",
    "this.cursorTrack.hasPrevious ().markInterested ()",
    "this.cursorTrack.hasNext ().markInterested ()",
    "this.siblingTrackBank.cursorIndex ().get ()",
    "this.siblingTrackBank.getItemAt (targetIndex)",
    "!this.canSelectPrevious ()",
    "!this.canSelectNext ()",
    "this.track.afterTrackInsertionPoint ().moveTracks (prevTrack)",
    "this.track.beforeTrackInsertionPoint ().moveTracks (nextTrack)",
):
    if token not in cursor_track:
        raise SystemExit(f"CursorTrackImpl sibling-move postcondition missing: {token}")
cursor_track_path.write_text(cursor_track, encoding="utf-8")

# Device-mode In/Out: DeviceParamsMode already pages device and parameter banks.
# DeviceChainsMode gets explicit pages for Rack chains, eight entries per page.
patch_page_command("PageLeftCommand", "left")
patch_page_command("PageRightCommand", "right")
patch_shift_track_cursor_arrows ()

chains_path = ROOT / "controller/ableton/push/mode/device/DeviceChainsMode.java"
chains = chains_path.read_text(encoding="utf-8")
chains = replace_once(
    chains,
    "public class DeviceChainsMode extends DeviceParamsMode\n{\n",
    "public class DeviceChainsMode extends DeviceParamsMode\n{\n"
    "    private static final int CHAINS_PER_PAGE = 8;\n"
    "    private int chainPageOffset;\n\n",
    "DeviceChainsMode page state",
)
constructor_anchor = """    public DeviceChainsMode (final PushControlSurface surface, final IModel model)
    {
        super (surface, model);
    }


"""
constructor_replacement = constructor_anchor + """    /** {@inheritDoc} */
    @Override
    public void onActivate ()
    {
        super.onActivate ();
        this.chainPageOffset = 0;
    }


    private String [] getCurrentSlotChains ()
    {
        final String [] slotChains = this.model.getCursorDevice ().getSlotChains ();
        final int maxPageOffset = slotChains.length <= CHAINS_PER_PAGE ? 0 : ((slotChains.length - 1) / CHAINS_PER_PAGE) * CHAINS_PER_PAGE;
        if (this.chainPageOffset > maxPageOffset)
            this.chainPageOffset = maxPageOffset;
        return slotChains;
    }


    /** {@inheritDoc} */
    @Override
    public void selectPreviousItemPage ()
    {
        this.getCurrentSlotChains ();
        if (this.chainPageOffset > 0)
        {
            this.chainPageOffset = Math.max (0, this.chainPageOffset - CHAINS_PER_PAGE);
            this.updateDisplay ();
        }
    }


    /** {@inheritDoc} */
    @Override
    public void selectNextItemPage ()
    {
        if (this.hasNextItemPage ())
        {
            this.chainPageOffset += CHAINS_PER_PAGE;
            this.updateDisplay ();
        }
    }


    /** {@inheritDoc} */
    @Override
    public boolean hasPreviousItemPage ()
    {
        this.getCurrentSlotChains ();
        return this.chainPageOffset > 0;
    }


    /** {@inheritDoc} */
    @Override
    public boolean hasNextItemPage ()
    {
        return this.chainPageOffset + CHAINS_PER_PAGE < this.getCurrentSlotChains ().length;
    }


"""
chains = replace_once(chains, constructor_anchor, constructor_replacement, "DeviceChainsMode paging methods")
chains = replace_once(
    chains,
    """            final String [] slotChains = cd.getSlotChains ();
            if (index >= slotChains.length)
                return;
            cd.selectSlotChain (slotChains[index]);
""",
    """            final String [] slotChains = this.getCurrentSlotChains ();
            final int chainIndex = this.chainPageOffset + index;
            if (chainIndex >= slotChains.length)
                return;
            cd.selectSlotChain (slotChains[chainIndex]);
""",
    "DeviceChainsMode chain selection offset",
)
old_colors = """    @Override
    public int getButtonColor (final ButtonID buttonID)
    {
        final int index = this.isButtonRow (0, buttonID);
        if (index >= 0)
            return super.getButtonColor (buttonID);

        final int existsColor = this.isPush2 ? PushColorManager.PUSH2_COLOR_YELLOW_LO : PushColorManager.PUSH1_COLOR_YELLOW_LO;
        final int offColor = this.isPush2 ? PushColorManager.PUSH2_COLOR_BLACK : PushColorManager.PUSH1_COLOR_BLACK;
        final String [] slotChains = this.model.getCursorDevice ().getSlotChains ();
        return index < slotChains.length ? existsColor : offColor;
    }
"""
new_colors = """    @Override
    public int getButtonColor (final ButtonID buttonID)
    {
        final int index = this.isButtonRow (0, buttonID);
        if (index < 0)
            return super.getButtonColor (buttonID);

        final int existsColor = this.isPush2 ? PushColorManager.PUSH2_COLOR_YELLOW_LO : PushColorManager.PUSH1_COLOR_YELLOW_LO;
        final int offColor = this.isPush2 ? PushColorManager.PUSH2_COLOR_BLACK : PushColorManager.PUSH1_COLOR_BLACK;
        final String [] slotChains = this.getCurrentSlotChains ();
        return this.chainPageOffset + index < slotChains.length ? existsColor : offColor;
    }
"""
chains = replace_once(chains, old_colors, new_colors, "DeviceChainsMode chain LED mapping")
chains = replace_once(
    chains,
    """        final String [] slotChains = cd.getSlotChains ();
        for (int i = 0; i < 8; i++)
        {
            final String bottomMenu = i < slotChains.length ? slotChains[i] : "";
            display.setCell (3, i, bottomMenu);
        }
""",
    """        final String [] slotChains = this.getCurrentSlotChains ();
        for (int i = 0; i < CHAINS_PER_PAGE; i++)
        {
            final int chainIndex = this.chainPageOffset + i;
            final String bottomMenu = chainIndex < slotChains.length ? slotChains[chainIndex] : "";
            display.setCell (3, i, bottomMenu);
        }
""",
    "DeviceChainsMode Push 1 chain page display",
)
chains = replace_once(
    chains,
    """        final String [] slotChains = cd.getSlotChains ();
        for (int i = 0; i < 8; i++)
        {
            final boolean isTopMenuOn = this.getTopMenuEnablement (cd, hasPinning, i);
            final String bottomMenu = i < slotChains.length ? slotChains[i] : "";
            final String bottomMenuIcon = "";
            final boolean isBottomMenuOn = i < slotChains.length;
            display.addParameterElement (this.hostMenu[i], isTopMenuOn, bottomMenu, bottomMenuIcon, bottomMenuColor, isBottomMenuOn, "", 0, "", false, -1);
        }
""",
    """        final String [] slotChains = this.getCurrentSlotChains ();
        for (int i = 0; i < 8; i++)
        {
            final int chainIndex = this.chainPageOffset + i;
            final boolean isTopMenuOn = this.getTopMenuEnablement (cd, hasPinning, i);
            final String bottomMenu = chainIndex < slotChains.length ? slotChains[chainIndex] : "";
            final String bottomMenuIcon = "";
            final boolean isBottomMenuOn = chainIndex < slotChains.length;
            display.addParameterElement (this.hostMenu[i], isTopMenuOn, bottomMenu, bottomMenuIcon, bottomMenuColor, isBottomMenuOn, "", 0, "", false, -1);
        }
""",
    "DeviceChainsMode Push 2 chain page display",
)
chains_path.write_text(chains, encoding="utf-8")


# Device parameter page buttons must advance exactly one remote-control page.
# DeviceParamsMode's inherited bank is the 8-parameter bank, so its generic
# selectNext/PreviousItemPage methods add/subtract eight page indices at once.
# Use the parameter-page bank's single-step scroll API for this mode instead.
device_params_path = ROOT / "controller/ableton/push/mode/device/DeviceParamsMode.java"
device_params = device_params_path.read_text(encoding="utf-8")
device_params = replace_once(
    device_params,
    "        super.selectPreviousItemPage ();\n",
    "        this.model.getCursorDevice ().getParameterPageBank ().scrollBackwards ();\n",
    "DeviceParamsMode previous single-page navigation",
)
device_params = replace_once(
    device_params,
    "        super.selectNextItemPage ();\n",
    "        this.model.getCursorDevice ().getParameterPageBank ().scrollForwards ();\n",
    "DeviceParamsMode next single-page navigation",
)
device_params = replace_once(
    device_params,
    "        return super.hasPreviousItemPage ();\n",
    "        return this.model.getCursorDevice ().getParameterPageBank ().canScrollBackwards ();\n",
    "DeviceParamsMode previous-page availability",
)
device_params = replace_once(
    device_params,
    "        return super.hasNextItemPage ();\n",
    "        return this.model.getCursorDevice ().getParameterPageBank ().getSelectedItemPosition () < this.model.getCursorDevice ().getParameterPageBank ().getItemCount () - 1;\n",
    "DeviceParamsMode next-page availability",
)
device_params = replace_once(
    device_params,
    "                return cursorDevice.getIndex () > 0;\n",
    "                return cursorDevice.canSelectPrevious ();\n",
    "DeviceParamsMode previous device swap availability",
)
device_params = replace_once(
    device_params,
    "                return cursorDevice.getIndex () < 7;\n",
    "                return cursorDevice.canSelectNext ();\n",
    "DeviceParamsMode next device swap availability",
)
device_params_path.write_text(device_params, encoding="utf-8")


# Browser In/Out shifts the seven-column filter viewport through all enabled
# Bitwig browser filters. The eighth Push display column remains content/results.
browser_path = ROOT / "controller/ableton/push/mode/device/DeviceBrowserMode.java"
browser = browser_path.read_text(encoding="utf-8")
browser = replace_once(
    browser,
    "    private int              filterColumn;\n",
    "    private int              filterColumn;\n"
    "    private int              displayColumnOffset;\n",
    "Browser display offset state",
)
browser = replace_once(
    browser,
    """    public void changeSelectedColumnValue (final int value)
    {
        final int index = this.filterColumn == -1 ? 7 : this.filterColumn;
        this.changeValue (index, value);
    }
""",
    """    public void changeSelectedColumnValue (final int value)
    {
        if (this.filterColumn < 0)
            this.changeValue (7, value);
        else
            this.changeFilterColumnValue (this.filterColumn, value);
    }
""",
    "Browser selected filter encoder mapping",
)
browser = replace_once(
    browser,
    """    public void resetFilterColumn ()
    {
        this.filterColumn = -1;
    }


""",
    """    public void resetFilterColumn ()
    {
        this.filterColumn = -1;
    }


    public boolean canScrollFilterColumnsLeft ()
    {
        this.clampDisplayColumnOffset ();
        return this.displayColumnOffset > 0;
    }


    public boolean canScrollFilterColumnsRight ()
    {
        this.clampDisplayColumnOffset ();
        return this.displayColumnOffset < this.getMaxDisplayColumnOffset ();
    }


    public void scrollFilterColumnsLeft ()
    {
        if (this.canScrollFilterColumnsLeft ())
        {
            this.displayColumnOffset--;
            this.resetFilterColumn ();
            this.updateDisplay ();
        }
    }


    public void scrollFilterColumnsRight ()
    {
        if (this.canScrollFilterColumnsRight ())
        {
            this.displayColumnOffset++;
            this.resetFilterColumn ();
            this.updateDisplay ();
        }
    }


    private int getVisibleFilterColumnCount ()
    {
        final IBrowser browser = this.model.getBrowser ();
        final boolean [] browserDisplayFilter = this.surface.getConfiguration ().getBrowserDisplayFilter ();
        final int count = Math.min (browser.getFilterColumnCount (), browserDisplayFilter.length);
        int visibleCount = 0;
        for (int i = 0; i < count; i++)
        {
            if (browserDisplayFilter[i])
                visibleCount++;
        }
        return visibleCount;
    }


    private int getMaxDisplayColumnOffset ()
    {
        return Math.max (0, this.getVisibleFilterColumnCount () - 7);
    }


    private void clampDisplayColumnOffset ()
    {
        this.displayColumnOffset = Math.max (0, Math.min (this.displayColumnOffset, this.getMaxDisplayColumnOffset ()));
    }


""",
    "Browser horizontal page methods",
)
browser = replace_once(
    browser,
    """    public void selectPreviousItemPage ()
    {
        this.resetFilterColumn ();
        this.model.getBrowser ().previousContentType ();
    }
""",
    """    public void selectPreviousItemPage ()
    {
        this.displayColumnOffset = 0;
        this.resetFilterColumn ();
        this.model.getBrowser ().previousContentType ();
    }
""",
    "Browser previous content type reset",
)
browser = replace_once(
    browser,
    """    public void selectNextItemPage ()
    {
        this.resetFilterColumn ();
        this.model.getBrowser ().nextContentType ();
    }
""",
    """    public void selectNextItemPage ()
    {
        this.displayColumnOffset = 0;
        this.resetFilterColumn ();
        this.model.getBrowser ().nextContentType ();
    }
""",
    "Browser next content type reset",
)
old_column_method = """    private Optional<IBrowserColumn> getFilterColumn (final int index)
    {
        final IBrowser browser = this.model.getBrowser ();
        int column = -1;
        final boolean [] browserDisplayFilter = this.surface.getConfiguration ().getBrowserDisplayFilter ();
        for (int i = 0; i < browser.getFilterColumnCount (); i++)
        {
            if (browserDisplayFilter[i])
            {
                column++;
                if (column == index)
                    return Optional.of (browser.getFilterColumn (i));
            }
        }
        return Optional.empty ();
    }


"""
new_column_method = """    private Optional<IBrowserColumn> getFilterColumn (final int index)
    {
        this.clampDisplayColumnOffset ();
        final IBrowser browser = this.model.getBrowser ();
        final boolean [] browserDisplayFilter = this.surface.getConfiguration ().getBrowserDisplayFilter ();
        final int columnCount = Math.min (browser.getFilterColumnCount (), browserDisplayFilter.length);
        final int requestedColumn = this.displayColumnOffset + index;
        int visibleColumn = -1;
        for (int i = 0; i < columnCount; i++)
        {
            if (browserDisplayFilter[i])
            {
                visibleColumn++;
                if (visibleColumn == requestedColumn)
                    return Optional.of (browser.getFilterColumn (i));
            }
        }
        return Optional.empty ();
    }


"""
browser = replace_once(browser, old_column_method, new_column_method, "Browser visible column offset mapping")
browser = replace_once(
    browser,
    """    private void selectNext (final int index, final int count)
""",
    """    private void changeFilterColumnValue (final int columnIndex, final int value)
    {
        int speed = this.model.getValueChanger ().calcSteppedKnobChange (value);
        final boolean direction = speed > 0;
        if (this.surface.isShiftPressed ())
            speed = speed * 4;

        speed = Math.abs (speed);
        final IBrowser browser = this.model.getBrowser ();
        if (direction)
        {
            for (int i = 0; i < speed; i++)
                browser.selectNextFilterItem (columnIndex);
        }
        else
        {
            for (int i = 0; i < speed; i++)
                browser.selectPreviousFilterItem (columnIndex);
        }
    }


    private void selectNext (final int index, final int count)
""",
    "Browser absolute filter encoder helper",
)
browser = replace_once(
    browser,
    """                    if (i == this.filterColumn)
                        name = Push1Display.SELECT_ARROW + name;
""",
    """                    if (column.isPresent () && column.get ().getIndex () == this.filterColumn)
                        name = Push1Display.SELECT_ARROW + name;
""",
    "Browser text display selected column marker",
)
browser = replace_once(
    browser,
    """                    display.addOptionElement (headerTopName, column.isEmpty () ? "" : column.get ().getName (), i == this.filterColumn, headerBottomName, menuBottomName, !menuBottomName.equals (" "), false);
""",
    """                    display.addOptionElement (headerTopName, column.isEmpty () ? "" : column.get ().getName (), column.isPresent () && column.get ().getIndex () == this.filterColumn, headerBottomName, menuBottomName, !menuBottomName.equals (" "), false);
""",
    "Browser graphics display selected column marker",
)
browser_path.write_text(browser, encoding="utf-8")


# Drive the physical buttons and their LEDs from exactly the same context logic.
setup_path = ROOT / "controller/ableton/push/PushControllerSetup.java"
setup = setup_path.read_text(encoding="utf-8")
old_registration = """        this.addButton (ButtonID.PAGE_LEFT, "Page Left", new PageLeftCommand (this.model, surface), PushControlSurface.PUSH_BUTTON_DEVICE_LEFT, () -> {

            if (viewManager.isActive (Views.SESSION))
                return this.model.getCurrentTrackBank ().canScrollPageBackwards ();
            final IView activeView = viewManager.getActive ();
            final INoteClip clip = activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView) ? sequencerView.getClip () : null;
            return clip != null && clip.doesExist () && clip.canScrollStepsBackwards ();

        }, ColorManager.BUTTON_STATE_OFF, ColorManager.BUTTON_STATE_ON);
        this.addButton (ButtonID.PAGE_RIGHT, "Page Right", new PageRightCommand (this.model, surface), PushControlSurface.PUSH_BUTTON_DEVICE_RIGHT, () -> {

            if (viewManager.isActive (Views.SESSION))
                return this.model.getCurrentTrackBank ().canScrollPageForwards ();
            final IView activeView = viewManager.getActive ();
            final INoteClip clip = activeView instanceof final AbstractSequencerView<?, ?> sequencerView && !(activeView instanceof ClipLengthView) ? sequencerView.getClip () : null;
            return clip != null && clip.doesExist () && clip.canScrollStepsForwards ();

        }, ColorManager.BUTTON_STATE_OFF, ColorManager.BUTTON_STATE_ON);
"""
new_registration = """        final PageLeftCommand pageLeftCommand = new PageLeftCommand (this.model, surface);
        this.addButton (ButtonID.PAGE_LEFT, "Page Left", pageLeftCommand, PushControlSurface.PUSH_BUTTON_DEVICE_LEFT, pageLeftCommand::canNavigate, ColorManager.BUTTON_STATE_OFF, ColorManager.BUTTON_STATE_ON);
        final PageRightCommand pageRightCommand = new PageRightCommand (this.model, surface);
        this.addButton (ButtonID.PAGE_RIGHT, "Page Right", pageRightCommand, PushControlSurface.PUSH_BUTTON_DEVICE_RIGHT, pageRightCommand::canNavigate, ColorManager.BUTTON_STATE_OFF, ColorManager.BUTTON_STATE_ON);
"""
setup = replace_once(setup, old_registration, new_registration, "Push In/Out command and LED registration")
setup_path.write_text(setup, encoding="utf-8")


# Fail safely if any of the intended behaviors was not patched.
for command_name, required in (
    ("PageLeftCommand.java", ("scrollFilterColumnsLeft ()", "selectPreviousItemPage ()", "sequencerView.onLeft (event)", "canNavigate ()")),
    ("PageRightCommand.java", ("scrollFilterColumnsRight ()", "selectNextItemPage ()", "sequencerView.onRight (event)", "canNavigate ()")),
):
    content = (ROOT / "controller/ableton/push/command/trigger" / command_name).read_text(encoding="utf-8")
    for token in required:
        if token not in content:
            raise SystemExit(f"{command_name}: missing navigation postcondition {token}")

page_left_source = (ROOT / "controller/ableton/push/command/trigger/PageLeftCommand.java").read_text(encoding="utf-8")
page_right_source = (ROOT / "controller/ableton/push/command/trigger/PageRightCommand.java").read_text(encoding="utf-8")
for page_source in (page_left_source, page_right_source):
    if "Views.SESSION" in page_source or "selectPreviousPage ()" in page_source or "selectNextPage ()" in page_source:
        raise SystemExit("Page commands: redundant Session page navigation remains")

track_helper_source = track_helper_path.read_text(encoding="utf-8")
for token in (
    "Modes.SESSION",
    "Modes.isTrackMode (activeModeID)",
    "surface.isShiftPressed ()",
    "cursorTrack.swapWithPrevious ()",
    "cursorTrack.swapWithNext ()",
    "cursorTrack.canSelectPrevious ()",
    "cursorTrack.canSelectNext ()",
    "return true;",
):
    if token not in track_helper_source:
        raise SystemExit(f"Push1TrackMoveCommand: missing safety postcondition {token}")

for command_name in ("PageLeftCommand.java", "PageRightCommand.java"):
    page_source = (ROOT / "controller/ableton/push/command/trigger" / command_name).read_text(encoding="utf-8")
    if "Push1TrackMoveCommand.executeIfRequested" not in page_source:
        raise SystemExit(f"{command_name}: Shift + In/Out track move was not routed")

cursor_track_source = cursor_track_path.read_text(encoding="utf-8")
if "largeTrackBank" in cursor_track_source or "getPosition () - 1" in cursor_track_source or "getPosition () + 1" in cursor_track_source:
    raise SystemExit("CursorTrackImpl: unsafe flat-bank track-neighbour lookup remains")

updated_browser = browser_path.read_text(encoding="utf-8")
for token in ("displayColumnOffset", "canScrollFilterColumnsLeft", "canScrollFilterColumnsRight", "changeFilterColumnValue"):
    if token not in updated_browser:
        raise SystemExit(f"DeviceBrowserMode: missing browser navigation postcondition {token}")

updated_chains = chains_path.read_text(encoding="utf-8")
for token in ("CHAINS_PER_PAGE", "selectPreviousItemPage", "selectNextItemPage", "hasPreviousItemPage", "hasNextItemPage"):
    if token not in updated_chains:
        raise SystemExit(f"DeviceChainsMode: missing chain navigation postcondition {token}")

device_params = device_params_path.read_text(encoding="utf-8")
for token in (
    "getParameterPageBank ().scrollBackwards ()",
    "getParameterPageBank ().scrollForwards ()",
    "getParameterPageBank ().canScrollBackwards ()",
    "getSelectedItemPosition () < this.model.getCursorDevice ().getParameterPageBank ().getItemCount () - 1",
    "cursorDevice.canSelectPrevious ()",
    "cursorDevice.canSelectNext ()",
):
    if token not in device_params:
        raise SystemExit(f"DeviceParamsMode: missing single-page navigation postcondition {token}")
if "super.selectPreviousItemPage ()" in device_params or "super.selectNextItemPage ()" in device_params:
    raise SystemExit("DeviceParamsMode: old 8-parameter-bank page jump is still present")


if "pageLeftCommand::canNavigate" not in setup or "pageRightCommand::canNavigate" not in setup:
    raise SystemExit("PushControllerSetup: In/Out LED state is not linked to command availability")

if not context_path.is_file() or "static boolean isDeviceNavigationMode" not in context_path.read_text(encoding="utf-8"):
    raise SystemExit("Push1NavigationContext: shared Device mode helper is missing")

cursor_command_source = (ROOT / "controller/ableton/push/command/trigger/PushCursorCommand.java").read_text(encoding="utf-8")
for token in ("isShiftTrackNavigationDisabled ()", "activeModeID == Modes.SESSION", "Modes.isTrackMode (activeModeID)"):
    if token not in cursor_command_source:
        raise SystemExit(f"PushCursorCommand: Shift + track-arrow guard missing: {token}")

print("StrattV4 Push 1 navigation applied: Shift + In/Out owns track/group/device moves; Shift + Left/Right is disabled for track contexts; other navigation is preserved.")
