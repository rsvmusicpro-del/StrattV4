"""Shared, fail-closed primitives for StrattV4 source patch scripts."""

from __future__ import annotations


def replace_once(source: str, old: str, new: str, label: str) -> str:
    """Replace one exact, non-empty source anchor or stop on source drift.

    Empty anchors and no-op replacements are rejected explicitly: both usually
    indicate a malformed patch definition rather than a useful source change.
    The input string is immutable, so failures cannot partially modify a file.
    """
    if not isinstance(source, str):
        raise SystemExit(f"{label}: source must be text")
    if not isinstance(old, str) or not old:
        raise SystemExit(f"{label}: source anchor must be a non-empty string")
    if not isinstance(new, str):
        raise SystemExit(f"{label}: replacement must be text")
    if not isinstance(label, str) or not label.strip():
        raise SystemExit("patch label must be a non-empty string")
    if old == new:
        raise SystemExit(f"{label}: refusing a no-op source replacement")

    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one source anchor, found {count}"
        )
    return source.replace(old, new, 1)
