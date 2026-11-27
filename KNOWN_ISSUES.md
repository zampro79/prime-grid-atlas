# Known Issues — Prime Grid Atlas 1.1.0

## R08-08 — Intermittent native crash

**HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN.**

An intermittent native SIGSEGV occurred during an offscreen Qt test. Native analysis located the failure in Shiboken object destruction, but the root cause and operational scope remain unknown. Subsequent controlled runs did not reproduce it; this does not establish that it is resolved or confined to tests.

A crash may terminate the application without warning, lose unsaved results and interrupt an export. Keep copies of completed results and experiment settings. After exporting, verify that all expected files and manifests are present, inspect completion status and validate output hashes. Matching hashes establish file integrity, not scientific completeness.

The verified CPU regression runs reproduce the recorded CSV baselines byte-for-byte. This is not a guarantee against corruption in other executions or interrupted exports. No verified workaround is currently available.

## Validation and engineering limitations

- **CUDA:** real CUDA execution/equivalence was not validated in the release
  preparation environments; mocked routing tests are not GPU validation.
- **Platforms:** candidate validation was performed on Linux. Simulated missing
  POSIX APIs do not establish validation on Windows, macOS or other platforms.
- **Concurrency:** thread safety is not certified. Global configuration, caches
  and backend state do not provide per-operation reservations or isolation.
- **Memory estimates:** preventive estimates include identified simultaneous
  buffers and configured margins. They are not universal upper bounds across
  libraries, allocators or concurrent memory pressure, and cannot guarantee
  avoidance of MemoryError or native failures.
- **Exports:** individual atomic file replacement and handled-failure guards do
  not provide a multi-file transaction or protection from every abrupt crash.
  Check expected files, manifests, completion state and hashes after exporting.
- **Research I provenance:** byte-identical diagnostic reconstruction of the
  historical CSVs does not identify the complete original source snapshot or
  recover the historical environment. Preserve the distinction between current
  fixed non-DC protocol reruns and exact historical numerical reproduction.

Visual patterns, rankings and heuristic scores are descriptive. They are not
proofs, automatic significance tests or evidence of new prime-distribution laws.

## Shared runtime and backend observations

Configuration, caches and backend state are shared. Run scans, placement
comparisons and profile changes sequentially; no global job isolation or memory
reservation is provided (PGA-ARCH-04 remains deferred). Requested GPU mode and
unknown cached-data backend attribution must not be promoted to observed GPU
execution. Handled-export consistency is improved but remains partial with
respect to abrupt crashes and concurrent writers (PROV-02).

## Editorial status and historical evidence

The STEP 10R.4 review classified R08-07 as **FIXED for the reviewed integrated
visual examples and historical prototype material only**. Distribution privacy
reviews apply to each concrete source snapshot separately. Original capture metadata and native manifests
remain unchanged. Preparatory bab02ccf/runtime 1.0.0 images are preserved outside
the public tree and are not 1.1.0 screenshots.
The diagnostic observation that `ModuleScanTab.thread` shadows `QObject.thread()`
is not a demonstrated cause of R08-08; that attribute has not been changed.
