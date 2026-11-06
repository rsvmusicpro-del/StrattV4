"""Behavioral tests for the transactional patch orchestration helpers."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apply_push1_palette_transactional as pipeline
from patch_manifest import REQUIRED_SOURCES


class TransactionalPatchPipelineTests(unittest.TestCase):
    def test_staged_source_validation_accepts_complete_output_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in REQUIRED_SOURCES:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("// generated test source\n", encoding="utf-8")
            pipeline.validate_staged_sources(root)

    def test_staged_source_validation_fails_closed_on_missing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(SystemExit, "Staged patch validation failed"):
                pipeline.validate_staged_sources(Path(temporary))

    def test_install_staged_source_replaces_original_on_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            staging = root / "staging"
            backup = root / "backup"
            source.mkdir()
            staging.mkdir()
            (source / "marker.txt").write_text("original", encoding="utf-8")
            (staging / "marker.txt").write_text("staged", encoding="utf-8")

            pipeline.install_staged_source(source, staging, backup)

            self.assertEqual((source / "marker.txt").read_text(encoding="utf-8"), "staged")
            self.assertEqual((backup / "marker.txt").read_text(encoding="utf-8"), "original")

    def test_install_staged_source_restores_original_if_final_swap_fails(self):
        real_replace = pipeline.os.replace
        calls = 0

        def fail_second_replace(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected staged install failure")
            return real_replace(source, destination)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            staging = root / "staging"
            backup = root / "backup"
            source.mkdir()
            staging.mkdir()
            (source / "marker.txt").write_text("original", encoding="utf-8")
            (staging / "marker.txt").write_text("staged", encoding="utf-8")

            with patch.object(pipeline.os, "replace", side_effect=fail_second_replace):
                with self.assertRaisesRegex(OSError, "injected staged install failure"):
                    pipeline.install_staged_source(source, staging, backup)

            self.assertEqual(calls, 3)
            self.assertEqual((source / "marker.txt").read_text(encoding="utf-8"), "original")
            self.assertTrue(staging.is_dir())
            self.assertFalse(backup.exists())

    def test_patch_runner_executes_registry_in_declared_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(pipeline.subprocess, "run") as run:
                pipeline.run_patch_steps(Path(temporary))

        self.assertEqual(run.call_count, len(pipeline.PATCH_STEPS))
        for call, step, script in zip(run.call_args_list, pipeline.PATCH_STEPS, pipeline.PATCH_SCRIPTS):
            self.assertEqual(call.args[0][-1], str(script))
            self.assertEqual(call.kwargs["cwd"], Path(temporary))
            self.assertEqual(step.script, script.name)

    def test_patch_runner_stops_at_first_failed_step_with_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(
                pipeline.subprocess,
                "run",
                side_effect=[None, pipeline.subprocess.CalledProcessError(7, ["python", "bad.py"])],
            ) as run:
                with self.assertRaisesRegex(
                    SystemExit,
                    "apply_push1_master_display.py.*exit code 7",
                ):
                    pipeline.run_patch_steps(Path(temporary))

        self.assertEqual(run.call_count, 2)

    def test_upstream_revision_guard_accepts_only_the_pinned_sha(self):
        result = type("Completed", (), {"stdout": pipeline.EXPECTED_UPSTREAM + "\n"})()
        with patch.object(pipeline.subprocess, "run", return_value=result):
            self.assertEqual(
                pipeline.verify_upstream_revision(Path("vendor/DrivenByMoss")),
                pipeline.EXPECTED_UPSTREAM,
            )

    def test_upstream_revision_guard_rejects_source_drift(self):
        result = type("Completed", (), {"stdout": "unexpected-revision\n"})()
        with patch.object(pipeline.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(SystemExit, "unexpected DrivenByMoss revision"):
                pipeline.verify_upstream_revision(Path("vendor/DrivenByMoss"))

    def test_dirty_upstream_source_tree_is_rejected(self):
        result = type("Completed", (), {"stdout": " M src/main/java/de/mossgrabers/Track.java\n"})()
        with patch.object(pipeline.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(SystemExit, "modified DrivenByMoss Java source tree"):
                pipeline.ensure_clean_source_tree(Path("vendor/DrivenByMoss"))


if __name__ == "__main__":
    unittest.main()
