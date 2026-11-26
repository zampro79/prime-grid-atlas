"""Optional GPU compute backend.

NumPy remains the required backend.  CuPy is imported lazily so the application
keeps working on machines without CUDA or without a compatible CuPy package.
"""

import numpy as np
import math

from app_config import get_config

_requested_mode = "Auto"
_cupy = None
_gpu_checked = False
_gpu_error = "GPU not checked"
_gpu_prime_sieve = None
_gpu_prime_sieve_limit = -1


def _load_cupy():
    global _cupy, _gpu_checked, _gpu_error
    if _gpu_checked:
        return _cupy

    _gpu_checked = True
    try:
        import cupy as cp

        device_count = int(cp.cuda.runtime.getDeviceCount())
        if device_count < 1:
            _gpu_error = "no CUDA device detected"
            return None
        # Exercise the same facilities used by metrics.py.  Creating a CUDA
        # context alone is not enough: some CuPy installations can allocate
        # memory but fail later when NVRTC needs CUDA headers to compile a
        # reduction or an elementwise kernel.
        probe = cp.arange(16, dtype=cp.float64).reshape(4, 4)
        cp.sqrt(probe + 1).sum().item()
        cp.log2(probe + 1).sum().item()
        cp.pad(probe, 1, mode="edge").sum().item()
        cp.fft.fft2(probe).real.sum().item()
        probe_mask = cp.ones(32, dtype=cp.bool_)
        probe_mask[4::2] = False
        probe_mask.sum().item()
        _cupy = cp
        _gpu_error = ""
    except Exception as exc:
        _cupy = None
        _gpu_error = str(exc)
    return _cupy


def configure_backend(mode):
    global _requested_mode
    normalized = str(mode).strip().title()
    _requested_mode = normalized if normalized in ("Auto", "Cpu", "Gpu") else "Auto"
    if _requested_mode != "Cpu":
        _load_cupy()
    return backend_summary()


def should_use_gpu(element_count):
    if _requested_mode == "Cpu":
        return False
    if _load_cupy() is None:
        return False
    if _requested_mode == "Gpu":
        return True
    return int(element_count) >= get_config().gpu_auto_min_elements


def gpu_module():
    return _load_cupy()


def release_gpu_caches():
    """Release CuPy's unused FFT plans and pooled blocks.

    Module scan visits many matrix shapes, so retaining every cuFFT plan can
    consume several GiB without increasing sustained GPU utilisation.  This
    function is deliberately called at scan boundaries, not for every row.
    """
    cp = _cupy
    if cp is None:
        return
    try:
        cp.fft.config.get_plan_cache().clear()
    except Exception:
        pass
    try:
        cp.get_default_memory_pool().free_all_blocks()
        cp.get_default_pinned_memory_pool().free_all_blocks()
    except Exception:
        pass


def disable_gpu(exc):
    """Disable CUDA for the current process after a runtime failure."""
    global _cupy, _gpu_checked, _gpu_error, _gpu_prime_sieve, _gpu_prime_sieve_limit
    _cupy = None
    _gpu_checked = True
    _gpu_error = str(exc)
    _gpu_prime_sieve = None
    _gpu_prime_sieve_limit = -1


def to_numpy(value):
    cp = _cupy
    if cp is not None and isinstance(value, cp.ndarray):
        return cp.asnumpy(value)
    return np.asarray(value)


def scalar(value):
    if hasattr(value, "item"):
        return value.item()
    return value


def coprime_mask(values, step):
    """Compute a GCD mask on CUDA when enabled, with transparent CPU retry."""
    array = np.asarray(values)
    if not should_use_gpu(array.size):
        return np.gcd(np.abs(array), int(step)) == 1
    cp = gpu_module()
    try:
        device_values = cp.asarray(array)
        return cp.asnumpy(cp.gcd(cp.abs(device_values), int(step)) == 1)
    except Exception as exc:
        disable_gpu(exc)
        return np.gcd(np.abs(array), int(step)) == 1


def _small_cpu_primes(limit):
    if limit < 2:
        return np.empty(0, dtype=np.int64)
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            sieve[prime * prime :: prime] = False
    return np.flatnonzero(sieve)


def prime_mask(values, cpu_fallback):
    """Return a prime mask, using a cached CUDA sieve when the backend allows it."""
    global _gpu_prime_sieve, _gpu_prime_sieve_limit
    array = np.asarray(values)
    if array.size == 0 or not should_use_gpu(array.size):
        return cpu_fallback(array)
    valid = array >= 2
    if not np.any(valid):
        return np.zeros(array.shape, dtype=bool)
    limit = int(array[valid].max())
    cp = gpu_module()
    try:
        if _gpu_prime_sieve is None or limit > _gpu_prime_sieve_limit:
            sieve = cp.ones(limit + 1, dtype=cp.bool_)
            if limit >= 0:
                sieve[0] = False
            if limit >= 1:
                sieve[1] = False
            if limit >= 4:
                sieve[4::2] = False
            for prime in _small_cpu_primes(math.isqrt(limit)):
                prime = int(prime)
                if prime >= 3:
                    sieve[prime * prime :: prime * 2] = False
            _gpu_prime_sieve = sieve
            _gpu_prime_sieve_limit = limit
        result = cp.zeros(array.shape, dtype=cp.bool_)
        device_values = cp.asarray(array[valid], dtype=cp.int64)
        result[cp.asarray(valid)] = _gpu_prime_sieve[device_values]
        return cp.asnumpy(result)
    except Exception as exc:
        disable_gpu(exc)
        return cpu_fallback(array)


def backend_summary():
    cp = None if _requested_mode == "Cpu" else _load_cupy()
    if _requested_mode == "Cpu":
        return "CPU / NumPy"
    if cp is None:
        label = "GPU requested" if _requested_mode == "Gpu" else "Auto"
        return f"{label}: CPU fallback — CUDA runtime incomplete"
    try:
        device_id = int(cp.cuda.Device().id)
        props = cp.cuda.runtime.getDeviceProperties(device_id)
        raw_name = props.get("name", b"CUDA GPU")
        name = (
            raw_name.decode(errors="replace")
            if isinstance(raw_name, bytes)
            else str(raw_name)
        )
    except Exception:
        name = "CUDA GPU"
    if _requested_mode == "Auto":
        threshold = get_config().gpu_auto_min_elements
        return f"Auto: {name} for arrays >= {threshold:,} cells"
    return f"GPU / CuPy: {name}"


def backend_error():
    """Return the complete CUDA diagnostic without crowding the main sidebar."""
    return _gpu_error


def backend_state():
    """Return machine-readable requested and currently available backend state."""
    cp = None if _requested_mode == "Cpu" else _load_cupy()
    return {
        "requested": {"Cpu": "CPU", "Gpu": "GPU"}.get(
            _requested_mode, _requested_mode
        ),
        "cuda_available": cp is not None,
        "runtime_policy": backend_summary(),
        "cuda_error": _gpu_error if cp is None and _requested_mode != "Cpu" else "",
    }
