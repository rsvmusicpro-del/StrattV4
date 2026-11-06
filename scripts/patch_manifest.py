"""Single source of truth for StrattV4's ordered DrivenByMoss patch pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EXPECTED_UPSTREAM = "013620c1330cdcf896e96ef8fdc8a2123e4fce6a"


@dataclass(frozen=True)
class PatchStep:
    """One ordered, independently executable customization."""

    script: str
    purpose: str


PATCH_STEPS = (
    PatchStep("apply_push1_all_encoder_vu.py", "Guard encoder rotations and initialize live VU state."),
    PatchStep("apply_push1_master_display.py", "Restore the Push 1 master-volume position marker."),
    PatchStep("apply_push1_touch_lifecycle.py", "Keep encoder touch bind/unbind lifecycle symmetric."),
    PatchStep("apply_push1_palette.py", "Apply the 64-color Push 1 palette and LED mapping."),
    PatchStep("apply_push1_smart.py", "Register SMART while preserving native tools."),
    PatchStep("apply_push1_midi_lifecycle.py", "Protect MIDI note and delayed mapping lifecycles."),
    PatchStep("apply_push1_poly_sequencer_lifecycle.py", "Reset poly-sequencer gesture state on context changes."),
    PatchStep("apply_push1_note_sequencer_lifecycle.py", "Reset note-sequencer gestures on context changes."),
    PatchStep("apply_push1_modifier_gestures.py", "Latch modifier gestures at button-down."),
    PatchStep("apply_push1_note_edit_touch_owner.py", "Keep note-edit transactions bound to their original clip."),
    PatchStep("apply_push1_navigation.py", "Add context-aware Push 1 In/Out navigation."),
    PatchStep("apply_push1_track_reorder.py", "Resolve track moves through the cursor's sibling bank."),
    PatchStep("apply_push1_device_reorder.py", "Add one-position device-chain reordering."),
    PatchStep("apply_push1_french.py", "Apply French UI strings and safe ASCII SysEx output."),
    PatchStep("apply_push1_startup_message.py", "Preserve the actionable startup prompt."),
    PatchStep("apply_push1_long_names.py", "Improve display of long track and device names."),
    PatchStep("apply_push1_clip_accent.py", "Apply the Push 1 clip accent behavior."),
    PatchStep("apply_push1_playhead.py", "Apply the Push 1 playhead display behavior."),
    PatchStep("apply_push1_small_knob_guard.py", "Guard small encoder interactions."),
    PatchStep("apply_push1_encoder_touch.py", "Apply encoder touch behavior."),
    PatchStep("apply_push1_new_scene.py", "Add the Push 1 new-scene command."),
    PatchStep("apply_push1_new_scene_gesture.py", "Add the new-scene gesture lifecycle."),
)


REQUIRED_SOURCES = (
    "framework/daw/DAWColor.java",
    "controller/ableton/push/PushControllerSetup.java",
    "controller/ableton/push/view/SmartView.java",
    "framework/view/PadMidiNoteTracker.java",
    "bitwig/framework/hardware/HwRelativeKnobImpl.java",
    "bitwig/framework/daw/data/CursorTrackImpl.java",
    "controller/ableton/push/view/PadViewTaskGuard.java",
    "controller/ableton/push/command/trigger/PageLeftCommand.java",
    "controller/ableton/push/command/trigger/PushCursorCommand.java",
    "controller/ableton/push/command/trigger/PageRightCommand.java",
    "controller/ableton/push/command/trigger/Push1NavigationContext.java",
    "controller/ableton/push/command/trigger/Push1DeviceMoveCommand.java",
    "controller/ableton/push/mode/device/DeviceBrowserMode.java",
    "controller/ableton/push/mode/device/DeviceChainsMode.java",
    "controller/ableton/push/mode/device/DeviceLayerDetailsMode.java",
    "controller/ableton/push/controller/Push1French.java",
    "framework/daw/constants/TransportConstants.java",
    "controller/ableton/push/mode/track/MasterMode.java",
    "controller/ableton/push/mode/track/ClipMode.java",
    "controller/ableton/push/command/trigger/PlayPositionKnobCommand.java",
    "framework/command/trigger/mode/KnobTouchOwner.java",
    "framework/command/trigger/clip/NewCommand.java",
    "framework/command/trigger/clip/Push1SelectGesture.java",
    "framework/mode/NoteEditTouchOwner.java",
)


def resolve_patch_scripts(repository_root: Path) -> tuple[Path, ...]:
    """Validate the registry and resolve its ordered script paths."""
    scripts_root = repository_root / "scripts"
    names = tuple(step.script for step in PATCH_STEPS)
    if len(names) != len(set(names)):
        raise SystemExit("Patch registry contains duplicate script names")

    resolved = []
    for step in PATCH_STEPS:
        if Path(step.script).name != step.script or not step.script.endswith(".py"):
            raise SystemExit(f"Invalid patch script path in registry: {step.script}")
        path = scripts_root / step.script
        if not path.is_file():
            raise SystemExit(f"Patch script is missing: {path}")
        resolved.append(path)
    return tuple(resolved)
