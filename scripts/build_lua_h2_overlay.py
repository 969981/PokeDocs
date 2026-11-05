#!/usr/bin/env python3
"""Build a safe H2 candidate *overlay* without modifying Lua Hashlists.

Merges three completed source-grammar searches (two wide rounds + one event-
specific round); recomputes full 64-bit FNV, requires current blank target row,
rejects any colliding candidate, joins pinned native context, emits deterministic
TSV/JSON. H2 is NOT a recovered original native Lua source identifier.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/evidence/hash-bruteforce-2026-11-05"
SOURCES = ("sv-matches.tsv", "za-matches.tsv",
           "sv-round2-matches.tsv", "za-round2-matches.tsv",
           "za-megarematch-matches.tsv")
COLS = (
    "game", "kind", "hash", "lua_token", "candidate_name", "evidence_grade",
    "first_matched_stage", "matching_stages", "candidate_grammar",
    "native_structure", "native_opcode_refs", "native_C_to_S_edges",
    "native_global_reg_edges", "native_original_name_confirmed",
    "hashlist_updated",
)


def fnv64(source: str) -> int:
    h = 0xCBF29CE484222645
    for b in source.encode("utf-8"):
        h = ((h ^ b) * 0x100000001B3) & ((1 << 64) - 1)
    return h


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def original_rows(root, game, kind):
    path = root / game / "Hashlists/Lua" / f"lua_{kind.lower()}_hashes.txt"
    data = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        cols = raw.split(maxsplit=1)
        if not cols:
            continue
        if len(cols[0]) != 18 or cols[0][:2].lower() != "0x":
            raise ValueError(f"Malformed hashlist line: {path}:{line_no}")
        digest = int(cols[0][2:], 16)
        name = cols[1].strip() if len(cols) > 1 else ""
        if name and fnv64(name) != digest:
            raise ValueError(f"Existing named hash mismatch: {path}:{line_no}")
        data[line_no] = (digest, name)
    return data


def generate(root=ROOT, evidence=BASE):
    manifest_hashes = {
        src: hashlib.sha256((evidence / src).read_bytes()).hexdigest()
        for src in SOURCES
    }
    catalog = {}
    for stage, filename in enumerate(SOURCES, 1):
        for item in rows(evidence / filename):
            game, kind = item["game"], item["kind"].upper()
            digest = int(item["hash"], 16)
            name = item.get("candidate") or item.get("candidate_name")
            if game not in ("SV", "ZA") or kind not in ("C", "F", "S"):
                raise ValueError(f"Unexpected target game/kind: {game} {kind}")
            if game == "SV" and kind != "C":
                raise ValueError("Only SV C target expected")
            if fnv64(name) != digest:
                raise ValueError(f"64-bit candidate failed: {name}")
            key = (game, kind, digest)
            existing = catalog.get(key)
            method = item.get("method") or item.get("evidence") or "unknown"
            if existing:
                if existing["candidate_name"] != name:
                    raise ValueError(f"Conflicting H2 candidates for {key}")
                existing["matching_stages"].append(filename)
            else:
                catalog[key] = {
                    "game": game, "kind": kind, "hash": f"0x{digest:016X}",
                    "lua_token": f"{kind}{digest:016X}", "candidate_name": name,
                    "evidence_grade": "H2_EXACT_64BIT_HASH_SOURCE_GRAMMAR",
                    "first_matched_stage": filename,
                    "matching_stages": [filename],
                    "candidate_grammar": method,
                    "native_original_name_confirmed": "NO",
                    "hashlist_updated": "NO",
                    "original_line": int(item["line"]),
                }
    if (len(catalog) != 28 or
            Counter((x["game"], x["kind"]) for x in catalog.values())
            != Counter({("SV","C"):12,("ZA","S"):10,("ZA","F"):6})):
        raise ValueError("Pinned 28-candidate H2 baseline changed")

    context_sv = {
        x["hash"].upper().replace("0X", "0x"): x
        for x in rows(root / "docs/evidence/lua-join-2026-11-05/sv-native-class-queue.tsv")
    }
    context_za = {
        (x["kind"].upper(), x["hash"].upper().replace("0X", "0x")): x
        for x in rows(root / "docs/evidence/lua-closure-2026-11-05/za-current-155.tsv")
    }
    list_cache = {}
    for item in catalog.values():
        game, kind, h = item["game"], item["kind"], item["hash"]
        list_key = (game, kind)
        if list_key not in list_cache:
            list_cache[list_key] = original_rows(root, game, kind)
        digest, name = list_cache[list_key].get(item["original_line"], (None, None))
        if digest != int(h, 16) or name != "":
            raise ValueError(f"Candidate does not refer to an unchanged blank row: {game}/{kind}/{item['original_line']}")
        if game == "SV":
            source = context_sv.get(h)
            if source is None:
                raise ValueError(f"Unknown SV C native evidence key: {h}")
            item["native_structure"] = source["status"]
            item["native_opcode_refs"] = ""
            item["native_C_to_S_edges"] = source["static_S_count"]
            item["native_global_reg_edges"] = source["global_reg_count"]
        else:
            source = context_za.get((kind, h))
            if source is None:
                raise ValueError(f"Unknown ZA native evidence key: {kind} {h}")
            item["native_structure"] = ("NO_INDEXED_NATIVE_OPCODE" if
                int(source["native_opcode_references"]) == 0 else "NATIVE_OPCODE_REFERENCE_ONLY")
            item["native_opcode_refs"] = source["native_opcode_references"]
            item["native_C_to_S_edges"] = source["native_C_to_S_closure_edges"]
            item["native_global_reg_edges"] = ""

    ordered = sorted(catalog.values(), key=lambda x: (x["game"], x["kind"], x["hash"]))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLS, delimiter="\t",
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in ordered:
        writer.writerow({**row, "matching_stages": ";".join(row["matching_stages"])})
    tsv = out.getvalue()
    summary = {
        "evidence": "H2_SOURCE_DERIVED_EXACT_HASH_CANDIDATE_NOT_NATIVE_NAME",
        "source_file_sha256": manifest_hashes,
        "unique_candidates": len(ordered),
        "by_game_kind": {f"{key[0]}_{key[1]}": value
                         for key, value in sorted(Counter((x["game"], x["kind"]) for x in ordered).items())},
        "ZA_without_current_native_opcode": [
            row["lua_token"] for row in ordered if row["game"] == "ZA"
            and row["native_structure"] == "NO_INDEXED_NATIVE_OPCODE"
        ],
        "overlay_sha256": hashlib.sha256(tsv.encode("utf-8")).hexdigest(),
        "native_original_names_confirmed": 0,
        "official_hashlist_updates": 0,
        "warnings": ["Overlay does not overwrite upstream PokeDocs Hashlists.",
                     "A full FNV-1a 64-bit candidate match is H2, not proof of original source identity.",
                     "ZA current opcode absence reflects only the existing pinned four native Lua packs."],
    }
    return tsv, json.dumps(summary, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--evidence", type=Path, default=BASE)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tsv, summary = generate(a.repo, a.evidence)
    target_tsv = a.evidence / "h2-candidate-overlay.tsv"
    target_summary = a.evidence / "h2-overlay-summary.json"
    if a.check:
        if (not target_tsv.exists() or target_tsv.read_text(encoding="utf-8") != tsv or
                not target_summary.exists() or target_summary.read_text(encoding="utf-8") != summary):
            raise SystemExit("H2 overlay evidence drift, rebuild and review")
    else:
        a.evidence.mkdir(parents=True, exist_ok=True)
        target_tsv.write_text(tsv, encoding="utf-8")
        target_summary.write_text(summary, encoding="utf-8")
    print(json.dumps({"unique_candidates": 28, "formal_updates": 0,
                      "original_names": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
