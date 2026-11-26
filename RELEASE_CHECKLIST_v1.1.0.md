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
- [x] Author approved STEP 10R and the source commit S (STEP 10R.1).
- [x] Source S = eaf6c433722521c5f0dd6a6b07e112e643b5d05b; capture and verification used a separate clean checkout.

## Final validation

- [x] STEP 10R working-tree checks completed in both existing CPU environments:
  unittest, compileall, theorem verification, native version/export and fresh
  11/11 Research I plus 4/4 Research II CSV baseline comparisons. No new crash
  observed; R08-08 remains unresolved.
- [x] Reconcile original preparation records with S; preserve original evidence and source hashes.
- [x] STEP 10R.4 full unittest suite in each existing environment with faulthandler: 169
  tests, 168 passed, one real-CUDA skip, no failures or new native crash.
- [x] STEP 10R.4 compileall and Research II verifier conform in both existing environments; no historical module imported by tests/startup.
- [x] STEP 10R.6 fresh fixed non-DC Research I and Research II reruns from the
  extracted D distribution matched 11/11 and 4/4 baseline CSVs per environment.
- [x] STEP 10R.6 both existing Linux CPU suites passed 169 tests (168 passed, one
  CUDA skip), compileall, Research II and no-Git runtime/provenance checks.
- [x] Source-S native launch/title/export evidence reports 1.1.0; integrated current startup smoke passed in both environments. Provenance schema
  remains pga.provenance/1.0, with actual source identity/dirty state.
- [x] Historical package/checksums, 33 scientific historical files and 32 separately preserved preparatory files remain intact; integrated links/checksum checks pass.
- [x] STEP 10R.6 validated the complete current CFF against official schema 1.2.0;
  STEP 10R.8 repeats validation with the reserved 1.1.0 DOI and no release date.
- [x] Author authorized planned date 2026-11-27 in STEP 10R.9; CITATION.cff
  records it as date-released and is validated against CFF 1.2.0.
- [ ] Confirm that publication can occur on that planned date; if it cannot, stop
  publication and request metadata realignment before proceeding.
- [x] Record validation limits honestly; do not mark CUDA/non-Linux/thread safety
  validated through skips or simulations.

## Visual examples and privacy

- [x] Author approved the portable capture procedure and final STEP 10R.2 artifacts.
- [x] Eleven authentic modern PNGs and seven examples were generated from S; their bytes are unchanged during integration.
- [x] Main README uses four approved modern images; complete gallery has
  coprimality, scan and native viewport/framebuffer details.
- [x] Inspect actual renderer, configuration/result correspondence, native
  manifests, completeness, hashes and all visible/embedded privacy fields.
- [x] STEP 10R.6 reviewed all 205 candidate-D files and all PNG metadata/images;
  R08-07 FIXED for the exact complete reviewed distribution. Review later changes
  and the final archive without relabelling the original evidence.
- [x] Keep all 32 preparatory bab02ccf/runtime 1.0.0 files unchanged outside the public tree; use an
  explicit allow-list for new public assets, never blanket staging of examples/.
- [x] Preserve author-approved historical Celle Primi source under MIT, with four contemporary captures and its original NameError/layout limits. Exclude it from current scientific validation.
- [x] Rerun the seven-example numeric verifier on a separate copy against clean S: arithmetic, FFT, 6406 3D positions, 14 placements, 49 scan rows, five sidecars and seven native outputs.
- [x] Author approved documentation/asset commit D =
  5335d72191458021145c5a6553dd81efc9d3fc67. Artifacts still identify S, not D.

## Residual-risk decision and publication metadata

- [x] Author explicitly accepted residual R08-08 risk for publication in
  STEP 10R.9, separately from preparation/local-commit risk. It remains HIGH /
  OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN, not FIXED. This acceptance is not
  authorization to publish.
- [x] Public Known Issues and release metadata disclose possible unsaved-work
  loss, interrupted exports and unknown root cause/scope without invented odds.
- [x] Author reserved 1.1.0 DOI 10.5281/zenodo.24573039 in a new version draft
  in the existing concept series. The DOI is not yet registered by publication.
- [x] CITATION.cff includes that reserved DOI; the 1.0.0 DOI is not reassigned.
- [x] Author authorized the planned date and local metadata commit M in
  STEP 10R.9; preserve citation/source-archive sequencing in ZENODO.md.
- [ ] Author approves the final archive and publication texts after validation.
- [ ] Review GitHub/Zenodo version, author, license, links and source ZIP identity.
- [ ] Obtain explicit final approval before any merge, push, tag, GitHub release
  or Zenodo publication. Preserve the original deposit and concept family.

STEP 10R.4 checks conserved STEP 10R Research I fixed non-DC and Research II
outputs against retained baselines (11/11 and 4/4 per environment); it does not
claim a new regeneration. STEP 10R.6 subsequently performed fresh reruns from
the extracted D distribution and verified all 205 files. Source S remains fixed
in original manifests. STEP 10R.9 authorizes local commit M and final archive
preparation with planned date 2026-11-27, not tag creation or publication. The
actual publication remains pending.

Until the remaining gates are satisfied, publication remains suspended. A passing test
run is not a declaration that R08-08 is resolved or that an export is universally
safe against native termination.
