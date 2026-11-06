#!/usr/bin/env python3
"""Preserve the mode that received an encoder touch until the matching release."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
COMMAND = ROOT / "framework/command/trigger/mode/KnobRowTouchModeCommand.java"
OWNER = ROOT / "framework/command/trigger/mode/KnobTouchOwner.java"

OWNER_SOURCE = """package de.mossgrabers.framework.command.trigger.mode;

/**
 * Remembers which mode owns a physical knob-touch gesture until its release.
 *
 * @param <T> The owner type
 */
public final class KnobTouchOwner<T>
{
    private T owner;

    /**
     * Begin a touch if no owner is currently active.
     *
     * @param candidate The mode active at touch-down
     * @return True if the candidate became the owner
     */
    public boolean begin (final T candidate)
    {
        if (candidate == null || this.owner != null)
            return false;
        this.owner = candidate;
        return true;
    }


    /**
     * End the current touch and return its original owner.
     *
     * @return The owner, or null if no touch was active
     */
    public T end ()
    {
        final T previous = this.owner;
        this.owner = null;
        return previous;
    }
}
"""

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


def main() -> None:
    if OWNER.exists():
        if OWNER.read_text(encoding="utf-8") != OWNER_SOURCE:
            raise SystemExit("KnobTouchOwner: refusing to overwrite an unexpected source file")
    else:
        OWNER.write_text(OWNER_SOURCE, encoding="utf-8")

    source = COMMAND.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "    private final int index;\n",
        "    private final int index;\n"
        "    private final KnobTouchOwner<IMode> touchOwner = new KnobTouchOwner<> ();\n",
        "encoder touch owner state",
    )
    source = replace_once(
        source,
        """        final IMode m = this.surface.getModeManager ().getActive ();
        if (m != null && event != ButtonEvent.LONG)
            m.onKnobTouch (this.index, event == ButtonEvent.DOWN);
""",
        """        if (event == ButtonEvent.LONG)
            return;

        if (event == ButtonEvent.DOWN)
        {
            final IMode activeMode = this.surface.getModeManager ().getActive ();
            if (this.touchOwner.begin (activeMode))
                activeMode.onKnobTouch (this.index, true);
            return;
        }

        if (event == ButtonEvent.UP)
        {
            final IMode touchOwner = this.touchOwner.end ();
            if (touchOwner != null)
                touchOwner.onKnobTouch (this.index, false);
        }
""",
        "encoder touch owner routing",
    )
    if "this.touchOwner.begin (activeMode)" not in source or "this.touchOwner.end ()" not in source:
        raise SystemExit("Encoder touch owner postcondition failed")
    COMMAND.write_text(source, encoding="utf-8")
    print("Push 1 encoder touch releases now return to the mode that received touch-down.")


if __name__ == "__main__":
    main()
