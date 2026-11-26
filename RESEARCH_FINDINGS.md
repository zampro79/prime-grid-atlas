# Research findings

This page summarizes the two Prime Grid Atlas investigations. It does not
replace the complete [Phase I audit](SCIENTIFIC_AUDIT.md), the
[implemented methodology](RESEARCH.md), or the
[Phase II report](research_ii/PRIME_GRID_ATLAS_RESEARCH_II.md).

## Mathematical identities

- Linear placement is `n(x,y,z)=Start+x+X*y+X*Y*z` with array order `(Z,Y,X)`.
- XY, XZ and YZ accumulation follows arithmetic progressions of step `X*Y`,
  `X` and `1`, respectively.
- Along a progression, `gcd(b+kM,M)=gcd(b,M)`. A noncoprime class cannot contain
  a prime except for the explicit exceptional term equal to a prime divisor.
- The one-dimensional DFT of the coprime indicator modulo `M` is the Ramanujan
  sum `c_M(k)`.
- The periodic pair count of two coprime residues factors prime by prime through
  the Chinese remainder theorem.

These are known mathematical results or direct consequences of the embedding,
not claims of new number theory.

## Analytical predictions

Phase II proves exact mean, coefficient variance and expected spectral power
for a fixed-size uniform sample of coprime residues. It also gives a general
forced-peak criterion: if the allowed support lies in a character coset, every
fixed-size sample has the corresponding maximal Fourier coefficient. The parity
peak observed in Phase I is a special case.

For `M=X*Y`, horizontal 2D frequencies correspond directly to Ramanujan sums
`c_M(uY)`. Vertical frequencies generally involve block sums. The row-major
embedding therefore creates anisotropy even when the underlying residue system
is unchanged.

## Computational verification

- Independent enumeration verifies the Linear mapping, projections, masks and
  arithmetic functions on small cases.
- Direct DFT oracles verify the implemented Fourier power and ratios.
- Phase II checks all 1,074 coefficients for selected prime, prime-power,
  composite, primorial and `30p` moduli.
- Exact verification for every `2 <= M <= 120` checks Ramanujan sums, CRT pair
  counts and the forced-peak formula.
- Explicit seeds and manifests accompany both experimental phases.

## Experimental observations

- Uniform random support makes modular patterns appear extremely anomalous.
- In the 30×30×2, Start=1001 case, the dominant FFT peak is identical in every
  coprime-conditioned sample and is exactly explained by parity support.
- Raw FFT metrics vary substantially between different `X*Y` factorizations of
  the same modulus.
- Density, depth, Start, aspect ratio and field selection affect local and
  spectral statistics.
- Across the limited Phase II hierarchy, no convincing prime-specific residual
  remained after appropriate modular controls.

## Known limitations

- The application baseline is uniform over the plane, not conditioned on
  coprimality or local prime density.
- The coprime mask is not density-matched to observed prime hits.
- Structural, beauty and multimetric residual scores are not significance tests.
- The application does not provide automatic confidence intervals, p-values or
  multiple-comparison correction.
- Historical v170 figures and archived papers are exploratory and do not
  constitute v1.0.0 validation.
- CUDA numerical equivalence and interactive OpenGL remain environment-dependent
  and were not certified by the current CPU audit.

## Open research questions

- Do any statistics remain stable on held-out intervals under a null conditioned
  on coprimality, exact count and `1/log(n)` intensity?
- Can residual Fourier power be predicted from two-point Hardy–Littlewood
  singular-series corrections?
- Which quantities are invariant under CRT-adapted coordinates but not under
  row-major reshaping?
- How should the complete scan-and-selection process be calibrated to avoid
  maximum-selection and multiple-comparison bias?

No new theorem about the distribution of primes is claimed.
