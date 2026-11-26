# Prime Grid Atlas — Research II

## Status and scope

This report develops an analytic theory for the Linear embedding

\[
n(x,y,z)=s+x+Xy+XYz.
\]

It is a mathematical investigation, not a validation of visual patterns.  The
application source was not imported or modified.  The independent experiment
is `research_ii_experiments.py`; generated data are under `data/`.

Evidence labels used here are:

- **PROVED**: accompanied by a proof below;
- **KNOWN / REDISCOVERED**: a standard result used in this setting;
- **OBSERVED**: finite numerical evidence only;
- **CONJECTURED**: a falsifiable proposed extension;
- **ARTIFACT**: forced by representation, support, or numerical definition;
- **OPEN**: not decided by this study.

## 1. Fourier theory of admissible residues

Let

\[
U_M(n)=\mathbf 1_{(n,M)=1},\qquad n\in\mathbb Z/M\mathbb Z,
\]

and use the unnormalised DFT

\[
\widehat U_M(k)=\sum_{n\bmod M}U_M(n)e^{-2\pi i kn/M}.
\]

### Theorem 1 — exact spectrum of the coprime mask

**Statement (KNOWN / REDISCOVERED).** For every integer \(k\),

\[
\widehat U_M(k)=c_M(k)
=\mu\!\left(\frac M g\right)
  \frac{\varphi(M)}{\varphi(M/g)},
\qquad g=(M,k),
\]

where \(c_M(k)\) is the Ramanujan sum.

**Proof.** The first equality is the definition of a Ramanujan sum.  Insert
\(\mathbf1_{(n,M)=1}=\sum_{d\mid(n,M)}\mu(d)\), interchange sums, and use
orthogonality of additive characters.  Only divisors for which \(M/d\mid k\)
survive.  Their divisor sum gives the displayed closed form.  ∎

For an interval beginning at \(s\), the mask on offsets \(r=0,\ldots,M-1\)
is \(U_M(s+r)\).  Translation multiplies coefficient \(k\) by
\(e^{2\pi i ks/M}\), so all spectral powers remain unchanged.

The experiment checks all 1,074 coefficients for
\(M=11,16,27,30,60,210,330,390\).  Maximum direct-formula error is
\(5.9\times10^{-12}\), consistent with floating-point roundoff.

### Corollary 1 — CRT factorisation

If \((a,b)=1\), then

\[
c_{ab}(k)=c_a(k)c_b(k).
\]

**Proof.** The Chinese remainder theorem identifies a unit modulo \(ab\) with
a pair of units modulo \(a,b\), and the additive character factors.  ∎

Thus the one-dimensional spectrum is completely determined prime-power by
prime-power.  This is arithmetic structure, not residual prime structure.

### Proposition 2 — exact finite-population null

Let \(A\subseteq\mathbb Z/M\mathbb Z\), \(|A|=L\), and choose a subset
\(S\subseteq A\) of exactly \(K\) points uniformly without replacement.  Put

\[
Z_k=\sum_{n\in S}e^{-2\pi i kn/M},\qquad
F_A(k)=\sum_{n\in A}e^{-2\pi i kn/M}.
\]

Then **PROVED**:

\[
\mathbb E Z_k=\frac KL F_A(k),
\]

\[
\mathbb E\left|Z_k-\mathbb EZ_k\right|^2
=\frac{K(L-K)}{L-1}
 \left(1-\frac{|F_A(k)|^2}{L^2}\right),
\]

and therefore

\[
\mathbb E|Z_k|^2
=\frac{K^2}{L^2}|F_A(k)|^2
+\frac{K(L-K)}{L-1}
 \left(1-\frac{|F_A(k)|^2}{L^2}\right).
\]

**Proof.** Write the sample with inclusion indicators \(I_n\).  Their means
are \(K/L\), variances are \(K(L-K)/L^2\), and distinct indicators have
covariance \(-K(L-K)/(L^2(L-1))\).  Expanding the squared modulus and collecting
diagonal and off-diagonal terms gives the formulas.  ∎

For \(A=(\mathbb Z/M\mathbb Z)^\times\), substitute \(F_A=c_M\).  Across the
nondegenerate simulated coefficients, the median relative error of empirical
complex variance is 4.3% with 240 trials; the 95th percentile is 12.5%.

### Theorem 3 — general forced-peak criterion

Let a binary field occupy \(K\) points in an \(N\)-point periodic grid.  If an
additive character \(\chi\ne1\) is constant on the allowed support, then every
size-\(K\) occupancy of that support has

\[
|\widehat f(\chi)|=K.
\]

No Fourier coefficient can have larger modulus.  After centring the field,
Parseval gives total non-DC power \(K(N-K)\).  Hence **PROVED**:

\[
\operatorname{peak\ ratio}=\frac{K}{N-K}.
\]

**Proof.** Constancy makes the Fourier sum \(K\lambda\), \(|\lambda|=1\).
The triangle inequality bounds every coefficient by \(K\).  Centring changes
only DC, and unnormalised Parseval gives \(NK-K^2\).  ∎

The parity result from Phase I is the case where \(M\) is even and every unit
is odd; the order-two character is constant.  The theorem also covers any
support contained in a coset of the kernel of a nontrivial character.

### The 2D atlas and the privileged horizontal axis

Write \(M=XY\), \(r=x+Xy\).  At 2D frequency \((u,v)\),

\[
F(u,v)=\sum_{x,y}U_M(s+x+Xy)
e^{-2\pi i(ux/X+vy/Y)}.
\]

For \(v=0\), the phase is the one-dimensional character with
\(k=uY\); consequently

\[
F(u,0)=e^{2\pi i uYs/M}c_M(uY).
\]

This identity was checked for all 92 tested factorizations, with maximum error
\(2.4\times10^{-12}\).  In general the vertical frequencies contain DFTs of
block sums and are not single Ramanujan sums.  The row-major embedding therefore
breaks x/y symmetry even when arithmetic modulo \(M\) does not.

## 2. Exact autocorrelation anatomy

### Theorem 4 — coprime pair count

Define the periodic pair count

\[
C_M(h)=\sum_{n\bmod M}U_M(n)U_M(n+h).
\]

For \(M=\prod_{p^a\parallel M}p^a\), **PROVED**:

\[
C_M(h)=\prod_{p^a\parallel M}p^{a-1}
\begin{cases}
p-1,&p\mid h,\\
p-2,&p\nmid h.
\end{cases}
\]

**Proof.** Modulo \(p\), if \(p\mid h\), only the residue zero is forbidden;
otherwise both \(0\) and \(-h\) are forbidden.  Each allowed residue has
\(p^{a-1}\) lifts modulo \(p^a\).  Multiply the independent local counts by
CRT.  ∎

This formula is the exact finite-wheel precursor of local factors in
Hardy–Littlewood singular series.  Peaks in autocorrelation at shifts divisible
by many prime factors of \(M\) are necessary sieve effects.

Wiener–Khinchin supplies an independent check: the DFT of \(C_M\) is
\(|c_M(k)|^2\).  Thus the spectral and pair-correlation descriptions are two
views of the same modular structure.

## 3. Anatomy by modulus and factorisation

### Prime modulus \(p\)

\(c_p(0)=p-1\) and \(c_p(k)=-1\) otherwise.  Apart from DC, the complete
coprime mask has flat one-dimensional power.  Any visually preferred direction
therefore comes from reshaping, finite sampling, or the prime field, not from
unequal nonzero Ramanujan magnitudes.

### Prime powers \(p^a\)

The spectrum is sparse by divisibility of \(k\): coefficients vanish when
\(p^{a-1}\nmid k\), equal \(-p^{a-1}\) when
\(p^{a-1}\parallel k\), and equal \(\varphi(p^a)\) at DC.  Prime powers impose
hierarchical periodic bands.

### Square-free composites and primorials

CRT multiplies local factors.  Primorials combine many exclusion periods and
produce strong, highly structured axis harmonics.  These patterns are expected
wheel-sieve geometry.

For the full masks in the experiment, changing only \(X\times Y=M\) produced:

| M | peak-ratio range | axis-ratio range |
|---:|---:|---:|
| 30 | 0.12576–0.36364 | 0.13636–1.00000 |
| 210 | 0.10247–0.29630 | 0.07716–1.00000 |
| 330 | 0.11067–0.32000 | 0.04800–1.00000 |
| 390 | 0.11293–0.32653 | 0.03656–1.00000 |

The unit set and one-dimensional Ramanujan spectrum are invariant, while the 2D
allocation of power is not.  Raw 2D FFT metrics are therefore invariants of the
pair *(arithmetic mask, factorisation/reshape)*, not of \(M\) alone.

### Family \(M=30p\)

When \(p\notin\{2,3,5\}\), CRT gives

\[
c_{30p}(k)=c_{30}(k)c_p(k),\qquad
\varphi(30p)=8(p-1).
\]

No new spectral law is needed to explain the coprime mask.  Interesting prime
questions can begin only after subtracting or conditioning on this exact
product structure.

## 4. Reference-model hierarchy

The experiment uses five configurations, 240 trials per null and ten metrics:
occupancy, mean/variance of hits, fixed-denominator spectral entropy, peak and
axis ratios, nearest and distance-two autocovariances.  The real-prime field is
level 6.

1. `L1_uniform`: calibrated independent uniform draws.
2. `L2_coprime_M`: draws restricted to numbers coprime to \(M\).
3. `L3_coprime_log`: the same support with probability proportional to
   \(1/\log n\).
4. `L4_wheel_7`: finite wheel through 7 with \(1/\log n\) weights.
5. `L5_deep_sieve_19`: finite wheel through 19, a proxy for more local factors.
6. Real primes.

Levels 4–5 reproduce some local factors that occur in prime-tuple heuristics;
they are **not** full Hardy–Littlewood models.  The singular-series model for a
tuple \(\mathcal H\) uses

\[
\mathfrak S(\mathcal H)=
\prod_q\left(1-\frac{\nu_q(\mathcal H)}q\right)
       \left(1-\frac1q\right)^{-|\mathcal H|},
\]

and remains conjectural in general.

### Observed residuals

There are 50 metric/configuration comparisons at each level:

| Null | maximum \(|z|\) | \(|z|>2\) | \(|z|>3\) |
|---|---:|---:|---:|
| Uniform | 170.00 | 41 | 37 |
| Coprime to M | 1.52 | 0 | 0 |
| Coprime + \(1/\log n\) | 1.51 | 0 | 0 |
| Wheel through 7 | 3.86 | 3 | 2 |
| Wheel through 19 | 1.26 | 0 | 0 |

**OBSERVED:** the spectacular deviations against uniform randomness disappear
once modular support is respected.  The non-monotonic wheel-7 row warns that a
partially specified sieve can fit worse than a control aligned with \(M\).

**No statistically significant residual phenomenon was found.** This statement
is limited to five configurations, these metrics and these finite Monte Carlo
runs.  The empirical fractions are descriptive; no claim relies on an
uncorrected minimum over the 50 comparisons.

## 5. Artifacts and necessary distinctions

- **ARTIFACT:** parity/Nyquist peaks and their general character-coset form.
- **ARTIFACT:** axis power changes under different \(X\times Y\) reshapes.
- **ARTIFACT:** density and depth alter projected occupancy and hit variance.
- **ARTIFACT:** spectral entropy normalised by the count of numerically positive
  bins is not symmetry robust.  This report uses a fixed denominator \(M-1\).
- **NECESSARY:** Ramanujan harmonics of the admissible support.
- **STATISTICALLY EXPECTED:** fluctuations given by Proposition 2.
- **POTENTIAL RESIDUAL:** only a reproducible deviation beyond an arithmetic,
  intensity-matched and selection-corrected null.

The hierarchy is not nested in every finite interval, and z-scores from
different models are not interchangeable.  Exact conditioning on total prime
count would be preferable for a formal randomisation test.

## 6. Relation to known mathematics and originality

Theorem 1, CRT multiplicativity, and the pair-count local factors are standard
number theory recast for this atlas.  The prime-pair local product is the same
mechanism underlying Hardy–Littlewood singular series.  Modern formulations
explicitly express those series as products of local densities; see
Lemke Oliver–Soundararajan, *Unexpected biases in the distribution of
consecutive primes* (PNAS 2016), and Goldston–Pintz–Yıldırım, *Primes in Tuples
I* (Annals of Mathematics 2009).

The exact finite-population formulas are standard sampling identities applied
to additive characters.  The forced-peak theorem is elementary.  Their joint
application to Prime Grid Atlas is useful and may be novel as documentation or
experimental design, but **no claim of mathematical originality is made**.
Establishing novelty would require a dedicated literature search beyond the
sources consulted here and, for publication, independent expert review.

Relevant sources:

- G. H. Hardy and J. E. Littlewood's prime-tuple conjecture as formulated in
  [Primes in Tuples I](https://annals.math.princeton.edu/wp-content/uploads/annals-v170-n2-p10-p.pdf).
- R. J. Lemke Oliver and K. Soundararajan,
  [Unexpected biases in the distribution of consecutive primes](https://www.pnas.org/content/pnas/113/31/E4446.full.pdf),
  including the singular-series local factors.
- The historical Ulam-grid context in Martin Gardner's
  [1964 Scientific American article](https://www.wkbpic.com/wkbx/SA/1964/1964-03-01.pdf).
- For the limits of naive independent prime models,
  [Small-scale distribution of linear patterns of primes](https://londmathsoc.onlinelibrary.wiley.com/doi/full/10.1112/jlms.13001).

## 7. Counterexamples and falsification attempts

1. Reflections falsify the application's positive-support spectral-entropy
   invariance; the fixed-denominator alternative passes exact spectral
   permutations by construction.
2. Factorisations of the same \(M\) falsify invariance of raw axis and peak
   metrics under reshape.
3. Coprime-conditioned samples falsify interpretation of the parity peak as a
   prime-specific phenomenon.
4. The wheel-7 experiment falsifies the assumption that adding any sieve
   condition must monotonically improve every metric.
5. Prime, prime-power, composite, primorial, and \(30p\) cases were included in
   the Ramanujan identity tests; no counterexample was found.

## 8. Open problems and proposed next experiments

### Conjecture A — calibrated residual convergence

For fixed shape and depth, after conditioning on local admissibility through a
wheel bound \(B\), exact count, and \(1/\log n\), standardised low-order atlas
statistics for primes approach the null as both interval location and \(B\)
increase suitably.  This is deliberately broad and may fail on statistics
sensitive to Hardy–Littlewood correlations.

### Conjecture B — spectral residual from singular series

The expected residual power at frequency \(k\), after subtracting the exact
Ramanujan-support contribution, can be expressed as a Fourier transform of
two-point singular-series corrections.  A rigorous finite formula can be
written for a specified finite wheel; passage to all primes is conjectural.

### Required next work

1. Implement exact-count weighted sampling, not only calibrated Bernoulli
   sampling.
2. Add explicit Hardy–Littlewood pair predictions for every grid displacement
   \(h=\Delta x+X\Delta y+M\Delta z\).
3. Use disjoint, preregistered Start intervals and a held-out confirmation set.
4. Simulate the maximum statistic over the full scanned family to incorporate
   selection and multiple comparisons.
5. Analyse depth as a marked point process: hit-count factorial moments retain
   information lost by alive occupancy.
6. Use CRT-adapted coordinates as a control embedding.  Comparing them with
   row-major coordinates would isolate reshape anisotropy.
7. Scale to segmented sieving and intervals high enough that \(1/\log n\)
   varies slowly but measurably without allocating a sieve up to `Start`.

## 9. Can the Atlas become a rigorous research environment?

Yes, with a narrower scientific contract.  Its strongest role is as a visual
and numerical front end for explicitly specified finite arithmetic models.
For rigor it needs:

- exact arithmetic predictions beside plots;
- null models conditioned on the same modular support;
- metric definitions stable under mathematical symmetries;
- complete trial distributions and provenance;
- preregistration/holdout for scans;
- a strict separation between arithmetic invariants, embedding-dependent
  quantities, and inferential residuals.

At present it is a capable exploratory laboratory.  It is not yet an
inferential system for discovering new laws of primes.  Phase II found useful
exact theory for its dominant structures, but no unexplained prime-specific
phenomenon.

## Reproduction

From the repository root:

```bash
python research_ii/research_ii_experiments.py \
  --trials 240 --seed 20261126
```

Outputs:

- `data/spectral_ramanujan.csv` — exact and sampled spectral formulas;
- `data/factorization_anatomy.csv` — 92 factorizations and 2D metrics;
- `data/hierarchy_trials.csv` — all Monte Carlo trials;
- `data/hierarchy_summary.csv` — observed/null comparisons;
- `data/manifest.json` — seed, trial count, NumPy version and limitations.
