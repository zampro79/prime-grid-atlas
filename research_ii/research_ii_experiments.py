#!/usr/bin/env python3
"""Independent Phase-II experiments for Prime Grid Atlas.

This file deliberately does not import the application.  It studies the same
linear embedding with small, independently implemented number-theory routines.
Outputs are deterministic CSV/JSON files in ``research_ii/data`` by default.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent


def sieve(limit: int) -> np.ndarray:
    a = np.ones(limit + 1, dtype=bool)
    if limit >= 0:
        a[0] = False
    if limit >= 1:
        a[1] = False
    for p in range(2, math.isqrt(limit) + 1):
        if a[p]:
            a[p * p :: p] = False
    return a


def factor(n: int) -> dict[int, int]:
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def mobius(n: int) -> int:
    fs = factor(n)
    return 0 if any(e > 1 for e in fs.values()) else (-1) ** len(fs)


def phi(n: int) -> int:
    v = n
    for p in factor(n):
        v -= v // p
    return v


def ramanujan_sum(m: int, k: int) -> int:
    """c_m(k) = mu(m/g) phi(m) / phi(m/g), g=gcd(m,k)."""
    q = m // math.gcd(m, k)
    return mobius(q) * phi(m) // phi(q)


def grid_units(m: int, xdim: int, start: int = 0) -> np.ndarray:
    assert m % xdim == 0
    vals = start + np.arange(m)
    return (np.gcd(vals, m) == 1).reshape(m // xdim, xdim)


def centered_power(a: np.ndarray) -> np.ndarray:
    z = np.asarray(a, float) - float(np.mean(a))
    p = np.abs(np.fft.fftshift(np.fft.fft2(z))) ** 2
    p[p.shape[0] // 2, p.shape[1] // 2] = 0.0
    return p


def stable_metrics(hits: np.ndarray) -> dict[str, float]:
    a = np.asarray(hits)
    alive = a > 0
    p = centered_power(alive)
    total = float(p.sum())
    cy, cx = np.array(p.shape) // 2
    axis = np.zeros(p.shape, bool)
    axis[cy, :] = True
    axis[:, cx] = True
    axis[cy, cx] = False
    q = p.ravel() / total if total else np.zeros(p.size)
    # Fixed denominator makes this invariant under exact spectral permutations.
    positive = q > 0
    hspec = -float(np.sum(q[positive] * np.log2(q[positive])))
    hspec /= math.log2(max(2, p.size - 1))

    def corr(dy: int, dx: int) -> float:
        left = alive[max(0, dy) : alive.shape[0] + min(0, dy),
                     max(0, dx) : alive.shape[1] + min(0, dx)]
        right = alive[max(0, -dy) : alive.shape[0] + min(0, -dy),
                      max(0, -dx) : alive.shape[1] + min(0, -dx)]
        if left.size == 0:
            return 0.0
        density = float(alive.mean())
        return float((left * right).mean() - density * density)

    return {
        "alive_density": float(alive.mean()),
        "mean_hits": float(a.mean()),
        "var_hits": float(a.var()),
        "fft_peak_ratio": float(p.max() / total) if total else 0.0,
        "fft_axis_ratio": float(p[axis].sum() / total) if total else 0.0,
        "fft_entropy_fixed": hspec,
        "autocov_x1": corr(0, 1),
        "autocov_y1": corr(1, 0),
        "pair_x2": corr(0, 2),
        "pair_y2": corr(2, 0),
    }


def weighted_bernoulli(rng: np.random.Generator, weights: np.ndarray,
                       target: int) -> np.ndarray:
    """Independent draws calibrated so the expected total is target."""
    weights = np.asarray(weights, float)
    if target <= 0 or not np.any(weights > 0):
        return np.zeros(weights.shape, bool)
    lo, hi = 0.0, max(1.0, target / weights[weights > 0].min())
    for _ in range(70):
        mid = (lo + hi) / 2
        if np.minimum(1.0, mid * weights).sum() < target:
            lo = mid
        else:
            hi = mid
    probs = np.minimum(1.0, hi * weights)
    return rng.random(weights.shape) < probs


def projected_hits(mask: np.ndarray, xdim: int, ydim: int, zdim: int) -> np.ndarray:
    return mask.reshape(zdim, ydim, xdim).sum(axis=0)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def spectral_theory(output: Path, seed: int, trials: int) -> None:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    cases = [
        (11, "prime"), (16, "prime_power"), (27, "prime_power"),
        (30, "primorial"), (60, "composite"), (210, "primorial"),
        (330, "30p"), (390, "30p"),
    ]
    for m, family in cases:
        units = np.flatnonzero(np.gcd(np.arange(m), m) == 1)
        l = len(units)
        ksample = max(1, round(0.55 * l))
        for kfreq in range(m):
            chars = np.exp(-2j * np.pi * kfreq * units / m)
            exact = chars.sum()
            predicted = ramanujan_sum(m, kfreq)
            samples = np.empty(trials, complex)
            for t in range(trials):
                chosen = rng.choice(l, ksample, replace=False)
                samples[t] = chars[chosen].sum()
            mean_theory = ksample * predicted / l
            variance_theory = (
                ksample * (l - ksample) / (l - 1)
                * (1.0 - (predicted / l) ** 2)
                if l > 1 else 0.0
            )
            power_theory = abs(mean_theory) ** 2 + variance_theory
            rows.append({
                "M": m, "family": family, "frequency": kfreq,
                "phi_M": l, "sample_K": ksample,
                "ramanujan": predicted,
                "direct_real": float(exact.real),
                "direct_imag": float(exact.imag),
                "sample_mean_real": float(samples.mean().real),
                "mean_theory_real": float(mean_theory),
                "sample_complex_variance": float(np.mean(abs(samples - samples.mean()) ** 2)),
                "complex_variance_theory": float(variance_theory),
                "sample_mean_power": float(np.mean(abs(samples) ** 2)),
                "mean_power_theory": float(power_theory),
            })
    write_csv(output / "spectral_ramanujan.csv", rows)


def factorization_anatomy(output: Path) -> None:
    rows: list[dict] = []
    for m in [30, 60, 210, 330, 390, 420]:
        for xdim in range(1, m + 1):
            if m % xdim:
                continue
            ydim = m // xdim
            a = grid_units(m, xdim)
            met = stable_metrics(a)
            # Horizontal modes are additive characters k=uY mod M.
            max_axis_error = 0.0
            for u in range(xdim):
                direct = np.sum(a * np.exp(-2j * np.pi * u * np.arange(xdim) / xdim))
                max_axis_error = max(max_axis_error, abs(abs(direct) - abs(ramanujan_sum(m, u * ydim))))
            rows.append({
                "M": m, "factorization": "*".join(
                    f"{p}^{e}" if e > 1 else str(p) for p, e in factor(m).items()),
                "X": xdim, "Y": ydim, "phi_M": phi(m),
                "aspect": xdim / ydim,
                "horizontal_ramanujan_max_abs_error": max_axis_error,
                **met,
            })
    write_csv(output / "factorization_anatomy.csv", rows)


def hierarchy(output: Path, seed: int, trials: int) -> None:
    rng = np.random.default_rng(seed + 1)
    configs = [
        (15, 20, 4, 1001), (20, 15, 4, 1001),
        (30, 30, 2, 1001), (11, 30, 4, 10007),
        (13, 30, 4, 50021),
    ]
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    rows: list[dict] = []
    summary: list[dict] = []
    metric_names = list(stable_metrics(np.zeros((2, 2), int)))
    for xdim, ydim, zdim, start in configs:
        m = xdim * ydim
        values = start + np.arange(m * zdim)
        prime_table = sieve(int(values[-1]))
        real_mask = prime_table[values]
        target = int(real_mask.sum())
        real_stats = stable_metrics(projected_hits(real_mask, xdim, ydim, zdim))
        models: dict[str, np.ndarray] = {
            "L1_uniform": np.ones(values.shape, float),
            "L2_coprime_M": (np.gcd(values, m) == 1).astype(float),
            "L3_coprime_log": (np.gcd(values, m) == 1) / np.log(np.maximum(3, values)),
        }
        # Increasing finite wheels reproduce progressively more of the local
        # factors that also occur in Hardy--Littlewood singular series.  They
        # remain finite-sieve proxies, not a simulation of that conjecture.
        for level, bound in [("L4_wheel_7", 7), ("L5_deep_sieve_19", 19)]:
            support = np.ones(values.shape, bool)
            for p in small_primes:
                if p > bound:
                    break
                support &= values % p != 0
            models[level] = support / np.log(np.maximum(3, values))

        for model, weights in models.items():
            samples = {name: [] for name in metric_names}
            for trial in range(trials):
                draw = weighted_bernoulli(rng, weights, target)
                met = stable_metrics(projected_hits(draw, xdim, ydim, zdim))
                rows.append({
                    "X": xdim, "Y": ydim, "Z": zdim, "Start": start,
                    "M": m, "model": model, "trial": trial, **met,
                })
                for name in metric_names:
                    samples[name].append(met[name])
            for name in metric_names:
                vals = np.asarray(samples[name])
                sd = float(vals.std(ddof=1))
                obs = real_stats[name]
                summary.append({
                    "X": xdim, "Y": ydim, "Z": zdim, "Start": start,
                    "M": m, "model": model, "metric": name,
                    "prime_observed": obs, "null_mean": float(vals.mean()),
                    "null_sd": sd, "z_score": (obs - vals.mean()) / sd if sd else 0.0,
                    "two_sided_empirical_fraction": float(
                        (np.abs(vals - vals.mean()) >= abs(obs - vals.mean())).mean()
                    ),
                    "trials": trials,
                })
        rows.append({
            "X": xdim, "Y": ydim, "Z": zdim, "Start": start, "M": m,
            "model": "L6_real_primes", "trial": -1, **real_stats,
        })
    write_csv(output / "hierarchy_trials.csv", rows)
    write_csv(output / "hierarchy_summary.csv", summary)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "data")
    p.add_argument("--trials", type=int, default=240)
    p.add_argument("--seed", type=int, default=20261126)
    args = p.parse_args()
    if args.trials < 20:
        p.error("--trials must be at least 20")
    args.output.mkdir(parents=True, exist_ok=True)
    spectral_theory(args.output, args.seed, args.trials)
    factorization_anatomy(args.output)
    hierarchy(args.output, args.seed, args.trials)
    manifest = {
        "seed": args.seed, "trials": args.trials,
        "numpy": np.__version__, "embedding": "n=Start+x+X*y+X*Y*z",
        "notes": [
            "Independent implementation; application modules are not imported.",
            "Empirical tail fractions are descriptive and uncorrected.",
            "L5 is a finite wheel through 19, not the full Hardy-Littlewood model.",
        ],
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
