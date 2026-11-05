#!/usr/bin/env python3
"""Rank unknown SV Lua C hashes by *direct* C.prototype[F] bytecode signatures.

Input: TSV/TSV.gz emitted by trace_sv_lua_c2f.py. This does NOT infer the
original C name, ownership of indirect calls, inheritance, or runtime execution.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path

from inspect_sv_blua import load_hashlists

TOKEN = re.compile(r"^[CF][0-9A-F]{16}$")


def token_id(value: str, kind: str) -> int:
    value = value.strip().upper()
    if not TOKEN.fullmatch(value) or value[0] != kind:
        raise ValueError(f"Expected a {kind}+16-hex token, got {value!r}")
    return int(value[1:], 16)


def read_assignments(path: Path) -> dict[int, set[int]]:
    opener = gzip.open if path.suffix.lower() == ".gz" else open
    methods: dict[int, set[int]] = defaultdict(set)
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not {"class_hash", "function_hash"} <= set(reader.fieldnames or []):
            raise ValueError("Missing class_hash/function_hash TSV columns")
        for line, row in enumerate(reader, 2):
            try:
                c = token_id(row["class_hash"], "C")
                f = token_id(row["function_hash"], "F")
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}:{line}: {exc}") from exc
            methods[c].add(f)
    return methods


def rank_classes(methods: dict[int, set[int]],
                 known_c: dict[int, str], unknown_c: set[int],
                 known_f: dict[int, str], min_shared: int = 2,
                 top_k: int = 3) -> dict:
    if min_shared < 1 or top_k < 1:
        raise ValueError("min_shared and top_k must be positive")
    inverted: dict[int, set[int]] = defaultdict(set)
    for cls, funcs in methods.items():
        if cls in known_c:
            for fn in funcs:
                inverted[fn].add(cls)
    ranked = []
    for cls in sorted(unknown_c & methods.keys()):
        funcs = methods[cls]
        overlaps: dict[int, set[int]] = defaultdict(set)
        for fn in funcs:
            for peer in inverted.get(fn, ()):
                overlaps[peer].add(fn)
        neighbors = []
        for peer, shared in overlaps.items():
            if len(shared) < min_shared:
                continue
            # Rare methods contribute more; common Setup/Update-like keys
            # cannot dominate by frequency alone.
            weight = sum(1.0 / len(inverted[fn]) for fn in shared)
            name = known_c[peer]
            neighbors.append({
                "known_class_hash": f"0x{peer:016X}",
                "known_class_name": name,
                "known_namespace": name.rpartition(".")[0],
                "shared_F_count": len(shared),
                "shared_F_weight": round(weight, 6),
                "shared_F": [
                    {"hash": f"0x{fn:016X}", "name": known_f.get(fn)}
                    for fn in sorted(shared)
                ],
            })
        neighbors.sort(key=lambda x: (
            -x["shared_F_weight"], -x["shared_F_count"],
            x["known_class_name"], x["known_class_hash"]
        ))
        ranked.append({
            "unknown_class_hash": f"0x{cls:016X}",
            "direct_defined_F_count": len(funcs),
            "mapped_F_count": sum(fn in known_f for fn in funcs),
            "candidate_peer_count": len(neighbors),
            "nearest_named_classes": neighbors[:top_k],
            "evidence": "DIRECT_C_PROTOTYPE_F_ASSIGNMENTS_ONLY",
            "inference_limit": "Nearest named classes are leads, not original C names",
        })
    ranked.sort(key=lambda x: (
        not bool(x["nearest_named_classes"]),
        -(x["nearest_named_classes"][0]["shared_F_weight"]
          if x["nearest_named_classes"] else 0),
        -x["direct_defined_F_count"], x["unknown_class_hash"]
    ))
    return {
        "method": "inverse-frequency shared direct C.prototype[F] keys",
        "evidence_scope": "native Lua54 static closure assignment TSV",
        "limitations": [
            "No original name recovered by similarity",
            "No C-to-S or global registration association inferred",
            "No proof of runtime execution, inherited method, or target instance identity",
            "Missing strict 8-opcode assignment is not proof of absence",
        ],
        "direct_classes_in_tsv": len(methods),
        "known_C_with_direct_methods": len(methods.keys() & known_c.keys()),
        "unknown_C_in_hashlist": len(unknown_c),
        "unknown_C_with_direct_methods": len(unknown_c & methods.keys()),
        "unknown_C_without_direct_methods": len(unknown_c - methods.keys()),
        "unknown_C_with_ranked_peer": sum(bool(x["nearest_named_classes"]) for x in ranked),
        "min_shared": min_shared,
        "top_k": top_k,
        "records": ranked,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--assignments", type=Path, required=True,
                        help="Existing exact C->prototype->F TSV or TSV.gz")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-shared", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    unknown, known = load_hashlists(args.repo, "SV")
    methods = read_assignments(args.assignments)
    report = rank_classes(methods, known["C"], unknown["C"], known["F"],
                          min_shared=args.min_shared, top_k=args.top_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("records", "limitations")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
