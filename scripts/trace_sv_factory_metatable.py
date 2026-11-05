#!/usr/bin/env python3
"""Read-only original SV 4.0.0 Lua factory/metatable proof for 95 unknown C.

Verifies literal Lua54 bytecode, Upvalue descriptors, stable root R15 and
95 class registrations. Does not prove runtime object identity, existence of
original symbol names, or absence of intervening global-table mutations.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import csv
import re
from pathlib import Path

SHA = "c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815"


def load(path):
    spec = importlib.util.spec_from_file_location("sv_factory_core", path)
    if spec is None or spec.loader is None:
        raise ValueError("Unable to import Lua parser")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_upvalues(core, raw):
    class LuaWithUpvalues(core.Lua54):
        def _proto(self, parent, depth):
            if depth > 150:
                raise core.FormatError("Suspicious prototype depth")
            r = self.reader
            pid = len(self.protos)
            p = {"id": pid, "parent": parent, "depth": depth, "children": []}
            self.protos.append(p)
            r.string(); r.vint(); r.vint(); r.take(3)
            n = r.vint()
            p["code_offset"] = r.off
            p["code_count"] = n
            r.take(n * 4)
            const = []
            for _ in range(r.vint()):
                tag = r.u8()
                if tag in (0, 1, 17):
                    const.append(None)
                elif tag in (3, 19):
                    r.take(8); const.append(None)
                elif tag in (4, 20):
                    const.append(r.string())
                else:
                    raise core.FormatError("Unsupported constant tag")
            p["constants"] = const
            p["upvalues"] = [tuple(r.take(3)) for _ in range(r.vint())]
            for _ in range(r.vint()):
                p["children"].append(self._proto(pid, depth + 1))
            r.take(r.vint())
            for _ in range(r.vint()):
                r.vint(); r.vint()
            for _ in range(r.vint()):
                r.string(); r.vint(); r.vint()
            for _ in range(r.vint()):
                r.string()
            return pid
    obj = LuaWithUpvalues(raw)
    obj.parse()
    return obj


def assert_op(code, pc, name, a=None, b=None, c=None):
    x = code[pc]
    if (x[0] != name or (a is not None and x[1] != a) or
            (b is not None and x[2] != b) or
            (c is not None and x[3] != c)):
        raise ValueError(f"Native opcode mismatch at {pc}: {x}, expected {name}")
    return x


def check_factory(code, root_constants, root_children, factory, child_code):
    assert_op(code, 43, "NEWTABLE", a=13)
    assert_op(code, 45, "SETFIELD", a=13, c=12)
    assert_op(code, 46, "GETTABUP", a=14, b=0)
    assert_op(code, 47, "SETFIELD", a=13, c=14)
    if (root_constants[code[45][2]] != b"__newindex" or
            root_constants[code[46][3]] != b"_hx_tostring" or
            root_constants[code[47][2]] != b"__tostring"):
        raise ValueError("Root metatable keys differ")
    closure = assert_op(code, 49, "CLOSURE", a=15)
    if (closure[5] != 18 or root_children[18] != factory["id"] or
            factory["id"] != 19 or factory["parent"] != 0 or
            factory["upvalues"] != [(0, 0, 0), (1, 13, 0)]):
        raise ValueError("Factory closure/captured R13 identity changed")
    if factory["constants"] != [b"setmetatable", b"__fields__"]:
        raise ValueError("Factory literal source strings differ")
    expected = ("GETTABUP", "NEWTABLE", "EXTRAARG", "NEWTABLE",
                "EXTRAARG", "SETFIELD", "GETUPVAL", "TAILCALL",
                "RETURN", "RETURN0")
    if tuple(x[0] for x in child_code) != expected:
        raise ValueError("Factory opcode sequence differs")
    assert_op(child_code, 0, "GETTABUP", a=0, b=0, c=0)
    assert_op(child_code, 1, "NEWTABLE", a=1)
    assert_op(child_code, 3, "NEWTABLE", a=2)
    assert_op(child_code, 5, "SETFIELD", a=1, b=1, c=2)
    assert_op(child_code, 6, "GETUPVAL", a=2, b=1)
    assert_op(child_code, 7, "TAILCALL", a=0, b=3, c=0)
    return {
        "factory_root_pc": 49, "factory_child_proto_id": factory["id"],
        "factory_upvalues": [list(u) for u in factory["upvalues"]],
        "captured_shared_metatable_root_register": 13,
        "native_function_string": "setmetatable",
        "native_field_string": "__fields__",
        "metatable_field_names": ["__newindex", "__tostring"],
        "tailcall_source": "setmetatable(new_table_with_fields, captured_metatable)",
        "factory_directly_returns_raw_newtable": False,
    }


def possible_writes_to_R15(code, start, end):
    """Conservatively reject apparent writes to the captured factory register."""
    out = []
    for pc in range(start, end):
        op, a, b, c, k, bx, ax = code[pc]
        if a == 15:
            out.append([pc, op, "direct-A"])
        if op == "SELF" and a + 1 == 15:
            out.append([pc, op, "SELF A+1"])
        if op == "LOADNIL" and a <= 15 <= a + b:
            out.append([pc, op, "LOADNIL range"])
        if op in ("CALL", "VARARG") and a <= 15 and (c == 0 or a + c - 2 >= 15):
            out.append([pc, op, "result range"])
        if op in ("FORPREP", "FORLOOP", "TFORPREP", "TFORLOOP", "TFORCALL") and a <= 15 <= a + 5:
            out.append([pc, op, "iterator range"])
    return out


def run(main, parser, registrations, static, unknown):
    raw = main.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SHA:
        raise ValueError(f"Unexpected SV main sha256: {digest}")
    core = load(parser)
    lua = parse_upvalues(core, raw)
    root = lua.protos[0]
    code = core.instructions(raw, root)
    const = root["constants"]
    factory = lua.protos[root["children"][18]]
    proof = check_factory(code, const, root["children"], factory,
                          core.instructions(raw, factory))
    with registrations.open(encoding="utf-8-sig", newline="") as f:
        global_rows = list(csv.DictReader(f, delimiter="\t"))
    with static.open(encoding="utf-8-sig", newline="") as f:
        static_rows = list(csv.DictReader(f, delimiter="\t"))
    missing = {
        "C" + m.group(1).upper()
        for line in unknown.read_text(encoding="utf-8-sig").splitlines()
        if (m := re.fullmatch(r"0x([0-9a-fA-F]{16})\s*", line))
    }
    static_classes = {r["class_hash"] for r in static_rows}
    selected = sorted(
        (r for r in global_rows if r["class_hash"] in static_classes and r["class_hash"] in missing),
        key=lambda r: r["class_hash"]
    )
    if len(selected) != 95 or len({r["class_hash"] for r in selected}) != 95:
        raise ValueError("Unknown-C dual-structure baseline is not 95")
    root_pcs = [int(r["root_pc"]) for r in selected]
    hazards = possible_writes_to_R15(code, 50, max(root_pcs) + 5)
    if hazards:
        raise ValueError(f"R15 may have been overwritten: {hazards[:20]}")
    details = []
    for row in selected:
        pc = int(row["root_pc"])
        seq = code[pc:pc+5]
        if [r[0] for r in seq] != ["GETUPVAL", "LOADK", "MOVE", "CALL", "SETTABLE"]:
            raise ValueError("Registration opcode sequence differs")
        a = seq[0][1]
        if not (seq[0][2] == 0 and seq[1][1] == a+1 and
                const[seq[1][5]] == row["class_hash"].encode() and
                seq[2][1:3] == (a+2, 15) and seq[3][1:4] == (a+2, 1, 2) and
                seq[4][1:4] == (a, a+1, a+2)):
            raise ValueError(f"Registration register mismatch: {row['class_hash']}")
        details.append({
            "class_hash": row["class_hash"], "root_pc": pc,
            "factory_register": 15, "factory_proto_id": factory["id"],
            "root_upvalue_env_index": 0, "global_slot_proven": True,
            "runtime_instance_identity_confirmed": False,
        })
    report = {
        "version": "SV 4.0.0", "main_sha256": digest,
        "root_prototype_instruction_count": len(code), **proof,
        "unknown_dual_C": len(details),
        "registration_uses_shared_factory": len(details),
        "factory_register_R15_maywrite_sites_before_last_registration": len(hazards),
        "native_original_names_recovered": 0,
        "runtime_instance_identity_confirmed": 0,
        "boundary": "Verified metatable factory and lexical register source; dynamic global table mutation/identity not proven.",
    }
    return report, details


def main_cli():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("main", "parser", "registrations", "static", "unknown", "out"):
        ap.add_argument("--" + name, type=Path, required=True)
    args = ap.parse_args()
    report, records = run(args.main, args.parser, args.registrations,
                          args.static, args.unknown)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "sv-95-factory-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.out / "sv-95-factory-registers.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main_cli()
