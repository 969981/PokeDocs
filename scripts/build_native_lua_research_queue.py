#!/usr/bin/env python3
"""Rebuild pinned SV C native-evidence and ZA S/F Haxe investigation queues.

Pure standard library. Does not run game bytecode, infer original names,
modify any hashlist, or silently accept a changed upstream snapshot.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/lua-join-2026-11-05"
HASHLINE = re.compile(r"^0x([0-9a-fA-F]{16})(?:\s+(.*))?$")
SV_SHA = "4619e7da6d2d9c6faab4eb0d5f3a2d6c8ef0e046"
ZA_SHA = "30bd7b29277844bfe41c5efe54739471bed12766"
SV_FIELDS = ("hash", "line", "status", "direct_F", "static_S_count", "global_reg_count",
             "root_ref_ops", "nested_ref_ops", "phase4", "static_PC", "global_PC",
             "static_S_keys", "original_name_confirmed")
ZA_FIELDS = ("kind", "hash", "line", "prior_source_line", "haxe_refs", "haxe_calls",
             "haxe_reads", "haxe_writes", "haxe_declarations", "haxe_abi", "score",
             "first_haxe_source", "first_haxe_line", "evidence", "native_opcode_verified",
             "original_name_confirmed")


def hashlist(path: Path):
    rows = []
    for line, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        m = HASHLINE.fullmatch(raw.rstrip())
        if not m:
            raise ValueError(f"Malformed hashlist {path}:{line}")
        rows.append({"hash": m[1].upper(), "name": (m[2] or "").strip(), "line": line})
    return rows


def tsv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def group(rows, key):
    result = defaultdict(list)
    for row in rows:
        result[row[key]].append(row)
    return result


def dump_tsv(rows, fields):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def build(root: Path = ROOT):
    evidence = root / "docs/evidence/lua-join-2026-11-05"
    native_no_f = tsv(evidence / "upstream-sv-unknown-c.tsv")
    static = tsv(evidence / "upstream-sv-static-s.tsv")
    global_reg = tsv(evidence / "upstream-sv-global-registrations.tsv")
    residual = tsv(evidence / "upstream-sv-residual-80.tsv")
    haxe = tsv(evidence / "upstream-za-haxe-references.tsv")
    za_index = tsv(evidence / "upstream-za-unresolved-index.tsv")
    if (len(native_no_f), len(static), len(global_reg), len(residual),
            len(haxe), len(za_index)) != (299, 281, 213, 80, 258, 162):
        raise ValueError("Pinned native/Haxe source corpus was changed")

    sv_lua = root / "SV/Hashlists/Lua"
    za_lua = root / "ZA/Hashlists/Lua"
    current_c = [r for r in hashlist(sv_lua / "lua_c_hashes.txt") if not r["name"]]
    named_s = {"S" + r["hash"]: r["name"]
               for r in hashlist(sv_lua / "lua_s_hashes.txt") if r["name"]}
    missing_original = {x["class_hash"]: x for x in native_no_f}
    native_static = group(static, "class_hash")
    native_global = group(global_reg, "class_hash")
    native_residual = {x["class_hash"]: x for x in residual}

    sv_rows = []
    for row in current_c:
        token = "C" + row["hash"]
        previous = missing_original.get(token)
        s = native_static.get(token, [])
        g = native_global.get(token, [])
        r = native_residual.get(token)
        status = ("DIRECT_C_TO_F" if previous is None
                  else "STATIC_C_TO_S_PLUS_GLOBAL" if s and g
                  else "STATIC_C_TO_S" if s
                  else "GLOBAL_CLASS_REG" if g
                  else r["status"] if r else "UNREFERENCED_BY_INDEXED_OPS")
        sv_rows.append({
            "hash": "0x" + row["hash"], "line": row["line"], "status": status,
            "direct_F": "YES" if previous is None else "NO_STRICT_CHAIN",
            "static_S_count": len(s), "global_reg_count": len(g),
            "root_ref_ops": previous["root_ref_ops"] if previous else "",
            "nested_ref_ops": previous["nested_ref_ops"] if previous else "",
            "phase4": r["status"] if r else "",
            "static_PC": ";".join(x["source"] + ":" + x["root_pc"] for x in s[:4]),
            "global_PC": ";".join(x["source"] + ":" + x["root_pc"] for x in g[:4]),
            "static_S_keys": ";".join(
                named_s.get(x["s_field_hash"]) or x["s_field_name"] or x["s_field_hash"]
                for x in s[:8]),
            "original_name_confirmed": "NO",
        })

    prior = {(x["kind"], x["hash"][2:].upper()): x for x in za_index}
    haxe_by_hash = group(haxe, "hash")
    za_rows = []
    for kind in ("s", "f"):
        for current in (r for r in hashlist(za_lua / f"lua_{kind}_hashes.txt")
                        if not r["name"]):
            digest = current["hash"]
            old = prior.get((kind, digest))
            if old is None:
                raise ValueError(f"ZA {kind} hash absent from pinned source: {digest}")
            refs = [x for x in haxe_by_hash.get("0x" + digest, [])
                    if x["kind"] == kind]
            roles = Counter(x["role"] for x in refs)
            score = (roles["CALL"] * 6 + roles["WRITE"] * 5
                     + roles["READ"] * 3 + roles["DECLARATION"]
                     + roles["ABI_ANNOTATION"])
            za_rows.append({
                "kind": kind, "hash": "0x" + digest, "line": current["line"],
                "prior_source_line": old["original_line"],
                "haxe_refs": len(refs), "haxe_calls": roles["CALL"],
                "haxe_reads": roles["READ"], "haxe_writes": roles["WRITE"],
                "haxe_declarations": roles["DECLARATION"],
                "haxe_abi": roles["ABI_ANNOTATION"], "score": score,
                "first_haxe_source": refs[0]["path"] if refs else "",
                "first_haxe_line": refs[0]["line"] if refs else "",
                "evidence": "HAXE_ONLY" if refs else "NO_HAXE_REF",
                "native_opcode_verified": "NO", "original_name_confirmed": "NO",
            })
    za_rows.sort(key=lambda x: (-x["score"], x["kind"], x["hash"]))

    if (len(sv_rows), len(za_rows)) != (1334, 155):
        raise ValueError("Current Hashlist counts drifted; create a new research baseline")
    if sum(x["direct_F"] == "YES" for x in sv_rows) != 1047:
        raise ValueError("Native C-to-F complement count changed")
    if (sum(x["kind"] == "s" and x["haxe_refs"] > 0 for x in za_rows) != 114
            or sum(x["haxe_refs"] for x in za_rows) != 256):
        raise ValueError("Pinned Haxe references no longer match")
    counts = dict(Counter(x["status"] for x in sv_rows))
    summary = {
        "SV": {
            "current_unknown_C": len(sv_rows), "direct_C_to_F": 1047,
            "old_no_direct_299": len(native_no_f),
            "current_no_direct_F": sum(x["direct_F"] != "YES" for x in sv_rows),
            "statuses": counts, "native_C_to_S_edges_in_old_299": 281,
            "native_global_registration_edges_in_old_299": 213,
        },
        "ZA": {
            "current_unknown_S": 114, "current_unknown_F": 41,
            "haxe_references_to_unknown_S": 256, "S_with_references": 114,
            "F_with_references": 0, "native_ZA_Lua_opcode_verified": False,
        },
        "source": {"SV_Resources_commit": SV_SHA, "ZA_Resources_commit": ZA_SHA},
        "evidence_limit": ("SV direct-F class membership comes from old 299 no-direct-F native set complement. "
                           "Per-F original PC not stored here. ZA Haxe references are reconstructed, "
                           "not native original names."),
        "original_names_recovered_by_this_join": 0,
    }
    return {
        evidence / "sv-native-class-queue.tsv": dump_tsv(sv_rows, SV_FIELDS),
        evidence / "za-haxe-queue.tsv": dump_tsv(za_rows, ZA_FIELDS),
        evidence / "summary.json": json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    }, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Compare golden output without modifying files")
    mode.add_argument("--write", action="store_true", help="Rebuild pinned evidence outputs in place")
    args = parser.parse_args()
    generated, summary = build(args.root)
    for path, content in generated.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Evidence drift: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
