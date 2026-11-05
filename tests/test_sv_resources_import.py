"""Synthetic regression checks for provenance/hash/line guardrails."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lua_hash import lua_hash
from verify_sv_resources_import import verify_import


class EvidenceImportTests(unittest.TestCase):
    def fixture(self, base: Path):
        f = lambda s: f"0x{lua_hash(s):016X}"
        zf = base / "ZA/Hashlists/Lua/lua_f_hashes.txt"
        sf = base / "SV/Hashlists/Lua/lua_f_hashes.txt"
        zf.parent.mkdir(parents=True)
        sf.parent.mkdir(parents=True)
        zf.write_text(f( "TestAction" ) + " TestAction\n", encoding="utf-8")
        sf.write_text(f( "onTestChanged" ) + " onTestChanged\n", encoding="utf-8")
        folder = base / "docs/evidence/sv-resources"
        folder.mkdir(parents=True)
        def save(name, heads, rows):
            with (folder / name).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                writer.writerow(heads)
                writer.writerows(rows)
        zhash = f("TestAction")
        shash = "F" + f("onTestChanged")[2:]
        save("za-lua-recovered.tsv", ["kind", "hash", "candidate_name"],
             [["f", zhash, "TestAction"]])
        save("za-lua-source-line-index.tsv",
             ["kind", "hash", "candidate_name", "original_line", "source_sha",
              "evidence_grade", "reconstruction_path", "reconstruction_line"],
             [["f", zhash, "TestAction", "1", "old_sha",
               "SOURCE_CORROBORATED", "source/Test.hx", "9"]])
        save("za-lua-source-evidence.tsv",
             ["kind", "hash", "name", "original_line", "reconstruction_path",
              "reconstruction_line"],
             [["f", zhash, "TestAction", "1", "source/Test.hx", "9"]])
        save("sv-lua-f-new-exact-candidates.tsv",
             ["function_hash", "candidate_name", "exact_native_source_bindings"],
             [[shash, "onTestChanged", "1"]])
        save("sv-lua-f-native-bindings.tsv",
             ["target_hash", "candidate_name"], [[shash, "onTestChanged"]])
        return zf, sf, folder

    def test_valid_fixture(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.fixture(root)
            result = verify_import(root)
            self.assertEqual(result["za_candidates_validated"], 1)
            self.assertEqual(result["sv_native_context_candidates_validated"], 1)
            self.assertEqual(result["total_named_hash_rows"], 2)

    def test_line_move_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            _, _, folder = self.fixture(root)
            path = folder / "za-lua-source-line-index.tsv"
            path.write_text(path.read_text().replace("\t1\told_sha", "\t2\told_sha"))
            with self.assertRaisesRegex(ValueError, "original 1-based line"):
                verify_import(root)

    def test_wrong_name_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            zf, _, _ = self.fixture(root)
            zf.write_text(zf.read_text().replace("TestAction", "WrongName"))
            with self.assertRaises(ValueError):
                verify_import(root)


if __name__ == "__main__":
    unittest.main()
