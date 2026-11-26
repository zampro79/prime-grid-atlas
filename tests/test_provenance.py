"""Tests for the standard-library scientific provenance layer."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from provenance import (
    ExportConsistencyGuard,
    SCHEMA,
    collect_environment,
    collect_source_identity,
    finalize_experiment_manifest,
    new_experiment_manifest,
    manifest_sidecar_path,
    sha256_file,
    write_manifest_atomic,
)


class ProvenanceTests(unittest.TestCase):
    def manifest(self, **kwargs):
        return new_experiment_manifest("1.0.0", "test", **kwargs)

    def init_git(self, root):
        subprocess.run(["git", "init", "-q", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "test@invalid"], check=True)

    def create_active_export(self, root, name="result.csv", content=b"old"):
        output = root / name
        output.write_bytes(content)
        sidecar = manifest_sidecar_path(output)
        manifest = finalize_experiment_manifest(
            self.manifest(), root, [output.name], manifest_path=sidecar
        )
        write_manifest_atomic(sidecar, manifest)
        return output, sidecar

    def test_sha256_streaming(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), hashlib.sha256(b"abc").hexdigest())

    def test_sidecar_naming_preserves_complete_filename(self):
        root = Path("exports")
        self.assertEqual(manifest_sidecar_path(root / "same.csv").name, "same.csv.manifest.json")
        self.assertEqual(manifest_sidecar_path(root / "same.png").name, "same.png.manifest.json")
        self.assertEqual(
            manifest_sidecar_path(root / "archive.data.csv").name,
            "archive.data.csv.manifest.json",
        )
        self.assertNotEqual(
            manifest_sidecar_path(root / "same.csv"),
            manifest_sidecar_path(root / "same.png"),
        )

    def test_git_clean_dirty_and_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.init_git(root)
            source = root / "source.py"
            source.write_text("value = 1\n")
            subprocess.run(["git", "-C", root, "add", "source.py"], check=True)
            subprocess.run(["git", "-C", root, "commit", "-qm", "initial"], check=True)
            clean = collect_source_identity(root, ["source.py", "missing.py"])
            self.assertEqual(clean["identity_status"], "git_commit_and_file_hashes_clean")
            self.assertFalse(clean["git"]["dirty"])
            self.assertEqual(clean["missing_files"][0]["path"], "missing.py")
            source.write_text("value = 2\n")
            dirty = collect_source_identity(root, ["source.py"])
            self.assertEqual(dirty["identity_status"], "git_commit_and_file_hashes_dirty")
            self.assertTrue(dirty["git"]["dirty"])

    def test_parent_repository_is_not_attributed_to_extracted_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.init_git(root)
            extracted = root / "archive"
            extracted.mkdir()
            (extracted / "source.py").write_text("pass\n")
            identity = collect_source_identity(extracted, ["source.py"])
            self.assertEqual(identity["identity_status"], "file_hashes_only")
            self.assertFalse(identity["git"]["available"])

    def test_no_git_archive_and_outside_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "archive"
            root.mkdir()
            (root / "source.py").write_text("pass\n")
            identity = collect_source_identity(root, ["source.py", root.parent / "private"])
            self.assertEqual(identity["identity_status"], "file_hashes_only")
            self.assertEqual(identity["files"][0]["path"], "source.py")
            self.assertEqual(identity["missing_files"][0]["path"], "<outside-project>")

    def test_environment_is_allow_listed(self):
        environment = collect_environment(cuda_available=False)
        encoded = json.dumps(environment).lower()
        for forbidden in ("hostname", "username", "token", "remote", "home"):
            self.assertNotIn(forbidden, encoded)

    def test_manifest_states_seed_known_unknown_and_backend_records(self):
        for state in ("running", "completed", "failed", "cancelled", "partial"):
            manifest = self.manifest(status=state)
            self.assertEqual(manifest["experiment"]["status"], state)
        known = self.manifest(randomness={"status": "observed", "seed": 7, "algorithm": "explicit-test"})
        self.assertEqual(known["randomness"]["seed"], 7)
        unknown = self.manifest(randomness={"status": "not_verified", "seed": None, "algorithm": None})
        self.assertIsNone(unknown["randomness"]["seed"])
        cache = self.manifest(compute={
            "requested_backend": "Auto", "effective_backend": None,
            "result_origin": "cache", "producer_backend": None,
            "backend_evidence": "cache_hit_unattributed", "fallback_events": [],
        })
        self.assertIsNone(cache["compute"]["producer_backend"])
        fallback = self.manifest(compute={
            "requested_backend": "GPU", "effective_backend": "CPU",
            "result_origin": "computed", "producer_backend": "CPU",
            "backend_evidence": "observed_fallback", "fallback_events": [{"from": "GPU", "to": "CPU"}],
        })
        self.assertEqual(fallback["compute"]["fallback_events"][0]["to"], "CPU")

    def test_outputs_complete_missing_partial_traversal_and_self_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ok.csv").write_text("x\n1\n")
            manifest_path = root / "run.manifest.json"
            manifest_path.write_text("{}")
            result = finalize_experiment_manifest(
                self.manifest(), root,
                ["ok.csv", "missing.csv", {"path": "ok.csv", "status": "partial"}, "../outside", "run.manifest.json"],
                manifest_path=manifest_path,
            )
            self.assertEqual(result["experiment"]["status"], "partial")
            self.assertEqual([item["status"] for item in result["outputs"]],
                             ["complete", "missing", "partial", "invalid", "invalid"])
            self.assertEqual(result["outputs"][-1]["reason"], "manifest_self_reference")
            self.assertEqual(result["outputs"][0]["binary_integrity"], "verified_sha256")
            self.assertEqual(result["outputs"][2]["scientific_completeness"], "partial")

    def test_external_symlink_is_invalid_and_input_unchanged(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external:
            root = Path(directory)
            target = Path(external) / "private"
            target.write_text("secret")
            link = root / "link"
            link.symlink_to(target)
            before = target.read_bytes()
            result = finalize_experiment_manifest(self.manifest(), root, ["link"])
            self.assertEqual(result["outputs"][0]["status"], "invalid")
            self.assertEqual(target.read_bytes(), before)

    def test_strict_json_rejects_non_finite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.assertRaises(ValueError):
                    write_manifest_atomic(path, {"value": value})
            self.assertFalse(path.exists())

    def test_atomic_write_and_previous_manifest_survives_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            write_manifest_atomic(path, {"schema": SCHEMA, "value": 1})
            previous = path.read_bytes()
            with self.assertRaises(TypeError):
                write_manifest_atomic(path, {"unsupported": object()})
            self.assertEqual(path.read_bytes(), previous)
            with patch("provenance.os.replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    write_manifest_atomic(path, {"schema": SCHEMA, "value": 2})
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])

    def test_finalization_does_not_mutate_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result").write_text("data")
            original = self.manifest()
            snapshot = json.dumps(original, sort_keys=True)
            finalize_experiment_manifest(original, root, ["result"])
            self.assertEqual(json.dumps(original, sort_keys=True), snapshot)

    def test_repeated_export_replaces_manifest_and_removes_inactive_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with ExportConsistencyGuard(sidecar):
                output.write_bytes(b"new")
                manifest = finalize_experiment_manifest(
                    self.manifest(), root, [output.name], manifest_path=sidecar
                )
                write_manifest_atomic(sidecar, manifest)
            current = json.loads(sidecar.read_text())
            self.assertEqual(current["outputs"][0]["sha256"], sha256_file(output))
            self.assertEqual(list(root.glob("*.inactive-*.json")), [])

    def test_invalidation_failure_stops_before_output_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            before = output.read_bytes()
            with patch("provenance.os.replace", side_effect=OSError("invalidation failed")):
                with self.assertRaises(OSError):
                    with ExportConsistencyGuard(sidecar):
                        output.write_bytes(b"must not run")
            self.assertEqual(output.read_bytes(), before)
            self.assertTrue(sidecar.exists())

    def test_output_failure_restores_still_matching_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    raise OSError("simulated output failure")
            self.assertTrue(sidecar.exists())
            self.assertEqual(
                json.loads(sidecar.read_text())["outputs"][0]["sha256"],
                sha256_file(output),
            )

    def test_changed_output_and_manifest_failure_leave_no_active_stale_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    output.write_bytes(b"changed")
                    with patch("provenance.write_manifest_atomic", side_effect=OSError("write failed")):
                        from provenance import write_manifest_atomic as failing_write
                        failing_write(sidecar, self.manifest())
            self.assertFalse(sidecar.exists())
            inactive = list(root.glob("*.inactive-*.json"))
            self.assertEqual(len(inactive), 1)
            self.assertNotEqual(
                json.loads(inactive[0].read_text())["outputs"][0]["sha256"],
                sha256_file(output),
            )

    def test_hash_failure_and_partial_batch_leave_no_active_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, sidecar = self.create_active_export(root, "first.csv")
            second = root / "second.csv"
            second.write_bytes(b"old-second")
            old = json.loads(sidecar.read_text())
            old["outputs"].append({
                "path": second.name,
                "status": "complete",
                "required": True,
                "size": second.stat().st_size,
                "sha256": sha256_file(second),
                "binary_integrity": "verified_sha256",
                "scientific_completeness": "complete",
            })
            write_manifest_atomic(sidecar, old)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    first.write_bytes(b"partial-new-first")
                    raise OSError("second batch output failed")
            self.assertFalse(sidecar.exists())
            self.assertEqual(len(list(root.glob("*.inactive-*.json"))), 1)

            hash_output = root / "hash.csv"
            hash_output.write_bytes(b"data")
            hash_sidecar = manifest_sidecar_path(hash_output)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(hash_sidecar):
                    with patch("provenance.sha256_file", side_effect=OSError("hash failed")):
                        finalize_experiment_manifest(
                            self.manifest(), root, [hash_output.name], manifest_path=hash_sidecar
                        )
            self.assertFalse(hash_sidecar.exists())

    def test_unrecognized_active_sidecar_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "result.csv"
            output.write_bytes(b"unchanged")
            sidecar = manifest_sidecar_path(output)
            sidecar.write_text('{"owner": "unrelated"}\n')
            with self.assertRaises(FileExistsError):
                with ExportConsistencyGuard(sidecar):
                    output.write_bytes(b"must not run")
            self.assertEqual(output.read_bytes(), b"unchanged")

    def test_reserved_and_duplicate_output_destinations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "result.csv.manifest.json"
            reserved = root / "other.csv.manifest.json"
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [reserved]):
                    self.fail("reserved output must be rejected before writing")
            duplicate = root / "same.csv"
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [duplicate, duplicate]):
                    self.fail("duplicate outputs must be rejected before writing")
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [manifest]):
                    self.fail("manifest self-overwrite must be rejected")


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HAS_QT = importlib.util.find_spec("PySide6") is not None


@unittest.skipUnless(HAS_QT, "PySide6 is needed for FFT provenance integration")
class FFTTemporalProvenanceTests(unittest.TestCase):
    def test_fft_uses_rendered_data_snapshot_before_and_after_deferred_render(self):
        from app_config import reset_config
        from PySide6.QtWidgets import QApplication
        import qt_app

        app = QApplication.instance() or QApplication([])
        window = qt_app.MainWindow()
        class FakeAxes:
            def imshow(self, *args, **kwargs):
                return object()

            def set_title(self, *args, **kwargs):
                return None

        class FakeFigure:
            def colorbar(self, *args, **kwargs):
                return None

            def tight_layout(self):
                return None

            def savefig(self, path, **kwargs):
                Path(path).write_bytes(b"simulated-png")

        pyplot = types.ModuleType("matplotlib.pyplot")
        pyplot.subplots = lambda **kwargs: (FakeFigure(), FakeAxes())
        pyplot.close = lambda figure: None
        matplotlib = types.ModuleType("matplotlib")
        matplotlib.pyplot = pyplot
        try:
            window.backend.setCurrentText("CPU")
            window.set_dims(3, 3, 2)
            window.render()
            self.assertEqual(window._render_provenance["configuration"]["grid"]["x"], 3)
            window.x_spin.setValue(4)
            window.timer.stop()
            with tempfile.TemporaryDirectory() as directory:
                first = Path(directory) / "fft.before.png"
                with patch.dict(
                    sys.modules,
                    {"matplotlib": matplotlib, "matplotlib.pyplot": pyplot},
                ), patch.object(
                    qt_app.QFileDialog, "getSaveFileName", return_value=(str(first), "")
                ):
                    window.save_fft()
                before = json.loads(manifest_sidecar_path(first).read_text())
                self.assertEqual(
                    before["configuration"]["effective"]["current_data_source"]["grid"]["x"],
                    3,
                )
                self.assertEqual(
                    before["configuration"]["requested"]["current_widgets_at_export"]["grid"]["x"],
                    4,
                )

                window.render()
                second = Path(directory) / "fft.after.png"
                with patch.dict(
                    sys.modules,
                    {"matplotlib": matplotlib, "matplotlib.pyplot": pyplot},
                ), patch.object(
                    qt_app.QFileDialog, "getSaveFileName", return_value=(str(second), "")
                ):
                    window.save_fft()
                after = json.loads(manifest_sidecar_path(second).read_text())
                self.assertEqual(
                    after["configuration"]["effective"]["current_data_source"]["grid"]["x"],
                    4,
                )
        finally:
            window.timer.stop()
            window.close()
            app.processEvents()
            reset_config()


if __name__ == "__main__":
    unittest.main()
