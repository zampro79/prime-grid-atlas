# Spectral families of modular \(p\times 30\) embeddings

[Italian original](research_protocol.it.md)

> **Implementation status:** this document also contains a future plan.
> Exact hit permutations, prime-like nulls, Moran's I, intervals,
> p-values and multiple-comparison corrections are not implemented in the release.
> [RESEARCH.md](../RESEARCH.md) documents what the code actually computes.

## Working document for theoretical and experimental development

**Project:** Prime Grid Atlas

**Reference software version:** v1.0.0 PySide6/GPU
**Status:** research draft

**Date:** July 30, 2026

This English translation preserves the draft's hypotheses and proposed equations, with owner-approved implementation-status clarifications. The Italian original remains unchanged. See the [scientific audit](../SCIENTIFIC_AUDIT.md) for subsequently identified limitations; translating a proposal does not validate it.

---

## 1. Objective

This document develops a research program for configurations

\[
X=p,\qquad Y=30,\qquad Z\ge 1,
\]

where \(p>5\) is prime. The modulus associated with the XY projection is

\[
M=30p=2\cdot3\cdot5\cdot p.
\]

The aim is not to formulate new laws of prime distribution, but to study quantitatively:

1. the geometry of the mask of coprime residue classes modulo \(30p\);
2. the spectral structure induced by the rectangular \(p\times30\) embedding;
3. how finite prime overlays inherit this structure;
4. whether a residual remains unexplained by coprime geometry alone;
5. how these geometries depend on the class \(p\bmod30\).

The case \(p=71\), for which

\[
71\equiv11\pmod{30},
\]

is the empirical starting point, not the result to be proved.

---

## 2. Scope of the analysis

The theoretical statements in this document apply to:

- the v1.0.0 Linear embedding for protocol experiments;
- the **XY** projection;
- an explicitly stated starting value;
- the embedding

\[
n_s(x,y,z)=s+zXY+yX+x,
\]

with

\[
0\le x<X,\qquad 0\le y<Y,\qquad 0\le z<Z.
\]

In the main case:

\[
X=p,\qquad Y=30,
\]

and therefore

\[
n_s(x,y,z)=s+30pz+py+x.
\]

Version v1.0.0 also offers thirteen exploratory placements. `Linear` is the chosen reference for the complete coordinate model and is explicitly required by the implemented protocol metrics. Fixed planar alternatives also preserve the vertical step XY, although their planar progressions and geometry generally differ; preserving that vertical step alone does not make them part of this protocol.

XZ and YZ projections may be studied as controls, but they do not represent the same system of residue classes modulo \(30p\).

In v1.0.0, the `Prime research`, `Scientific controls` and `Modular diagnostics` groups constitute the permitted catalog for the main work. Generic exploratory sequences from v180 may suggest additional comparisons or controls, but their visual patterns do not enter the protocol without a new explicit hypothesis, baseline and falsification criterion defined before analysis.

---

## 3. Fundamental definitions

### 3.1 Residue associated with a cell

For a cell \((x,y)\) in the XY plane, define

\[
r_s(x,y)=s+py+x.
\]

The corresponding vertical column contains

\[
n_k=r_s(x,y)+30pk,
\qquad 0\le k<Z.
\]

### 3.2 Coprime mask

Define

\[
C_{p,s}(x,y)=
\mathbf 1_{\gcd(r_s(x,y),30p)=1}.
\]

This is the deterministic geometry of potentially prime-bearing residue classes.

### 3.3 Binary prime mask at depth \(Z\)

Define

\[
A_{p,s,Z}(x,y)=
\mathbf 1_{\exists\,0\le k<Z:\ r_s(x,y)+30pk\text{ is prime}}.
\]

This mask records whether a column contains at least one prime within the observed depth.

### 3.4 Hit field

Also define the count

\[
H_{p,s,Z}(x,y)=
\sum_{k=0}^{Z-1}
\mathbf 1_{\mathbb P}(r_s(x,y)+30pk).
\]

Always distinguish:

- the binary mask \(A\);
- the count field \(H\);
- the coprime mask \(C\).

These three quantities are not interchangeable.

### 3.5 Power spectrum

For a two-dimensional field \(U\), after subtracting the mean, define

\[
\widetilde U=U-\langle U\rangle
\]

and

\[
P_U(k_x,k_y)=|\mathcal F_2(\widetilde U)|^2.
\]

For comparisons between different dimensions, use the normalized spectrum

\[
\widehat P_U=
\frac{P_U}{\sum_{k_x,k_y}P_U(k_x,k_y)}.
\]

---

## 4. Known results and immediate consequences

This section contains no new conjectures.

### 4.1 Sterility of noncoprime classes

If

\[
d=\gcd(r_s(x,y),30p)>1,
\]

then every term in the column is divisible by \(d\). The column can contain at most the exceptional prime \(d\), if it occurs in the observed interval.

### 4.2 Binary convergence for a fixed modulus

For every class \(r\) coprime with \(30p\), Dirichlet's theorem guarantees infinitely many primes in the progression

\[
r+30pk.
\]

Since there are finitely many reduced residue classes, for each fixed \(p\) and \(s\) there is a finite depth \(Z_0(p,s)\) beyond which all coprime classes have been activated at least once.

Consequently, apart from exceptional primes in noncoprime classes,

\[
A_{p,s,Z}\longrightarrow C_{p,s}
\]

as \(Z\to\infty\).

Qualitative convergence is therefore not a conjecture. The experimental and theoretical questions concern:

- the convergence rate;
- uniform dependence on \(p\);
- behavior when \(p\) and \(Z\) grow together;
- convergence of metrics and normalized spectra.

### 4.3 Coprime density

For \(p>5\):

\[
\frac{\varphi(30p)}{30p}
=
\left(1-\frac12\right)
\left(1-\frac13\right)
\left(1-\frac15\right)
\left(1-\frac1p\right)
=\frac4{15}\left(1-\frac1p\right).
\]

For \(p=71\):

\[
\frac{\varphi(2130)}{2130}
=\frac{560}{2130}
\approx0.26291.
\]

### 4.4 Action of the class \(p\bmod30\)

The mask simultaneously satisfies

\[
r_s(x,y)\equiv s+x\pmod p
\]

and

\[
r_s(x,y)\equiv s+x+(p\bmod30)y\pmod{30}.
\]

The component modulo \(p\) produces an exclusion aligned along X, while the wheel modulo 30 is translated from one row to the next by

\[
a=p\bmod30.
\]

Since \(p>5\),

\[
a\in(\mathbb Z/30\mathbb Z)^\times
=\{1,7,11,13,17,19,23,29\}.
\]

The 30 rows therefore traverse a complete orbit of translations modulo 30.

---

## 5. Conjecture A — Eight spectral families

### Qualitative statement

After normalization of the X axis, coprime \(p\times30\) geometries form eight spectral families determined by the class

\[
p\bmod30.
\]

### Preliminary quantitative form

Let \(p\) and \(q\) be primes greater than 5 with

\[
p\equiv q\pmod{30}.
\]

Let \(\mathcal R\) be a specified operator for resampling the spectrum onto a common grid. The conjecture is that

\[
d_{\mathrm{spec}}(p,q)
=
\left\|
\mathcal R(\widehat P_{C_{p,s}})
-
\mathcal R(\widehat P_{C_{q,s}})
\right\|_2
\]

is, on average, smaller than the distance between primes belonging to different classes modulo 30.

A stronger asymptotic version would be

\[
d_{\mathrm{spec}}(p,q)\to0
\]

as \(p,q\to\infty\) within the same class, but this formulation requires a rigorous geometric normalization operator.

### Prediction for 71

Since

\[
71\equiv11\pmod{30},
\]

the \(71\times30\) configuration should be more similar to

\[
41\times30,\quad101\times30,\quad131\times30,\quad191\times30
\]

than to comparably sized configurations belonging to other classes modulo 30.

### Falsification criterion

The conjecture is weakened or rejected if a classifier trained exclusively on coprime-mask spectra cannot distinguish the eight classes better than chance on a separate test set.

---

## 6. Conjecture B — Spectral inheritance of prime overlays

### Statement

The main spectral structures of the binary prime overlay converge to those of the corresponding coprime mask as \(Z\) increases.

Define

\[
\rho(p,s,Z)=
\operatorname{corr}
\left(
\widehat P_{A_{p,s,Z}},
\widehat P_{C_{p,s}}
\right).
\]

The proposed test asks whether

\[
\rho(p,s,Z)\to1
\]

and at what rate.

### Nontrivial component

For fixed \(p\), eventual binary convergence follows from Dirichlet's theorem. The interesting object is a uniform scaling law, for example in the regime

\[
p\to\infty,
\qquad
Z=Z(p)\to\infty.
\]

No form such as \(1/\log Z\) is assumed in advance. Candidate laws must be compared through out-of-sample validation.

### Falsification criterion

The strong spectral conjecture is rejected if, even after almost all coprime classes have been activated, spectral correlation does not increase or exhibits irregular dependencies incompatible with the density of cells not yet activated.

---

## 7. Conjecture C — Geometric equivalence within the same class

### Statement

Let \(G\) be a vector of standardized observables including at least:

- FFT peak ratio;
- FFT axis ratio;
- low-frequency ratio;
- spectral entropy;
- autocorrelation along X and Y;
- orientation of spectral maxima;
- mean local entropy;
- edge density.

For primes \(p,q\) in the same class modulo 30, the conjecture is that

\[
d_G(p,q)
=
\left\|
\widetilde G(C_{p,s})-
\widetilde G(C_{q,s})
\right\|_2
\]

is systematically smaller than the distance between different classes.

Components must be standardized on a training set:

\[
\widetilde G_i=
\frac{G_i-\mu_i}{\sigma_i}.
\]

### Suggested test

Use eight-class classification with:

- train/test splits over disjoint ranges of \(p\);
- nearest centroid as an interpretable model;
- a confusion matrix;
- balanced accuracy;
- a label permutation test.

---

## 8. Conjecture D — Extremality of orientation

### Question

For a fixed modulus

\[
M=30p,
\]

the geometry depends on the rectangular factorization

\[
M=XY.
\]

### Preliminary statement

The orientations

\[
(X,Y)=(p,30)
\qquad\text{and}\qquad
(30,p)
\]

are candidates for extremizing anisotropy measures relative to other factorizations of \(30p\), but along different directions.

One testable form is

\[
R_{\mathrm{axis}}(p,30)
\ge
R_{\mathrm{axis}}(X,Y)
\]

for the other pairs \((X,Y)\) with \(XY=30p\), or a variant based on the leading eigenvalue of the spectral tensor.

### Essential control

The comparison must not confuse arithmetic anisotropy with aspect ratio. All matrices must be:

- resampled onto a common grid;
- compared against random masks with the same aspect ratio;
- analyzed using metrics corrected for rectangular shape.

---

## 9. Conjecture E — Absence or persistence of a prime-specific residual

This is the project's central question.

### Null hypothesis

After controlling for:

- the coprime mask;
- alive-cell density;
- the exact hit distribution;
- matrix dimensions;
- depth \(Z\);

the prime-specific geometric residual tends to zero:

\[
D(p,s,Z)	o0.
\]

### Proposed definition

Let \(G\) be the metric vector, and let \(\mu_0,\Sigma_0\) be the mean and covariance estimated from a null ensemble. Define the Mahalanobis distance

\[
D^2=
(G_{\mathrm{prime}}-G_{\mathrm{coprime}})^T
\Sigma_0^{-1}
(G_{\mathrm{prime}}-G_{\mathrm{coprime}}).
\]

This is a proposed replacement for the L1/L2 sum of unnormalized metrics, not an implemented change.

**Open methodological decision:** the draft defines a null mean μ0 but centers the displayed difference on the deterministic coprime metric vector. These are distinct reference choices. Before implementation, specify whether the statistic measures departure from that deterministic control or from the null mean, and define its null calibration accordingly. The equation is retained pending that decision; no significance interpretation is established by this proposal.

### Two scientifically valid outcomes

1. **Residual compatible with the null.** The observed geometry is explained almost entirely by coprime classes and occupancy effects.
2. **Persistent residual.** Some prime-specific components remain outside the null ensemble and require a more precise model.

Neither outcome should be considered a failure.

---

## 10. Experimental design

### 10.1 Prime set

Construct eight balanced groups:

\[
\mathcal P_a=
\{p\text{ prime}:p\equiv a\pmod{30}\},
\]

with

\[
a\in\{1,7,11,13,17,19,23,29\}.
\]

Use at least:

- 30 primes per class for exploratory analysis;
- 100 primes per class for confirmatory analysis;
- comparable magnitude ranges across classes.

### 10.2 Depth

Use a logarithmic scale, for example:

\[
Z\in\{1,2,4,8,16,32,64,128,256,512,1024\}.
\]

Record both \(A\) and \(H\) for every configuration.

### 10.3 Starting values

The main experiment must fix

\[
s=1.
\]

Secondary experiments may use multiple values of \(s\), identifying them as translation and robustness tests.

### 10.4 Baselines

Use at least three null models:

1. **Exact spatial permutation:** permute all cells while preserving hit values exactly.
2. **Randomized coprime mask:** preserve the number of coprime classes but randomize their positions.
3. **Prime-like model:** a probability depending on \(n\) and conditioned on coprimality, inspired by a wheel-corrected Cramér model.

For preliminary analyses, use at least 200 replicates; for final results, at least 1,000 replicates per configuration or an adaptive strategy based on interval precision.

### 10.5 Exploratory/confirmatory separation

- Choose metrics and thresholds on the exploratory set.
- Register hypotheses before confirmatory analysis.
- Do not use primes in the confirmatory set to tune scores or visualizations.

---

## 11. Metrics to record

### 11.1 Occupancy metrics

- alive density;
- coprime alive ratio;
- noncoprime alive ratio;
- fraction of coprime classes not yet activated;
- mean and variance of hits on coprime classes.

### 11.2 Spatial metrics

- Moran's I or another specified spatial autocorrelation;
- autocorrelation along X and Y;
- local entropy with explicit window and bin definitions;
- edge density with a preregistered threshold;
- connected-component statistics.

### 11.3 Spectral metrics

- peak power ratio;
- axis power ratio;
- low-frequency power ratio;
- normalized spectral entropy;
- orientation of the non-DC maximum;
- spectral second-moment tensor;
- correlation between prime and coprime spectra.

### 11.4 Distance metrics

- L2 distance after standardization;
- Mahalanobis distance;
- Jensen–Shannon divergence between normalized spectra;
- spectral earth mover's distance, if computationally feasible.

---

## 12. Statistical analysis

For each metric \(T\), calculate relative to the baseline:

\[
z_T=
\frac{T_{\mathrm{obs}}-\mu_T}{\sigma_T}.
\]

Report:

- mean;
- standard deviation;
- confidence interval;
- 2.5%, 50%, 97.5% quantiles;
- empirical p-value;
- multiple-comparison correction;
- effect size.

For the eight families modulo 30, use:

- ANOVA or a nonparametric alternative;
- a model including \(\log p\), class modulo 30 and \(\log Z\);
- class × depth interaction;
- validation on primes not used during exploration.

Do not use “significant” without a specified statistical procedure.

---

## 13. Control experiments

### Control A — Transposition

Compare

\[
p\times30
\qquad\text{and}\qquad
30\times p.
\]

### Control B — Nearby composite numbers

Compare \(p\) with composite values of similar magnitude, distinguishing:

- numbers coprime with 30;
- numbers not coprime with 30;
- squares and products of two primes.

### Control C — Other wheels

Repeat the protocol with:

\[
6p,\qquad 30p,\qquad 210p.
\]

### Control D — Geometric permutations

Apply transformations preserving the multiset of values:

- row permutation;
- column permutation;
- cyclic translations;
- rotation and transposition.

### Constraint E — Embedding

All experiments in the v1.0.0 protocol use the Linear embedding. Nonlinear placements are available for exploratory geometric comparisons, but their results are not directly comparable to the protocol's Linear metrics.

---

## 14. Reproducible outputs

Every dataset row must include at least:

- software version and commit;
- seed;
- \(p,X,Y,Z,M\);
- \(p\bmod30\);
- start;
- embedding (`Linear`, a fixed value recorded automatically);
- plane and depth;
- field type: prime, coprime or baseline;
- number of trials;
- metric definition/version;
- CPU/GPU timings;
- all observed metrics;
- baseline mean, standard deviation and quantiles.

The project's minimum outputs should be:

```text
experiments/
├── protocol.yaml
├── primes_by_class.csv
├── raw_metrics.csv
├── baseline_summary.csv
├── spectral_fingerprints.npz
├── figures/
└── logs/
```

---

## 15. Required figures

1. \(71\times30\) coprime mask.
2. Prime overlays for multiple values of \(Z\).
3. Side-by-side prime/coprime/random FFTs.
4. Spectral correlation as a function of \(Z\).
5. Comparison of the eight classes modulo 30.
6. Confusion matrix for the family classifier.
7. Comparison of \(p\times30\) against \(30\times p\).
8. Baseline distribution and position of the observed value.
9. Standardized residual as a function of \(p\) and \(Z\).
10. CPU/GPU timings and the GPU break-even threshold.

---

## 16. Proposed paper structure

1. Introduction and research question.
2. Definition of the embedding with the start parameter.
3. Exact geometry of the \(p\times30\) coprime mask.
4. Action of the classes \(p\bmod30\).
5. Complete metric definitions.
6. Null models and statistical protocol.
7. Experiment on the eight families.
8. Convergence with depth.
9. Prime/coprime/random comparison.
10. Dependence on orientation.
11. Out-of-sample results.
12. Limitations.
13. Conclusions.

---

## 17. Operational plan

### Phase 1 — Specification

- [ ] Freeze metric definitions.
- [ ] Correct the baseline to permute hit counts exactly.
- [ ] Add standard deviation and quantiles.
- [ ] Define the experimental protocol format.

### Phase 2 — Headless engine

- [ ] Add a general-purpose headless scan CLI. The separate `tools/scientific_audit_experiments.py` CLI already runs fixed audit experiments; it is not a general scan interface.
- [x] Save the seed and application configuration with every CSV through a JSON sidecar.
- [x] Add a hardware-conditional CPU/GPU equivalence test (`tests/test_backend.py`).
- [ ] Run and validate that test on compatible CUDA hardware without silent CPU fallback; a skipped test does not establish equivalence.
- [ ] Add automated benchmarks.

### Phase 3 — Pilot study

- [ ] Select 30 primes per class modulo 30.
- [ ] Run the preliminary depth scale.
- [ ] Assess metric stability and redundancy.
- [ ] Estimate the cost of confirmatory baselines.

### Phase 4 — Internal preregistration

- [ ] Freeze conjectures and falsification criteria.
- [ ] Separate training and test sets.
- [ ] Freeze the planned figures and statistical analyses.

### Phase 5 — Confirmatory study

- [ ] Run at least 100 primes per class.
- [ ] Run enough baseline trials for the required precision.
- [ ] Automatically generate tables and figures.
- [ ] Preserve all negative results.

---

## 18. Interpretation of possible results

### Outcome 1 — Eight clearly distinguishable families

This would support the existence of a geometric-spectral classification of the embedding determined by the action of \((\mathbb Z/30\mathbb Z)^\times\).

### Outcome 2 — Visual families without statistical robustness

The images would mainly reflect aspect ratio, resampling or visual selection. The model should be simplified.

### Outcome 3 — No prime-specific residual

This result would show quantitatively that the observed structures are explained by coprime geometry and finite occupancy.

### Outcome 4 — A stable residual outside the baseline

The next step would be to identify which known arithmetic statistics are missing from the null model before discussing new structure.

---

## 19. Guiding principle

The project should not seek visual confirmation of the \(71\times30\) configuration. It should actively attempt to falsify the hypothesis that 71 is special.

The strongest scientific result will be one that survives:

- comparison between classes modulo 30;
- variation of \(Z\);
- grid transposition;
- spectral normalization;
- exact baselines;
- out-of-sample tests;
- multiple-comparison correction.

The final question is not:

> Why does \(71\times30\) produce an attractive image?

but:

> Which components of its geometry are necessary consequences of the wheel modulo 30, which depend on the embedding, and which, if any, remain specific to finite-depth prime occupancy?
