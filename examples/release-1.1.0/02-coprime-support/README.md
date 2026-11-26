# EX-02 — Coprimality and Modular Structure

## Mathematical meaning

For M=71*30=2130, gcd(base + k*M, M)=gcd(base,M). This control measures modular admissibility, not primality. Prime divisors of M are exceptional prime hits outside coprime support.

## Manual reproduction

Reuse EX-01 dimensions/projection/start/placement; choose Coprimes with N and N=2130. Draw, reset the native view, and Save PNG.

## Observed results and scope

Observed: 560 occupied projected cells, 16800 selected cells over 30 layers; independently verified with math.gcd.


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
