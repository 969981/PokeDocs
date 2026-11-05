#!/usr/bin/env python3
"""Read-only verification of the pinned SV_Resources Lua evidence imported into PokeDocs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from lua_hash import HASH_LINE, known_symbols, lua_hash, symbol_lines


def normalize_hash(value: str) -> str:
    return f"0x{int(value, 16):016X}"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def row_lookup(root: Path, game: str, kind: str, cache: dict) -> dict[str, tuple[int, str]]:
    key = (game, kind)
    if key not in cache:
        path = root / game / "Hashlists" / "Lua" / f"lua_{kind}_hashes.txt"
        result = {}
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = HASH_LINE.fullmatch(raw)
            if not match:
                raise ValueError(f"Malformed source row {path}:{line_no}")
            digest = normalize_hash(match.group(1))
            if digest in result:
                raise ValueError(f"Duplicate hash in {path}: {digest}")
            result[digest] = (line_no, match.group(3).strip())
        cache[key] = result
    return cache[key]


def verify_import(root: Path) -> dict:
    root = root.resolve()
    evidence = root / "docs" / "evidence" / "sv-resources"
    za = read_tsv(evidence / "za-lua-recovered.tsv")
    idx = read_tsv(evidence / "za-lua-source-line-index.tsv")
    src = read_tsv(evidence / "za-lua-source-evidence.tsv")
    sv = read_tsv(evidence / "sv-lua-f-new-exact-candidates.tsv")
    bindings = read_tsv(evidence / "sv-lua-f-native-bindings.tsv")
    indexed = {(x["kind"], normalize_hash(x["hash"])): x for x in idx}
    sources = {(x["kind"], normalize_hash(x["hash"])): x for x in src}
    if len(indexed) != len(idx) or len(sources) != len(src):
        raise ValueError("Duplicate ZA evidence row")
    cache = {}
    seen = set()
    corroborated = 0
    for item in za:
        kind, digest, name = item["kind"], normalize_hash(item["hash"]), item["candidate_name"]
        key = (kind, digest)
        if kind not in ("f", "s") or key in seen:
            raise ValueError(f"Unexpected or duplicated ZA row: {key}")
        seen.add(key)
        if f"0x{lua_hash(name):016X}" != digest:
            raise ValueError(f"ZA hash does not match candidate: {key} {name}")
        row = row_lookup(root, "ZA", kind, cache).get(digest)
        if row is None or row[1] != name:
            raise ValueError(f"ZA canonical mapping missing or mismatched: {key}")
        reference = indexed.get(key)
        if reference is None or reference["candidate_name"] != name:
            raise ValueError(f"ZA source-line index missing: {key}")
        if int(reference["original_line"]) != row[0]:
            raise ValueError(f"ZA original 1-based line changed: {key}")
        if reference["evidence_grade"] == "SOURCE_CORROBORATED":
            corroborated += 1
            source = sources.get(key)
            if source is None or source["name"] != name:
                raise ValueError(f"ZA Haxe source evidence missing: {key}")
            for source_col, index_col in (("original_line", "original_line"),
                                          ("reconstruction_path", "reconstruction_path"),
                                          ("reconstruction_line", "reconstruction_line")):
                if source[source_col] != reference[index_col]:
                    raise ValueError(f"ZA source provenance mismatch: {key} {source_col}")
        elif reference["evidence_grade"] != "HASH_EXACT_CANDIDATE":
            raise ValueError(f"Unknown evidence grade for ZA {key}")
    if set(indexed) != seen or set(sources) != {key for key in seen if indexed[key]["evidence_grade"] == "SOURCE_CORROBORATED"}:
        raise ValueError("ZA source files contain missing or unexpected evidence keys")
    bind_lookup = {}
    for b in bindings:
        bind_lookup.setdefault((b["target_hash"].upper(), b["candidate_name"]), []).append(b)
    sv_seen = set()
    for item in sv:
        token, name = item["function_hash"].upper(), item["candidate_name"]
        if len(token) != 17 or token[0] != "F":
            raise ValueError(f"Malformed F token: {token}")
        digest = "0x" + token[1:]
        if token in sv_seen or f"0x{lua_hash(name):016X}" != digest:
            raise ValueError(f"SV F hash conflict: {token} {name}")
        sv_seen.add(token)
        row = row_lookup(root, "SV", "f", cache).get(digest)
        if row is None or row[1] != name:
            raise ValueError(f"SV F canonical mapping missing or mismatched: {token}")
        if len(bind_lookup.get((token, name), ())) != int(item["exact_native_source_bindings"]):
            raise ValueError(f"SV native bytecode source-binding count mismatch: {token}")
    entries = list(symbol_lines(root))
    _, invalid = known_symbols(entries)
    if invalid:
        raise ValueError(f"Invalid existing hash names: {invalid[:3]}")
    remaining = {}
    for path, _, _, name in entries:
        if not name:
            key = f"{path.relative_to(root).parts[0]}/{path.stem}"
            remaining[key] = remaining.get(key, 0) + 1
    report_file = evidence / "import-report-2026-11-05.json"
    if report_file.exists():
        expected = json.loads(report_file.read_text(encoding="utf-8"))
        if len(za) != expected["za"]["candidates"] or corroborated != expected["za"]["source_corrob"]:
            raise ValueError("ZA source snapshot counts differ from import report")
        if len(sv) != expected["sv"]["new_native_correlated_f"]:
            raise ValueError("SV source snapshot counts differ from import report")
    return {"za_candidates_validated": len(za), "za_haxe_correlated": corroborated,
            "sv_native_context_candidates_validated": len(sv),
            "total_named_hash_rows": sum(bool(x[3]) for x in entries),
            "total_remaining_unknown": sum(remaining.values()),
            "unknown_by_table": dict(sorted(remaining.items())),
            "invalid_named_hashes": len(invalid)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = verify_import(args.root)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Evidence validation failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
