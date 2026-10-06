# Measured astrometric sigmas for the stations of 3I/ATLAS

*Per-station position uncertainties for anyone fitting the orbit of 3I/ATLAS. Free.
Version 1, 5 October 2026.*

An orbit fit weights each observation by its uncertainty.
The public per-station values found (Vereš et al. 2017, Tables 2-4, and Find_Orb's `sigma.txt`) cover 8.1-8.6% of 3I's 8,442 observations from 346 stations, as the Minor Planet Center (MPC) served them on 3 October 2026.
This package adds measured values for 52 more of those stations, from their own observations of numbered asteroids in 2025-26, against JPL's orbits, following the method of Vereš et al. 2017 as `METHOD.md` reads it (without their catalog debiasing).
Those 52 stations hold 2,390 of 3I's observations (28.3%); with the published values, 36.4-36.9% of 3I's observations now have a per-station value.
The measured sigmas run from 0.02″ (X05) to 1.00″ (L92).

## What is inside

| File | What it is |
|---|---|
| `sigma_3I_stations.txt` | 56 lines in the layout of Find_Orb's `sigma.txt`: one measured position sigma a station, for observations from 2025-05-01 to 2026-05-01. |
| `weights_3I_stations.md` | The table: 96 rows, one for each station and source of a value (published, or measured by a route), each measured value with its sample, RMS, bias, magnitudes and rate of motion, beside the station's own 3I magnitudes. |
| `METHOD.md` | How the values were measured, the controls, and the limits. |
| `data/measured.json` | The measured statistics, one entry for each station and route: what the table and the sigma file are built from. |
| `data/published.json` | The published values read for 3I's stations, each with its source and line. |
| `data/stations_3I.json` | 3I's observations summarized by station: the count, the magnitudes, and the observers' own median reported uncertainty. |
| `build_table.py` | Builds the table and the sigma file from `data/`. Python 3, standard library only. |
| `measure.py` | The statistics, as `METHOD.md` states them: the residuals, the gross cut, the clipping, the RMS, the bias and its standard error, the robust sigma, the faintest third. Standard library only. |
| `tests/` | The tests: the table and the sigma file rebuilt byte for byte; the statistics on planted data with known answers; planted faults that must be caught; the checksums. Run `python3 -m unittest discover -s tests`. |
| `SHA256SUMS` | The checksums of every other file. |
| `LICENSE` | The MIT license, for what the package's makers wrote; the published values stay their authors' (see "License"). |

## How to use it

**In Find_Orb.**
1. Copy Find_Orb's `sigma.txt` to a new name, and put that name on the `SIGMAS_FILE` line in `environ.dat`, as the file's own comments recommend.
2. Paste the 56 lines of `sigma_3I_stations.txt` at the top of the copy, above any line for the same station and above its catch-all lines.
   In the file's own words, Find_Orb "looks through this file from top to bottom" and keeps going "until sigmas have been found for all three quantities".
3. Each line sets a position sigma only; the magnitude and time sigmas come from the lines below it.

The lines were checked against Find_Orb's own file character by character; they were not run in Find_Orb for this release.

**Elsewhere.**
The table gives RA and Dec apart; the sigma file gives the larger of the two.
Each value applies to observations from 2025-05-01 to 2026-05-01.

**To rebuild.**
`python3 build_table.py` writes the table and the sigma file from `data/` into `rebuilt/`; `python3 -m unittest discover -s tests` builds them again and checks them against the files here, byte for byte.

## The checks

- Every sigma line and every measured row traces to its entry of measured statistics, and the table rebuilds from those entries with no value differing.
- Three stations' residuals were rebuilt from their raw observations and JPL's positions by code written apart from the measuring code, and matched.
- The pipeline was run on F51, G96 and 703, three stations with published values that rest on measured statistics (Vereš et al. 2017): each RMS came out under its published weight.
- At F51 and G96, the two sampling routes agree within 0.01″.
- `measure.py` gives the same statistics as the code that measured, within 1e-15, on that code's own planted control and on 24 more planted sets.
- The package's own tests, above, need nothing beyond Python's standard library.

## Honest limits

- **Asteroids, not a comet.** These are each station's errors on numbered asteroids, which are point sources. 3I is a comet: a centroid on its coma can carry more error. Read each value as a floor for that station's errors on 3I at matching magnitudes and rates, not their total.
- **A number belongs with its sample.** A station's value moves with its sample: of the 13 stations measured by both routes, the two values differ by more than 0.01″ at 11. Each row gives its sample's magnitudes and rate of motion, beside the station's own 3I magnitudes.
- **Measured, not inflated.** The file carries the measured RMS. Vereš et al. "conservatively set the data weights according to the upper bound of the RMS as a function of brightness".
- **Bias.** The table gives each station's mean residual against JPL's orbits, with its standard error clustered by night. The ATLAS units (W68, T05, R17, M22, T08) carry +0.04″ to +0.06″ in both coordinates. They carry it in the southern hemisphere (W68, M22) as in the northern (T05, T08, R17), and the shared positive offset in Dec does not grow with a weaker orbit. No cause is named.
- **The dates measured.** 2025-05-01 to 2026-05-01 only.
- **Not reached.** Some of 3I's busiest stations (213, 958, 134, 323, Y05 and M47 among them) reported too few of the numbered asteroids sampled to be measured in this window; they have no value here.
- **The rebuild starts from the measured statistics.** The raw observations and JPL's positions they were measured from are not in the package. `measure.py` is tested on planted data; the rate column and the 3I magnitudes are carried as the measurement computed them.

## Where every file comes from

| File | Its origin |
|---|---|
| `README.md`, `METHOD.md` | Written by Annie, 5 Oct 2026, from the measurement's records of 3-4 Oct 2026. |
| `build_table.py`, `measure.py`, `tests/` | Written by Annie, 5 Oct 2026, Python's standard library only. |
| `sigma_3I_stations.txt`, `weights_3I_stations.md` | Measured by Domino Observatory, 3-4 Oct 2026, as `METHOD.md` describes; the published rows are their authors' values. |
| `data/measured.json` | The same measurement's statistics, one entry for each station and route. |
| `data/published.json` | Read from Vereš et al. 2017 (arXiv:1703.03479v2, Tables 2-4) and Find_Orb's `sigma.txt` (https://raw.githubusercontent.com/Bill-Gray/find_orb/master/sigma.txt, read 3 Oct 2026). |
| `data/stations_3I.json` | Summarized from 3I's observations as the MPC's get-obs service served them on 3 Oct 2026, 20:40 UTC: counts, magnitude percentiles and medians only, no observation. |

## License

What the package's makers wrote is under the MIT license (`LICENSE`, "Copyright (c) 2026 Domino Observatory"): the code, the tests, this README, `METHOD.md`, and the measured values.
The published values in the table and in `data/published.json` are Vereš et al.'s and Find_Orb's, carried with their sources; the MIT terms do not cover them.
3I's per-station counts and magnitudes are summaries of observations its observers reported to the MPC.

## Citing

Vereš, P., Farnocchia, D., Chesley, S. R., Chamberlin, A. B. (2017). Statistical Analysis of Astrometric Errors for the Most Productive Asteroid Surveys. arXiv:1703.03479v2.

---

A Castle product from Domino Observatory. Built by Annie, the Castle's AI. A human approves every release.
