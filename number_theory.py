import math
from functools import lru_cache

import numpy as np

from memory_policy import MemoryEstimate, estimate_sieve, require_memory


_prime_sieve_limit = -1
_prime_sieve_values = None


@lru_cache(maxsize=1_000_000)
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if n % i == 0:
            return False
    return True


def prime_sieve_upto(limit):
    """Return a writable sieve copy isolated from the private cached buffer."""
    normalized = int(limit)
    require_memory(estimate_sieve(
        max(0, normalized), public_copy=True, old_limit=_prime_sieve_limit
    ))
    return _prime_sieve_upto_cached(limit).copy()


def _prime_sieve_upto_cached(limit):
    """Return the private sieve buffer or a view for internal read-only use."""
    global _prime_sieve_limit, _prime_sieve_values

    limit = int(limit)
    if _prime_sieve_values is not None and limit <= _prime_sieve_limit:
        return _prime_sieve_values[: limit + 1]

    require_memory(estimate_sieve(max(0, limit), old_limit=_prime_sieve_limit))

    if limit < 2:
        sieve = np.zeros(max(0, limit) + 1, dtype=bool)
    else:
        sieve = np.ones(limit + 1, dtype=bool)
        sieve[:2] = False
        sieve[4::2] = False
        root = math.isqrt(limit)
        for p in range(3, root + 1, 2):
            if sieve[p]:
                sieve[p * p :: 2 * p] = False

    _prime_sieve_limit = limit
    _prime_sieve_values = sieve
    return _prime_sieve_values


def prime_mask_for_values(values):
    arr = np.asarray(values)
    require_memory(MemoryEstimate(
        "prime mask input and result",
        temporary=arr.size,
        components={"result mask": arr.size},
    ))
    mask = np.zeros(arr.shape, dtype=bool)
    if arr.size == 0:
        return mask

    valid = arr >= 2
    if not np.any(valid):
        return mask

    valid_values = arr[valid].astype(np.int64, copy=False)
    require_memory(estimate_sieve(
        int(valid_values.max()), values_cells=arr.size,
        old_limit=_prime_sieve_limit,
    ))
    sieve = _prime_sieve_upto_cached(int(valid_values.max()))
    mask[valid] = sieve[valid_values]
    return mask


def euler_phi_ratio(n):
    n = int(max(1, n))
    result = n
    d = 2
    value = n
    while d * d <= value:
        if value % d == 0:
            while value % d == 0:
                value //= d
            result -= result // d
        d += 1 if d == 2 else 2
    if value > 1:
        result -= result // value
    return result / n if n else 0.0


@lru_cache(maxsize=1_000_000)
def factorize_int(n):
    n = int(abs(n))
    factors = []
    if n < 2:
        return tuple(factors)
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    if count:
        factors.append((2, count))
    d = 3
    while d * d <= n:
        count = 0
        while n % d == 0:
            n //= d
            count += 1
        if count:
            factors.append((d, count))
        d += 2
    if n > 1:
        factors.append((n, 1))
    return tuple(factors)


def factorization_label(n):
    factors = factorize_int(n)
    if not factors:
        return str(n)
    parts = []
    for prime, exponent in factors:
        if exponent == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exponent}")
    return " * ".join(parts)


def omega_int(n):
    return len(factorize_int(n))


def divisor_count_int(n):
    if int(n) <= 0:
        return 0
    total = 1
    for _prime, exponent in factorize_int(n):
        total *= exponent + 1
    return total


def mobius_int(n):
    n = int(n)
    if n == 1:
        return 1
    if n <= 0:
        return 0
    factors = factorize_int(n)
    if any(exponent > 1 for _prime, exponent in factors):
        return 0
    return -1 if len(factors) % 2 else 1


def is_semiprime(n):
    return int(n) >= 4 and sum(exponent for _prime, exponent in factorize_int(n)) == 2


def is_prime_power(n):
    return int(n) >= 2 and len(factorize_int(n)) == 1


def is_square_free(n):
    return int(n) >= 1 and all(exponent == 1 for _prime, exponent in factorize_int(n))


def scalar_sequence_mask(values, predicate):
    array = np.asarray(values)
    return np.fromiter(
        (predicate(int(value)) for value in array.ravel()), bool, array.size
    ).reshape(array.shape)


def scalar_sequence_values(values, function):
    array = np.asarray(values)
    return np.fromiter(
        (function(int(value)) for value in array.ravel()), np.float64, array.size
    ).reshape(array.shape)
