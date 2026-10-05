"""measure.py on planted data with known answers, and three planted faults that must each be caught."""
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import measure  # noqa: E402


def obs80(obj, night, frac, ra, dec, mag=17.5, cat="V", stn="XXX"):
    """An 80-column record at the given RA and Dec (degrees)."""
    h = ra / 15.0
    hh = int(h); mm = int((h - hh) * 60); ss = ((h - hh) * 60 - mm) * 60
    sgn = "-" if dec < 0 else "+"
    d = abs(dec); dd = int(d); dm = int((d - dd) * 60); ds = ((d - dd) * 60 - dm) * 60
    date = f"{night.replace('-', ' ')}.{frac:05d}"
    line = (f"{obj:5s}" + " " * 9 + "C" + f"{date:16s} " + f"{hh:02d} {mm:02d} {ss:06.3f}"
            + f"{sgn}{dd:02d} {dm:02d} {ds:05.2f}" + " " * 9 + f"{mag:4.1f} G" + cat + "     " + stn)
    assert len(line) == 80
    return line


def planted(seed=4242, n=300):
    """n observations of 10 objects on 20 nights near Dec +60 (cos 0.5): bias +0.20" in RA*cos(Dec) and -0.10" in Dec,
    scatter 0.30" and 0.25", and 9 gross outliers at 8"."""
    rng = random.Random(seed)
    nights = [f"2025-{8 + i // 10:02d}-{10 + i % 10:02d}" for i in range(20)]
    lines, pos = [], []
    for i in range(n):
        ra_t, dec_t = 40.0 + 0.01 * i, 60.0 + 0.002 * i
        dra, ddec = 0.20 + rng.gauss(0, 0.30), -0.10 + rng.gauss(0, 0.25)
        if i % 33 == 5:
            dra, ddec = 8.0, -8.0
        mag = 16.0 + 3.0 * rng.random()
        lines.append(obs80(f"{10000 + i % 10:05d}", nights[i % 20], 10000 + i,
                           ra_t + dra / 3600.0 / math.cos(math.radians(dec_t)), dec_t + ddec / 3600.0, mag=mag))
        pos.append({"ra": ra_t, "dec": dec_t})
    return lines, pos


def recovers(s):
    return (s["n_gross"] == 9 and abs(s["mean_ra"] - 0.20) <= 3 * s["se_ra"] and abs(s["mean_dec"] + 0.10) <= 3 * s["se_dec"]
            and 0.25 <= s["sd_ra"] <= 0.35 and 0.20 <= s["sd_dec"] <= 0.30
            and 0.30 <= s["rms_ra"] <= 0.42 and 0.20 <= s["rms_dec"] <= 0.33)


class TestPlanted(unittest.TestCase):
    def test_recovers_the_planted_scatter_and_bias(self):
        for seed in (4242, 1, 2, 3):
            lines, pos = planted(seed)
            s = measure.stats(measure.residuals(lines, pos))
            self.assertTrue(recovers(s), (seed, s))
            self.assertEqual((s["objects"], s["nights"]), (10, 20))
            self.assertEqual(s["sigma_file"], max(s["rms_ra"], s["rms_dec"]))

    def test_planted_faults_are_caught(self):
        lines, pos = planted()
        real = measure.residuals(lines, pos)
        no_cos = [dict(r, dra=r["dra"] / math.cos(math.radians(p["dec"]))) for r, p in zip(real, pos)]
        flipped = [dict(r, dra=-r["dra"], ddec=-r["ddec"]) for r in real]
        by_60 = [dict(r, dra=r["dra"] / 60.0, ddec=r["ddec"] / 60.0) for r in real]
        for name, res in (("cos(Dec) dropped", no_cos), ("sign flipped", flipped), ("arcsec by 60", by_60)):
            self.assertFalse(recovers(measure.stats(res)), name)


class TestPieces(unittest.TestCase):
    def test_se_by_night_by_hand(self):
        # nights of 1, 2 and 3 observations: (0.3 | 0.1 0.2 | -0.1 0.0 0.1); the mean is 0.1; the nights' sums of
        # deviations are 0.2, 0.1 and -0.3; sqrt(3/2 * 0.14) / 6 = sqrt(0.21) / 6
        se = measure.se_by_night([0.3, 0.1, 0.2, -0.1, 0.0, 0.1], ["a", "b", "b", "c", "c", "c"])
        self.assertAlmostEqual(se, math.sqrt(0.21) / 6.0, places=12)

    def test_quantile_linear(self):
        self.assertEqual(measure.quantile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)
        self.assertAlmostEqual(measure.quantile([10.0, 20.0, 30.0], 2 / 3), 23.333333333333332)
        self.assertEqual(measure.quantile([5.0], 0.95), 5.0)

    def test_robust_sigma(self):
        self.assertAlmostEqual(measure.robust_sigma([-2.0, -1.0, 0.0, 1.0, 2.0]), 1.4826)

    def test_obs80_round_trip(self):
        l = obs80("12345", "2025-09-01", 12345, 123.456789, -12.345678, mag=18.3, cat="W")
        ra, dec = measure.obs80_radec(l)
        self.assertLess(abs(ra - 123.456789) * 3600 * math.cos(math.radians(dec)), 0.01)
        self.assertLess(abs(dec + 12.345678) * 3600, 0.01)
        self.assertEqual(measure.obs80_mag(l), 18.3)
        r = measure.residuals([l], [{"ra": ra, "dec": dec}])[0]
        self.assertEqual((r["night"], r["obj"], r["cat"]), ("2025 09 01", "12345", "W"))

    def test_gross_cut_and_clipping_are_about_zero(self):
        # a constant offset of 1" with a small scatter: nothing is cut, since the cut and the clipping are about zero
        res = [{"dra": 1.0 + 0.01 * ((i % 7) - 3), "ddec": 0.0, "mag": None, "night": str(i % 4), "obj": str(i % 5),
                "cat": "V"} for i in range(40)]
        s = measure.stats(res)
        self.assertEqual((s["n"], s["n_gross"], s["n_clipped"]), (40, 0, 0))
        self.assertAlmostEqual(s["mean_ra"], sum(r["dra"] for r in res) / 40, places=12)
        self.assertGreater(s["mean_ra"], 0.99)


if __name__ == "__main__":
    unittest.main()
