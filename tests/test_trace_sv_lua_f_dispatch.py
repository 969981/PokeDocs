"""Synthetic Lua 5.4 coverage for F-field receiver origin and static SELF->CALL."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_sv_blua import HEADER
from trace_sv_lua_f_dispatch import FDispatchReader

TOKEN = b'F18D6EEB7767BB85C'
HASH = int(TOKEN[1:], 16)


def vi(num):
    parts = [num & 127]
    num >>= 7
    while num:
        parts.insert(0, num & 127)
        num >>= 7
    parts[-1] |= 128
    return bytes(parts)


def ins(op, a=0, b=0, c=0, k=0, bx=None):
    if bx is not None:
        return op | (a << 7) | (bx << 15)
    return op | (a << 7) | (k << 15) | (b << 16) | (c << 24)


def jump(delta):
    return 56 | ((delta + ((1 << 25) - 1)//2) << 7)


def chunk(code, constants, nparams=1):
    data = vi(0) + vi(0) + vi(0) + bytes([nparams, 0, 12])
    data += vi(len(code)) + struct.pack('<%dI' % len(code), *code)
    data += vi(len(constants))
    for c in constants:
        data += b'\x04' + vi(len(c) + 1) + c
    data += vi(1) + b'\x00\x00\x00'
    data += vi(0)  # children
    data += vi(0)*4  # debug vectors
    return HEADER + b'\x01' + data


class TestUnknownFDispatch(unittest.TestCase):
    def parse(self, code, constants=None, nparams=1):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/'test.blua'
            file.write_bytes(chunk(code, constants or [TOKEN], nparams))
            reader = FDispatchReader(file, {HASH})
            reader.analyze()
            return reader.field_sites

    def test_condition_guard_exact_jmp_target(self):
        code = [
            ins(14,a=1,b=0,c=0),
            ins(60,a=1,b=1,k=1),
            jump(2),
            ins(20,a=1,b=0,c=0,k=1),
            ins(68,a=1,b=2,c=1),
            ins(71),
        ]
        refs = self.parse(code, [TOKEN,b'F'])
        self.assertEqual([r['opcode'] for r in refs],
                         ['GETFIELD','SELF'])
        x = refs[-1]
        self.assertEqual(x['receiver_origin']['kind'], 'FORMAL_PARAMETER')
        self.assertEqual(x['call']['call_pc'], 4)
        self.assertEqual(x['preceding_guard_getfield_pc'], 0)
        self.assertEqual(x['guard_jmp_pc'], 2)
        self.assertEqual(x['guard_jump_target_pc'], 5)

    def test_call_uses_self_after_extra_argument_move(self):
        code = [ins(20,a=1,b=0,c=0,k=1), ins(0,a=3,b=0),
                ins(68,a=1,b=3,c=1), ins(71)]
        refs = self.parse(code)
        self.assertEqual(refs[0]['call']['call_pc'], 2)
        self.assertIsNone(refs[0]['preceding_guard_getfield_pc'])

    def test_overwritten_callee_rejected(self):
        code = [ins(20,a=1,b=0,c=0,k=1), ins(0,a=1,b=0),
                ins(68,a=1,b=2,c=1), ins(71)]
        self.assertIsNone(self.parse(code)[0]['call'])

    def test_branch_between_self_and_call_rejected(self):
        code = [ins(20,a=1,b=0,c=0,k=1), jump(1),
                ins(68,a=1,b=2,c=1), ins(71)]
        self.assertIsNone(self.parse(code)[0]['call'])

    def test_receiver_indexed_from_first_parameter(self):
        code = [ins(13,a=2,b=0,c=8),ins(9,a=3,b=0),
                ins(0,a=4,b=1),ins(68,a=3,b=2,c=2),
                ins(18,a=2,b=0,c=3),ins(71)]
        refs = self.parse(code,nparams=2)
        self.assertEqual(refs[0]['receiver_origin']['kind'],'INDEXED_TABLE')
        self.assertEqual(refs[0]['receiver_origin']['index'],8)
        self.assertEqual(refs[0]['receiver_origin']['table']['kind'],'FORMAL_PARAMETER')
        self.assertEqual(refs[0]['value_origin']['kind'],'CALL_RESULT_UNRESOLVED')

    def test_literal_token_is_not_a_method_reference(self):
        self.assertEqual(self.parse([ins(3,a=2,bx=0),ins(71)]),[])

    def test_getfield_not_equivalent_to_call(self):
        refs = self.parse([ins(14,a=1,b=0,c=0),ins(71)])
        self.assertEqual(len(refs),1)
        self.assertEqual(refs[0]['opcode'],'GETFIELD')
        self.assertNotIn('call',refs[0])


if __name__ == '__main__':
    unittest.main()
