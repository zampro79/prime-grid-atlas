# Release checklist — v1.1.0

**Integrity, Reproducibility & Reliability Update — preparation, not published.**
The historical [v1.0.0 checklist](RELEASE_CHECKLIST.md) remains unchanged.
This checklist is for final-source/artifact acceptance, not a claim that every
publication gate has been completed by a working-tree test run.

## Versioned source and documentation

- [x] Author approved the official runtime label 1.1.0 and MINOR scope.
- [x] Keep configuration schema 1, provenance schema pga.provenance/1.0,
  mathematical definitions, dependencies and 1024 MiB default cap unchanged.
- [x] Prepare current README, Known Issues, changelog and release notes.
- [x] Preserve the original v1.0.0 citation, DOI, tag and historical evidence.
- [ ] Author approves the complete STEP 10R diff and a separately authorized commit.
- [ ] Record the actual source commit S and verify source hashes and clean status.

## Final validation

- [x] STEP 10R working-tree checks completed in both existing CPU environments:
  unittest, compileall, theorem verification, native version/export and fresh
  11/11 Research I plus 4/4 Research II CSV baseline comparisons. No new crash
  observed; R08-08 remains unresolved.
- [ ] Reconcile working-tree validation evidence with committed source S.
- [ ] Full unittest suite in each existing environment with faulthandler: 169
  tests, 168 passed, one real-CUDA skip, no failures or new native crash.
- [ ] compileall and Research II verifier conform.
- [ ] Fresh fixed non-DC Research I and Research II reruns match relevant
  baselines: 11/11 and 4/4 CSVs in each environment.
- [ ] Native application launch/title and export report 1.1.0; provenance schema
  remains pga.provenance/1.0, with actual source identity/dirty state.
- [ ] Historical package/checksums, 33 historical files and 32 preparatory files
  remain intact; links and CFF syntax/coherence checks pass.
- [ ] Record validation limits honestly; do not mark CUDA/non-Linux/thread safety
  validated through skips or simulations.

## Visual examples and privacy

- [ ] Approve a portable future capture procedure before running it.
- [ ] Generate authentic 1.1.0 material from S, not from a later asset commit.
- [ ] Main README uses no more than four approved images; complete gallery has
  coprimality, scan and native viewport/framebuffer details.
- [ ] Inspect actual renderer, configuration/result correspondence, native
  manifests, completeness, hashes and all visible/embedded privacy fields.
- [ ] Close R08-07 only after the definitive public files pass review.
- [ ] Keep preparatory bab02ccf/runtime 1.0.0 evidence unchanged/private; use an
  explicit allow-list for new public assets, never blanket staging of examples/.
- [ ] Author approves the distinct documentation/asset commit D. Artifacts still
  identify application source S, not D.

## Residual-risk decision and publication metadata

- [ ] Author explicitly accepts final R08-08 risk for publication separately
  from the already accepted preparation/local-commit risk. It remains HIGH /
  OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN, not FIXED.
- [ ] Public Known Issues and release metadata disclose possible unsaved-work
  loss, interrupted exports and unknown root cause/scope without invented odds.
- [ ] Establish the actual 1.1.0 DOI/date through a separately authorized process;
  resolve citation/source-archive sequencing before publication.
- [ ] Complete CITATION.cff consistently; never assign the 1.0.0 version DOI to 1.1.0.
- [ ] Review GitHub/Zenodo version, author, license, links and source ZIP identity.
- [ ] Obtain explicit final approval before any merge, push, tag, GitHub release
  or Zenodo publication. Preserve the original deposit and concept family.

Until these gates are satisfied, publication remains suspended. A passing test
run is not a declaration that R08-08 is resolved or that an export is universally
safe against native termination.
