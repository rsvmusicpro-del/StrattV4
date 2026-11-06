#!/usr/bin/env python3
"""Keep Push 1 Note Mode note-edit sessions bound to the original clip."""

from pathlib import Path

ROOT = Path("vendor/DrivenByMoss/src/main/java/de/mossgrabers")
MODE = ROOT / "controller/ableton/push/mode/NoteMode.java"
OWNER = ROOT / "framework/mode/NoteEditTouchOwner.java"

OWNER_SOURCE = """package de.mossgrabers.framework.mode;

import java.util.Arrays;


/**
 * Keeps a note-edit transaction attached to the clip which received the first
 * encoder touch. Multiple simultaneous knob touches share one edit session.
 */
public final class NoteEditTouchOwner<T>
{
    private static final int KNOB_COUNT = 8;

    private final boolean [] activeTouches = new boolean [KNOB_COUNT];
    private T owner;
    private int activeTouchCount;


    /**
     * Begin or join a touch gesture.
     *
     * @param index The physical knob index
     * @param candidate The clip active at touch-down
     * @return True only when the caller must start the edit transaction
     */
    public boolean begin (final int index, final T candidate)
    {
        if (index < 0 || index >= KNOB_COUNT || candidate == null || this.activeTouches[index])
            return false;
        if (this.owner != null && this.owner != candidate)
            return false;

        if (this.owner == null)
            this.owner = candidate;
        this.activeTouches[index] = true;
        ++this.activeTouchCount;
        return this.activeTouchCount == 1;
    }


    /**
     * End one physical knob touch.
     *
     * @param index The physical knob index
     * @return The original owner when the final touch ends, otherwise null
     */
    public T end (final int index)
    {
        if (index < 0 || index >= KNOB_COUNT || !this.activeTouches[index])
            return null;

        this.activeTouches[index] = false;
        --this.activeTouchCount;
        if (this.activeTouchCount != 0)
            return null;

        final T previous = this.owner;
        this.owner = null;
        return previous;
    }


    /**
     * Cancel all active touches and return the original edit owner.
     *
     * @return The owner, or null if no edit transaction is active
     */
    public T clear ()
    {
        final T previous = this.owner;
        this.owner = null;
        this.activeTouchCount = 0;
        Arrays.fill (this.activeTouches, false);
        return previous;
    }
}
"""


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one insertion point, found {count}")
    return source.replace(old, new, 1)


OWNER.parent.mkdir(parents=True, exist_ok=True)
if OWNER.exists():
    if OWNER.read_text(encoding="utf-8") != OWNER_SOURCE:
        raise SystemExit("Refusing to overwrite unexpected NoteEditTouchOwner.java")
else:
    OWNER.write_text(OWNER_SOURCE, encoding="utf-8")

source = MODE.read_text(encoding="utf-8")
source = replace_once(
    source,
    "import de.mossgrabers.framework.mode.NoteEditor;\n",
    "import de.mossgrabers.framework.mode.NoteEditor;\n"
    "import de.mossgrabers.framework.mode.NoteEditTouchOwner;\n",
    "NoteMode touch owner import",
)
source = replace_once(
    source,
    "    private final NoteEditor                    noteEditor         = new NoteEditor ();\n",
    "    private final NoteEditor                    noteEditor         = new NoteEditor ();\n"
    "    private final NoteEditTouchOwner<INoteClip> editTouchOwner    = new NoteEditTouchOwner<> ();\n"
    "    private final boolean []                   deleteTouches     = new boolean [8];\n",
    "NoteMode touch owner state",
)
old = """    /** {@inheritDoc} */
    @Override
    public void onKnobTouch (final int index, final boolean isTouched)
    {
        final List<NotePosition> notes = this.noteEditor.getNotes ();
        if (notes.isEmpty ())
            return;

        if (isTouched && this.surface.isDeletePressed ())
        {
            this.surface.setTriggerConsumed (ButtonID.DELETE);
            this.defaultParameterProvider.get (index).resetValue ();
            return;
        }

        final INoteClip clip = this.noteEditor.getClip ();
        if (isTouched)
            clip.startEdit (notes);
        else
            clip.stopEdit ();
    }
"""
new = """    /** {@inheritDoc} */
    @Override
    public void onKnobTouch (final int index, final boolean isTouched)
    {
        if (index < 0 || index >= 8)
            return;

        if (isTouched)
        {
            if (this.deleteTouches[index])
                return;

            if (this.surface.isDeletePressed ())
            {
                this.deleteTouches[index] = true;
                this.surface.setTriggerConsumed (ButtonID.DELETE);
                this.defaultParameterProvider.get (index).resetValue ();
                return;
            }

            final List<NotePosition> notes = this.noteEditor.getNotes ();
            if (!notes.isEmpty () && this.editTouchOwner.begin (index, this.noteEditor.getClip ()))
                this.noteEditor.getClip ().startEdit (notes);
            return;
        }

        if (this.deleteTouches[index])
        {
            this.deleteTouches[index] = false;
            return;
        }

        final INoteClip editOwner = this.editTouchOwner.end (index);
        if (editOwner != null)
            editOwner.stopEdit ();
    }


    /** {@inheritDoc} */
    @Override
    public void onDeactivate ()
    {
        final INoteClip editOwner = this.editTouchOwner.clear ();
        if (editOwner != null)
            editOwner.stopEdit ();

        for (int i = 0; i < this.deleteTouches.length; i++)
            this.deleteTouches[i] = false;

        super.onDeactivate ();
    }
"""
source = replace_once(source, old, new, "NoteMode note-edit touch lifecycle")
for token in (
    "this.editTouchOwner.begin (index, this.noteEditor.getClip ())",
    "this.editTouchOwner.end (index)",
    "this.editTouchOwner.clear ()",
    "editOwner.stopEdit ();",
    "this.deleteTouches[index] = true;",
):
    if token not in source:
        raise SystemExit(f"NoteMode touch lifecycle postcondition missing: {token}")
MODE.write_text(source, encoding="utf-8")
print("Note Mode edit transactions now retain their original clip across multi-touch and context changes.")
