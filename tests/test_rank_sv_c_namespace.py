"""Safe synthetic tests for direct-method signature prioritization."""
import csv
import gzip
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lua_hash import lua_hash
from rank_sv_c_namespace import rank_classes, read_assignments, token_id


class TestRankSvCNamespace(unittest.TestCase):
    def test_exact_shared_signature_and_no_name_recovery(self):
        view = lua_hash("main.ui.View")
        other = lua_hash("main.other.Controller")
        unknown = lua_hash("main.missing.NotNamed")
        setup = lua_hash("Setup")
        configure = lua_hash("Configure")
        update = lua_hash("Update")
        methods = {view: {setup, configure, update},
                   other: {setup}, unknown: {setup, configure}}
        report = rank_classes(methods,
            {view: "main.ui.View", other: "main.other.Controller"},
            {unknown}, {setup: "Setup", configure: "Configure"}, top_k=2)
        self.assertEqual(report["unknown_C_with_ranked_peer"], 1)
        row = report["records"][0]
        self.assertEqual(row["unknown_class_hash"], f"0x{unknown:016X}")
        self.assertEqual(len(row["nearest_named_classes"]), 1)
        self.assertEqual(row["nearest_named_classes"][0]["shared_F_count"], 2)
        self.assertEqual(row["nearest_named_classes"][0]["known_namespace"], "main.ui")
        self.assertIn("not original C names", row["inference_limit"])

    def test_no_shared_methods_no_fabricated_peer(self):
        report = rank_classes({7: {10}, 8: {11}}, {7: "main.Known"}, {8}, {})
        self.assertEqual(report["unknown_C_with_ranked_peer"], 0)
        self.assertEqual(report["records"][0]["nearest_named_classes"], [])

    def test_tsv_and_gzip_duplicates_deduplicated(self):
        rows = [{"class_hash": "C0000000000000001", "function_hash": "F0000000000000002"},
                {"class_hash": "C0000000000000001", "function_hash": "F0000000000000002"}]
        with tempfile.TemporaryDirectory() as temp:
            for ext, opener in ((".tsv", open), (".tsv.gz", gzip.open)):
                path = Path(temp) / ("test" + ext)
                with opener(path, "wt", encoding="utf-8", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=list(rows[0]), delimiter="\t")
                    writer.writeheader()
                    writer.writerows(rows)
                self.assertEqual(read_assignments(path), {1: {2}})

    def test_reject_non_class_token(self):
        with self.assertRaises(ValueError):
            token_id("F0000000000000001", "C")


if __name__ == "__main__":
    unittest.main()
