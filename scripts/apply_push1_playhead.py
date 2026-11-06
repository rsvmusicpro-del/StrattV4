#!/usr/bin/env python3
"""Correct the Push 1 play-position knob touch indication."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


command_path = ROOT / "controller/ableton/push/command/trigger/PlayPositionKnobCommand.java"
command = command_path.read_text(encoding="utf-8")

# The Play Position encoder must not mark the unrelated Tempo parameter as
# touched. Keep the display update on touch; encoder movement is unchanged.
command = replace_once(
    command,
    "        this.transport.setTempoIndication (activate);\n"
    "        if (activate)\n"
    "            this.displayPosition ();\n",
    "        if (activate)\n"
    "            this.displayPosition ();\n",
    "Play Position touch must not indicate Tempo",
)

if "setTempoIndication" in command:
    raise SystemExit("PlayPositionKnobCommand still indicates the Tempo parameter")
if "this.displayPosition ();" not in command:
    raise SystemExit("Play Position display update was unexpectedly removed")

command_path.write_text(command, encoding="utf-8")
print("Push 1 Play Position touch indication corrected; transport movement unchanged.")
