#!/usr/bin/env python3
"""Regression checks for the StrattV4 build and transactional patch pipeline."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/main.yml"
PATCHER = ROOT / "scripts/apply_push1_palette_transactional.py"


class Push1BuildPipelineTests(unittest.TestCase):
    def test_workflow_checks_out_the_recursive_pinned_submodule(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", source)
        self.assertIn("uses: actions/setup-java@b843ebf9b913146b38da2eaa7aeddf76074ae1ad", source)
        upload_action = "uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"
        self.assertEqual(source.count(upload_action), 1, "the workflow must publish exactly one test artifact")
        self.assertEqual(source.count("name: StrattV4-Push1-Test"), 1)
        self.assertNotIn("StrattV4-Push1\n", source)
        self.assertNotIn("Upload StrattV4 release candidate", source)
        self.assertNotIn("actions/checkout@v4", source)
        self.assertNotIn("actions/setup-java@v4", source)
        self.assertNotIn("actions/upload-artifact@v4", source)
        self.assertIn("submodules: recursive", source)
        self.assertIn("permissions:\n  contents: read", source)
        self.assertIn("persist-credentials: false", source)
        self.assertIn("branches: [evolution]", source)
        self.assertNotIn("branches: [main, v4-foundation]", source)
        self.assertNotIn("v4-foundation", source)
        self.assertIn("Build StrattV4 Push 1", source)
        self.assertIn("timeout-minutes: 30", source)
        self.assertIn('expected="013620c1330cdcf896e96ef8fdc8a2123e4fce6a"', source)

    def test_workflow_repairs_only_the_known_stale_checksum_in_ci(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Repair stale nativefilechooser POM checksum in CI workspace", source)
        self.assertIn("expected_stale=\"681a3e092c24eee87603e5058b0baf616d704118\"", source)
        self.assertIn("expected_actual=\"6728463afe1035bf871269c076c24d615acc683f\"", source)
        self.assertIn("sha1sum \"$pom\"", source)

    def test_workflow_tests_before_build_and_registers_only_push1(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        tests = source.index("python3 -B -m unittest discover")
        build = source.index("mvn -B package")
        self.assertLess(tests, build)
        self.assertNotIn("-DskipTests", source)
        self.assertIn(
            "de.mossgrabers.bitwig.controller.ableton.push.Push1ControllerExtensionDefinition",
            source,
        )
        self.assertNotIn("Push2ControllerExtensionDefinition", source)

    def test_all_customizations_run_in_staging_before_atomic_swap(self):
        source = PATCHER.read_text(encoding="utf-8")
        scripts = (
            "apply_push1_all_encoder_vu.py",
            "apply_push1_master_display.py",
            "apply_push1_touch_lifecycle.py",
            "apply_push1_palette.py",
            "apply_push1_smart.py",
            "apply_push1_midi_lifecycle.py",
            "apply_push1_poly_sequencer_lifecycle.py",
            "apply_push1_note_sequencer_lifecycle.py",
            "apply_push1_modifier_gestures.py",
            "apply_push1_note_edit_touch_owner.py",
            "apply_push1_navigation.py",
            "apply_push1_device_reorder.py",
            "apply_push1_track_reorder.py",
            "apply_push1_french.py",
            "apply_push1_startup_message.py",
            "apply_push1_long_names.py",
            "apply_push1_clip_accent.py",
            "apply_push1_playhead.py",
            "apply_push1_small_knob_guard.py",
            "apply_push1_encoder_touch.py",
            "apply_push1_new_scene.py",
            "apply_push1_new_scene_gesture.py",
        )
        positions = [source.index(name) for name in scripts]
        self.assertEqual(positions, sorted(positions))
        run_loop = source.index("for patch_script in PATCH_SCRIPTS:")
        swap = source.index("os.replace(SOURCE_ROOT, backup)")
        install = source.index("os.replace(staging_root, SOURCE_ROOT)")
        restore = source.index("os.replace(backup, SOURCE_ROOT)")
        self.assertLess(run_loop, swap)
        self.assertLess(swap, install)
        self.assertLess(install, restore)
        self.assertIn("if revision != EXPECTED_UPSTREAM:", source)
        self.assertIn('"SmartView.java"', source)
        self.assertIn('"KnobTouchOwner.java"', source)
        self.assertIn('"Push1SelectGesture.java"', source)
        self.assertIn('"status", "--porcelain", "--", "src/main/java/de/mossgrabers"', source)
        self.assertIn("Refusing to patch a modified DrivenByMoss Java source tree", source)
        self.assertNotIn("CheatView.java", source)
        self.assertNotIn("apply_push1_cheat.py", source)
        self.assertIn("except Exception:", source)

    def test_transactional_pipeline_patch_scripts_are_unique(self):
        source = PATCHER.read_text(encoding="utf-8")
        scripts = (
            "apply_push1_all_encoder_vu.py",
            "apply_push1_master_display.py",
            "apply_push1_touch_lifecycle.py",
            "apply_push1_palette.py",
            "apply_push1_smart.py",
            "apply_push1_midi_lifecycle.py",
            "apply_push1_poly_sequencer_lifecycle.py",
            "apply_push1_note_sequencer_lifecycle.py",
            "apply_push1_modifier_gestures.py",
            "apply_push1_note_edit_touch_owner.py",
            "apply_push1_navigation.py",
            "apply_push1_device_reorder.py",
            "apply_push1_track_reorder.py",
            "apply_push1_french.py",
            "apply_push1_startup_message.py",
            "apply_push1_long_names.py",
            "apply_push1_clip_accent.py",
            "apply_push1_playhead.py",
            "apply_push1_small_knob_guard.py",
            "apply_push1_encoder_touch.py",
            "apply_push1_new_scene.py",
            "apply_push1_new_scene_gesture.py",
        )
        for name in scripts:
            with self.subTest(script=name):
                self.assertEqual(source.count(f'"{name}"'), 1)


    def test_push1_startup_message_is_left_aligned_at_top(self):
        source = (ROOT / "scripts/apply_push1_startup_message.py").read_text(encoding="utf-8")
        self.assertIn('"     Please start"', source)
        self.assertIn('this.host.getName () + " to play..."', source)
        self.assertNotIn("MICHA EST TROP", source)

    def test_legacy_encoder_guards_and_touch_lifecycle_are_part_of_every_build(self):
        patcher = PATCHER.read_text(encoding="utf-8")
        self.assertLess(patcher.index("apply_push1_all_encoder_vu.py"), patcher.index("apply_push1_touch_lifecycle.py"))
        self.assertLess(patcher.index("apply_push1_touch_lifecycle.py"), patcher.index("apply_push1_palette.py"))
        self.assertNotIn("apply_push1_vu_startup_state.py", patcher)
        self.assertIn("HwRelativeKnobImpl.java", patcher)
        encoder = (ROOT / "scripts/apply_push1_all_encoder_vu.py").read_text(encoding="utf-8")
        touch = (ROOT / "scripts/apply_push1_touch_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("this.touchCommand != null && !this.isTouched ()", encoder)
        self.assertIn("this.touchInput.bindTouch", touch)
        self.assertIn("this.triggerTouch (false);", touch)
        self.assertIn("beginTouchAction ().setActionMatcher (null)", touch)

    def test_all_play_family_views_guard_both_delayed_mapping_stages(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("guard final delayed mapping application for every view", lifecycle)
        self.assertIn("guard first delayed mapping calculation for every Play-family view", lifecycle)
        self.assertIn("beginNoteMappingUpdate ()", lifecycle)
        self.assertIn("isNoteMappingUpdateCurrent (generation)", lifecycle)
        self.assertIn("this.delayedUpdateNoteMapping (this.getMapping (), generation)", lifecycle)
        self.assertIn("++this.noteMappingGeneration;", lifecycle)

    def test_all_views_clear_pressed_pad_state_when_deactivated(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("this.keyManager.clearPressedKeys ();", lifecycle)
        self.assertIn("invalidate pending mappings on view deactivation", lifecycle)
        self.assertIn("++this.noteMappingGeneration;", lifecycle)

    def test_push1_shutdown_deactivates_active_view_before_hardware_shutdown(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("Push 1 active view shutdown cleanup", lifecycle)
        self.assertIn("final IView activeView = this.getViewManager ().getActive ();", lifecycle)
        self.assertIn("activeView.onDeactivate ();", lifecycle)
        self.assertIn("activeView.onDeactivate ();\n\n        this.setRibbonMode", lifecycle)
        self.assertIn("this.setRibbonValue (0);\n\n        super.internalShutdown ();", lifecycle)

    def test_smart_keeps_native_root_note_and_tracks_only_added_chord_tones(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        smart = lifecycle.split('new_smart_method = """', 1)[1].split('"""', 1)[0]
        self.assertIn("super.onGridNote (key, velocity);", smart)
        self.assertIn("noteOn (key, channel, additionalNotes, chordVelocity", smart)
        self.assertNotIn("noteOn (key, channel, rootNote, additionalNotes", smart)

    def test_chord_tracker_excludes_the_native_root_pitch(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("noteOnExcept (key, channel, note, chord, chordVelocity", lifecycle)
        self.assertIn("noteOn (key, channel, additionalNotes, chordVelocity", lifecycle)
        self.assertIn("this.releaseChordNote (key);", lifecycle)

    def test_midi_ledger_is_bounded_and_allocation_free(self):
        lifecycle = (ROOT / "scripts/apply_push1_midi_lifecycle.py").read_text(encoding="utf-8")
        self.assertIn("private static final int NOTE_WORD_COUNT = NOTE_COUNT / Long.SIZE", lifecycle)
        self.assertIn("long [] padNotes = new long [PAD_COUNT * NOTE_WORD_COUNT]", lifecycle)
        self.assertIn("int [] references = new int [CHANNEL_COUNT * NOTE_COUNT]", lifecycle)
        self.assertIn("final int padNoteIndex = pad * NOTE_WORD_COUNT + word;", lifecycle)
        self.assertIn("final int referenceIndex = channel * NOTE_COUNT + note;", lifecycle)
        self.assertNotIn("long [][] padNotes", lifecycle)
        self.assertNotIn("int [][] references", lifecycle)
        self.assertIn("Long.numberOfTrailingZeros (activeNotes)", lifecycle)
        self.assertIn("activeNotes &= activeNotes - 1", lifecycle)
        self.assertIn("private static boolean isValidPad", lifecycle)
        self.assertNotIn("LinkedHashMap", lifecycle)
        self.assertNotIn("LinkedHashSet", lifecycle)

    def test_async_view_task_guard_is_compiled_and_required_in_staging(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        patcher = PATCHER.read_text(encoding="utf-8")
        self.assertIn("PadViewTaskGuard.java", workflow)
        self.assertIn("PadViewTaskGuardTest.java", workflow)
        self.assertIn("PadViewTaskGuard.java", patcher)
        self.assertIn("PadViewTaskGuardTest", workflow)
        self.assertIn("Push1SelectGestureTest.java", workflow)
        self.assertIn("Push1SelectGestureTest", workflow)
        self.assertIn("NoteEditTouchOwner.java", workflow)
        self.assertIn("NoteEditTouchOwnerTest.java", workflow)
        self.assertIn("apply_push1_poly_sequencer_lifecycle.py", patcher)
        self.assertIn("apply_push1_note_sequencer_lifecycle.py", patcher)
        self.assertIn("apply_push1_modifier_gestures.py", patcher)
        self.assertIn("apply_push1_note_edit_touch_owner.py", patcher)


if __name__ == "__main__":
    unittest.main()
