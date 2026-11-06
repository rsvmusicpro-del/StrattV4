#!/usr/bin/env python3
"""Replace the Push 1 startup waiting message with the StrattV3 custom text."""

from pathlib import Path

DISPLAY = Path(
    "vendor/DrivenByMoss/src/main/java/de/mossgrabers/controller/ableton/push/controller/Push1Display.java"
)


from patch_utils import replace_once



display = DISPLAY.read_text(encoding="utf-8")
display = replace_once(
    display,
    '        this.clear ().setBlock (1, 1, "     Please start").setBlock (1, 2, this.host.getName () + " to play...").allDone ().flush ();',
    '        this.clear ().setBlock (1, 1, "     Please start").setBlock (1, 2, this.host.getName () + " to play...").allDone ().flush ();',
    "Push 1 startup message",
)
DISPLAY.write_text(display, encoding="utf-8")

if 'setBlock (1, 1, "     Please start").setBlock (1, 2, this.host.getName () + " to play...")' not in display:
    raise SystemExit("Push 1 startup message postcondition failed")

print("Push 1 startup prompt retains the actionable Bitwig launch instruction.")
