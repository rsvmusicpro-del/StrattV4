#!/usr/bin/env python3
"""Add a Push 1 modifier for creating a scene from currently playing clips."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


from patch_utils import replace_once



command_path = ROOT / "framework/command/trigger/clip/NewCommand.java"
command = command_path.read_text(encoding="utf-8")

old = """    public void executeNormal (final ButtonEvent event)
    {
        if (event == ButtonEvent.UP)
            this.handleExecute (true);
    }
"""
new = """    public void executeNormal (final ButtonEvent event)
    {
        if (event != ButtonEvent.UP)
            return;

        // SELECT + NEW creates a scene from all clips currently playing in
        // the launcher. Plain NEW and SHIFT + NEW retain their original logic.
        if (this.surface.isSelectPressed ())
        {
            this.model.getProject ().createSceneFromPlayingLauncherClips ();
            return;
        }

        this.handleExecute (true);
    }
"""
command = replace_once(command, old, new, "Push 1 SELECT + NEW scene-copy mapping")

if "createSceneFromPlayingLauncherClips ()" not in command:
    raise SystemExit("Scene-copy action is missing")
if command.count("this.handleExecute (true);") != 2 or command.count("this.handleExecute (false);") != 1:
    raise SystemExit("Plain NEW or SHIFT + NEW behavior was unexpectedly changed")

command_path.write_text(command, encoding="utf-8")
print("SELECT + NEW scene-copy mapping applied; NEW and SHIFT + NEW preserved.")
