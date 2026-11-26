"""Conservative pre-allocation memory estimates for Prime Grid Atlas.

The policy limits *additional peak memory for one operation*.  Existing RSS is
reported for context but is never compared with a budget derived from memory
that is already available.  Estimates are preventive engineering bounds, not
proof that an admitted operation cannot encounter ``MemoryError``.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
try:
    import resource
except ImportError:  # Optional on platforms without POSIX resource limits.
    resource = None
from typing import Mapping


MIB = 1024 * 1024
SAFETY_NUMERATOR = 6
SAFETY_DENOMINATOR = 5


def _integer(value, name, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


def _cells(shape):
    total = 1
    dimensions = tuple(shape)
    if not dimensions:
        raise ValueError("shape must contain at least one dimension")
    for index, dimension in enumerate(dimensions):
        total *= _integer(dimension, f"shape[{index}]", 1)
    return total


def _margin(byte_count):
    value = _integer(byte_count, "byte_count")
    return (value * SAFETY_NUMERATOR + SAFETY_DENOMINATOR - 1) // SAFETY_DENOMINATOR


@dataclass(frozen=True)
class MemoryEstimate:
    operation: str
    already_allocated: int = 0
    persistent: int = 0
    temporary: int = 0
    transfers: int = 0
    components: Mapping[str, int] = field(default_factory=dict)
    confidence: str = "conservative-model"

    def __post_init__(self):
        if not str(self.operation).strip():
            raise ValueError("operation must not be empty")
        for name in ("already_allocated", "persistent", "temporary", "transfers"):
            object.__setattr__(self, name, _integer(getattr(self, name), name))
        normalized = {
            str(name): _integer(value, f"component {name}")
            for name, value in self.components.items()
        }
        object.__setattr__(self, "components", normalized)

    @property
    def additional_peak(self):
        return self.persistent + self.temporary + self.transfers

    @property
    def total_peak(self):
        return self.already_allocated + self.additional_peak

    def dominant_components(self, limit=3):
        return tuple(
            sorted(self.components.items(), key=lambda item: item[1], reverse=True)[:limit]
        )


@dataclass(frozen=True)
class BudgetInfo:
    bytes: int
    source: str
    confidence: str
    candidates: Mapping[str, int] = field(default_factory=dict)


class MemoryBudgetExceeded(MemoryError):
    """Structured rejection raised before a predictably excessive allocation."""

    code = "memory_budget_exceeded"

    def __init__(self, estimate, budget):
        self.estimate = estimate
        self.budget = budget
        dominant = ", ".join(
            f"{name}={value / MIB:.1f} MiB"
            for name, value in estimate.dominant_components()
        ) or "not itemized"
        super().__init__(
            f"{estimate.operation} needs an estimated additional "
            f"{estimate.additional_peak / MIB:.1f} MiB (total peak "
            f"{estimate.total_peak / MIB:.1f} MiB), above the effective "
            f"{budget.bytes / MIB:.1f} MiB budget from {budget.source}; "
            f"dominant components: {dominant}; confidence: {estimate.confidence}"
        )


def compose_estimates(operation, phases, *, already_allocated=0,
                      confidence="conservative-composite"):
    """Compose sequential phases while retaining each phase's new buffers.

    A phase's ``persistent`` bytes remain live in later phases.  Temporary and
    transfer buffers from different phases are treated as mutually exclusive;
    buffers within one phase remain simultaneous.  Inputs are already margined
    estimates, so composition deliberately applies no second safety factor.
    """
    phases = tuple(phases)
    if not phases:
        return MemoryEstimate(operation, already_allocated=already_allocated,
                              confidence=confidence)
    resident_new = 0
    peak = 0
    components = {}
    inherited_resident = _integer(already_allocated, "already_allocated")
    for index, estimate in enumerate(phases):
        if not isinstance(estimate, MemoryEstimate):
            raise TypeError("every phase must be a MemoryEstimate")
        phase_peak = resident_new + estimate.additional_peak
        peak = max(peak, phase_peak)
        resident_new += estimate.persistent
        inherited_resident = max(inherited_resident, estimate.already_allocated)
        components[f"phase {index + 1}: {estimate.operation}"] = estimate.additional_peak
    # A persistent buffer cannot disappear at operation completion.
    peak = max(peak, resident_new)
    return MemoryEstimate(
        operation,
        already_allocated=inherited_resident,
        persistent=resident_new,
        temporary=peak - resident_new,
        components=components,
        confidence=confidence,
    )


def estimate_volume(shape, *, placement="Linear", public_copy=False,
                    scalar_field=False, cache_entries_alive=0):
    cells = _cells(shape)
    numbers = cells * 8
    selected = cells
    placement_extra = 0 if placement == "Linear" else cells * 24
    scalar = cells * 8 if scalar_field else 0
    copy_bytes = numbers + selected + scalar if public_copy else 0
    persistent = numbers + selected + scalar
    old_cache = _integer(cache_entries_alive, "cache_entries_alive") * (numbers + selected)
    components = {
        "new cached volume": numbers + selected,
        "placement temporaries": placement_extra,
        "public defensive copy": copy_bytes,
        "scalar field": scalar,
    }
    return MemoryEstimate(
        "volume construction",
        already_allocated=old_cache,
        persistent=_margin(persistent),
        temporary=_margin(placement_extra + copy_bytes),
        components=components,
    )


def estimate_projection(shape, plane_cells, *, public_copy=True, scalar_field=False):
    volume_cells = _cells(shape)
    plane_cells = _integer(plane_cells, "plane_cells", 1)
    copies = volume_cells * (9 + (8 if scalar_field else 0)) if public_copy else 0
    hits = plane_cells * 4
    field = plane_cells * 8 if scalar_field else 0
    return MemoryEstimate(
        "projection",
        temporary=_margin(copies + hits + field),
        components={"volume copies": copies, "hit projection": hits, "field plane": field},
    )


def estimate_sieve(limit, *, values_cells=0, public_copy=False, old_limit=-1,
                   device="host"):
    limit = _integer(limit, "limit")
    cells = _integer(values_cells, "values_cells")
    sieve = limit + 1
    old = max(0, _integer(max(-1, old_limit) + 1, "old sieve size"))
    mask = cells
    indexing = cells * 8
    copy_bytes = sieve if public_copy else 0
    transfers = (cells * 9 + mask) if device == "gpu" else 0
    return MemoryEstimate(
        f"{device} prime sieve",
        already_allocated=old,
        persistent=_margin(sieve),
        temporary=_margin(mask + indexing + copy_bytes),
        transfers=_margin(transfers),
        components={"new sieve": sieve, "value/index buffers": mask + indexing,
                    "public copy": copy_bytes, "host/device transfers": transfers},
    )


def estimate_entropy(shape, bins=8, *, device="host"):
    if len(tuple(shape)) != 2:
        raise ValueError("entropy shape must be two-dimensional")
    cells = _cells(shape)
    bins = _integer(bins, "bins", 2)
    # Match the existing eager expression, not just its named final arrays.
    # Input/ratios/quantized/padding can remain live throughout. During
    # -probs * log2(probs), counts (4B), probs (8B), condition (B), negative
    # (8B), logarithm (8B) and product (8B) may coexist: 37B bytes/cell.
    padding_cells = (int(shape[0]) + 2) * (int(shape[1]) + 2)
    retained = cells * 20 + padding_cells * 4
    expression = bins * cells * 37
    # Other phases are exclusive, not cumulative. Quantization includes
    # float intermediates; reduction retains counts/probs/terms and output.
    bytes_raw = max(cells * 44, retained + expression,
                    retained + bins * cells * 20 + cells * 8)
    transfers = cells * 16 if device == "gpu" else 0
    return MemoryEstimate(
        "local entropy",
        temporary=_margin(bytes_raw),
        transfers=_margin(transfers),
        components={"entropy expression peak": expression,
                    "retained quantization and padding": retained,
                    "host/device transfers": transfers},
    )


def estimate_fft(shape, *, display=False, device="host"):
    cells = _cells(shape)
    # Metrics additionally build probabilities, masks, indices and radius.
    bytes_per_cell = 110 if not display else 72
    transfers = cells * 24 if device == "gpu" else 0
    return MemoryEstimate(
        "FFT display" if display else "FFT metrics",
        temporary=_margin(cells * bytes_per_cell),
        transfers=_margin(transfers),
        components={"FFT work and derived arrays": cells * bytes_per_cell,
                    "host/device transfers": transfers},
    )


def estimate_overlay(shape, plane_cells, *, trials=1, placement="Linear",
                     bins=8, plane_shape=None):
    volume_cells = _cells(shape)
    plane_cells = _integer(plane_cells, "plane_cells", 1)
    _integer(trials, "trials", 1)  # sequential: validates but does not multiply peak
    persistent = volume_cells * 9
    factor = 400 if placement == "Linear" else 520
    # Without dimensions a singleton plane conservatively bounds padding.
    plane_shape = (1, plane_cells) if plane_shape is None else tuple(plane_shape)
    if len(plane_shape) != 2 or _cells(plane_shape) != plane_cells:
        raise ValueError("plane_shape must match plane_cells")
    envelope = _margin(plane_cells * factor)
    entropy = estimate_entropy(plane_shape, bins).additional_peak
    fft = estimate_fft(plane_shape).additional_peak
    # Caller-side masks, bases, random-control work and retained entropy
    # output surround sequential entropy/FFT phases. Child work is included
    # once, already margined; the empirical envelope is an alternative.
    workspace = _margin(plane_cells * 64)
    temporary = max(envelope, workspace + max(entropy, fft))
    return MemoryEstimate(
        "overlay metrics",
        already_allocated=persistent,
        temporary=temporary,
        components={"resident volume": persistent,
                    "metric envelope": envelope,
                    "caller workspace": workspace,
                    "entropy child": entropy, "FFT child": fft},
    )


def estimate_scan(pair_count, *, result_columns=24, operation_peak=0):
    pairs = _integer(pair_count, "pair_count")
    columns = _integer(result_columns, "result_columns", 1)
    operation_peak = _integer(operation_peak, "operation_peak")
    python_structures = pairs * (160 + columns * 40)
    return MemoryEstimate(
        "module scan",
        persistent=_margin(python_structures),
        temporary=operation_peak,
        components={"pair/result Python objects": python_structures,
                    "single operation peak": operation_peak},
    )


def estimate_3d(shape, *, selected_points=None):
    cells = _cells(shape)
    points = cells if selected_points is None else min(
        cells, _integer(selected_points, "selected_points")
    )
    # np.indices creates three int64 volumes before filtering/subsampling.
    coordinates = cells * 24
    masks = cells * 2
    point_arrays = points * (24 + 8 + 16)
    return MemoryEstimate(
        "3D visualization",
        temporary=_margin(coordinates + masks + point_arrays),
        components={"dense coordinate grids": coordinates,
                    "selection masks": masks, "point/color arrays": point_arrays},
    )


def _read_int(path):
    try:
        text = Path(path).read_text(encoding="ascii").strip()
        if text in ("", "max"):
            return None
        value = int(text)
        return value if value >= 0 else None
    except (OSError, ValueError, UnicodeError):
        return None


def _proc_status_value(name):
    try:
        for line in Path("/proc/self/status").read_text(encoding="ascii").splitlines():
            if line.startswith(name + ":"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def _os_available_memory():
    try:
        page = int(os.sysconf("SC_PAGE_SIZE"))
        pages = int(os.sysconf("SC_AVPHYS_PAGES"))
        return page * pages if page > 0 and pages >= 0 else None
    except (ValueError, OSError, AttributeError):
        return None


def _cgroup_remaining():
    """Headroom in the process's visible, mounted memory hierarchies only.

    Ancestors above a mount root or namespace-relative memberships that cannot
    be mapped to that root are unknown; do not guess a foreign cgroup.
    """
    candidates = []
    try:
        memberships = Path("/proc/self/cgroup").read_text(encoding="ascii").splitlines()
        mounts = Path("/proc/self/mountinfo").read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError):
        return None

    def unescape(value):
        # Decode mountinfo's escapes in one pass (including literal backslash).
        import re
        return re.sub(r"\\(040|011|012|134)",
                      lambda match: chr(int(match[1], 8)), value)

    for line in memberships:
        try:
            _hierarchy, controllers, membership = line.split(":", 2)
        except ValueError:
            continue
        v2 = controllers == ""
        if not v2 and "memory" not in controllers.split(","):
            continue
        member = Path(membership)
        if not member.is_absolute() or ".." in member.parts:
            continue
        for mount in mounts:
            try:
                before, after = mount.split(" - ", 1)
                fields, options = before.split(), after.split()
                kind = options[0]
                if kind != ("cgroup2" if v2 else "cgroup"):
                    continue
                if not v2 and "memory" not in options[2].split(","):
                    continue
                root, point = Path(unescape(fields[3])), Path(unescape(fields[4]))
                if not root.is_absolute() or not point.is_absolute():
                    continue
                if ".." in root.parts or ".." in point.parts:
                    continue
                relative = member.relative_to(root)
            except (ValueError, IndexError):
                continue
            node = point / relative
            while True:
                limit_name = "memory.max" if v2 else "memory.limit_in_bytes"
                usage_name = "memory.current" if v2 else "memory.usage_in_bytes"
                maximum = _read_int(node / limit_name)
                current = _read_int(node / usage_name)
                # Legacy ancestors constrain descendants only when their
                # hierarchical accounting is enabled. Unknown is not proof.
                applicable = (v2 or node == point / relative or
                              _read_int(node / "memory.use_hierarchy") == 1)
                if applicable and maximum is not None and current is not None:
                    candidates.append(max(0, maximum - current))
                if node == point:
                    break
                node = node.parent
    return min(candidates) if candidates else None


def _rlimit_as_headroom():
    if resource is None or not hasattr(resource, "RLIMIT_AS"):
        return None
    try:
        soft, _hard = resource.getrlimit(resource.RLIMIT_AS)
    except (ValueError, OSError, AttributeError):
        return None
    if soft in (resource.RLIM_INFINITY, -1):
        return None
    virtual = _proc_status_value("VmSize")
    return max(0, int(soft) - virtual) if virtual is not None else None


def effective_budget(configured_mib=None, available_fraction=None):
    if configured_mib is None or available_fraction is None:
        from app_config import get_config
        config = get_config()
        configured_mib = config.memory_budget_mb
        available_fraction = config.memory_available_fraction
    cap = _integer(configured_mib, "memory_budget_mb", 1) * MIB
    fraction = float(available_fraction)
    if not 0.0 < fraction <= 1.0:
        raise ValueError("memory_available_fraction must be in (0, 1]")
    candidates = {"configured cap": cap}
    for name, value in (("OS available", _os_available_memory()),
                        ("cgroup headroom", _cgroup_remaining())):
        if value is not None:
            candidates[name] = int(value * fraction)
    rlimit = _rlimit_as_headroom()
    if rlimit is not None:
        candidates["RLIMIT_AS virtual headroom"] = rlimit
    source, budget = min(candidates.items(), key=lambda item: item[1])
    confidence = "dynamic" if len(candidates) > 1 else "configured-cap-only"
    return BudgetInfo(max(0, budget), source, confidence, candidates)


def require_memory(estimate, *, budget=None):
    if not isinstance(estimate, MemoryEstimate):
        raise TypeError("estimate must be a MemoryEstimate")
    info = effective_budget() if budget is None else (
        budget if isinstance(budget, BudgetInfo)
        else BudgetInfo(_integer(budget, "budget"), "explicit", "caller-supplied")
    )
    if estimate.additional_peak > info.bytes:
        raise MemoryBudgetExceeded(estimate, info)
    return info


def effective_gpu_budget(cupy_module, configured_mib=None, available_fraction=None):
    """Return a VRAM budget, without inferring device capacity from host RAM."""
    if configured_mib is None or available_fraction is None:
        from app_config import get_config
        config = get_config()
        configured_mib = config.memory_budget_mb
        available_fraction = config.memory_available_fraction
    cap = _integer(configured_mib, "memory_budget_mb", 1) * MIB
    candidates = {"configured device cap": cap}
    confidence = "configured-cap-only"
    try:
        free_bytes, _total_bytes = cupy_module.cuda.runtime.memGetInfo()
        free_bytes = _integer(free_bytes, "free VRAM")
        fraction = float(available_fraction)
        if not 0.0 < fraction <= 1.0:
            raise ValueError("memory_available_fraction must be in (0, 1]")
        candidates["CUDA free VRAM"] = int(free_bytes * fraction)
        confidence = "device-runtime"
    except (AttributeError, TypeError, ValueError, RuntimeError):
        pass
    source, byte_count = min(candidates.items(), key=lambda item: item[1])
    return BudgetInfo(byte_count, source, confidence, candidates)
