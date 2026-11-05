import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_sv_blua import HEADER, Reader, hash_bytes


def var(value):
    parts = [value & 127]
    value >>= 7
    while value:
        parts.insert(0, value & 127)
        value >>= 7
    parts[-1] |= 128
    return bytes(parts)


class TestBytecodeReader(unittest.TestCase):
    def test_hash(self):
        self.assertEqual(hash_bytes(b"SetCursorPos"), 0x0170EA75A6880AF5)

    def test_minimal_native_chunk(self):
        symbol = b"F9D25C0BA1A393C61"
        # Lua header + one top-level closure with one string constant.
        contents = (HEADER + b"\x01" + var(0) + var(0) + var(0)
                    + b"\x00\x01\x02" + var(0) + var(1)
                    + b"\x04" + var(len(symbol) + 1) + symbol
                    + var(0) + var(0) + var(0) + var(0) + var(0) + var(0))
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "test.blua"
            file.write_bytes(contents)
            report = Reader(file).scan()
            self.assertEqual(report["prototypes"], 1)
            self.assertEqual(report["constants"], 1)
            self.assertEqual(report["encoded"]["F"]["unique_hashes"], 1)
            self.assertEqual(report["encoded"]["F"]["occurrences"], 1)

    def test_reject_bad_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "broken.blua"
            file.write_bytes(b"garbage")
            with self.assertRaises(ValueError):
                Reader(file).scan()


if __name__ == "__main__":
    unittest.main()
