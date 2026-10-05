#!/usr/bin/env python3
"""A station's residual statistics against an orbit's positions, as METHOD.md states them (steps 3 and 4).
Python 3, standard library only. Pure functions: no network, no files.

residuals(lines, positions) -> one dict an observation: dra (RA*cos(Dec), arcsec), ddec (arcsec), mag, night, obj, cat
    lines: the observations, as 80-column MPC records; positions: one dict a line, {"ra", "dec"} in degrees (the orbit's
    astrometric position at the observation's time, topocentric at its station).
stats(res) -> the statistics:
  1. the robust sigma, 1.4826 x the median absolute deviation, on everything given;
  2. the gross cut, about zero: |dra| or |ddec| above the larger of 5" and ten robust sigmas of that coordinate is out;
  3. 3-sigma clipping about zero, each coordinate against its own RMS, until nothing changes (at most 20 rounds); an
     observation out in either coordinate is out;
  4. on what is kept: N, objects, nights (the UT date); the RMS; the mean (the bias) and its standard error clustered
     by night, sqrt(G/(G-1) * sum over nights of (sum of (x - mean))^2) / n over G nights; the standard deviation;
     the faintest third's RMS (the kept observations at or fainter than the two-thirds point of their magnitudes);
     the magnitudes' 5/50/95% points; the star catalogs' codes;
  5. sigma_file: the larger of the RA and Dec RMS.
Quantiles interpolate linearly between ranks.
Set apart before calling stats: the positions whose orbit 3-sigma exceeds 0.15" in RA or in Dec (METHOD.md, step 3).
"""
import math
import statistics


def obs80_radec(l):
    """RA and Dec in degrees from an 80-column record."""
    h, m, s = float(l[32:34]), float(l[35:37]), float(l[38:44])
    ra = 15.0 * (h + m / 60.0 + s / 3600.0)
    sign = -1.0 if l[44] == "-" else 1.0
    d, dm, ds = float(l[45:47]), float(l[48:50]), float(l[51:56])
    return ra, sign * (d + dm / 60.0 + ds / 3600.0)


def obs80_mag(l):
    """The magnitude as reported (columns 66-70), in whatever band the station gives; None when blank."""
    try:
        return float(l[65:70])
    except ValueError:
        return None


def residuals(lines, positions):
    out = []
    for l, p in zip(lines, positions):
        ra, dec = obs80_radec(l)
        dra = ((ra - p["ra"] + 180.0) % 360.0 - 180.0) * math.cos(math.radians(p["dec"])) * 3600.0
        out.append({"dra": dra, "ddec": (dec - p["dec"]) * 3600.0, "mag": obs80_mag(l), "night": l[15:25],
                    "obj": l[0:5], "cat": l[71]})
    return out


def quantile(xs, p):
    """Linear interpolation between ranks: rank h = (n - 1) p."""
    s = sorted(xs)
    h = (len(s) - 1) * p
    lo = int(math.floor(h))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (h - lo) * (s[hi] - s[lo])


def robust_sigma(xs):
    if not xs:
        return float("nan")
    med = statistics.median(xs)
    return 1.4826 * statistics.median([abs(x - med) for x in xs])


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def se_by_night(xs, nights):
    """The mean's standard error clustered by night."""
    n = len(xs)
    mu = sum(xs) / n
    sums = {}
    for x, g in zip(xs, nights):
        sums[g] = sums.get(g, 0.0) + (x - mu)
    k = len(sums)
    if k < 2:
        return float("nan")
    return math.sqrt(k / (k - 1.0) * sum(s * s for s in sums.values())) / n


def stats(res):
    if not res:
        return {"n": 0}
    dra = [r["dra"] for r in res]
    ddec = [r["ddec"] for r in res]
    rob_ra, rob_dec = robust_sigma(dra), robust_sigma(ddec)
    g_ra, g_dec = max(5.0, 10 * rob_ra), max(5.0, 10 * rob_dec)
    keep = [abs(a) <= g_ra and abs(b) <= g_dec for a, b in zip(dra, ddec)]
    n_gross = keep.count(False)
    for _ in range(20):
        r_ra = rms([a for a, k in zip(dra, keep) if k])
        r_dec = rms([b for b, k in zip(ddec, keep) if k])
        new = [k and abs(a) <= 3 * r_ra and abs(b) <= 3 * r_dec for a, b, k in zip(dra, ddec, keep)]
        if new == keep:
            break
        keep = new
    idx = [i for i, k in enumerate(keep) if k]
    out = {"n_all": len(res), "n_gross": n_gross, "n_clipped": len(res) - n_gross - len(idx), "n": len(idx),
           "objects": len({res[i]["obj"] for i in idx}), "nights": len({res[i]["night"] for i in idx}),
           "robust_ra": rob_ra, "robust_dec": rob_dec}
    nights = [res[i]["night"] for i in idx]
    for name, x in (("ra", dra), ("dec", ddec)):
        xs = [x[i] for i in idx]
        out[f"mean_{name}"] = sum(xs) / len(xs)
        out[f"se_{name}"] = se_by_night(xs, nights)
        out[f"sd_{name}"] = statistics.stdev(xs) if len(xs) > 1 else float("nan")
        out[f"rms_{name}"] = rms(xs)
    mags = [res[i]["mag"] for i in idx if res[i]["mag"] is not None]
    if len(mags) >= 9:
        cut = quantile(mags, 2 / 3)
        fk = [i for i in idx if res[i]["mag"] is not None and res[i]["mag"] >= cut]
        out["faint_third_from_mag"] = cut
        out["faint_rms_ra"] = rms([dra[i] for i in fk])
        out["faint_rms_dec"] = rms([ddec[i] for i in fk])
        out["mag_p05"], out["mag_p50"], out["mag_p95"] = (quantile(mags, q) for q in (0.05, 0.5, 0.95))
    cats = {}
    for i in idx:
        cats[res[i]["cat"]] = cats.get(res[i]["cat"], 0) + 1
    out["catalogs"] = cats
    out["sigma_file"] = max(out["rms_ra"], out["rms_dec"])
    return out
