"""Unit tests for the shared StrattV4 patching primitives."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from patch_utils import replace_once


class ReplaceOnceTests(unittest.TestCase):
    def test_replaces_exactly_one_anchor(self):
        self.assertEqual(replace_once("alpha beta", "beta", "gamma", "sample"), "alpha gamma")

    def test_rejects_missing_anchor(self):
        with self.assertRaisesRegex(SystemExit, "sample: expected exactly one source anchor, found 0"):
            replace_once("alpha", "beta", "gamma", "sample")

    def test_rejects_ambiguous_anchor(self):
        with self.assertRaisesRegex(SystemExit, "sample: expected exactly one source anchor, found 2"):
            replace_once("alpha alpha", "alpha", "beta", "sample")

    def test_rejects_empty_anchor(self):
        with self.assertRaisesRegex(SystemExit, "sample: source anchor must be a non-empty string"):
            replace_once("alpha", "", "beta", "sample")

    def test_rejects_no_op_replacement(self):
        with self.assertRaisesRegex(SystemExit, "sample: refusing a no-op source replacement"):
            replace_once("alpha", "alpha", "alpha", "sample")

    def test_rejects_empty_label(self):
        with self.assertRaisesRegex(SystemExit, "patch label must be a non-empty string"):
            replace_once("alpha", "alpha", "beta", " ")

    def test_does_not_mutate_input_on_failure(self):
        source = "alpha alpha"
        with self.assertRaises(SystemExit):
            replace_once(source, "alpha", "beta", "sample")
        self.assertEqual(source, "alpha alpha")


if __name__ == "__main__":
    unittest.main()
