# Prime Grid Atlas — project context

## Purpose and scope

Prime Grid Atlas is a desktop environment for experimental mathematics: it places consecutive integers in finite volumes, selects arithmetic subsets, visualizes slices and accumulated occupancy, and compares descriptive metrics against explicit controls. The current application version is `1.1.0`, in release preparation; the first official release remains `1.0.0`. See [VERSIONING.md](VERSIONING.md) for the project's version convention.

The central research question is:

> How much of the apparent geometry of prime numbers under a chosen spatial embedding is explained by modular admissibility, coprime residue classes, embedding geometry, and finite sampling, and what measurable residual structure remains after controlled baselines are considered?

This is a question, not an established result. The program computes prime masks with sieves; it does not establish a new prime-generating formula, distribution law or proof that visual patterns represent new arithmetic structure.

## Reading route and evidence

- [AGENTS.md](AGENTS.md): operating rules, approval boundaries and impact checklist.
- [ARCHITECTURE.md](ARCHITECTURE.md): actual data flow, module contracts, metric inputs, export dependencies and test routes.
- [RESEARCH.md](RESEARCH.md): existing description of the implemented methodology.
- [SCIENTIFIC_AUDIT.md](SCIENTIFIC_AUDIT.md): Phase I exact cases, experiments and findings at the audited snapshot.
- [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md): concise public synthesis of Phase I and Phase II.
- [research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md): Phase II analytical theory and experiments.
- [VERSIONING.md](VERSIONING.md): project compatibility policy and version approval procedure.
- [ZENODO.md](ZENODO.md): verified v1.0.0 archive, DOI distinction, integrity evidence and future-version procedure.
- [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md): file-by-file review, discrepancies, version inventory and bootstrap validation.

**Documentation describes intent. Code and tests establish current behavior.** Read the relevant implementation rather than inferring behavior from names such as “projection”, “structural” or “Protocol-valid”. Record disagreements before proposing changes.

The [manual](doc/software_manual.md) describes interaction but has known qualifications listed in the bootstrap report. The [30p protocol](doc/research_protocol.md) includes proposed experiments, not only available features. Files in `doc/archive/` are historical papers; `doc/evidence/` contains historical illustrations. `docs/scientific_audit/` contains recorded audit experiments, not an automatically refreshed benchmark. English is the current documentation language; `.it.md` files preserve Italian originals. Preserve historical evidence and its provenance.

## Core concepts

| Concept | Current meaning |
|---|---|
| Volume | Consecutive int64 integers in an array of shape `(Z,Y,X)`, plus a Boolean selection of the same shape |
| Numerical modes | 13 modes: four prime families, four arithmetic controls, five modular diagnostics; four diagnostics also produce scalar fields |
| Slice | One selected depth in XY, XZ or YZ |
| Multilayer overlay | Inclusive count of selected entries from depth 0 to k along the orthogonal axis; alive means count > 0 |
| Coprime structure | The mask `gcd(base, step)==1`; modular admissibility, including explicit exceptional prime divisors outside the mask |
| Random control | Fixed alive-cell count, uniform distinct positions, positive hits sampled with replacement; not a coprime-conditioned or exact-histogram null |
| Placement | One of 14 arrangements of the same volume interval; geometric comparison changes arrangement while fixing experiment parameters |
| Metrics | Occupancy, entropy, entropy-threshold edges, FFT fractions/entropy and heuristic scores; no automatic statistical significance |
| Module scan | Primes/Linear over all requested X/Y pairs at fixed Z and full orthogonal depth, sorted by structural score |
| 3D | Cartesian points or fixed/rotating equal-area spherical cells; a rendering transform, not a different arithmetic or spectral model |

## Core mathematical model

Verified in `atlas_engine.build_volume` and `tests/test_linear_embedding.py`: for Linear placement and zero-based indices,

$$n(x,y,z)=Start+x+Xy+XYz,$$

$$\Delta_x=1,\qquad\Delta_y=X,\qquad\Delta_z=XY.$$

For a fixed XY position,

$$n_z=a+zM,\qquad a=Start+x+Xy,\qquad M=XY.$$

This describes the supported integer range, not arbitrary int64 overflow. Negative values are permitted but never classified as prime. The complete volume interval is `[Start, Start+XYZ-1]` when representable.

| Plane | Rows, columns | Accumulated axis | Linear step |
|---|---|---|---|
| XY | Y, X | z | XY |
| XZ | Z, X | y | X |
| YZ | Z, Y | x | 1 |

The base is the first term along that axis. The identity `gcd(a+j·step,step)=gcd(a,step)` explains the control. If the common divisor is greater than one, a prime term can only be that divisor itself, if it is prime. Coprimality is not a finite-depth prediction. YZ has an all-true control because its step is 1.

Fixed planar placements retain the vertical step XY but alter planar progressions; 3D helix can also change the vertical progression. `overlay_metrics` explicitly requires Linear. A complete-volume permutation need not preserve the subset seen in a slice or the counts aggregated in another plane.

## Field identity matters

Keep integers, Boolean selections, hit counts, normalized hits and arithmetic scalar slices separate. `projection` returns both a slice and cumulative hits even when overlay is off. Non-overlay analytical views of selection modes can analyze integer values. Scalar diagnostics keep current-slice values even when overlay is on. FFT selection views and scan FFT binarize occupancy; placement comparisons use selection/hits even for scalar modes.

Consequently, the same mode, palette or image title does not establish that two views measure the same field. See the field-routing table in [ARCHITECTURE.md](ARCHITECTURE.md).

## Scientific caution and current limits

Use **IMPLEMENTED**, **OBSERVED**, **HYPOTHESIZED** and **PROVEN** explicitly. A large difference from one baseline does not establish a new prime property or statistical significance. Structural score is beauty minus the uniform-null mean, and can retain modular effects. Residual norms mix unstandardized quantities. Finite depth, density, aspect ratio, boundary handling and selection of scan maxima affect interpretation.

The Phase I audit records a fixed scalar-FFT cache corruption bug and three then-open expectations. Release preparation resolved spectral-entropy reflection invariance, int64 interval rejection and cached safety-limit enforcement with ordinary regression tests. CUDA equivalence still requires actual hardware, and offscreen Qt does not validate interactive OpenGL.

## Working and publication context

Run commands from this project directory. It is a source application with flat local imports, not an installable package: no `pyproject.toml`, setup metadata or dedicated test-configuration file exists in the inspected project tree. The repository includes `.github/workflows/cpu-tests.yml`, which runs the CPU test suite and the Phase II identity verifier on Python 3.11 and 3.12. This workflow does not validate CUDA, interactive OpenGL or unlisted environments. The application starts with `python main.py`; NumPy suffices for numerical headless use, while desktop/plotting dependencies are declared in `requirements.txt`.

Use the repository root reported by `git rev-parse --show-toplevel`; do not rely on machine-specific paths. Local `results/` are ignored/untracked. Earlier audit statements about tracked results describe a former parent repository, not the current index. Preserve those outputs and inspect Git status before staging. The public author and copyright holder are `zampro79`; the project is licensed under MIT.

## 1.1.0 release-preparation status

The author-approved title is **Integrity, Reproducibility & Reliability Update**.
The runtime label is formalized; publication, final capture generation and the
new version DOI/date remain pending. R08-08 stays HIGH/open with unknown cause;
consult [Known Issues](KNOWN_ISSUES.md), the
[release notes](RELEASE_NOTES_v1.1.0.md) and
[version checklist](RELEASE_CHECKLIST_v1.1.0.md). Do not relabel the original
publication or the preparatory bab02ccf/runtime 1.0.0 artifacts.
