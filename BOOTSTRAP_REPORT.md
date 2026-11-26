# Persistent-context bootstrap report

> **Version correction (2026-09-10):** the owner established `1.0.0` as the first official release after this snapshot was written. References below to `2.00.0`, `v2.00` or `v200` record the earlier, incorrect labels found during the bootstrap; they are not official release identifiers. Current code and documentation use `1.0.0`.

> **Release-state correction (2026-11-26):** the owner subsequently confirmed
> public identity and copyright holder `zampro79` and approved the MIT License.
> Pending identity/license statements below are retained only as historical
> bootstrap observations and do not describe the v1.0.0 release candidate.

## Owner-approved follow-up

After the bootstrap, the owner designated a standalone repository as the definitive working directory and authorized the proposed documentation updates. The sections below retain the original bootstrap snapshot, including its file counts, line references, initial no-edit outcome and then-pending proposals; they are not a fresh inventory of the standalone repository.

Applied in the English documents: manual qualifications D2–D7, protocol clarifications D8–D9, an explicit open methodological note for D15 without changing the equation, RESEARCH input/range and H1 notes (D10), README navigation, and the approved Added/Fixed changelog entries (D12). AGENTS.md, PROJECT_CONTEXT.md and RELEASE_CHECKLIST.md now describe the definitive standalone location. ARCHITECTURE.md points to the updated methodological notes.

No version normalization, numerical fix, citation metadata, license choice or historical evidence rewrite is included. D1, D13 and the methodological choice in D15 remain open; D11/D14 remain preserved historical evidence. Italian originals remain unchanged. Authorization to clarify documentation does not resolve the underlying scientific bugs or select the proposed distance's reference center.

## Repository analyzed

Scope: the current `prime_grid_atlas_v200_pyside6` project directory, including its existing local results for schema/provenance review; not unrelated projects or the history of the enclosing Git repository. Baseline recorded on 2026-09-10 before writing the new files. `SCIENTIFIC_AUDIT.md` and `doc/research_protocol.md` already had uncommitted translation changes; this bootstrap preserves them byte for byte.

Inventory before this task: **130 files excluding caches/environments**: 24 Python files (9 application modules, 14 test/helper files, 1 experiment script), 22 Markdown files, 6 JSON files, 13 CSV files, 3 TXT files, 1 CFF file, 1 `.gitignore`, 57 PNGs, 2 PDFs and 1 DOCX. The 70 textual files were reviewed for their role, implementation/documentation relationships or data schema; generated data were parsed rather than treated as source. All 13 CSVs have consistent row widths. Two older scan datasets have 10,000 and 441 rows, each with 58 columns. The 11 curated audit CSVs include 1,500 null trials and use the audit script's separate schema.

Of the 130 files, 54 are local `results/` artifacts already tracked in the parent Git repository. The remaining 76 comprise current source, documentation, tests and curated evidence. No project-local `AGENTS.md`, `PROJECT_CONTEXT.md`, `ARCHITECTURE.md` or `VERSIONING.md` existed. `RESEARCH.md` did exist and was reviewed in full. No applicable ancestor AGENTS file was found. No packaging manifest, pytest configuration, CI workflow or `examples/` directory was present in this project.

PDF text/metadata and DOCX document/core XML were inspected for historical role and conflicting claims. PNGs were inventoried as illustrations or experiment outputs; their visual content was not independently validated in this bootstrap. No claims about new prime properties, graphical correctness or the parent's Git history follow from this review.

## Created

- [AGENTS.md](AGENTS.md): concise persistent policy, reading route, impact analysis and approval/report requirements.
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md): project purpose, verified model, scope and scientific cautions.
- [ARCHITECTURE.md](ARCHITECTURE.md): module responsibilities, inputs/outputs, callers, data flow, metric/field/export contracts and test routes.
- [VERSIONING.md](VERSIONING.md): owner-confirmed bump workflow, scientific compatibility policy and proposed version source strategy.
- `BOOTSTRAP_REPORT.md`: this review record, discrepancies and file/version inventory.

## Modified

**No pre-existing file modified by this bootstrap.** `RESEARCH.md` was verified and retained. Application code, tests, configuration, dependencies, README, CHANGELOG, CFF, license state and original evidence are unchanged. The two pre-existing translation diffs remain distinguishable from the five new documentation files.

## Architecture discovered

`main.py` enters `qt_app.run`, which creates/reuses QApplication, loads an optional application profile and constructs MainWindow. GUI controls create a GridConfig; the headless engine assigns integers, dispatches arithmetic selections/scalars, requests slices/cumulative hits, and computes metrics or display fields. `metrics.py` owns entropy/FFT/beauty and uniform-null generation; the engine assembles coprime/random comparisons and metadata. `number_theory.py` supplies CPU arithmetic, `compute_backend.py` optional CuPy operations with CPU retry, and `grid_model.py` projection shapes and spherical coordinates.

Scan iteration belongs to a Qt worker thread; placement comparison runs CPU calculations in GUI-thread timer steps. GUI classes own all interactive export schemas. The audit script is a separate headless experimental CLI, not the GUI scan CLI. Global profile/backend/cache state is shared rather than isolated per job. Rendering and scientific computation are distinct, although field routing and export provenance in the GUI have scientific consequences.

## Mathematical model verified

Direct inspection of `build_volume`, `get_plane_data`, `_base_and_step` and metric implementations confirms Linear `n=Start+x+Xy+XYz`, array order `(Z,Y,X)` and increments 1, X, XY in the supported integer range. XY/XZ/YZ accumulate z/y/x with arithmetic steps XY/X/1; endpoints are inclusive. Scalar diagnostic values remain a current slice. Coprime admissibility is `gcd(base,step)==1` with explicit prime-divisor exceptions. The random baseline fixes alive count but resamples positive hits with replacement on unrestricted positions. FFT selection inputs are binary; scalar views retain amplitudes. Structural score and residuals are descriptive differences/norms, not inferential tests.

The existing independent-oracle tests cover these statements on finite cases. This bootstrap does not establish universal input validity, backend equivalence or new mathematics. Definition/input/range/interpretation/limitation contracts for important metrics are collected in ARCHITECTURE.md while proposed additions to the existing methodological reference await approval.

## Documentation inconsistencies and proposed changes

No pre-existing document or behavior has been changed to resolve these entries. Existing audit findings remain open unless their tests establish otherwise. Distinguish a demonstrated contradiction from an omission, historical statement or methodological decision.

| ID | File / section or location | Documentation says | Code/tests establish | Recommended action |
|---|---|---|---|---|
| D1 | Current version labels; README version line, CFF version, `qt_app.APP_VERSION` | Current application `2.00.0`; new owner policy requires Semantic Versioning | Sources agree on the label, but `00` is not a valid strict SemVer numeric component | Owner decides future canonical spelling; propose `2.0.0` normalization separately, not an automatic bump |
| D2 | `doc/software_manual.md` §11, rendering parameters; Italian source §11 | Configuration includes a maximum batch PNG side length | `export_max_side` is exposed/serialized but `save_heatmap_figure` uses fixed 10×8 inches at 180 dpi and never reads it | Add a short “currently not enforced” qualification; implementing a cap is a separate behavior change |
| D3 | Manual §9, `Linear 71×30×30` radial-direction paragraph; Italian source §9 | Each radial direction holds 30 values spaced by 2130 | Fixed shells preserve directions; nonzero layer rotation changes θ with z | Qualify the sentence with “For nonrotating spherical shells” |
| D4 | Manual §4, sentence following scalar FFT description; Italian source §4 | Modes can require factorization or digit iteration | Current 13-mode dispatch contains no digit-iteration mode | Remove “or digit iteration”; keep factorization cost caution |
| D5 | Manual §11, final sentence; Italian source §11 | Disabling Configuration during a scan prevents mixed-profile rows | Separate comparison/scan tabs share global state and can re-enable controls independently; no global job lock | Qualify guarantee and require sequential runs; do not redesign concurrency in this task |
| D6 | Manual §7 GPU list; Italian source §7 | Broad “GCD/coprime masks” acceleration | `compute_backend.coprime_mask` can accelerate the engine control; scalar GCD and direct Coprimes mode dispatch use NumPy, as does much of `prime_grid_metrics` | State which mask path is accelerated rather than implying all GCD diagnostics run on GPU |
| D7 | Manual §14 module list; Italian source §14 | `atlas_engine.py` described as engine and scan; `grid_model.py` as embedding and projections | Engine computes a configuration; pair iteration is `qt_app.ScanWorker`; integer placement is in engine, while grid_model handles slices and shell coordinates | Refine these two module labels; use new ARCHITECTURE.md for full ownership |
| D8 | `doc/research_protocol.md` §2; Italian source §2 | Linear is mandatory “because it preserves the vertical arithmetic progressions” | Fixed planar alternatives also preserve the vertical XY step; engine nevertheless explicitly restricts protocol metrics to Linear | Explain that Linear is the chosen full coordinate/protocol reference, not the only placement retaining z progressions |
| D9 | Protocol §17 Phase 2; Italian source §17 | “Add CPU/GPU equivalence tests” unchecked; general CLI proposed | Hardware-conditional equivalence test exists but hardware validation remains pending; an audit CLI exists but no general scan CLI | Split implemented test from unperformed hardware validation; distinguish audit CLI from proposed general CLI |
| D10 | `RESEARCH.md` Metrics and Current limitations | Correct formulas and cautions; many ranges are implicit and spectral support sensitivity is mentioned briefly | Local/global entropy are not [0,1]-normalized; Hspec can change from 1 to .5 under reflection (open test) | Optional targeted addition of input/range contracts and explicit link to H1; no formula correction needed |
| D11 | `doc/archive/complete_paper_v1.md` §§2,5,6.5,6.7,11; corresponding historical PDF/DOCX and revised PDF | Start-free mapping, Tkinter, spatial reading of global entropy, preserved hit distribution and significance language | Current GUI is PySide6, Start is explicit, histogram entropy is permutation-invariant, positive hits are resampled, no engine significance calibration | Preserve originals; existing archive disclaimer already flags limitations. Future paper revision needs independent evidence and owner approval |
| D12 | `CHANGELOG.md` release-preparation list versus subsequent scientific audit | Earlier preparation preserved numerical algorithms; later scalar-FFT fix is not listed | C1 subsequently fixed cached scalar mutation in `fft_spectrum`; regression exists | Add a separately approved Fixed entry; preserve the earlier historical statement rather than rewriting it |
| D13 | `CITATION.cff` authors/repository and absent license/date/DOI | Explicit placeholders | Code cannot establish owner identity or release metadata | Owner supplies real values; no inferred edits |
| D14 | `docs/scientific_audit/manifest.json` source hashes | Records the original experiment's nine module hashes | Only current metrics.py differs; comparison with the matching Git source shows executable AST unchanged after removing docstrings | Preserve manifest; existing translated audit already explains the comment/docstring translation, so no update required |
| D15 | Protocol §9 proposed Mahalanobis distance | Defines μ0/Σ0 from a null but centers the displayed difference on Gcoprime | Neither this distance nor its calibration is implemented; the draft's intended center is ambiguous | Owner/research decision: clarify deterministic control versus null mean before implementation; do not silently substitute a formula |

D1 is a syntax issue, not evidence of a runtime version mismatch: [SemVer rule 2](https://semver.org/#spec-item-2) forbids leading zeroes. The numerical choice and any migration of consumers require owner approval. D10 is an enhancement to an otherwise consistent methodological reference. D11 is historical disagreement already disclosed, not authorization to edit archival sources.

### README section-by-section review

| Section | Compared against | Outcome |
|---|---|---|
| Overview / Research scope / Scientific limitations | Engine baselines, scores and existing audits | Cautious research question; no unsupported discovery claim requiring a rewrite |
| Key features / Placements | Mode catalog, PLACEMENTS, comparison implementation | 13 modes and 14 placements match; Linear restriction and descriptive distance correctly qualified |
| Installation / CPU requirements / Running | Source layout, main.py, imports and requirements | Commands fit a source application; Python 3.10+ is stated with compatible-wheel qualification, not tested as a full compatibility matrix here |
| Optional CUDA/GPU | Probe, threshold, retry and diagnostics | Matches optional compute behavior; hardware verification remains unperformed |
| Mathematical model / Projections | build_volume, grid_model and base/step helper | Formula, shapes, scalar-slice distinction and YZ degeneration agree |
| Prime/coprime/random / Metrics | metrics.py and overlay_metrics | Fixed K and replacement sampling, field distinction and descriptive scores agree |
| Module scan | ScanWorker, SCAN_COLUMNS and snapshots | Fixed Primes/Linear, full depth, step-vs-M distinction and approximate pass cost agree |
| 3D visualization | spherical_shell_positions / show_3d | Equal-area bands and rendering-only role agree; physical display not validated |
| Basic workflow / Export | load_config and serializers | Profile-vs-experiment distinction and single-image provenance limitations agree; no claim of runtime job isolation |
| Repository structure | Current file inventory | Existing overview omits later scientific audit/script and new context files; optional navigation addition, not a behavioral contradiction |
| Version / Citation / License | APP_VERSION / CFF / absence of LICENSE | Existing values/placeholders agree; D1 and D13 remain owner decisions |

No mandatory README behavioral correction was found. A navigation link to PROJECT_CONTEXT.md and ARCHITECTURE.md would make the new material easier for humans to discover; AGENTS.md already routes future agents without requiring a README edit.

### Concrete documentation proposal awaiting authorization

1. Manual: apply the seven localized qualifications D2–D7 (D7 concerns two module labels), retaining formulas and numerical behavior. Leave `.it.md` originals unchanged and identify the English document as subsequently clarified if approved.
2. Protocol: clarify the Linear rationale and Phase 2 status (D8–D9), and add an explicit open methodological note for D15 without changing the proposed equation.
3. RESEARCH.md: add input/range notes for the metric table and link the open Hspec issue to the scientific audit (D10).
4. README.md: optionally add links to the new context/architecture documents and scientific audit under Repository structure.
5. CHANGELOG.md: proposed **Added** entry: “Persistent agent instructions, project context, architecture and versioning policy.” Proposed separate **Fixed** entry for the earlier C1 work: “Prevent scalar FFT display from modifying cached arithmetic fields.” Neither entry has been applied.
6. CITATION.cff: no edit until the owner provides real identity/publication values or explicitly authorizes an agreed version change.

Version normalization/refactoring is a separate decision and is not included in approval of these documentation clarifications.

## Version consistency

Runtime and export identification is centralized within `qt_app.APP_VERSION`, but documentation/CFF and one test assertion are independent copies. Current labels agree on `2.00.0`; two local historical manifests explicitly retain `1.90.0-pyside6-prime-focused`. Snapshot and dependency versions must not be replaced by search-and-replace.

The following table inventories version-bearing locations in the pre-bootstrap text. Repeated occurrences in one file are grouped by value with line numbers; locations refer to that snapshot. Schema versions are listed separately. Historical paper `v1` / `v3` filenames are document revision identifiers, not application version sources. New documents repeat current identity only as documented context.

| File | Location (snapshot lines) | Version / identifier | Purpose |
|---|---|---|---|
| `AUDIT_REPORT.md` | 120 | `0.14.0` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 135 | `1.2.0` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 119 | `12.3.0` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 135 | `2.0.0` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 32, 57 | `2.00.0` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 119 | `2.5.3` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 120 | `3.1.10` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 119 | `3.11.1` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 118 | `3.14.7` | Recorded audit build/environment; preserve snapshot |
| `AUDIT_REPORT.md` | 119 | `6.11.2` | Recorded audit build/environment; preserve snapshot |
| `CHANGELOG.md` | 19 | `2.00.0` | Current build/reference (independent text copy) |
| `CHANGELOG.md` | 3 | `v2.00.0` | Current build/reference (independent text copy) |
| `CITATION.cff` | 1 | `1.2.0` | CFF schema |
| `CITATION.cff` | 5 | `2.00.0` | Citation application version |
| `README.md` | 5 | `2.00.0` | Current build/reference (independent text copy) |
| `README.md` | 83 | `3.10` | Stated Python minimum, subject to compatible dependency wheels |
| `README.md` | 79 | `v170` | Historical generation/definition reference |
| `README.md` | 79 | `v2.00.0` | Current build/reference (independent text copy) |
| `RELEASE_CHECKLIST.md` | 14 | `1.2.0` | CFF schema validation reference, not an application version |
| `RELEASE_CHECKLIST.md` | 8 | `2.00.0` | Release checklist identity / proposed commands, not executed |
| `RELEASE_CHECKLIST.md` | 1, 16, 42, 45, 48 | `v2.00.0` | Release checklist identity / proposed commands, not executed |
| `SCIENTIFIC_AUDIT.it.md` | 254 | `2.5.3` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.it.md` | 254 | `3.14.7` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.it.md` | 254 | `6.11.2` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.it.md` | 5 | `v2.00.0` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.md` | 258 | `2.5.3` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.md` | 258 | `3.14.7` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.md` | 258 | `6.11.2` | Recorded audit build/environment; preserve snapshot |
| `SCIENTIFIC_AUDIT.md` | 9 | `v2.00.0` | Recorded audit build/environment; preserve snapshot |
| `app_config.py` | 9 | `CONFIG_SCHEMA_VERSION=1` | Configuration schema, separate from application version |
| `atlas_engine.py` | 605 | `v160` | Historical generation/definition reference |
| `atlas_engine.py` | 315 | `v200` | Current generation shorthand, not strict SemVer |
| `config.example.json` | 18 | `schema_version=1` | Configuration schema, separate from application version |
| `doc/README.it.md` | 6 | `2.00.0` | Preserved original build/generation reference |
| `doc/README.it.md` | 34, 38 | `v170` | Historical generation/definition reference |
| `doc/README.it.md` | 1 | `v2.00.0` | Preserved original build/generation reference |
| `doc/README.it.md` | 3, 8, 28, 40 | `v200` | Current generation shorthand, not strict SemVer |
| `doc/README.md` | 7 | `2.00.0` | Current build/reference (independent text copy) |
| `doc/README.md` | 29, 33 | `v170` | Historical generation/definition reference |
| `doc/README.md` | 1 | `v2.00.0` | Current build/reference (independent text copy) |
| `doc/README.md` | 5, 9, 25, 33 | `v200` | Current generation shorthand, not strict SemVer |
| `doc/archive/README.it.md` | 12 | `v170` | Historical generation/definition reference |
| `doc/archive/README.it.md` | 5, 26 | `v2.00.0` | Preserved original build/generation reference |
| `doc/archive/README.md` | 12 | `v170` | Historical generation/definition reference |
| `doc/archive/README.md` | 5, 26 | `v2.00.0` | Current build/reference (independent text copy) |
| `doc/evidence/README.it.md` | 1, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19 | `v170` | Historical generation/definition reference |
| `doc/evidence/README.it.md` | 28 | `v190` | Historical generation/definition reference |
| `doc/evidence/README.md` | 1, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20 | `v170` | Historical generation/definition reference |
| `doc/evidence/README.md` | 28 | `v190` | Historical generation/definition reference |
| `doc/research_protocol.it.md` | 88 | `v180` | Historical generation/definition reference |
| `doc/research_protocol.it.md` | 11 | `v2.00.0` | Preserved original build/generation reference |
| `doc/research_protocol.it.md` | 53, 80, 86, 676 | `v200` | Current generation shorthand, not strict SemVer |
| `doc/research_protocol.md` | 90 | `v180` | Historical generation/definition reference |
| `doc/research_protocol.md` | 14 | `v2.00.0` | Current build/reference (independent text copy) |
| `doc/research_protocol.md` | 59, 86, 90, 675 | `v200` | Current generation shorthand, not strict SemVer |
| `doc/software_manual.it.md` | 5 | `2.00.0` | Preserved original build/generation reference |
| `doc/software_manual.it.md` | 116 | `v160` | Historical generation/definition reference |
| `doc/software_manual.it.md` | 395 | `v170` | Historical generation/definition reference |
| `doc/software_manual.it.md` | 1 | `v2.00` | Preserved original build/generation reference |
| `doc/software_manual.it.md` | 478 | `v200` | Current generation shorthand, not strict SemVer |
| `doc/software_manual.md` | 9 | `2.00.0` | Current build/reference (independent text copy) |
| `doc/software_manual.md` | 116 | `v160` | Historical generation/definition reference |
| `doc/software_manual.md` | 306 | `v170` | Historical generation/definition reference |
| `doc/software_manual.md` | 1 | `v2.00` | Current build/reference (independent text copy) |
| `doc/software_manual.md` | 383 | `v200` | Current generation shorthand, not strict SemVer |
| `docs/scientific_audit/manifest.json` | 34 | `2.5.3` | Recorded audit build/environment; preserve snapshot |
| `docs/scientific_audit/manifest.json` | 36 | `3.14.7` | Recorded audit build/environment; preserve snapshot |
| `docs/scientific_audit/manifest.json` | 20 | `schema_version=1` | Configuration schema, separate from application version |
| `main.py` | 1 | `v2.00.0` | Current build/reference (independent text copy) |
| `mode_catalog.py` | 1 | `v200` | Current generation shorthand, not strict SemVer |
| `qt_app.py` | 84 | `2.00.0` | Runtime source for title and export metadata |
| `qt_app.py` | 149, 1545 | `v160` | Historical generation/definition reference |
| `qt_app.py` | 660 | `v170` | Historical generation/definition reference |
| `qt_app.py` | 1 | `v2.00.0` | Current build/reference (independent text copy) |
| `requirements-gpu-cuda12.txt` | 6 | `0.13.7` | Dependency constraint / CUDA profile |
| `requirements-gpu-cuda12.txt` | 7 | `3.1.7` | Dependency constraint / CUDA profile |
| `requirements-gpu-cuda12.txt` | 3 | `cupy-cuda12x[ctk]>=13` | Dependency constraint / CUDA profile |
| `requirements.txt` | 5 | `0.13.7` | Dependency constraint / CUDA profile |
| `requirements.txt` | 1 | `1.24` | Dependency constraint / CUDA profile |
| `requirements.txt` | 3 | `10.0` | Dependency constraint / CUDA profile |
| `requirements.txt` | 6 | `3.1.7` | Dependency constraint / CUDA profile |
| `requirements.txt` | 2 | `3.7` | Dependency constraint / CUDA profile |
| `requirements.txt` | 4 | `6.7` | Dependency constraint / CUDA profile |
| `results/1to100x_1to100y_100/atlas.config.json` | 30 | `schema_version=1` | Historical output provenance; preserve |
| `results/1to100x_1to100y_100/metric_screenshots.json` | 2 | `1.90.0-pyside6-prime-focused` | Historical output provenance; preserve |
| `results/1to100x_1to100y_100/metric_screenshots.json` | 20 | `schema_version=1` | Historical output provenance; preserve |
| `results/60to80x_20to40y_100/atlas.config.json` | 30 | `schema_version=1` | Historical output provenance; preserve |
| `results/60to80x_20to40y_100/metric_screenshots.json` | 2 | `1.90.0-pyside6-prime-focused` | Historical output provenance; preserve |
| `results/60to80x_20to40y_100/metric_screenshots.json` | 20 | `schema_version=1` | Historical output provenance; preserve |
| `screenshots/README.md` | 7 | `v170` | Historical generation/definition reference |
| `screenshots/README.md` | 3 | `v2.00.0` | Current build/reference (independent text copy) |
| `tests/test_core.py` | 1 | `v200` | Current generation shorthand, not strict SemVer |
| `tests/test_export_provenance.py` | 56 | `2.00.0` | Regression assertion or suite generation reference |

Proposed future single source: a dependency-free version module consumed by GUI/export and future headless tools; reviewed checks for CFF/current documentation. No refactoring implemented. Detailed policy is in VERSIONING.md.

## File-by-file review

Each textual file below was reviewed; no pre-existing edits were needed to create the bootstrap. `POTENTIALLY AFFECTED` means a concrete documentation/owner decision remains, not an unperformed source read. “Version” distinguishes release identity from schemas, historical references and dependency/environment records. Binary assets and generated image pixels are scoped separately above.

| File | Role | Behavior relevance | Documentation dependencies | Version dependencies | Review / inconsistencies |
|---|---|---|---|---|---|
| `.gitignore` | Local/output exclusion rules | New artifact tracking, not runtime | RELEASE_CHECKLIST; README Export | No version source | REVIEWED — no change required; 54 results already tracked |
| `AUDIT_REPORT.md` | Earlier release-preparation audit | Historical implementation/evidence record | README; release checklist; scientific audit | Recorded app/dependency versions | REVIEWED — no change required; not current test certification |
| `CHANGELOG.md` | Release-preparation history | Change provenance, no runtime | README; audit reports | v2.00.0 | POTENTIALLY AFFECTED — proposed Added/Fixed entries D12 |
| `CITATION.cff` | Citation metadata | Public attribution/version, no numerical input | README Citation; release checklist | CFF1.2.0; app2.00.0 | POTENTIALLY AFFECTED — owner placeholders and D1/D13; no edits |
| `CONTRIBUTING.md` | Contribution/reproduction guidance | Unittest and scientific reporting workflow | AGENTS; RESEARCH; LICENSE_CHOICE | No release source | REVIEWED — no change required; instructions remain compatible |
| `LICENSE_CHOICE.md` | Owner licensing decision note | No selected project license | README License; CFF; release checklist | SPDX/license labels, not app versions | REVIEWED — no change required; no license inferred |
| `README.md` | Public overview and usage | Features, launch, model and exports | RESEARCH/manual; new context navigation | 2.00.0 and Python floor | REVIEWED — no behavioral correction; optional navigation; D1 |
| `RELEASE_CHECKLIST.md` | Publication decision checklist | Proposed isolated publication workflow | README; CFF; LICENSE_CHOICE | 2.00.0; CFF1.2.0 | REVIEWED — no change required now; proposed commands not executed |
| `RESEARCH.md` | Implemented methodology | Baseline/field/metric interpretation | Engine and metric tests; scientific audit | No release source | POTENTIALLY AFFECTED — optional range/H1 detail D10; formulas agree |
| `SCIENTIFIC_AUDIT.it.md` | Italian audit original | Historical source for translation | English scientific audit | Recorded build/environment | REVIEWED — no change required; original preserved |
| `SCIENTIFIC_AUDIT.md` | Scientific audit English translation | Exact cases, findings, reproduction | RESEARCH; tests; audit CSV/manifest | Recorded build/environment | REVIEWED — no change required; pre-existing translation preserved |
| `app_config.py` | Application settings and JSON | Defaults, clamp/coercion, global snapshots | Manual §11; config example; ARCHITECTURE | Configuration schema 1 | REVIEWED — no change required; no general finite-value validation |
| `atlas_engine.py` | Headless orchestration | Placements, masks, projections, metrics | RESEARCH; ARCHITECTURE; scientific audit | v200/v160 comments | REVIEWED — no change required; known int64/cache issues |
| `compute_backend.py` | Optional CuPy and CPU retry | Prime/GCD/metric backend selection | README GPU; manual §7; ARCHITECTURE | No release source | REVIEWED — no change required; not all arithmetic accelerated |
| `config.example.json` | Portable default profile | Matches AppConfig fields and defaults | README workflow; manual §11 | Schema 1 | REVIEWED — no change required; not a complete experiment |
| `doc/README.it.md` | Preserved Italian source for doc/README.md | Historical parallel text, not runtime | English counterpart; paired formulas/sections | Preserved build/generation labels | REVIEWED — preserve original; counterpart findings apply as historical limitations |
| `doc/README.md` | Documentation index | Current versus historical navigation | Manual/protocol/archive/evidence | 2.00.0/v200; historical v170 | REVIEWED — no change required; new AGENTS supplies agent routing |
| `doc/archive/README.it.md` | Preserved Italian source for doc/archive/README.md | Historical parallel text, not runtime | English counterpart; paired formulas/sections | Preserved build/generation labels | REVIEWED — preserve original; counterpart findings apply as historical limitations |
| `doc/archive/README.md` | Historical archive disclaimer | Prevents treating papers as current specs | Manual/protocol and archive files | 2.00.0/v170; paper v1/v3 | REVIEWED — no change required; D11 already qualified |
| `doc/archive/complete_paper_v1.md` | Historical paper | Old hypotheses/claims, not runtime behavior | Archive disclaimer | Paper revision v1, not app version | REVIEWED — preserve historical content; D11 |
| `doc/evidence/README.it.md` | Preserved Italian source for doc/evidence/README.md | Historical parallel text, not runtime | English counterpart; paired formulas/sections | Preserved build/generation labels | REVIEWED — preserve original; counterpart findings apply as historical limitations |
| `doc/evidence/README.md` | Historical images/dataset inventory | v170 provenance; unavailable CSV names/hashes | doc index; README screenshots | v170/v190 | REVIEWED — no change required; do not infer missing dataset parameters |
| `doc/research_protocol.it.md` | Preserved Italian source for doc/research_protocol.md | Historical parallel text, not runtime | English counterpart; paired formulas/sections | Preserved build/generation labels | REVIEWED — preserve original; counterpart findings apply as historical limitations |
| `doc/research_protocol.md` | 30p research draft | Conjectures and planned controls, not engine spec | RESEARCH; scientific audit; audit script | 2.00.0/v200/v180 | POTENTIALLY AFFECTED — D8/D9/D15; pre-existing translation preserved |
| `doc/software_manual.it.md` | Preserved Italian source for doc/software_manual.md | Historical parallel text, not runtime | English counterpart; paired formulas/sections | Preserved build/generation labels | REVIEWED — preserve original; counterpart findings apply as historical limitations |
| `doc/software_manual.md` | Interactive user manual | Controls, views, exports and configuration | README; RESEARCH; scientific audit | v2.00,2.00.0,v160,v170,v200 | POTENTIALLY AFFECTED — targeted D2–D7 proposals |
| `docs/scientific_audit/aspect_summary.csv` | Experiment table: 4 rows, 12 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/aspect_trials.csv` | Experiment table: 200 rows, 12 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/density_summary.csv` | Experiment table: 5 rows, 10 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/density_trials.csv` | Experiment table: 250 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/manifest.json` | Audit reproduction metadata | Configuration, source hashes and environment | Scientific audit; experiment script | Schema1; Python/NumPy snapshot | REVIEWED — preserve; metrics hash differs only by translation D14 |
| `docs/scientific_audit/null_controls.csv` | Experiment table: 2 rows, 10 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/null_summary.csv` | Experiment table: 27 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/null_trials.csv` | Experiment table: 1500 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/placement_metrics.csv` | Experiment table: 42 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/scalar_fft_regression.md` | C1 before/after evidence | Private buffer prevents scalar cache mutation | FFT test; scientific audit C1 | No release source | REVIEWED — no change required; do not rerun over old evidence |
| `docs/scientific_audit/start_z_m30.csv` | Experiment table: 100 rows, 16 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/symmetry_metrics.csv` | Experiment table: 10 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/synthetic_metrics.csv` | Experiment table: 10 rows, 11 columns | Historical schema/data; all row widths checked | Scientific audit + experiment script | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `docs/scientific_audit/test_results.txt` | Archived unittest output | 67-test historical run, not current validation | Scientific audit | No release source | REVIEWED — preserve snapshot; new test run reported separately |
| `grid_model.py` | Slices/hits and shell coordinates | Axis order; rendering transform | RESEARCH projections; manual §§5/9; ARCHITECTURE | No release source | REVIEWED — no change required; unknown planes fall through to YZ |
| `main.py` | Desktop entry point | Startup → qt_app.run | README Running; ARCHITECTURE | Build docstring | REVIEWED — no change required; no forced display backend |
| `metrics.py` | Metric and random-control definitions | All numerical comparisons | RESEARCH Metrics/Randomized baseline; ARCHITECTURE | No release source | REVIEWED — no change required; Hspec support issue; D14 |
| `mode_catalog.py` | Mode-name partition | GUI catalog; engine dispatch must agree | README features; manual §4 | v200 comment | REVIEWED — no change required; 4+4+5 names |
| `number_theory.py` | CPU sieve and arithmetic | Prime/family/helper semantics | RESEARCH controls; scientific audit §§3–5 | No release source | REVIEWED — no change required; nonpositive conventions and full sieve |
| `qt_app.py` | UI, jobs, rendering, exports | Field routing; scan/comparison; CSV/JSON | README; manual §§3–11; ARCHITECTURE | APP_VERSION and historical labels | REVIEWED — no change required; D1/D2/D5/D6; shared job state |
| `requirements-gpu-cuda12.txt` | Optional CUDA profile | CuPy acceleration; repeated OpenGL entries | README GPU; GUI diagnostics | CUDA12; cupy>=13; OpenGL floors | REVIEWED — no change required; repeated requirements harmless |
| `requirements.txt` | CPU/desktop dependency floors | Installation/import coverage | README Installation; manual §2 | Six dependency lower bounds | REVIEWED — no change required; not a lockfile; pytest absent |
| `results/1to100x_1to100y_100/atlas.config.json` | Historical scan profile | Old export consumer/provenance example | README Export; release audit | Schema 1 | REVIEWED — no change required; predates current snapshot/status fields |
| `results/1to100x_1to100y_100/atlas.csv` | Experiment table: 10000 rows, 58 columns | Historical schema/data; all row widths checked | README Export; historical JSON sidecars | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `results/1to100x_1to100y_100/metric_screenshots.json` | Historical screenshot manifest | Old export consumer/provenance example | README Export; release audit | 1.90.0-pyside6-prime-focused; schema1 | REVIEWED — no change required; predates current snapshot/status fields |
| `results/60to80x_20to40y_100/atlas.config.json` | Historical scan profile | Old export consumer/provenance example | README Export; release audit | Schema 1 | REVIEWED — no change required; predates current snapshot/status fields |
| `results/60to80x_20to40y_100/atlas.csv` | Experiment table: 441 rows, 58 columns | Historical schema/data; all row widths checked | README Export; historical JSON sidecars | Environment in adjacent manifest; no release scalar in CSV | REVIEWED — no change required; preserve original data |
| `results/60to80x_20to40y_100/metric_screenshots.json` | Historical screenshot manifest | Old export consumer/provenance example | README Export; release audit | 1.90.0-pyside6-prime-focused; schema1 | REVIEWED — no change required; predates current snapshot/status fields |
| `screenshots/README.md` | Current-illustration submission guide | Requires real outputs and provenance | README 3D/export; RESEARCH | 2.00.0/v170 | REVIEWED — no change required; no current screenshot supplied |
| `tests/scientific_reference.py` | Independent trial-division/factor/entropy/DFT oracles and CPU fixture | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_backend.py` | Absent/injected GPU fallback; conditional hardware equivalence | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_coprime_mask.py` | Every-plane GCD identity/density, M30 exceptions and Start shifts | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_core.py` | 20 core/catalog/placement/scalar/configuration/spherical regressions | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | v200 comment | REVIEWED — no change required |
| `tests/test_export_provenance.py` | Offscreen scan/comparison snapshots after control edits; CSV/batch metadata | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | 2.00.0 assertion | REVIEWED — no change required |
| `tests/test_fft_metrics.py` | Private scalar buffer, direct DFT, exact spectra, degeneracy and symmetries | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_known_scientific_issues.py` | Three expected failures: Hspec reflection, overflow, cache safety limit | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required; expected failures remain open |
| `tests/test_linear_embedding.py` | Exact integer interval, axes, starts and invalid dimensions | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_metrics.py` | Enumerated entropy/edges, affine gradient, histogram invariance and beauty | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_number_theory.py` | Trial-division primes/families, arithmetic recurrence and sign conventions | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_placements.py` | 1372 finite permutations, geometry versus arithmetic and shell transform | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_projections.py` | All depths/planes, inclusive hits/base-step, scalar and integer fields | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_random_baseline.py` | Fixed K, replacement draws, reproducibility, deltas and norms | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tests/test_scientific_ui.py` | Inclusive reversed scan ranges, same-M rows/ranking, fixed comparison config | Executable behavior/evidence contract | ARCHITECTURE test routes; RESEARCH; scientific audit | No release source | REVIEWED — no change required |
| `tools/scientific_audit_experiments.py` | Standalone audit CLI | Synthetic/null/density/shape/placement experiments | Scientific audit; RESEARCH limitations; ARCHITECTURE | Records env/source hashes, no app version import | REVIEWED — no change required; CLI is not general scan interface |

## Cross-document consistency

AGENTS routes to context/architecture/research/versioning; context uses the verified Linear formula and evidence categories; architecture documents actual field routing and keys; RESEARCH agrees on implemented formulas and controls; VERSIONING preserves the current label while flagging strict syntax. README is compared rather than used as unquestioned authority. Metric ranges added in the new architecture document supplement, rather than overwrite, RESEARCH. New documents distinguish proposed controls from the audit script and engine capabilities.

## Tests

Validation performed after creating the bootstrap documents, using `/usr/bin/python` on Linux: **Python 3.14.7, NumPy 2.4.6, PySide6 6.11.1**. These differ from the archived scientific-audit environment; the old evidence was not overwritten.

| Check | Status | Evidence / limitation |
|---|---|---|
| `python -m compileall .` | PASS | All project Python files compile; generated bytecode is ignored |
| `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v` | PASS with documented unresolved expectations | 67 tests: 63 passed, 3 expected failures, 1 skipped; no unexpected failures |
| `python -m pytest` | NOT RUN — runner unavailable | Invocation exits 1 with `No module named pytest`; not an application test failure. No dependency installed or requirements edited |
| Existing offscreen Qt/export regressions | PASS, included in suite | Actual small CPU scan/comparison and run-bound metadata; dialogs and batch figure rendering mocked |
| Audit CLI: `--output /tmp/prime-atlas-bootstrap-smoke --trials 2 --replicates 1 --seed 20260910` | PASS | Creates 11 CSVs and manifest; internal uniform-null equivalence assertion passes. This small smoke run is not a rerun of the published 500-trial study |
| Config and catalog/schema checks | PASS | Example equals AppConfig defaults; 13 modes, 14 placements, 58 scan columns, 22 heatmaps, 11 comparison columns |
| Manual exact CPU case | PASS | Linear 3×2×3 gives integers 1…18, cumulative hits `[[2,1,1],[0,3,0]]`, XY step 6 |
| New document local links / fenced blocks / source references | PASS | Links resolve; source names and consumers checked against definitions; no accidental formula/behavior edits |
| All pre-existing files against start-of-task SHA-256 snapshot | PASS | All 130 files byte-identical, including all application/test code, historical data and the two prior translation changes |
| Archived metrics source-hash investigation | PASS | Matching prior Git source has the same executable AST after removing docstrings; translation explains D14 |
| Actual CUDA equivalence | NOT RUN — skipped | CuPy/CUDA absent; fallback tests pass but are not hardware certification |
| Actual Matplotlib FFT/batch PNG smoke | NOT RUN | Matplotlib absent in this environment; previous audit recorded it separately, not reused as a current pass |
| Interactive desktop/OpenGL | NOT RUN | Offscreen testing does not validate physical display/camera/driver behavior; pyqtgraph/PyOpenGL also absent |

The three expected failures are the existing Hspec reflection instability, int64 overflow rejection and cached-volume/lowered-limit issue. They remain defects/expectations to address, not passes. No runtime fix was applied. Git diff/status and content hashes distinguish the five new files from the two prior translation diffs. Validation logs and smoke outputs were written under `/tmp`, not into curated evidence.

## Open questions

- Authorize the concrete pre-existing-document changes above, or retain them as recorded discrepancies?
- Decide eventual strict version spelling and approve any later version-source refactor separately.
- Decide the proposed Mahalanobis center/calibration before implementing that research method.
- Supply author, public URL and license/publication decisions when preparing an actual release.
- Select a compatible environment for pytest/plotting smoke checks and real CUDA/OpenGL validation if those checks are required beyond this documentation bootstrap.

## Version recommendation

```text
Current: 2.00.0
Recommended: unchanged for this bootstrap
PATCH/MINOR/MAJOR/no change: no change
Reason: documentation and operating context only; runtime/protocol preserved
Version update: not required
```

Strict SemVer spelling is a separately identified owner decision, not an applied normalization or implied release.

## Documentation recommendation

```text
Update required: yes, targeted pre-existing-document clarifications proposed
Affected files: doc/software_manual.md, doc/research_protocol.md
Optional additions: RESEARCH.md, README.md, CHANGELOG.md
Affected sections: D2–D10, D12, D15 and concrete proposal above
Reason: distinguish intended behavior, actual limitations, audit capabilities and historical changes
Status: awaiting owner authorization; new bootstrap files are already authorized and complete
```

No tag, release, push, DOI creation, public-repository operation, license change or version update was performed.
