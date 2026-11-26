# Prime Grid Atlas v1.0.0 — Software manual

[Italian original](software_manual.it.md)

This English translation includes owner-approved clarifications following the scientific audit; the Italian original is preserved unchanged. For subsequently identified implementation limitations, consult the [scientific audit](../SCIENTIFIC_AUDIT.md).

## 1. Purpose

Prime Grid Atlas is an interactive environment for exploring modular embeddings, primality masks and coprime structures. Build `1.0.0`, the first official release, uses:

- PySide6 for the tabbed interface;
- NumPy as the required numerical backend;
- CuPy/CUDA as an optional GPU backend;
- PyQtGraph/OpenGL for the 3D view;
- Matplotlib for scientific exports.

The program is an experimental mathematics tool. It does not generate prime numbers or prove new laws of their distribution.

## 2. Installation

Main requirements:

```bash
python -m pip install -r requirements.txt
```

Optional NVIDIA CUDA 12 backend:

```bash
python -m pip install --upgrade -r requirements-gpu-cuda12.txt
```

Launch:

```bash
python -B main.py
```

Check CuPy:

```bash
python -c "import cupy as cp; a=cp.arange(1000); print(cp.sqrt(a).sum()); print(cp.fft.fft(a).shape)"
```

If CUDA is unavailable, the program automatically continues with NumPy.

## 3. Interface structure

The application uses a single window with permanent tabs or tabs created when needed:

- **Grid**: main configuration and visualization;
- **Module scan**: asynchronous atlas scan;
- **FFT / Heatmap**: heatmaps produced by Module scan; the current FFT is integrated into Grid;
- **3D**: OpenGL visualization;
- **Configuration**: persistent application and scientific parameters.

## 4. Grid configuration

### Dimensions

The `X`, `Y` and `Z` controls define the discrete volume. With `Linear` placement:

\[
n(x,y,z)=s+zXY+yX+x,
\]

where `Start` corresponds to \(s\).

`Lock aspect ratio` preserves the current proportions when a dimension changes.

### Presets

Quick configurations are available:

- `71×30×30`;
- `37×32×30`;
- Prime overlay;
- Entropy;
- Twin primes;
- Residues mod N.

### Modes

The `Mode group` control divides the functions into three methodological groups.

#### Prime research

- `Primes`, `Twin primes`, `Sophie Germain primes` and `Safe primes`.

#### Scientific controls

- `Coprimes with N`, `Square-free numbers`, `Semiprimes` and `Prime powers`.

#### Modular diagnostics

- `Multiples of k`, `Residues modulo N`, `Divisor count τ(n)`, `Möbius μ(n)` and `GCD with N`.

`Parameter` represents \(k\) or the modulus N and is enabled only for modes that require it.

Implementation conventions:

- `Semiprimes` requires two prime factors counted with multiplicity, so it includes \(p^2\);
- `Prime powers` also includes primes, corresponding to exponent 1;
- `Twin primes` selects the lower member \(p\) when \(p+2\) is also prime;
- `Sophie Germain primes` requires both \(p\) and \(2p+1\) to be prime;
- `Safe primes` requires both \(p\) and \((p-1)/2\) to be prime.

Arithmetic fields are not reduced to binary masks:

- `Residues modulo N` computes the scalar field \(n \bmod N\) for each cell;
- `Divisor count τ(n)` colors the total number of positive divisors;
- `Möbius μ(n)` uses red for −1, gray for 0 and blue for +1;
- `GCD with N` colors the value of \(\gcd(n,N)\);
- `Coprimes with N` selects only cells with \(\gcd(n,N)=1\).

The FFT of residues, τ, μ and GCD operates on the centered scalar field. Other modes continue to use the binary presence/absence spectrum, preserving the historical v160 definition.

Modes requiring factorization are more expensive than the prime mask. For interactive exploration, begin with moderate volumes and increase dimensions after checking execution times.

### Placement

- `Linear`: preserves modular arithmetic progressions and the interpretation of columns modulo \(XY\).
- `Spiral inward`: on each XY plane, starts at the upper-left corner, follows the boundary clockwise and proceeds toward the center. The next Z plane restarts at the boundary and continues the numbering.
- `Spiral outward (Ulam)`: starts at the center and expands in a spiral; for even dimensions, the upper-left central cell is the conventional origin.
- `Boustrophedon`: alternates left-to-right and right-to-left rows.
- `Hilbert curve`: uses a Hilbert curve on a virtual square whose side is a power of two and clips coordinates outside the grid.
- `Morton Z-order`: recursively visits blocks using interleaved coordinate bits.
- `Diagonal zigzag`: traverses diagonals in alternating directions.
- `Corner expanding rings`: starts at the upper left and adds successive rectangular shells.
- `Concentric rings`: traverses boundaries from outside to center, alternating direction between consecutive rings.
- `Radial spokes`: groups cells by angular ray and proceeds outward from the center along each ray.
- `Prime modulus weave`: groups integers by `n mod N`, using `Placement parameter / seed` as N.
- `Seeded random`: applies a reproducible pseudorandom permutation; the seed is set through `Placement parameter / seed` and combined with X and Y.
- `Bit reversal`: orders indices by reversing their bits.
- `3D helix`: uses the inward spiral and rotates its orientation between Z levels; rectangular grids use corresponding reflections that preserve their shape.

Nonlinear placements are distinct geometric experiments. Orthogonal accumulation remains available on XY, XZ and YZ and geometrically sums cells along the chosen axis. Fixed planar placements preserve the XY step along Z, but generally not the steps along X/Y; 3D helix also changes orientation between layers. Quick modular metrics are not shown for these placements, and Module scan continues to use `Linear` exclusively.

### Placement comparison

`Compare placements` opens a tab that recalculates the current configuration with every placement. `Linear` is labeled `Protocol-valid`; the others are labeled `Exploratory`. The comparison uses geometric quantities compatible across embeddings: density, local and global entropy, edge density and four FFT metrics. `distance_from_linear` is the unstandardized Euclidean distance across these eight metrics and should be read as a descriptive indicator, not statistical significance.

Calculation proceeds one placement at a time, displays progress and can be cancelled. `Export CSV` saves the table and a `.config.json` sidecar containing version, dimensions, mode, parameters, Start, plane, level, accumulation and scientific configuration.

## 5. Projections and navigation

- `XY`: depth along Z and modular step \(XY\);
- `XZ`: depth along Y and step X;
- `YZ`: depth along X and step 1.

Matrices always follow the `(rows, columns)` convention: XY=`(Y,X)`, XZ=`(Z,X)` and YZ=`(Z,Y)`.

Controls:

- mouse wheel: zoom;
- `Shift+mouse wheel`: change level;
- drag: pan the grid;
- arrows beside the level: previous/next level;
- `Reset view`: fit the grid to the tab again.

`Accumulate 0..k` overlays every level from the origin through the selected depth.

## 6. 2D views

- `Classic`;
- `Heatmap`;
- `Normalized heatmap`;
- `Gradient`;
- `Local entropy`;
- `Entropy edges only`;
- `FFT 2D`.

`Numbers` and `Grid` control vector overlays. Numeric labels are created up to `Maximum text labels` (12,000 by default) to avoid an excessive number of graphics objects.

## 7. CPU/GPU backend

### Auto

Uses the GPU above `Auto GPU threshold` (65,536 elements by default) and the CPU for smaller matrices. This is the recommended mode for normal use: it avoids transfer and CUDA kernel overhead when the workload is too small to compensate for it.

### CPU

Forces NumPy. Useful for performance comparisons, reproducibility, diagnostics and working while other processes occupy GPU memory.

### GPU

Forces CuPy when CUDA is operational. Accelerated operations include:

- the main sieve and prime-mask lookup;
- 2D FFT;
- gradients;
- local entropy;
- the coprime control mask computed through `compute_backend.coprime_mask`;
- matrix components of the atlas scan.

Scalar `GCD with N`, direct `Coprimes with N` selection and the GCD/count calculations inside `prime_grid_metrics` use NumPy on the CPU. GPU selection does not move every arithmetic operation to CUDA.

The short list of base primes up to \(\sqrt N\), the GUI, CSV operations and table construction remain on the CPU.

GPU selection is an override, not a promise of greater speed. In Module scan, planes may be small and continuously change shape: CPU/GPU transfers, kernel launches and cuFFT plan creation can make forced GPU execution slower than CPU execution. The scan periodically releases unused FFT plans and CuPy blocks and clears caches at completion, preventing different FFT shapes from retaining several GiB without useful work.

`GPU diagnostics / setup` shows the complete backend status. `CUDA runtime incomplete` means the application's CuPy probe failed to complete at least one allocation, reduction, padding, FFT or sieve operation. It does not necessarily mean the driver is broken. Run detailed diagnostics from the project directory in the same virtual environment:

```bash
python -c "import cupy; cupy.show_config()"
python -c "from compute_backend import configure_backend,backend_error; print(configure_backend('GPU')); print(backend_error())"
```

A CUDA 12.x runtime supplied by `cupy-cuda12x` can work with a driver exposing a later CUDA version. `CUDA Root: None` and the absence of `nvcc` are not errors if CuPy finds the runtime, headers, NVRTC and cuFFT in the virtual environment.

## 8. FFT

`FFT 2D` is available directly in `View type` and uses the grid area. The button with the same name is a shortcut for selecting this view. Numbers and grid lines are hidden in this mode because pixels represent frequencies rather than integer cells. The program:

1. converts masks and overlays to presence/absence; residues, τ, μ and GCD retain their scalar values;
2. subtracts the mean;
3. computes the two-dimensional FFT;
4. uses the power spectrum;
5. removes the DC component.

Metrics:

- peak power ratio;
- axis power ratio;
- low-frequency power ratio;
- normalized spectral entropy.

The main metrics appear in the status bar. `Save FFT` exports the spectrum as PNG. The transform uses CuPy when the selected GPU backend is active and the configured threshold is exceeded, with NumPy fallback.

## 9. 3D view

The 3D tab uses OpenGL. Options and controls:

- `3D selected only`: show only selected points;
- `3D geometry`: choose `Cartesian grid`, `Spherical shells` or `Rotating spherical shells`;
- `Inner shell radius`: radius of level Z=0;
- `Shell spacing`: radial increment between consecutive Z levels;
- `Shell rotation`: longitudinal rotation added at each level in the rotating spherical geometry;
- left drag: rotate;
- middle/right drag: pan;
- mouse wheel: zoom;
- `Reset`, `Top`, `Front`, `Side`: camera;
- `Observer 0,0,0`: place the camera at the origin inside the shells, looking toward the outer sphere;
- arrows and `Z±`: navigation;
- `Zoom ±`: precise control.

The graphics window persists: subsequent generations update the same OpenGL context.

The internal view shows the prime sky from the atlas center. `Reset` and orthogonal views return the camera to the outside. Pressing `Observer 0,0,0` again restores the central viewpoint exactly.

In spherical geometries, X represents longitude, Y uses equal-area sampling between the poles and Z identifies increasingly distant concentric shells. The transformation changes rendering only: integers, primality, placement and 2D projections remain unchanged. Three great circles mark the outer shell boundary. For nonrotating spherical shells with `Linear 71×30×30`, each radial direction contains 30 values separated by 2130 and therefore preserves the same residue class modulo 30. With nonzero shell rotation, the longitude of a fixed grid column changes between layers, so its values no longer share one radial direction.

The current FFT still refers to the unwrapped rectangular map; it is not yet a spherical-harmonic analysis.

For safety, visualization is subsampled to `Maximum 3D points` (two million by default). Point size is also configurable.

## 10. Module scan

The Module scan tab explores X and Y ranges at fixed Z. The scan runs in a worker separate from the GUI. Progress updates are delivered through queued Qt slots in the main thread; the grid is temporarily frozen to prevent repainting or backend changes concurrent with the worker. Closing the application during a scan requests a stop; the window remains open if the current numerical step has not finished, avoiding destruction of a running thread.

Controls:

- X/Y ranges;
- fixed Z;
- number of baselines;
- Auto/CPU/GPU backend;
- progress and cancellation.

`Trials` specifies how many randomized control arrangements are generated for each X/Y combination. Each trial preserves the number of alive cells and samples the observed positive values while randomizing their positions. Saved random metrics are trial means. Deltas are observed metrics minus random means; a nonzero delta is an exploratory signal, not proof of statistical significance.

The approximate number of full passes is:

```text
X/Y combinations × (Trials + 2)
```

The two additional passes are the observed grid and the coprime mask. The GUI shows this cost before starting. Values of 1–2 trials suit initial exploration; 10–20 suit a preliminary comparison; larger values should be used on a restricted candidate set. Execution time grows approximately linearly with Trials.

The application imposes no limit on the number of combinations: all requested X/Y ranges are accepted. Very large scans may require substantial time and memory; `Cancel` remains available between successive numerical steps.

The scan produces 58 fields, including:

- modulus properties;
- prime metrics;
- random baselines;
- deltas from the baseline;
- coprime-mask metrics;
- prime/coprime deltas;
- L1/L2 residuals;
- class counts.

Available actions:

- CSV export, accompanied by a `.config.json` file containing all scan parameters and settings;
- one `Heatmap metric` selector for all viewable metrics;
- `Show heatmap` to open the selected metric;
- `Save screenshot` to export the selected metric as PNG;
- `Save all metric screenshots` to export all 22 PNGs listed in the selector after choosing a directory once.

The selector includes structural scores, density, coprime ratios, entropies, FFT metrics, baseline deltas and coprime residuals. There are no longer separate save buttons for each heatmap type.

The full export uses numbered filenames from `01_structural_score.png` through `22_delta_coprime_fft_axis_ratio.png` and writes `metric_screenshots.json`. This JSON file records the application version, each metric's name and key, scan ranges, Z, Trials, plane and scientific configuration. It does not rerun the scan or export a grid for every X/Y pair: it captures the 22 result matrices already calculated.

Interactive and exported heatmaps use the same `viridis` palette, the same linear min/max normalization as the FFT display and a lower Y origin. Missing combinations, for example after a cancelled scan, are gray and excluded from normalization.

## 11. Configuration

This tab applies parameters without restarting the program. `Reset defaults` restores the numerical values validated in v170; `Load JSON` and `Save JSON` load and save profiles. If `prime_atlas_config.json` exists in the application directory, it is loaded automatically at startup.

Parameters are logically divided into:

- computation: Auto GPU threshold, maximum volume, default baselines and seed (`-1` uses the deterministic seed derived from the experiment);
- metrics: entropy bins, edge threshold, low-frequency FFT radius and beauty-score coefficients;
- rendering: label limit, 3D point count and size, redraw delay and the exposed maximum batch PNG side setting.

The maximum batch PNG side setting (`export_max_side`) is currently not enforced. Batch heatmaps use a fixed 10×8-inch figure at 180 dpi; changing this setting does not resize them.

Changing a scientific parameter legitimately changes analytical images and scores. Use the same JSON profile when comparing two scans. The tab is disabled by a scan, but scan and placement-comparison tabs share process-wide configuration, backend and caches without a global job lock. Completion of one can re-enable controls while another is active. Run these analyses sequentially and keep the configuration fixed until completion; disabling the tab is not a guarantee of isolated execution.

## 12. Implemented metric definitions

### Local entropy

- 3×3 window;
- edge-replicating padding;
- configurable bin count (8 by default);
- quantization relative to the field minimum/maximum;
- base-2 logarithm.

### Edge density

The threshold is:

\[
T=H_{min}+r(H_{max}-H_{min}),
\]

with `r=0.72` by default.

### Global entropy

This is the entropy of the hit-value distribution, not a direct measure of its spatial arrangement.

### Beauty score

An internal heuristic score; the following formula shows the defaults, while the coefficients can be changed in Configuration:

\[
B=\max(0,R_c-R_n)
(1+0.35H_{loc}+0.65E)
e^{-18(\rho-0.27)^2}.
\]

It is neither a mathematical invariant nor a statistical significance measure.

### Structural score

\[
S=B_{obs}-\overline{B}_{random}.
\]

## 13. Limitations

- Current baselines are exploratory and default to 12 trials.
- Confidence intervals and p-values are not yet produced automatically.
- L1/L2 residuals combine unstandardized metrics.
- Coprime analysis on YZ is degenerate because the step is 1.
- The Linear formula is fixed; Start, dimensions and placement are configurable.
- GPU 3D rendering and CUDA computation use distinct backends.

See [research_protocol.md](research_protocol.md) for the scientific protocol and planned changes.

## 14. Main modules

```text
main.py             entry point
qt_app.py           PySide6 interface, scan iteration and interactive exports
app_config.py       validated configuration and JSON serialization
atlas_engine.py     headless volume, placements and per-configuration metrics
compute_backend.py  NumPy/CuPy selection and GPU sieve
metrics.py          geometric and spectral metrics
mode_catalog.py     Prime/Controls/Diagnostics groups
grid_model.py       slices, cumulative hits and spherical coordinates
number_theory.py    CPU arithmetic functions
```

The v1.0.0 distribution contains only modules belonging to the active pipeline. Earlier theoretical material has been preserved in [`archive/`](archive/README.md) and indexed in [`README.md`](README.md). Read the historical papers with the limitations stated in the archive index.
