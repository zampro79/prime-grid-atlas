# Research framework

## Motivation

How much of prime-overlay geometry is explained by modular admissibility and spatial embedding, and what measurable differences remain against controlled baselines? This software supports exploration, not a claim that a new property of primes has been discovered.

Use four explicit evidence labels: **Implemented** (code behavior), **Observed** (recorded experiment), **Hypothesized** (interpretation to test), **Proven** (mathematical statement with proof). No empirical release study is asserted here.

## Linear integer embedding

$$
n(x,y,z)=Start+x+Xy+XYz
$$

Coordinates are zero-based and bounded by positive integer dimensions X,Y,Z; array order is `(Z,Y,X)`. Primality is false for integers below 2.

## Interpretation of the three axes

Holding the other coordinates fixed, incrementing x adds 1, y adds X and z adds XY. Dimensions and Start are part of every experimental specification. Negative Starts are supported by the UI, but do not turn negative integers into primes.

## XY / XZ / YZ projections

| Plane | Base values | Accumulation | Step |
|---|---|---|---|
| XY | Start+x+Xy | z | XY |
| XZ | Start+x+XYz | y | X |
| YZ | Start+Xy+XYz | x | 1 |

Each projected cell is a finite progression in Linear placement. The YZ coprime mask is identically true; it cannot discriminate modular admissibility. Matrix shapes are `(Y,X)`, `(Z,X)`, `(Z,Y)` respectively.

## Multilayer overlays

For selected indicator I, a depth-k overlay stores $h=\sum_{j=0}^{k} I_j$ and alive indicator $A=\mathbf 1_{h>0}$. The endpoint is included. A normalized occupancy image divides hits by k+1. Alive density measures occupied projected cells, not prime density in the volume.

Scan entropy uses hit counts, whereas scan FFT uses binary alive occupancy. In non-overlay Heatmap, Gradient and Local entropy views, selection modes use integer values as the analytical source; they are not automatically maps of prime density. Scalar diagnostics use current-slice residue, τ, μ or GCD values and do not accumulate those scalar values. These field choices must be stated with exported images.

## Modular interpretation

In XY the step is $M=XY$. For base b, $\gcd(b+kM,M)=\gcd(b,M)$. If d=gcd(b,M)>1, every term is divisible by d. A prime term can only equal d, with d prime; terms greater than d are composite. Coprimality expresses admissibility, not a finite primality guarantee. The exceptional primes dividing M must not be silently discarded.

## Experimental controls

### Observed prime distribution

The engine uses a sieve-based prime mask. Module scan always builds Primes / Linear at full depth along the selected plane's orthogonal axis. Twin-prime mode selects the lower member p for which p+2 is prime, including when p+2 lies outside the volume. Sophie Germain and safe-prime predicates similarly test their related integers. Semiprimes include prime squares; prime powers include exponent one.

### Coprime baseline

The control is the binary field $C=\mathbf 1_{\gcd(b,step)=1}$. It is evaluated with the same metric functions. It is neither a density-matched prime process nor an expected hit-count field. For direct interactive comparison, select Coprimes with N and set N to the relevant step. Noncoprime activation counts retain exceptional prime terms.

### Randomized baseline

For each trial, choose exactly as many distinct positions as observed alive cells, uniformly over all projected cells. Assign positive hit counts drawn with replacement from observed positive hits. Thus alive density is exact; the positive-hit histogram and total hits fluctuate. This is not an exact permutation null and is not conditioned on coprime positions or on integer size.

The implementation averages metrics over trials (default 12); it does not export trial distributions or variance. The default seed is the 32-bit deterministic function of X,Y,Z, plane, Start and placement in `metrics.deterministic_seed_for_atlas`. A configured nonnegative seed overrides it; RNG initialization masks the seed to 32 bits. Save the profile, software version and NumPy version; derived seeds use full dimensions even for partial overlays. Changing trial count with the same seed extends the same initial random sequence.

Conceptually the experiment asks whether

$$
Observed = Modular/Coprime\ structure + Residual\ structure.
$$

This is a conceptual protocol model, **not a theorem or an exact additive decomposition**. Implemented residuals are differences between selected metrics; omitted null-model assumptions may explain them.

## Metrics

Definitions below describe `metrics.py` and `atlas_engine.py`, with default settings from `AppConfig`.

| Implemented field | Definition |
|---|---|
| alive_density | Fraction h>0 over projected cells |
| coprime_alive_ratio | Alive coprime cells / coprime cells; zero for empty denominator |
| noncoprime_alive_ratio | Analogous ratio over noncoprime cells |
| *_count | Coprime/noncoprime cell totals and alive subtotals |
| local_entropy_mean | Mean Shannon entropy in 3×3 windows; edge-replicating padding, 8 globally min/max-quantized bins, base-2 logs |
| edge_density | Fraction of local entropy values ≥ Hmin+0.72(Hmax−Hmin); zero for constant entropy |
| global_entropy | Shannon entropy of the exact hit-value histogram, including zero; insensitive to spatial permutation |
| fft_peak_ratio | Largest non-DC power / total non-DC power |
| fft_axis_ratio | Power on central horizontal and vertical frequency axes, excluding DC / total |
| fft_lowfreq_ratio | Power at radii 0<r≤max(1,0.18 rmax), in frequency-bin coordinates / total |
| fft_spectral_entropy | Power-probability entropy divided by log2(W·H−1), a fixed non-DC support size; zero when W·H≤2 or power is zero |

For compatible finite inputs, the ranges and fields are:

| Quantity | Input / range | Interpretation limit |
|---|---|---|
| Alive density and activation ratios | Binary occupancy; [0,1], zero for an empty class denominator | Occupancy is not volume prime density; YZ has no noncoprime class |
| Class counts | Binary coprime/occupancy intersections; integers from 0 to N projected cells | Exceptional prime divisors remain counted |
| Global entropy | Hit histogram; 0…log2(min(N,d+1)) for hits from 0 to d | Not normalized to [0,1]; ignores cell arrangement |
| Mean local entropy | Quantized hit windows; 0…log2(min(B,9)); B=8 discrete maximum ≈2.9477 | Not normalized to [0,1]; depends on bins, density and boundary padding |
| Edge density | Local-entropy threshold mask; [0,1] | High-entropy fraction, not geometric contour density |
| FFT fractions and spectral entropy | Centered binary occupancy, or scalar values in scalar FFT views; nominally [0,1] | Shape and density affect interpretation; one-dimensional nonconstant fields are evaluated, while zero-power cases return zero |
| Beauty | Activation contrast, local entropy, edge density and density weighting; nonnegative, conservative default upper bound 2.7 | Bound is for defaults; changing weights changes the bound; not a probability |
| Structural and metric deltas | Observed value minus the relevant baseline mean/value; signed | Structural score can exceed 1; differences do not imply significance |
| Residual norms and placement distance | Seven/eight metric differences respectively; nonnegative | Unstandardized distances; not pixel distances or calibrated effect sizes |

Here N is the number of projected cells, d the number of accumulated layers and B the local-entropy bin count. Analytical views may use integer or scalar slices instead of hits, as described under Multilayer overlays; the global-hit bound does not apply to arbitrary scalar distributions. Detailed consumer-specific contracts are in [ARCHITECTURE.md](ARCHITECTURE.md).

FFT uses a centered binary field for selection masks/overlays, FFT shift and squared magnitude, with DC explicitly zeroed. Scalar FFT views retain centered scalar values. Zero-power inputs produce zero metrics; metrics also return zero when either dimension is ≤1, even though the display can contain one-dimensional spectral power. Low-frequency radius depends on rectangular shape; tiny floating-point powers can affect spectral-entropy support. Display images show log1p(power), not the values used to compute ratios.

The configurable heuristic beauty score is

$$
B=\max(0,R_c-R_n)(1+w_H H_{loc}+w_E E)\exp[-d(\rho-\rho_0)^2],
$$

with defaults wH=0.35, wE=0.65, d=18 and ρ0=0.27. Structural score is $B_{obs}-\overline B_{random}$.

Seven geometry fields (local entropy, edge density, global entropy and four FFT metrics) each have random means, observed-minus-random deltas, coprime-mask values and observed-minus-coprime deltas. `coprime_residual_l1` sums absolute coprime deltas; L2 is their Euclidean norm. Density has a separate coprime delta and is not in that seven-field norm. Placement comparison uses eight fields including density and reports an unstandardized Euclidean distance from Linear. Mixing scales makes these distances descriptive and weight-sensitive.

Gradient magnitude is also implemented for visualization: centered differences in interiors, one-sided differences at boundaries, zero derivative for singleton axes. It is not an additional scan score.

## Module scan

Each X/Y pair at fixed Z produces metadata $M=X\cdot Y$, factorization, φ(M)/M, ω(M) (distinct prime factors) and τ(M). The GUI exports 58 columns and offers 22 metric heatmaps. On XZ and YZ, M is still XY metadata but coprimality uses X and 1 respectively; do not interpret these as XY-residue scans. Results sort by structural score, which introduces selection bias if the top rows become the only reported outcomes.

Run-start metadata accompanies CSV and batch image exports. An explicit seed or the deterministic seed rule permits reconstruction, but sidecars do not include dependency versions, commit hashes or raw random trials. Record those separately. Do not run placement comparisons and module scans concurrently: they share global configuration, caches and backend state.

## Placement controls

The fourteen choices listed in README permute integer positions while preserving the volume's multiset. Compare fixed dimensions, Start, mode, depth and seeds to measure dependence on geometry. Fixed planar permutations retain the z increment XY; X/Y progressions generally change, and the helix changes layer orientation. Linear alone is accepted by protocol metrics. Spherical shells are a rendering transformation, not another primality or spectral model.

Placement comparisons use Boolean selection/occupancy even for scalar diagnostic modes; their statistics are not the scalar FFT view's statistics.

## Falsification mindset

Attempt to invalidate interesting patterns by:

- comparing both random and coprime controls;
- varying Start and X,Y,Z, including transposed aspect ratios;
- comparing placements with fixed arithmetic input;
- replicating across controlled seeds and increasing random trials;
- comparing metrics with different sensitivities;
- retaining negative results and separating exploratory selection from held-out confirmation.

A residual outside one null model should first motivate better controls, not a claim of a new prime property.

## Current limitations

There are no automatic complete confidence intervals, empirical p-values, standardized effect sizes or multiple-testing corrections. Heuristic scores are not statistical significance. Multiple comparisons can yield false positives. A structured FFT does not imply a new prime theorem. Visual pattern ≠ proof.

The pre-release implementation uses the fixed non-DC denominator `log2(W*H-1)` for spectral entropy. This replaces the audited positive-bin-count denominator, which could change under reflection because of roundoff. The regression in `tests/test_known_scientific_issues.py` verifies reflection invariance on the original counterexample. This metric is therefore not numerically comparable with audit CSV columns generated by the earlier definition.

The random baseline is unconditioned and resamples counts; the coprime mask is binary. Neither models all known arithmetic dependence. Finite depth and density saturation can hide differences. FFT boundary conventions, aspect ratio, quantization and heuristic coefficients affect results. Spherical views have no spherical-harmonic analysis. CPU/GPU numerical equivalence is not certified by this release audit.

The specialized [30p draft](doc/research_protocol.md) includes future exact-permutation and prime-like nulls, spatial autocorrelations and inferential statistics. These are **proposed**, not implemented release features. Phase II implements independent research scripts, not application features; see [Research findings](RESEARCH_FINDINGS.md) and the [Phase II report](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md). Historical papers contain stronger empirical language and must be independently re-evaluated before citation as evidence.
