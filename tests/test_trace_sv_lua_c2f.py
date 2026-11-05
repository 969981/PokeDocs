"""Synthetic Lua 5.4 chunks: validate direct C.prototype[F] assignment evidence."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_sv_blua import HEADER
from trace_sv_lua_c2f import AssignmentReader


def var(v):
    out = [v & 127]
    v >>= 7
    while v:
        out.insert(0, v & 127)
        v >>= 7
    out[-1] |= 0x80
    return bytes(out)


def ins(op, a=0, b=0, c=0, k=0, bx=None):
    if bx is not None:
        return op | (a << 7) | (bx << 15)
    return op | (a << 7) | (k << 15) | (b << 16) | (c << 24)


def mkproto(code, const, upvalues=1, children=()):
    blob = var(0) + var(0) + var(0) + bytes((0, 0, 8))
    blob += var(len(code)) + struct.pack("<%dI" % len(code), *code)
    blob += var(len(const))
    for name in const:
        blob += b"\x04" + var(len(name) + 1) + name
    blob += var(upvalues) + bytes(3 * upvalues)
    blob += var(len(children)) + b"".join(children)
    return blob + var(0) * 4


class TestTrace(unittest.TestCase):
    def parse(self, code, strings, children):
        data = HEADER + b"\x01" + mkproto(code, strings, 1, children)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.blua"
            path.write_bytes(data)
            reader = AssignmentReader(path)
            return reader.scan_assignments(), reader.assignments

    def sample(self):
        return [
            ins(9, a=0, b=0),      # GETUPVAL
            ins(3, a=1, bx=0),     # LOADK class
            ins(12, a=0, b=0, c=1),
            ins(3, a=1, bx=1),     # LOADK prototype
            ins(12, a=0, b=0, c=1),
            ins(3, a=1, bx=2),     # LOADK function
            ins(79, a=2, bx=0),    # CLOSURE direct child
            ins(16, a=0, b=1, c=2, k=0),  # SETTABLE register value
            ins(71),
        ]

    def test_verified_chain_resolves_direct_child(self):
        child = mkproto([ins(71)], [], 0, ())
        report, rows = self.parse(self.sample(),
            [b"CFD9B049511E682DA", b"prototype", b"F7C68FEDB79AB6396"], [child])
        self.assertEqual(report["assignments"], 1)
        self.assertEqual(rows[0]["class_hash"], "CFD9B049511E682DA")
        self.assertEqual(rows[0]["function_hash"], "F7C68FEDB79AB6396")
        self.assertEqual(rows[0]["closure_proto"], 1)
        self.assertEqual(rows[0]["pc_write"], 7)

    def test_wrong_key_register_is_not_relationship(self):
        child = mkproto([ins(71)], [], 0, ())
        code = self.sample()
        code[7] = ins(16, a=0, b=8, c=2, k=0)
        _, rows = self.parse(code,
            [b"CFD9B049511E682DA", b"prototype", b"F7C68FEDB79AB6396"], [child])
        self.assertEqual(len(rows), 0)

    def test_different_property_not_prototype(self):
        child = mkproto([ins(71)], [], 0, ())
        _, rows = self.parse(self.sample(),
            [b"CFD9B049511E682DA", b"not_prototype", b"F7C68FEDB79AB6396"], [child])
        self.assertEqual(len(rows), 0)

    def test_constant_value_not_closure(self):
        child = mkproto([ins(71)], [], 0, ())
        code = self.sample()
        code[7] = ins(16, a=0, b=1, c=2, k=1)
        _, rows = self.parse(code,
            [b"CFD9B049511E682DA", b"prototype", b"F7C68FEDB79AB6396"], [child])
        self.assertEqual(len(rows), 0)

    def test_unknown_f_fields_inside_short_child_proto(self):
        token = b"F33571D8C0B39C3CD"
        child = mkproto([ins(14, a=0, b=0, c=0),
                         ins(18, a=0, b=0, c=0, k=0), ins(71)], [token], 0, ())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.blua"
            path.write_bytes(HEADER + b"\x01" + mkproto([ins(71)], [], 1, [child]))
            reader = AssignmentReader(path)
            reader.target_unknown_f = {int(token[1:], 16)}
            report = reader.scan_assignments()
            self.assertEqual(report["assignments"], 0)
            refs = reader.unknown_f_references
            self.assertEqual(len(refs), 2)
            self.assertEqual([x["opcode"] for x in refs], ["GETFIELD", "SETFIELD"])
            self.assertEqual([x["pc"] for x in refs], [0, 1])

    def test_invalid_child_reference_is_rejected(self):
        child = mkproto([ins(71)], [], 0, ())
        code = self.sample()
        code[6] = ins(79, a=2, bx=1)
        with self.assertRaisesRegex(ValueError, "CLOSURE Bx"):
            self.parse(code,
                [b"CFD9B049511E682DA", b"prototype", b"F7C68FEDB79AB6396"], [child])


if __name__ == "__main__":
    unittest.main()
