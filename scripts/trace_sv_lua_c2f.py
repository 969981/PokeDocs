#!/usr/bin/env python3
"""Proof-grade C -> prototype -> F assignments in genuine Lua 5.4 chunks.

Requires inspect_sv_blua.py from this repo. Does not execute bytecode, guess
symbol names, or treat constants coexisting as proof of an assignment.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import struct
from collections import Counter
from pathlib import Path
from inspect_sv_blua import Reader, load_hashlists

CLASS = re.compile(rb"C[0-9A-F]{16}\Z")
FIELD = re.compile(rb"F[0-9A-F]{16}\Z")
# Fixed Lua 5.4 opcode numbers: verify against official lopcodes.h.
MOVE, LOADK, GETUPVAL, GETTABLE, SETTABLE, CLOSURE = 0, 3, 9, 12, 16, 79
OP_PATTERN = (GETUPVAL, LOADK, GETTABLE, LOADK, GETTABLE, LOADK, CLOSURE, SETTABLE)
COLUMNS = ("file", "outer_proto", "outer_proto_offset", "class_hash", "function_hash",
           "closure_proto", "closure_child_index", "pc_start", "pc_write", "byte_offset_write",
           "class_const_index", "prototype_const_index", "function_const_index",
           "register_base", "register_key", "register_value", "upvalue_index")


def opcode(w): return w & 0x7f

def reg_a(w): return (w >> 7) & 255

def reg_b(w): return (w >> 16) & 255

def reg_c(w): return (w >> 24) & 255

def arg_bx(w): return (w >> 15) & 131071


class AssignmentReader(Reader):
    def __init__(self, path: Path):
        super().__init__(path)
        self.assignments = []
        self.total_candidate_windows = 0
        self.target_unknown_f = set()
        self.unknown_f_references = []

    def function(self, depth=0):
        if depth > 250:
            raise ValueError("Prototype recursion limit")
        this_proto = self.protos
        self.protos += 1
        self.max_depth = max(self.max_depth, depth)
        proto_offset = self.pos
        self.lua_string()
        self.integer(); self.integer()
        self.skip(3)
        ncode = self.integer()
        code_offset = self.pos
        self.skip(4 * ncode)
        nconst = self.integer()
        if nconst > 5_000_000:
            raise ValueError("Unreasonable constant count")
        self.constants += nconst
        constants = {}
        seen_kinds = set()
        for kidx in range(nconst):
            tag = self.byte()
            self.tag_counts[tag] += 1
            if tag in (0, 1, 17):
                pass
            elif tag in (3, 19):
                self.skip(8)
            elif tag in (4, 20):
                off = self.pos
                value = self.lua_string()
                constants[kidx] = value
                self.record_string(value, off, this_proto, seen_kinds)
            else:
                raise ValueError(f"Unexpected constant tag {tag} at 0x{self.pos:X}")
        nup = self.integer()
        self.skip(3 * nup)
        nchildren = self.integer()
        if nchildren > 100_000:
            raise ValueError("Unreasonable child count")
        children = []
        for _ in range(nchildren):
            child = self.protos
            self.function(depth + 1)
            children.append(child)
        self.skip(self.integer())
        for _ in range(self.integer()):
            self.integer(); self.integer()
        for _ in range(self.integer()):
            self.lua_string(); self.integer(); self.integer()
        for _ in range(self.integer()):
            self.lua_string()
        if this_proto and 'C' in seen_kinds and 'F' in seen_kinds:
            self.c_f_same_proto += 1
        self.trace(code_offset, ncode, constants, children, nup, this_proto, proto_offset)
        return this_proto

    def trace(self, offset, ncode, constants, children, nup, proto, proto_offset):
        code = struct.unpack_from(f"<{ncode}I", self.data, offset)
        if self.target_unknown_f:
            for pc, word in enumerate(code):
                op = opcode(word)
                if op not in (14, 18):  # GETFIELD / SETFIELD
                    continue
                kidx = reg_c(word) if op == 14 else reg_b(word)
                token = constants.get(kidx)
                if token and FIELD.fullmatch(token) and int(token[1:], 16) in self.target_unknown_f:
                    self.unknown_f_references.append({
                        'file': self.file.name, 'proto': proto, 'pc': pc,
                        'byte_offset': offset + 4 * pc,
                        'opcode': 'GETFIELD' if op == 14 else 'SETFIELD',
                        'function_hash': token.decode('ascii'), 'constant_index': kidx,
                    })
        if ncode < len(OP_PATTERN):
            return
        for pc in range(ncode - 7):
            words = code[pc:pc+8]
            if tuple(map(opcode, words)) != OP_PATTERN:
                continue
            self.total_candidate_windows += 1
            ra, rb, rc = reg_a(words[0]), reg_a(words[1]), reg_a(words[6])
            if not (reg_a(words[2]) == ra and reg_b(words[2]) == ra and reg_c(words[2]) == rb
                    and reg_a(words[3]) == rb and reg_a(words[4]) == ra
                    and reg_b(words[4]) == ra and reg_c(words[4]) == rb
                    and reg_a(words[5]) == rb and reg_a(words[7]) == ra
                    and reg_b(words[7]) == rb and reg_c(words[7]) == rc):
                continue
            if (words[7] >> 15) & 1:  # SETTABLE k=1 uses K[C], not the closure register.
                continue
            if reg_b(words[0]) >= nup:
                raise ValueError(f"GETUPVAL out of range in Proto {proto} pc {pc}")
            cidx, pidx, fidx, child_idx = (arg_bx(words[1]), arg_bx(words[3]),
                                          arg_bx(words[5]), arg_bx(words[6]))
            c, pname, f = constants.get(cidx), constants.get(pidx), constants.get(fidx)
            if not (c and CLASS.fullmatch(c) and pname == b"prototype"
                    and f and FIELD.fullmatch(f)):
                continue
            if child_idx >= len(children):
                raise ValueError(f"CLOSURE Bx {child_idx} > child count {len(children)}")
            self.assignments.append(dict(zip(COLUMNS, (
                self.file.name, proto, proto_offset, c.decode("ascii"), f.decode("ascii"),
                children[child_idx], child_idx, pc, pc+7, offset+4*(pc+7),
                cidx, pidx, fidx, ra, rb, rc, reg_b(words[0])
            ))))

    def scan_assignments(self):
        report = self.scan()  # Lua header / EOF validation via shared Reader.
        by_cf = {(r['class_hash'], r['function_hash']) for r in self.assignments}
        return {"file": self.file.name, "sha256": report['sha256'],
                "byte_size": report['bytes'], "prototypes": report['prototypes'],
                "candidate_opcode_windows": self.total_candidate_windows,
                "assignments": len(self.assignments), "unique_pairs": len(by_cf),
                "distinct_class_hashes": len({c for c, _ in by_cf}),
                "distinct_function_hashes": len({f for _, f in by_cf}),
                "upvalue_index_counts": dict(Counter(str(r['upvalue_index']) for r in self.assignments))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='+', type=Path, help='Original Library .blua paths')
    p.add_argument('--report', type=Path, help='Summary JSON only; no original bytecode')
    p.add_argument('--repo', type=Path, help='PokeDocs root for unmapped F coverage')
    p.add_argument('--game', choices=('SV', 'ZA'), default='SV')
    p.add_argument('--assignments', type=Path, help='Complete CSV/TSV/GZ assignment evidence')
    p.add_argument('--references', type=Path, help='Evidence of unmapped F GETFIELD/SETFIELD sites')
    args = p.parse_args()
    reports, records = [], []
    observed_f = set()
    references = []
    unknown_f = set()
    if args.repo:
        unknown, _ = load_hashlists(args.repo, args.game)
        unknown_f = unknown['F']
    for path in args.files:
        reader = AssignmentReader(path)
        reader.target_unknown_f = unknown_f
        report = reader.scan_assignments()
        reports.append(report)
        observed_f.update(reader.encountered['F'])
        references.extend(reader.unknown_f_references)
        records.extend(reader.assignments)
        print(f"{path.name}: {report['assignments']} assignment definitions, "
              f"{report['distinct_class_hashes']} C, {report['distinct_function_hashes']} F")
    summary = {"evidence": "NATIVE_LUA54_INSTRUCTION_CHAIN_C_PROTOTYPE_F_ASSIGNMENT",
               "limits": "Shows bytecode closure assignment, not actual runtime calls or recovered original names. "
                         "Game version is not authenticated by Lua header alone.",
               "files": reports,
               "all_assignments": len(records),
               "global_unique_class_hashes": len({r['class_hash'] for r in records}),
               "global_unique_function_hashes": len({r['function_hash'] for r in records}),
               "global_unique_pairs": len({(r['class_hash'], r['function_hash']) for r in records})}
    if args.repo:
        f_unknown = unknown_f
        defined_f = {int(r['function_hash'][1:], 16) for r in records}
        owner = {(r['file'], r['closure_proto']): r for r in records}
        for ref in references:
            caller = owner.get((ref['file'], ref['proto']))
            ref['caller_class_hash'] = caller['class_hash'] if caller else ''
            ref['caller_method_hash'] = caller['function_hash'] if caller else ''
        summary['unknown_F'] = {
            'unmapped_F_count': len(f_unknown),
            'found_as_any_bytecode_constant': len(f_unknown & observed_f),
            'found_as_strict_C_prototype_F_definition': len(f_unknown & defined_f),
            'not_found_as_bytecode_constant': len(f_unknown - observed_f),
            'getfield_sites': sum(r['opcode'] == 'GETFIELD' for r in references),
            'setfield_sites': sum(r['opcode'] == 'SETFIELD' for r in references),
            'reference_sites_in_directly_bound_closures': sum(bool(r['caller_class_hash']) for r in references),
        }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if args.assignments:
        args.assignments.parent.mkdir(parents=True, exist_ok=True)
        opener = gzip.open if args.assignments.suffix == '.gz' else open
        with opener(args.assignments, 'wt', encoding='utf-8', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=COLUMNS, delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(records)
    if args.references:
        args.references.parent.mkdir(parents=True, exist_ok=True)
        columns = ('file', 'proto', 'pc', 'byte_offset', 'opcode', 'function_hash',
                   'constant_index', 'caller_class_hash', 'caller_method_hash')
        opener = gzip.open if args.references.suffix == '.gz' else open
        with opener(args.references, 'wt', encoding='utf-8', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=columns, delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(references)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
