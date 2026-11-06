#!/usr/bin/env python3
"""Gate command-bound Push 1 rotations without replacing native parameter bindings; initialize VU display."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")


from patch_utils import replace_once



# Push 1 rotary controls expose separate command and native-parameter paths.
# Gate command-bound rotations here, but deliberately leave ParameterImpl bound
# directly to param.getParameter(): routing it through changeValue() changes the
# native relative-resolution/sensitivity semantics and is not an acceptable
# reliability fix without hardware equivalence tests.
knob_path = ROOT / "bitwig/framework/hardware/HwRelativeKnobImpl.java"
knob = knob_path.read_text(encoding="utf-8")

knob = replace_once(
    knob,
    """    public void handleValue (final double value)
    {
        if (this.command == null)
            return;
""",
    """    public void handleValue (final double value)
    {
        // A Push rotary encoder with a touch binding must be physically touched.
        // This gate covers all command-bound encoders, not only Tempo/Playhead.
        if (this.command == null || this.touchCommand != null && !this.isTouched ())
            return;
""",
    "Touch gate for command-bound rotations",
)

if knob.count("this.touchCommand != null && !this.isTouched ()") != 1:
    raise SystemExit("Command-bound relative encoder path must have exactly one touch guard")
if "target = param.getParameter ();" not in knob:
    raise SystemExit("Native Bitwig ParameterImpl binding was unexpectedly changed")
if "target = this.touchCommand == null ? param.getParameter () : this.defaultSimpleParameterAction;" in knob:
    raise SystemExit("Unsafe custom callback substitution for native parameter binding detected")
knob_path.write_text(knob, encoding="utf-8")


# The VU observer's setting has an On default, but the in-memory field starts
# false. Initialize it from the persisted setting immediately after observer
# registration, rather than waiting for the user to change the setting.
config_path = ROOT / "framework/configuration/AbstractConfiguration.java"
config = config_path.read_text(encoding="utf-8")
config = replace_once(
    config,
    """        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });

        this.isSettingActive.add (ENABLE_VU_METERS);
""",
    """        this.enableVUMetersSetting.addValueObserver (value -> {
            this.enableVUMeters = "On".equals (value);
            this.notifyObservers (ENABLE_VU_METERS);
        });
        // Reflect the stored/default setting immediately; otherwise the
        // initial false field can suppress the live VU bars until toggled.
        this.enableVUMeters = "On".equals (this.enableVUMetersSetting.get ());

        this.isSettingActive.add (ENABLE_VU_METERS);
""",
    "Initialize VU meters from persisted setting",
)
config_path.write_text(config, encoding="utf-8")

print("Push 1 command-bound rotations are touch-gated; native parameter bindings are preserved; live VU meters initialize from their setting.")
