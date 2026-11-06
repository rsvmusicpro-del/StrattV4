#!/usr/bin/env python3
"""Synchronize the Push VU-meter runtime flag with its persisted setting at startup.

The upstream setting defaults to On, but the in-memory flag starts false and the
observer is only guaranteed to run after a setting change. Read the current value
once after observer registration so startup state matches the user's preference.
"""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
CONFIG = ROOT / "framework/configuration/AbstractConfiguration.java"

OLD = """        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });

        this.isSettingActive.add (ENABLE_VU_METERS);
"""
NEW = """        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });

        // The observer handles subsequent changes; initialize the runtime state
        // from the persisted/default value as well, without emitting a fake change.
        this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());

        this.isSettingActive.add (ENABLE_VU_METERS);
"""


def main() -> None:
    source = CONFIG.read_text(encoding="utf-8")
    if source.count(NEW) == 1:
        print("Push VU startup state already synchronized.")
        return
    if source.count(OLD) != 1:
        raise SystemExit(
            "VU startup synchronization: expected exactly one original setting block; "
            f"found {source.count(OLD)}"
        )
    CONFIG.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
    updated = CONFIG.read_text(encoding="utf-8")
    if updated.count('this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());') != 1:
        raise SystemExit("VU startup synchronization postcondition failed")
    print("Push VU runtime state now matches the persisted setting at startup.")


if __name__ == "__main__":
    main()
