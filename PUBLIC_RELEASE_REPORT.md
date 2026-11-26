# Public release preparation report

> **Post-release archival update (2026-11-26):** v1.0.0 was subsequently
> published on GitHub and archived on Zenodo under version DOI
> `10.5281/zenodo.24546973` (concept DOI `10.5281/zenodo.24546972`). Statements
> below about actions not yet performed describe the preparation snapshot.

**Project:** Prime Grid Atlas 1.0.0

**Subtitle:** An Open Experimental Number Theory Laboratory

**Date:** 2026-11-26

**Preparation branch:** `release/v1.0.0-prep`

**Status:** **READY WITH DOCUMENTED LIMITATIONS**

## Executive decision

The software, CPU test suite, research artifacts and public documentation are
technically prepared and selectively staged. The owner has confirmed the public
identity and copyright holder `zampro79`, Copyright 2026, and explicitly
approved the MIT License. The former legal and attribution blockers are
resolved. Publication may proceed after the owner separately authorizes the
prepared Git operations.

Historical PDF/DOCX papers, historical images, two provenance-incomplete
screenshots and the local Git helper have been excluded through `.gitignore`;
their local originals were preserved and hashed in `EXCLUDED_MATERIALS.md`.

The accessible Git history contains one initial commit whose only payload is
the former 18-byte `README.md`. The candidate index now contains 86 reviewed
files, 2,734,443 bytes in the working-tree representation. There are no
unstaged or non-ignored untracked files.

No commit, tag, push, GitHub release, visibility change, DOI or history rewrite
was performed.

## Changes made

### Numerical and API corrections

- `atlas_engine.py`
  - validates positive dimensions, volume limit, complete int64 interval and
    prime-family partner operations before every request;
  - validates cached requests instead of allowing the cache to bypass a lowered
    safety limit;
  - rejects `random_trials < 1` before running a scan.
- `metrics.py`
  - replaces the roundoff-sensitive positive-bin spectral-entropy denominator
    with the fixed non-DC support `log2(W*H-1)`;
  - evaluates nonconstant one-dimensional FFT fields;
  - rejects nonpositive baseline trial counts.
- `grid_model.py`
  - strictly validates `XY`, `XZ` and `YZ` rather than treating unknown planes
    as YZ.
- `app_config.py`
  - rejects NaN and infinity in scientific/rendering floating configuration.
- `compute_backend.py`, `qt_app.py`
  - expose machine-readable requested/available/runtime backend state;
  - scan metadata distinguishes the requested mode from runtime policy;
  - placement comparison records its forced CPU backend state.

### Regression coverage

The three former expected failures are ordinary passing regressions:

- spectral entropy is invariant under the audited reflection case;
- overflowing int64 intervals are rejected;
- cached volumes obey a subsequently lowered safety limit.

Additional tests cover family-partner overflow, unknown planes, non-finite
configuration, nonpositive trial counts, one-dimensional FFT metrics and backend
provenance. The suite increased from 67 to 72 tests.

### Public documentation and release assets

- Reorganized `README.md` as the public entry page.
- Added `RESEARCH_FINDINGS.md` as a concise Phase I/II synthesis.
- Integrated Phase II links and current metric behavior into `RESEARCH.md`,
  `ARCHITECTURE.md` and `PROJECT_CONTEXT.md`.
- Preserved the Phase I audit as a historical snapshot and added a current
  status note instead of rewriting old results.
- Added `GITHUB_METADATA.md` and `RELEASE_NOTES_v1.0.0.md`.
- Added `.github/workflows/cpu-tests.yml` for Python 3.11/3.12 CPU CI.
- Updated `CHANGELOG.md` and `RELEASE_CHECKLIST.md`.
- Replaced machine-specific absolute paths in public text with portable wording.
- Updated the verified GitHub repository URL in `CITATION.cff`; the unknown
  author was deliberately not invented.

## Files created during release preparation

- `.github/workflows/cpu-tests.yml`
- `GITHUB_METADATA.md`
- `PUBLIC_RELEASE_REPORT.md`
- `RELEASE_NOTES_v1.0.0.md`
- `RESEARCH_FINDINGS.md`

Phase II files created immediately before this release task and now integrated:

- `research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md`
- `research_ii/README.md`
- `research_ii/research_ii_experiments.py`
- `research_ii/verify_theorems.py`
- `research_ii/data/*.csv`
- `research_ii/data/manifest.json`

## Files modified during release preparation

- Runtime: `app_config.py`, `atlas_engine.py`, `compute_backend.py`,
  `grid_model.py`, `metrics.py`, `qt_app.py`.
- Tests: `tests/test_core.py`, `tests/test_export_provenance.py`,
  `tests/test_fft_metrics.py`, `tests/test_known_scientific_issues.py`,
  `tests/test_random_baseline.py`.
- Public documentation: `README.md`, `RESEARCH.md`, `ARCHITECTURE.md`,
  `PROJECT_CONTEXT.md`, `SCIENTIFIC_AUDIT.md`, `AUDIT_REPORT.md`, `AGENTS.md`,
  `BOOTSTRAP_REPORT.md`, `CHANGELOG.md`, `CITATION.cff`,
  `RELEASE_CHECKLIST.md`, `screenshots/README.md`.

No original paper, historical image, historical CSV, audit manifest or
application screenshot was deleted. Uncertain-rights material remains local
but is absent from the candidate index.

## Test and reproducibility evidence

### Clean environment

Temporary virtual environment, Linux, Python 3.14.7:

- NumPy 2.5.5
- Matplotlib 3.11.2
- Pillow 13.0.0
- PySide6 6.12.0
- pyqtgraph 0.14.0
- PyOpenGL 3.1.10

`pip install -r requirements.txt`: **PASS**

`pip check`: **PASS**, no broken requirements.

### Runtime and tests

| Check | Result |
|---|---|
| `python -m compileall -q .` | PASS |
| `python -m unittest discover -s tests -v` | PASS: 72 tests, 1 CUDA skip, 0 failures |
| Offscreen Qt MainWindow construction/render | PASS |
| Actual grid and FFT PNG writes to temporary storage | PASS |
| CSV/JSON export provenance regression | PASS |
| `research_ii/verify_theorems.py` | PASS |
| Phase II regeneration, seed 20261126, 240 trials | PASS |
| Generated Phase II CSV SHA-256 vs curated copies | IDENTICAL for all four CSVs |
| Local Markdown relative-link check | PASS: zero broken targets |
| `cffconvert 2.0.0 --validate` | PASS, CFF 1.2.0 |
| Interactive desktop/OpenGL inspection | NOT RUN |
| Real CUDA/CuPy equivalence | NOT RUN; hardware unavailable |

The first clean-install attempt failed because sandbox DNS was unavailable; the
approved network retry succeeded. That initial infrastructure failure is not
reported as a project test pass.

## Scientific compatibility note

The spectral-entropy normalization changed before the first official release.
Current values use a fixed non-DC denominator and are invariant under spectral
permutations. Audit-era CSVs use the former strictly-positive-bin denominator.
Historical data are preserved and labelled; values must not be compared across
definitions without recalculation.

The application still uses its documented uniform random baseline. Phase II
coprime/log/sieve models are independent research scripts, not GUI features.

## Privacy and security audit

Inspected source, Markdown, configuration, CSV/JSON text, accessible Git
history, PDF/DOCX metadata and PNG metadata.

Results:

- no apparent credentials, API keys, tokens, passwords or private keys;
- no personal email address in the release payload; Git history uses a GitHub
  noreply address;
- no absolute local user path remains in text files;
- `.gitignore` excludes virtual environments, caches, local configuration,
  generated results, uncertain-rights archives/images and local-only helpers;
- generated `__pycache__` files exist locally but are ignored and absent from
  Git status;
- PNG metadata contains no comments or EXIF payload in the inspected images;
- archived PDFs identify Author `ChatGPT Canvas` and Creator `ChatGPT`;
- the archived DOCX has an empty creator and 2026 timestamps.

The PDF/DOCX metadata do not establish human authorship; those files therefore
remain excluded. Automated pattern scanning cannot prove the absence of every
secret format.

Accessible Git history: one initial commit. No sensitive text pattern was found
in its tracked payload. History was not rewritten.

## License review

The repository contains the standard MIT License with Copyright (c) 2026
zampro79. `CITATION.cff` records the public author pseudonym and SPDX identifier
`MIT`. No legal name, affiliation, email, ORCID, DOI or release date was
invented.

Dependencies are installed from their own distributions and are not vendored.
The clean environment reports, among others, PySide6 under
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, pyqtgraph as MIT and PyOpenGL
as BSD-classified metadata. A source-only release does not relicense these
packages. Bundled executable distribution would require a separate detailed Qt
and third-party compliance review.

## Documentation status

The root README now contains the requested public structure, with technical
details routed to dedicated documents. Phase I and II are connected through a
concise findings page. All checked relative links resolve.

Genuine current-version screenshots with complete sidecars are still missing.
Two authentic viewport captures exist under `screenshots/`, but their complete
release parameters cannot be reconstructed, so they are not promoted in the
root README. Historical images remain explicitly labelled.

## Remaining limitations

- The prime sieve allocates up to the maximum integer rather than using a
  segmented interval sieve; valid but very large Start values can exhaust RAM.
- Hit arrays use int32 and extreme headless dimensions beyond GUI limits are not
  certified, although the configured volume cap constrains normal operation.
- Scan/comparison jobs share global backend/config/cache state and should run
  sequentially.
- Individual PNG exports do not have complete experiment sidecars.
- No automatic confidence intervals, p-values or multiple-comparison control.
- Uniform application null does not remove modular admissibility.
- Interactive OpenGL and actual CUDA execution remain unverified.

## Owner decisions resolved

The owner confirmed:

1. public author and copyright holder: `zampro79`;
2. copyright year: 2026;
3. license: MIT, explicitly approved;
4. version: 1.0.0 and open-source distribution;
5. uncertain-rights historical material remains excluded.

Provenance-complete screenshots, interactive desktop/OpenGL testing and real
CUDA testing are documented limitations, not blockers for this source release.

No DOI, release date or author field should be added before the corresponding
facts exist.

## Version assessment

Current version: `1.0.0`

Recommended version: `1.0.0`

Increment: no change

Reason: these are pre-release correctness fixes and documentation consolidation
for the already designated first official release. No prior public 1.0.0
contract is being superseded. Historical outputs retain their original labels.

Version update: not required.

## Final publication commands — do not run without separate authorization

First review exactly what would enter the initial release:

```bash
git switch release/v1.0.0-prep
git status --short
git diff --cached --name-status
git diff --cached --stat
git diff --cached
git ls-files --others --exclude-standard
```

The identity, license and selective staging are complete. Before commit:

```bash
git diff --cached --check -- . ':(exclude)**/*.csv'
git diff --cached --stat
git diff --cached
python -m unittest discover -s tests -v
python research_ii/verify_theorems.py
git commit -m "Prepare Prime Grid Atlas v1.0.0 public release"
```

Push the reviewed preparation branch:

```bash
git push -u origin release/v1.0.0-prep
gh pr create --base main --head release/v1.0.0-prep --title "Prime Grid Atlas v1.0.0" --body-file RELEASE_NOTES_v1.0.0.md
```

After separate approval, merge the reviewed pull request without rewriting
history. Substitute the actual pull-request number for `<PR_NUMBER>`:

```bash
gh pr merge <PR_NUMBER> --merge
```

Only after the merge is approved and completed:

```bash
git switch main
git pull --ff-only
git tag -a v1.0.0 -m "Prime Grid Atlas v1.0.0"
git push origin v1.0.0
```

After separate publication authorization:

```bash
gh release create v1.0.0 --title "Prime Grid Atlas v1.0.0" --notes-file RELEASE_NOTES_v1.0.0.md --verify-tag
```

Changing repository visibility and enabling Zenodo remain separate explicit
owner actions.

## Exact candidate-tree summary

- Files: 86 (`git ls-files` is the canonical complete path list).
- Size: 2,734,443 bytes (sum of the 86 working-tree file sizes).
- Diff against the accessible initial commit: 86 files changed, 21,527
  insertions, 1 deletion.
- Index/worktree divergence: none.
- Non-ignored untracked files: none.
- `git diff --cached --check` passes for source and documentation. Generated
  CSVs retain their verified CRLF byte representation and are excluded from
  that whitespace-only check because normalization would invalidate their
  recorded reproducibility hashes.

The complete publication inventory is the output of:

```bash
git ls-files
```

It consists of the root release/documentation files, nine Python runtime modules,
two requirement files, 12 test modules, the English/Italian manuals and
protocols, the complete `docs/scientific_audit/` dataset, the complete
`research_ii/` report/scripts/dataset, one CI workflow, one audit tool and only
the README from `screenshots/`. The exact excluded paths and SHA-256 digests are
listed in `EXCLUDED_MATERIALS.md`.
