# Scalar FFT regression: C1

Before the fix, `test_scalar_fft_does_not_modify_arithmetic_field_or_cache`
failed in four subtests: Residues modulo N, Divisor count τ(n), Möbius μ(n),
and GCD with N. Every scalar value in the tested 3×2 slice was changed by
subtracting the slice mean. The volume used two layers and Start=1.

For Residues modulo N, N=5, slice XY at depth zero:

```text
Before FFT: [[1, 2, 3], [4, 0, 1]]
After FFT:  [[-0.8333333333, 0.1666666667, 1.1666666667],
             [2.1666666667, -1.8333333333, -0.8333333333]]
```

Original test outcome: `Ran 1 test; FAILED (failures=4)`.

The localized change in `atlas_engine.fft_spectrum` is:

```diff
- else xp.asarray(values, dtype=xp.float64)
+ else xp.array(values, dtype=xp.float64, copy=True)
```

A short comment explains ownership of the working buffer. The centering,
FFT, DC removal, power and metric definitions are unchanged.

After the fix the same test passes for all four modes. It checks both the
original projection and a fresh projection from the cache, and checks that
a repeated FFT returns the same display spectrum. The full audit suite's
result is in `test_results.txt`.
