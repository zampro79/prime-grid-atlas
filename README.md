# Prime Grid Atlas

## An Open Experimental Number Theory Laboratory

Prime Grid Atlas is an interactive laboratory for exploring prime-number
patterns through multidimensional grids, modular arithmetic, spectral analysis
and controlled statistical baselines.

Version **1.0.0** · Python / PySide6 · NumPy CPU computation · optional CuPy
CUDA acceleration.

> Prime Grid Atlas supports experimental mathematics. Visual patterns and
> heuristic scores are not proofs, discoveries, or statistical significance.

## Screenshots

Current-release screenshots are being provenance-checked before publication.
The repository contains authentic exploratory application images, but images
without complete v1.0.0 parameters are not presented here as release evidence.
See [screenshots/README.md](screenshots/README.md) and the clearly labelled
[historical v170 evidence](doc/evidence/README.md).

## What is Prime Grid Atlas?

The Linear embedding assigns consecutive integers to a three-dimensional grid:

\[
n(x,y,z)=Start+x+Xy+XYz.
\]

An XY cell followed through z is an arithmetic progression with step \(XY\).
The application compares prime occupancy with modular admissibility, coprime
residue masks, alternative spatial embeddings and randomized controls. It helps
ask which visible structures are mathematically forced and which require a
stronger explanation.

## Key features

- Prime, twin-prime, Sophie Germain and safe-prime masks.
- Coprime, square-free, semiprime and prime-power controls.
- Residues, divisor counts, Möbius values and GCD diagnostics.
- XY, XZ and YZ slices and cumulative selected-count maps.
- Heatmaps, gradients, local/global entropy and 2D Fourier analysis.
- Module scans with observed, coprime and randomized comparisons.
- Fourteen integer placements and Cartesian or spherical 3D views.
- CSV/JSON/PNG exports with run-bound provenance for tabular analyses.
- NumPy CPU backend and optional CuPy CUDA acceleration with CPU fallback.

## Research highlights

Two scientific investigations accompany the application. Their principal
conclusion is conservative: in the studied cases, the dominant spectral and
geometric structures are explained by modular admissibility, grid shape and
the embedding; no convincing new prime-specific residual was found.

Established and experimentally verified results include:

- the DFT of the coprime-residue indicator is a Ramanujan sum;
- exact spectral moments are available for fixed-size samples on admissible
  support;
- parity and character-coset constraints force specific spectral peaks;
- coprime autocorrelation factors exactly through the Chinese remainder theorem;
- reshaping the same modulus as different \(X\times Y\) grids changes raw 2D
  spectral metrics;
- uniform randomness is an inadequate null for fields with modular support.

Read the concise [research findings](RESEARCH_FINDINGS.md), the
[Phase I scientific audit](SCIENTIFIC_AUDIT.md), and the
[Phase II report](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md).

## Quick start

Python 3.10 or newer is recommended, subject to wheel availability for the
declared dependencies.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Begin with a 10×10×10 grid and select **CPU** for reproducible CPU work. A
desktop display is required for interactive use; OpenGL is required for 3D.

Optional CUDA 12 profile:

```bash
python -m pip install -r requirements-gpu-cuda12.txt
python -c "from compute_backend import configure_backend; print(configure_backend('GPU'))"
```

Requesting GPU is not evidence that GPU execution succeeded. Check the runtime
backend status. CUDA equivalence has not been verified for this release
preparation environment.

## Scientific methodology

For zero-based coordinates, arrays have shape `(Z, Y, X)`. The arithmetic step
along the accumulated axis is:

| Plane | Step | Matrix shape |
|---|---:|---|
| XY | `X*Y` | `(Y, X)` |
| XZ | `X` | `(Z, X)` |
| YZ | `1` | `(Z, Y)` |

The coprime mask `gcd(base, step) == 1` measures modular admissibility. It does
not predict which finite terms are prime. The application random baseline fixes
the number of alive cells, randomizes their positions over the full plane and
resamples positive hit counts with replacement. It is not conditioned on
coprimality and does not preserve the hit histogram exactly.

Metric definitions, input fields and limitations are specified in
[RESEARCH.md](RESEARCH.md). Code and tests define current behavior.

## Reproducing experiments

Run the CPU test suite:

```bash
python -m unittest discover -s tests -v
```

Reproduce Phase I audit experiments in a separate output directory:

```bash
python tools/scientific_audit_experiments.py \
  --output results/scientific_audit --trials 500 --replicates 50 \
  --seed 20260910
```

Reproduce Phase II:

```bash
python research_ii/verify_theorems.py
python research_ii/research_ii_experiments.py \
  --trials 240 --seed 20261126
```

The Phase II script is independent of the application and writes CSV data plus
a manifest under `research_ii/data/` by default.

## Documentation

- [Software manual](doc/software_manual.md)
- [Implemented research framework](RESEARCH.md)
- [Research findings](RESEARCH_FINDINGS.md)
- [Architecture](ARCHITECTURE.md)
- [Scientific audit / Phase I](SCIENTIFIC_AUDIT.md)
- [Research II](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md)
- [Contribution guide](CONTRIBUTING.md)
- [Release checklist](RELEASE_CHECKLIST.md)

Historical papers and v170 images are preserved for provenance, but are not
authoritative v1.0.0 specifications or validated release results.

## Scientific limitations

- No automatic p-values, confidence intervals or multiple-comparison correction.
- Structural, beauty and residual scores are descriptive heuristics.
- The application null is not conditioned on coprime support or \(1/\log n\).
- Density, aspect ratio, depth and interval position affect the metrics.
- Spectral and local metrics depend on the selected embedding and field.
- Large `Start` values can make the full sieve expensive even for small volumes.
- Individual image exports do not always contain complete experiment sidecars.
- Interactive OpenGL and actual CUDA hardware remain unverified here.

## Citation

Machine-readable citation metadata are in [CITATION.cff](CITATION.cff). Author
identity is the public pseudonym **zampro79**. Do not invent a DOI; add one only
after an actual archive record exists.

## License and contributions

Prime Grid Atlas is Copyright (c) 2026 zampro79 and is distributed under the
[MIT License](LICENSE).

Contributions are welcome after the public repository is released; see
[CONTRIBUTING.md](CONTRIBUTING.md). Third-party dependencies retain their own
licenses, including the Qt/PySide6 licensing terms.
