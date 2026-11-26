# EX-01 — Prime Occupancy

## Mathematical meaning

Linear integers obey n = Start + x + X*y + X*Y*z. The XY overlay counts selected prime cells through layers 0–29. A red projected cell indicates at least one prime, and intensity reflects accumulated hits.

## Manual reproduction

Set X=71, Y=30, Z=30, Start=1, Primes, inactive mode parameter 2, Linear, placement parameter 7, XY, depth index 29 (30/30), overlay enabled, Classic, numbers hidden, grid visible. Draw and use Reset view, then Save PNG.

## Observed results and scope

Observed: 6406 prime cells, 564 occupied cells among 2130 projected cells. Independent trial-division verification passed.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [hits.csv](hits.csv)
- [interface.png](interface.png)
- [results.json](results.json)
- [viewport.png](viewport.png)
- [viewport.png.manifest.json](viewport.png.manifest.json)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
