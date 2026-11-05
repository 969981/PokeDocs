"""Synthetic checks for SV 4.0.0 shared C factory, no game assets needed."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/trace_sv_factory_metatable.py"
SPEC = importlib.util.spec_from_file_location("sv_factory_test", SCRIPT)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def opcode(op, a=0, b=0, c=0, k=0, bx=0, ax=0):
    return (op, a, b, c, k, bx, ax)


class FactoryMetatableTest(unittest.TestCase):
    def setUp(self):
        self.root = [opcode("MOVE") for _ in range(55)]
        self.constants = [None] * 8
        self.constants[3] = b"__newindex"
        self.constants[4] = b"_hx_tostring"
        self.constants[5] = b"__tostring"
        self.root[43] = opcode("NEWTABLE", 13)
        self.root[45] = opcode("SETFIELD", 13, 3, 12)
        self.root[46] = opcode("GETTABUP", 14, 0, 4)
        self.root[47] = opcode("SETFIELD", 13, 5, 14)
        self.root[49] = opcode("CLOSURE", 15, bx=18)
        self.children = list(range(1, 23))
        self.factory = {
            "id": 19, "parent": 0,
            "upvalues": [(0, 0, 0), (1, 13, 0)],
            "constants": [b"setmetatable", b"__fields__"],
        }
        self.child = [
            opcode("GETTABUP", 0, 0, 0),
            opcode("NEWTABLE", 1), opcode("EXTRAARG"),
            opcode("NEWTABLE", 2), opcode("EXTRAARG"),
            opcode("SETFIELD", 1, 1, 2), opcode("GETUPVAL", 2, 1),
            opcode("TAILCALL", 0, 3, 0), opcode("RETURN"), opcode("RETURN0"),
        ]

    def test_captured_metatable_factory(self):
        proof = MOD.check_factory(self.root, self.constants,
                                  self.children, self.factory, self.child)
        self.assertEqual(proof["factory_child_proto_id"], 19)
        self.assertEqual(proof["captured_shared_metatable_root_register"], 13)
        self.assertEqual(proof["native_field_string"], "__fields__")
        self.assertFalse(proof["factory_directly_returns_raw_newtable"])

    def test_capture_wrong_register_fails(self):
        self.factory["upvalues"] = [(0, 0, 0), (1, 12, 0)]
        with self.assertRaisesRegex(ValueError, "capture"):
            MOD.check_factory(self.root, self.constants,
                              self.children, self.factory, self.child)

    def test_wrong_field_literal_fails(self):
        self.constants[3] = b"__other__"
        with self.assertRaisesRegex(ValueError, "keys differ"):
            MOD.check_factory(self.root, self.constants,
                              self.children, self.factory, self.child)

    def test_possible_write_to_factory_register(self):
        arr = [opcode("MOVE", 16) for _ in range(10)]
        self.assertEqual(MOD.possible_writes_to_R15(arr, 0, len(arr)), [])
        arr[4] = opcode("SELF", 14, 2)
        self.assertEqual(MOD.possible_writes_to_R15(arr, 0, len(arr))[0][0], 4)

    def test_call_result_range_is_considered_hazard(self):
        arr = [opcode("MOVE", 16), opcode("CALL", 14, 1, 0)]
        self.assertTrue(MOD.possible_writes_to_R15(arr, 0, 2))


if __name__ == "__main__":
    unittest.main()
