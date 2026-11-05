import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lua_hash import lua_hash
from scan_lua_evidence import audit, scan_text


class TestLuaEvidence(unittest.TestCase):
    def setup_repo(self, root: Path):
        folder = root / "SV" / "Hashlists" / "Lua"
        folder.mkdir(parents=True)
        for kind in ("c", "e", "f", "s"):
            (folder / f"lua_{kind}_hashes.txt").write_text(
                (f"0x{lua_hash('main.ui.hud_info.HudInfoPlayer'):016X} \n"
                 if kind == "c" else f"0x{lua_hash('ExampleMethod'):016X} \n"
                 if kind == "f" else f"0x{lua_hash('FlagValue'):016X} \n"
                 if kind == "s" else "0xA124459F7716D653 \n"),
                encoding="utf-8")
        return folder

    def test_header_source_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_repo(root)
            path = root / "lua_names.h"
            path.write_text(
                '{"CFD9B049511E682DA", "main.ui.hud_info.HudInfoPlayer"},\n',
                encoding="utf-8")
            report = audit(root, "SV", [path], [], "SV 3.0.1 legacy")
            matches = report["new_exact_matches"]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["kind"], "c")
            self.assertEqual(matches[0]["name"], "main.ui.hud_info.HudInfoPlayer")
            self.assertEqual(report["ambiguous"], [])

    def test_function_comment_and_raw_bytecode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_repo(root)
            src = root / "C123.lua"
            src.write_text(
                f"--- main.ui.hud_info.HudInfoPlayer.ExampleMethod\n"
                f"function CFD9B049511E682DA_prototype:F{lua_hash('ExampleMethod'):016X}(self)\n"
                f'  local x = "FlagValue"\n'
                f"end\n", encoding="utf-8")
            binary = root / "main.blua"
            binary.write_bytes(f"\x1bLua\x54\u0000 CFD9B049511E682DA F{lua_hash('ExampleMethod'):016X}".encode("utf-8"))
            report = audit(root, "SV", [src], [binary], "SV 4.0.0 raw")
            matches = {(r["kind"], r["name"]) for r in report["new_exact_matches"]}
            self.assertIn(("c", "main.ui.hud_info.HudInfoPlayer"), matches)
            self.assertIn(("f", "ExampleMethod"), matches)
            self.assertIn(("s", "FlagValue"), matches)
            self.assertEqual(len(report["binary_presence"][str(binary)]["unknown_tokens"]), 2)

    def test_bad_annotated_name_does_not_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_repo(root)
            src = root / "bad.lua"
            src.write_text(
                f"--- main.wrong.Class.ExampleMethod\n"
                f"function CFD9B049511E682DA_prototype:F{lua_hash('ExampleMethod'):016X}(self)\n",
                encoding="utf-8")
            result = audit(root, "SV", [src], [], "SV 3.0.1")
            self.assertFalse(any(x["kind"] == "c" for x in result["new_exact_matches"]))


if __name__ == "__main__":
    unittest.main()
