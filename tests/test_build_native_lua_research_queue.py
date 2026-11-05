"""Pinned SV native/Haxe ZA investigation-queue reproducibility."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_native_lua_research_queue import build, ROOT, HASHLINE

class TestNativeLuaResearchQueue(unittest.TestCase):
    def test_pinned_tables_match_committed_reports(self):
        files, summary = build(ROOT)
        for path, content in files.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content, str(path))
        self.assertEqual(summary["SV"]["current_unknown_C"], 1334)
        self.assertEqual(summary["SV"]["direct_C_to_F"], 1047)
        self.assertEqual(summary["ZA"]["current_unknown_S"], 114)
        self.assertEqual(summary["ZA"]["current_unknown_F"], 41)

    def test_unsupported_hashline(self):
        self.assertIsNone(HASHLINE.fullmatch("0x0123 not-a-64bit-hash"))

if __name__ == "__main__":
    unittest.main()
