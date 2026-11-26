# Prime Grid Atlas 1.1.0 — visual demonstrations

**Integrity, Reproducibility & Reliability Update — integrated documentation, not published.**

Application source S: `eaf6c433722521c5f0dd6a6b07e112e643b5d05b`; parent `39b50c425ca9af365ff292deafdf99a4fdbb70d8`. The original outputs were calculated from a separate clean Git checkout of S, runtime **1.1.0**, using the existing virtual environment. The complete tracked Python hashes and native source observations are in [source-origin.json](source-origin.json). Scripts and outputs remained outside that checkout. The later documentation/asset commit D does not replace S in the original evidence.

## Seven demonstrations

- [EX-01 — Prime Occupancy](01-prime-occupancy/README.md)
- [EX-02 — Coprimality and Modular Structure](02-coprime-support/README.md)
- [EX-03 — Three-Dimensional Prime Distribution](03-cartesian-3d/README.md)
- [EX-04 — Spectral Analysis](04-fft/README.md)
- [EX-05 — Placement Comparison](05-placement-comparison/README.md)
- [EX-06 — Parametric Scan](06-parametric-scan/README.md)
- [EX-07 — Scientific Provenance](07-provenance-export/README.md)

These examples illustrate application behavior, not new mathematical discoveries, confirmatory studies or replacements for Research I/II. See [gallery](GALLERY.md), [validation](VALIDATION.md) and [privacy review](PRIVACY_REVIEW.md).

## Environment and portable reproduction

Use an existing compatible environment; these commands install nothing. Run from the repository root. Obtain S from the approved local repository (it need not already be public); create a new separate clone, detach at S and confirm clean status. Do not put scripts, diagnostics or outputs inside that clean checkout. Keep all three destination names new; adjust the relative names if they exist.

```bash
git clone --no-hardlinks --no-checkout . ../pga-clean-source-S
git -C ../pga-clean-source-S checkout --detach eaf6c433722521c5f0dd6a6b07e112e643b5d05b
git -C ../pga-clean-source-S rev-parse HEAD
git -C ../pga-clean-source-S status --porcelain
python examples/release-1.1.0/scripts/verify_package.py --package examples/release-1.1.0
cp -R examples/release-1.1.0 ../pga-example-verification
PYTHONDONTWRITEBYTECODE=1 python examples/release-1.1.0/scripts/verify_examples.py \
  --source ../pga-clean-source-S --package ../pga-example-verification
```

The numerical verifier writes numerical-validation.json in the separate verification copy; it must not overwrite the approved evidence in this tree. Its copied checksum for that diagnostic file is expected to become stale after recalculation; use the original integrated tree for the integrity check. Compare numerical outcomes separately from diagnostic-file identity.

For an explicitly requested new capture, use a real desktop and a fresh output directory; do not set QT_QPA_PLATFORM=offscreen. This integration step does not regenerate screenshots:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1 \
  python -X faulthandler examples/release-1.1.0/scripts/capture.py \
  --source ../pga-clean-source-S --output ../pga-new-capture
```

Set MPLCONFIGDIR to a writable directory outside the source checkout when needed. The capture helper refuses an existing output directory.

Only save-file chooser responses and successful export notifications are automated. Real widgets, workers, engine functions, Matplotlib, OpenGL and native provenance writers run unchanged. The helper never synthesizes numerical results, substitutes a renderer or edits image pixels. `window.grab()` captures only the real application widget, excluding unrelated desktop content and window-manager decorations. The OpenGL framebuffer comes directly from grabFramebuffer(). The first successful capture was preserved privately; the selected second run changes only native splitter/camera framing and recalculates fresh outputs. No previous native manifest was rewritten.

The [full profile](shared-profile.json) preserves unchanged AppConfig defaults apart from the explicitly approved baseline seed 20261126. All seven case configurations retain inactive settings. Native viewports and CSV/config/FFT exports keep their original names, timestamps, UUIDs and emitted sidecars. EX-07 reuses the EX-06 export instead of duplicating it. Hits, rendered positions and log-power CSVs are editorial serializations of real computed arrays, not additional native application export formats.

## Graphics and interpretation

Observed Linux Wayland, Qt Fusion, DejaVu Sans 11 and native device-pixel ratio 1.25. Python/package/renderer versions are recorded in [environment-public.json](environment-public.json). CPU/NumPy is the computational backend; AMD/Mesa OpenGL is the graphics renderer. CUDA, general thread safety and other platforms are unverified. No offscreen screenshots are presented as desktop screenshots.

PNG files remain original, unretouched and unresampled. Application aspect-ratio fitting retains some whitespace. Tables are readable at native resolution: placement has all 14 rows/11 columns; scan is explicitly an excerpt of 49 rows/58 columns. Full CSVs are authoritative. FFT viewport screenshots are qualitative, with no quantitative frequency axes/colorbar. The native Matplotlib export supplies array-index axes/colorbar, not fully annotated physical-frequency axes.

## Provenance and integrity

Five native sidecars use unchanged schema pga.provenance/1.0; editorial metadata are explicitly separate. Native loaded_code_identity remains not_verified: disk hashes do not prove the identity of already loaded modules. The process imported the clean S checkout, and recorded source files remained unchanged. Native producer_backend null is preserved rather than inferred.

[numerical-validation.json](numerical-validation.json) distinguishes independent trial division/MCD/FFT definitions from same-implementation comparison/scan reruns. [preservation-validation.json](preservation-validation.json) checks conserved STEP 10R Research I fixed non-DC (11 CSVs) and Research II (4 CSVs) in each environment; those scientific studies were not regenerated in this step.

R08-08 remains **HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN**. Two successful capture processes and successful suites do not resolve that risk. A sandbox desktop-access probe aborted during Qt platform initialization (SIGABRT), before application import; authorized real-desktop access then succeeded. This is distinct from a segmentation fault.

The author approved editorial integration. A separately authorized commit D, citation metadata completion, final distribution privacy review and publication approval remain pending. See [INTEGRATION.md](INTEGRATION.md) for preserved evidence versus integration-time documentation.
