# Scripts

## SV/ZA Lua hash verification and recovery

Python 3.10+, standard library only:

```powershell
python scripts/lua_hash.py calc SetCursorPos
python scripts/lua_hash.py verify
python scripts/lua_hash.py recover --numeric-radius 8
python scripts/lua_hash.py recover --dictionary my_names.txt --json-out report.json
python scripts/lua_hash.py recover --apply
python -m unittest discover -s tests -v
```

The script uses the verified nonstandard FNV-1a 64-bit basis `0xCBF29CE484222645`. It reads 8 Lua lists under SV and ZA, skips missing files, preserves existing names, and applies only unique 64-bit exact matches.

Read the Obsidian docs at [../docs/README.md](../docs/README.md). Do **not** use this algorithm for FileSystem hashes without separate proof.

## Trinity TRPAK internal paths

```powershell
python scripts/trinity_path_hash.py calc "avalon/data/personal_array.bin"
python scripts/trinity_path_hash.py verify ZA/Hashlists/FileSystem/hashes_inside_trpak.txt
python scripts/trinity_path_hash.py recover --targets unknown.txt --dictionary path_candidates.txt --output matched.tsv
```

Exact path bytes are required. Do not silently lowercase or normalize slashes. See [../docs/FileSystem-Hashes.md](../docs/FileSystem-Hashes.md).

## Cross-repository evidence merge verification (2026-11-05)

`python scripts/verify_sv_resources_import.py` validates 611 pinned ZA name/hash candidates, 4 SV F callbacks, their original source line numbers, independent evidence TSV, and all currently named SV/ZA Lua hashes without writing to hashlists. The exact pinned sources and provenance are under [`../docs/evidence/sv-resources/`](../docs/evidence/sv-resources/). See [`../docs/SV-Resources-Research-Sync-2026-11-05.md`](../docs/SV-Resources-Research-Sync-2026-11-05.md).

## SV unknown-C method-signature investigation

Export the proven direct assignment relationships from the original complete Lua 5.4 files, then rank unknown class hashes by uncommon method keys shared with already named classes:

~~~powershell
python scripts/trace_sv_lua_c2f.py "D:\SV\main.blua" "D:\SV\main_dynamic.blua" --repo . --game SV --assignments "c2f.tsv.gz"
python scripts/rank_sv_c_namespace.py --repo . --assignments "c2f.tsv.gz" --output "docs/local-sv-c-rank.json" --min-shared 2 --top-k 3
~~~

The ranking is **not** a name recovery, C-to-S proof, inheritance proof, or dynamic-call proof. Generated local report and original Lua files need not be committed. See [../docs/Lua-Next-Phase-2026-11-05.md](../docs/Lua-Next-Phase-2026-11-05.md).

## Pinned SV/ZA Lua investigation queues

`python scripts/build_native_lua_research_queue.py --check` verifies the exact 1,334-class SV native C inventory and 155 ZA unresolved S/F Haxe reference prioritization. It is read-only. The original evidence TSV and source commit SHAs are under `docs/evidence/lua-join-2026-11-05/`; `--write` regenerates only the three derived evidence files from those snapshots. No unknown names are written into Hashlists.


## SV 95 unknown-C native _ENV slot audit

The read-only [audit_sv_dual_global_slot.py](audit_sv_dual_global_slot.py) validates the 95 dual-structure C hashes against the original SV 4.0.0 `main.blua` (pinned SHA-256), including 95 registration writes, 252 S closure assignments, root upvalue 0, and closure child Prototype IDs. It never changes Lua Hashlists or claims runtime object identity.

The original Lua file and the `Analyze-SV-Lua54.py` parser are local inputs; do not check game binaries into the repository.

~~~powershell
python scripts/audit_sv_dual_global_slot.py --main "D:\SV\main.blua" --parser "D:\SV\Analyze-SV-Lua54.py" --static "D:\SV\followup-c-static-s-closures.tsv" --registrations "D:\SV\followup-c-global-registrations.tsv" --hashlist SV/Hashlists/Lua/lua_c_hashes.txt --out "D:\SV\audits"
~~~

See [../docs/Lua-Proto-Owner-Join-2026-11-05.md](../docs/Lua-Proto-Owner-Join-2026-11-05.md) for counts and limitations.
 
## SV / ZA high-throughput C++ brute-force name candidates

A bounded source-derived search (not generic 2^64 brute force) is implemented by [hash_bruteforce.cpp](hash_bruteforce.cpp). It verifies every pre-existing named hash, tests original namespace/class and Haxe nested `_Impl_` grammars, then ZA verb/CamelCase sequences. The source-guided H2 candidates are never applied automatically.

~~~bash
g++ -std=c++20 -O3 -DNDEBUG -pthread scripts/hash_bruteforce.cpp -o hash_bruteforce
./hash_bruteforce --repo . --mode sv --budget 300000000 --out sv
./hash_bruteforce --repo . --mode za --budget 300000000 --out za
python scripts/verify_hash_bruteforce.py --repo . --input-dir docs/evidence/hash-bruteforce-2026-11-05
~~~

For extended round two, add `--extended --budget 650000000` and both `--seed docs/evidence/hash-bruteforce-2026-11-05/sv-matches.tsv --seed docs/evidence/hash-bruteforce-2026-11-05/za-matches.tsv` to each game call. Seed files are *strictly rehashed* and act only as documented H2 grammar inputs, not native source strings. GitHub Actions run the CPU-intensive calculations and publish TSV/JSON to `docs/evidence/hash-bruteforce-2026-11-05/`.

See [the November 5th research audit](../docs/Lua-Hash-BruteForce-2026-11-05.md) and [the independent H2 validation](../docs/evidence/hash-bruteforce-2026-11-05/audit-summary.json). Do not confuse full-hash matches with original-name or receiver-type evidence.


The follow-up [trace_sv_factory_metatable.py](trace_sv_factory_metatable.py) proves the shared Lua table factory (root R15 / child Proto 19), its captured metatable R13, and exactly 95 `_ENV[C].__name__ = C` native metadata writes using the original SHA-pinned `main.blua`. It does **not** prove dynamic instance identity or readable class names. For local reproduction, use the same `--main`, `--parser`, `--registrations`, `--static` inputs, and pass the C hashlist as `--unknown` instead of `--hashlist`; output is supplied with `--out`. See [SV factory evidence](../docs/SV-Lua-Factory-Metatable-2026-11-05.md).


### ZA event-context batch and 28-entry H2 overlay

The event-specific third round is an optimized prefix-state FNV-1a search restricted to the `Ev_sys_megarematch` rebuilt Haxe context and five previously missing S targets:

~~~bash
g++ -std=c++20 -O3 -DNDEBUG scripts/brute_za_megarematch_context.cpp -o brute_za_megarematch
mkdir -p outputs
./brute_za_megarematch --out outputs/za-megarematch --budget 400000000
~~~

The reproducible H2-only overlay is derived from all five completed TSV batches (two rounds plus the ZA event-specific batch), and **never updates `SV/Hashlists/Lua` or `ZA/Hashlists/Lua`**:

~~~bash
python scripts/verify_hash_bruteforce_round2.py --repo . --out docs/evidence/hash-bruteforce-2026-11-05/round2-audit-summary.json
python scripts/build_lua_h2_overlay.py --repo .
python scripts/build_lua_h2_overlay.py --repo . --check
~~~

See [the 28-entry H2 overlay](../docs/evidence/hash-bruteforce-2026-11-05/h2-candidate-overlay.tsv) and [the entire study](../docs/Lua-Hash-BruteForce-2026-11-05.md). The third round actually evaluated **317,296,440** candidates; total across all three rounds was **1,167,121,655** candidate attempts (not distinct strings).
