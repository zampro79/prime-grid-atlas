# Public release preparation audit

> **Version correction (2026-09-10):** the owner established `1.0.0` as the first official release. References below to `2.00.0` describe metadata observed during this historical audit and do not identify an official release.

> **Current status:** this document is a historical audit snapshot. The later
> public-release report records the pre-release numerical fixes, Phase II,
> privacy review and current validation results. Its former pending identity
> and license findings were resolved on 2026-11-26: public identity `zampro79`,
> Copyright 2026, MIT License. Statements below that these decisions remain
> open describe the audit date, not the v1.0.0 release candidate.

## Scope and outcome

Reviewed all application modules, requirements, existing tests, current and
historical Markdown, runtime/export JSON, CSV headers/data patterns, PDF text
and metadata, DOCX XML/metadata and PNG metadata. This audit concerns the project
working tree, not the history or unrelated contents of its parent repository.
No push, tag, commit, repository initialization or index mutation was performed.

The release documentation and conservative fixes are applied. Public release
still requires owner identity, repository URL and license decisions. Numerical
formulas, scoring, baselines, primality and placement algorithms are unchanged.

## Created files

- `.gitignore`
- `README.md` (replaces lowercase `readme.md`)
- `RESEARCH.md`
- `CITATION.cff`
- `LICENSE_CHOICE.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `config.example.json`
- `screenshots/README.md`
- `RELEASE_CHECKLIST.md`
- `AUDIT_REPORT.md`
- `tests/test_export_provenance.py`

## Modified files

- `qt_app.py`: current version normalized to 2.00.0; capture scan and placement
  scientific configuration at run start; export scan version, parameters and
  status with CSV and batch image metadata. Clear prior rows before a new scan
  so old results cannot acquire a new scan's metadata after failure.
- `atlas_engine.py`: removed the unused `is_prime` import only.
- `doc/README.md`: version and standalone documentation navigation.
- `doc/evidence/README.md`: unavailable sibling CSVs listed as an inventory,
  without broken links suggesting the files are included.
- `doc/archive/README.md`: current-version reference and explicit historical
  methodology/attribution caveats.
- `doc/research_protocol.md`: distinguishes proposed statistics from implemented
  functionality; grammatical correction.
- `doc/software_manual.md`: version, placement-step and configuration wording.
- `readme.md`: replaced by canonical uppercase `README.md`.

Original PDFs, DOCX, historical evidence and local result data were preserved.

## Findings and corrections

1. **Export provenance bug (fixed):** scan CSV and screenshot metadata used live
   controls, and comparison configuration was read at export time. Changing
   controls after calculation could relabel results. The regression test now
   performs a CPU scan and comparison, edits controls/configuration, exports,
   and checks that original parameters survive.
2. **Release metadata:** UI/export version used a development suffix, while the
   entry point identified 2.00.0. Current metadata now agrees. Old export version
   strings remain intact to preserve provenance.
3. **Missing public materials:** added ignore rules, public documentation,
   configuration example, contribution/citation/license-decision materials and
   release checklist. No definitive LICENSE was inferred.
4. **Dependencies:** the normal interpreter lacked Matplotlib, pyqtgraph and
   PyOpenGL; the declared CPU requirements installed successfully in a fresh
   virtual environment. The GPU requirements repeat OpenGL dependencies from the
   CPU requirements, harmlessly. Existing version lower bounds are retained;
   they are not a fully tested compatibility matrix or a dependency lockfile.
5. **Paths and artifacts:** no machine-specific execution path was found in
   application code. Runtime config intentionally lives beside the source.
   Historical sibling-dataset links would break in a standalone publication and
   were replaced with unavailable-dataset inventory text. Local caches/results
   are ignored for a new repository; existing tracked results in the parent Git
   repository remain tracked. Use the isolated-copy commands in the checklist.
6. **Sensitive data:** pattern inspection found no apparent embedded tokens,
   private keys, personal email addresses or absolute user paths in the inspected
   source/data/document payloads and image metadata. This is not a guarantee
   about Git history, image pixels or all possible secret formats. No human
   author could be established: historical Markdown uses a placeholder, DOCX
   creator is empty, and PDF metadata says Author “ChatGPT Canvas”, Creator
   “ChatGPT”. Confirm attribution and rights before public distribution.
7. **Code quality:** one clearly unused import was removed. No invasive
   refactoring or removal of experimental features was performed. Parallel CPU
   and GPU implementations of metrics/sieves are intentional fallback paths.

## Scientific and remaining implementation limitations

- The random baseline fixes alive count but resamples positive hits with
  replacement. It does not preserve the exact histogram or coprime support.
- Binary coprime masks and observed hit fields have different distributions;
  residuals do not isolate a proven prime-specific component.
- Entropy/FFT fields differ by view: slice analytical views can measure integer
  values, while scan FFT uses occupancy. Scalar modes keep current-slice scalar
  values; placement comparisons use selection masks even for scalar modes.
- Coprime residuals and placement distances combine unstandardized metrics.
  Scores provide no p-values, confidence intervals or multiple-testing control.
- YZ step is 1; its coprime control is degenerate. M=XY metadata is not the
  orthogonal progression step in XZ/YZ.
- FFT metrics return zeros for singleton dimensions, although the display can
  have nonzero one-dimensional power. No behavior was changed silently.
- Most planar placements retain XY steps across z, despite older wording that
  implied all nonlinear placements destroy these progressions. Planar geometry
  changes, and helix orientation can alter the vertical progressions too.
- Historical global-entropy interpretations and claims of statistical
  significance are not established by this audit. Future tests and null models
  in the 30p draft are not implemented capabilities.
- The volume limit does not bound the sieve's maximum integer, all temporaries,
  scan row count or total memory. Extreme headless int64 inputs are not certified.
- Direct headless configuration changes should clear volume caches; cached volume
  results are keyed by GridConfig rather than every global configuration field.
- Module scan and placement comparison share backend/configuration/cache state;
  simultaneous runs are not covered by thread-safety guarantees. Run them
  sequentially. This audit did not redesign their execution model.
- PNGs exported individually do not capture full provenance. CSV/batch sidecars
  still omit commit, dependency versions, actual per-row backend and raw trials;
  keep these separately for research use. GPU equivalence remains untested.

## Validation results

Fresh temporary virtual environment, Linux, Python 3.14.7:
NumPy 2.5.3, Matplotlib 3.11.1, Pillow 12.3.0, PySide6 6.11.2,
pyqtgraph 0.14.0, PyOpenGL 3.1.10. These are observed installed versions,
not claims of minimum compatible versions.

| Check | Result |
|---|---|
| Clean install from requirements.txt | PASS |
| pip check | PASS, no broken requirements |
| Syntax compilation of every .py | PASS |
| Import of all 9 application modules and pyqtgraph.opengl | PASS |
| Existing CPU numerical/configuration regression suite | 20/20 PASS |
| New Qt export provenance regression | 1/1 PASS |
| Default example configuration construction/load | PASS |
| Repeated seeded CPU baseline on XY/XZ/YZ | PASS |
| Offscreen CPU MainWindow construction and 2D rendering | PASS |
| Actual FFT and heatmap PNG export using Matplotlib Agg | PASS |
| CITATION.cff, cffconvert 2.0.0 / CFF schema 1.2.0 | PASS; owner placeholders remain |
| Interactive desktop/3D OpenGL rendering | NOT TESTED |
| CUDA computation / CPU-GPU equivalence | NOT TESTED |

The regression test mocks file dialogs and batch figure rendering to inspect
metadata; separate smoke checks actually render FFT and heatmap PNGs into a
temporary directory. No synthetic research-result screenshots were added.

## Human decisions before publication

Confirm public author, repository URL, copyright and historical material rights;
choose a license and decide which historical papers/screenshots to publish.
MIT allows permissive downstream reuse subject to notices; GPL-3.0 requires
copyleft conditions and corresponding source for covered distributions. Consult
[LICENSE_CHOICE.md](LICENSE_CHOICE.md) and its primary-source links, including
Qt's separate licensing terms. No license was selected automatically.

Complete desktop/GPU testing as relevant, review the standalone publication
copy, then execute the proposed Git commands in
[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Add Zenodo/DOI metadata only after
an actual archival release exists.
