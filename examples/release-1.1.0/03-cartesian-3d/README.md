# EX-03 — Three-Dimensional Prime Distribution

## Mathematical meaning

The real OpenGL renderer displays Cartesian coordinates of the selected prime cells from EX-01. Display geometry does not establish a new arithmetic law. Occlusion and perspective affect the visible point pattern.

## Manual reproduction

Compute EX-01 again before opening 3D view. Select Cartesian grid and selected-only, point size 5, max points 2000000. Native camera elevation 24 degrees, azimuth 42 degrees, center (35,14.5,14.5), distance 115.02; this is one native 0.9 zoom from 127.8.

## Observed results and scope

Observed: 6406 selected and 6406 submitted scatter positions, no subsampling. Every saved position was checked against independent trial-division coordinates. Submitted point count is not a count of individually visible pixels.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [framebuffer.png](framebuffer.png)
- [interface.png](interface.png)
- [rendered-positions.csv](rendered-positions.csv)
- [results.json](results.json)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
