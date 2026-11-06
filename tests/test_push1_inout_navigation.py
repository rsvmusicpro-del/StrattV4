#!/usr/bin/env python3
"""Static regression checks for the StrattV4 Push 1 In/Out patch."""

from pathlib import Path
import unittest

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
COMMANDS = ROOT / "controller/ableton/push/command/trigger"
BROWSER = ROOT / "controller/ableton/push/mode/device/DeviceBrowserMode.java"
CHAINS = ROOT / "controller/ableton/push/mode/device/DeviceChainsMode.java"
DEVICE_PARAMS = ROOT / "controller/ableton/push/mode/device/DeviceParamsMode.java"
SETUP = ROOT / "controller/ableton/push/PushControllerSetup.java"
PUSH_CURSOR = COMMANDS / "PushCursorCommand.java"
CONTEXT = COMMANDS / "Push1NavigationContext.java"


class Push1InOutNavigationTests(unittest.TestCase):
    def test_left_and_right_commands_are_contextual(self):
        left = (COMMANDS / "PageLeftCommand.java").read_text(encoding="utf-8")
        right = (COMMANDS / "PageRightCommand.java").read_text(encoding="utf-8")

        cases = (
            (left, "scrollFilterColumnsLeft ()", "selectPreviousItemPage ()", "sequencerView.onLeft (event)"),
            (right, "scrollFilterColumnsRight ()", "selectNextItemPage ()", "sequencerView.onRight (event)"),
        )
        for source, browser_action, device_action, sequencer_action in cases:
            with self.subTest(command="left" if source is left else "right"):
                self.assertIn("modeManager.isActive (Modes.BROWSER)", source)
                self.assertIn("Push1NavigationContext.isDeviceNavigationMode (modeManager)", source)
                self.assertIn(browser_action, source)
                self.assertIn(device_action, source)
                self.assertNotIn("Views.SESSION", source)
                self.assertIn("!(activeView instanceof ClipLengthView)", source)
                self.assertIn(sequencer_action, source)
                self.assertIn("public boolean canNavigate ()", source)

    def test_cursor_arrows_move_tracks_one_by_one_and_eight_with_shift(self):
        source = PUSH_CURSOR.read_text(encoding="utf-8")
        left = source[source.index("protected void scrollLeft"):source.index("protected void scrollRight")]
        right = source[source.index("protected void scrollRight"):source.index("protected ISceneBank getSceneBank")]
        self.assertIn("Modes.BROWSER", left)
        self.assertIn("activeMode.selectPreviousItemPage ()", left)
        self.assertIn("trackBank.selectPreviousItem ()", left)
        self.assertIn("trackBank.selectPreviousPage ()", left)
        self.assertIn("isShiftPressed ()", left)
        self.assertIn("Modes.BROWSER", right)
        self.assertIn("activeMode.selectNextItemPage ()", right)
        self.assertIn("trackBank.selectNextItem ()", right)
        self.assertIn("trackBank.selectNextPage ()", right)
        self.assertIn("isShiftPressed ()", right)

    def test_cursor_leds_match_shifted_track_and_scene_pages(self):
        source = PUSH_CURSOR.read_text(encoding="utf-8")
        update = source[source.index("protected void updateArrowStates"):]
        for token in (
            "trackBank.canScrollBackwards ()",
            "trackBank.canScrollForwards ()",
            "trackBank.canScrollPageBackwards ()",
            "trackBank.canScrollPageForwards ()",
            "sceneBank.canScrollPageBackwards ()",
            "sceneBank.canScrollPageForwards ()",
            "isShiftPressed ()",
        ):
            self.assertIn(token, update)

    def test_device_mode_context_is_declared_once(self):
        source = CONTEXT.read_text(encoding="utf-8")
        self.assertIn("static boolean isDeviceNavigationMode", source)
        self.assertIn("Modes.DEVICE_CHAINS || Modes.isDeviceMode", source)
        nav_script = (Path("scripts") / "apply_push1_navigation.py").read_text(encoding="utf-8")
        self.assertEqual(nav_script.count("private static boolean isDeviceNavigationMode"), 0)
        self.assertEqual(nav_script.count("Push1NavigationContext.isDeviceNavigationMode"), 4)

    def test_browser_shifts_a_seven_column_window(self):
        source = BROWSER.read_text(encoding="utf-8")
        self.assertIn("displayColumnOffset", source)
        self.assertIn("getMaxDisplayColumnOffset", source)
        self.assertIn("Math.min (browser.getFilterColumnCount (), browserDisplayFilter.length)", source)
        self.assertIn("this.displayColumnOffset + index", source)
        self.assertIn("changeFilterColumnValue (this.filterColumn, value)", source)
        self.assertIn("column.get ().getIndex () == this.filterColumn", source)
        left = source[source.index("public void scrollFilterColumnsLeft"):source.index("public void scrollFilterColumnsRight")]
        right = source[source.index("public void scrollFilterColumnsRight"):source.index("private int getVisibleFilterColumnCount")]
        mapping = source[source.index("private Optional<IBrowserColumn> getFilterColumn"):source.index("private void changeFilterColumnValue")]
        self.assertIn("this.resetFilterColumn ()", left)
        self.assertIn("this.resetFilterColumn ()", right)
        self.assertIn("this.clampDisplayColumnOffset ()", mapping)

    def test_device_parameter_page_navigation_moves_one_page_at_a_time(self):
        source = DEVICE_PARAMS.read_text(encoding="utf-8")
        self.assertIn("getParameterPageBank ().scrollBackwards ()", source)
        self.assertIn("getParameterPageBank ().scrollForwards ()", source)
        self.assertIn("getParameterPageBank ().canScrollBackwards ()", source)
        self.assertIn("cursorDevice.canSelectPrevious ()", source)
        self.assertIn("cursorDevice.canSelectNext ()", source)
        self.assertIn("getSelectedItemPosition () < this.model.getCursorDevice ().getParameterPageBank ().getItemCount () - 1", source)
        # The inherited parameter-bank methods jump by eight parameter-page indices.
        self.assertNotIn("super.selectPreviousItemPage ()", source)
        self.assertNotIn("super.selectNextItemPage ()", source)

    def test_rack_chains_are_paginated_in_groups_of_eight(self):
        source = CHAINS.read_text(encoding="utf-8")
        self.assertIn("private static final int CHAINS_PER_PAGE = 8", source)
        self.assertIn("this.chainPageOffset + index", source)
        self.assertIn("this.chainPageOffset += CHAINS_PER_PAGE", source)
        self.assertIn("this.chainPageOffset + CHAINS_PER_PAGE < this.getCurrentSlotChains ().length", source)

    def test_leds_follow_the_same_availability_as_commands(self):
        source = SETUP.read_text(encoding="utf-8")
        self.assertIn("pageLeftCommand::canNavigate", source)
        self.assertIn("pageRightCommand::canNavigate", source)
        self.assertIn("PushControlSurface.PUSH_BUTTON_DEVICE_LEFT", source)
        self.assertIn("PushControlSurface.PUSH_BUTTON_DEVICE_RIGHT", source)


if __name__ == "__main__":
    unittest.main()
