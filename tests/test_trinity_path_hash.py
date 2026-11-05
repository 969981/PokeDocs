import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lua_hash import lua_hash
from trinity_path_hash import ROW


class TestTrinityPaths(unittest.TestCase):
    def test_za_reference_vectors(self):
        examples = {
            "avalon/data/personal_array.bin": 0x68AB38E2CF1281ED,
            "avalon/data/growTable.bin": 0x6E640887C479E026,
            "avalon/data/waza_array.bin": 0xA90026235522C2F0,
            "avalon/data/tokusei_array.bin": 0xACD40B49C2F91CCD,
            "ai_influence/ba_battle_area_0003_01_00_00.imap": 0x05AFD1BF8BA6BBF9,
        }
        for path, expected in examples.items():
            with self.subTest(path=path):
                self.assertEqual(lua_hash(path), expected)

    def test_path_row(self):
        row = "0x68AB38E2CF1281ED avalon/data/personal_array.bin"
        self.assertEqual(ROW.fullmatch(row).group(2), "avalon/data/personal_array.bin")


if __name__ == "__main__":
    unittest.main()
