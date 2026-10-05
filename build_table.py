#!/usr/bin/env python3
"""Builds the table (weights_3I_stations.md) and the sigma file (sigma_3I_stations.txt) from data/.

    python3 build_table.py [OUT_DIR]      (default: rebuilt/)

Python 3, standard library only. The rules, as METHOD.md states them:
- one row for each measured station and route (the field route first), then one for each published value, each
  station in order of its 3I observations (most first), then its code;
- the sigma file: the larger of the RA and Dec RMS, from the field route where the station is measured there,
  otherwise from the NEO route; each line in the columns of Find_Orb's sigma.txt, its comment from character 59.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

HEADER = ["station", "3I obs", "source", "N / objects / nights", "RMS RA / Dec (\")", "bias RA / Dec (\")",
          "robust σ (\")", "faintest third RMS (\")", "asteroid mags 5/50/95%", "its 3I mags 5/50/95%",
          "median rate (\"/min)", "catalogs", "observers' own median rms on 3I (\")"]

SIGMA_HEAD = (
    "# Measured position sigmas for stations that observed 3I/ATLAS, in the layout of Find_Orb's sigma.txt.\n"
    "# Each line applies to observations from 2025-05-01 to 2026-05-01 only (the dates measured).\n"
    "# Find_Orb reads sigma.txt from the top and keeps going until it has all three sigmas: put these lines at the top,"
    " above any line for the same station (its own file has one for F51) and above its catch-all lines.\n"
    "#Obs P  <--start-> <--end -->           Pos   Mag  Time\n"
    "#COD C  yyyy mm dd yyyy mm dd mag1 mag2 sig   sig  sig    Comment\n")


def load(data_dir):
    def rd(name):
        with open(os.path.join(data_dir, name), encoding="utf-8") as f:
            return json.load(f)
    return rd("stations_3I.json")["stations"], rd("measured.json")["entries"], rd("published.json")["values"]


def cell(v, fmt="{:.2f}"):
    """A number in its format, or "-" when there is none."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return fmt.format(v)


def measured_row(stn, s3, e):
    mags3 = "-" if s3["mag_p05"] is None else f"{s3['mag_p05']:.1f}/{s3['mag_p50']:.1f}/{s3['mag_p95']:.1f}"
    cats = " ".join(f"{k}:{v}" for k, v in sorted(e["catalogs"].items(), key=lambda kv: -kv[1]))
    return [stn, s3["n_obs"], f"measured here: {e['route']} route",
            f"{e['n']} / {e['objects']} / {e['nights']}",
            f"{e['rms_ra']:.2f} / {e['rms_dec']:.2f}",
            f"{e['mean_ra']:+.2f}±{cell(e['se_ra'])} / {e['mean_dec']:+.2f}±{cell(e['se_dec'])}",
            f"{e['robust_ra']:.2f} / {e['robust_dec']:.2f}",
            f"{cell(e['faint_rms_ra'])} / {cell(e['faint_rms_dec'])}",
            f"{cell(e['mag_p05'], '{:.1f}')}/{cell(e['mag_p50'], '{:.1f}')}/{cell(e['mag_p95'], '{:.1f}')}",
            mags3, f"{e['rate_arcsec_per_min']:.2f}", cats, cell(s3["own_median_rms"])]


def published_row(stn, s3, p):
    text = f"published: {p['source']}: {p['sigma']:g}\""
    if p["condition"]:
        text += f" ({p['condition']})"
    if p["mags"]:
        text += f" (mag {p['mags'][0]}-{p['mags'][1]})"
    return [stn, s3["n_obs"], text] + ["-"] * 9 + [cell(s3["own_median_rms"])]


def sigma_line(stn, e):
    sig = max(e["rms_ra"], e["rms_dec"])
    comment = (f"measured ({e['route']} route): RMS {e['rms_ra']:.2f}/{e['rms_dec']:.2f}\", N={e['n']}, "
               f"{e['objects']} numbered asteroids, mag {cell(e['mag_p05'], '{:.1f}')}-{cell(e['mag_p95'], '{:.1f}')}")
    line = f" {stn:3s}" + " " * 4 + "2025 05 01 2026 05 01" + " " * 11 + f"{sig:<6.2f}" + " " * 12 + comment
    # Find_Orb's columns (its header): the code at 2-4, the dates at 9-18 and 20-29, the position sigma at 41-46,
    # the magnitude and time sigmas at 47-55 (left blank), the comment from 59
    assert line[1:4] == stn and line[8:18] == "2025 05 01" and line[19:29] == "2026 05 01"
    assert float(line[40:46]) == round(sig, 2) and line[46:58].strip() == "" and line[58] != " "
    return line


def build(data_dir):
    """The table's text and the sigma file's text."""
    s3, entries, pub = load(data_dir)
    by = {}
    for e in entries:
        by.setdefault(e["station"], {})[e["route"]] = e
    pubs = {}
    for p in pub:
        pubs.setdefault(p["station"], []).append(p)
    rows, lines = [], []
    for stn in sorted(set(by) | set(pubs), key=lambda c: (-s3[c]["n_obs"], c)):
        for route in ("field", "NEO"):
            if route in by.get(stn, {}):
                rows.append(measured_row(stn, s3[stn], by[stn][route]))
        for p in pubs.get(stn, []):
            rows.append(published_row(stn, s3[stn], p))
        use = by.get(stn, {}).get("field") or by.get(stn, {}).get("NEO")
        if use:
            lines.append(sigma_line(stn, use))
    table = "| " + " | ".join(HEADER) + " |\n|" + "---|" * len(HEADER) + "\n"
    table += "".join("| " + " | ".join(str(x) for x in r) + " |\n" for r in rows)
    return table, SIGMA_HEAD + "".join(l + "\n" for l in lines)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "rebuilt")
    os.makedirs(out, exist_ok=True)
    table, sigma = build(os.path.join(HERE, "data"))
    for name, text in (("weights_3I_stations.md", table), ("sigma_3I_stations.txt", sigma)):
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"{table.count(chr(10)) - 2} rows; {sigma.count(chr(10)) - 5} sigma lines; written to {out}")


if __name__ == "__main__":
    main()
