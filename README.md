# Prime Grid Atlas

**1.1.0 — Integrity, Reproducibility & Reliability Update**

**Release preparation — not yet published.** Original author: **zampro79**.

Prime Grid Atlas is a desktop laboratory for experimental number theory. It maps
integers into finite grids, displays arithmetic subsets and compares measured
patterns with modular and randomized controls.

> **Known native crash risk:** R08-08 remains **HIGH / OPEN / NOT REPRODUCED /
> ROOT CAUSE UNKNOWN**. A crash can lose unsaved results or interrupt an export.
> Read [Known Issues](KNOWN_ISSUES.md) before relying on a run.

## Scientific scope

Visual patterns, rankings and heuristic scores are not proofs, discoveries or
automatic significance tests. Technical validation is not academic certification.
The [implemented research framework](RESEARCH.md) defines fields, metrics and
controls; [research findings](RESEARCH_FINDINGS.md) separate mathematical results
from finite experimental observations.

## Screenshots and gallery

The four approved main views are prime occupancy, desktop 3D, desktop FFT and
placement comparison. The complete gallery will also include coprimality,
parametric scan, viewports and an OpenGL framebuffer.

**Final 1.1.0 images have not been generated.** The preparatory bab02ccf images
retain runtime 1.0.0 and their original provenance; they are not displayed here
as 1.1.0 evidence. See the [capture specification](screenshots/CAPTURE_PLAN_v1.1.0.md)
and [screenshot provenance requirements](screenshots/README.md). Gallery links
will be added only after the actual files exist and pass review.

## Features

- Prime families, coprime and arithmetic controls, residues, divisor counts,
  Möbius values and GCD diagnostics.
- XY/XZ/YZ slices, accumulated hit maps, gradients, entropy and 2D FFT.
- Fourteen placements, descriptive parameter scans and Cartesian/spherical 3D.
- Native CSV/configuration/PNG exports and provenance sidecars on supported paths.
- Defensive cache copies and preventive operation-local memory budgets.
- NumPy CPU computation and optional CuPy routing; real CUDA is not validated here.

## Mathematical framework

For zero-based coordinates, Linear placement uses
`n(x,y,z) = Start + x + X*y + X*Y*z`, with arrays shaped `(Z,Y,X)`.

| Plane | Step along the accumulated axis | Matrix shape |
|---|---:|---|
| XY | X*Y | (Y,X) |
| XZ | X | (Z,X) |
| YZ | 1 | (Z,Y) |

`gcd(base, step) = 1` defines modular admissibility, not primality; exceptional
primes dividing the step require separate treatment. The application random
control fixes occupancy, randomizes positions over the full plane and resamples
positive hits with replacement. It is not coprime-conditioned or exact-histogram.
See [RESEARCH.md](RESEARCH.md) and [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Installation

Use a compatible existing Python environment or create a local environment for
a new installation. Commands below use relative paths; dependency installation
is a reader action, not something performed during this preparation step.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Use the appropriate relative activation command for another shell. Preparation
validation uses Linux/Python 3.14.10; other platforms are not validated by API
simulations. A desktop is required for interactive use and OpenGL for 3D.
The optional CUDA profile is [requirements-gpu-cuda12.txt](requirements-gpu-cuda12.txt).
Requested GPU mode is not proof of actual GPU execution; inspect backend status.

## Quick start

Begin with a small grid and select **CPU**. Record dimensions, Start, mode and
parameter, placement and parameter, plane, depth, overlay and the complete
configuration. Keep native exports and sidecars together in a new output directory.
The [software manual](doc/software_manual.md) describes the interface.

## Reproducible examples

The approved example plan covers prime occupancy, coprimality, 3D, FFT, placement
comparison, scan and native provenance export. Each final case must include
configuration, seed policy, actual environment/backend, source identity, runtime
version, results, screenshots, manifests and checksums. These demonstrations are
separate from Research I/II. The [capture plan](screenshots/CAPTURE_PLAN_v1.1.0.md)
specifies their provenance and privacy gates; the final package is still pending.

## Research I and Research II

- [Research I audit](SCIENTIFIC_AUDIT.md) and
  [historical reproduction evidence](docs/reproducibility/research_i/README.md).
- [Research II theory and experiments](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md).

Current fixed non-DC Research I reruns are distinct from exact historical
reproduction; the complete original source provenance remains unresolved.
Use new, separate output directories, never the preserved datasets:

```bash
python tools/scientific_audit_experiments.py --output results/repeat-research-i --trials 500 --replicates 50 --seed 20260910
python research_ii/verify_theorems.py
python research_ii/research_ii_experiments.py --output results/repeat-research-ii --trials 240 --seed 20261126
```

Choose new directory names if those already exist. Research II is independently
implemented. Numerical agreement does not establish statistical significance.

## Scientific provenance

Supported exporters record observed source identity, effective configuration,
environment, backend evidence and output hashes. Unknown provenance remains
unknown. A documentation summary is not a native manifest; preserve emitted
sidecars unchanged. Hashes establish byte integrity, not scientific completeness.
See [the architecture](ARCHITECTURE.md#scientific-provenance-sidecars).

## Resource management

The default cap is **1024 MiB of estimated additional memory per operation**.
Checks compose persistent buffers and mutually exclusive work, including
bin-dependent entropy temporaries. Available memory, mapped cgroup headroom and
optional POSIX limits constrain admission where observable. This is not a
reservation or universal upper bound; see [memory policy](ARCHITECTURE.md#preventive-memory-policy).

## Validation

```bash
python -X faulthandler -m unittest discover -s tests -v
```

The 1.1.0 preparation working tree completed 169 tests in each existing Linux CPU
environment: 168 passed and one real-CUDA test skipped. Fresh Research I fixed
non-DC and Research II reruns matched 11/11 and 4/4 relevant baseline CSVs in each
environment; compileall and the Research II verifier also passed. These checks
apply to the observed source hashes and environments; committed-source and
final-asset acceptance remain in the [1.1.0 checklist](RELEASE_CHECKLIST_v1.1.0.md).
Recorded desktop validation applies to its actual source/driver environment and
must not be relabelled as a final 1.1.0 capture. No CUDA or general thread-safety
certification is claimed.

## Known issues

Read [KNOWN_ISSUES.md](KNOWN_ISSUES.md), including R08-08, platform/CUDA limits,
shared runtime state, export atomicity, memory estimates and incomplete historical
Research I provenance. See also [release notes](RELEASE_NOTES_v1.1.0.md).

## Citation

[CITATION.cff](CITATION.cff) now describes **1.1.0 in preparation**, without an
invented DOI or release date. Complete those fields only when established.

The original publication remains:

> zampro79. (2026). *Prime Grid Atlas* (Version 1.0.0) [Computer software].
> Zenodo. https://doi.org/10.5281/zenodo.24546973

That version DOI identifies **1.0.0 only**. Concept DOI
[10.5281/zenodo.24546972](https://doi.org/10.5281/zenodo.24546972) identifies the
version family. The 1.1.0 version DOI is pending. See [ZENODO.md](ZENODO.md).

## License and authorship

Copyright (c) 2026 **zampro79**, original author of Prime Grid Atlas.
[MIT License](LICENSE); dependencies retain their own licenses, including Qt/PySide6
terms. See [CONTRIBUTING.md](CONTRIBUTING.md). Publication requires a separate
explicit author decision.
