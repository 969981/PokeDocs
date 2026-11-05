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

The follow-up [trace_sv_factory_metatable.py](trace_sv_factory_metatable.py) proves the shared Lua table factory (root R15 / child Proto 19), its captured metatable R13, and exactly 95 `_ENV[C].__name__ = C` native metadata writes using the original SHA-pinned `main.blua`. It does **not** prove dynamic instance identity or readable class names. For local reproduction, use the same `--main`, `--parser`, `--registrations`, `--static` inputs, and pass the C hashlist as `--unknown` instead of `--hashlist`; output is supplied with `--out`. See [SV factory evidence](../docs/SV-Lua-Factory-Metatable-2026-11-05.md).
