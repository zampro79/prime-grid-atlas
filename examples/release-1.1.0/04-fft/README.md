# EX-04 — Spectral Analysis

## Mathematical meaning

Let A be binary prime-hit occupancy in the EX-01 projection. Subtract mean(A), apply FFT2 and fftshift, form squared magnitude P, set the central DC bin to zero, and display log1p(P). Ratios and spectral entropy use P, not logarithmic display values.

## Manual reproduction

Compute EX-01 and use the unchanged application FFT display path. The editorial helper calls show_matrix_tab with the newly computed matrix, not historical data. Use the native save_fft exporter for the Matplotlib figure. The helper also saves the full 30-by-71 matrix in engine row order.

## Observed results and scope

Independent NumPy FFT verification passed with maximum absolute matrix difference 0.0. Viewport PNGs lack frequency axes and colorbar and are qualitative application captures. native-fft.png is an actual Matplotlib export with array-index axes and colorbar; it is not a fully annotated frequency-domain publication figure. Qt vertically flips the numerical array for display.


Source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`. Runtime: **1.1.0**. These demonstrations were captured from S for the **Integrity, Reproducibility & Reliability Update**, not a published release.

Use the complete [configuration](configuration.json), including inactive fields, and the [shared profile](../shared-profile.json). [Editorial metadata](editorial-metadata.json) link the observed [environment](../environment-public.json) and [source hashes](../source-origin.json). CPU was explicitly selected. Do not interpret the graphics renderer as a compute backend. Native producer-backend values marked unknown remain unknown.

Baseline seed: **20261126**; 12 trials, `numpy.random.default_rng`; entropy bins 8. Deterministic arithmetic selection, FFT and Cartesian positions need no independent seed. The profile is retained because associated null metrics can use it. No claim of cross-version or cross-driver PNG byte identity is made.

See the common [reproduction procedure](../README.md), [numerical validation](../numerical-validation.json), [desktop validation](../desktop-validation.json) and [native file checker](../scripts/verify_package.py). Run `sha256sum -c SHA256SUMS` in this case directory and at the package root.

## Evidence files

- [configuration.json](configuration.json)
- [editorial-metadata.json](editorial-metadata.json)
- [interface.png](interface.png)
- [log-power.csv](log-power.csv)
- [native-fft.png](native-fft.png)
- [native-fft.png.manifest.json](native-fft.png.manifest.json)
- [results.json](results.json)
- [viewport.png](viewport.png)

Integration note: document links were adapted during STEP 10R.4; captured results and native provenance remain original.
