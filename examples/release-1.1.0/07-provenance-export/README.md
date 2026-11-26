# EX-07 — Scientific Provenance

## Mathematical meaning

The unchanged native manifest records source/environment/configuration, randomness, output integrity and scientific completeness for the actual scan. A verified checksum proves binary identity, not a mathematical conclusion.

## Manual reproduction

Reuse the EX-06 native CSV, configuration and manifest together. Check their output sizes/hashes and completed status. Do not rename an editorial summary as a native application manifest. No provenance-inspector UI exists.

## Observed results and scope

The native files are referenced in place in EX-06, avoiding duplicate evidence. native-manifest-explanation.json is an explicitly labelled editorial explanation, not a second native manifest.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [native-manifest-explanation.json](native-manifest-explanation.json)
- [Native scan manifest](../06-parametric-scan/scan.csv.manifest.json)
- [Native CSV](../06-parametric-scan/scan.csv)
- [Native configuration](../06-parametric-scan/scan.config.json)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
