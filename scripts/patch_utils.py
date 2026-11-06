"""Shared, fail-closed primitives for StrattV4 source patch scripts."""

from __future__ import annotations


def replace_once(source: str, old: str, new: str, label: str) -> str:
    """Replace one exact source anchor or stop the build on source drift."""
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one source anchor, found {count}"
        )
    return source.replace(old, new, 1)
