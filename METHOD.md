# The method

*How the values in this package were measured, 3-4 October 2026, and what they are.*

## The question

How large are each station's astrometric errors, for the stations that observed 3I/ATLAS?
Of 3I's 8,442 observations from 346 stations (the MPC's get-obs service, 3 October 2026), the public per-station values found cover 8.1-8.6%: Vereš et al. 2017 (Tables 2-4) and Find_Orb's `sigma.txt`.
Find_Orb's own file calls its values "simply default values, used when there's no other way to know the uncertainty".

## Vereš et al. 2017, as read

They used "the root-mean-square (RMS) of astrometric residuals in RA and DEC", the residuals of "debiased astrometric positions" "computed by the JPL orbit determination pipeline", restricted "to the astrometric dataset corresponding to multi-apparition orbits".
They "analyzed the astrometric residuals as a function of observation epoch, observed brightness and rate of motion".

## What was done here, for each station

1. **The sample:** its observations of numbered asteroids (absolute magnitude H ≤ 17) dated 2025-05-01 to 2026-05-01, by two routes:
   - **the field route:** the numbered asteroids that stood within 20′ of 3I's reported position (V ≤ 19.5) on the nights the stations observed 3I: 615 objects;
   - **the NEO route:** the numbered near-Earth asteroids (q < 1.3 au) reaching V ≤ 17.5 in the window: 106 objects.

   Each object's observations were read from the MPC's get-obs service on 3 October 2026; at most 150 objects a station by each route (60 in a later pass over the stations beyond the first 78), drawn with a fixed seed where more were available.
2. **The positions:** JPL's published orbits through the Horizons API, at each observation's reported UT, topocentric at the station's code: astrometric RA and Dec and the orbit's 3-sigma.
3. **The residuals,** in RA·cos(Dec) and Dec.
   Positions whose orbit 3-sigma exceeds 0.15″ in RA or in Dec are set apart.
   The robust sigma (1.4826 × the median absolute deviation) is taken on what remains.
   A gross cut about zero at the larger of 5″ and ten robust sigmas, in either coordinate.
   Then 3-sigma clipping about zero, each coordinate against its own RMS, repeated until nothing changes (at most 20 rounds); an observation out in either coordinate is out.
4. **On what is kept:** the RMS; the mean (the bias), with its standard error clustered by night (the UT date): √(G/(G−1) · Σ over nights of (Σ (x − x̄))²) / n over G nights and n observations; and the faintest third's RMS (the kept observations at or fainter than the two-thirds point of their magnitudes).

A station is called measured with at least 30 kept observations of at least 5 objects on at least 3 nights.
The sigma file takes the larger of the RA and Dec RMS, from the field route where the station is measured there, otherwise from the NEO route.

`measure.py` states steps 3 and 4 as code.

## The controls

- **The code:** on 300 planted observations (a known scatter of 0.30″ and 0.25″, a known bias of +0.20″ and −0.10″, nine gross outliers), the statistics recovered 0.290″ and 0.240″, +0.215″ and −0.090″, and set apart the nine; three planted faults were each caught.
- **The pipeline:** F51, G96 and 703, whose published values rest on measured statistics (Vereš et al. 2017, Tables 1-3), measured the same way.
  Field route: RMS 0.036″/0.032″, 0.076″/0.082″, 0.352″/0.376″; NEO route: 0.040″/0.042″, 0.084″/0.088″, 0.237″/0.235″.
  Every RMS came out under its published weight (0.2″, 0.5″, 0.8″).
- **The two routes:** at F51 and G96 they agree within 0.01″.
- **The table checks itself:** every sigma line traces to its station's statistics, the table's rows rebuild from those statistics with no value differing, and three stations' residuals (C23, C40, X05) rebuild exactly from their raw observations and JPL's positions by code written apart from the measuring code.

## What was measured

- **56 stations of 3I/ATLAS:** 52 without a published value, and F51, G96, 703 and W84 beside their published values.
- **Coverage:** the 52 hold 2,390 of 3I's 8,442 observations (28.3%); with the published values, 36.4-36.9% of 3I's observations have a per-station value.
- **Not measured:** some of 3I's busiest stations (213, 958, 134, 323, Y05 and M47 among them) reported too few of the numbered asteroids sampled to be measured, by either route, in this window (under 30 observations each).

## Scope and limits

- **Point sources, not a coma.** These are each station's errors on asteroids. 3I is a comet: a centroid on its coma can carry more error, and a bias that depends on aperture and seeing, neither measured here. Read the values as a floor for 3I's own errors at matching magnitudes and rates, not their total.
- **A number belongs with its sample.** Of the 13 stations measured by both routes, the two values differ by more than 0.01″ at 11, by each station's larger RMS. Each value is given with the magnitudes and the rate of motion of its sample, beside the station's own 3I magnitudes. Magnitudes are as reported, in each station's own band.
- **The rule's reading.** Two fair readings of "3-sigma clipping" (about zero against the RMS; about the mean against the standard deviation) move the second decimal wherever a station carries an offset, at any sample size (C40, 4,114 observations: 0.15″ or 0.14″). Step 3 above states the reading used.
- **Bias.** The table gives each measured station's mean residual against JPL's orbits with its standard error clustered by night. The ATLAS units (W68, T05, R17, M22, T08) carry +0.04″ to +0.06″ in both coordinates. They carry it in the southern hemisphere (W68, M22) as in the northern (T05, T08, R17). The shared positive offset in Dec does not grow with a weaker orbit. No cause is named.
- **No catalog debiasing.** The star catalogs each station used are named beside its values, as the MPC's catalog codes (column 72 of the observation records; a blank code shows as " :N").
- **Measured, not inflated.** Vereš et al. "conservatively set the data weights according to the upper bound of the RMS as a function of brightness". This file carries the measured RMS.
- **One number a station.** Find_Orb's `sigma.txt` takes one position sigma a line; the table gives RA and Dec apart.
- **The dates measured.** Each line applies to 2025-05-01 to 2026-05-01 only.

## How Find_Orb reads the lines

In Find_Orb's own words, it "looks through this file from top to bottom" and keeps going "until sigmas have been found for all three quantities".
So the lines go at the top of the file, above any line for the same station (Find_Orb's own file has one for F51, at 0.2″) and above its catch-all lines.
Each line gives a position sigma only; the magnitude and time sigmas come from the lines below it.
Each field sits in the characters Find_Orb's own lines use, each comment from character 59 (checked against its file character by character; not run in Find_Orb).

## Sources

- Vereš, P., Farnocchia, D., Chesley, S. R., Chamberlin, A. B. (2017). Statistical Analysis of Astrometric Errors for the Most Productive Asteroid Surveys. arXiv:1703.03479v2.
- Find_Orb's `sigma.txt`: https://raw.githubusercontent.com/Bill-Gray/find_orb/master/sigma.txt, read 3 October 2026, 20:38 UTC.
- The MPC's get-obs service, for 3I's observations (3 October 2026, 20:40 UTC) and the numbered asteroids' (3 October 2026).
- JPL's Horizons API, for the asteroids' positions and their orbits' uncertainties (3-4 October 2026).
