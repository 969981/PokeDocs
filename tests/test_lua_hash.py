import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lua_hash import OFFSET_BASIS, derived_names, lua_hash, known_symbols


class TestLuaHash(unittest.TestCase):
    def test_reference_vectors(self):
        samples = {
            "SetCursorPos": 0x0170EA75A6880AF5,
            "GetMenu": 0x00D5938E012F68A8,
            "onComplete": 0x0085F7055F019927,
            "getListSize": 0x01D67550130FC696,
            "main.event.ik.CoroutineExecutor": 0x051A4F1726DB4DE1,
        }
        for name, expected in samples.items():
            with self.subTest(name=name):
                self.assertEqual(lua_hash(name), expected)

    def test_basis_and_case(self):
        self.assertEqual(lua_hash(""), OFFSET_BASIS)
        self.assertNotEqual(lua_hash("OnComplete"), lua_hash("onComplete"))

    def test_numeric(self):
        self.assertIn(("POKE_DERUBIRU05", "numeric"),
                      list(derived_names("POKE_DERUBIRU04", 1)))

    def test_known_name_validation(self):
        _, issues = known_symbols([(Path("sample"), 1, 0x0170EA75A6880AF5, "SetCursorPos")])
        self.assertEqual(issues, [])
        _, bad = known_symbols([(Path("sample"), 1, 0, "SetCursorPos")])
        self.assertEqual(len(bad), 1)


if __name__ == "__main__":
    unittest.main()
