"""Central, serializable runtime configuration for Prime Grid Atlas."""

from dataclasses import asdict, dataclass, fields, replace
import json
from pathlib import Path
from threading import RLock
import math


CONFIG_SCHEMA_VERSION = 1
DEFAULT_CONFIG_PATH = Path(__file__).with_name("prime_atlas_config.json")


@dataclass(frozen=True)
class AppConfig:
    schema_version: int = CONFIG_SCHEMA_VERSION

    # Compute and scan
    gpu_auto_min_elements: int = 65_536
    max_volume: int = 25_000_000
    baseline_trials: int = 12
    baseline_seed: int = -1  # -1 = deterministic seed derived from the experiment

    # Scientific metrics
    entropy_bins: int = 8
    edge_threshold: float = 0.72
    fft_low_radius: float = 0.18
    beauty_entropy_weight: float = 0.35
    beauty_edge_weight: float = 0.65
    beauty_target_density: float = 0.27
    beauty_density_decay: float = 18.0

    # Rendering
    max_text_cells: int = 12_000
    max_3d_points: int = 2_000_000
    point_size_3d: float = 5.0
    redraw_delay_ms: int = 60
    export_max_side: int = 1_400


_lock = RLock()
_config = AppConfig()


def validate_config(config):
    values = asdict(config)
    integer_minimums = {
        "gpu_auto_min_elements": 1,
        "max_volume": 1,
        "baseline_trials": 1,
        "entropy_bins": 2,
        "max_text_cells": 0,
        "max_3d_points": 1,
        "redraw_delay_ms": 0,
        "export_max_side": 64,
    }
    for key, minimum in integer_minimums.items():
        values[key] = max(minimum, int(values[key]))
    values["baseline_seed"] = int(values["baseline_seed"])
    finite_fields = (
        "edge_threshold", "fft_low_radius", "beauty_entropy_weight",
        "beauty_edge_weight", "beauty_target_density",
        "beauty_density_decay", "point_size_3d",
    )
    for key in finite_fields:
        values[key] = float(values[key])
        if not math.isfinite(values[key]):
            raise ValueError(f"{key} must be finite")
    values["edge_threshold"] = min(1.0, max(0.0, values["edge_threshold"]))
    values["fft_low_radius"] = min(1.0, max(0.001, float(values["fft_low_radius"])))
    values["beauty_entropy_weight"] = max(0.0, float(values["beauty_entropy_weight"]))
    values["beauty_edge_weight"] = max(0.0, float(values["beauty_edge_weight"]))
    values["beauty_target_density"] = min(
        1.0, max(0.0, float(values["beauty_target_density"]))
    )
    values["beauty_density_decay"] = max(0.0, float(values["beauty_density_decay"]))
    values["point_size_3d"] = max(0.1, float(values["point_size_3d"]))
    values["schema_version"] = CONFIG_SCHEMA_VERSION
    return AppConfig(**values)


def get_config():
    with _lock:
        return replace(_config)


def set_config(config):
    global _config
    with _lock:
        _config = validate_config(config)
        return replace(_config)


def reset_config():
    return set_config(AppConfig())


def config_dict(config=None):
    return asdict(config or get_config())


def save_config(path=DEFAULT_CONFIG_PATH, config=None):
    path = Path(path)
    path.write_text(
        json.dumps(config_dict(config), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_config(path=DEFAULT_CONFIG_PATH):
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    allowed = {field.name for field in fields(AppConfig)}
    values = {key: value for key, value in raw.items() if key in allowed}
    return set_config(AppConfig(**values))


def load_default_config_if_present():
    if DEFAULT_CONFIG_PATH.exists():
        return load_config(DEFAULT_CONFIG_PATH)
    return get_config()
