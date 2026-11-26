# Prime Grid Atlas v1.0.0

Prime Grid Atlas is an open experimental number theory laboratory for exploring
prime patterns through multidimensional integer grids, modular controls,
spectral analysis and reproducible randomized baselines.

This is the first official release of an independent experimental-mathematics
laboratory maintained under the public identity `zampro79`.

## Highlights

- Thirteen numerical modes and fourteen spatial placements.
- XY, XZ and YZ slices and cumulative selected-count maps.
- Prime, coprime and randomized module-scan comparisons.
- Entropy, gradient and Fourier views.
- Cartesian and spherical 3D visualization.
- CPU NumPy backend with optional CuPy CUDA acceleration and explicit fallback.
- Reproducible Phase I and Phase II scientific investigations.

## Scientific position

This release makes no claim of a new theorem or a newly discovered law of prime
distribution. The accompanying research found that dominant structures in the
studied cases are explained by modular admissibility, parity, grid shape and
the selected embedding. No convincing prime-specific residual remained under
the tested conditioned controls.

## Pre-release correctness fixes

- Reject int64 interval and prime-family partner overflow.
- Enforce the volume limit on cached and uncached requests.
- Use a symmetry-stable fixed-support spectral-entropy normalization.
- Validate projection planes and randomized trial counts.
- Evaluate one-dimensional nonconstant FFT fields.
- Reject non-finite scientific configuration values.
- Distinguish requested backend from runtime backend policy in provenance.

The spectral-entropy definition differs from audit-era CSV outputs. Historical
data remain unchanged and retain their original provenance.

## Known limitations

- No automatic inferential statistics or multiple-comparison correction.
- The application random null is not conditioned on coprime support.
- Individual image exports have incomplete provenance.
- Large Start values can make the full sieve memory-intensive.
- CUDA numerical equivalence and interactive OpenGL were not verified in the
  release-preparation environment.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

See `README.md`, `RESEARCH_FINDINGS.md` and `RELEASE_CHECKLIST.md` for details.

## License and citation

Prime Grid Atlas is Copyright (c) 2026 zampro79 and released under the MIT
License. Citation metadata are provided in `CITATION.cff`. The preserved source
archive is available at https://doi.org/10.5281/zenodo.24546973.
