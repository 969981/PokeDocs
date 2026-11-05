"""Synthetic known-vector tests for bounded source-guided Lua hash brute-force.

Compiles C++ locally in CI. Does not download any game bytecode.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/hash_bruteforce.cpp"
BASIS = 0xCBF29CE484222645
PRIME = 0x100000001B3


def hash_name(name):
    h = BASIS
    for b in name.encode("utf-8"):
        h = ((h ^ b) * PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


class HashBruteforceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("g++"):
            raise unittest.SkipTest("g++ required")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.tmp.name) / "hash_bruteforce"
        subprocess.run(["g++", "-std=c++20", "-O2", str(SOURCE),
                        "-o", str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tmp"):
            cls.tmp.cleanup()

    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(self.sandbox.cleanup)
        self.repo = Path(self.sandbox.name)
        entries = {
            ("SV", "c"): [("main.fake.KnownData", True),
                          ("main.fake.HelperController", True),
                          ("main.fake.KnownManager", False)],
            ("ZA", "c"): [("event_ik.SampleController", True)],
            ("ZA", "s"): [("GetRequest", True), ("SetRequest", False)],
            ("ZA", "f"): [("ExecuteRequest", False)],
        }
        for game in ("SV", "ZA"):
            for kind in ("c", "e", "f", "s"):
                p = self.repo / game / "Hashlists" / "Lua" / f"lua_{kind}_hashes.txt"
                p.parent.mkdir(parents=True, exist_ok=True)
                lines = [
                    f"0x{hash_name(name):016X} {name if named else ''}"
                    for name, named in entries.get((game, kind), [])
                ]
                p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_mode(self, mode):
        prefix = self.repo / "out"
        cmd = [str(self.binary), "--repo", str(self.repo),
               "--mode", mode, "--out", str(prefix),
               "--budget", "5000000"]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True,
                           timeout=90)
        summary = json.loads((self.repo / "out-summary.json").read_text())
        matches = (self.repo / "out-matches.tsv").read_text(encoding="utf-8")
        self.assertEqual(summary["hashlist_updates"], 0)
        self.assertEqual(summary["native_original_names_confirmed"], 0)
        self.assertFalse(summary["budget_exhausted"])
        return p.stdout, summary, matches

    def test_sv_known_stem_suffix(self):
        stdout, report, matches = self.run_mode("sv")
        self.assertIn("main.fake.KnownManager", matches)
        self.assertEqual(report["exact_hash_matching_candidates"], 1)
        self.assertIn("stem_plus_class_suffix", matches)
        self.assertGreater(report["attempted_candidates"], 5)

    def test_za_verb_from_known_stem(self):
        stdout, report, matches = self.run_mode("za")
        self.assertIn("ExecuteRequest", matches)
        self.assertIn("SetRequest", matches)
        self.assertEqual(report["exact_hash_matching_candidates"], 2)

    def test_wrong_existing_symbol_hash_rejected(self):
        p = self.repo / "SV/Hashlists/Lua/lua_c_hashes.txt"
        s = p.read_text().replace("0x"+f"{hash_name('main.fake.KnownData'):016X}", "0xFFFFFFFFFFFFFFFF")
        p.write_text(s)
        proc = subprocess.run([str(self.binary), "--repo", str(self.repo),
                               "--mode", "sv", "--out", str(self.repo/"out"),
                               "--budget", "100000"],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Preexisting invalid full-hash mapping", proc.stderr)


if __name__ == "__main__":
    unittest.main()
