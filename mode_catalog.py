"""Focused mode catalog for the Prime Grid Atlas v1.0.0 interface."""

PRIME_MODES = (
    "Primes",
    "Twin primes",
    "Sophie Germain primes",
    "Safe primes",
)

CONTROL_MODES = (
    "Coprimes with N",
    "Square-free numbers",
    "Semiprimes",
    "Prime powers",
)

DIAGNOSTIC_MODES = (
    "Multiples of k",
    "Residues modulo N",
    "Divisor count τ(n)",
    "Möbius μ(n)",
    "GCD with N",
)

MODE_GROUPS = {
    "Prime research": PRIME_MODES,
    "Scientific controls": CONTROL_MODES,
    "Modular diagnostics": DIAGNOSTIC_MODES,
}

ALL_MODES = PRIME_MODES + CONTROL_MODES + DIAGNOSTIC_MODES
