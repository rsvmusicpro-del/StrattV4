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


def main() -> int:
    if not SOURCE_ROOT.is_dir():
        raise SystemExit(f"DrivenByMoss source tree is missing: {SOURCE_ROOT}")

    revision = subprocess.run(
        ["git", "-C", str(SUBMODULE), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if revision != EXPECTED_UPSTREAM:
        raise SystemExit(
            "Refusing to patch an unexpected DrivenByMoss revision: "
            f"expected {EXPECTED_UPSTREAM}, found {revision}"
        )

    # Refuse to build on a locally modified or untracked upstream Java tree.
    # The checksum sidecar repair in CI is outside this source subtree and is
    # intentionally unaffected by this guard.
    source_status = subprocess.run(
        ["git", "-C", str(SUBMODULE), "status", "--porcelain", "--", "src/main/java/de/mossgrabers"],
        check=True, capture_output=True, text=True,
    ).stdout
    if source_status.strip():
        raise SystemExit(
            "Refusing to patch a modified DrivenByMoss Java source tree; "
            "restore the pinned source before building:\\n" + source_status
        )

    parent = SOURCE_ROOT.parent
    with tempfile.TemporaryDirectory(prefix=".strattv4-push1-stage-", dir=parent) as temporary:
        staging_submodule = Path(temporary) / "vendor" / "DrivenByMoss"
        staging_root = staging_submodule / "src" / "main" / "java" / "de" / "mossgrabers"
        staging_root.parent.mkdir(parents=True)
        shutil.copytree(SOURCE_ROOT, staging_root)

        # All destructive edits happen in the temporary tree. A failed anchor,
        # missing file or postcondition leaves the checked-out source untouched.
        for step, patch_script in zip(PATCH_STEPS, PATCH_SCRIPTS):
            try:
                subprocess.run(
                    [sys.executable, "-B", str(patch_script)],
                    cwd=Path(temporary),
                    check=True,
                )
            except subprocess.CalledProcessError as error:
                raise SystemExit(
                    f"Patch step '{step.script}' failed (exit code {error.returncode}); "
                    "the staged source tree was discarded."
                ) from error

        for relative_path in REQUIRED_SOURCES:
            required_source = staging_root / relative_path
            if not required_source.is_file():
                raise SystemExit(
                    "Staged patch validation failed: "
                    f"{relative_path} is missing"
                )

        backup = Path(temporary) / "mossgrabers-original"
        os.replace(SOURCE_ROOT, backup)
        try:
            os.replace(staging_root, SOURCE_ROOT)
        except Exception:
            # Restore the exact original directory if the final rename fails.
            os.replace(backup, SOURCE_ROOT)
            raise

    print("Transactional StrattV4 Push 1 customizations completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
