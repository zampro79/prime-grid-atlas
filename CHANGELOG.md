# Changelog

## v1.0.0 — first official release

No public release date or earlier release history is asserted here.

### Existing capabilities included

- PySide6 tabs for 13 numerical modes, XY/XZ/YZ slices and accumulated overlays.
- Fourteen placements and geometric comparisons against Linear.
- Entropy, gradient and FFT views; observed/coprime/random module scans.
- NumPy CPU operation and optional CuPy CUDA computation with fallback.
- Cartesian and fixed/rotating spherical OpenGL views with an internal observer.
- Runtime configuration and CSV/JSON/PNG exports, including 22 scan heatmaps.

### Release preparation

- Public README, implemented-methodology reference, contribution guide, citation metadata, portable configuration, ignore rules and publication checklist.
- Established `1.0.0` as the first official application version; historical exports remain unchanged.
- Captured scan and placement-comparison configuration at run start to prevent later UI edits from changing export provenance; scan metadata now includes version, Start and run status.
- Removed one unused engine import; numerical formulas and algorithms preserved.
- Marked draft-only research proposals and historical evidence explicitly; repaired links to unavailable sibling datasets.

### Added

- Persistent agent instructions, project context, architecture and versioning policy.

### Fixed

- Prevent scalar FFT display from modifying cached arithmetic fields (scientific audit C1; implemented before the documentation bootstrap).
- Reject int64 interval and prime-family partner overflow before array arithmetic.
- Recheck the configured volume safety limit even when a cached volume exists.
- Normalize spectral entropy by the fixed non-DC support size, restoring reflection invariance; earlier audit CSV values use the former definition.
- Reject nonpositive randomized-baseline trial counts and unsupported projection planes.
- Evaluate nonconstant one-dimensional FFT fields instead of returning degenerate zero metrics.
- Reject non-finite scientific configuration weights and thresholds.
- Record requested and runtime backend policy separately in scan/comparison provenance.

Public author and copyright holder set to `zampro79`; MIT license and verified
repository URL added for the v1.0.0 public release candidate.

### Documentation maintenance

- Added the verified Zenodo v1.0.0 DOI, concept DOI, citation, archive integrity
  record and a non-duplicating procedure for future Zenodo versions.
