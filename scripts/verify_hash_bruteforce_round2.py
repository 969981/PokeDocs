#!/usr/bin/env python3
"""Independently audit H2 seeded round two without granting H3 status.

Strictly rehash every stage-two row, require original Hashlist line to remain
empty and require all stage-one hits remain identical. No Hashlist writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from verify_hash_bruteforce import verify, fnv64, read_hashlist, records

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/hash-bruteforce-2026-11-05"


def run(root=ROOT, evidence=EVIDENCE):
    previous = verify(root, evidence)
    previous_map = {}
    for game in ("SV", "ZA"):
        for row in previous["games"][game]["items"]:
            previous_map[(game, row["kind"], row["hash"])] = row["name"]
    new = []
    searched = {}
    for short, game, kinds in (("sv", "SV", ("c",)), ("za", "ZA", ("s", "f"))):
        summary_path = evidence / f"{short}-round2-summary.json"
        matches_path = evidence / f"{short}-round2-matches.tsv"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        matches = records(matches_path)
        if (summary["mode"] != short or summary["budget_exhausted"] is not False or
                summary["exact_hash_matching_candidates"] != len(matches) or
                summary["target_unknown_hashes"] != (1334 if short == "sv" else 155)):
            raise ValueError("Seeded stage-2 manifest or budget does not agree")
        lists = {
            k: set(read_hashlist(root / game / "Hashlists/Lua" / f"lua_{k}_hashes.txt"))
            for k in kinds
        }
        seen = {}
        for row in matches:
            if row["game"] != game or row["kind"] not in kinds:
                raise ValueError("Stage-2 game/kind not allowed")
            label = row["candidate"]
            digest = row["hash"].replace("0X", "0x").upper().replace("0X", "0x")
            if fnv64(label) != int(digest, 16):
                raise ValueError("Stage-2 exact digest mismatch")
            if (int(row["line"]), digest, "") not in lists[row["kind"]]:
                raise ValueError("Stage-2 target does not match unmodified blank row")
            if digest in seen and seen[digest] != label:
                raise ValueError("Ambiguous H2 candidates under same digest")
            seen[digest] = label
            key = (game, row["kind"].upper(), digest)
            old = previous_map.get(key)
            if old is not None and old != label:
                raise ValueError("Stage-2 conflicted with stage-1 source-derived H2 string")
            if old is None:
                new.append({
                    "game": game,
                    "kind": row["kind"].upper(),
                    "line": int(row["line"]),
                    "hash": digest,
                    "candidate": label,
                    "method": row["method"],
                    "source_seed_or_word": row["prefix_source"],
                    "evidence_grade": "H2_SOURCE_DERIVED_EXACT_HASH_CANDIDATE",
                    "original_name_confirmed": False,
                })
        for (prior_game, prior_kind, prior_hash), name in previous_map.items():
            if prior_game == game and prior_hash not in seen:
                raise ValueError("Stage-2 failed to reproduce stage-1 matched Hash")
        searched[short] = {
            "attempted_candidates": summary["attempted_candidates"],
            "matches_including_stage1": len(matches),
            "additional_hits": sum(row["game"] == game for row in new),
            "input_summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
            "input_matches_sha256": hashlib.sha256(matches_path.read_bytes()).hexdigest(),
        }
    cumulative = sum(searched[k]["attempted_candidates"] for k in searched) + (
        json.loads((evidence / "sv-summary.json").read_text())["attempted_candidates"] +
        json.loads((evidence / "za-summary.json").read_text())["attempted_candidates"]
    )
    unique = len(previous_map)+len(new)
    return {
        "stage_one_exact_candidates": len(previous_map),
        "stage_two_new_exact_candidates": len(new),
        "total_unique_H2_exact_candidates": unique,
        "attempted_candidates_cumulative_with_repeated_grammars": cumulative,
        "stage_two": searched,
        "new_candidates": sorted(new, key=lambda x: (x["game"], x["kind"], x["hash"])),
        "official_hashlist_updates": 0,
        "H3_native_original_name_confirmations": 0,
        "note": (
            "All seeds are H2-only. Exhausted specified grammar is not an "
            "exhausted 64-bit preimage search. Later hypotheses are not original names."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.repo, args.evidence)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "total_unique_H2": result["total_unique_H2_exact_candidates"],
        "new_stage_two": result["stage_two_new_exact_candidates"],
        "candidates_computed": result["attempted_candidates_cumulative_with_repeated_grammars"],
        "name_recoveries_H3": 0, "hashlist_updates": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
