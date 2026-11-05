#!/usr/bin/env python3
"""Independently verify generated H2 SV/ZA candidate names and native evidence.

The C++ generator is not trusted as its own validator. This Python script
checks every candidate against the original blank hashlist line and recomputes
FNV-1a 64-bit independently. It does not modify any hashlist or promote H2
names to native-original H3.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/hash-bruteforce-2026-11-05"
HEX = re.compile(r"0x[0-9A-Fa-f]{16}\Z")


def fnv64(name: str) -> int:
    value = 0xCBF29CE484222645
    for ch in name.encode("utf-8"):
        value ^= ch
        value = value * 0x100000001B3 & 0xFFFFFFFFFFFFFFFF
    return value


def records(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_hashlist(path):
    names = []
    for i, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        digest = parts[0]
        if not HEX.fullmatch(digest):
            raise ValueError(f"Malformed current Hashlist {path}:{i}")
        name = parts[1].strip() if len(parts) > 1 else ""
        if name and fnv64(name) != int(digest, 16):
            raise ValueError(f"Existing Hashlist name disagrees with raw 64-bit hash: {path}:{i}")
        names.append((i, digest.upper().replace("0X", "0x"), name))
    return names


def verify(root=ROOT, out=OUTPUT):
    manifests = {f"{game}/{kind}": root / game / "Hashlists/Lua" / f"lua_{kind}_hashes.txt"
                 for game in ("SV", "ZA") for kind in ("c", "e", "f", "s")}
    lists = {key: read_hashlist(path) for key, path in manifests.items()}
    paths = {key: hashlib.sha256(path.read_bytes()).hexdigest()
             for key, path in manifests.items()}
    context = {
        "SV": {x["hash"].upper().replace("0X", "0x"): x
               for x in records(root / "docs/evidence/lua-join-2026-11-05/sv-native-class-queue.tsv")},
        "ZA": {(x["kind"].lower(), x["hash"].upper().replace("0X", "0x")): x
               for x in records(root / "docs/evidence/lua-closure-2026-11-05/za-current-155.tsv")},
    }
    results = {}
    for game in ("sv", "za"):
        stats = json.loads((out / f"{game}-summary.json").read_text(encoding="utf-8"))
        hits = records(out / f"{game}-matches.tsv")
        expected = {"sv": (1334, "SV"), "za": (155, "ZA")}
        target_count, title = expected[game]
        if stats.get("target_unknown_hashes") != target_count:
            raise ValueError(f"Target baseline changed: {game}")
        if stats.get("budget_exhausted") is not False:
            raise ValueError(f"Enumeration budget exhausted: {game}")
        if stats.get("exact_hash_matching_candidates") != len(hits):
            raise ValueError(f"Match manifest count inconsistent: {game}")
        found_hashes = set()
        items = []
        for record in hits:
            kind = record["kind"]
            if record["game"] != title or kind not in (("c",) if game == "sv" else ("s", "f")):
                raise ValueError("Mismatched game/kind candidate")
            path = f"{title}/{kind}"
            raw = record["hash"]
            key = raw.upper().replace("0X", "0x")
            name = record["candidate"]
            if not HEX.fullmatch(raw) or fnv64(name) != int(raw, 16):
                raise ValueError(f"Candidate hash verification FAILED: {name}")
            if not record["method"] or not record["prefix_source"] or not record["leaf_or_stem_source"]:
                raise ValueError("Missing candidate generation provenance")
            index = int(record["line"])
            if (index, key, "") not in lists[path]:
                raise ValueError(f"Previously unknown target changed or row does not match: {path}:{index}")
            if key in found_hashes:
                raise ValueError(f"Multiple candidate names for one hash require manual adjudication: {key}")
            found_hashes.add(key)
            native = (context["SV"].get(key) if game == "sv"
                      else context["ZA"].get((kind, key)))
            if native is None:
                raise ValueError(f"No pinned native evidence baseline row for {title} {key}")
            item = {
                "kind": kind.upper(), "line": index, "hash": key,
                "name": name, "method": record["method"],
                "source_a": record["prefix_source"],
                "source_b": record["leaf_or_stem_source"],
                "evidence_grade": "H2_EXACT_HASH_SOURCE_GRAMMAR_CANDIDATE",
                "native_original_name_confirmed": False,
                "receiver_identity_confirmed": False,
            }
            if game == "sv":
                item["native_class_status"] = native["status"]
                item["native_static_S_edges"] = int(native["static_S_count"])
                item["native_global_registration_edges"] = int(native["global_reg_count"])
            else:
                item["native_opcode_references"] = int(native["native_opcode_references"])
                item["native_C_to_S_closure_edges"] = int(native["native_C_to_S_closure_edges"])
                item["native_adjacent_call_edges"] = int(native["adjacent_field_call_edges"])
            items.append(item)
        results[game.upper()] = {
            "exact_hash_matches": len(items),
            "unknown_baseline_count": target_count,
            "would_remain_if_all_H2_were_separately_accepted": target_count-len(items),
            "grade": "H2_CANDIDATE_NOT_NATIVE_ORIGINAL_NAME",
            "items": items,
        }
    return {
        "source_hashlists_sha256": paths,
        "total_independently_verified_exact_candidates": sum(
            v["exact_hash_matches"] for v in results.values()),
        "source_repositories": {
            "SV": "969981/PokeDocs develop + SV_Resources native evidence",
            "ZA": "969981/PokeDocs develop + ZA_Resources native opcode evidence",
        },
        "games": results,
        "formal_hashlist_updates": 0,
        "native_original_names_confirmed": 0,
        "warning": (
            "Exact 64-bit source-derived names are H2 candidates. "
            "No source string identity or native receiver confirmation; "
            "all existing hashlist empty rows stay empty."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--input-dir", type=Path, default=OUTPUT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = verify(args.repo, args.input_dir)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidates": result["total_independently_verified_exact_candidates"],
        "SV_C": result["games"]["SV"]["exact_hash_matches"],
        "ZA_S": sum(x["kind"] == "S" for x in result["games"]["ZA"]["items"]),
        "ZA_F": sum(x["kind"] == "F" for x in result["games"]["ZA"]["items"]),
        "native_original_names_confirmed": 0,
        "hashlist_updates": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
