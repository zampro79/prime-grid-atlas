"""Headless numerical engine shared by the PySide6 interface and workers."""

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np

from app_config import get_config
from compute_backend import (
    disable_gpu,
    gpu_module,
    coprime_mask,
    prime_mask,
    should_use_gpu,
    to_numpy,
)
from grid_model import get_depth_limit_for_plane, get_plane_data, plane_dimensions
from metrics import (
    deterministic_seed_for_atlas,
    entropy_edge_mask,
    fft2_structure_metrics,
    gradient_magnitude_grid,
    local_entropy_grid,
    prime_grid_metrics,
    random_baseline_metrics_for_hits,
)
from number_theory import (
    divisor_count_int,
    euler_phi_ratio,
    factorization_label,
    is_prime_power,
    is_semiprime,
    is_square_free,
    mobius_int,
    omega_int,
    prime_mask_for_values,
    scalar_sequence_mask,
    scalar_sequence_values,
)
from memory_policy import (
    MemoryEstimate,
    compose_estimates,
    estimate_entropy,
    estimate_fft,
    estimate_overlay,
    estimate_projection,
    estimate_sieve,
    estimate_volume,
    require_memory,
)


GEOMETRY_METRIC_KEYS = (
    "local_entropy_mean",
    "edge_density",
    "global_entropy",
    "fft_peak_ratio",
    "fft_axis_ratio",
    "fft_lowfreq_ratio",
    "fft_spectral_entropy",
)

PLACEMENTS = (
    "Linear",
    "Spiral inward",
    "Spiral outward (Ulam)",
    "Boustrophedon",
    "Hilbert curve",
    "Morton Z-order",
    "Diagonal zigzag",
    "Corner expanding rings",
    "Concentric rings",
    "Radial spokes",
    "Prime modulus weave",
    "Seeded random",
    "Bit reversal",
    "3D helix",
)


_volume_cache_keys = []
_scalar_cache_keys = []


def _cache_key_is_warm(keys, config):
    return config in keys


def _touch_cache_key(keys, config):
    if config in keys:
        keys.remove(config)
    keys.append(config)
    del keys[:-2]


def _mode_uses_sieve(mode):
    return mode in (
        "Primes", "Twin primes", "Sophie Germain primes", "Safe primes"
    )


def _sieve_limit_for_config(config, total):
    end = int(config.start) + int(total) - 1
    if config.mode == "Twin primes":
        return max(0, end + 2)
    if config.mode == "Sophie Germain primes":
        return max(0, 2 * end + 1)
    return max(0, end)


def _volume_construction_phases(config, *, force_cold=False, placement=None):
    total = int(config.x) * int(config.y) * int(config.z)
    cold = force_cold or not _cache_key_is_warm(_volume_cache_keys, config)
    if not cold:
        return []
    phases = [estimate_volume(
        (config.z, config.y, config.x), placement=placement or config.placement,
        cache_entries_alive=len(_volume_cache_keys),
    )]
    if _mode_uses_sieve(config.mode):
        # The integer volume remains live while the selection mask is built.
        phases.append(estimate_sieve(
            _sieve_limit_for_config(config, total), values_cells=total,
        ))
    return phases


def _volume_operation_memory_estimate(config, *, public_copy=False,
                                      force_cold=False):
    total = int(config.x) * int(config.y) * int(config.z)
    phases = _volume_construction_phases(config, force_cold=force_cold)
    if public_copy:
        phases.append(MemoryEstimate(
            "public volume defensive copy", temporary=total * 9,
            components={"numbers and selection copies": total * 9},
        ))
    return compose_estimates("volume operation", phases)


def _scalar_operation_memory_estimate(config, *, public_copy=False,
                                      force_cold=False):
    phases = _volume_construction_phases(config, force_cold=force_cold)
    scalar_mode = config.mode in (
        "Residues modulo N", "Divisor count τ(n)", "Möbius μ(n)", "GCD with N"
    )
    total = int(config.x) * int(config.y) * int(config.z)
    scalar_cold = force_cold or not _cache_key_is_warm(_scalar_cache_keys, config)
    if scalar_mode and scalar_cold:
        phases.append(MemoryEstimate(
            "cached scalar field", persistent=total * 8,
            components={"float64 scalar field": total * 8},
        ))
    if scalar_mode and public_copy:
        phases.append(MemoryEstimate(
            "public scalar-field defensive copy", temporary=total * 8,
            components={"scalar field copy": total * 8},
        ))
    return compose_estimates("scalar-field operation", phases)


def _projection_operation_memory_estimate(config, plane, *, public_copy=True,
                                          force_cold=False):
    phases = _volume_construction_phases(config, force_cold=force_cold)
    scalar_mode = config.mode in (
        "Residues modulo N", "Divisor count τ(n)", "Möbius μ(n)", "GCD with N"
    )
    total = int(config.x) * int(config.y) * int(config.z)
    if scalar_mode and (force_cold or not _cache_key_is_warm(_scalar_cache_keys, config)):
        phases.append(MemoryEstimate("cached scalar field", persistent=total * 8))
    px, py = plane_dimensions(plane, config.x, config.y, config.z)
    phases.append(estimate_projection(
        (config.z, config.y, config.x), px * py,
        public_copy=public_copy, scalar_field=scalar_mode,
    ))
    return compose_estimates("projection operation", phases)


def _overlay_operation_memory_estimate(config, plane, *, trials=1,
                                       placement=None, force_cold=False):
    phases = _volume_construction_phases(
        config, force_cold=force_cold, placement=placement,
    )
    px, py = plane_dimensions(plane, config.x, config.y, config.z)
    scalar_mode = config.mode in (
        "Residues modulo N", "Divisor count τ(n)", "Möbius μ(n)", "GCD with N"
    )
    if scalar_mode and (force_cold or not _cache_key_is_warm(_scalar_cache_keys, config)):
        phases.append(MemoryEstimate(
            "cached scalar field", persistent=config.x * config.y * config.z * 8,
        ))
    projection_buffers = estimate_projection(
        (config.z, config.y, config.x), px * py, public_copy=False,
        scalar_field=scalar_mode,
    )
    # Hits and other projection products remain live throughout the metrics.
    phases.append(MemoryEstimate(
        "retained projection buffers", persistent=projection_buffers.additional_peak,
    ))
    phases.append(estimate_overlay(
        (config.z, config.y, config.x), px * py, trials=trials,
        placement=placement or config.placement,
        bins=get_config().entropy_bins, plane_shape=(py, px),
    ))
    return compose_estimates("overlay operation", phases)


def _render_operation_memory_estimate(config, plane, view, overlay):
    """Retain projection/analysis/display buffers across sequential metrics."""
    px, py = plane_dimensions(plane, config.x, config.y, config.z)
    cells = px * py
    shape = (py, px)
    projection = _projection_operation_memory_estimate(config, plane, public_copy=True)
    phases = [MemoryEstimate("retained projection", persistent=projection.additional_peak)]
    if view in ("Local entropy", "Entropy edges only"):
        analysis = estimate_entropy(shape, get_config().entropy_bins)
    elif view == "FFT 2D":
        analysis = compose_estimates("FFT display and metrics", (
            MemoryEstimate("retained FFT display",
                           persistent=estimate_fft(shape, display=True).additional_peak),
            estimate_fft(shape),
        ))
    else:
        analysis = MemoryEstimate("ordinary analysis", temporary=cells * 32)
    # One float64 analysis output remains while RGB/QImage and quick metrics
    # are built. Reserve it from the child's peak, without a second margin.
    retained = min(analysis.additional_peak, (cells * 8 * 6 + 4) // 5)
    phases.append(MemoryEstimate("analysis", persistent=retained,
                                 temporary=analysis.additional_peak - retained))
    phases.append(MemoryEstimate("RGB and QImage workspace", persistent=cells * 32))
    if config.mode == "Primes" and overlay and config.placement == "Linear":
        phases.append(estimate_overlay(
            (config.z, config.y, config.x), cells,
            bins=get_config().entropy_bins, plane_shape=shape,
        ))
    return compose_estimates("interactive rendering", phases)


@dataclass(frozen=True)
class GridConfig:
    x: int = 10
    y: int = 10
    z: int = 10
    mode: str = "Primes"
    param: int = 2
    placement: str = "Linear"
    start: int = 1
    placement_param: int = 7


def _spiral_plane_offsets(dim_x, dim_y):
    """Return XY offsets in a clockwise spiral from the outside inward."""
    offsets = np.empty((dim_y, dim_x), dtype=np.int64)
    top, bottom = 0, dim_y - 1
    left, right = 0, dim_x - 1
    value = 0

    while top <= bottom and left <= right:
        width = right - left + 1
        offsets[top, left : right + 1] = np.arange(value, value + width)
        value += width
        top += 1

        height = bottom - top + 1
        if height > 0:
            offsets[top : bottom + 1, right] = np.arange(value, value + height)
            value += height
        right -= 1

        if top <= bottom and left <= right:
            width = right - left + 1
            offsets[bottom, left : right + 1] = np.arange(
                value + width - 1, value - 1, -1
            )
            value += width
            bottom -= 1

        if top <= bottom and left <= right:
            height = bottom - top + 1
            offsets[top : bottom + 1, left] = np.arange(
                value + height - 1, value - 1, -1
            )
            value += height
            left += 1

    return offsets


def _offsets_from_coordinates(dim_x, dim_y, coordinates):
    offsets = np.empty((dim_y, dim_x), dtype=np.int64)
    for value, (x, y) in enumerate(coordinates):
        offsets[y, x] = value
    return offsets


def _ulam_coordinates(dim_x, dim_y):
    """Center-out clockwise square spiral, clipped to a rectangular grid."""
    x, y = (dim_x - 1) // 2, (dim_y - 1) // 2
    coordinates = []
    seen = set()

    def include(px, py):
        if 0 <= px < dim_x and 0 <= py < dim_y and (px, py) not in seen:
            coordinates.append((px, py))
            seen.add((px, py))

    include(x, y)
    step = 1
    while len(coordinates) < dim_x * dim_y:
        for dx, dy in ((1, 0), (0, -1), (-1, 0), (0, 1)):
            distance = step
            for _ in range(distance):
                x += dx
                y += dy
                include(x, y)
            if (dx, dy) in ((0, -1), (0, 1)):
                step += 1
    return coordinates


def _boustrophedon_coordinates(dim_x, dim_y):
    return [
        (x, y)
        for y in range(dim_y)
        for x in (range(dim_x) if y % 2 == 0 else range(dim_x - 1, -1, -1))
    ]


def _hilbert_xy(side, distance):
    x = y = 0
    scale = 1
    value = distance
    while scale < side:
        rx = 1 & (value // 2)
        ry = 1 & (value ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = scale - 1 - x, scale - 1 - y
            x, y = y, x
        x += scale * rx
        y += scale * ry
        value //= 4
        scale *= 2
    return x, y


def _hilbert_coordinates(dim_x, dim_y):
    side = 1 << max(dim_x, dim_y).bit_length()
    if side > max(dim_x, dim_y) and side // 2 >= max(dim_x, dim_y):
        side //= 2
    return [
        (x, y)
        for distance in range(side * side)
        for x, y in (_hilbert_xy(side, distance),)
        if x < dim_x and y < dim_y
    ]


def _morton_key(x, y):
    result = 0
    bit = 0
    while (1 << bit) <= max(x, y):
        result |= ((x >> bit) & 1) << (2 * bit)
        result |= ((y >> bit) & 1) << (2 * bit + 1)
        bit += 1
    return result


def _morton_coordinates(dim_x, dim_y):
    return sorted(
        ((x, y) for y in range(dim_y) for x in range(dim_x)),
        key=lambda point: _morton_key(*point),
    )


def _diagonal_coordinates(dim_x, dim_y):
    coordinates = []
    for diagonal in range(dim_x + dim_y - 1):
        points = [
            (x, diagonal - x)
            for x in range(dim_x)
            if 0 <= diagonal - x < dim_y
        ]
        coordinates.extend(reversed(points) if diagonal % 2 == 0 else points)
    return coordinates


def _concentric_coordinates(dim_x, dim_y):
    """Outside-in rings whose direction alternates at every depth."""
    inward = _spiral_plane_offsets(dim_x, dim_y)
    yy, xx = np.indices((dim_y, dim_x))
    rings = np.minimum.reduce((yy, xx, dim_y - 1 - yy, dim_x - 1 - xx))
    coordinates = []
    for ring in range(int(rings.max()) + 1):
        points = list(zip(*np.nonzero(rings == ring)))
        points.sort(key=lambda point: int(inward[point]))
        if ring % 2:
            points.reverse()
        coordinates.extend((x, y) for y, x in points)
    return coordinates


def _corner_expanding_coordinates(dim_x, dim_y):
    coordinates = [(0, 0)]
    for shell in range(1, max(dim_x, dim_y)):
        if shell < dim_x:
            coordinates.extend(
                (shell, y) for y in range(min(shell, dim_y - 1) + 1)
            )
        if shell < dim_y:
            start_x = min(shell - 1, dim_x - 1) if shell < dim_x else dim_x - 1
            coordinates.extend(
                (x, shell) for x in range(start_x, -1, -1)
            )
    return coordinates


def _radial_coordinates(dim_x, dim_y):
    cx, cy = (dim_x - 1) / 2.0, (dim_y - 1) / 2.0

    def key(point):
        x, y = point
        dx2, dy2 = 2 * x - (dim_x - 1), 2 * y - (dim_y - 1)
        divisor = math.gcd(abs(dx2), abs(dy2)) or 1
        ray = (dx2 // divisor, dy2 // divisor)
        angle = (math.atan2(ray[1], ray[0]) + 2 * math.pi) % (2 * math.pi)
        radius = (x - cx) ** 2 + (y - cy) ** 2
        return angle, radius

    return sorted(((x, y) for y in range(dim_y) for x in range(dim_x)), key=key)


def _bit_reversal_coordinates(dim_x, dim_y):
    total = dim_x * dim_y
    bits = max(1, (total - 1).bit_length())

    def reverse_bits(value):
        result = 0
        for _ in range(bits):
            result = (result << 1) | (value & 1)
            value >>= 1
        return result

    indices = sorted(range(total), key=reverse_bits)
    return [(index % dim_x, index // dim_x) for index in indices]


def _plane_offsets(config):
    dim_x, dim_y = int(config.x), int(config.y)
    placement = config.placement
    if placement == "Spiral inward":
        return _spiral_plane_offsets(dim_x, dim_y)
    coordinate_builders = {
        "Spiral outward (Ulam)": _ulam_coordinates,
        "Boustrophedon": _boustrophedon_coordinates,
        "Hilbert curve": _hilbert_coordinates,
        "Morton Z-order": _morton_coordinates,
        "Diagonal zigzag": _diagonal_coordinates,
        "Corner expanding rings": _corner_expanding_coordinates,
        "Concentric rings": _concentric_coordinates,
        "Radial spokes": _radial_coordinates,
        "Bit reversal": _bit_reversal_coordinates,
    }
    if placement == "Seeded random":
        seed = (
            dim_x * 73856093
            ^ dim_y * 19349663
            ^ int(config.placement_param) * 2654435761
        ) & 0xFFFFFFFF
        order = np.random.default_rng(seed).permutation(dim_x * dim_y)
        offsets = np.empty(dim_x * dim_y, dtype=np.int64)
        offsets[order] = np.arange(dim_x * dim_y)
        return offsets.reshape(dim_y, dim_x)
    if placement == "Prime modulus weave":
        values = np.arange(dim_x * dim_y, dtype=np.int64) + int(config.start)
        modulus = max(1, abs(int(config.placement_param)))
        order = np.lexsort((values, np.mod(values, modulus)))
        offsets = np.empty(values.size, dtype=np.int64)
        offsets[np.arange(values.size)] = order
        return offsets.reshape(dim_y, dim_x)
    builder = coordinate_builders.get(placement)
    if builder is None:
        raise ValueError(f"Unsupported placement for v1.0.0: {placement}")
    return _offsets_from_coordinates(dim_x, dim_y, builder(dim_x, dim_y))


def _validate_volume_request(config):
    total = int(config.x) * int(config.y) * int(config.z)
    if min(int(config.x), int(config.y), int(config.z)) < 1:
        raise ValueError("Grid dimensions must be positive")
    maximum = get_config().max_volume
    if total > maximum:
        raise ValueError(
            f"Volume {total:,} exceeds the {maximum:,}-cell safety limit"
        )
    start = int(config.start)
    end = start + total - 1
    int64 = np.iinfo(np.int64)
    if start < int64.min or end > int64.max:
        raise OverflowError(
            f"Integer interval [{start}, {end}] is outside the int64 range"
        )
    if config.mode == "Twin primes" and end > int64.max - 2:
        raise OverflowError("Twin-prime partner n+2 exceeds the int64 range")
    if config.mode == "Sophie Germain primes" and end > (int64.max - 1) // 2:
        raise OverflowError("Sophie Germain partner 2n+1 exceeds the int64 range")
    if config.mode == "Safe primes" and start <= int64.min:
        raise OverflowError("Safe-prime partner (n-1)//2 exceeds the int64 range")
    return total


def build_volume(config):
    """Return writable arrays isolated from the private cached volume."""
    _validate_volume_request(config)
    require_memory(_volume_operation_memory_estimate(config, public_copy=True))
    numbers, selected = _build_volume_internal(config)
    return numbers.copy(), selected.copy()


def _build_volume_internal(config):
    """Return private cached arrays for controlled read-only internal use."""
    _validate_volume_request(config)
    result = _build_volume_cached(config)
    _touch_cache_key(_volume_cache_keys, config)
    return result


@lru_cache(maxsize=2)
def _build_volume_cached(config):
    total = int(config.x) * int(config.y) * int(config.z)
    require_memory(estimate_volume(
        (config.z, config.y, config.x), placement=config.placement,
        cache_entries_alive=_build_volume_cached.cache_info().currsize,
    ))
    if config.placement == "Linear":
        numbers = (np.arange(total, dtype=np.int64) + int(config.start)).reshape(
            config.z, config.y, config.x
        )
    elif config.placement == "3D helix":
        plane_size = int(config.x) * int(config.y)
        plane = _spiral_plane_offsets(int(config.x), int(config.y))
        levels = []
        for z in range(int(config.z)):
            if config.x == config.y:
                oriented = np.rot90(plane, -(z % 4))
            else:
                oriented = (
                    plane,
                    np.fliplr(plane),
                    np.flipud(np.fliplr(plane)),
                    np.flipud(plane),
                )[z % 4]
            levels.append(oriented + z * plane_size + int(config.start))
        numbers = np.stack(levels)
    else:
        plane_size = int(config.x) * int(config.y)
        plane = _plane_offsets(config)
        levels = np.arange(int(config.z), dtype=np.int64)[:, None, None]
        numbers = plane[None, :, :] + levels * plane_size + int(config.start)

    if config.mode == "Primes":
        selected = prime_mask(numbers, prime_mask_for_values)
    elif config.mode == "Multiples of k":
        selected = numbers % max(1, abs(config.param)) == 0
    elif config.mode == "Semiprimes":
        selected = scalar_sequence_mask(numbers, is_semiprime)
    elif config.mode == "Prime powers":
        selected = scalar_sequence_mask(numbers, is_prime_power)
    elif config.mode == "Square-free numbers":
        selected = scalar_sequence_mask(numbers, is_square_free)
    elif config.mode == "Twin primes":
        selected = prime_mask(numbers, prime_mask_for_values) & prime_mask(
            numbers + 2, prime_mask_for_values
        )
    elif config.mode == "Sophie Germain primes":
        selected = prime_mask(numbers, prime_mask_for_values) & prime_mask(
            2 * numbers + 1, prime_mask_for_values
        )
    elif config.mode == "Safe primes":
        selected = (
            prime_mask(numbers, prime_mask_for_values)
            & (numbers > 2)
            & prime_mask((numbers - 1) // 2, prime_mask_for_values)
        )
    elif config.mode == "Coprimes with N":
        selected = np.gcd(np.abs(numbers), max(1, abs(int(config.param)))) == 1
    elif config.mode == "Residues modulo N":
        # Every integer belongs to one residue class; the meaningful output is
        # the scalar field produced by build_scalar_field().  Keeping every
        # cell selected preserves all classes in Classic and analytical views.
        selected = np.ones(numbers.shape, dtype=bool)
    elif config.mode == "Divisor count τ(n)":
        selected = numbers > 0
    elif config.mode == "Möbius μ(n)":
        selected = scalar_sequence_mask(numbers, lambda n: mobius_int(n) != 0)
    elif config.mode == "GCD with N":
        # GCD is a scalar diagnostic: every residue class must remain visible.
        selected = np.ones(numbers.shape, dtype=bool)
    else:
        raise ValueError(f"Unsupported numerical mode: {config.mode}")
    return numbers, selected


def build_scalar_field(config):
    """Return a writable scalar field isolated from the private cache."""
    _validate_volume_request(config)
    require_memory(_scalar_operation_memory_estimate(config, public_copy=True))
    field = _build_scalar_field_internal(config)
    return None if field is None else field.copy()


def _build_scalar_field_internal(config):
    """Track every successful cache access, including cached None results.

    Update after the LRU returns, before callers allocate public copies. A
    failed cache construction leaves both the real LRU and its registry intact.
    This mirrors sequential access only; it is not a concurrency guarantee.
    """
    field = _build_scalar_field_cached(config)
    _touch_cache_key(_scalar_cache_keys, config)
    return field


@lru_cache(maxsize=2)
def _build_scalar_field_cached(config):
    require_memory(MemoryEstimate(
        "scalar field construction",
        persistent=int(config.x) * int(config.y) * int(config.z) * 8,
        components={"cached float64 field": int(config.x) * int(config.y) * int(config.z) * 8},
    ))
    numbers, _selected = _build_volume_internal(config)
    if config.mode == "Residues modulo N":
        modulus = max(1, abs(int(config.param)))
        return np.mod(numbers, modulus).astype(np.float64)
    if config.mode == "Divisor count τ(n)":
        return scalar_sequence_values(numbers, divisor_count_int)
    if config.mode == "Möbius μ(n)":
        return scalar_sequence_values(numbers, mobius_int)
    if config.mode == "GCD with N":
        return np.gcd(np.abs(numbers), max(1, abs(int(config.param)))).astype(
            np.float64
        )
    return None


def clear_volume_cache():
    _build_volume_cached.cache_clear()
    _build_scalar_field_cached.cache_clear()
    _volume_cache_keys.clear()
    _scalar_cache_keys.clear()


def projection(config, plane="XY", depth=None, overlay=False):
    """Return writable projection arrays isolated from private cached buffers.

    Plane arrays may share memory with the corresponding 3D arrays in this
    result, but no returned array shares memory with another projection or an
    internal cached buffer.
    """
    return _projection_data(config, plane, depth, overlay, isolate=True)


def _projection_internal(config, plane="XY", depth=None, overlay=False):
    """Return a projection over cached buffers for controlled internal reads."""
    return _projection_data(config, plane, depth, overlay, isolate=False)


def _projection_data(config, plane, depth, overlay, isolate):
    require_memory(_projection_operation_memory_estimate(
        config, plane, public_copy=isolate,
    ))
    numbers, selected = _build_volume_internal(config)
    if isolate:
        numbers = numbers.copy()
        selected = selected.copy()
    depth_limit = get_depth_limit_for_plane(plane, config.x, config.y, config.z)
    depth = (
        depth_limit - 1 if depth is None else max(0, min(int(depth), depth_limit - 1))
    )
    data = get_plane_data(plane, depth, overlay, numbers, selected)
    scalar_field = _build_scalar_field_internal(config)
    if scalar_field is not None:
        if isolate:
            scalar_field = scalar_field.copy()
        field_data = get_plane_data(plane, depth, False, scalar_field, selected)
        data["mode_values"] = np.asarray(field_data["numbers"], dtype=float)
    px, py = plane_dimensions(plane, config.x, config.y, config.z)
    data.update(
        numbers_3d=numbers,
        selected_3d=selected,
        proj_x=px,
        proj_y=py,
        depth=depth,
        depth_limit=depth_limit,
    )
    return data


def analysis_values(data, view, overlay):
    numbers = np.asarray(data["numbers"]).ravel()
    hits = np.asarray(data["hits"]).ravel()
    scalar_field = data.get("mode_values")
    source = (
        np.asarray(scalar_field, dtype=float).ravel()
        if scalar_field is not None
        else (
            hits.astype(float) / max(1, data["visible_depth"])
            if overlay
            else numbers.astype(float)
        )
    )
    if view == "Gradient":
        values = gradient_magnitude_grid(source, data["proj_x"], data["proj_y"])
    elif view in ("Local entropy", "Entropy edges only"):
        values = local_entropy_grid(source, data["proj_x"], data["proj_y"])
    elif view == "Normalized heatmap":
        if overlay and scalar_field is None:
            values = source
        else:
            low, high = float(source.min()), float(source.max())
            values = (source - low) / max(1.0, high - low)
    elif view == "Heatmap":
        values = (
            source
            if scalar_field is not None
            else (hits.astype(float) if overlay else numbers.astype(float))
        )
    else:
        values = (
            source
            if scalar_field is not None
            else (
                hits.astype(float)
                if overlay
                else np.asarray(data["selected"]).ravel().astype(float)
            )
        )
    return np.asarray(values)


def _base_and_step(data, plane, config):
    numbers = data["numbers_3d"]
    if plane == "XY":
        return numbers[0].ravel(), config.x * config.y
    if plane == "XZ":
        return numbers[:, 0, :].ravel(), config.x
    return numbers[:, :, 0].ravel(), 1


def overlay_metrics(config, plane="XY", depth=None, random_trials=None):
    if config.placement != "Linear":
        raise ValueError("Protocol metrics require Linear placement")
    app_config = get_config()
    random_trials = (
        app_config.baseline_trials if random_trials is None else int(random_trials)
    )
    if random_trials < 1:
        raise ValueError("random_trials must be at least 1")
    require_memory(_overlay_operation_memory_estimate(
        config, plane, trials=random_trials,
    ))
    data = _projection_internal(config, plane, depth, True)
    hits = np.asarray(data["hits"]).ravel()
    base, step = _base_and_step(data, plane, config)
    metrics = prime_grid_metrics(hits, base, data["proj_x"], data["proj_y"], step)
    seed = deterministic_seed_for_atlas(
        config.x, config.y, config.z, plane, config.start, config.placement
    )
    if app_config.baseline_seed >= 0:
        seed = app_config.baseline_seed
    random = random_baseline_metrics_for_hits(
        hits,
        base,
        data["proj_x"],
        data["proj_y"],
        step,
        trials=random_trials,
        seed=seed,
    )
    coprime_hits = coprime_mask(base, step).astype(np.int32)
    coprime = prime_grid_metrics(
        coprime_hits, base, data["proj_x"], data["proj_y"], step
    )
    for key in GEOMETRY_METRIC_KEYS:
        metrics[f"random_{key}"] = float(random.get(key, 0.0))
        metrics[f"delta_{key}"] = float(metrics[key] - random.get(key, 0.0))
        metrics[f"coprime_mask_{key}"] = float(coprime.get(key, 0.0))
        metrics[f"delta_coprime_{key}"] = float(metrics[key] - coprime.get(key, 0.0))
    metrics["random_beauty_score"] = float(random.get("beauty_score", 0.0))
    metrics["structural_score"] = (
        metrics["beauty_score"] - metrics["random_beauty_score"]
    )
    deltas = np.array([metrics[f"delta_coprime_{k}"] for k in GEOMETRY_METRIC_KEYS])
    metrics["coprime_residual_l1"] = float(np.abs(deltas).sum())
    metrics["coprime_residual_l2"] = float(np.sqrt(np.square(deltas).sum()))
    metrics["coprime_mask_alive_density"] = float(coprime.get("alive_density", 0.0))
    metrics["delta_coprime_alive_density"] = float(
        metrics.get("alive_density", 0.0) - metrics["coprime_mask_alive_density"]
    )
    metrics.update(
        M=config.x * config.y,
        phi_ratio=euler_phi_ratio(config.x * config.y),
        omega=omega_int(config.x * config.y),
        tau=divisor_count_int(config.x * config.y),
        factorization=factorization_label(config.x * config.y),
        random_trials=random_trials,
    )
    return metrics


def current_overlay_metrics(config, data, plane):
    """Fast metrics for the status bar, without randomized baseline trials."""
    base, step = _base_and_step(data, plane, config)
    return prime_grid_metrics(
        np.asarray(data["hits"]).ravel(), base, data["proj_x"], data["proj_y"], step
    )


def placement_geometry_metrics(config, plane="XY", depth=None, overlay=True):
    """Placement-neutral metrics for comparing geometric embeddings."""
    require_memory(_overlay_operation_memory_estimate(
        config, plane, placement=config.placement,
    ))
    data = _projection_internal(config, plane, depth, overlay)
    values = np.asarray(
        data["hits"] if overlay else data["selected"], dtype=np.float64
    ).ravel()
    alive = values > 0
    entropy_values = local_entropy_grid(values, data["proj_x"], data["proj_y"])
    edges = entropy_edge_mask(entropy_values)
    _, counts = np.unique(values, return_counts=True)
    probabilities = counts.astype(np.float64) / max(1, counts.sum())
    with np.errstate(divide="ignore", invalid="ignore"):
        global_entropy = float(
            np.sum(
                np.where(
                    probabilities > 0,
                    -probabilities * np.log2(probabilities),
                    0.0,
                )
            )
        )
    fft = fft2_structure_metrics(
        values, data["proj_x"], data["proj_y"], binary=True
    )
    return {
        "alive_density": float(alive.mean()) if alive.size else 0.0,
        "local_entropy_mean": float(entropy_values.mean())
        if entropy_values.size
        else 0.0,
        "edge_density": float(edges.mean()) if edges.size else 0.0,
        "global_entropy": global_entropy,
        **{key: float(value) for key, value in fft.items()},
    }


def fft_spectrum(data, overlay):
    scalar_field = data.get("mode_values")
    values = np.asarray(
        scalar_field
        if scalar_field is not None
        else (data["hits"] if overlay else data["selected"]),
        dtype=float,
    )
    binary = scalar_field is None
    require_memory(compose_estimates(
        "FFT display and metrics",
        (
            MemoryEstimate(
                "retained FFT display", persistent=estimate_fft(
                    values.shape, display=True
                ).additional_peak,
            ),
            estimate_fft(values.shape),
        ),
    ))
    use_gpu = should_use_gpu(values.size)
    xp = gpu_module() if use_gpu else np
    try:
        # Preserve the v160 definition: FFT of presence/absence, not of the
        # accumulated hit count. This keeps slice and overlay spectra comparable.
        work = (
            (xp.asarray(values) > 0).astype(xp.float64)
            if binary
            # Scalar slices may share storage with the cached arithmetic field.
            # Center a private buffer so viewing FFT cannot change that field.
            else xp.array(values, dtype=xp.float64, copy=True)
        )
        work -= work.mean()
        power = xp.abs(xp.fft.fftshift(xp.fft.fft2(work))) ** 2
        power[power.shape[0] // 2, power.shape[1] // 2] = 0.0
        power = to_numpy(power) if use_gpu else power
    except Exception as exc:
        if not use_gpu:
            raise
        disable_gpu(exc)
        work = (values > 0).astype(np.float64) if binary else values.astype(np.float64)
        work -= work.mean()
        power = np.abs(np.fft.fftshift(np.fft.fft2(work))) ** 2
        power[power.shape[0] // 2, power.shape[1] // 2] = 0.0
    return np.log1p(power), fft2_structure_metrics(
        values.ravel(), data["proj_x"], data["proj_y"], binary=binary
    )
