#!/usr/bin/env python3
"""Fix Push 1 Clip-mode Accent encoder scaling in pinned DrivenByMoss."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


# Bitwig stores Accent normalized to [0.0, 1.0], but the display maps that
# interval to [-100%, +100%] (200 displayed percentage points).
# Therefore one displayed percentage point equals 0.005 normalized units.
constants_path = ROOT / "framework/daw/constants/TransportConstants.java"
constants = constants_path.read_text(encoding="utf-8")
constants = replace_once(
    constants,
    "    public static final double INC_FRACTION_ACCENT      = 1.0;",
    "    public static final double INC_FRACTION_ACCENT      = 0.005;",
    "Clip accent normal increment",
)
constants = replace_once(
    constants,
    "    public static final double INC_FRACTION_ACCENT_SLOW = 1.0 / 16;",
    "    public static final double INC_FRACTION_ACCENT_SLOW = 0.005 / 16;",
    "Clip accent fine increment",
)
constants_path.write_text(constants, encoding="utf-8")

# Bitwig exposes the clip's Play Stop time as the playback end. On Push 1,
# the Play End encoder must move that endpoint in the opposite numeric
# direction to the other clip-time controls: clockwise increases the end.
# Keep this inversion local to Play End; do not alter the shared value changer.
cursor_clip_path = ROOT / "bitwig/framework/daw/CursorClipImpl.java"
cursor_clip = cursor_clip_path.read_text(encoding="utf-8")
cursor_clip = replace_once(
    cursor_clip,
    """    public void changePlayEnd (final int control, final boolean slow)
    {
        final boolean increase = this.valueChanger.isIncrease (control);
        final double frac = slow ? TransportConstants.INC_FRACTION_TIME_SLOW : TransportConstants.INC_FRACTION_TIME;
        this.getClip ().getPlayStop ().inc (increase ? frac : -frac);
    }""",
    """    public void changePlayEnd (final int control, final boolean slow)
    {
        final boolean increase = this.valueChanger.isIncrease (control);
        final double frac = slow ? TransportConstants.INC_FRACTION_TIME_SLOW : TransportConstants.INC_FRACTION_TIME;
        this.getClip ().getPlayStop ().inc (increase ? -frac : frac);
    }""",
    "Push 1 Play End direction",
)
cursor_clip_path.write_text(cursor_clip, encoding="utf-8")

# ClipMode throttles all encoder events to one in eight. Keep that behavior
# for the time controls, but process every Accent detent so its increment is
# consistent and responsive.
clip_mode_path = ROOT / "controller/ableton/push/mode/track/ClipMode.java"
clip_mode = clip_mode_path.read_text(encoding="utf-8")
clip_mode = replace_once(
    clip_mode,
    """        if (!this.increaseKnobMovement ())
            return;

        final IClip clip = this.model.getCursorClip ();
""",
    """        if (index != 7 && !this.increaseKnobMovement ())
            return;

        final IClip clip = this.model.getCursorClip ();
""",
    "Clip Accent encoder must not be throttled",
)
clip_mode_path.write_text(clip_mode, encoding="utf-8")
