#!/usr/bin/env python3
"""Calculate/verify raw Trinity TRPAK-internal resource-path hashes."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from lua_hash import lua_hash

ROW = re.compile(r"^0x([0-9a-fA-F]{16})(?:[ \t]+(.+))?$")


def entries(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        for number, raw in enumerate(stream, 1):
            match = ROW.fullmatch(raw.rstrip("\r\n"))
            if match:
                yield number, int(match.group(1), 16), (match.group(2) or "").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    calc = commands.add_parser("calc", help="Hash exact UTF-8 paths (no normalization)")
    calc.add_argument("paths", nargs="+")
    verify = commands.add_parser("verify", help="Verify lines formatted as '0xHASH path'")
    verify.add_argument("input", type=Path)
    recover = commands.add_parser("recover", help="Match hash-only targets against candidate paths")
    recover.add_argument("--targets", type=Path, required=True)
    recover.add_argument("--dictionary", type=Path, required=True)
    recover.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.command == "calc":
        for path in args.paths:
            print(f"0x{lua_hash(path):016X} {path}")
    elif args.command == "verify":
        total = bad = 0
        for line, expected, path in entries(args.input):
            if not path:
                continue
            total += 1
            actual = lua_hash(path)
            if actual != expected:
                bad += 1
                if bad <= 20:
                    print(f"{args.input}:{line}: 0x{expected:016X} != 0x{actual:016X} {path}")
        print(f"Verified {total} named paths; mismatches: {bad}")
        if total == 0 or bad:
            raise SystemExit(1)
    else:
        targets = {digest for _, digest, name in entries(args.targets) if not name}
        found: dict[int, set[str]] = {}
        with args.dictionary.open(encoding="utf-8-sig") as stream:
            for raw in stream:
                path = raw.strip()
                if path and not path.startswith("#"):
                    digest = lua_hash(path)
                    if digest in targets:
                        found.setdefault(digest, set()).add(path)
        unique = [(digest, next(iter(names))) for digest, names in sorted(found.items())
                  if len(names) == 1]
        ambiguous = sum(len(names) > 1 for names in found.values())
        print(f"Target hashes: {len(targets)}; exact matches: {len(unique)}; ambiguous: {ambiguous}")
        output = "\n".join(f"0x{digest:016X}\t{path}" for digest, path in unique)
        if output:
            output += "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")


if __name__ == "__main__":
    main()
