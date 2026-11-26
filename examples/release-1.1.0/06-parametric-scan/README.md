# EX-06 — Parametric Scan

## Mathematical meaning

A finite exploratory grid compares descriptive occupancy/control metrics over 49 dimension pairs. Selecting a large structural score does not imply statistical significance. Native GUI table sorting may differ from CSV row ordering.

## Manual reproduction

Set Start=1001 and XY. Open Module scan: X from 26 to 32, Y from 26 to 32, Z=2, Trials=12, Compute CPU. Run to 100%, then Export CSV. Scan internally uses Primes, mode parameter 2, Linear, placement parameter 7 and full-depth XY overlay.

## Observed results and scope

Observed: all 49 distinct pairs, 58 exported columns. All numeric results were recalculated. The screenshot is a row/column excerpt; the complete scan.csv is authoritative. Scan worker and thread reached normal native cleanup.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [interface.png](interface.png)
- [results.json](results.json)
- [scan.config.json](scan.config.json)
- [scan.csv](scan.csv)
- [scan.csv.manifest.json](scan.csv.manifest.json)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
