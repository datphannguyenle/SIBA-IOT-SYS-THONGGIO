"""Kiểm tra logic tổng hợp soak VENT-012; không kết nối runtime."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deploy/thingsboard"))
import vent012_soak as soak  # noqa: E402


class Vent012SoakTest(unittest.TestCase):
    def test_pass_requires_enough_clean_samples(self):
        clean = {"ok": True, "devices": {"ND2-1": {"ok": True, "sourceAgeSec": 2,
                                                       "invalidKeyCount": 0}}}
        self.assertTrue(soak.summarize([clean, clean], 2)["pass"])
        self.assertFalse(soak.summarize([clean], 2)["pass"])

    def test_any_failure_or_invalid_key_fails(self):
        failed = {"ok": False, "devices": {"ND2-1": {"ok": True, "sourceAgeSec": 2,
                                                         "invalidKeyCount": 0}}}
        invalid = {"ok": True, "devices": {"ND2-1": {"ok": True, "sourceAgeSec": 2,
                                                         "invalidKeyCount": 1}}}
        self.assertFalse(soak.summarize([failed], 1)["pass"])
        self.assertFalse(soak.summarize([invalid], 1)["pass"])


if __name__ == "__main__":
    unittest.main()
