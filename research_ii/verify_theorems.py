#!/usr/bin/env python3
"""Exact small-case checks for the Phase-II propositions."""
import math
import numpy as np

from research_ii_experiments import factor, phi, ramanujan_sum


def direct_ramanujan(m, k):
    return sum(
        np.exp(-2j * np.pi * k * n / m)
        for n in range(m) if math.gcd(n, m) == 1
    )


def pair_formula(m, h):
    result = 1
    for p, a in factor(m).items():
        result *= p ** (a - 1) * (p - 1 if h % p == 0 else p - 2)
    return result


for m in range(2, 121):
    units = np.array([math.gcd(n, m) == 1 for n in range(m)], dtype=int)
    assert units.sum() == phi(m)
    for k in range(m):
        assert abs(direct_ramanujan(m, k) - ramanujan_sum(m, k)) < 1e-9
    for h in range(m):
        direct = sum(units[n] * units[(n + h) % m] for n in range(m))
        assert direct == pair_formula(m, h)

# General forced-peak theorem: odd support in an even cyclic grid.
for n in range(4, 80, 2):
    support = np.arange(1, n, 2)
    for k_count in range(1, len(support) + 1):
        chosen = support[:k_count]
        field = np.zeros(n)
        field[chosen] = 1
        power = abs(np.fft.fft(field - field.mean())) ** 2
        power[0] = 0
        observed = power.max() / power.sum()
        expected = k_count / (n - k_count)
        assert abs(observed - expected) < 1e-10

print("PASS: Ramanujan, CRT pair-count, and forced-peak checks")
