#!/usr/bin/env python3
"""Apply StrattV4 patches transactionally to the pinned DrivenByMoss source tree.

All StrattV4 Push 1 patch sets run against a staged copy. The checked-out
submodule is swapped only after every patch and its postconditions succeed.
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SUBMODULE = REPOSITORY_ROOT / "vendor" / "DrivenByMoss"
SOURCE_ROOT = SUBMODULE / "src" / "main" / "java" / "de" / "mossgrabers"
PATCH_SCRIPTS = (
    # Restore the proven #389 global touch gate and symmetric MIDI unbind/rebind lifecycle.
    REPOSITORY_ROOT / "scripts" / "apply_push1_all_encoder_vu.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_master_display.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_touch_lifecycle.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_palette.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_smart.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_midi_lifecycle.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_poly_sequencer_lifecycle.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_note_sequencer_lifecycle.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_modifier_gestures.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_note_edit_touch_owner.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_navigation.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_device_reorder.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_track_reorder.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_french.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_startup_message.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_long_names.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_clip_accent.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_playhead.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_small_knob_guard.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_encoder_touch.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_new_scene.py",
    REPOSITORY_ROOT / "scripts" / "apply_push1_new_scene_gesture.py",
)
EXPECTED_UPSTREAM = "013620c1330cdcf896e96ef8fdc8a2123e4fce6a"


def main() -> int:
    if not SOURCE_ROOT.is_dir():
        raise SystemExit(f"DrivenByMoss source tree is missing: {SOURCE_ROOT}")
    for patch_script in PATCH_SCRIPTS:
        if not patch_script.is_file():
            raise SystemExit(f"Patch script is missing: {patch_script}")

    revision = subprocess.run(
        ["git", "-C", str(SUBMODULE), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if revision != EXPECTED_UPSTREAM:
        raise SystemExit(
            "Refusing to patch an unexpected DrivenByMoss revision: "
            f"expected {EXPECTED_UPSTREAM}, found {revision}"
        )

    # Refuse to build on a locally modified or untracked upstream Java tree.
    # The checksum sidecar repair in CI is outside this source subtree and is
    # intentionally unaffected by this guard.
    source_status = subprocess.run(
        ["git", "-C", str(SUBMODULE), "status", "--porcelain", "--", "src/main/java/de/mossgrabers"],
        check=True, capture_output=True, text=True,
    ).stdout
    if source_status.strip():
        raise SystemExit(
            "Refusing to patch a modified DrivenByMoss Java source tree; "
            "restore the pinned source before building:\\n" + source_status
        )

    parent = SOURCE_ROOT.parent
    with tempfile.TemporaryDirectory(prefix=".strattv4-push1-stage-", dir=parent) as temporary:
        staging_submodule = Path(temporary) / "vendor" / "DrivenByMoss"
        staging_root = staging_submodule / "src" / "main" / "java" / "de" / "mossgrabers"
        staging_root.parent.mkdir(parents=True)
        shutil.copytree(SOURCE_ROOT, staging_root)

        # All destructive edits happen in the temporary tree. A failed anchor,
        # missing file or postcondition leaves the checked-out source untouched.
        for patch_script in PATCH_SCRIPTS:
            subprocess.run(
                [sys.executable, "-B", str(patch_script)],
                cwd=Path(temporary),
                check=True,
            )

        required_sources = (
            staging_root / "framework" / "daw" / "DAWColor.java",
            staging_root / "controller" / "ableton" / "push" / "PushControllerSetup.java",
            staging_root / "controller" / "ableton" / "push" / "view" / "SmartView.java",
            staging_root / "framework" / "view" / "PadMidiNoteTracker.java",
            staging_root / "bitwig" / "framework" / "hardware" / "HwRelativeKnobImpl.java",
            staging_root / "controller" / "ableton" / "push" / "view" / "PadViewTaskGuard.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "PageLeftCommand.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "PushCursorCommand.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "PageRightCommand.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "Push1NavigationContext.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "Push1DeviceMoveCommand.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "Push1TrackMoveCommand.java",
            staging_root / "controller" / "ableton" / "push" / "mode" / "device" / "DeviceBrowserMode.java",
            staging_root / "controller" / "ableton" / "push" / "mode" / "device" / "DeviceChainsMode.java",
            staging_root / "controller" / "ableton" / "push" / "mode" / "device" / "DeviceLayerDetailsMode.java",
            staging_root / "controller" / "ableton" / "push" / "controller" / "Push1French.java",
            staging_root / "framework" / "daw" / "constants" / "TransportConstants.java",
            staging_root / "controller" / "ableton" / "push" / "mode" / "track" / "MasterMode.java",
            staging_root / "controller" / "ableton" / "push" / "mode" / "track" / "ClipMode.java",
            staging_root / "controller" / "ableton" / "push" / "command" / "trigger" / "PlayPositionKnobCommand.java",
            staging_root / "framework" / "command" / "trigger" / "mode" / "KnobTouchOwner.java",
            staging_root / "framework" / "command" / "trigger" / "clip" / "NewCommand.java",
            staging_root / "framework" / "command" / "trigger" / "clip" / "Push1SelectGesture.java",
            staging_root / "framework" / "mode" / "NoteEditTouchOwner.java",
        )
        for required_source in required_sources:
            if not required_source.is_file():
                raise SystemExit(f"Staged patch validation failed: {required_source.relative_to(staging_root)} is missing")

        backup = Path(temporary) / "mossgrabers-original"
        os.replace(SOURCE_ROOT, backup)
        try:
            os.replace(staging_root, SOURCE_ROOT)
        except Exception:
            # Restore the exact original directory if the final rename fails.
            os.replace(backup, SOURCE_ROOT)
            raise

    print("Transactional StrattV4 Push 1 customizations completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
