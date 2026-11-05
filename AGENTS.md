# PokeDocs development conventions

1. Preserve original SV/ZA and other game's data layouts; do not reformat entire source hashlists.
2. Keep new analysis scripts in `scripts/`, tests in `tests/`, and Obsidian-compatible Markdown in `docs/`.
3. Every recovered Lua name must round-trip against the **complete 64-bit hash** with the verified variant and exact UTF-8 bytes.
4. Never infer a name just from adjacent hash values; numbers and prefixes are only **candidate generators**.
5. Only write a match if it is unique, exact, and has provenance. Record game, source file, original row/hash, candidate derivation, and verification method.
6. Keep ambiguous and unmatched values blank and describe failures without inventing names.
7. Distinguish Lua symbol hashes from GFPAK/FileSystem path hashes, archive hashes, 32-bit hashes, and binary cache formats.
8. Preserve evidence under `docs/`; use Obsidian `[[wiki links]]` and document unknowns.
9. Run `python -m unittest discover -s tests -v` and `python scripts/lua_hash.py verify` before committing hash changes.
10. Never auto-commit a speculative guess into a source hashlist; inspect generated reports first.
