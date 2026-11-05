#!/usr/bin/env python3
"""Audit source/bytecode evidence for unknown SV/ZA Lua hashes without guessing names.

Source strings/comments and binary encoded tokens are DIFFERENT evidence classes.
No original game files are altered, uploaded, or committed by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from lua_hash import lua_hash

HASH_ROW = re.compile(r"^0x([a-fA-F0-9]{16})(?:[ \t]+(.+))?[ \t]*$")
HEADER_ENTRY = re.compile(r'\{\s*"([CEFS])([0-9A-Fa-f]{16})"\s*,\s*"([^"]+)"\s*\}')
ANNOTATION = re.compile(r"^\s*---\s+([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)+)")
METHOD_DEF = re.compile(r"\bfunction\s+C([0-9A-Fa-f]{16})_prototype:F([0-9A-Fa-f]{16})\s*\(")
QUOTED_NAME = re.compile(r"""(["'])([a-zA-Z_][a-zA-Z_0-9]{0,127})\1""")
FUNCTION_NAME = re.compile(r"\bfunction\s+(?:[A-Za-z_][\w]*[.:])*([A-Za-z_][\w]*)\s*\(")
BYTECODE_TOKEN = re.compile(rb"(?<![A-Za-z0-9_])([CFSE])([0-9A-F]{16})(?![A-Za-z0-9_])")
KINDS = "cefs"
TEXT_SUFFIXES = {".lua", ".h"}


def load_targets(root: Path, game: str):
    unknown = {kind: set() for kind in KINDS}
    named = {kind: {} for kind in KINDS}
    for kind in KINDS:
        path = root / game / "Hashlists" / "Lua" / f"lua_{kind}_hashes.txt"
        with path.open(encoding="utf-8-sig") as src:
            for line_no, line in enumerate(src, 1):
                raw = line.rstrip("\r\n")
                item = HASH_ROW.fullmatch(raw)
                if not item:
                    if raw.strip():
                        raise ValueError(f"Malformed list {path}:{line_no}")
                    continue
                digest = int(item.group(1), 16)
                name = (item.group(2) or "").strip()
                if name:
                    if lua_hash(name) != digest:
                        raise ValueError(f"Invalid original mapping {path}:{line_no}")
                    named[kind][digest] = name
                else:
                    unknown[kind].add(digest)
    return unknown, named


def fingerprint(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scan_text(path: Path):
    """Yield (kind, hash, candidate, evidence_type, line)."""
    prior_annotation = None
    prior_line = -100
    with path.open(encoding="utf-8", errors="replace") as src:
        for no, line in enumerate(src, 1):
            for m in HEADER_ENTRY.finditer(line):
                yield m.group(1).lower(), int(m.group(2), 16), m.group(3), "historical_header_identity", no
            comment = ANNOTATION.search(line)
            if comment:
                prior_annotation = comment.group(1)
                prior_line = no
            meth = METHOD_DEF.search(line)
            if meth and prior_annotation and no - prior_line <= 3:
                c = prior_annotation.rsplit(".", 1)[0]
                f = prior_annotation.rsplit(".", 1)[1]
                yield "c", int(meth.group(1), 16), c, "editor_method_comment", no
                yield "f", int(meth.group(2), 16), f, "editor_method_comment", no
            for match in QUOTED_NAME.finditer(line):
                for kind in ("s", "f"):
                    yield kind, lua_hash(match.group(2)), match.group(2), "lua_string_literal", no
            for match in FUNCTION_NAME.finditer(line):
                for kind in ("f", "s"):
                    yield kind, lua_hash(match.group(1)), match.group(1), "lua_function_definition", no


def iter_sources(sources: list[Path]):
    visited = set()
    for location in sources:
        if location.is_file():
            paths = [location] if location.suffix.lower() in TEXT_SUFFIXES else []
        elif location.is_dir():
            paths = (p for p in location.rglob("*")
                     if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES)
        else:
            raise FileNotFoundError(location)
        for path in paths:
            resolved = path.resolve()
            if resolved not in visited:
                visited.add(resolved)
                yield resolved


def audit(root: Path, game: str, sources: list[Path], binaries: list[Path],
          source_version: str, max_files: int = 30000):
    targets, known = load_targets(root, game)
    hits = defaultdict(dict)
    conflicts = []
    sources_used = []
    text_count = 0

    for path in iter_sources(sources):
        text_count += 1
        if text_count > max_files:
            raise ValueError(f"Exceeded --max-files={max_files}")
        sha = fingerprint(path)
        sources_used.append({"path": str(path), "sha256": sha, "kind": "text"})
        for kind, digest, name, evidence, line in scan_text(path):
            if lua_hash(name) != digest:
                # A historical header/annotation can contain stale or corrupted names.
                continue
            if digest in targets[kind]:
                record = {"kind": kind, "hash": f"0x{digest:016X}", "name": name,
                          "evidence": evidence, "source": str(path), "line": line,
                          "source_sha256": sha, "version": source_version}
                hits[(kind, digest)][name] = record
            elif digest in known[kind] and known[kind][digest] != name:
                if evidence in ("historical_header_identity", "editor_method_comment"):
                    conflicts.append({"kind": kind, "hash": f"0x{digest:016X}",
                                      "existing": known[kind][digest], "historical": name,
                                      "source": str(path), "line": line})

    # Native raw bytecode presence alone has no candidate names.
    binary_presence = {}
    for path in binaries:
        if not path.is_file():
            raise FileNotFoundError(path)
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        found = defaultdict(list)
        for m in BYTECODE_TOKEN.finditer(data):
            kind = m.group(1).decode("ascii").lower()
            digest = int(m.group(2), 16)
            if digest in targets[kind]:
                found[(kind, digest)].append(m.start())
        binary_presence[str(path)] = {
            "sha256": sha, "bytes": len(data),
            "source_version": source_version,
            "raw_token_presence_only": True,
            "unknown_tokens": [
                {"kind": k, "hash": f"0x{d:016X}",
                 "occurrences": len(loc), "first_offset": loc[0]}
                for (k, d), loc in sorted(found.items())
            ],
        }
        sources_used.append({"path": str(path), "sha256": sha, "kind": "binary"})

    exact = []
    ambiguous = []
    for (kind, digest), names in sorted(hits.items()):
        if len(names) == 1:
            exact.append(next(iter(names.values())))
        else:
            ambiguous.append({"kind": kind, "hash": f"0x{digest:016X}",
                              "candidates": sorted(names)})
    return {
        "game": game, "source_version": source_version,
        "evidence": "HASH_EXACT_CANDIDATE, not runtime semantics",
        "limits": "Existing names never overwritten; binary raw token presence does not prove call or ownership.",
        "sources": sources_used,
        "unmapped_before": {kind: len(items) for kind, items in targets.items()},
        "new_exact_matches": exact, "ambiguous": ambiguous,
        "conflicting_historical_names": conflicts,
        "binary_presence": binary_presence,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--game", choices=("SV", "ZA"), default="SV")
    p.add_argument("--source", type=Path, action="append", default=[],
                   help="Lua source file/folder, or header data/lua_names.h (repeatable)")
    p.add_argument("--bytecode", type=Path, action="append", default=[],
                   help="Local raw .blua file for encoded hash presence (repeatable)")
    p.add_argument("--source-version", required=True,
                   help="Record exact source version; do not imply 3.0.1 is 4.0.0")
    p.add_argument("--max-files", type=int, default=30000)
    p.add_argument("--output", type=Path, help="Write complete JSON audit")
    p.add_argument("--names-out", type=Path, help="Write exact-match candidate dictionary")
    a = p.parse_args()
    if not a.source and not a.bytecode:
        p.error("Provide at least one --source or --bytecode")
    if a.max_files < 1:
        p.error("--max-files must be >= 1")
    report = audit(a.root, a.game, a.source, a.bytecode, a.source_version, a.max_files)
    print(json.dumps({
        "game": a.game,
        "exact_matches": len(report["new_exact_matches"]),
        "ambiguous": len(report["ambiguous"]),
        "historical_conflicts": len(report["conflicting_historical_names"]),
        "binary_unknown_tokens": sum(len(x["unknown_tokens"]) for x in report["binary_presence"].values()),
    }, ensure_ascii=False))
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.names_out:
        a.names_out.parent.mkdir(parents=True, exist_ok=True)
        a.names_out.write_text("\n".join(x["name"] for x in report["new_exact_matches"]) + "\n",
                               encoding="utf-8")


if __name__ == "__main__":
    main()
