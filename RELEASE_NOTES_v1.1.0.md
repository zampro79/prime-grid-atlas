# Prime Grid Atlas 1.1.0

## Integrity, Reproducibility & Reliability Update

**Release preparation only — not published.** No publication date or new
version DOI has been assigned. Original author: **zampro79**. MIT License.
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
snapshot or recover the original environment. R08-07 remains open for final
public artifacts. No speculative Qt cleanup change is included.

## Remaining publication gates

- Author approval and commit of the versioned source/documents; no commit is
  created by STEP 10R itself.
- Actual 1.1.0 screenshots/examples from that source, with native-renderer,
  numerical, provenance and privacy checks; preparatory images remain 1.0.0.
- Verified future version DOI and release date, consistent citation/archive
  metadata, final source/assets review and explicit publication authorization.

See [the 1.1.0 checklist](RELEASE_CHECKLIST_v1.1.0.md) and
[capture specification](screenshots/CAPTURE_PLAN_v1.1.0.md). No push, merge,
tag, GitHub release or Zenodo operation is implied.
