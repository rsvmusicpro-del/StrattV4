#!/usr/bin/env python3
"""Apply Ableton-style Push 1 In/Out navigation to pinned DrivenByMoss."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


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


# Device-mode In/Out: DeviceParamsMode already pages device and parameter banks.
# DeviceChainsMode gets explicit pages for Rack chains, eight entries per page.
patch_page_command("PageLeftCommand", "left")
patch_page_command("PageRightCommand", "right")

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

cursor = cursor_path.read_text(encoding="utf-8")
for token in (
    "final var trackBank = this.model.getCurrentTrackBank ()",
    "trackBank.selectPreviousItem ()",
    "trackBank.selectNextItem ()",
    "trackBank.canScrollBackwards ()",
    "trackBank.canScrollForwards ()",
    "trackBank.selectPreviousPage ()",
    "trackBank.selectNextPage ()",
    "trackBank.canScrollPageBackwards ()",
    "trackBank.canScrollPageForwards ()",
    "sceneBank.canScrollPageBackwards ()",
    "sceneBank.canScrollPageForwards ()",
    "Modes.BROWSER",
):
    if token not in cursor:
        raise SystemExit(f"PushCursorCommand: missing arrow navigation postcondition {token}")
if "activeMode.selectPreviousItemPage ()" not in cursor or "activeMode.selectNextItemPage ()" not in cursor:
    raise SystemExit("PushCursorCommand: Browser content-type navigation was not preserved")
if "this.surface.isShiftPressed () && this.isTrackReorderContext ()" not in cursor:
    raise SystemExit("PushCursorCommand: Shift+arrow track move gesture is missing")
if "private boolean isTrackReorderContext ()" not in cursor or "Modes.TRACK" not in cursor or "Modes.VOLUME" not in cursor:
    raise SystemExit("PushCursorCommand: Session/Track/Volume contexts are not all supported")
left = cursor[cursor.index("protected void scrollLeft"):cursor.index("protected void scrollRight")]
right = cursor[cursor.index("protected void scrollRight"):cursor.index("protected ISceneBank getSceneBank")]
if "isSelectPressed" in left or "isSelectPressed" in right:
    raise SystemExit("PushCursorCommand: obsolete SELECT track-reorder assignment remains")

if not context_path.is_file() or "static boolean isDeviceNavigationMode" not in context_path.read_text(encoding="utf-8"):
    raise SystemExit("Push1NavigationContext: shared Device mode helper is missing")

print("StrattV4 Push 1 In/Out navigation applied: Browser columns, Device/parameter banks, Rack chains, Session pages and sequencer pages.")
