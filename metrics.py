import math

import numpy as np

from app_config import get_config
from compute_backend import disable_gpu, gpu_module, scalar, should_use_gpu, to_numpy
from memory_policy import estimate_entropy, estimate_fft, require_memory

RANDOM_BASELINE_TRIALS = 12


def gradient_magnitude_grid(values, dim_x, dim_y):
    if dim_x <= 0 or dim_y <= 0:
        return []

    use_gpu = should_use_gpu(dim_x * dim_y)
    xp = gpu_module() if use_gpu else np
    try:
        return _gradient_magnitude_grid(values, dim_x, dim_y, xp, use_gpu)
    except Exception as exc:
        if not use_gpu:
            raise
        disable_gpu(exc)
        return _gradient_magnitude_grid(values, dim_x, dim_y, np, False)


def _gradient_magnitude_grid(values, dim_x, dim_y, xp, use_gpu):
    arr = xp.asarray(values, dtype=xp.float64).reshape(dim_y, dim_x)
    dx = xp.empty_like(arr)
    dy = xp.empty_like(arr)

    if dim_x == 1:
        dx[:, :] = 0.0
    else:
        dx[:, 1:-1] = (arr[:, 2:] - arr[:, :-2]) / 2.0
        dx[:, 0] = arr[:, 1] - arr[:, 0]
        dx[:, -1] = arr[:, -1] - arr[:, -2]

    if dim_y == 1:
        dy[:, :] = 0.0
    else:
        dy[1:-1, :] = (arr[2:, :] - arr[:-2, :]) / 2.0
        dy[0, :] = arr[1, :] - arr[0, :]
        dy[-1, :] = arr[-1, :] - arr[-2, :]

    gradients = xp.sqrt(dx * dx + dy * dy)
    return to_numpy(gradients).ravel() if use_gpu else gradients.ravel()


def local_entropy_grid(values, dim_x, dim_y, bins=None):
    if dim_x <= 0 or dim_y <= 0:
        return []

    bins = get_config().entropy_bins if bins is None else int(bins)
    require_memory(estimate_entropy((int(dim_y), int(dim_x)), bins))
    use_gpu = should_use_gpu(dim_x * dim_y)
    xp = gpu_module() if use_gpu else np
    try:
        return _local_entropy_grid(values, dim_x, dim_y, bins, xp, use_gpu)
    except Exception as exc:
        if not use_gpu:
            raise
        disable_gpu(exc)
        return _local_entropy_grid(values, dim_x, dim_y, bins, np, False)


def _local_entropy_grid(values, dim_x, dim_y, bins, xp, use_gpu):
    arr = xp.asarray(values, dtype=xp.float64).reshape(dim_y, dim_x)
    if arr.size == 0:
        return np.zeros(dim_x * dim_y, dtype=np.float64)

    value_min = float(scalar(arr.min()))
    value_max = float(scalar(arr.max()))
    span = value_max - value_min

    if span <= 0:
        quantized = xp.zeros((dim_y, dim_x), dtype=xp.int32)
    else:
        ratios = (arr - value_min) / span
        quantized = xp.floor(ratios * bins).astype(xp.int32)
        quantized = xp.clip(quantized, 0, bins - 1)

    padded = xp.pad(quantized, 1, mode="edge")
    counts = xp.zeros((bins, dim_y, dim_x), dtype=xp.int32)

    for by in range(3):
        for bx in range(3):
            window = padded[by : by + dim_y, bx : bx + dim_x]
            for b in range(bins):
                counts[b] += window == b

    probs = counts.astype(xp.float64) / 9.0
    with xp.errstate(divide="ignore", invalid="ignore"):
        entropy_terms = xp.where(probs > 0, -probs * xp.log2(probs), 0.0)

    entropies = entropy_terms.sum(axis=0)
    return to_numpy(entropies).ravel() if use_gpu else entropies.ravel()


def entropy_edge_mask(entropy_values, threshold_ratio=None):
    if len(entropy_values) == 0:
        return np.array([], dtype=bool)

    threshold_ratio = (
        get_config().edge_threshold
        if threshold_ratio is None
        else float(threshold_ratio)
    )
    arr = np.asarray(entropy_values, dtype=np.float64)
    e_min = float(arr.min())
    e_max = float(arr.max())
    if e_max <= e_min:
        return np.zeros(arr.shape, dtype=bool)

    threshold = e_min + (e_max - e_min) * threshold_ratio
    return arr >= threshold


def fft2_structure_metrics(flat_hits, dim_x, dim_y, binary=True):
    """2D spectral metrics for the hit/alive matrix.

    Subtract the mean to remove the DC component. These metrics are intended
    for relative comparisons across moduli and against random baselines,
    not as theoretical invariants.
    """
    default = {
        "fft_peak_ratio": 0.0,
        "fft_axis_ratio": 0.0,
        "fft_lowfreq_ratio": 0.0,
        "fft_spectral_entropy": 0.0,
    }
    if dim_x <= 0 or dim_y <= 0:
        return default

    require_memory(estimate_fft((int(dim_y), int(dim_x))))

    use_gpu = should_use_gpu(int(dim_x) * int(dim_y))
    xp = gpu_module() if use_gpu else np
    try:
        return _fft2_structure_metrics(flat_hits, dim_x, dim_y, xp, binary)
    except Exception as exc:
        if not use_gpu:
            raise
        disable_gpu(exc)
        return _fft2_structure_metrics(flat_hits, dim_x, dim_y, np, binary)


def _fft2_structure_metrics(flat_hits, dim_x, dim_y, xp, binary=True):
    default = {
        "fft_peak_ratio": 0.0,
        "fft_axis_ratio": 0.0,
        "fft_lowfreq_ratio": 0.0,
        "fft_spectral_entropy": 0.0,
    }
    values = xp.asarray(flat_hits, dtype=xp.float64).ravel()
    expected = int(dim_x) * int(dim_y)
    if values.size < expected:
        return default

    arr = values[:expected].reshape(int(dim_y), int(dim_x))
    # Selection masks use presence/absence; arithmetic scalar fields retain
    # their values so τ(n), μ(n) and gcd(n,N) have meaningful spectra.
    arr = (arr > 0).astype(xp.float64) if binary else arr.astype(xp.float64)
    arr -= float(scalar(arr.mean()))
    if not bool(scalar(xp.any(arr))):
        return default

    spectrum = xp.fft.fftshift(xp.fft.fft2(arr))
    power = xp.abs(spectrum) ** 2
    cy = dim_y // 2
    cx = dim_x // 2
    power[cy, cx] = 0.0
    total_power = float(scalar(power.sum()))
    if total_power <= 0:
        return default

    probs = power.ravel() / total_power
    probs = probs[probs > 0]
    # A fixed support size makes the normalization invariant under exact
    # spectral permutations.  Counting merely-positive roundoff bins made a
    # reflected field change entropy despite identical mathematical power.
    non_dc_bins = expected - 1
    if probs.size > 0 and non_dc_bins > 1:
        spectral_entropy = float(
            scalar(-xp.sum(probs * xp.log2(probs))) / math.log2(non_dc_bins)
        )
    else:
        spectral_entropy = 0.0

    peak_ratio = float(scalar(power.max()) / total_power)

    # Power on the spectral axes: horizontal/vertical bands and residual harmonics.
    axis_mask = xp.zeros_like(power, dtype=bool)
    axis_mask[cy, :] = True
    axis_mask[:, cx] = True
    axis_mask[cy, cx] = False
    axis_ratio = float(scalar(power[axis_mask].sum()) / total_power)

    yy, xx = xp.indices(power.shape)
    radius = xp.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_radius = float(scalar(radius.max())) if radius.size else 1.0
    low_radius = get_config().fft_low_radius
    low_mask = (radius > 0) & (radius <= max(1.0, low_radius * max_radius))
    lowfreq_ratio = (
        float(scalar(power[low_mask].sum()) / total_power)
        if bool(scalar(xp.any(low_mask)))
        else 0.0
    )

    return {
        "fft_peak_ratio": peak_ratio,
        "fft_axis_ratio": axis_ratio,
        "fft_lowfreq_ratio": lowfreq_ratio,
        "fft_spectral_entropy": spectral_entropy,
    }


def prime_grid_metrics(
    flat_hits,
    flat_base_numbers,
    dim_x,
    dim_y,
    step,
    precomputed_coprime_mask=None,
):
    default_metrics = {
        "coprime_alive_ratio": 0.0,
        "noncoprime_alive_ratio": 0.0,
        "local_entropy_mean": 0.0,
        "edge_density": 0.0,
        "global_entropy": 0.0,
        "alive_density": 0.0,
        "coprime_count": 0,
        "noncoprime_count": 0,
        "coprime_alive_count": 0,
        "noncoprime_alive_count": 0,
        "beauty_score": 0.0,
        "fft_peak_ratio": 0.0,
        "fft_axis_ratio": 0.0,
        "fft_lowfreq_ratio": 0.0,
        "fft_spectral_entropy": 0.0,
        "step": int(max(0, step)),
    }

    if dim_x <= 0 or dim_y <= 0 or step <= 0:
        return default_metrics

    hits = np.asarray(flat_hits, dtype=np.int32).ravel()
    base_numbers = np.asarray(flat_base_numbers, dtype=np.int64).ravel()
    total_cells = min(hits.size, base_numbers.size)
    if total_cells == 0:
        return default_metrics

    hits = hits[:total_cells]
    base_numbers = base_numbers[:total_cells]
    alive_mask = hits > 0

    if precomputed_coprime_mask is None:
        coprime_mask = np.gcd(np.abs(base_numbers), int(step)) == 1
    else:
        coprime_mask = np.asarray(precomputed_coprime_mask, dtype=bool).ravel()
        if coprime_mask.size < total_cells:
            raise ValueError("precomputed coprime mask is smaller than the grid")
        coprime_mask = coprime_mask[:total_cells]
    noncoprime_mask = ~coprime_mask

    coprime_count = int(coprime_mask.sum())
    noncoprime_count = int(noncoprime_mask.sum())
    coprime_alive_count = int(np.logical_and(coprime_mask, alive_mask).sum())
    noncoprime_alive_count = int(np.logical_and(noncoprime_mask, alive_mask).sum())

    coprime_alive_ratio = coprime_alive_count / coprime_count if coprime_count else 0.0
    noncoprime_alive_ratio = (
        noncoprime_alive_count / noncoprime_count if noncoprime_count else 0.0
    )
    alive_density = float(alive_mask.mean()) if total_cells else 0.0

    entropy_values = local_entropy_grid(hits.astype(np.float64), dim_x, dim_y)
    local_entropy_mean = float(np.mean(entropy_values)) if len(entropy_values) else 0.0
    edge_mask = entropy_edge_mask(entropy_values)
    edge_density = float(np.mean(edge_mask)) if len(edge_mask) else 0.0

    _, counts = np.unique(hits, return_counts=True)
    probs = counts.astype(np.float64) / counts.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        global_entropy = float(
            np.sum(np.where(probs > 0, -probs * np.log2(probs), 0.0))
        )

    contrast = max(0.0, coprime_alive_ratio - noncoprime_alive_ratio)
    config = get_config()
    richness = (
        config.beauty_entropy_weight * local_entropy_mean
        + config.beauty_edge_weight * edge_density
    )
    target_density = config.beauty_target_density
    readability = math.exp(
        -config.beauty_density_decay * ((alive_density - target_density) ** 2)
    )
    beauty_score = contrast * (1.0 + richness) * readability
    fft_metrics = fft2_structure_metrics(hits, dim_x, dim_y)

    return {
        "coprime_alive_ratio": coprime_alive_ratio,
        "noncoprime_alive_ratio": noncoprime_alive_ratio,
        "local_entropy_mean": local_entropy_mean,
        "edge_density": edge_density,
        "global_entropy": global_entropy,
        "alive_density": alive_density,
        "coprime_count": coprime_count,
        "noncoprime_count": noncoprime_count,
        "coprime_alive_count": coprime_alive_count,
        "noncoprime_alive_count": noncoprime_alive_count,
        "beauty_score": beauty_score,
        "fft_peak_ratio": float(fft_metrics["fft_peak_ratio"]),
        "fft_axis_ratio": float(fft_metrics["fft_axis_ratio"]),
        "fft_lowfreq_ratio": float(fft_metrics["fft_lowfreq_ratio"]),
        "fft_spectral_entropy": float(fft_metrics["fft_spectral_entropy"]),
        "step": int(step),
    }


def deterministic_seed_for_atlas(
    dim_x, dim_y, dim_z, plane, start_value, placement_mode
):
    plane_code = {"XY": 11, "XZ": 17, "YZ": 23}.get(plane, 31)
    placement_code = {
        "Lineare": 101,
        "Linear": 101,
        "Spiral inward": 307,
        "Spiral outward (Ulam)": 311,
        "Boustrophedon": 313,
        "Hilbert curve": 317,
        "Morton Z-order": 331,
        "Diagonal zigzag": 337,
        "Corner expanding rings": 347,
        "Concentric rings": 349,
        "Radial spokes": 353,
        "Prime modulus weave": 359,
        "Seeded random": 367,
        "Bit reversal": 373,
        "3D helix": 379,
    }.get(placement_mode, 401)
    seed = (
        int(dim_x) * 73856093
        ^ int(dim_y) * 19349663
        ^ int(dim_z) * 83492791
        ^ int(start_value) * 2654435761
        ^ plane_code * 1000003
        ^ placement_code
    )
    return seed & 0xFFFFFFFF


def random_baseline_metrics_for_hits(
    flat_hits,
    flat_base_numbers,
    dim_x,
    dim_y,
    step,
    trials=RANDOM_BASELINE_TRIALS,
    seed=0,
):
    """Random baseline: preserve the alive-cell count and randomize positions.

    Alive cells receive hit counts sampled from the observed positive values,
    making density and the count distribution comparable to the observed
    prime projection.
    """
    trial_count = int(trials)
    if trial_count < 1:
        raise ValueError("trials must be at least 1")
    hits = np.asarray(flat_hits, dtype=np.int32).ravel()
    base_numbers = np.asarray(flat_base_numbers, dtype=np.int64).ravel()
    total_cells = min(hits.size, base_numbers.size)
    if total_cells <= 0:
        return prime_grid_metrics([], [], dim_x, dim_y, step)

    hits = hits[:total_cells]
    base_numbers = base_numbers[:total_cells]
    alive_indices = np.flatnonzero(hits > 0)
    alive_count = int(alive_indices.size)
    if alive_count <= 0:
        return prime_grid_metrics(
            np.zeros(total_cells, dtype=np.int32), base_numbers, dim_x, dim_y, step
        )

    positive_values = hits[alive_indices]
    # The base numbers and step do not change between random trials.  Reusing
    # this mask avoids repeating the same full-grid gcd calculation N times.
    fixed_coprime_mask = np.gcd(np.abs(base_numbers), int(step)) == 1
    rng = np.random.default_rng(int(seed) & 0xFFFFFFFF)
    accum = None
    metric_keys = None
    for _ in range(trial_count):
        random_hits = np.zeros(total_cells, dtype=np.int32)
        positions = rng.choice(total_cells, size=alive_count, replace=False)
        sampled_values = rng.choice(positive_values, size=alive_count, replace=True)
        random_hits[positions] = sampled_values
        metrics = prime_grid_metrics(
            random_hits,
            base_numbers,
            dim_x,
            dim_y,
            step,
            precomputed_coprime_mask=fixed_coprime_mask,
        )
        if metric_keys is None:
            metric_keys = [
                key
                for key, value in metrics.items()
                if isinstance(value, (int, float, np.integer, np.floating))
            ]
            accum = {key: 0.0 for key in metric_keys}
        for key in metric_keys:
            accum[key] += float(metrics[key])

    averaged = {key: accum[key] / trial_count for key in metric_keys}
    averaged["trials"] = trial_count
    averaged["alive_count"] = alive_count
    return averaged
