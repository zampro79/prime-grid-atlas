# Prime Grid Atlas 1.1.0

## Integrity, Reproducibility & Reliability Update

**Release preparation only — not published.** The author has reserved version
DOI **10.5281/zenodo.24573039**, not yet registered by publication. The
author-authorized planned publication date is **2026-11-27**; this does not
assert a completed publication. Original author: **zampro79**. MIT License.
Read [Known Issues](KNOWN_ISSUES.md), especially the unresolved native crash.

## Additive capabilities

- Standard-library scientific provenance manifests record observed source
  identity/hashes, environment, effective configuration and backend evidence.
  Output sizes/hashes and scientific-completeness metadata are distinct.
- Preventive memory budgets use configurable caps and available-resource
  observations. They estimate additional operation-local allocations, including
  host/device work; they do not reserve memory or guarantee against OOM.
- The persistent Research I evidence package preserves A/B/C/D manifests, source
  hashes, an isolated legacy-normalization reconstruction procedure and CSV
  comparison tooling. Original historical-source provenance remains incomplete.

## Reliability corrections

- Public arrays are isolated from internal caches through defensive copies for
  volumes, scalar fields, projections and the CPU sieve. Caller mutations no
  longer expose cached numerical buffers; the mathematical sieve is unchanged.
- Scalar LRU tracking follows successful accesses, including cached None entries,
  without altering eviction policy or inventing warm-cache entries.
- Rendering publishes data, image, viewport, metrics and provenance together
  after a successful calculation. Handled refusals/errors preserve the previous
  valid generation; exports require a valid result.
- Placement-comparison exports retain the profile/grid used during calculation.
  Source identity includes memory_policy.py, even without Git metadata.
- Handled-export consistency prevents known stale-manifest cases and filename
  collisions while preserving existing CSV/configuration/image formats. It is
  not a multi-file transaction under abrupt crashes or concurrent writers.
- Memory preflights compose cold/warm cache work, public copies and retained
  buffers. Entropy estimates include simultaneous NumPy expression temporaries
  and propagate the actual bin count into overlay/render/scan/comparison guards.
- Cgroup detection maps process membership through applicable v1/v2 mount roots,
  mount points and visible hierarchy limits. Exhausted known limits retain zero
  headroom. Optional resource/RLIMIT_AS detection permits import and configured
  caps when those sources are absent.

## Scientific preservation and validation

This version-label/documentation step changes no mathematical formula, numerical
algorithm, declared dependency, configuration schema (1), provenance schema
(`pga.provenance/1.0`) or default cap (1024 MiB). All original scientific datasets,
manifests and checksums remain preserved, as do the v1.0.0 tag/deposit and notes.

Preparation validation requires one complete unittest run per existing Linux
CPU environment with faulthandler (169 tests: 168 pass, one CUDA skip), compileall,
Research II theorem verification and fresh Research I fixed non-DC / Research II
reruns. Required CSV comparisons are 11/11 and 4/4 byte-identical respectively.
Version-only test assertions may change; numerical expectations must not.
Local validation evidence must identify the actual working-tree hashes until a
new source commit exists. A later final candidate still needs its own reviewed
validation record; these notes do not assert release publication.

The STEP 10R preparation working tree passed those checks in both existing
environments: 169 tests each (168 passed, one CUDA skip), compileall, the Research
II verifier and 11/11 plus 4/4 fresh CSV comparisons. Native launch/title and
scan exports reported 1.1.0 with the existing schemas. Source identity correctly
reported the uncommitted working tree based on 39b50c4; this is not a new release
commit or permission to publish. No new native crash was observed in these runs.

STEP 10R.6 subsequently validated the complete 205-file distribution extracted
from D = 5335d72191458021145c5a6553dd81efc9d3fc67 without Git metadata. Both
existing Linux CPU environments passed 169 tests (168 passed, one CUDA skip),
compileall, Research II verification and native runtime/provenance checks. Fresh
Research I fixed non-DC and Research II reruns matched 11/11 and 4/4 baseline
CSVs per environment. The seven-example verifier passed 5,953 numerical checks
against clean S. Native provenance without Git reported file hashes and unknown
Git fields, without inventing a commit. No new native crash was observed.

The 1.1.0 cache, export-provenance and memory-policy changes listed above address
pre-existing reliability gaps and cases identified during 1.1.0 development.
Earlier mathematical-definition corrections, including fixed non-DC spectral
entropy normalization, already belonged to 1.0.0; they are not new 1.1.0 fixes.
R08-08 remains unresolved.

## Integrated visual documentation and project origins

The author approved the source-S [seven demonstrations](examples/release-1.1.0/README.md),
[complete gallery](examples/release-1.1.0/GALLERY.md) and
[validation evidence](examples/release-1.1.0/VALIDATION.md). Eleven original PNGs,
numerical outputs/configurations and five unchanged native manifests retain
source S = eaf6c433722521c5f0dd6a6b07e112e643b5d05b and original capture times.
A later documentation commit D does not replace that source identity. No image
or Research dataset was regenerated during editorial integration.

[Project history](history/README.md) preserves the author-provided Celle Primi
V0.10 source byte for byte under explicitly approved MIT licensing. Its four
images are contemporary executions, not original 2025 screenshots. The observed
level_spin startup NameError and layout limits remain documented and unfixed.
The prototype is not a current feature, dependency or scientifically validated
part of the 1.1.0 engine. Its future inclusion in the 1.1.0 archive is approved
in principle; no release or Zenodo publication is performed by this integration.

## Known unresolved issues and scope

**R08-08: HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN.** An intermittent
native SIGSEGV was observed during an offscreen Qt test, in Shiboken object
destruction. Its root cause and operational scope are unknown; it is not proven
to be confined to tests or caused by any particular component. Controlled
subsequent runs did not reproduce it. No crash probability or workaround is
established. A crash may lose unsaved results or interrupt exports. See
[the complete disclosure](KNOWN_ISSUES.md).

Real CUDA, non-Linux platforms and general thread safety are not validated.
Memory estimates vary with libraries/allocators; shared configuration and
concurrent execution are not isolated (PGA-ARCH-04 remains deferred). Historical
Research I CSV reconstruction does not identify the complete original source
snapshot or recover the original environment. STEP 10R.6 completed the full
candidate-D privacy review: R08-07 is FIXED for those exact reviewed bytes.
Later metadata/archive changes require their own scoped privacy check. No
speculative Qt cleanup change is included.

## Citation and archive identity

Reserved version 1.1.0 DOI: **10.5281/zenodo.24573039**, not yet registered by
publication. Concept DOI: **10.5281/zenodo.24546972**. The published version
1.0.0 DOI **10.5281/zenodo.24546973** identifies 1.0.0 only.

Use [CITATION.cff](CITATION.cff) for the version actually used. Until the new
archive is published, do not describe the reserved DOI as an available archived
release; identify the actual source commit. After publication, cite the verified
version DOI and actual publication date. Source-S captures and native manifests
retain their original source identity regardless of a later metadata commit M.

## Remaining publication gates

- Verify that actual publication can take place on the authorized planned date
  2026-11-27; otherwise stop and realign the metadata before publishing.
- Complete author review of the prepared final archive and publication texts.
  Metadata commit M is authorized by STEP 10R.9; D was validated in STEP 10R.6.
- Identify and verify the final source snapshot, tag and archive, without changing
  source-S evidence, historical datasets or separately retained preparatory files.
- Preserve R08-08 as open despite the author’s explicit publication-risk
  acceptance in STEP 10R.9. Acceptance does not authorize publication.
- Explicit authorization for any push, merge, tag, GitHub Release or Zenodo
  publication; verify the reserved DOI and matching final records at that stage.

See [the 1.1.0 checklist](RELEASE_CHECKLIST_v1.1.0.md),
[Known Issues](KNOWN_ISSUES.md) and [Zenodo metadata](ZENODO.md).
No publication or external operation is implied by these local release notes.
