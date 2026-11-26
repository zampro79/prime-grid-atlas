# EX-05 — Placement Comparison

## Mathematical meaning

Fourteen placements assign one integer interval to different spatial layouts. Eight geometric metrics and their Euclidean distance from Linear are descriptive. These differences are not significance tests and may change accumulated occupancy.

## Manual reproduction

Set X=Y=30, Z=2, Start=1001, Primes, retain inactive mode parameter 2130, Linear, placement parameter 7, XY, depth index 1 (2/2), overlay true. Open Placement comparison, Compare all placements, then Export CSV.

## Observed results and scope

Observed: 14 complete rows and 11 native CSV columns. All rows and distances were recalculated with the same implementation. Seeded random placement derives its seed as (X*73856093 XOR Y*19349663 XOR 7*2654435761) AND 0xFFFFFFFF; see the observed integer in editorial-metadata.json. This seed is distinct from baseline_seed.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [interface.png](interface.png)
- [placements.config.json](placements.config.json)
- [placements.csv](placements.csv)
- [placements.csv.manifest.json](placements.csv.manifest.json)
- [results.json](results.json)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
