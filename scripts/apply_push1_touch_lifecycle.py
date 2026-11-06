#!/usr/bin/env python3
"""Make Push 1 encoder touch bindings reversible and release stale touch state."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return source.replace(old, new, 1)


path = ROOT / "bitwig/framework/hardware/HwRelativeKnobImpl.java"
source = path.read_text(encoding="utf-8")

source = replace_once(
    source,
    """    private int                                  control;
""",
    """    private int                                  control;
    private IMidiInput                           touchInput;
    private BindType                              touchType;
    private int                                   touchChannel;
    private int                                   touchControl;
""",
    "Touch binding state fields",
)

source = replace_once(
    source,
    """        this.touchCommand = command;

        this.hardwareKnob.beginTouchAction ().addBinding (this.controllerHost.createAction ( () -> this.triggerTouch (true), () -> ""));
""",
    """        this.touchCommand = command;
        this.touchInput = input;
        this.touchType = type;
        this.touchChannel = channel;
        this.touchControl = control;

        this.hardwareKnob.beginTouchAction ().addBinding (this.controllerHost.createAction ( () -> this.triggerTouch (true), () -> ""));
""",
    "Remember touch binding for rebind",
)

source = replace_once(
    source,
    """    public void unbind ()
    {
        if (this.input != null)
            this.input.unbind (this);
    }
""",
    """    public void unbind ()
    {
        // A lost MIDI Touch-UP must not leave the encoder armed while input
        // controls are suspended (e.g. device reconnect or host rebind).
        if (this.isTouched ())
            this.triggerTouch (false);

        if (this.input != null)
            this.input.unbind (this);

        // Touch actions are separate from the relative-CC matcher. Remove both
        // explicitly; otherwise a supposedly unbound knob still reacts to touch.
        this.hardwareKnob.beginTouchAction ().setActionMatcher (null);
        this.hardwareKnob.endTouchAction ().setActionMatcher (null);
    }
""",
    "Release touch state and unbind touch matchers",
)

source = replace_once(
    source,
    """    public void rebind ()
    {
        if (this.input != null)
            this.input.bind (this, this.type, this.channel, this.control, this.encoding);
    }
""",
    """    public void rebind ()
    {
        if (this.input != null)
            this.input.bind (this, this.type, this.channel, this.control, this.encoding);

        // Restore the independent touch matchers together with the rotation
        // matcher. This keeps suspend/resume symmetrical for every encoder.
        if (this.touchCommand != null && this.touchInput != null)
            this.touchInput.bindTouch (this, this.touchType, this.touchChannel, this.touchControl);
    }
""",
    "Restore touch matchers on rebind",
)

for token in ("this.touchInput = input;", "this.triggerTouch (false);",
              "beginTouchAction ().setActionMatcher (null)",
              "endTouchAction ().setActionMatcher (null)",
              "this.touchInput.bindTouch (this, this.touchType, this.touchChannel, this.touchControl);"):
    if token not in source:
        raise SystemExit(f"Touch lifecycle postcondition missing: {token}")

path.write_text(source, encoding="utf-8")
print("Push 1 encoder touch bindings now release, unbind and rebind symmetrically.")
