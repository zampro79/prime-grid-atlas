# Research I reproduction report

## Comparison matrix

- **A** — published historical outputs.
- **B** — official `v1.0.0` with fixed non-DC normalization.
- **C** — diagnostic reconstruction from a second isolated `v1.0.0` copy.
- **D** — unmodified partial historical candidate at `4bf12b3`.

| Comparison | Byte-identical CSV files |
|---|---:|
| A vs B | 1/11 |
| A vs C | 11/11 |
| A vs D | 11/11 |

All eleven files had identical dimensions and headers across the four sets.
C and D had the same rows in the same order as A and had zero absolute and
relative numerical differences. For A versus B, row order is reported only
where it can be isolated from content differences; otherwise it is
indeterminate rather than inferred from all-numeric rows.
The comparison report uses exact row sequences and duplicate-aware row
multisets. It reports row order only when the two multisets match; otherwise
the order field is indeterminate. Non-finite values are reported explicitly
and are excluded from finite-value magnitude statistics.

## Spectral-entropy definitions

Both implementations center the input, compute an unnormalized FFT2, apply
`fftshift`, form power `P=|F|^2`, explicitly zero the central DC coefficient and
normalize the remaining powers by their total. Exact zero powers do not enter
the Shannon sum.

For positive powers `p_j=P_j/sum(P)` and
`K_+=#{j:P_j>0}`, the audit-era definition is

```text
H_old = -sum(p_j log2(p_j)) / log2(K_+)    when K_+ > 1,
        0                                    otherwise.
```

For `N=W*H`, v1.0.0 uses

```text
H_new = -sum(p_j log2(p_j)) / log2(N-1)    when N-1 > 1 and power exists,
        0                                    otherwise.
```

Constant and zero-power fields return zero. The old denominator can change when
floating-point roundoff changes a coefficient between exact zero and a small
positive value. The fixed denominator removes that discontinuity for a fixed
shape, but it is not a claim of universal numerical invariance across every
backend or transform. The historical formula is preserved for reproduction;
it is not proposed as a correction to the current application.

## Numerical differences: A versus B

| CSV | Changed columns | Maximum absolute | Maximum relative | Ranking change |
|---|---|---:|---:|---|
| `aspect_summary.csv` | Hspec | 1.07032e-5 | 1.15814e-5 | no |
| `aspect_trials.csv` | Hspec | 5.35160e-4 | 5.87689e-4 | no |
| `density_summary.csv` | Hspec | 4.49719e-5 | 4.79098e-5 | no |
| `density_trials.csv` | Hspec | 7.93838e-4 | 8.48766e-4 | Hspec only |
| `null_controls.csv` | Hspec | 1.93099e-1 | 3.53879e-1 | no |
| `null_summary.csv` | Hspec mean/SD rows | 3.49854e-7 | 1.13759e-4 | no |
| `null_trials.csv` | Hspec | 1.00151e-4 | 1.63641e-4 | Hspec only |
| `placement_metrics.csv` | Hspec | 2.73361e-1 | 3.52782e-1 | Hspec only |
| `start_z_m30.csv` | none | 0 | 0 | no |
| `symmetry_metrics.csv` | Hspec | 8.51664e-1 | 8.51664e-1 | Hspec only |
| `synthetic_metrics.csv` | Hspec | 5.06561e-1 | 8.27109e-1 | Hspec only |

Peak ratio, axis ratio, low-frequency ratio, local/global entropy, edge density,
Beauty Score and Structural Score did not change. Beauty does not use spectral
entropy. The principal experimental interpretation concerning parity,
coprimality and embedding is therefore unchanged for the investigated cases.

## Execution evidence

The verified B and C runs used Python 3.14.10, NumPy 2.4.6, Linux and CPU/NumPy,
with seed `20260910`, 500 trials and 50 replicates. D used the same effective
environment and parameters. D completed in 2.05 seconds with a recorded maximum
RSS of 51,024 KiB. Available UTC timestamps for D are
2026-11-26T11:07:22Z through 2026-11-26T11:07:32Z.

The historical PNG was not regenerated because Matplotlib 3.11.1 was not
available and no dependency installation was authorized. The historical
Python/NumPy environment was not restored. CUDA was not available or validated.
The A/B/C/D manifests differ because they truthfully record different source
hashes and effective environments.

## Interpretation limits

Exact CSV reproduction demonstrates numerical equality for the exercised
protocol. It does not prove complete source identity, behavior outside the
tested inputs, GPU equivalence, GUI equivalence or a new property of prime
numbers. Five required historical source hashes remain unavailable.
