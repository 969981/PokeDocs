#!/usr/bin/env python3
"""Verify and recover SV/ZA Lua names using the proven 64-bit Game Freak hash."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

OFFSET_BASIS = 0xCBF29CE484222645
FNV_PRIME = 0x100000001B3
MASK = (1 << 64) - 1
KINDS = ("c", "e", "f", "s")
HASH_LINE = re.compile(r"(0x[0-9a-fA-F]{16})([ \t]*)(.*)")
DIGITS = re.compile(r"\d+")


def lua_hash(name: str) -> int:
    """UTF-8 FNV-1a 64-bit with the Lua-table offset basis."""
    value = OFFSET_BASIS
    for byte in name.encode("utf-8"):
        value = ((value ^ byte) * FNV_PRIME) & MASK
    return value


def symbol_lines(root: Path):
    """Yield (path, 1-based line, hash, name), including hashes lacking a space."""
    for game in ("SV", "ZA"):
        for kind in KINDS:
            path = root / game / "Hashlists" / "Lua" / f"lua_{kind}_hashes.txt"
            if not path.exists():
                continue
            for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                match = HASH_LINE.fullmatch(raw.rstrip("\r\n"))
                if match:
                    yield path, number, int(match.group(1), 16), match.group(3).strip()


def known_symbols(entries):
    by_hash = defaultdict(set)
    invalid = []
    for path, number, expected, name in entries:
        if not name:
            continue
        actual = lua_hash(name)
        if actual == expected:
            by_hash[expected].add(name)
        else:
            invalid.append((str(path), number, f"0x{expected:016X}", name, f"0x{actual:016X}"))
    return by_hash, invalid


def derived_names(name: str, radius: int):
    """Produce bounded, one-change-at-a-time candidates; never infer semantics."""
    for match in list(DIGITS.finditer(name))[:4]:
        token = match.group()
        if len(token) > 4:
            continue
        number = int(token)
        for delta in range(-radius, radius + 1):
            next_number = number + delta
            if delta and 0 <= next_number <= 9999:
                yield (name[:match.start()] + str(next_number).zfill(len(token))
                       + name[match.end():], "numeric")
    if name.startswith("get_"):
        yield "set_" + name[4:], "prefix"
    if name.startswith("set_"):
        yield "get_" + name[4:], "prefix"
    if name.startswith("Is"):
        yield "Get" + name[2:], "prefix"
    if name.startswith("Get"):
        yield "Set" + name[3:], "prefix"
        yield "Is" + name[3:], "prefix"
    if name.startswith("Set"):
        yield "Get" + name[3:], "prefix"
    if name.startswith("on"):
        yield "On" + name[2:], "case"
    if name.startswith("On"):
        yield "on" + name[2:], "case"


def recover(root: Path, radius: int, dictionaries: list[Path]):
    entries = list(symbol_lines(root))
    named, invalid = known_symbols(entries)
    if invalid:
        raise ValueError(f"Existing names have mismatched hashes: {invalid[:5]}")
    targets = defaultdict(list)
    for path, number, digest, name in entries:
        if not name:
            targets[digest].append({"path": path.relative_to(root).as_posix(), "line": number})
    found = defaultdict(dict)

    def offer(name: str, method: str, source: str):
        digest = lua_hash(name)
        if digest in targets and name not in found[digest]:
            found[digest][name] = {"method": method, "source": source}

    for digest in targets:
        for name in named.get(digest, ()):
            offer(name, "cross-hashlist", "existing verified name")
    all_names = set().union(*named.values()) if named else set()
    for name in sorted(all_names):
        for candidate, method in derived_names(name, radius):
            if candidate not in all_names:
                offer(candidate, method, name)
    for path in dictionaries:
        for raw in path.read_text(encoding="utf-8").splitlines():
            candidate = raw.strip()
            if candidate and not candidate.startswith("#"):
                offer(candidate, "dictionary", str(path))
    ambiguous = {f"0x{digest:016X}": sorted(names)
                 for digest, names in found.items() if len(names) > 1}
    records = []
    for digest in sorted(found):
        if len(found[digest]) != 1:
            continue
        name, evidence = next(iter(found[digest].items()))
        records.append({"hash": f"0x{digest:016X}", "name": name,
                        **evidence, "locations": targets[digest]})
    return entries, targets, records, ambiguous


def apply_recovery(root: Path, records: list[dict]) -> int:
    mapping = {int(record["hash"], 16): record["name"] for record in records}
    changed = 0
    for game in ("SV", "ZA"):
        for kind in KINDS:
            path = root / game / "Hashlists" / "Lua" / f"lua_{kind}_hashes.txt"
            if not path.exists():
                continue
            original = path.read_text(encoding="utf-8")
            updated = []
            for raw in original.splitlines(keepends=True):
                body = raw.rstrip("\r\n")
                eol = raw[len(body):]
                match = HASH_LINE.fullmatch(body)
                if match and not match.group(3).strip():
                    digest = int(match.group(1), 16)
                    if digest in mapping:
                        raw = match.group(1) + (match.group(2) or " ") + mapping[digest] + eol
                        changed += 1
                updated.append(raw)
            result = "".join(updated)
            if result != original:
                path.write_text(result, encoding="utf-8", newline="")
    return changed


def markdown_report(entries, targets, records, ambiguous):
    filled = sum(len(r["locations"]) for r in records)
    lines = ["# Lua Hash 恢复报告", "",
             "> [!NOTE] 完整 Hash 匹配只证明候选字符串匹配，不自动证明游戏内语义。", "",
             f"- 初始空白行：{sum(map(len, targets.values()))}",
             f"- 唯一匹配 Hash：{len(records)}",
             f"- 可回填行：{filled}",
             f"- 尚未匹配行：{sum(map(len, targets.values())) - filled}",
             f"- 歧义 Hash：{len(ambiguous)}", "",
             "| Hash | 名称 | 策略 | 来源 | 文件位置 |",
             "| --- | --- | --- | --- | --- |"]
    for r in records:
        locations = ", ".join(f"\`{v['path']}:{v['line']}\`" for v in r["locations"])
        lines.append(f"| \`{r['hash']}\` | \`{r['name']}\` | {r['method']} | "
                     f"\`{r['source']}\` | {locations} |")
    if ambiguous:
        lines += ["", "## 歧义（不回填）", "", "\`\`\`json",
                  json.dumps(ambiguous, indent=2, ensure_ascii=False), "\`\`\`"]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    calc = commands.add_parser("calc", help="Calculate hash for exact (case-sensitive) symbol")
    calc.add_argument("names", nargs="+")
    commands.add_parser("verify", help="Validate all currently named Lua hashes")
    recovery = commands.add_parser("recover", help="Match unknown hashes with documented candidates")
    recovery.add_argument("--numeric-radius", type=int, default=8)
    recovery.add_argument("--dictionary", action="append", type=Path, default=[])
    recovery.add_argument("--apply", action="store_true")
    recovery.add_argument("--markdown-out", type=Path)
    recovery.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    if args.command == "calc":
        for name in args.names:
            print(f"0x{lua_hash(name):016X} {name}")
    elif args.command == "verify":
        entries = list(symbol_lines(args.root))
        _, invalid = known_symbols(entries)
        print(f"Validated {sum(bool(e[3]) for e in entries)} names; mismatches: {len(invalid)}")
        for issue in invalid[:20]:
            print(*issue, sep=" | ")
        if invalid:
            raise SystemExit(1)
    else:
        if not 0 <= args.numeric_radius <= 100:
            parser.error("--numeric-radius must be 0..100")
        entries, targets, records, ambiguous = recover(
            args.root, args.numeric_radius, args.dictionary)
        print(f"Blanks: {sum(map(len, targets.values()))}; unique matches: {len(records)}; "
              f"matched rows: {sum(len(x['locations']) for x in records)}; "
              f"ambiguous: {len(ambiguous)}")
        if args.markdown_out:
            args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
            args.markdown_out.write_text(markdown_report(entries, targets, records, ambiguous),
                                         encoding="utf-8")
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps({"matches": records, "ambiguous": ambiguous},
                                                indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
        if args.apply:
            print(f"Filled {apply_recovery(args.root, records)} rows")


if __name__ == "__main__":
    main()
