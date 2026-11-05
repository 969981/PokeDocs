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
