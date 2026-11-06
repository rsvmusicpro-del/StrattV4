#!/usr/bin/env python3
"""Regression checks for the additive Push 1 device-reordering gesture."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from patch_manifest import PATCH_STEPS, REQUIRED_SOURCES

SCRIPT = ROOT / "scripts/apply_push1_device_reorder.py"


class Push1DeviceReorderTests(unittest.TestCase):
    def test_reorder_patch_runs_after_existing_device_navigation(self):
        patch_names = tuple(step.script for step in PATCH_STEPS)
        navigation = patch_names.index("apply_push1_navigation.py")
        reorder = patch_names.index("apply_push1_device_reorder.py")
        self.assertLess(navigation, reorder)
        self.assertIn(
            "controller/ableton/push/command/trigger/Push1DeviceMoveCommand.java",
            REQUIRED_SOURCES,
        )

    def test_new_helper_is_generated_without_replacing_existing_mappings(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('helper_path = TRIGGER / "Push1DeviceMoveCommand.java"', source)
        self.assertIn('patch_page_command("PageLeftCommand", True)', source)
        self.assertIn('patch_page_command("PageRightCommand", False)', source)
        self.assertIn("replace_once(", source)
        self.assertIn("Push1DeviceMoveCommand.executeIfRequested", source)
        self.assertIn("Refusing to overwrite an existing source", source)
        self.assertNotIn("PushControllerSetup.java", source)
        self.assertNotIn("ButtonID.", source)

    def test_move_is_limited_to_shift_chord_in_device_navigation_modes(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("surface.isShiftPressed ()", source)
        self.assertIn("Push1NavigationContext.isDeviceNavigationMode (modeManager)", source)
        self.assertIn("event == ButtonEvent.DOWN", source)
        self.assertIn("cursorDevice.doesExist ()", source)

    def test_only_existing_adjacent_devices_can_be_swapped(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("cursorDevice.canSelectPrevious ()", source)
        self.assertIn("cursorDevice.swapWithPrevious ()", source)
        self.assertIn("cursorDevice.canSelectNext ()", source)
        self.assertIn("cursorDevice.swapWithNext ()", source)
        self.assertIn("return true;", source)

    def test_plain_in_out_navigation_remains_outside_the_new_helper(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("selectPreviousItemPage", source)
        self.assertNotIn("selectNextItemPage", source)
        self.assertNotIn("DeviceChainsMode.java", source)
        self.assertNotIn("PushCursorCommand.java", source)


if __name__ == "__main__":
    unittest.main()
