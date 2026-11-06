#!/usr/bin/env python3
"""Restore the Push 1 master-volume position marker without changing other views."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
MASTER = ROOT / "controller/ableton/push/mode/track/MasterMode.java"

OLD = """        display.setCell (2, 0, this.surface.getConfiguration ().isEnableVUMeters () ? master.getVu () : master.getVolume (), Format.FORMAT_VALUE);
"""
NEW = """        // Keep the master volume position visible over the live VU bar,
        // matching the established Push 1 Volume/Track view convention.
        // When VU meters are disabled, render the volume value as a full bar.
        final int upperBound = this.model.getValueChanger ().getUpperBound ();
        display.setCell (2, 0, this.surface.getConfiguration ().isEnableVUMeters () ? Push1Display.formatValue (master.getVolume (), master.getVu (), upperBound) : Push1Display.formatValue (master.getVolume (), upperBound));
"""

IMPORT = "import de.mossgrabers.controller.ableton.push.controller.Push1Display;\n"

def main() -> None:
    source = MASTER.read_text(encoding="utf-8")
    if source.count(NEW) == 1:
        print("Push 1 master volume marker already restored.")
        return
    if source.count(OLD) != 1:
        raise SystemExit(
            "Master display restoration: expected exactly one original volume row; "
            f"found {source.count(OLD)}"
        )
    if source.count(IMPORT) != 0:
        raise SystemExit("Master display restoration: unexpected Push1Display import already exists")
    package = "package de.mossgrabers.controller.ableton.push.mode.track;\n\n"
    if source.count(package) != 1:
        raise SystemExit("Master display restoration: package declaration anchor is ambiguous")
    source = source.replace(package, package + IMPORT, 1)
    source = source.replace(OLD, NEW, 1)
    MASTER.write_text(source, encoding="utf-8")
    verified = MASTER.read_text(encoding="utf-8")
    if verified.count("Push1Display.formatValue (master.getVolume (), master.getVu (), upperBound)") != 1:
        raise SystemExit("Master display restoration postcondition failed")
    if verified.count("Push1Display.formatValue (master.getVolume (), upperBound)") != 1:
        raise SystemExit("Master display no-VU postcondition failed")
    print("Push 1 master volume position marker restored; other master controls remain unchanged.")

if __name__ == "__main__":
    main()
