#!/usr/bin/env python3
"""Apply StrattV4 patches transactionally to the pinned DrivenByMoss source tree.

All StrattV4 Push 1 patch sets run against a staged copy. The checked-out
submodule is swapped only after every patch and its postconditions succeed.
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from patch_manifest import EXPECTED_UPSTREAM, PATCH_STEPS, REQUIRED_SOURCES, resolve_patch_scripts

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SUBMODULE = REPOSITORY_ROOT / "vendor" / "DrivenByMoss"
SOURCE_ROOT = SUBMODULE / "src" / "main" / "java" / "de" / "mossgrabers"
PATCH_SCRIPTS = resolve_patch_scripts(REPOSITORY_ROOT)


def verify_upstream_revision(submodule: Path) -> str:
    """Refuse to patch anything except the exact pinned upstream revision."""
    revision = subprocess.run(
        ["git", "-C", str(submodule), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if revision != EXPECTED_UPSTREAM:
        raise SystemExit(
            "Refusing to patch an unexpected DrivenByMoss revision: "
            f"expected {EXPECTED_UPSTREAM}, found {revision}"
        )
    return revision


def ensure_clean_source_tree(submodule: Path) -> None:
    """Refuse to overwrite modified or untracked upstream Java sources."""
    source_status = subprocess.run(
        ["git", "-C", str(submodule), "status", "--porcelain", "--", "src/main/java/de/mossgrabers"],
        check=True, capture_output=True, text=True,
    ).stdout
    if source_status.strip():
        raise SystemExit(
            "Refusing to patch a modified DrivenByMoss Java source tree; "
            "restore the pinned source before building:\\n" + source_status
        )


def run_patch_steps(temporary_root: Path) -> None:
    """Execute the ordered patch registry against the temporary staged tree."""
    for step, patch_script in zip(PATCH_STEPS, PATCH_SCRIPTS):
        try:
            subprocess.run(
                [sys.executable, "-B", str(patch_script)],
                cwd=temporary_root,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            raise SystemExit(
                f"Patch step '{step.script}' failed (exit code {error.returncode}); "
                "the staged source tree was discarded."
            ) from error


def validate_staged_sources(staging_root: Path) -> None:
    """Require every generated or patched Java source before installation."""
    for relative_path in REQUIRED_SOURCES:
        required_source = staging_root / relative_path
        if not required_source.is_file():
            raise SystemExit(
                "Staged patch validation failed: "
                f"{relative_path} is missing"
            )


def install_staged_source(source_root: Path, staging_root: Path, backup: Path) -> None:
    """Atomically install the staged tree, restoring the original on failure."""
    os.replace(source_root, backup)
    try:
        os.replace(staging_root, source_root)
    except Exception:
        # Restore the exact original directory if the final rename fails.
        os.replace(backup, source_root)
        raise


def main() -> int:
    if not SOURCE_ROOT.is_dir():
        raise SystemExit(f"DrivenByMoss source tree is missing: {SOURCE_ROOT}")

    verify_upstream_revision(SUBMODULE)
    ensure_clean_source_tree(SUBMODULE)

    parent = SOURCE_ROOT.parent
    with tempfile.TemporaryDirectory(prefix=".strattv4-push1-stage-", dir=parent) as temporary:
        temporary_root = Path(temporary)
        staging_submodule = temporary_root / "vendor" / "DrivenByMoss"
        staging_root = staging_submodule / "src" / "main" / "java" / "de" / "mossgrabers"
        staging_root.parent.mkdir(parents=True)
        shutil.copytree(SOURCE_ROOT, staging_root)

        # All destructive edits happen in the temporary tree. A failed anchor,
        # missing file or postcondition leaves the checked-out source untouched.
        run_patch_steps(temporary_root)
        validate_staged_sources(staging_root)

        backup = temporary_root / "mossgrabers-original"
        install_staged_source(SOURCE_ROOT, staging_root, backup)

    print("Transactional StrattV4 Push 1 customizations completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
