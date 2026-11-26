"""Portable scientific provenance manifests for Prime Grid Atlas exports.

The module intentionally uses only the Python standard library.  It records
observations, not guarantees about code already loaded in memory or hardware
that was not exercised by an experiment.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import tempfile
import uuid


SCHEMA = "pga.provenance/1.0"
MANIFEST_STATES = {"running", "completed", "failed", "cancelled", "partial"}
OUTPUT_STATES = {"complete", "partial", "missing", "invalid"}


def utc_now():
    """Return an RFC 3339 UTC timestamp with second precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sha256_file(path, chunk_size=1024 * 1024):
    """Return the streaming SHA-256 digest of a regular file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_sidecar_path(output_path):
    """Return a collision-resistant sidecar path preserving the full filename."""
    output = Path(output_path)
    return output.with_name(output.name + ".manifest.json")


def _git(root, *arguments, timeout=2.0):
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        return None
    return result.stdout.strip()


def collect_source_identity(project_root, source_paths, timeout=2.0):
    """Observe Git state and hashes for a curated set of project sources.

    A Git repository is accepted only when its top level is exactly
    ``project_root``.  This prevents an extracted copy inside an unrelated
    parent repository from inheriting the parent's commit identity.
    """
    root = Path(project_root).resolve(strict=True)
    observed_at = utc_now()
    files = []
    missing = []
    for supplied in source_paths:
        candidate = Path(supplied)
        candidate = candidate if candidate.is_absolute() else root / candidate
        try:
            resolved = candidate.resolve(strict=True)
            relative = resolved.relative_to(root)
            if resolved.is_symlink() or not resolved.is_file():
                raise ValueError
        except (OSError, ValueError):
            try:
                label = candidate.relative_to(root).as_posix()
            except ValueError:
                label = "<outside-project>"
            missing.append({"path": label, "status": "missing_or_invalid"})
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "size": resolved.stat().st_size,
                "sha256": sha256_file(resolved),
                "observed_at": observed_at,
            }
        )

    git = {"available": False, "commit": None, "dirty": None}
    try:
        top_level = _git(root, "rev-parse", "--show-toplevel", timeout=timeout)
        pertinent = top_level is not None and Path(top_level).resolve() == root
        if pertinent:
            commit = _git(root, "rev-parse", "HEAD", timeout=timeout)
            status = _git(
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=normal",
                timeout=timeout,
            )
            if commit and status is not None:
                git = {
                    "available": True,
                    "commit": commit,
                    "dirty": bool(status),
                }
    except (OSError, subprocess.SubprocessError):
        pass

    if git["available"]:
        identity_status = (
            "git_commit_and_file_hashes_dirty"
            if git["dirty"]
            else "git_commit_and_file_hashes_clean"
        )
    elif files:
        identity_status = "file_hashes_only"
    else:
        identity_status = "unavailable"
    return {
        "identity_status": identity_status,
        "observed_at": observed_at,
        "git": git,
        "files": files,
        "missing_files": missing,
        "loaded_code_identity": "not_verified",
    }


def _package_version(distribution):
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def collect_environment(cuda_available=None, cupy_relevant=False):
    """Collect an allow-listed, non-identifying execution environment."""
    return {
        "observed_at": utc_now(),
        "python": platform.python_version(),
        "packages": {
            "numpy": _package_version("numpy"),
            "cupy": _package_version("cupy") if cupy_relevant else None,
            "cupy_status": "observed" if cupy_relevant else "not_applicable",
        },
        "platform": {
            "system": platform.system() or None,
            "machine": platform.machine() or None,
        },
        "cuda_available": cuda_available,
        "cuda_availability_status": (
            "observed" if cuda_available is not None else "not_verified"
        ),
    }


def new_experiment_manifest(
    application_version,
    experiment_kind,
    *,
    source=None,
    environment=None,
    requested_configuration=None,
    effective_configuration=None,
    randomness=None,
    compute=None,
    started_at=None,
    status="running",
    warnings=None,
    limitations=None,
):
    """Create a new manifest without inferring unavailable observations."""
    if status not in MANIFEST_STATES:
        raise ValueError(f"invalid manifest state: {status}")
    started = started_at or utc_now()
    return {
        "schema": SCHEMA,
        "schema_version": "1.0",
        "application": {
            "name": "Prime Grid Atlas",
            "version": str(application_version),
        },
        "experiment_id": str(uuid.uuid4()),
        "source": deepcopy(source) if source is not None else {
            "identity_status": "not_verified"
        },
        "environment": deepcopy(environment) if environment is not None else {
            "status": "not_verified"
        },
        "experiment": {
            "kind": str(experiment_kind),
            "status": status,
            "experiment_started_at": started,
            "experiment_completed_at": None,
            "exported_at": None,
            "command": None,
            "command_status": "not_recorded_for_privacy",
        },
        "configuration": {
            "requested": deepcopy(requested_configuration),
            "effective": deepcopy(effective_configuration),
        },
        "randomness": deepcopy(randomness) if randomness is not None else {
            "status": "not_applicable",
            "seed": None,
            "algorithm": None,
        },
        "compute": deepcopy(compute) if compute is not None else {
            "requested_backend": None,
            "effective_backend": None,
            "result_origin": "unknown",
            "producer_backend": None,
            "backend_evidence": "not_verified",
            "fallback_events": [],
        },
        "outputs": [],
        "warnings": list(warnings or []),
        "limitations": list(limitations or []),
    }


def _safe_output_path(output_root, supplied):
    root = Path(output_root).resolve(strict=True)
    raw = Path(supplied)
    if not raw.is_absolute() and ".." in PurePosixPath(raw.as_posix()).parts:
        return None, None
    if raw.is_absolute():
        try:
            raw.relative_to(root)
        except ValueError:
            return None, None
    candidate = raw if raw.is_absolute() else root / raw
    try:
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(root)
    except (OSError, ValueError):
        return None, None
    if candidate.is_symlink() or not resolved.is_file():
        return None, None
    portable = PurePosixPath(relative.as_posix())
    if portable.is_absolute() or ".." in portable.parts:
        return None, None
    return resolved, portable.as_posix()


def _manifest_matches_outputs(path):
    """Return whether a PGA manifest still matches every recorded output."""
    manifest_path = Path(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema") != SCHEMA:
            return False
        outputs = manifest["outputs"]
        if not isinstance(outputs, list) or not outputs:
            return False
        root = manifest_path.parent.resolve(strict=True)
        for record in outputs:
            if record.get("status") not in ("complete", "partial"):
                return False
            resolved, _ = _safe_output_path(root, record.get("path"))
            if resolved is None:
                return False
            if resolved.stat().st_size != record.get("size"):
                return False
            if sha256_file(resolved) != record.get("sha256"):
                return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


class ExportConsistencyGuard:
    """Keep an obsolete manifest from remaining active during an export.

    The guard is intentionally not a general multi-file transaction.  It moves
    a pertinent active manifest aside before callers alter outputs.  On failure
    it restores that manifest only when every recorded checksum still matches.
    """

    def __init__(self, manifest_path, output_paths=()):
        self.manifest_path = Path(manifest_path)
        self.output_paths = tuple(Path(path) for path in output_paths)
        self.inactive_path = None

    def __enter__(self):
        active = self.manifest_path
        destinations = [path.resolve(strict=False) for path in self.output_paths]
        if len(destinations) != len(set(destinations)):
            raise ValueError("export output destinations must be distinct")
        if active.resolve(strict=False) in destinations:
            raise ValueError("the active manifest cannot also be an export output")
        if any(path.name.endswith(".manifest.json") for path in self.output_paths):
            raise ValueError("export output uses the reserved .manifest.json suffix")
        if not active.exists():
            return self
        try:
            existing = json.loads(active.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FileExistsError(
                f"refusing to replace unrecognized sidecar: {active.name}"
            ) from exc
        if existing.get("schema") != SCHEMA:
            raise FileExistsError(
                f"refusing to replace non-PGA sidecar: {active.name}"
            )
        inactive = active.with_name(
            f"{active.name}.inactive-{uuid.uuid4().hex}.json"
        )
        os.replace(active, inactive)
        self.inactive_path = inactive
        return self

    def _restore_if_current(self):
        inactive = self.inactive_path
        if inactive is None or not inactive.exists():
            return
        if self.manifest_path.exists():
            return
        if _manifest_matches_outputs(inactive):
            os.replace(inactive, self.manifest_path)

    def __exit__(self, exception_type, exception, traceback):
        if exception_type is not None:
            self._restore_if_current()
            return False
        if not self.manifest_path.exists():
            self._restore_if_current()
            raise OSError("export completed without an active provenance manifest")
        if self.inactive_path is not None:
            try:
                self.inactive_path.unlink()
            except FileNotFoundError:
                pass
        return False


def finalize_experiment_manifest(
    manifest,
    output_root,
    outputs,
    *,
    manifest_path=None,
    status="completed",
    completed_at=None,
    exported_at=None,
):
    """Return a finalized copy with output integrity observations.

    ``outputs`` contains paths or dictionaries with ``path``, ``required`` and
    optional ``status`` (used to label a known partial file).  Missing or
    invalid required outputs prevent a completed experiment state.
    """
    if status not in MANIFEST_STATES:
        raise ValueError(f"invalid manifest state: {status}")
    result = deepcopy(manifest)
    root = Path(output_root).resolve(strict=True)
    manifest_resolved = None
    if manifest_path is not None:
        candidate = Path(manifest_path)
        manifest_resolved = (
            candidate if candidate.is_absolute() else root / candidate
        ).resolve(strict=False)
    records = []
    required_problem = False
    for item in outputs:
        descriptor = {"path": item} if isinstance(item, (str, os.PathLike)) else dict(item)
        supplied = descriptor.get("path")
        required = bool(descriptor.get("required", True))
        requested_state = descriptor.get("status", "complete")
        if requested_state not in OUTPUT_STATES:
            raise ValueError(f"invalid output state: {requested_state}")
        resolved, relative = _safe_output_path(root, supplied)
        if resolved is None:
            raw = Path(supplied)
            if raw.is_absolute():
                try:
                    label = raw.relative_to(root).as_posix()
                except ValueError:
                    label = "<outside-output-root>"
            else:
                label = PurePosixPath(raw.as_posix()).as_posix()
            safe_missing = not raw.is_absolute() and ".." not in PurePosixPath(raw.as_posix()).parts
            state = "missing" if safe_missing and not (root / raw).exists() else "invalid"
            record = {
                "path": label,
                "status": state,
                "required": required,
                "size": None,
                "sha256": None,
                "binary_integrity": "not_verified",
                "scientific_completeness": descriptor.get(
                    "scientific_completeness", "unknown"
                ),
            }
        elif manifest_resolved is not None and resolved == manifest_resolved:
            record = {
                "path": relative,
                "status": "invalid",
                "required": required,
                "size": None,
                "sha256": None,
                "reason": "manifest_self_reference",
                "binary_integrity": "not_verified",
                "scientific_completeness": descriptor.get(
                    "scientific_completeness", "unknown"
                ),
            }
        else:
            record = {
                "path": relative,
                "status": requested_state,
                "required": required,
                "size": resolved.stat().st_size,
                "sha256": sha256_file(resolved),
                "binary_integrity": "verified_sha256",
                "scientific_completeness": descriptor.get(
                    "scientific_completeness",
                    "partial" if requested_state == "partial" else "complete",
                ),
            }
        if required and record["status"] != "complete":
            required_problem = True
        records.append(record)
    if status == "completed" and required_problem:
        status = "partial"
    result["outputs"] = records
    result["experiment"]["status"] = status
    result["experiment"]["experiment_completed_at"] = completed_at or (
        utc_now() if status != "running" else None
    )
    result["experiment"]["exported_at"] = exported_at or utc_now()
    return result


def _reject_non_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("manifest contains NaN or Infinity")
    if isinstance(value, dict):
        for item in value.values():
            _reject_non_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_finite(item)


def write_manifest_atomic(path, manifest):
    """Write strict JSON atomically, preserving an older valid destination."""
    destination = Path(path)
    _reject_non_finite(manifest)
    payload = json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
