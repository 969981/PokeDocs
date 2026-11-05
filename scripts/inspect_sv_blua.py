#!/usr/bin/env python3
"""Read Lua 5.4 bytecode structure and compare real constants to PokeDocs hashes.

No execution, disassembly assumptions, bytecode publishing, or guessed names.
Input bytecode stays on the local machine. Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.setrecursionlimit(2000)
HEADER = (b"\x1bLua\x54\x00\x19\x93\r\n\x1a\n\x04\x08\x08"
          + struct.pack("<q", 0x5678) + struct.pack("<d", 370.5))
TOKEN = re.compile(rb"^([CFSE])([0-9A-F]{16})$")
SYMBOL = re.compile(rb"^[A-Za-z_][A-Za-z_0-9./:\-]{1,180}$")
ROW = re.compile(r"^0x([a-fA-F0-9]{16})(?:[ \t]+(.+))?[ \t]*$")
BASIS = 0xCBF29CE484222645
PRIME = 0x100000001B3
MASK = 0xFFFFFFFFFFFFFFFF


def hash_bytes(data: bytes) -> int:
    value = BASIS
    for c in data:
        value = ((value ^ c) * PRIME) & MASK
    return value


def load_hashlists(repo: Path, game: str):
    unknown = {kind: set() for kind in "CFSE"}
    known = {kind: {} for kind in "CFSE"}
    for kind in "CFSE":
        path = repo / game / "Hashlists" / "Lua" / f"lua_{kind.lower()}_hashes.txt"
        with path.open(encoding="utf-8-sig") as stream:
            for lineno, line in enumerate(stream, 1):
                value = line.strip()
                if not value:
                    continue
                m = ROW.fullmatch(value)
                if not m:
                    raise ValueError(f"Invalid Lua hash row: {path}:{lineno}")
                digest = int(m.group(1), 16)
                name = (m.group(2) or "").strip()
                if not name:
                    unknown[kind].add(digest)
                else:
                    if hash_bytes(name.encode("utf-8")) != digest:
                        raise ValueError(f"Invalid named hash: {path}:{lineno}")
                    known[kind][digest] = name
    return unknown, known


class Reader:
    def __init__(self, file: Path, unknown=None, known=None):
        self.file = file
        self.data = file.read_bytes()
        self.pos = 0
        self.protos = 0
        self.max_depth = 0
        self.constants = 0
        self.tag_counts = Counter()
        self.encountered = {kind: Counter() for kind in "CFSE"}
        self.match_candidates = defaultdict(dict)
        self.known_name_matches = 0
        self.c_f_same_proto = 0
        self.unknown = unknown
        self.known = known

    def byte(self):
        if self.pos >= len(self.data):
            raise ValueError(f"Truncated chunk at 0x{self.pos:X}")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def skip(self, n: int):
        if n < 0 or self.pos + n > len(self.data):
            raise ValueError(f"Invalid length {n} at 0x{self.pos:X}")
        self.pos += n

    def read(self, n: int):
        start = self.pos
        self.skip(n)
        return self.data[start:self.pos]

    def integer(self):
        result = 0
        for _ in range(11):
            digit = self.byte()
            result = (result << 7) | (digit & 127)
            if digit & 128:
                return result
        raise ValueError("Invalid Lua 5.4 variable integer")

    def lua_string(self):
        size = self.integer()
        if not size:
            return None
        if size > 2_000_000:
            raise ValueError("Unreasonable Lua string length")
        return self.read(size - 1)

    def record_string(self, data: bytes | None, byte_offset: int, proto: int,
                      token_kinds: set[str]):
        if not data:
            return
        match = TOKEN.fullmatch(data)
        if match:
            kind = match.group(1).decode("ascii")
            digest = int(match.group(2), 16)
            self.encountered[kind][digest] += 1
            token_kinds.add(kind)
            return
        if self.unknown is None or not SYMBOL.fullmatch(data):
            return
        digest = hash_bytes(data)
        name = data.decode("ascii")
        for kind in "CFSE":
            if digest in self.unknown[kind]:
                self.match_candidates[(kind, digest)][name] = {
                    "kind": kind, "hash": f"0x{digest:016X}", "candidate": name,
                    "file": self.file.name, "proto": proto,
                    "constant_offset": byte_offset, "evidence": "H2_STRING_CONSTANT_HASH_EXACT",
                }
            elif digest in self.known[kind] and self.known[kind][digest] == name:
                self.known_name_matches += 1

    def function(self, depth=0):
        if depth > 250:
            raise ValueError("Unreasonable prototype nesting depth")
        proto = self.protos
        self.protos += 1
        self.max_depth = max(self.max_depth, depth)
        self.lua_string()  # source, inherited from parent if null
        self.integer()     # linedefined
        self.integer()     # lastlinedefined
        self.skip(3)       # numparams, vararg, maxstacksize
        self.skip(4 * self.integer())  # native Lua 5.4 instructions
        n = self.integer()
        if n > 5_000_000:
            raise ValueError("Unreasonable constant count")
        self.constants += n
        seen_kinds = set()
        for _ in range(n):
            tag = self.byte()
            self.tag_counts[tag] += 1
            if tag in (0, 1, 17):
                pass
            elif tag in (3, 19):
                self.skip(8)
            elif tag in (4, 20):
                start = self.pos
                self.record_string(self.lua_string(), start, proto, seen_kinds)
            else:
                raise ValueError(f"Unknown Lua constant tag {tag} at 0x{self.pos:X}")
        self.skip(3 * self.integer())  # upvalue descriptors
        children = self.integer()
        if children > 100_000:
            raise ValueError("Unreasonable subprototype count")
        for _ in range(children):
            self.function(depth + 1)
        self.skip(self.integer())  # lineinfo bytes
        for _ in range(self.integer()):
            self.integer()  # absolute line pc
            self.integer()  # absolute line number
        for _ in range(self.integer()):
            self.lua_string()
            self.integer()
            self.integer()
        for _ in range(self.integer()):
            self.lua_string()
        if proto and "C" in seen_kinds and "F" in seen_kinds:
            self.c_f_same_proto += 1

    def scan(self):
        if self.read(len(HEADER)) != HEADER:
            raise ValueError("Invalid or unsupported Lua 5.4 bytecode header")
        initial_upvalues = self.byte()
        self.function()
        if self.pos != len(self.data):
            raise ValueError(f"Unparsed bytes: {len(self.data) - self.pos}")
        exact = []
        ambiguous = []
        for (kind, digest), names in sorted(self.match_candidates.items()):
            if len(names) == 1:
                exact.append(next(iter(names.values())))
            else:
                ambiguous.append({"kind": kind, "hash": f"0x{digest:016X}",
                                  "candidates": sorted(names)})
        return {
            "file": self.file.name,
            "sha256": hashlib.sha256(self.data).hexdigest(),
            "bytes": len(self.data), "header_hex": HEADER.hex(),
            "format": "Lua 5.4 bytecode (game version not authenticated by header)",
            "initial_upvalues": initial_upvalues, "prototypes": self.protos,
            "maximum_depth": self.max_depth, "constants": self.constants,
            "constant_types": {str(k): v for k, v in sorted(self.tag_counts.items())},
            "encoded": {kind: {"occurrences": sum(counter.values()),
                               "unique_hashes": len(counter)}
                        for kind, counter in self.encountered.items()},
            "proto_contains_C_and_F_constants": self.c_f_same_proto,
            "warning": "C and F constants coexisting in one prototype is NOT proof of ownership or a call",
            "named_constant_matches": self.known_name_matches,
            "new_hash_exact_candidates": exact,
            "ambiguous_candidates": ambiguous,
        }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("files", nargs="+", type=Path, help="Locally available .blua files")
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--game", choices=("SV", "ZA"), default="SV")
    p.add_argument("--output", type=Path, help="Report JSON (no raw bytecode)")
    a = p.parse_args()
    unknown, known = load_hashlists(a.repo, a.game)
    reports = []
    for path in a.files:
        report = Reader(path, unknown, known).scan()
        reports.append(report)
        print(f"{path.name}: Lua5.4, {report['prototypes']} prototypes, "
              f"{report['constants']} constants, "
              f"{len(report['new_hash_exact_candidates'])} new hash-exact constants")
    output = {"game": a.game,
              "note": "Hash exact match is not native semantic proof. Header does not authenticate game version.",
              "files": reports}
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")


if __name__ == "__main__":
    main()
