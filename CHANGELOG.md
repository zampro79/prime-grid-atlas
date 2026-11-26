# Changelog

## v1.1.0 — Integrity, Reproducibility & Reliability Update (in preparation)

Not yet published. Version DOI **10.5281/zenodo.24573039** has been reserved
by the author in a new version draft in the existing Zenodo series; it is not
yet registered by publication. The author-authorized planned publication date
is **2026-11-27**; no publication has occurred. If the release is postponed,
realign the metadata before publishing.

### Added

- Standard-library scientific provenance manifests with observed source identity,
  configuration, environment, backend evidence, output hashes and completeness.
- Persistent Research I reproducibility evidence, A/B/C/D manifests, source
  hashes, isolated legacy-normalization procedure and CSV comparison tooling.
- Configurable preventive memory budgets with host/device estimates and
  operation-local admission before heavy allocations.
- Regression tests for cache isolation, export provenance, memory composition,
  scalar LRU tracking, cgroup detection and simulated portability limitations.

### Fixed

- Isolate public arrays from internal caches through defensive copies, including
  the CPU sieve, volumes, scalar fields and projections.
- Keep the last successful data, viewport, metrics and provenance together after
  handled render failures; prevent completed exports before any valid result.
- Preserve placement-comparison scientific configuration across later UI edits;
  include memory_policy.py in observed source identity.
- Compose cold/warm cache allocations, retained buffers and entropy-bin-dependent
  NumPy temporaries; preserve scalar LRU tracking including cached None entries.
- Resolve applicable cgroup v1/v2 mounts and hierarchical limits; retain zero
  headroom at exhausted limits and make resource/RLIMIT_AS detection optional.
- Improve handled-export consistency while preserving existing output formats.

### Known limitations

- R08-08 remains HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN. A native
  SIGSEGV was observed during Qt object destruction; no causal component has
  been established. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md).
- Real CUDA, non-Linux platforms and thread safety are not validated. Memory
  estimates and multi-file crash atomicity have limits; historical Research I
  source provenance remains incomplete.
- Source-S 1.1.0 screenshots and examples are integrated in commit D. STEP
  10R.6 completed full-distribution privacy/CFF validation and fresh 11/11
  Research I plus 4/4 Research II CSV baseline comparisons in both CPU
  environments. The planned date is authorized; actual publication, final
  archive acceptance and publication authorization remain pending. Original v1.0.0 datasets,
  manifests, tag, DOI and release notes remain preserved. No scientific formula,
  schema or dependency update is part of this metadata-completion step.

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
