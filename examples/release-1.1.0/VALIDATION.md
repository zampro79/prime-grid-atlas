# Validation scope

**PASS WITH LIMITATIONS.** The source S checkout stayed clean. [Numerical checks](numerical-validation.json), [native desktop checks](desktop-validation.json), [regression executions](regression-validation.json) and [historical preservation](preservation-validation.json) contain observed results.

- New arithmetic outputs: independent trial-division prime oracle, independent gcd support and direct NumPy FFT, including all four FFT metrics.
- 3D: all 6406 saved/submitted positions equal independent oracle coordinates; no subsampling. Individual point visibility is affected by perspective/occlusion.
- Same-implementation recalculation: 14 comparison rows, 49 scan rows, 5953 numeric assertions including native CSV serialization. Relative/absolute tolerance 1e-12. This is repeatability evidence, not a proof of every metric.
- Native sidecars: five original manifests; application 1.1.0, full source S, clean Git observation, source hashes, real UTC timestamps, completed status, output sizes and hashes verified. Native unknown backend fields remain unknown.
- Existing system and virtual environments: 169 unittest cases each, 168 passed and one actual-CUDA skip, zero failures; compileall and Research II verifier passed in both. Tests are Qt offscreen; separate real Wayland capture provides the observed desktop/OpenGL evidence.
- Historical checks: 33 protected files and 32 preparatory artifacts unchanged. Research I SHA256SUMS 12 entries, historical CSV_SHA256SUMS 11 entries, preparatory package SHA256SUMS 30 entries pass. Preserved STEP 10R CSVs match both retained baselines: 11 Research I fixed non-DC and 4 Research II per environment. No scientific study regenerated.
- Visual review: all 11 PNGs inspected at original resolution; English labels and captions, no visible private paths, no retouching. Real Qt Fusion style is shared. Native Matplotlib scientific export is distinguished from qualitative application screenshots.
- Privacy: all text, JSON, CSV, script contents, PNG ancillary metadata and visible screenshots checked. R08-07 is FIXED only for this reviewed package, not for historical preparatory material or future exports. See the [privacy report](PRIVACY_REVIEW.md) and the integration checksum index.

R08-08 remains HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN. A sandbox access probe had a Qt initialization SIGABRT before application import; the real desktop probe and both complete capture processes then exited normally. No new SIGSEGV occurred. Qt Wayland emitted nonfatal text-input focus warnings; private logs are excluded from the review ZIP. No CUDA, non-Linux, general thread safety or universal crash-freedom validation is claimed.

Native aspect-ratio fitting retains whitespace. Some GUI controls require scrolling; the scan is a table excerpt. Qt widget captures omit OS window decorations and therefore may not show the application title/version; source/runtime are bound by metadata and exports. FFT exports show array indices, not annotated normalized-frequency coordinates. Publication still requires author review and the remaining release/citation gates.

## Integration scope

This document was adapted during STEP 10R.4. The original JSON validation/capture observations retain their original timestamps and values. Integrated documentation and script instruction paths are covered by newly generated checksum indices. These indices describe this layout; they do not replace original archive checksums or source S. The historical prototype is excluded from this scientific validation.
