"""The table and the sigma file, rebuilt from data/, byte for byte; a planted change must show."""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build_table  # noqa: E402


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class TestBuild(unittest.TestCase):
    def test_rebuilds_byte_for_byte(self):
        table, sigma = build_table.build(os.path.join(ROOT, "data"))
        self.assertEqual(table, read("weights_3I_stations.md"))
        self.assertEqual(sigma, read("sigma_3I_stations.txt"))
        self.assertEqual(table.count("\n") - 2, 96)
        self.assertEqual(len([l for l in sigma.splitlines() if not l.startswith("#")]), 56)

    def test_a_planted_change_shows(self):
        tmp = tempfile.mkdtemp()
        try:
            for name in os.listdir(os.path.join(ROOT, "data")):
                shutil.copy(os.path.join(ROOT, "data", name), tmp)
            p = os.path.join(tmp, "measured.json")
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            d["entries"][0]["rms_dec"] += 0.01
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f)
            table, sigma = build_table.build(tmp)
            self.assertNotEqual(table, read("weights_3I_stations.md"))
            self.assertNotEqual(sigma, read("sigma_3I_stations.txt"))
        finally:
            shutil.rmtree(tmp)

    def test_sigma_lines_sit_in_find_orbs_columns(self):
        for l in read("sigma_3I_stations.txt").splitlines():
            if l.startswith("#"):
                continue
            self.assertEqual((l[0], l[8:18], l[19:29]), (" ", "2025 05 01", "2026 05 01"))
            self.assertGreater(float(l[40:46]), 0.0)
            self.assertEqual(l[46:58].strip(), "")
            self.assertTrue(l[58:].startswith("measured ("))


if __name__ == "__main__":
    unittest.main()
